# The BASIC machine, built: what holds, and what still copies

The redesign in [the design note](basic-machine-design.md) is built beside the
old interpreter, on roc-apps branch `basic-machine`. `basic-run` now runs it.
This is where it stands: the gate, the allocation counts, and the three kinds
of statement that still copy for a reason I have not found.

Every time below names the program that spent it. "Dev" and "speed" are the
Roc compiler's `--opt=dev` and default LLVM backends building the same
interpreter.

---

## What is built

- **`Vec.roc`**: a persistent vector, a tree of 32-slot nodes over 32-entry
  leaves. It supports `repeat`, `get`, `set` and `replace` (take an entry out
  and leave a placeholder). A write takes each node out with `List.replace`
  before writing it. Checked against a plain `List` at sizes 1 to 1,048,577:
  no mismatches.
- **`Parse.roc`**: each statement is parsed once into a `Stmt`, and all lines'
  statements form one list. Constant jumps become statement indices, and a
  failed IF goes to the next line's first statement. A malformed statement
  parses to the evaluations before its fault, then a node that stops the
  machine.
- **`Machine.roc`**: the machine record, a read-only evaluator, and the run
  loop `machine_state_at_next_effect`.
  - The evaluator answers a value and its effects: the next seed, the reports
    it printed, the reason it stopped, and any arrays used before they
    existed.
  - The statement that asked applies those effects.
  - The batch door, the page's `start`/`resume`, `status` and `screen` keep
    the old signatures. The page itself is not switched yet.

The design note's two questions, decided:

1. **One vector per kind**: numbers, strings and arrays, each a vector of 572
   slots. A name's type is in its text, so a stored number never carries a
   tag.
2. **A slot is computed from the name**: a letter, an optional digit and an
   optional `$`, giving 26 × 11 × 2 names of each kind. No dictionary is built.
   A long name would need one; the interpreter reads none today.

`back` is untouched, because the page still runs the old machine.

## The gate

Every corpus program went through both interpreters, one process each:

- the old one, `basic-run-old`, speed build, 10 s limit;
- the new one, dev build, 20 s limit.

The transcripts were compared byte for byte by `basic/compare.sh`.

| suite | identical | differ | timed out |
|---|---|---|---|
| NBS (208) | 207 | 0 | P134, on both |
| games (99) | 95 | 0 | bunny, footbal2, gomoko, lunar, on the old one only |

- **One real bug, found by the gate and fixed.** P112's reply of four items
  to three string variables was accepted where ECMA-55 asks again: the "too
  many items" check sat behind the string branch.
- **The four games the old interpreter never finished:**
  - **bunny** now matches its corpus capture byte for byte. The GOSUB return
    point is a statement index, as designed.
  - **gomoko** and **lunar** end where their captures end: the capture says
    "Error on line N: No more input", and ours says `*** UNSUPPORTED: Out of
    input`.
  - **footbal2** uses RND.

## What the probes established

Small Roc programs on the default platform, with `strace` counting `mmap`
calls: every heap allocation there is one call
([roc-lang/roc#11335](https://github.com/roc-lang/roc/issues/11335)).
Each loop is 100,000 iterations.

| shape | mmap |
|---|---|
| read-only recursive evaluator, then a store into the machine | 7 |
| a non-recursive `step` called from a recursive loop, or from `while` over `var $m` | 6 |
| a tail-recursive helper that updates the machine and returns it, then a store | 200,004 |
| the same helper not tail-recursive | 200,004 |
| a `for` loop updating `var $m`, then a store | 200,005 |
| a loop over the screen's list (recursive or `for`), called from a step | 7 |
| `Vec`, 1,000,000 entries: 100,000 sets, then the same 100,000 again | 21,265 both times |
| a 16 MB `Vec(U8)`, 100,000 sets at one address | 11 |
| a vector of arrays, each holding its own vector of cells: take out, set, put back | 9 |

So the machine follows three rules:

1. The only loop that takes the machine and hands it back is the run loop.
2. Every other loop works on a piece of the machine, or only reads it.
3. The evaluator reads.

READ, INPUT and DIM store one item per step (`part` counts them), so no
statement loops over the machine.

## Dispatch had to be a table of calls

The first build allocated 2 per `NEXT`: 200,059 for a 100,000-iteration
FOR/NEXT loop, against the old interpreter's 35.

- Four guesses changed nothing: NEXT's `for` loop, the fuel record update,
  how the statement is fetched, and NEXT's `List.sublist`.
- Neither did the suspicious arms of `exec`: DEF's `?? m.defined`, the jumps
  that name `m` twice, and READ/DIM's `m.part`.

Cutting `exec`'s match arms, counted on 10,000 FOR/NEXT iterations:

| variant | mmap |
|---|---|
| all 25 arms, bodies inline | 20,038 |
| NEXT dispatched in `step` directly, the rest through `exec` | 38 |
| For/Next/End plus any one quarter of the other arms | 38 each |
| For/Next/End plus either half | 20,038 each |
| all 25 arms, each body its own function | 38 |

No arm causes it; the size of `exec` does. `exec` is now a table of one-line
calls, with a comment saying so and that the mechanism is Roc's and unknown.
Moving the program out of the machine record did not matter (20,038).

## The pathological programs

`basic/allocs.sh` runs `basic/pathological/*.bas`, one process each.

| program | new: mmap | old: mmap | new, dev: ms | old, speed: ms |
|---|---|---|---|---|
| x-plus-one (100,000 × `X=X+1`) | 75 | 100,043 | 797 | 2,080 |
| for-next (100,000) | 60 | 35 | 217 | 85 |
| goto-loop (100,000 × `I=I+1` + IF) | 66 | 100,038 | 1,298 | 3,059 |
| if-false (100,000) | 63 | 36 | 853 | 938 |
| many-vars (286 names × 350) | 1,543 | 50,398 | 345 | 1,942 |
| gosub-deep (1,000) | 86 | 2,043 | 21 | 68 |
| nested-for (100³) | 30,385 | 20,254 | 2,600 | 1,152 |
| big-array (DIM 10,000; 100,000 RND updates) | 220,442 | 320,061 | 6,111 | 7,525 |
| poke (100,000) | 427,554 | 239,938 | 7,155 | 14,814 |
| print (10,000) | 10,084 | 50,009 | 260 | 615 |
| string-growth (10,000) | 10,054 | 20,021 | 241 | 281 |

The new interpreter's times are its dev build, measured while the gate was
running on the same two cores. They are not a comparison with the old
interpreter's speed build; speed numbers follow.

## What still copies

Counted on the dev build, 10,000 iterations each:

| statement | mmap per execution |
|---|---|
| `X=A(5)`, `IF A(5)<>3`, `X=INT(RND(1)*10)`, `POKE 1024,7` (screen) | 0 |
| `A(5)=I` (array store) | 2 |
| `POKE 262144,7` (memory) | 5, the full depth of the 16 MB vector |
| `FOR K=1 TO 1` entered again inside a loop | 3 |
| `PRINT I` | 1: `Str.to_utf8` of the line to draw it; the builtins have no byte walk over a `Str` |

`Vec` alone does not copy in either layout (the last two probe rows above).
So something in the machine makes `mem` and `arrs` referred to twice at the
store. The cuts, each a separate dev build counted on the array-store and
POKE loops:

| cut | array store | POKE |
|---|---|---|
| as built | 20,064 | 50,052 |
| POKE's memory branch its own function | 20,064 | 50,052 |
| array store through `Vec.update` (take out, change, put back) | 40,063 | 50,052 |
| FOR's loop list by length, helpers for enter and skip | — | — (the program overflowed the stack) |
| POKE without `settle` | 20,064 | **56** |
| POKE without `settle`, constant operands | 20,064 | **56** |
| array store without `settle` | 40,063 | 50,052 |
| `settle` without taking `arrs` out beside the machine | 20,064 | 50,052 |
| `settle` without `emit` | 20,064 | 50,052 |
| `settle` without its record building | 20,064 | 50,052 |
| `settle` with a fast path `{ ..m, seed }` | 20,064 | 50,052 |
| `poke_at` and `set_arr` as tables of calls, with and without the fast path | 20,064 | 50,052 |

POKE stops copying only when `settle` is not called at all. Nothing inside
`settle` is responsible. I stopped here rather than keep reshaping code
around a mechanism I cannot see. Each remaining copy is bounded: a path of
32-entry nodes, never a table.

## The Roc compiler building it

- **Dev:** `BasicRun.roc` builds in 4 s.
- **Speed:** the first build failed after about 8 minutes, unable to write its
  static data object under `/tmp/roc`. Dev builds were running in the same
  temp directory at the time, which is the likely cause.
- **Speed, second attempt:** it has run for more than 7 minutes, where the old
  interpreter took 67 s (61 s of it LLVM). It is not attributed yet.

## Open

- The copies in array stores, POKE and a re-entered FOR, and why calling
  `settle` makes them.
- P134 still times out (20 s, dev build). It is array stores and reads in a
  loop, so it waits on the first item.
- The speed build's time, and the speed timings of the table above.
- The page, moved onto the new machine; and `ladder.sh`, moved onto
  `basic-run`.
