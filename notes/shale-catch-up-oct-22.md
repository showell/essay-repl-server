# Shale: a catch-up

*2026-10-22. What happened to Shale over the last three days, by theme. The
details live in shale's commits, metal-vmm's QUEUE-ARCHIVE (items 241-243)
and FEEDBACK.*

## Where it stands

| | then (10-19) | now |
|---|---|---|
| Zig | 0.16 | 0.17.0, every repo |
| `zig build test` | 313 pass, **15 skipped** | **349 pass, 0 skipped** |
| fuzz hunts | 15, run only by hand | 20, counted, and failing on any skip |
| line coverage, the site's modules | unmeasured | **100%** (3 exemptions, each a function, each with a reason) |
| line coverage, the two preludes | unmeasured | **100%**, measured by the engine itself |
| loud comment lines (bold, ALL-CAPS, banners) | 461 | 5, none of them shouting |
| the VM on a while loop | 1.0 | about 0.6 of before; **step counts identical** |
| who owns it | the box | CC for about a day, now the box again |

## 1. Shale itself is easier to reach for

The upgrade gave me two days of honest data. Every time I stepped past the
gate, the escape was logged, and there were 694:
- `grep` 195;
- `sed -n` (reading line ranges) 120;
- `git` 98;
- `zig build | grep` about 70.

Most were shell habits for things Shale already did. You named the rule: when
Claude avoids Shale where it already works, that's a documentation failure, so
fix the docs. So:

- **The agent doc now opens with a habit-to-Shale table.** For example,
  `sed -n 40,80p` becomes `look.shale at=f:40-80`. The git prelude, which
  already did every git job I'd escaped for, is in the first screen.
- **Two recipes for the two commonest reads:**
  - `look.shale`: line ranges from several files, and a word's lines across
    folders, mounts, or a git revision.
  - `zig_build.shale`: a build's verdict without its noise: the summary, each
    error once, failed tests by name. It now also says when counts came from
    the cache (that misled me twice) and when a build was killed.
- **Scripts launch through a mount**, `shale cookbook:look.shale`, from any
  checkout.
- **A new compiler is one config line you approve once:**
  `zig = ~/zig-0.17.0 ro tools`. Shale's `run` refuses a program git doesn't
  track (a script just written?). A `tools` mount says "this folder is a
  toolchain", so its programs pass without a per-run exemption.
- **Small additions from CC's own escapes:**
  - `trim_start` / `trim_end` (your right trim);
  - `look` at a git revision;
  - a filter on `zig_build`'s output.

CC's later chunks show habit wins anyway: it reported working mostly in the
shell for a while, out of habit, not missing features. The table helps;
it doesn't settle it.

## 2. No carried skips

The 15 `expensive` tests used to compile into every `zig build test` and skip
there, so every run printed "15 skipped". Now:
- They live in a hunt step of their own, and `zig build test` prints no skips.
- `zig build fuzz` fails if any hunt skips, or if fewer run than are defined.
- A guard test fails on any new skip anywhere in the code.

I planted a skip in one hunt: both the fuzz step and the guard went red,
naming the line.

## 3. Line coverage, and what it took to trust it

**Line coverage didn't exist for Shale.** The kernel had a Python tool
that runs each test binary under a debugger, with a breakpoint on every line.
CC ported it to Zig, in the coverage SDK, so both repos share it. It had to
learn to follow forks first, since Shale's tests fork, and a fork would have
died on an inherited breakpoint. That fix was red first, then green.

**The tool itself had bugs, and so did Zig.**
- The port found a bug the Python shared: rows from another file counted as
  the measured file's lines. Fixed, red then green.
- It found a **Zig 0.17 bug**: a generic function's debug rows carry line
  numbers that don't exist (lines 24 and 25 of an 11-line file). You filed it.
- Until Zig fixes it, a guard refuses any row whose line doesn't exist, has
  no code, or is shorter than the row's column, and counts what it refused.
  The column check alone would have missed one bad row, at column 1, which
  is why the "no code" rule is there too.
- The kernel now uses the Zig tool too, its numbers matching the Python's,
  and the Python is gone.

**Then the climb:** from 125 uncovered lines in the site's six module groups to
0. In order:
- the route that reads a signed script's envelope before checking the signature;
- regex;
- the parser;
- the compiler and VM;
- the interpreter and budgets;
- the builtins.

The rules you set:
- **dead code is deleted, not tested;**
- **a line nothing can reach may carry an exemption comment with its
  reason** (three functions do: two run only in a forked child the tool
  can't see);
- **the Linux host is measured, not held to 100%.**

**Two deletions changed a promise, so I checked them:**
- **The interpreter's error set** is now "a stop", never "out of memory". The
  compiler enforces it.
- **"A const read before it's set" is now an assertion, not an error.** If
  that were wrong, a script on lynrummy.com would crash the server. I attacked
  it with eight scripts:
  - a function reading a const declared below it;
  - a call before its declaration;
  - consts hidden in branches and loops that never run;
  - recursion.

  Every attack is refused by the parser before a step runs. The guarantee is
  structural, so it stays.

**One real bug from the climb:** a small leak in the parser when memory runs
out mid-prelude, found by an allocation sweep, red then green.

**The preludes, too:** a test fails if any prelude function is uncalled. And
in test builds only, the VM records which prelude lines run, so the preludes
appear in the same coverage table, both at 100%.

## 4. Fuzzing

- **A generator of well-formed scripts**, with hunts holding new invariants:
  - **budgets are exact:** a run given exactly what it used ends the same,
    and given one less, stops on that budget;
  - **slicing changes nothing:** a VM run cut into slices of 1 to 64 steps
    ends as it does whole;
  - **every stop is one line with a class;**
  - **arithmetic past 64 bits stops, never wraps.**
- **It found two bugs, both in the gate, not the engines.** The gate holds
  the VM to the tree-walking interpreter on every run. It wrongly refused
  correct pairs where one engine ran out of memory and the other didn't.
  Both are fixed, red then green. **No engine bug yet.**
- **Zig 0.17's own fuzzer** now runs over the lexer and parser: about
  10,000 inputs each, with no failures. CC also hit two oddities in Zig's
  fuzzer:
  - a misleading "corrupted coverage file" message on the default backend;
  - a second fuzz test in one binary getting only unit-test runs.

  I'm to research both and draft them for you.
- **An experiment with the SDK's explorer** against blind runs showed no gain.
  The generator makes no named choices for it to steer. Named choices are the
  next measure.

## 5. Speed, with one rule

**A step is the unit every budget is in.** A "speedup" that changes step
counts changes which scripts fit, and that's a policy change, not a speedup.
So every speed change must leave every benchmark's steps identical, and a
script (`tools/bench.shale`) fails otherwise.

Two VM changes:
- popping a value by shortening the stack;
- integer `+ - <` done inline.

On the box, steps were identical in every case, and the VM got faster: a
while loop at 0.61 of its old time, a loop 0.78, calls 0.85. The walker,
untouched, moved 0.95 to 1.07, which is the noise. One run a side, so the
ratios are rough; the steps are not.

**One speedup declined:** removing a bounds check on reading a variable would
save 5% more. Without it, a compiler bug would read the wrong variable
silently, on a server that runs scripts other people send. It stays.

## 6. Comments in the Zig compiler's voice

You asked Shale's Zig to read like the Zig team's. The sample was `AstGen.zig`,
the heart of Zig's front end, and its companion `Zir.zig`. Measured against
Shale, Zig's authors write:
- **in algorithms:** few comments (1-7 per 100 lines), saying only why;
- **in data definitions:** a terse doc on every field;
- **never:** bold, capitals, dates or history.

CC rewrote 83 files:
- loud lines 461 to 5;
- dated lines 236 to 1.

A Shale recipe compared each file's code tokens before and after: comments
only, every commit. I planted a one-token code change and it was caught. I
read the docs CC flagged against the code, and they were true.

## 7. Where Shale runs

- **The box:** this box's binary, built with 0.17, with the gate.
- **Prod (the Caddy box):** a static build of current master, with the old
  one kept beside it.
- **lynrummy.com and Dog Park:** both embed Shale through their kernels.
  v35 and Dog Park v4 shipped built on 0.17.

## What's open

- **The request heap** (your ruling today): the per-request memory figure now
  counts a growth by what it grew, wherever the block lands, so the same
  request always reports the same number. The fix and its unparked test are
  green. A 200-seed sweep is running before I push.
- **Left from CC's plan, now mine:**
  - the VM's instruction layout;
  - the explorer with named choices;
  - test names that still carry queue numbers.
- **To draft for you:** the two Zig fuzzer reports.
- **Shale's own wants:** keep reading the escape log as I work. The table
  only helps if the next reach for the shell is caught.
