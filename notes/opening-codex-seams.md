# Where opening.codex comes apart

Measured at Update 55 (`675a0775`), on first principles, with the collapse
rather than by reading.

`codex/compiler/opening.codex` is **2,385 lines and 191 definitions**. It is the
chapter every harness we own has spent two years standing in for, and the one
Update 55 finally made bundlable.

---

## What cohesion says, and why it is not enough

    compiler/opening.codex   defs 191 (162 fn)  edges 282  components 7  SPLIT

Seven components sounds like seven pieces. It is not: one component holds 184
definitions and the other six are strays. That is the same answer cohesion gave
for `Render.codex` and for `ZigEmitter.codex`, and it is the same answer for the
same reason — a chapter can be one connected blob and still be two programs.

The collapse is what sees it. Absorb every single-caller definition into its
caller, to a fixed point, and what survives is the shared spine:

| block | lines | defs | callers |
|---|---|---|---|
| `codex-opening` | **1,499** | 125 | **0** |
| `compile-checked` | 444 | 20 | 2 |
| `compile-frontend-passes` | 69 | 2 | 2 |
| `compact-phase` | 37 | 6 | 3 |
| everything else | ~300 | 38 | — |

**Sixty-three per cent of the chapter is reachable only from the entry point.**
The compile driver — the part plugs, harnesses and the ladder actually call — is
about five hundred lines. The rest is the program that wraps it.

## The cut is the opposite of the one we proposed

PR 116 asked upstream to move 69 definitions OUT into a `Compile Driver`
chapter, leaving `opening` behind. Upstream closed it in favour of a smaller cut
— `opening` becomes `codex-opening`, a fourteen-line `EntryPoint.codex` holds
the entry point — and they were right on the merits.

But the collapse says the interesting cut runs the other way. The driver is the
small, stable, widely-called thing. The **entry point's own machinery is the
1,499 lines**, and nothing outside it reaches any of it.

## Three leaves, measured

For each candidate I asked the two questions that decide whether a split is
free: what does it call outside itself, and how many names is it entered
through. A block that calls nothing out and is entered through a handful of
names moves without argument.

| candidate | defs | bytes | calls out | entry points |
|---|---|---|---|---|
| **Quotations** | 31 | 12,126 | **0** | 4 |
| **Measurement** | 9 | 2,309 | **0** | 4 |
| **Disk loading** | 7 | 4,515 | 2 | **1** |
| Deck arithmetic and poison | 21 | 9,710 | 3 | 12 |

### Quotations — the one to take first

Sections `Quoted Works`, `Hex`, `Reading The Offered Works` and
`Refusing A Quotation`. Thirty-one definitions that **call nothing else in the
chapter at all**, entered through exactly four names:

    compile-with-quotations -> build-works
    compile-with-quotations -> resolve-quotations
    dispatch-on-mode        -> has-quotations
    dispatch-on-mode        -> split-quoted-works

Two callers, four names, zero outbound edges. This is the shape `ZigPrelude`
had, and that one moved without a single semantic change.

It is also a coherent SUBJECT rather than a coherent call graph, which is the
better test: it is the signed-works trust system — marker scanning, hex
decoding, digest checking, and the seven refusal diagnostics
(`ImportCorrupt`, `ImportForged`, `ImportUnsigned`, `ImportUntrusted`,
`ImportUnknownSigner`, `ImportMissing`, `ImportOk`). Someone auditing how
Codex decides to trust a quoted work should be able to read one file.

Apply the deletability test: **if quotations were removed from the compiler,
what would you delete?** Exactly these thirty-one definitions and nothing else.

### Measurement — nine definitions of pure formatting

`format-phase-metrics`, `format-heap-marks`, `emit-mark-labels` and their loops.
Zero outbound edges, four entry points, and it is text formatting of numbers the
phases already produced. It has no business sitting in the same file as the
deck arithmetic that produced them.

### Disk loading — seven definitions, one door

`Library Loading` and `Disk Foreword Loading`, entered through the single name
`disk-resolve-forewords`. It calls out only to `scaled-floor` and
`effective-deck-scale`, which are deck policy and belong to the spine either
way. One entry point is as clean as a seam gets.

### Deck arithmetic and poison — the spine, not a leaf

Twenty-one definitions entered through **twelve** names: `scaled-floor`,
`effective-deck-scale`, `compact-phase`, `pipeline-of`, and the seven
`poison-*`. That is not a chapter waiting to be extracted, it is the policy
layer everything else consults. It either stays put or becomes a chapter that
the driver and the entry point both cite — and the second only pays if the
driver and the entry point become separate chapters first.

## What I would do, in order

1. **`Quotations`** — 31 definitions, zero coupling, a nameable subject. It is
   the free one and it is worth doing on its own merits.
2. **`PhaseReport`** (the Measurement nine) — small, pure, obviously misfiled.
3. **`DiskForeword`** (the seven) — one door.

That is 47 definitions and about 19 KB out of the file, all of it verified to
call nothing it would leave behind.

What it does NOT do is split the driver from the entry point, which is the
1,499-line question and the one worth arguing about with upstream rather than
deciding for them. Their EntryPoint cut says they are already thinking about it.

## One thing worth telling Damian regardless

`opening.codex` **reads `run-ir-pipeline`, `default-ir-pipeline`,
`ir-check-violation-bag` and `occ-info-bag` while citing nothing that defines
them.** B5 gives a bundle one flat namespace, so upstream never notices: some
other chapter's cite drags `IR/Passes.codex` in and the name resolves.

We noticed because a subject assembled from the cite list alone does not
resolve them — twenty `CDX3002`s at a time. It means a chapter's cite list is
not a description of its dependencies, which is a fair thing to know before
anyone splits this file, us or them.

`xref bundle` now reports it in four seconds.
