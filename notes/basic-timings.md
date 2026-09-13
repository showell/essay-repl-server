# Every BASIC program, timed: where P134's 12.9 seconds went

Every corpus program (208 NBS, 99 games) run once through the BASIC
interpreter with its time, the statements it executed and its allocations
recorded. P134 was the question; the run answers it, and shows a second cost
nobody had looked at.

---

## What it says

**P134 is not a slow statement; it is a lot of them.** It executes 1,742,747
statements, at 7.40 µs each, which is 12.9 s. The median over every program
that runs at least 10,000 statements is 8.85 µs, and P134 is below it. The five
programs over a second are all the same kind: hundreds of thousands to 1.7
million statements at 6 to 9 µs. So the bottom of P134 is **the cost of one
statement**, about 45,000 CPU cycles on this box, and not anything particular
to P134. Allocation is not that cost: P134's 45,676 mmaps over 1.7 million
statements is one allocation per 38 statements.

**A second cost: loading.** Many NBS programs run a few hundred statements yet
take 200 to 400 ms and make 20,000 to 40,000 allocations. P095 runs 184
statements in 377 ms with 39,357 mmaps. **Measured:** the same listings run in
the microcomputer dialect, which skips ECMA-55's load-time checks (`Listing`,
`Program`), take 15 to 29 ms:

| program | ECMA-55 | microcomputer | statements run |
|---|---|---|---|
| P095 | 373 ms | 15 ms | 184 |
| P024 | 290 ms | 20 ms | 396 |
| P018 | 306 ms | 16 ms | 390 |
| P019 | 357 ms | 19 ms | 782 |
| P027 | 385 ms | 29 ms | 1,678 |
| P151 | 175 ms | 18 ms | 155 |
| P011 | 184 ms | 16 ms | 183 |

Best of three each. So the checks cost 150 to 370 ms a program, and parsing
and running are the other 15 to 30. What in the checks costs that is next.

## P134, looked at closer

**What it executes.** An instrumented build (scratch only) counted P134's
statements by kind:

| statement | executed | share |
|---|---|---|
| IF … THEN line | 691,970 | 39.7% |
| NEXT | 446,028 | 25.6% |
| LET of a number | 301,701 | 17.3% |
| an array element stored | 211,666 | 12.1% |
| REM, GOTO, FOR, GOSUB, RETURN, PRINT | 91,382 | 5.2% |

It is a sort. Its IFs compare array elements (`IF P(J1)<=P(J1+1) THEN 850`)
and its stores swap them.

**Where a statement's 7.4 µs goes, as far as it can be seen.** `perf` on a dev
build with debug info, by symbol: 18% in the run loop's compiled code, and
**29% in list reference counting** (`list_incref` 15%, `list_decref` 14%): the
machine record and the evaluation's effects being copied and counted up and
down. **By source line the profile cannot be trusted:** counting time spent in
the functions a line calls, it gives 27% to `dim_one` and 8 to 9% each to
`Parse.resolve` and `Parse.text_of`. All three run once, at load, in a
13-second run whose load is a few milliseconds. The dev backend's line tables
put generated code under the wrong lines, so no claim here rests on them. The
ladder's rungs are the instrument instead (next section).

## Skipping `settle` when there is nothing to apply

`settle` applies what an evaluation did (its reports, a stop, arrays it made,
random numbers it drew) and rebuilds the machine record, after every
evaluation, whether there is anything to apply or not. In P134, IF (40% of its
statements) and LET (17%) always went through it. Array stores already skipped
it.

Two versions, measured against the committed build on the dev backend. Each
rung is 100,000 iterations, best of three; P134 is best of two.

| | committed | quiet | plain | quiet2 |
|---|---|---|---|---|
| `LET X=1` | 6.07 µs | 5.28 | 5.47 | 5.32 |
| `X=X+1` | 7.51 | 6.58 | 7.05 | 6.87 |
| `IF I<0 THEN` (false) | 7.93 | 7.06 | 7.09 | 7.19 |
| `IF I>0 THEN` (true) | 8.24 | 7.59 | 7.78 | 7.65 |
| `IF P(5)<>3 THEN` | 10.11 | 9.47 | 9.46 | 9.74 |
| `IF P(5)<=P(6) THEN` | 12.30 | 11.57 | 11.91 | 11.75 |
| `LET X1=INT(1100*0.5)` | 8.10 | 7.38 | 7.52 | 7.87 |
| `X=RND(1)` | 8.37 µs, 0 allocations | **29.50 µs, 2 allocations** | **29.87 µs, 2 allocations** | 7.43 µs, 0 allocations |
| P134 | 12,690 ms | 11,957 ms | 13,029 ms | 12,192 ms |

- **quiet:** IF and LET write the machine they were given when the evaluation
  reported nothing, stopped nothing, made no array and drew no Twister
  number; LET writes the new LCG seed in the same record update.
- **plain:** the same, but a LET whose seed changed goes through `settle`.
- **quiet2:** quiet, and a LET that drew from the Twister writes the Twister's
  state in the same record update, so only a report, a stop or a new array
  goes through `settle`.

A LET or an IF gets 0.6 to 0.9 µs cheaper, and P134 6% faster (quiet). But
**a LET that draws from the Twister now copies the path of `nums` on every
execution** in both versions, although its slow path is the code it had
before; only the fast branch beside it is new. That is the shape sensitivity
in `findings/helper-arg-copy`, and the ladder caught it on its first run.

**quiet2 is the one kept.** The ladder shows no rung off, RND is cheaper than
before (8.37 to 7.43 µs), and each LET or IF is 0.4 to 0.8 µs cheaper. P134 is
4% faster: 12,690 to 12,192 ms. Between runs of the same build, P134 varies by
about 2%, which is why quiet (11,957) and quiet2 cannot be told apart on it.
**This is a small step.** A statement is still 7 µs, so the evaluation's
scaffolding was not most of it.

## Reading an array element

An array read added about 2.3 µs over the same IF without one, and P134's
sort does two such reads on every one of its 232,332 comparisons.

**Was taking the array out of its vector load-bearing? For a read, no.** `elem`
needs the array's width, its cell count and one cell. It took them by
`Vec.get`-ting the whole array record out of the machine's vector of arrays,
because in Roc that is how a field of something inside a list is reached.
That "copy" is small: two integers and a vector handle, with the cells tree's
reference count going up and back down. No cells are copied. A *store* is
different: it has to take the array out with `replace` and put it back, or
the cells tree would be shared and copied. So the take-out is load-bearing on
the write path and never was on the read path.

Two ways in, each measured against the committed build (dev backend, 100,000
iterations, best of three; P134 best of two):

1. **No fill value.** `Vec.get(m.arrs, slot, Machine.no_arr)` hands `no_arr`,
   a constant holding a vector, to every call, although the slot is always in
   range. `Vec.at` takes no fill value.
2. **One cell space.** Every array's cells live in one machine-wide vector of
   16,777,216 cells, as POKE's memory does. An array is three integers: width,
   cell count, and `off`, where its cells start. A new array takes the next
   stretch from `cells_top`. A read is one walk; a store is one `Vec.set`, with
   no take-out and no put-back.

| | committed | `Vec.at` | one cell space |
|---|---|---|---|
| `IF I<0 THEN` (no array) | 7.42 µs | 7.25 | 7.62 |
| `X=A(5)` | 7.54 | 7.38 | 8.01 |
| `A(5)=I` | 9.31 | 9.18 | 9.01 |
| `IF P(5)<>3 THEN` | 9.78 | 9.41 | 10.32 |
| `IF P(5)<=P(6) THEN` | 12.03 | 11.59 | 13.04 |
| `P(5)=P(6)` | 11.20 | 11.18 | 11.50 |
| P134 | 12,230 ms | 12,005 ms | 12,822 ms |

The fill value was 0.2 to 0.4 µs a read, and P134 moved 1.8%, inside the 2% it
varies between runs. `Vec.at` is kept: it is a small, clean step, gated and
committed.

**One cell space reads slower, and is not kept.** Its stores gain a little (9.31
to 9.01 µs), but its reads lose more (the IF on two elements 12.03 to 13.04 µs),
and P134 is 5% slower. Not measured, but the likely reason: a read walks five
levels of a 16-million-cell tree, where before it walked two levels to the array
and one into its cells. So the array record coming out of its vector was not what
an array read costs. What is left is the evaluation around it: the subscript's
own evaluation, the records that carry it, and the tree walks.

**The noise, stated.** The same control, `IF I<0 THEN`, measured 7.93 µs in one
job and 7.42 µs in another, on the same build. Only a comparison run back to back
in one job is worth reading, and a difference under a few percent is not.

## Evaluating without the effects record: P134 12.3 s to 7.5 s

Every evaluation carried an effects record through every expression node: the
seed, the reports printed, why it stopped, the arrays it made, the random
numbers drawn. Four of those fields are reference-counted, so every node
counted them up and down. In P134, almost no statement ever has an effect.

**The change is not a smaller record; in the common case there is none.**
`fast` evaluates a numeric expression (numbers, variables, array elements,
`+ - * / ^`, a sign, the numeric functions, PEEK) and answers `Got(value)`, or
`Slow` the moment the full evaluator would have anything to record: an
overflow or a division by zero to report, a random number, an array used
before it exists, a subscript out of range, a string, a DEF call. A LET, an
IF and an array store try `fast` first; on `Slow` they run exactly the code
they had before. **Evaluating twice is safe because evaluation only reads the
machine**: nothing was written between the two. The read-only evaluator from
the design is what makes this possible.

**How it was checked.** A second build ran the full evaluator beside every
`Got` and crashed on any difference in the value or in its effects. All 208
NBS programs, all 99 games and every control went through it:

- no difference;
- no crash or timeout;
- every transcript identical to the committed ladder's;
- the allocation ladder still at none off.

Measured back to back against the committed build (dev backend, 100,000
iterations, best of three; P134 best of two):

| | committed | fast |
|---|---|---|
| NEXT (no evaluation) | 2.10 µs | 2.08 |
| `LET X=1` | 5.23 | 4.42 |
| `X=X+1` | 6.70 | 5.11 |
| `IF I<0 THEN` (false) | 7.20 | 4.87 |
| `IF I>0 THEN` (true) | 7.60 | 4.94 |
| `X=A(5)` | 7.41 | 5.37 |
| `A(5)=I` | 9.21 | 6.99 |
| `IF P(5)<>3 THEN` | 9.58 | 5.75 |
| `IF P(5)<=P(6) THEN` | 11.40 | 6.65 |
| `LET X1=INT(1100*0.5)` | 7.32 | 5.32 |
| `P(5)=P(6)` | 11.07 | 7.72 |
| `IF I-5<1 THEN` | 8.73 | 5.52 |
| **P134** | **12,321 ms** | **7,527 ms** |

P134 is 39% faster, and its sort's comparison, the line it runs 232,332 times,
went from 11.4 to 6.7 µs. **So the effects record was the largest single cost
in a statement,** larger than the machine record's copies and larger than the
array read.

## The fast path, checked for good

The fast path answers a LET, an IF or an array store without the effects
record, and hands anything else to the full evaluator. It is right only if
every answer it gives is the one the full evaluator would give. That was
checked once, by a scratch patch. **It is now a tool.**

`basic-check` (`basic/roc/BasicCheck.roc`) is basic-run with a run loop of its
own, so basic-run's loop is untouched. Wherever the fast path answers, the
statement runs both ways from the same machine, and the two machines are
compared on everything such a statement can write: where the program goes
next, whether and why it stopped, the random number state, the arrays made,
the output, the stacks, and the variable or cells it names, a number by its
bits. A difference stops the program with `fast differs on line N` and both
machines. `basic/check-fast.sh` runs every corpus program and every control
through basic-check and basic-run. It reports how many fast answers it
compared, the programs where fast differed, and any transcript that is not
basic-run's.

**Broken on purpose first.** `quick` refuses a value past the largest number,
so the full evaluator can report the overflow. It was changed to pass
everything. Of 836,228 fast answers compared, the check stopped four NBS
programs, each at the statement: P029 line 260, P030 line 360, P035 line 250
and P122 line 250, the overflow tests. It listed the same four transcripts as
unlike basic-run's.

**Its first version cost ten times a statement.** It built each machine's
summary as text for every statement. Both runs also started from a machine
still referred to, so each copied the path it wrote. P134 did not finish in
120 s. Three changes brought the cost down:

- the summaries are records of numbers, turned into text only when they differ;
- the full evaluator's run gets the machine last, so it writes in place;
- only the fast path's run still copies, once, because two machines have to exist.

Dev backend, 100,000 iterations, best of two, each pair from one job:

| | basic-run | basic-check, text | basic-run | basic-check, records |
|---|---|---|---|---|
| `LET X=1` | 4.50 µs, 0 mmap | 84.32 µs, 8 | 4.38, 0 | 32.01, 2 |
| `IF I<0 THEN` | 4.80, 0 | 52.29, 4 | 4.88, 0 | 12.05, 0 |
| `A(5)=I` | 6.97, 0 | 135.28, 12 | 6.97, 0 | 53.62, 3 |
| `IF P(5)<=P(6) THEN` | 6.65, 0 | 63.83, 4 | 6.72, 0 | 19.78, 0 |

**Unbroken, it agrees everywhere.** 2,011,762 fast answers were compared over
230 programs, corpus and controls. No program differed, every transcript was
basic-run's, and nothing timed out. P134 compared 1,175,337 of its 1,742,747
statements and took 47.7 s, against basic-run's 7.8 s. The whole check, both
executables over both corpora and the controls, takes 145 s.

To take the check apart, `run_measured` became three pieces that basic-run
and basic-check share: `loaded` (the listing checked and parsed), `started`
(the machine before its first statement) and `ended` (the transcript). The
command-line cleaning moved to `CommandLine`. basic-run's transcripts are
byte-identical to the committed build's on all 208 NBS and 99 games programs.
The ladder is 0 off.

## A step's cost is the machine record's width

Before a statement does its own work, the step pays for the machine record:
the run loop builds a fresh one for `fuel` and `steps`, and the statement
builds another. `perf` puts 22% of a bare FOR/NEXT loop in list reference
counting.

**The run loop's fresh record is load-bearing.** Two loops that hand the step
`$m` itself make every statement's store copy. One has no fuel and the other
counts fuel in a local. The cost is 2 allocations a NEXT, and P134 goes from
7.4 s to 37 s. The loop keeps its record update, with a comment saying why
(d0318fd).

**What the record costs, found by padding it.** Fifteen fields are added to
the machine record, and nothing reads or writes them. Dev backend, 100,000
iterations, best of three, one job; no variant allocates.

| | committed | + 15 lists | + 15 lists behind one reference | + 15 lists in a nested record |
|---|---|---|---|---|
| bare FOR/NEXT | 2.15 µs | 2.76 | 2.24 | 2.74 |
| `LET X=1` | 4.46 | 6.24 | 4.39 | 5.62 |
| `IF I<0 THEN` | 4.98 | 6.74 | 4.98 | 6.75 |
| `A(5)=I` | 6.95 | 9.30 | 7.32 | 9.47 |
| P134 | 7,443 ms | 10,010 | 7,498 | 9,564 |

In an earlier job, fifteen integers made P134 8,289 ms against 7,329, and the
same rungs 0.3 to 1.1 µs slower.

- Each list in the record costs about 60 ns a statement, about three times
  what an integer costs.
- **Behind one reference** (a one-element list of a record), fifteen lists
  cost nothing measurable. **In a nested record** held inline, they cost as
  much as loose fields.
- The machine record holds 15 lists and vectors today, and about 20 integers
  and flags.

**The plan:** split the machine into the state statements change every time
and the rest, behind one reference: the screen, memory, output, input and the
Twister's table. The padding predicts most of 60 ns a statement for each list
that moves. That is a prediction, not a measurement.

## P134, statement by statement

A scratch build counted every statement index P134 executes. By section of
the program:

| section | lines | statements | share |
|---|---|---|---|
| bubble-sort each group, back and forth | 740–920 | 741,416 | 42.5% |
| place 1,000 RND values, probing outward for a free slot | 380–590 | 573,104 | 32.9% |
| K+ and K− on the sorted data | 1000–1170 | 152,114 | 8.7% |
| compress out the empty slots | 930–990 | 126,024 | 7.2% |
| find the groups | 600–730 | 80,393 | 4.6% |
| mark 1,100 slots empty | 330–370 | 66,061 | 3.8% |
| the summary test on the 30 results | 1180–1770 | 3,602 | 0.2% |

The busiest lines:

| line | executed | |
|---|---|---|
| 800 | 232,332 | `IF P(J1)<=P(J1+1) THEN 850` |
| 850 | 232,332 | `NEXT J1` |
| 470 | 70,285 | `IF X1-J<1 THEN 510` |
| 480 | 68,349 | `IF P(X1-J)<>3 THEN 510` |
| 510 | 62,132 | `IF X1+J>N8 THEN 550` |
| 520 | 61,965 | `IF P(X1+J)<>3 THEN 550` |
| 810–840 | 58,876 each | the swap: `A3=9`, `W=P(J1)`, `P(J1)=P(J1+1)`, `P(J1+1)=W` |
| 550 | 56,648 | `NEXT J` |

**So P134 is doing exactly its own work.** The sort within groups is
quadratic, and the probe walks outward from each value's slot. Together those
are 75% of the statements. The program's result is real: all 30 statistics
and both summary tests fall inside its bounds, and it prints `*** TEST PASSED
***`. Making P134 faster means making those four IFs, one NEXT and four LETs
cheaper, which is making every statement cheaper.

## A statement's cost, rung by rung

The ladder's rungs are one-statement programs, so timing them gives each kind
of statement's cost, with no profiler involved. Each ran 100,000 iterations,
best of three, on the dev build. From each is taken the bare FOR/NEXT loop,
2.08 µs an iteration (whose one statement is the NEXT). The programs marked
*P134-shaped* are its own kinds of statement, written as rungs.

| statement | µs |
|---|---|
| NEXT (the bare loop) | 2.08 |
| GOTO | 2.33 |
| `LET X=1` | 3.96 |
| GOSUB and RETURN, each | ~2.0 |
| `LET X=I` | 4.15 |
| `X=X+1` | 5.42 |
| `IF I<0 THEN` (false) | 5.79 |
| `LET X1=INT(1100*0.5)` *P134-shaped* | 6.18 |
| `IF I>0 THEN` (true, jumps) | 6.19 |
| `A(5)=I` | 6.96 |
| `IF I-5<1 THEN` *P134-shaped* | 7.14 |
| `IF P(5)<>3 THEN` *P134-shaped* | 8.09 |
| `P(5)=P(6)` *P134-shaped* | 8.73 |
| `IF P(5)<=P(6) THEN` *P134-shaped* | 10.16 |
| `A$=A$+"X"` | 54.94 |
| a DEF FN call | 19.53 |

**Checked against P134.** P134's counts times these costs are about 9.5 s:
IF 692,000 at about 7.5 µs is 5.2 s; NEXT 446,000 at 2.08 is 0.9 s; LET 302,000
at about 5 is 1.5 s; array stores 212,000 at about 8 is 1.7 s; the rest 0.2 s.
It measures 12.9 s. The rungs account for three quarters. The rest is not
measured; P134's expressions are larger than the rungs' (`P(J1+1)`, `N8*X`),
which is the likely difference.

**What a statement costs is mostly not the BASIC.** `LET X=1` does less than
NEXT (NEXT finds its loop, reads and writes the variable, tests the limit), yet
costs twice as much. What `LET X=1` has that NEXT does not is an evaluation: a
fresh effects record carried through the evaluator, and `settle` rebuilding the
machine record after it. That is about 2 µs on every statement that evaluates
anything, which is 95% of P134's. Each operator, variable read or array access
then adds 0.5 to 2.5 µs.

So P134's 12.9 s is, in round numbers:

- **a step**, dispatch and the run loop's record update: about 2 µs × 1.74
  million = 3.6 s;
- **the evaluation scaffolding**, the effects record and `settle`: about 2 µs ×
  1.65 million = 3.3 s;
- **the expressions themselves**, array reads and arithmetic: the rest, about
  6 s.

## The load, found

**ECMA-55's checks turn keywords into byte lists, one allocation per keyword
tried.** P095 makes 39,335 allocations in the ECMA-55 dialect and 909 in the
microcomputer dialect. `strace -k`, counted by `basic/stacks.py`, puts 37,243
of the 39,335 in `Str.to_utf8`. Reading the check shows why:

- `Listing.starts(b, i, w)` is `starts_from(b, i, Str.to_utf8(w), 0)`: every
  word it tries becomes a new list.
- `Listing.first_kw` tries up to 25 keywords for each statement.
- `Program.tokens` tries up to 50 known words for every word in the program.

About 200 conversions a statement, each an `mmap` and a `munmap` on this
platform, is 150 to 370 ms before the first statement runs. The fix is to
compare the text without converting it; its measurement is to come.

## How it was measured

- **The interpreter:** `basic-run`, built once by the Roc compiler with the
  dev backend (no LLVM), from roc-apps branch `basic-machine` at `4e81cc4`.
  Every number below is this interpreter running a BASIC program. None of it
  is the Roc compiler.
- **One process a program**, run by `basic/timings.sh`, with nothing else
  running on the box (2 cores). NBS programs run in the ECMA-55 dialect, the
  games in the microcomputer dialect, each with the replies the ladder gives
  it. The limit is 60 s.
- **Wall time** is the process alone, from a clean run: start, read the
  listing, check it (ECMA-55), parse it, run it, write the transcript.
- **Statements run** is the machine's own count of statements executed.
  `basic-run` reports it on stderr, so the transcript on stdout is untouched.
  µs a statement is wall time divided by that count. For a program that runs
  few statements, that figure is mostly process startup and the load, so the
  per-statement tables only include programs that ran at least 10,000.
- **mmap** is from a second run of the same program under `strace -c`. On
  Roc's default platform every heap allocation is one `mmap`, so this counts
  allocations without timing anything.
- **Program statements** is how many statements the program parses to.

## Totals

| suite | programs | wall time, all | statements run, all | median µs a statement (≥ 10,000 run) | over 1 s | timeouts |
|---|---|---|---|---|---|---|
| nbs | 208 | 36.5 s | 3,151,186 | 8.85 | 5 | 0 |
| games | 99 | 2.6 s | 141,491 | 8.97 | 0 | 0 |

## The slowest thirty

| suite | program | wall ms | statements run | µs a statement | mmap | program statements |
|---|---|---|---|---|---|---|
| nbs | P134 | 12,904.8 | 1,742,747 | 7.40 | 45,676 | 182 |
| nbs | P137 | 3,230.6 | 556,172 | 5.80 | 24,799 | 114 |
| nbs | P133 | 2,109.7 | 258,704 | 8.15 | 38,381 | 151 |
| nbs | P141 | 1,826.6 | 206,368 | 8.85 | 30,288 | 108 |
| nbs | P138 | 1,147.4 | 141,461 | 8.11 | 30,057 | 118 |
| nbs | P206 | 514.3 | 8,047 | 63.90 | 48,015 | 232 |
| nbs | P140 | 458.4 | 47,769 | 9.59 | 23,050 | 90 |
| nbs | P027 | 411.0 | 1,678 | 244.93 | 39,534 | 251 |
| nbs | P132 | 403.8 | 52,566 | 7.68 | 11,910 | 54 |
| nbs | P166 | 384.8 | 22,861 | 16.83 | 26,017 | 163 |
| nbs | P095 | 377.4 | 184 | 2,051.19 | 39,357 | 178 |
| nbs | P019 | 376.9 | 782 | 482.00 | 37,757 | 209 |
| nbs | P024 | 352.3 | 396 | 889.59 | 29,815 | 254 |
| nbs | P110 | 340.5 | 1,884 | 180.70 | 33,393 | 235 |
| nbs | P018 | 340.2 | 390 | 872.32 | 32,048 | 209 |
| nbs | P046 | 307.9 | 396 | 777.41 | 29,811 | 225 |
| nbs | P025 | 299.5 | 825 | 363.07 | 28,347 | 266 |
| nbs | P164 | 298.2 | 687 | 434.02 | 28,572 | 142 |
| nbs | P136 | 296.1 | 15,900 | 18.62 | 21,614 | 85 |
| nbs | P139 | 285.7 | 18,663 | 15.30 | 16,845 | 76 |
| nbs | P112 | 257.4 | 2,036 | 126.40 | 23,871 | 225 |
| nbs | P109 | 255.0 | 1,296 | 196.74 | 20,911 | 199 |
| nbs | P057 | 237.6 | 6,538 | 36.34 | 18,926 | 154 |
| nbs | P203 | 237.5 | 1,781 | 133.36 | 22,776 | 234 |
| nbs | P056 | 236.8 | 6,538 | 36.21 | 18,909 | 154 |
| nbs | P151 | 228.0 | 155 | 1,470.98 | 18,447 | 189 |
| nbs | P058 | 221.9 | 5,633 | 39.39 | 18,985 | 157 |
| nbs | P061 | 220.4 | 304 | 725.12 | 21,313 | 87 |
| nbs | P135 | 208.5 | 13,236 | 15.75 | 10,570 | 62 |
| nbs | P011 | 204.6 | 183 | 1,118.02 | 19,396 | 183 |

## The most expensive statements (programs that ran at least 10,000)

| suite | program | µs a statement | statements run | wall ms | mmap |
|---|---|---|---|---|---|
| nbs | P136 | 18.62 | 15,900 | 296.1 | 21,614 |
| nbs | P166 | 16.83 | 22,861 | 384.8 | 26,017 |
| nbs | P135 | 15.75 | 13,236 | 208.5 | 10,570 |
| nbs | P139 | 15.30 | 18,663 | 285.7 | 16,845 |
| nbs | P140 | 9.59 | 47,769 | 458.4 | 23,050 |
| games | war | 9.38 | 10,738 | 100.8 | 1,388 |
| nbs | P141 | 8.85 | 206,368 | 1,826.6 | 30,288 |
| games | footbal2 | 8.56 | 10,236 | 87.7 | 3,291 |
| nbs | P133 | 8.15 | 258,704 | 2,109.7 | 38,381 |
| nbs | P138 | 8.11 | 141,461 | 1,147.4 | 30,057 |
| nbs | P132 | 7.68 | 52,566 | 403.8 | 11,910 |
| nbs | P134 | 7.40 | 1,742,747 | 12,904.8 | 45,676 |
| nbs | P137 | 5.80 | 556,172 | 3,230.6 | 24,799 |

## Wall time, spread

| wall time | nbs | games |
|---|---|---|
| 0–10 ms | 30 | 24 |
| 10–50 ms | 106 | 60 |
| 50–100 ms | 18 | 12 |
| 100–500 ms | 48 | 3 |
| 500–1,000 ms | 1 | 0 |
| 1,000–5,000 ms | 4 | 0 |
| over 5,000 ms | 1 | 0 |

## P134 against the rest

P134: 12,904.8 ms, 1,742,747 statements run, 7.40 µs a statement, 45,676 mmap, 182 statements in the program. Median µs a statement over programs that ran at least 10,000: 8.85.

## Next

- Split the machine record: the state statements change, and the rest behind
  one reference.
- The load: ECMA-55's line checks turn a keyword into bytes for every
  comparison, 37,243 of P095's 39,335 allocations.
