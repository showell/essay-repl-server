# The Roc programs expose IR type errors — a clean-slate plan (rev. 2)

*Revised after a cold review that corrected the first draft. What the review
caught is in "Where the first draft was wrong" at the end; the body now reflects
the corrected picture.*

## What we have

Six Roc-origin Codex programs compile and run correctly on the Rust interpreter
and the wasm plug, produce Roc's expected answer on both, and **cannot be
pushed through the zig plug.** The zig plug is the strict one; its refusal is
correct — fail-loud is the floor. So the six are real signals, and the corpus
has done its job. But they are **three different problems**, not one, and none
is the simple "the checker forgot to resolve a type" story.

## The three root causes

**A. The `__lam` cluster (iter-map, iter-keep-if, iter-drop-if) — a generic
closure the zig plug cannot monomorphize.** `iter-map : Iter a, (a -> b) ->
Iter b`. The lifted closure `__lam_0` carries `a` and `b` as its own type
variables, correctly threaded — the interpreter runs the program to `24` *with
those variables present*, so they are legitimate generics, not orphans. The zig
plug says "unresolved type variable T16 of __lam_0" because it needs a concrete
type to emit and meets a generic one. This is a **monomorphization /
lambda-lifting-vs-plug** problem, at the plug boundary — not a frontend
carry-forward bug.

This is also the **hardest** of the three. The prior effort reached it and
stopped on purpose: `bba94d1b` explicitly excludes the `ForExpr` `map-list`
lambda; `11df612c` tried the sibling instance-method site and `079e21df`
**reverted it** — "it fixes nothing and is not inert" — relocating the real
cause to **finding 64** (an instance dictionary's type argument instantiated
for one instance and not its sibling), which is unaddressed. There is a
known-failed attempt here, not an easy win.

**B. `alias-empty` — a genuinely unconstrained element type.** `x = [] ; y = x
; if list-length y == 0 then 42 else 0`. The empty list is only ever measured
for length, so nothing constrains its element type; both frontends leave it a
free variable (`(list (tvar 283))`). This is **not** the case the stranded
`8f1b202a` fixed — that one ("keep the element type the checker solved") was
measured on `roc-fold-empty`, where a parameter constrains the element type and
the checker *did* solve it. Here there is nothing to file. The honest answer is
to **default** a provably-empty list's unobserved element type — a policy call
(frontend or plug), best made with Damian.

**C. The discard pair (alias-original, list-called-twice) — an emitter codegen
fault.** The zig plug emits `_ = x;` to sequence an unused binding, then also
uses `x`, and zig rejects the pointless discard. This is purely in
`ZigEmitter.codex`. The stranded fix (`af119cc5` and three refinements) is
honest, careful work — iterated openly against a regression tree, each
narrowing catching a measured regression — and Steve then **deliberately
dropped it** (`ef359636`) on cost/benefit, banking the rule as knowledge. It is
the one of the three that is a plausible, self-contained clean fix, if
re-derived against the current tree with a self-hosting gate.

## Why "carry the stranded commits forward" and "fix in the fast Rust arm" are
both weak here

- **The stranded commits are rigorous, not paper-overs.** Read against the
  suspicion, they hold up: canaries, matrix measurements, honest scoping, and a
  revert of a change that "fixes nothing." They are a reliable *diagnosis* to
  read from — but they sit on a pre-U56 tree, one built-broken on u58 (cause
  unattributed: fix, 21% ZigEmitter drift, or a build flake), and they encode
  problems the effort itself judged "wait for an instrument."
- **The fast Rust arm cannot reproduce these failures.** The Rust tree has *no
  zig plug* — only `irdump`/`codexrun`. The failure is "the zig plug refuses,"
  which `irdump` cannot show; inspecting whether a tvar survives in IR text is a
  weak proxy, and the interpreter is *happy* with those tvars. The one
  genuinely transferable frontend fix — lambda spans — is already done in both
  trees. So iterating in Rust does not settle A, B, or C.

## The honest plan

1. **The corpus and arms are the deliverable already landed** — five arms, and
   `run-zig` is what surfaced all six. That value is banked.
2. **Cat C (discard) is the one shippable clean fix.** Re-derive it against the
   current `ZigEmitter`, verify it pushes `alias-original` and
   `list-called-twice` through, and gate on the native fixed point (the broken
   rebuild is a warning). One codexzig build, at the end, not per commit.
3. **Cat A (monomorphization) and Cat B (empty-list default) are upstream
   design questions, not bugs to "solve" locally.** Raise them with Damian,
   backed by the existing evidence — findings 60/64 and COMPILER-30 already did
   the hard diagnosis. A is the plug/monomorphization boundary; B is a
   defaulting policy. Neither is a fast-loop fix, and A has a known-failed
   attempt.
4. **First settle the attribution that is cheap:** was the broken u58 codexzig
   the fix or the drift? One clean-u58 sandbox rebuild (no fix) answers it
   without touching the fix logic.

## Where the first draft was wrong (for the record)

- Claimed the `__lam` tvars were an unresolved type the checker "never pinned."
  They are `iter-map`'s legitimate generics; the interpreter runs with them.
  The layer is monomorphization/plug, not checker carry-forward.
- Claimed `irdump` proves "our frontend is correct, upstream's is wrong." The
  Rust tree has no zig plug, so this was never tested; the tvar-count difference
  is not evidence the zig plug would accept our IR.
- Stated `(list error)` as current behavior for `alias-empty`. Stale — both
  frontends emit `(list (tvar 283))` now; `(list error)` was pre-`8f1b202a`.
- Called `8f1b202a` the fix for `alias-empty`. It fixed `fold-empty`; it does
  not transfer.
- Framed the stranded commits as likely paper-overs. On reading, they are
  disciplined root-cause work.
- Said "start with `__lam` — highest leverage." Backwards: it is the hardest
  residue with a reverted prior attempt.
