# Battle-testing the zig-plug discard fix into a PR

## What the change is

One rule in `codex/plugs/zig/ZigEmitter.codex`. An unused `let` emits `_ = <val>;`
to sequence its value. When the value is a bare NAME, reading it does nothing,
and `_ = x` is legal in zig only while `x` is otherwise unused; if `x` is read
elsewhere, zig calls the discard POINTLESS and refuses it. So a new
`zig-let-discard` drops the discard for a name read in the body and keeps it
otherwise. **Only a name is ever dropped, never an expression that could do
work, so a program's output cannot change** — which is the invariant the
abandoned versions (finding 60) violated when one shipped a wrong answer
(`deck-bracket-contract` match→differ).

## The completeness decision (settle before the PR)

The rule as written drops the discard when the name is read **in the body**.
That fixes `roc-alias-original`. It does NOT fix `roc-list-called-twice`, where
the name is read in an enclosing SIBLING binding (`let a = x` before the unused
`let b = x`), not in the body — the correct test is "read anywhere else in the
definition," which needs whole-definition use analysis. That is **finding 63**,
the scope defect, and it is why finding 60 was abandoned as negative-EV.

Two honest options:

1. **Ship the safe subset now.** The rule is correct for what it claims (a name
   read in the continuation); it just does not yet cover the sibling case. The
   PR says so, and finding 63 stays tracked. Smallest, safest, and true.
2. **Complete it first.** Thread a per-definition "read count" so the discard
   asks "read elsewhere in the whole definition," covering both. More infra,
   the correct general rule, and it retires finding 63 with it.

Recommendation: decide this first. The battle-test below is the same either
way; what changes is whether `list-called-twice` is green at the end.

## Where the change lives

The fix edits Cobblestone source (`ZigEmitter.codex`), so it is a Cobblestone
PR to Damian, not a Rust-arm change. It is currently uncommitted on the
`u58-roc` worktree. The Cat A/B work (Rust compiler) is already committed to
`rust-codex-compiler` and is a separate track.

## The battle-test, step by step

The point is the `codex-zig-transpiler` gate: rebuild `codexzig` from a checkout
carrying the fix and prove it still transpiles the whole compiler consistently
(the fixed point), then that it still handles safari and the curated set.

1. **Land the change on the candidate.** Commit the `ZigEmitter.codex` fix onto
   `u58-candidate` (in `cobblestone-u58`). New Cobblestone sha, call it `$NEW`.

2. **New branch on codex-zig-transpiler.** `git switch -c zigemit-discard-test`
   there, to hold the rebuilt `generated/` artifacts without touching `master`.

3. **Rebuild + fixed point (~7 min).** With `COBBLESTONE_ROOT=cobblestone-u58`
   (now at `$NEW`), run the codexzig build so it recompiles the transpiler
   through the changed plug and checks the fixed point — `codexzig`'s own source
   transpiled under QEMU must byte-match its native re-transpile. PROVENANCE
   records `$NEW`. **Gate: the fixed point holds.** If it does, the plug change
   did not break the compiler transpiling itself — the strongest "don't break
   anything" signal we have. (This is the step that produced a broken binary
   earlier when a stale commit was built onto a drifted tree; a clean hold here
   is exactly what we need to see.)

4. **Safari zig arm (quick).** Point safari's zig arm at the freshly built
   `codexzig` (via its `CODEXZIG=` override) and run it. **Gate: safari still
   builds and renders** — a big real application through the changed plug.

5. **Curated cobblestone via the new codexzig (quick).** Run the curated
   `run-zig` arm with `CODEXZIG=` the new binary. **Gate: 28/28 match.** This is
   the deck-bracket-class regression check — the same shape that caught the
   abandoned wrong rule.

6. **Reset codex-zig-transpiler to master.** The rebuilt artifacts were a
   throwaway branch; `git switch master` and drop `zigemit-discard-test` so the
   pristine `generated/` (the `8570fba1` oracles) is restored.

7. **Cut the PR branch.** On Cobblestone, a clean branch off U57 (or the
   candidate, noting it) carrying only the `ZigEmitter.codex` change, with a
   backlog row describing the rule and the measurement. Send to Damian as a
   Claude-authored PR, risks stated (we own the zig plug; the rule is measured
   against zig's actual pointless-discard behavior).

## Success criteria

- Fixed point holds at `$NEW`.
- Safari zig arm green.
- Curated `run-zig` 28/28.
- (If option 2) `list-called-twice` also green through the new `codexzig`.

## Estimate

~30 minutes including keyboard time; the ~7-minute fixed-point build is the long
pole, everything else is seconds-to-a-minute.
