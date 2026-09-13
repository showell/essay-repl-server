# Every BASIC program, timed: where P134's 12.9 seconds go

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

- P134 by source line, with 
 usage: perf [--version] [--help] [OPTIONS] COMMAND [ARGS]

 The most commonly used perf commands are:
   annotate        Read perf.data (created by perf record) and display annotated code
   archive         Create archive with object files with build-ids found in perf.data file
   bench           General framework for benchmark suites
   buildid-cache   Manage build-id cache.
   buildid-list    List the buildids in a perf.data file
   c2c             Shared Data C2C/HITM Analyzer.
   config          Get and set variables in a configuration file.
   daemon          Run record sessions on background
   data            Data file related processing
   diff            Read perf.data files and display the differential profile
   evlist          List the event names in a perf.data file
   ftrace          simple wrapper for kernel's ftrace functionality
   inject          Filter to augment the events stream with additional information
   iostat          Show I/O performance metrics
   kallsyms        Searches running kernel for symbols
   kvm             Tool to trace/measure kvm guest os
   list            List all symbolic event types
   mem             Profile memory accesses
   record          Run a command and record its profile into perf.data
   report          Read perf.data (created by perf record) and display the profile
   script          Read perf.data (created by perf record) and display trace output
   stat            Run a command and gather performance counter statistics
   test            Runs sanity tests.
   top             System profiling tool.
   version         display the version of perf binary
   probe           Define new dynamic tracepoints
   trace           strace inspired tool
   kmem            Tool to trace/measure kernel memory properties
   kwork           Tool to trace/measure kernel work properties (latencies)
   lock            Analyze lock events
   sched           Tool to trace/measure scheduler properties (latencies)
   timechart       Tool to visualize total system behavior during a workload

 See 'perf help COMMAND' for more information on a specific command. on a dev build with debug info: which parts
  of a statement's 7.4 µs are the evaluator, the machine record, dispatch.
- The load: the same listings in both dialects, and P095 by source line.
