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

The new interpreter's dev-build times above were measured while the gate was
running on the same two cores. Its speed build (commit `3167c82`), with the box
otherwise idle:

| program | mmap | new, speed: ms | old, speed: ms |
|---|---|---|---|
| x-plus-one | 74 | 366 | 2,080 |
| for-next | 59 | 57 | 85 |
| goto-loop | 65 | 624 | 3,059 |
| if-false | 62 | 293 | 938 |
| many-vars | 1,542 | 166 | 1,942 |
| gosub-deep | 1,077 | 24 | 68 |
| nested-for | 30,384 | 871 | 1,152 |
| big-array | 220,442 | 4,022 | 7,525 |
| poke | 402,478 | 6,137 | 14,814 |
| print | 10,083 | 139 | 615 |
| string-growth | 10,053 | 174 | 281 |

Faster than the old interpreter on every program, and still not fast enough.

- `IF` and `GOTO` cost about 3 to 6 µs a statement. FOR/NEXT costs 0.6 µs.
- big-array and poke are over a second, and they are exactly the copying
  statements.
- **The 3.7 µs for `X=X+1` is copying the machine.** `perf record` on
  x-plus-one, speed build: 54% of samples are in `defaultMemcpy` and 7% in
  `defaultMemset`, called from the run loop and two statement-level procs.
  Every `memcpy` call in those two procs is passed `0x2d8`, which is 728
  bytes: the machine record, 45 fields, 16 of them lists. A record update
  copies all of it, and a statement makes several. The next change shrinks
  what is copied: the fields no statement writes (the program, its tables,
  DATA, the replies, the dialect) go behind one `Box`.

## The control ladder (Steve: well-behaved programs first)

Pathological programs say that something is slow, not which feature made it
so. `basic/controls/` is a ladder of the smallest programs, each adding one
thing to the one before: an empty loop, `LET X=1`, `X=X+1`, an IF, a GOTO, a
GOSUB, an array read, an array store, PEEK, POKE, READ, and so on.
`basic/controls.sh` runs each at 1,000 and at 10,000 iterations. What changes
between the two mmap counts, over the extra 9,000 iterations, is what one
iteration allocates. Each rung is held to 0, or to a number written beside
its reason in `controls/expected.txt`. A change that makes a rung start
allocating names its feature.

Allocations per iteration, dev builds (**no LLVM builds**: the speed backend
spent 650 s in LLVM, and the problems here are the code's shape, which the dev
backend shows the same):

| rung | old interpreter | Machine, first gated | now (`50e919b`) |
|---|---|---|---|
| FOR/NEXT, LET, X=X+1, IF, GOTO | 0–1 | 0 | 0 |
| GOSUB | 1 | 1 | **0** |
| string LET, RND, PEEK, array read | 1 | 0 | 0 |
| DEF FN call | 2 | 2 | 1 |
| array store | 2 | 2 | **0** |
| POKE into memory | 2 | 5 | **0** |
| POKE into the screen | — | 0 | 0 |
| READ, READ into an array | 0, 2 | 2, 2 | **0, 0** |
| FOR entered again inside a loop | 2 | 3 | 2 |
| PRINT (the bytes it draws) | 5 | 1 | 1 |

What fixed each:

- **The program is not state.** Everything that does not change after the
  scan (statements, line tables, FOR skips, DEFs, DECLs, DATA, dialect) is
  `Parse.Program`, passed beside the machine, not kept in it.
- **POKE, array stores and READ write the machine they were given** when the
  evaluation had nothing to apply (no report, no stop, no array to make, no
  random number drawn). Writing the machine `settle` answered made them copy;
  why is being reduced separately, starting from the smallest program.
- **An array is taken out of its vector and put back** inside a helper called
  in the record update, as NEXT writes `nums`.
- **The return points and the open loops are a list and a depth.** A GOSUB and
  its RETURN pushed and popped a list back to empty, which allocated every
  time; popping now lowers the depth and pushing overwrites the entry.

Gate after each: NBS 207 identical (P134 finishes now, the old one never did),
games 95 identical.

## The ladder, grown (fifteen more rungs)

ON GOTO, ON GOSUB, a string comparison, LEFT$, MID$, CHR$, LEN, INT, `^`, `/`,
TAB in PRINT, nested GOSUB, a DIM passed through again, VAL and INPUT (one
reply line an iteration). On the committed machine (`7979adf`):

| rung | allocations an iteration | why |
|---|---|---|
| all the rest | 0 | |
| CHR$ | 0, from 1 | it built a one-byte list to make its string; it now indexes a table of the 256 one-character strings |
| DIM passed through again | 0, from 1 | it built the array's cells before asking whether the array existed |
| PRINT, PRINT with `;`, PRINT with TAB | 1 | the text is turned into bytes to draw it (`Str.to_utf8`) |
| string growth | 1 | the string grows |
| DEF FN call | 1 | the parameter binding appends to a list |
| INPUT | 3 | two `Str.to_utf8` and one list growing |
| **FOR entered again** | **2** | **not explained** |

The reasons in `controls/expected.txt` are measured. `basic/stacks.py` reads
an `strace -f -k` trace and counts each allocation under the first builtin on
its stack: INPUT's 3,080 allocations over 1,000 iterations are 2,000
`str_to_utf8` and 1,055 `list_reserve`; DEF FN's 1,056 are 1,027
`list_reserve`. A first reading of INPUT's three as "three texts drawn" was
wrong, and so was the first count: an awk loop that read ahead into the next
call's line counted only every other allocation. The parser in `stacks.py`
assigns every call.

## The copy, reduced, and the last rung fixed

A cold agent reduced the copy behind POKE, from a program that does not copy,
one ingredient of the machine at a time (154 dev builds, 28 minutes). The
smallest program is 19 lines and is kept in
`roc-apps/findings/helper-arg-copy/`, with `run.sh`:

| variant | mmap for 10,000 stores |
|---|---|
| `d = settle(m, m.fuel)`, then the store on `d` | 50,006 |
| `d = settle(m, 0)` | 10 |
| the store on `m` | 10 |

**The copy needs all four together:**

1. a helper given the record and a second argument read from it;
2. a caller passing a freshly updated record;
3. the store in its own function;
4. the store going through a union of more than one tag holding lists (the
   vector's tree).

What the helper does is irrelevant: `settle` is `|m, _x| m`. The hypothesis,
not verified: reading from the record after passing it makes the compiler
treat it as borrowed across the call.

**That named the last rung.** `enter_for` was given the machine and a frame
built from `m.pc + 1`. Reading `m.pc` inside instead took "FOR entered again"
from 2 allocations an iteration to 0. **The ladder now has no rung off**:
every control allocates nothing an iteration, or exactly its measured reason
(PRINT's bytes, a string growing, a DEF binding, INPUT's two conversions and a
list).

## The games' captures, and a harness bug

- **The captures are basic101's.** The games directory came into sehugg's
  test repository from github.com/wconrad/basic101, a Ruby BASIC-80
  interpreter, as its expected output. So basic101's source is the
  microcomputer dialect's specification. It prints an integer's digits and any
  other number as C's `%.7g`, where this machine had printed ECMA-55's six
  digits. With that, `rocket` matches its capture, `lem` and `target` come
  closer, and no game moves away. ECMA-55 keeps six digits; NBS is unchanged.
- **`banner` was a harness bug.** Its replies end in an empty line (Enter at
  SET PAGE), and `$(cat file)` drops trailing newlines, so `run.sh` gave it one
  reply too few. `run.sh` now reads each text with a marker after it and cuts
  the marker.
- **The grading ladder runs through `basic-run`.** No Roc app per program:
  games grade in 4.4 s, NBS in 46 s. NBS 195 PASS, 13 UNJUDGED (reader rows),
  none failing; games 12 of 99.

## Where the time goes now

`perf` on P134 (the one corpus program still over ten seconds, dev build):
14% in the run loop and 25% in `list_incref`/`list_decref`. So allocation is
no longer most of the cost.

**The width of the machine record is not the rest of it either.** A
standalone probe times 1,000,000 steps, each storing one number into a
record's vector, with the record carrying 2 lists and then 16:

| record | dev build |
|---|---|
| 2 lists | 365 ms |
| 16 lists | 434 ms |

Fourteen extra counted fields cost 0.07 µs a step, and a whole minimal step
costs 0.36 µs. The machine spends about 3.5 µs a statement (x-plus-one: 703 ms
for 100,000 iterations of two statements). An earlier version of this note
said the record's width was the cost; this probe says it is at most a fifth of
it.

`perf` on a dev build with debug info puts the time on source lines: the run
loop's `{ ..$m, fuel, steps }` about 7%, `settle` and `emit` about 12%, the
store in `do_set_num` about 8%, dispatch 4%. Three changes aimed at those,
measured on the dev build (best of three) and on the ladder:

| variant | x-plus-one | goto-loop | if-false | ladder |
|---|---|---|---|---|
| as committed | 703 ms | 1,074 ms | 765 ms | 2 rungs off |
| A: a variable read skips the empty DEF environment | 723 ms | 1,043 ms | 732 ms | — |
| A + fuel counted in a local of the run loop | 2,736 ms | 928 ms | 2,832 ms | **every rung 2 an iteration** |
| + LET, IF and PRINT write the machine they were given | 5,029 ms | 3,122 ms | 2,750 ms | every rung 2–7 |

None is kept. Counting the fuel in the run loop instead of the machine made
even the bare FOR/NEXT loop copy on every statement. **The ladder named that
at once, where the timings alone said only "slower".** The shapes that make
Roc keep the machine's lists unshared are being reduced separately, from the
smallest program up, before any more reshaping.

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
- **Speed, second attempt:** it built in **694 s**, where the old interpreter
  takes 67 s. A third build with `--timings` (667 s) attributes it:

  | phase | new interpreter | old interpreter |
  |---|---|---|
  | LLVM Optimize + Emit | 650.6 s | 61.2 s |
  | ARC | 9.9 s | 1.8 s |
  | Specializing, in all | 14.9 s | 5.7 s |
  | Type Checking | 0.8 s | 0.2 s |
  | peak RSS | 1.4 GB | 0.7 GB |

  Nearly all of it is LLVM. Whether the 728-byte machine record copied
  throughout the generated code is what LLVM spends its time on is not
  measured yet; shrinking the record will show whether the build time
  moves with it.

## Open

- The copies in array stores, POKE and a re-entered FOR, and why calling
  `settle` makes them.
- P134 still times out (20 s, dev build). It is array stores and reads in a
  loop, so it waits on the first item.
- The speed build's time, and the speed timings of the table above.
- The page, moved onto the new machine; and `ladder.sh`, moved onto
  `basic-run`.
