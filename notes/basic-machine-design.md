# The BASIC machine, redesigned: slots, a persistent vector, and a read-only evaluator

A design note for sign-off. Nothing in it is built yet. The measurements it
answers are in [timing the BASIC ladder](timing-the-basic-ladder.md).

---

## Why

Measured with one `basic-run` process per program and `strace` counting
`mmap` calls (on Roc's default platform every heap allocation is one `mmap`,
[roc-lang/roc#11335](https://github.com/roc-lang/roc/issues/11335)):

- a `NEXT` costs about 1 µs and allocates nothing;
- a `LET X=1`, `X=X+1`, `PRINT` or `POKE` allocates once or more **per
  statement**, because the list it writes is copied first;
- a `POKE` copies the whole 100 KB page table every time.

The copy has one cause, reproduced outside BASIC in
`roc-apps/findings/threaded-record-copy/`: **a value passed through a
recursive function and handed back makes the caller's next `List.set` copy
it**, whatever the spelling (field access, rebinding, destructuring). The
interpreter's evaluator (`sum` → `term` → `power` → `primary` →
`name_or_call`) takes the machine and returns it, so every write after an
expression copies. A recursive function that only **reads** the machine,
and returns something else, causes no copy — measured, with one function
and with two mutually recursive ones.

And a design that is fast only while Roc can prove nothing else refers to a
list fails the first time something does. So the design has two rules:

1. **Nothing evaluates by handing the machine back.** The evaluator reads.
2. **Every structure a statement writes has a bounded copy cost**, so a
   copy, when Roc makes one, costs a few small nodes and never a whole table.

---

## 1. Load: parse once, resolve names to slots

Today every statement is re-read from its source bytes each time it runs,
and every variable is found by comparing its name.

At load, after the ECMA-55 checks (`Listing`, `Program`) pass:

- **Each statement is parsed once** into a `Stmt` value: its kind, its
  expressions as trees, its numbers as numbers (`numeral` runs once), its
  jump targets as statement indices.
- **Each distinct variable name gets a slot**: a name → slot dictionary
  built during the parse, and finished before the first statement runs. It
  is never consulted again. `I`, `X9`, `A$`, and a microcomputer's
  `NUM_QUEENS_PLACED` all become small integers, and a long name costs
  nothing at run time.
- **A statement's position is an index into the statement list**, not a
  line and a byte offset. A GOSUB's return point is "the statement after
  this one", which removes the fault `bunny` found (`GOSUB 260: GOTO 450`
  returning to the start of its line) by construction.

```roc
Expr : [Num(F64), Text(Str), Var(U64), Elem(U64, List(Expr)), Call(Fn, List(Expr)), Neg(Expr), Bin(Op, Expr, Expr), ...]
Stmt : [Let(U64, Expr), SetElem(U64, List(Expr), Expr), Print(List(Item)), Goto(U64), Gosub(U64), Return, If(Cond, Then), For(U64, Expr, Expr, Expr), Next(U64), Read(List(Target)), Input(Str, List(Target)), Dim(List(Bound)), Poke(Expr, Expr), Sleep(Expr), End, ...]
```

The shapes are illustrative; the parse follows the recognizers `Listing.roc`
already has.

## 2. Values: one vector, indexed by slot

**All variables live in one persistent vector**, the Python-like dictionary
with its keys resolved at load. A slot holds a tagged value:

```roc
Value : [Num(F64), Text(Str), Nums(Grid), Texts(TextGrid), Unset]
```

A dimensioned array is one value in one slot, holding its own vector of
cells and its bounds.

**The vector is Elm's `Array` design, cut down.** A tree of 32-slot nodes,
five bits of the index a level. Its size is known when it is made (the
slot count at load; an array's cells at DIM), so Elm's tail and `push` —
the part about growing — has nothing to do. What remains is `get`, `set`
and `repeat`:

- a `set` copies at most one node per level, 32 entries each: one node for
  up to 32 variables, two for up to 1,024;
- when Roc does write in place, that is still what happens, and nothing
  depends on it.

POKE memory and the screen use the same vector type, which replaces
`Pages.roc`'s 4,096-entry table.

## 3. The evaluator reads and reports

```roc
eval : Machine, Expr -> { value : Value, effects : List(Effect) }
Effect : [Stop(Str), Report(Str), Seed(U64)]
```

The evaluator takes the machine and returns a value and what happened; it
never returns the machine. What it writes today, and where each goes:

| today | becomes |
|---|---|
| `fail`, `halt`, `done` — an exception that stops | `Stop(reason)` |
| `emit` of `?Overflow`, `?Division by zero`, `?Zero raised to a negative power` | `Report(message)`, printed by the statement |
| `rnd` advancing the seed | `Seed(next)` |
| `ensure_arr` creating an array on first use | at load: every array name has its slot; one never DIMmed gets its default bounds then |

The statement that ran the evaluation applies the effects to the machine,
once, and makes its own write — the only writes there are.

## 4. `machine_state_at_next_effect`

```roc
machine_state_at_next_effect : Machine -> Machine
```

The run loop as one pure function: it executes statements until one needs
the world — a line of input it does not have, a SLEEP, the end, a stop, or
its fuel running out — and returns the machine as it stands there, with
`status` saying which. The batch doors call it until the end; the page
calls it once per resume. The transcript and the screen stay in the machine,
as now.

## 5. Held to pathological programs

Each is one `basic-run` process, timed alone, with its `mmap` calls counted.
**The bar: no statement kind allocates per execution in the steady state,
and no cost grows with the number of variables, the size of an array, or
how long the program has run.** Anything over a second is a failure to
explain.

| program | what it stresses |
|---|---|
| 100,000 × `X=X+1` | the store after an expression |
| 300 distinct variables, stored round-robin 100,000 times | slot count |
| `DIM A(10000)`, filled, then 100,000 random reads and writes | a big array |
| 100,000 × `POKE` across 64 KB | memory |
| 10,000 × `PRINT` | the screen and the transcript |
| `A$=A$+"X"` to 10,000 characters | string growth |
| `FOR` nested 100 × 100 × 100 | loops |
| GOSUB 1,000 deep, then back | the return stack |

## 6. How it lands

- **Beside the old, not over it.** New modules — a parser to `Stmt`, the
  vector, the machine — and `BasicRun.roc` switched to them when they pass.
- **The gate is the transcripts.** Every NBS and games program through the
  new machine produces the transcript the old one does, byte for byte,
  except where the old one is wrong (the GOSUB return point, `bunny`).
  Differences are read one by one, not counted.
- **The page follows**, through the same pure function.

## Questions for sign-off

1. One vector of tagged values for everything, or one per kind (numbers,
   strings, arrays)? One is the dictionary as described; per kind saves the
   tag on every read.
2. The page's history of machines (`back`) is unused. The vector makes
   keeping it cheap either way; is it staying?
