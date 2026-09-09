# The Roc programs expose IR type errors — a clean-slate plan

## What we actually have

Six Roc-origin Codex programs compile and run correctly on the Rust
interpreter and the wasm plug, produce Roc's expected answer on both, and
**cannot be pushed through the zig plug.** The zig plug is the strict one: it
demands concrete types and refuses what the other two tolerate. So the six are
not "zig bugs" in the first instance — they are **type-resolution gaps the zig
plug is honest enough to surface.**

    roc-iter-map        unresolved type variable T16 of __lam_0
    roc-iter-keep-if    unresolved type variable ...
    roc-iter-drop-if    unresolved type variable ...
    roc-alias-empty     no element type for this empty list
    roc-alias-original  pointless discard of local constant
    roc-list-called-twice  pointless discard of local constant

## Two different problems wearing one "6 failures" label

**Four are IR type errors** — the frontend hands the plug a type it never
resolved:

- **The `__lam_0` cluster (3).** A comprehension/closure inside a polymorphic
  function leaves a type variable unbound in the IR. The checker never pinned
  it; the plug meets a free variable and cannot emit for it. Our own Rust
  frontend has the *same* family — I fixed one instance today (`acc & (for x
  in xs -> ...)` left `map-list`'s result element a free tvar because the `&`
  arm didn't unify its operands). This is the same shape one layer over.
- **The empty list (1).** The checker *does* solve the element type (from a
  parameter one line down), but never files it where lowering can read it, so
  `lower-empty-list` falls to `IrList [] ErrorTy` and the wire carries
  `(list error)`.

**Two are not IR type errors at all** — `alias-original` and
`list-called-twice` are an emitter codegen fault: the zig plug emits `_ = x;`
to sequence an unused binding, then also uses `x`, and zig rejects the
pointless discard. That is a plug bug, not a frontend one.

So "the core problem is IR types" is true for four of the six, and the pair
should be tracked separately.

## Where the fix belongs

The zig plug refusing an unresolved type is **correct** — fail-loud is the
floor. The defect is upstream of it: the checker solves these types (or could)
and does not **carry the knowledge forward** — it does not file the empty
list's element type, and it does not pin the closure's type variable. The right
layer is the checker/lowering boundary: resolve the type and file it under a
span so the IR, and therefore *every* plug, gets a concrete type. Fixing the
plug to swallow an unresolved variable would be the paper-over.

## Why the stranded commits are a trap, not a shortcut

We have ~14 commits on `roc-ports-type-recovery` (and one on
`roc-corpus-ports`) that Steve wrote a week ago against these exact programs,
on a pre-U56 base, never sent. They map onto the findings by subject line. But:

- **Low confidence they fix at the right layer; fair confidence at least some
  paper over.** The discard fix alone is a base commit plus three refinements
  ("only for a LOCAL", "only if read elsewhere", "correct the prose") — a shape
  that says the first rule was wrong and got narrowed by trial.
- **Verifying them is expensive and fragile.** Testing one commit means
  rebuilding codexzig through QEMU guest stages — ~7 minutes. And the one build
  we ran (the discard fix on u58) **produced a broken codexzig**: it failed the
  native fixed-point check and core-dumps on every input. Whether the fix
  breaks self-transpilation or the fixed point is just delicate, carrying these
  commits blind — and shipping them to Damian — is the opposite of careful.

## The asymmetry to exploit: two frontends, one fast

The IR type errors live in the **frontend**, and we have two:

- **Upstream's** (`codexir`/`codexzig`) — iterating it means QEMU guest builds,
  minutes each, fragile, and it is the one bound for Damian.
- **Ours** (`irdump`/`codexrun`, the Rust reimplementation) — `cargo build`,
  seconds, no guest, and I already fixed a member of the `__lam` family in it
  today.

`ir-irdump` already tells us both frontends share these gaps: for
`alias-empty` the two agree — on the *same wrong* `(list error)`; for the iter
cluster they differ only in how they spell the unresolved variable. So the Rust
frontend reproduces the core problem and can be fixed and re-tested in seconds.

## The plan

1. **Solve the IR type errors in the Rust frontend first**, at the right layer
   (checker resolves and files the type). Use `irdump` on the four IR-type
   programs as the fast loop; success is IR with no free type variable and no
   `error` type, checked in seconds. This is where we understand the root cause
   without paying QEMU per iteration.
2. **Port each understood fix to upstream's Codex source as one clean commit
   per root cause** — not the stack of refinements — and only then pay for one
   codexzig rebuild to confirm the program pushes through and self-hosting still
   holds.
3. **Treat the discard pair (Cat 3) separately** as a plug codegen fix, small
   and self-contained, but with the self-hosting check as a gate given the
   broken rebuild we just saw.
4. **Time-box.** The `__lam` type-variable resolution covers three of the six
   and is the same family as today's Rust fix — highest leverage, start there.
5. **Keep the old commits as a reference, not a source.** They point at the
   right programs and the right files; read them for the diagnosis, re-derive
   the fix cleanly. Do not cherry-pick them into a PR.

## Open questions (worth a second pair of eyes)

- Are these type errors real Codex-language bugs, or artifacts of the ports'
  adaptations (the `Iter`/`Step` encoding, the ignored thunk argument)? Worth
  reproducing the `__lam` gap in idiomatic Codex before calling it upstream's.
- Is the empty-list case genuinely "solved but not filed," or is there no
  constraint at all in some of these (a truly phantom element type that no
  layer can resolve, where defaulting is the only honest answer)?
- The Rust frontend and upstream's diverge on the iter cluster's spelling. If
  we fix ours, do we fix it the way upstream should, or just a way that
  happens to satisfy `irdump`'s own lowering?
- Is fixing the Rust frontend actually on the critical path to an upstream PR,
  or a detour? The deliverable Damian needs is a Codex-source fix; the Rust arm
  is the lab, not the product.
