# The wasm arms are already bootstrapped, and the nest is sound

Analysis, 2026-09-03, before spending any box time.

The question was how quickly we can get bootstrapped on U53-ish versions of
everything the wasm arms need. The answer is that we already are, on one
coherent base, and the refresh costs **no guest at all**.

---

## The base is 9632bb87, and three artifacts agree on it

| artifact | built from |
|---|---|
| `cobblestone-safari` (safari's `CODEX_ROOT`) | **9632bb87** |
| `codexzig-safari/generated/local/codexzig` | **9632bb87** |
| `codex-wasm-transpiler/generated/codexwasm.wasm` | **9632bb87** |

`9632bb87` is the U53 release plus 23 commits -- `wasm plug: a guard's scrutinee
bump leaked into its sibling branches`. Every artifact the wasm arms consume was
produced from that one tree. Nothing is mixed.

There is a SECOND codexzig on this box, `codex-zig-transpiler`'s, built from
`2f7e7375` -- U53 plus 3. It is not the one safari uses and it should not be:
`harness/build_codexzig.sh` resolves `$CODEXZIG_TREE`, defaulting to
`codexzig-safari`, and names it rather than searching. Two binaries with the
same name from different trees is exactly the hazard that naming defends
against.

The two trees are not in conflict, and it is worth seeing why: **2f7e7375 is an
ANCESTOR of 9632bb87.** The binary that built the wasm module came from an
earlier point on the same line, which is what a bootstrap looks like rather than
a mixture.

## The nest, level by level

    seed Codex.cdx  (U53-era)
      |  QEMU x3, codex-zig-transpiler's nine stages
      v
    codexzig            native binary      <- keyed by its own repo's PROVENANCE
      |  codexzig < codexwasm-subject.codex
      v
    codexwasm.zig
      |  zig build-exe
      v
    build/codexwasm     native binary      <- keyed by (subject, codexzig)
      |
      v
    safari .wat

**The guest cost is at the top and it is already paid.** Everything below
`codexzig` is native: a binary invocation and a zig compile. Refreshing the wasm
arms on this base needs no QEMU, no seed and no lock.

## The provenance already nests, and I expected it not to

I went looking for the gap and did not find one.

**safari keys on both levels.** `harness/build_codexwasm.sh`:

    want=$( { sha256sum "$subject"; sha256sum "$codexzig"; } | sha256sum )

with its own reason written down: *"the binary is a function of both: rebuild
the base transpiler underneath this and a key on the bundle alone hands back a
stale codexwasm saying it already matches -- in the one situation where it is
most likely to be wrong."* That is the nesting problem, solved, with the
incident that taught it.

**codex-wasm-transpiler records its transformer too.** On `--road zig` its
PROVENANCE carries the codexzig path, its sha256, and a note saying the binary
is in the trusted base and its own provenance belongs to its repository. It is
absent from the file currently on disk only because that build took
`--road self`.

**And `--road self` needs no such line, because the fixed point supplies it.**
The module compiles the source that produced it and must get itself back byte
for byte; when that holds, the module that RAN and the module recorded as
`assembled` are the same bytes. The identity is the invariant, not an omission.

So the honest finding is: nothing to fix here. I had drafted a change to add the
missing axis and then found the axis already present.

## What is actually stale, and why that is correct

`safari-codex/build/codexwasm.fp` does not match a freshly computed key. That is
not rot -- it is **today's chapter splits**. We moved 109 definitions into
`ZigPrelude.codex` and split the emitter four ways, so safari's subject changed
and the gate says rebuild. It is the mechanism working, in the direction it is
supposed to work.

## The fastest path, in order

1. **Rebuild `safari-codex/build/codexwasm`** from the existing
   `codexzig-safari` binary. One codexzig run plus one `zig build-exe`. No
   guest.
2. **Run safari's wasm tier** against it. That exercises the whole
   codex -> zig -> wasm leg on a base that is internally consistent.
3. **Leave `codex-wasm-transpiler` on `--road self`** for a U53-ish check. Its
   module and its `COBBLESTONE_ROOT` already agree, and the fixed point is the
   thing worth confirming.

None of that needs the box in the sense that matters -- no QEMU, no seed, no
compute lock.

## What this does NOT get us

**It does not get us to U55, and that is a separate and harder problem.** A
U53-era module cannot compile U55 source: fed `codex/test/ops/int-wrapping-
spelling.codex` it halts with

    CDX2071 Integer literal '9223372036854775808' exceeds 64 bits

which is U55's newly writable i64 minimum, from the trapping-arithmetic
spelling unit. Both roads start from a pre-U55 compiler, so both are blocked the
same way -- the same shape as the seed problem, one level up.

Getting the wasm arms to U55 means getting a U55-capable compiler first, and the
only ones are U55's own seed (QEMU) or a native built from U55, which the zig
plug cannot yet emit because `Types/Unifier.codex` calls `peek-32` and the plug
has no emitter for it. That is our unlanded `zig-plug-memory-builtins`.

So: U53-ish is free and coherent today. U55 waits on a plug fix that is already
written and not yet landed.
