# Safari to Roc: where it stands

*2026-09-11, evening. A status report, written while the first full sweep of
the emitter is still running. Numbers are as of the moment of writing and
the final tally follows in the console.*

## The pivot, in one paragraph

The Rust compiler is parked at 9044a29 with every instrument at 100% or
filed. The next subject is Roc: take safari, our hand-written Codex
screensaver, and make it a Roc program, so that the Roc chapters become the
real code and Codex is the source we translated from. Two roads were open,
porting by hand and emitting from the compiler, and the day walked both,
in that order, on purpose: the hand ports taught the Roc that the emitter
then had to write.

## The compiler

Roc's new compiler (zig, `roc-lang/roc` main at 68267ddd) is built from
source on this box, as a debug build. The ReleaseFast build was killed at
its final link twice; that link is all of LLVM, statically, and the box has
8 GB. Debug is fine for what we do with it: a spec compiles and runs in
about three seconds.

The installation check is Roc's own eval suite, which the hand-port session
ran in two processes: 2086 passed, 0 failed, 47 minutes.

## The hand ports

Two specs were ported by hand into `roc-apps/safari/`, each with the Codex
verdict frozen beside it as its expected output:

- **ViewYawSpec** (last session). It taught the shape of a spec in Roc: the
  Echo platform's `main!` takes args and returns a `Try`, its `echo!` writes
  no newline, and every Real has to be an annotated `F64`, because Roc's
  unannotated fraction is a `Dec` and the fourth case of the yaw fold is
  0.012500000000000011 in doubles, graded at tolerance 0.0.
- **SceneLimitsSpec** (today), the smallest spec in the suite. It taught the
  integer boundary: Codex `Integer` is `I64` everywhere, but Roc's `List.len`
  returns a `U64` and `List.get` takes one, and `F64.to_bits` returns a
  `U64`, so the conversions sit at those three seams and nowhere else.

Both run on `roc debug-68267ddd` and match their verdicts. `safari/run.sh`
in roc-apps runs them.

## The subset

Before writing an emitter, `roc-apps/docs/codex-subset.md` counted every
form safari uses, over the 54 frozen IRs the Rust compiler emits for the
specs. It is small: records and literals dominate, then names, calls,
`F64` arithmetic, comparisons, `if`, `let`, `match` over four sums and
`Maybe`, list literals, field access, negation, one `act` per unit. Absent:
`handle`, `try`, `fork`, `with-timeout`, field stores, `lazy`, induction,
vectors, units. Fifteen builtins. That is the whole target.

## The emitter

`rocemit`, a new binary in rust-codex-compiler (commit 8fe6596), takes a
resolved unit down the same road as `irdump whole` -- resolve, parse,
desugar, check, lower, pipeline, prune -- and then spells the in-memory IR
as one Roc program instead of as IR text. `lower_chapter` was extracted so
both emitters read one document.

Its rules, each of which was a probe against the real `roc` first:

- **Types are read, never inferred.** Every node on the wire carries one.
  `int-default` is `I64`, `real` is `F64`, `text` is `Str`, and every
  definition gets a signature, so no fraction is ever a `Dec`.
- **A Real literal arrives as bits** and leaves as the shortest decimal
  that round-trips, or as `F64.from_bits` when it would need an exponent.
- **Calls are saturated.** The IR is curried; the definition's parameter
  count says how many arguments to gather, and fewer is a refusal.
- **`let` chains are blocks, parenthesised**, because a bare brace opens a
  record. `if` and `match` are parenthesised too, so they can sit anywhere
  an operand can, which a probe confirmed Roc allows.
- **A binder nothing reads is `_name`.** An unused variable is a warning
  and a warning is exit 2.
- **`list-at` out of range is a `crash`**, which is what Codex does.
- **`=~=` is bit equality** on the two doubles, which is ordinal equality.
- **Everything else is refused by name.** No guesses.

`roc-apps/safari/emitted.sh` runs every unit through it and through roc and
diffs against the frozen verdict, counting pass, fail and refused apart.

## The first sweep, as of writing

| | |
|---|---|
| units | 54 |
| pass, byte for byte | 34 |
| fail | 0 |
| refused | 4, one cause |
| still running | the rest |

The one cause: four units carry a comprehension the compiler lifted to
`__lam_0`, and Roc reads a leading underscore as "unused". The fix strips
the underscores; it is built and the sweep picked it up midway, so those
four will be re-run.

The surprise is time, not correctness. CatStillsSpec took eight minutes
under `roc run`'s default dev backend where the Rust interpreter takes
seconds. Whether `--opt=speed` or `--opt=interpreter` changes that is the
first measurement after the tally.

## Steve's question: how do the modules get organised?

The question makes sense and the answer is good news. Roc's module system
is **type modules**: a file `ViewYaw.roc` is a module if it declares a
top-level nominal type named `ViewYaw`, and everything other files may see
hangs off that type as an associated item. A module that is just a
namespace of functions is a *void module*, `ViewYaw :: [].{ ... }`, and
the docs recommend it for exactly this case. A record type a chapter
declares nests inside: `Rider.RiderState`.

That is a Codex chapter. Every IR definition carries its `chapter_slug`,
so the emitter already knows which chapter each definition came from; the
single-file output groups by it today. Step two is to emit one type module
per chapter and have the spec be an app that imports them. Then the
screensaver itself is another app importing the same chapter modules,
built for a wasm platform instead of the Echo platform, and the specs go
on grading the chapters from the side. The Echo platform is for the specs
only; the app needs a platform with a canvas, which is its own piece of
work and not started.

Single file first, modules second, was deliberate: a failure in the first
sweep should have one axis to bisect, and the module split is a projection
over a def list that already passes.

## What is next

1. The tally, then re-run the four refused units on the fixed binary.
2. Measure the slow units under roc's other execution modes.
3. The module split.
4. Commit the `run-test-eval` and build facts to roc-apps's README (done),
   and keep `emitted.sh` as the gate.

| repo | revision | role |
|---|---|---|
| roc (roc-lang/roc) | main @ 68267ddd | the compiler, debug build |
| roc-apps | 9cae655 | hand ports, `emitted.sh`, the subset doc |
| rust-codex-compiler | 8fe6596 | `rocemit` and `lower_chapter` |
| safari-codex | units as of 2026-09-10 | the 54 units and their verdicts |
