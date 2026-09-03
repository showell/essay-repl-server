# The wasm arms: provenance and chain of proof

2026-09-03. What is actually proven about the wasm baseline, what is assumed,
and where the trust enters. Written because "the fixed point holds" is four
words doing a great deal of work.

---

## The claim, stated narrowly

**The U53 base is self-consistent across three artifacts.** That is all. It is
not a claim about U54, about U55, about our unlanded patches, or about the wasm
emitter being correct in general.

## The trust root, and it is one file

    seed/Codex.cdx      3,064,878 bytes      sha256 b066ceb5fe8fc9e8

Everything below descends from that binary, which we did not build and cannot
check: it is upstream's released seed. Its first eight hex digits are its name,
`B066CEB5`, which is how the Update 53 release note refers to it.

**And the whole wasm base runs on that exact seed.** The tree the arms are built
from, `9632bb87`, is Update 53 plus 23 commits, and its seed is byte-identical
to the release's -- those 23 commits moved plug source and not the image. For
contrast, U54's seed is `fcbabf07` and U55's is `81f9e817`; neither is in this
story anywhere.

Below the seed the trust widens to QEMU 8.2.2, zig 0.16.0, node v22, wabt, and
this box. None of those are verified by anything here either.

## Chain A -- codexzig, and what certifies it

    seed Codex.cdx
      |  GUEST 1  bundle + compile the ring plug        ringplug.cdx
      |  GUEST 2  compile the transpiler subject        codexzig.ir
      |  GUEST 3  push that IR through the ring plug    codexzig.qemu.zig
      |  host     zig build-exe                         codexzig  (native)
      |  host     the binary transpiles the SAME source codexzig.native.zig
      v
    DIFF: qemu.zig  ==  native.zig          <- THE FIXED POINT

The artifact in use: `codexzig-safari/generated/local/codexzig`,
27,897,741 bytes, sha256 `c853b92220729ba7`, built 2026-09-01 from `9632bb87`
in 437 s. Its certificate says `fixed point HOLDS` and
`arith.codex MATCHES arith.expected`.

**What that proves.** The emitter produces the same zig from the same source in
two very different execution environments -- as a bootable kernel on bare metal
under QEMU, and as a native Linux binary. Those two disagree if the emitter
depends on anything environmental, which is the class of bug the arrangement
exists to catch.

**What it does not prove.** That the emitted zig is CORRECT. Two identical
wrong answers agree perfectly. The sample program (`arith.codex` matching its
expected output) is the only behavioural evidence in this chain, and it is one
program.

**A second codexzig exists on this box** -- `codex-zig-transpiler`'s, sha256
`a47a914be0f73a80`, built from `2f7e7375`. It is NOT the one safari uses, and
the two are not a mixture: `2f7e7375` is an ANCESTOR of `9632bb87`, U53+3 under
U53+23. `harness/build_codexzig.sh` resolves `$CODEXZIG_TREE` and names it
rather than searching, which is what keeps the wrong binary out.

## Chain B -- the wasm module, which does not involve codexzig at all

    codexwasm-subject.codex        bundled from 9632bb87  (2,925,013 bytes)
      |  compiled BY generated/codexwasm.wasm  -- the tracked module ITSELF
      v
    generation-2 WAT
      |
      v
    DIFF against generated/codexwasm.wat     <- THE FIXED POINT
      |  wabt
      v
    codexwasm.wasm    806,061 bytes   sha256 4dde1d141a1d2969

Run today on `--road self`, 35 s: **fixed point HOLDS, sample matches.**

**No zig, no QEMU, no seed is in this loop.** The transformer is the previous
module. This is worth saying because "fixed point holds" reads like one
statement and there are two different ones in this document.

**What it proves.** The module compiles the source that produced it and gets
itself back, byte for byte. A module that had drifted from its source, or a
source edited without rebuilding, breaks it.

**What it does not prove.** Correctness of the wasm emitter beyond
self-reproduction, and the repository's own PROVENANCE says so in its header:
*"the fixed point cannot supply the difference -- it holds just as well against
the wrong source."* Which is exactly why the source is named by sha256 beside
it.

The baseline is now a DETACHED pin, `cobblestone-wasm53` at `9632bb87`. The
build had been reporting `checkout is on refs/heads/wasm-slot-from-type, not
detached -- it can move under a build`, and PROVENANCE.md asks for a checkout
that stays put. Re-running against the pin changed no artifact: subject, .wat
and .wasm all carry the same sha256 as before. Cleaner provenance, identical
bytes.

## Chain C -- safari's native codexwasm

    codexzig  (Chain A, c853b922)
      |  < safari's codexwasm-subject.codex   (61,278 lines, 2,923,711 bytes)
      v
    build/codexwasm.zig     2,486,690 bytes
      |  zig build-exe
      v
    build/codexwasm    28,208,632 bytes   sha256 8070173397f72e32

Keyed, in `harness/build_codexwasm.sh`, by BOTH inputs:

    want=$( { sha256sum "$subject"; sha256sum "$codexzig"; } | sha256sum )

with the reason written beside it: *"the binary is a function of both: rebuild
the base transpiler underneath this and a key on the bundle alone hands back a
stale codexwasm saying it already matches -- in the one situation where it is
most likely to be wrong."*

**This is the nesting done right.** Each level keys on the CONTENT of the level
below, so a change anywhere under it invalidates everything above. It does not
need to reproduce the lower level's provenance, because a sha256 of the binary
is a complete identifier for it.

**What it proves today.** That the leg runs and produces a binary from the
current safari source. Nothing about that binary's OUTPUT yet -- the wasm tier
has not run.

## Where the chains meet, and where they do not

Chains B and C are **independent roads to the same job**: both turn Codex into
WAT. Chain B's module is wasm; Chain C's is a native binary. They share the tree
(`9632bb87`) and nothing else -- B never touches zig, C never touches the wasm
module.

That independence is the strongest evidence available here, and **it has not
been cashed in.** Running the same Codex source through both and diffing the WAT
would be a real cross-check, because the two roads share only their source. No
such comparison has been run today.

## "Vestiges of U53" is the wrong mental model

The question came up whether we want U53 vestiges left in the chain. The framing
needs inverting: **there are no vestiges, because the chain is U53 in its
entirety.** One file at the root, `b066ceb5`, and everything else a descendant
of it. Nothing else is in there to remove.

Which means a U55-rooted chain **shares no artifact with this one**. Different
seed (`81f9e817`), therefore a different codexzig, a different module, a
different `build/codexwasm`. It is not a cleanup pass; it is the same three
chains built again from the top.

**The hazard is a MIXTURE, not a leftover.** Handing the U53 codexzig a U55
source is the dangerous shape, and it is worth being precise about why the keys
do not save you: content keys defend against STALENESS -- change an input and
everything above it is invalidated -- but a mismatched pair produces a key that
is perfectly valid and an artifact that is wrong. What defends against a mixture
is naming `COBBLESTONE_ROOT` rather than defaulting it, which every script here
does, and the tendency of a pre-U55 compiler to refuse U55 source loudly
(`CDX2071`) rather than miscompile it.

So the two goals are separate, and only one of them is met today: a working
baseline, which is U53 top to bottom and coherent; and a chain rooted at the
current release, which is blocked on a plug that cannot emit `peek-32`.

## The honest ledger

**Proven today, on this box:**

- The wasm module reproduces itself from its own source at `9632bb87`. 35 s.
- The baseline is recorded against a detached pin, and the artifacts are
  byte-identical to the previous build.
- `build/codexwasm` rebuilds from the named codexzig and the current safari
  source, no guest.

**Assumed, and reasonably:**

- The seed is what upstream released.
- codexzig's certificate from 2026-09-01 still describes the binary on disk --
  its sha256 is recorded, so this is checkable and was not re-checked today.
- QEMU, zig, node and wabt behave.

**Not proven, and not claimed:**

- Anything about **U55**. A U53-era module halts on U55 source with
  `CDX2071 Integer literal '9223372036854775808' exceeds 64 bits`, U55's newly
  writable i64 minimum. Both roads start pre-U55 and both are blocked the same
  way.
- That the wasm emitter is correct where the fixed point cannot see. Known gaps
  exist and finding more of them is deliberately not the goal.
- **safari's wasm tier has not run.** The codex -> wasm workflow is built but
  not yet exercised, which is the one remaining item of the three.
