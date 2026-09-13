# BASIC in Roc: where it stands

Branch `basic-machine` in roc-apps, at d0318fd. Not merged.

## The suites

- **NBS: 195 pass, 0 fail, 13 unjudged** of 208, graded on the current
  interpreter just before this page. An unjudged program prints no verdict of
  its own (readers, and ERROR programs with no row in `nbs-reports.txt`).
- **Games: 54 of 99** match basic101's captured output byte for byte.
- **The fast path agrees with the full evaluator** on every program
  (`basic/check-fast.sh`).

## What runs, precisely

| program | built by, from | mode | target | used for |
|---|---|---|---|---|
| the Roc compiler | roc-lang's nightly binary, `nightly-2026-09-11-793f9d8` | as published; we do not build it | x86-64 | every build below |
| `basic-run` | the Roc compiler, from `BasicRun.roc`: the **new** interpreter, `Machine.roc` | `--opt=dev` | x86-64 | NBS and games, one process a program |
| `basic-check` | the Roc compiler, from `BasicCheck.roc`: the same interpreter | `--opt=dev` | x86-64 | the fast-path check |
| `basic.wasm`, the page | the Roc compiler, from `BasicApp.roc`: the **old** interpreter, `Basic.roc` | `--opt=speed` | wasm32 | the browser, preview :9203 |

Three corrections to how you described it:

- **The Roc compiler is the nightly, not a tagged release.** It is the binary
  roc-lang publishes, unchanged; the modes below are for the code it
  generates, not for the compiler.
- **`--opt=dev` is not a debug build.** It is Roc's own native backend: no
  LLVM and no optimization. It is the closest Roc has to debug.
- **The page still runs the old interpreter,** built with LLVM (`--opt=speed`).

## The LLVM build

`basic-run` was built by the Roc compiler with `--opt=speed` (LLVM), native
x86-64, at d0318fd, and run beside the dev build of the same source.

- **The build takes 24 minutes and peaks at 2.2 GB.** The dev build takes 6 s.
- **The output is the same:** all 208 NBS and 99 games transcripts are
  identical.
- **Statements run 3 to 7 times faster.** P134 goes from 7.3 s to 2.7 s, a LET
  from 2.3 µs to 0.6, and an IF from 2.8 µs to 0.4.
- **Allocating is hardly faster.** String growth and DEF FN gain 1.1 to 1.2
  times, and a load-dominated NBS program gains 15% (P095, 403 ms to 322).
  The ECMA-55 load checks are allocation, and LLVM does not remove an
  allocation.

**Your call:** whether LLVM comes back into the loop, at 24 minutes a build, or
stays for an occasional measurement like this one.

## Bottlenecks

1. **Done: the fast path is checked for good.** Every program runs both ways,
   and a difference stops it at the statement.
2. **Now: the cost of a step.** Every statement pays for the width of the
   machine record, which is rebuilt several times a statement with every list
   in it counted up and down. Measured by padding the record: fifteen more
   lists make P134 35% slower, and the same fifteen behind one reference cost
   nothing. **The plan:** split the machine into the state statements change
   (program counter, variables, arrays, loops, returns, fuel) and the rest
   behind one reference: screen, memory, output, input, the Twister's table.
   It is the split you asked for when you called the machine too flat.
3. **Next: the ECMA-55 load checks**, 150 to 370 ms a program, where most NBS
   programs spend their time.

Numbers: [basic-timings](basic-timings.md).

## The browser

Move `BasicApp.roc` onto `Machine.roc`, whose `start` and `resume` doors are
already there. **Your call is the build.** The compiler's help calls `dev` the
native backend, and I have not tried it on wasm32. The other modes are `speed`
and `size`, both LLVM, and `interpreter`, an embedded interpreter backend.

## Cleaning up, once the page has moved

- `Basic.roc` (2,371 lines) and `Pages.roc`, the old interpreter;
- `basic/gen.py`, which the ladder no longer uses;
- merge `basic-machine`.

## Open

- Five game listings differ from basic101's copies (life, life2, poetry,
  splat, superstartrek). Take basic101's, or keep them as known mismatches?
