# What is slow, and what to do about it

*2026-09-11, late evening. A ledger of timings and known issues on the
Roc side, rough where it says rough, kept so the next sweep can be
targeted instead of waited for. Update in place.*

## Timings, as measured on this box

The box is 8 GB, two cores, and the Roc compiler is a DEBUG build, which
is roughly ten times slower than a release build would be at everything it
does. That factor sits under every compile number below.

| what | time | notes |
|---|---|---|
| `roc` compile + run of a small spec (Echo platform) | ~3 s | mostly compiler start-up and checking the modules |
| `safari/emitted.sh`, all 54 units | ~5 min | was 42 min before the stills were baked as strings |
| SafariSpec alone | ~50 s | `roc run` evaluates the ride at compile time |
| CatStillsSpec alone | ~7 s | was 8 min as literals |
| rocemit on one unit | well under 1 s | debug rocemit; release is faster |
| irdump whole over 54 units (the wire check) | ~1 min | |
| `cargo build` of rocemit, debug | ~10 s incremental | release build minutes; never in a fix loop |
| `roc build SafariApp.roc --target=wasm32` | 45 s to 1 m 40 s | grew with the accumulator rewrite's extra definitions |
| `zig build` of the wasm host | 4 s | |
| one frame in the browser module, before the rewrite | 110 ms | ride_frame 46, blit_expand 61, pack 3 |
| one frame after the accumulator rewrite | 28 ms | ride_frame 34 in isolation, blit_expand 0.7, pack 4 |
| `advance` (the physics step) | 0.07 ms | |
| Roc's eval test suite | 47 min | 2086 tests, two processes |
| Roc compiler, debug build from clean | ~10 min | |
| Roc compiler, ReleaseFast | fails | the final LLVM link reaches 5.4 GB resident and has been killed each time; one unattended retry pending, to run ALONE |
| native FrameBench (Echo platform, `--opt=speed`) | 820 ms per frame | not representative: the native Echo allocator dominates; use it for names, not numbers |

## Where the five minutes go

Fifty-four units at about five to six seconds each, plus SafariSpec's fifty.
Each unit pays the compiler's start-up, the check of every module it
imports, and the run. Two cores are idle half the time because the sweep
is serial.

## Known issues, each with its status

- **Roc's debug checker is quadratic in literal leaves per file.** Profiled
  to one loop that re-fetches the plan list each iteration, and the fetch
  asserts over every plan in Debug. One-line fix at `Check.zig:34522`,
  unverified, unreported, Steve's call. Worked around: any constant of 256
  or more literal leaves is baked as a string by `bake_stills.py`.
- **Cons-by-concat is quadratic in Roc.** `x & f rest` copies everything
  below at every level: 2,430 elements cost 1.7 s, 4,860 cost 4.7 s. The
  emitter now recognises the right-fold shape and emits an accumulator
  loop, with `List.append` per element; `List.concat` onto the accumulator
  is fifty times slower per element and goes quadratic for short literals.
  Fifty-seven safari definitions take the rewrite. Two recursive concat
  definitions remain (`kept_of`, `hull_insert`), both small.
- **`roc run` evaluates top-level constants at compile time.** SafariSpec's
  ride is built and stepped by the compile-time evaluator, which is why it
  costs fifty seconds where the wasm module steps in microseconds.
- **A Roc warning is exit 2.** Unused variables are handled by the emitter
  (`_name`); "condition known at compile time" in `Cat.roc:133` is not
  avoidable from the IR and is harmless.
- **No names in profiles.** The wasm module has no name section, and native
  Roc functions are `roc__proc_NNNN`. Stage probes in the app and micro
  benchmarks in `~/build/roc-apps/probe/` are what work.
- **The Echo platform's `args` has no program name at index 0.** My first
  benchmarks read `args[1]` as the mode and measured the default branch for
  half an hour. Read the output, not only the clock.
- **`--opt=speed` and the dev backend gave the same frame time** for the
  wasm module, which is suspicious and unexplained; the wasm path may go
  through LLVM either way.
- **The release build of roc needs the box to itself.** 5.4 GB at the link.

## Making sweeps shorter

Three moves, in the order I'd take them.

1. **Per-unit timing in the sweep's output.** One number on each PASS
   line, so the slow units are a fact and not a memory. Trivial; next edit
   of `emitted.sh`, after the running sweep ends (never edit a running
   bash script).
2. **Two units at a time.** The box has two cores and a unit's `roc` is a
   few hundred MB; `xargs -P2` halves the wall clock to about 2.5 minutes,
   with the chapter-identity check done after, not during.
3. **A targeted sweep from git.** `safari/roc/` is tracked, so after a
   rocemit change the modules that changed are `git status`, and the units
   to re-run are the specs that import them. A `safari/retest.sh` that
   computes that set and runs it would make most fix loops a coffee break
   or less. Until it exists, `emitted.sh <Spec>` runs one unit, and the
   five stills units and SafariSpec are the usual suspects.

Beyond those, the release build of roc is the multiplier on everything,
and the one-line checker fix is what makes the debug build tolerable if
the release build never links on this box.
