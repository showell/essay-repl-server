# Timing the BASIC ladder: which program took the time

A report on a day's measurements of the BASIC interpreter, most of them
taken wrongly at first, and what they say once each time is attributed to
the program that spent it.

---

## Three programs, and what "compile" means

Three different programs run when a corpus program is graded. Nothing here
compiles BASIC.

1. **The Roc compiler** (`~/build/roc-nightly/roc`, nightly
   `2026-09-11-793f9d8`) compiles Roc source — the interpreter's modules
   `Basic.roc`, `Listing.roc`, `Program.roc`, `Pages.roc`, plus a small app
   file — into an executable.
2. **That executable is the BASIC interpreter.** It splits a BASIC listing
   into lines, collects its DATA, and executes its statements one at a time.
3. **The BASIC program** (`bunny`, `P062`, hello world) is data the
   interpreter reads.

## How the ladder used to run, and why every time was wrong

`basic/gen.py` wrote one Roc app per BASIC program, with the listing and
its replies pasted in as string literals, because the Roc default platform
had no file or stdin effect that `gen.py` knew of. `basic/ladder.sh` then
ran `roc run Run.roc` for each program.

`roc run` does two things and reports one wall-clock time: **the Roc
compiler compiles the interpreter (again), then the interpreter runs the
BASIC program.** For a small program the first phase is most of it. Every
time quoted that day was this sum:

- "bunny ran fine in 11 s" was roughly 10 s of the Roc compiler and an
  unknown remainder of the interpreter.
- "200,000 array stores cost 19.7 s into 10 cells and 18.9 s into 4,000"
  included the compiler too. It was also blind in a second way: both arrays
  fit in one 4,096-cell page, so a page copied on every store would have
  cost the same in both.
- Bisecting `bunny` across commits with 90-second timeouts measured the Roc
  compiler and the interpreter together, under contention.

## One executable, built once

The default platform passes `main!` its command line as `List(Str)` — every
argument after the executable path (`roc/src/default_platform/roc_args.zig`,
`fromPosixArgv`). The interpreter is a pure function of the listing and its
replies, so the arguments are all the input it needs.

`basic/roc/BasicRun.roc` takes `ecma` or `micro`, the listing text and the
reply text, calls `Basic.run_ecma` or `Basic.run`, and `echo!`s the
transcript. It cleans the text exactly as `gen.py` did, and its seed is 1,
what every generated app got (`1 + List.len(args)` with no arguments).
`basic/build-run.sh` builds it once; `basic/run.sh` runs each corpus
program as its own process and reports that process's time alone.

| phase | measured |
|---|---|
| Roc compiler, `roc check BasicRun.roc` | 0.5 s |
| Roc compiler, `roc build BasicRun.roc` → `basic-run` | 62.7 – 71.6 s, not yet examined |
| `/bin/true` | 0.9 – 1.7 ms |
| `basic-run`, empty listing | 0.6 – 0.7 ms |
| `basic-run`, `10 PRINT "HELLO"` / `20 END` | 1.0 – 1.3 ms |

Fifteen programs known to pass — nine NBS, six games — produced
transcripts identical to the per-program Roc apps', except `banner`
(159 bytes against 3,277), which is not yet explained.

## What the interpreter spends per statement

Loops of 10,000 iterations, one process each, three runs agreeing within a
few percent. The cost is the body's, over the bare loop:

| body | per iteration |
|---|---|
| `FOR I … NEXT I` alone | 1.1 µs |
| `LET X=I` | 25 µs |
| `LET A(5)=I` | 41 µs |
| `PRINT` | 28 µs |
| `POKE 5000,7` | 147 µs |

Attributed with `strace`, which counts system calls rather than timing
anything. **On the default platform, every heap value the Roc program
allocates is its own `mmap`, and freeing it is a `munmap`**
([roc-lang/roc#11335](https://github.com/roc-lang/roc/issues/11335), filed
by us, open). Counted over the same 10,000 iterations:

| body | `mmap` calls | per iteration |
|---|---|---|
| `FOR/NEXT` | 14 | 0 |
| `LET X=I` | 20,014 | 2 |
| `PRINT` | 29,984 | 3 |
| `POKE 5000,7` | 20,014 | 2, of 100 KB and 8 KB |

The sizes say what each allocation is. A `LET` or `PRINT` allocates small
values (each rounded up to a 4 KB mapping). An array store allocates no
page per iteration: **Pages does write in place.** A `POKE` copies the
whole 4,096-entry page table (4,096 × 24 bytes, hence 100 KB) and one page,
every time.

## What was fixed

Read against the counts, two small allocations per `LET X=I` came from
converting text to bytes that did not need converting:

- `kw` ran `Str.to_utf8(word)` on every call, so every keyword check made a
  heap list of a literal like `"FN"`. It now compares `text_of` the line
  against the word.
- `name_or_call` ran `Str.to_utf8(k)` on every name, to ask whether it
  starts with FN. It now uses `Str.starts_with` and `Str.count_utf8_bytes`.

`LET X=I` went from 2 allocations a statement to 1 (260 ms to 172 ms for
10,000). Committed in roc-apps `basic-wip-arrays-margin`.

## What was tried and did not work

The remaining allocation belongs to the store, not the name: `LET X=1`
allocates as much as `LET X=I`, and `IF I<0 THEN 20`, which evaluates `I`
and stores nothing, allocates nothing. `NEXT` stores through the same
`set_num` and allocates nothing.

The hypothesis was that the machine is shared when it is handed on as
`r.m` while `r.at` is still to be read, so each write copies the list it
writes. Rebinding `at`, `v` and `m` out of the result first changed no
count for `LET` or `POKE`, and made `PRINT "X";` worse — 10,480 to 20,470
`mmap`s, 255 to 1,798 ms — because the rewritten `emit` built an extra
record. **The hypothesis is disproved at those sites; the rewrites are
reverted.** Where the remaining allocation per store comes from is open,
and it wants a tool that shows allocations by call site, not another guess
at Roc's reference counting.

## What `bunny` actually is

`bunny` draws a rabbit out of the letters B-U-N-N-Y from DATA rows of
column ranges. It should execute about 3,914 BASIC statements. It never
finished from the commit that made `READ` accept a sign onward.

Read, not bisected: line 240 is `GOSUB 260: GOTO 450`. `do_gosub` saves
only the line (`back.pc`), and `do_return` resumes it at byte 0
(`at: 0`), so the RETURN runs the GOSUB again, forever. `ON … GOSUB` has
the same fault. `10 GOSUB 30: PRINT "BACK": GOTO 50` alone never ends.
Before signed data, `bunny` read its `-1` row markers as 0, ran out of
DATA, and stopped before line 240 — so the fault was there all along and
nothing reached it. **Not yet fixed.**

## Open

- The allocation per `LET` store, the three per `PRINT` newline (`scroll`
  builds two new 1,000-byte lists per line), and POKE's table copy.
- `banner`'s transcript through `basic-run`.
- The Roc compiler's 63–72 s to build `basic-run`, and 2 min 45 s to build
  the same interpreter for wasm32 with `--opt=speed`; `roc check` alone is
  0.5 s.
- `ladder.sh` still builds one Roc app per program; it moves to `basic-run`
  once the above is understood.
