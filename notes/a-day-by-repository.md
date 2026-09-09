# A day's work, by repository

A status report on one day's work across the Codex repositories. The work fell
into three kinds: improving the upstream Cobblestone compiler (a PR, and
validating Update 57); improving our Rust compiler; and ergonomic changes to
the surrounding tooling. It is organized by repository rather than in the order
things happened.

## Cobblestone (upstream) — one PR, and Update 57 validated

**PR #138** fixes a zig-plug code-generation bug: an unused `let` bound to a
name that is read elsewhere reached the plug as `_ = x`, which zig 0.16 refuses
as a pointless discard of a used local. The emitter now binds the value to a
silenced local (`const b = val; _ = b;`) instead of discarding it — the value
stays used, and the fresh binding is what is silenced. It changes no output and
needs no whole-definition scope analysis. The PR carries a test that pins both
shapes of the bug.

The fix was battle-tested before sending: a `codexzig` built with it holds its
fixed point (byte-identical self-transpilation under QEMU and native), the
curated program set and the safari application's zig arm stay green, and the
Roc corpus (below) builds and runs correctly through it.

Update 57 / the u58 candidate were validated in passing: the curated 28 pass on
every arm, and the whole compiler still compiles itself to IR **byte-identical
to `codexir` across all 3,222 definitions**, with the five checker counters
exact against `codexcheck`.

The Roc corpus surfaced six defects, and naming their layer was most of the
work. Three are an upstream **frontend** gap (a generic lifted closure whose
type variable upstream leaves unresolved); one more is a **checker** gap; and
two are the **plug** bug that PR #138 fixes. Only the plug half is upstream's to
merge today; the frontend halves live in our Rust arm and are future frontend
PRs.

## rust-codex-compiler — two frontend fixes, both at the owning layer

**Binary-operator operand unification.** The checker answered a result type for
each binary operator but skipped the operand unification `infer-binary-op`
performs, for every operator except arithmetic. Comparisons, logical `and`/`or`,
`&` and cons now unify their operands as upstream does. This was the last
self-host divergence: it went from 3,221 to **3,222 of 3,222 byte-identical**,
with the minting counters unchanged (unification binds, it does not mint).

**Empty-list orphan default.** A monomorphic definition's unconstrained empty
list — the element observed only by `list-length` — left a type variable no
context bound, which reached a plug as "no element type." The checker now
resolves such an orphan to `int-default` at the end of a definition, so the
whole definition is consistent and every plug gets a concrete type. The
self-host and curated sets are unchanged (they have no such orphans); only
programs that actually carry one are affected.

Both fixes share a shape: knowledge the checker already had (the operands must
agree; the element type is unconstrained and should be defaulted) was not being
carried forward to lowering and the plugs. The correct place for each was the
checker, not a patch at a later layer.

## cobblestone-curated-tests — the Roc corpus lands, and a reorganization

The repository now holds **two parallel corpora**: `cobblestone/` (the 28
programs cut from Cobblestone's own corpus) and `roc/` (29 programs hand-ported
from roc-lang/roc's test suite, with Roc's own outputs as the oracle). Each is
self-contained — every program's `.codex` sits beside its `.expected` under
`units/` — and each carries its own arm scripts.

The arm scripts were renamed for what they do rather than how they were once
built: `run-interp`, `run-wasm`, `run-zig` (execute and check output against
`.expected`) and `ir-irdump`, `ir-interp` (compile and diff IR against
`codexir`). The zig arm is new. The war-story comments in the scripts were cut
to a sentence each.

## safari-codex — codexzig discovery simplified

Safari now finds `codexzig` by pointing at a bundle directory (one line in
`pins.tsv`) and reading the binary and the language pin from it. The previous
mechanism — a fingerprint resolver, a separate candidate-builder script, and
`CODEXZIG`/`SAFARI_COBBLESTONE` overrides — is gone; `cobblestone_pin.py` reads
the pin from the bundle's PROVENANCE. The zig arm still passes.

## codex-zig-transpiler and ~/codexzig — a durable bundle, a footgun removed

`codex-zig-transpiler/generated/` was untracked and rebuilt in place, so a build
could silently overwrite the `codexzig` other repositories depended on. The
verified codexzig now lives as a **bundle** at `~/codexzig`: the executable
beside a PROVENANCE that records the Cobblestone checkout it was built from.
Anything that needs codexzig points there. `generated/` was then deleted; it is
entirely rebuildable, and its absence is a deliberate trip-wire to finish moving
the remaining arms onto durable locations.

## Reflection

The recurring theme was the layer a fix belongs to. Every defect had a tempting
shallow fix — patch the list literal in lowering, drop the discard in the
emitter — and in each case the honest fix was one layer up, at the component
that actually owned the knowledge: the checker resolving a type, the emitter
binding rather than discarding. Fixing at the owning layer was usually also the
*simpler* fix once found, because it did the thing once instead of papering over
its absence everywhere downstream.

The other theme was that an independent front end earns its keep. The ladder's
original two arms shared one front end and could not see a defect above the IR;
our Rust reimplementation and Roc's own answers, between them, found six in an
afternoon. The corpus that exposed them is small and readable and demands
perfection of itself, which is exactly what let one red result mean something.
