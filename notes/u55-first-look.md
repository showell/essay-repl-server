# Update 55, the first look

Upstream `675a0775`, 2026-09-02. One day's work upstream: main 21230 to head.

455 files, +51,913 / −19,177. The compiler is 27 files, +1,126 / −551 —
`IR/Lowering` +319, `opening` +133, `TypeCheckerInference` +125, and
`Emit/X86_64Helpers` **−213**, which is a deletion, not a feature.

This is what U55 did with our work, and what it did to our ability to measure
it. Nothing here is a rebank; the sweep that would ground a rebank cannot run
yet, and the reason is the most useful thing on this page.

---

## a) Our issues, addressed and landed

**Issue 109 → COMPILER-36: plain `Integer` arithmetic traps on overflow.**
Ruled GO by Damian on 2026-09-02 and landed the same cycle: multiply (21676),
add and sub (21798), and a spelling unit (21902). `jno; ud2` after the op on
x86-64, keyed on the node's type. The wrapping band is spelled explicitly —
`mul-int-wrapping`, `add-int-wrapping`, `sub-int-wrapping` — and
`Foreword chapter Wrap64` now carries the mixers and hash accumulators that
wrap *by design*, declared rather than silently wrapped.

The plugs follow as backlog row 2.21. **zig and csharp are 57 of 57 on the
oracle.** That is our issue closed, in the compiler and in our plug, in one
cycle.

Their own lesson from it is worth stealing: the first grep for ten-digit
multipliers declared the compiler clean, and two gates then died in
accumulators spelled `h * 33 + c` and `acc * 10 + d`. A grep for the
*constant* missed the *shape*.

**Issue 115 → COMPILER-48 instance 5: an emit deck overflow faults instead of
corrupting.** Landed at 22074 and 22100. `emit-build` was `build` minus the
deck reservation guard and minus the top-cell poke, so `__deck-enter` armed
whatever the previous phase left — a measured ceiling of 449,847,088 against
an emit top of 16,392,728. **27x above the extent, with the UD2 unreachable.**
The undersized case without the fix exits 0, with output, having overrun by
about 150 MB that nothing noticed.

**safari-codex, taken in with credit** (22154, 22160). All twenty-seven port
chapters compile clean at their head — the staged expectation had been a red
compile — and the green is non-vacuous by its own control, an undefined name
reddening at the predicted line. Then through their wasm plug: an 11.3 MB WAT,
730 functions, a 1.57 MB module running under node (22205). Our eighteen
grader chapters run against our gold values (22215), and the ride's frame cost
was flattened (22221). `PROVENANCE.md` names the fork it was built against.

## b) Landed, but not all of it

The zig plug at U55, builtin by builtin:

| landed | absent |
|---|---|
| `address-of` | `peek-32` |
| `peek-byte` | `poke-32` |
| `hosted-kind` | `poke-byte` |
| `real-to-bits` | `__memset` |
| `bits-to-real` | `alloc-bytes` |
| | `real-to-int` |
| | `real-from-int` |

So the half of the memory-builtin work that unblocks the *native* build is in,
and the half our `zig-plug-memory-builtins` and `zig-plug-real-conversions`
branches carry is not. Those two are still ours to land.

**The backlog rows they were filed against have been reused.** Our PRs cite
plugs rows 2.19 and 2.20; at U55 those numbers belong to the img plug's
corrupted `SOURCE.SRC` and to the evidence plug that was built and never run.
This is the second cycle in a row that our row number went stale before the PR
was read — U54 already moved one row for the same reason. A PR that cites a
number is citing something that moves; it should cite the defect.

## c) Punted, deliberately and on the record

**COMPILER-42, list append, is now "the agents' problem."** Damian struck the
question from his queue for good on 2026-09-02. The bar he left behind is a
good one: any change on the append path needs a measurement that no previously
linear line went quadratic.

The arc landed the same evening — an ownership analysis deciding per push site
whether the list is owned, with `__list_snoc_copy` and `$list_push_copy`
helpers; the census reads 69 push sites, 51 in place and 18 copying. **And the
rewrite pass ships OFF by default**, because the end-to-end arm measured memory
linear and correctness broken: a compiler built with the pass applied to itself
crashes in `mcopy-labels`, wearing a deck-overflow costume on the large source.

That is the honest shape of it, said out loud in their own release note.

## d) What U55 did to our ability to measure it

This is the part that costs us.

**`lower-chapter` moved again, and this time it is not a token.**

```
U53   8 params                          -> IRChapter
U54   9 params  (+ rename : Boolean)    -> IRChapter
U55  11 params  (+ keep-base, keep-ceiling) -> (IRChapter, Integer)
```

U54's addition was one `Boolean` and we fixed it by passing `True`. U55's is
not that. `lower-chapter` now does `__deck-set keep-base` itself and
`lower-defs-keep` stops when `keep + guard >= keep-ceiling` — it manages a deck
*keep* region on the caller's behalf, which is stage 3 of the memory campaign
(DESUGAR straight into the frontend keep, host peak 550 → 506 MB). Passing
zeros is not available the way `ceiling = 0` was; zero ceiling stops the lift
on the first definition, and `__deck-set 0` is worse.

**Every harness we own that lowers has to learn the keep protocol.** The
ladder's `IrToCodexHarness`, `IrToX86Harness`, `LowerHarness`, `CodexIrHarness`
and `CodexZigHarness`, and `codex-zig-transpiler`'s `CodexZigHarness`. The
symptom is not an arity error — the call yields a *function value*, and it
surfaces one line later as

```
CDX2001: Type mismatch: Rec:IRChapter vs Fun
```

against `run-ir-pipeline`, naming neither the call nor the argument it wants.
It cost an afternoon to read that once at U54; it will cost minutes now.

**Where the sweep stopped.** `allcycles.sh` at U55 built the IR for lex, parse,
desugar, scope, check and lower, then died on `ir_to_codex` with exactly that
error. `0/14 rungs green, 428s in` — and no rung is *red*, because none of them
ran a comparison. There is no truth bank for this seed, so nothing to diff
against yet.

**The seed does not name itself.** `sandbox.sh` reports `seed-update
unreleased`: `seed_identity.py`'s matcher derived U54 with no change and does
not derive U55.

**U54's seed cannot compile U55's source at all.** Same input blob, two seeds:
U55 compiles it clean in 5.1 s; U54 halts with eight errors of the form
`Type mismatch: Con:Integer[T64] vs Integer` and `Arithmetic operator requires
Integer or Real`. `Con:Integer[...]` is the constrained integer the trapping
work introduced. That is not a defect — it is the type language moving, and it
means no cross-seed comparison is available on U55 source.

## e) What did not move, which is the good news

The checklist's first step is to read the diff on the surfaces we
re-implement, because a moved contract shows up as a diff in every truth at
once and is indistinguishable from a compiler change. U55 touches all three
files those contracts live in — `X86_64Boot.codex`, `tools/codex-vm.c`,
`build/vm-config.ps1` — and **moves none of them**:

| contract | ours | U55 |
|---|---|---|
| ring address | `RING_ADDR 0x500000` | `serial-ring-buf-addr = 5242880` |
| ring size | `RING_SIZE 0x100000` | `serial-ring-buf-size = 1048576` |
| write cursor | `WPOS_ADDR 28704` | `serial-write-pos-addr = 28704` |
| read cursor | `RPOS_ADDR 28712` | `serial-read-pos-addr = 28712` |

`codex-vm.c`'s 121 new lines are a Windows WHP teardown race — application
processors were not stopped before the partition was deleted under them. We run
QEMU; it does not reach us. `vm-config.ps1` is host memory accounting.

The `X86_64Boot` changes are two real fixes and both are worth knowing: the
spawn-affinity rest value was stored twelve instructions before the page tables
zeroed the page holding it (COMPILER-49), and a capability mask now goes
through a register because `or rax, imm32` **sign-extends under REX.W**, so
`or rax, 0x80000000` was setting bits 31 through 63.

And our harness gates pass at U55 unchanged: 6 emit roots, 7 bags merged, both
harnesses gated — so the generators still track `opening.codex` across its +133
lines.

---

## What this says about the next move

The measurement we actually want from a release is narrow: **bare metal and zig
agree, and nothing obviously regressed.** Everything above is either that
question or an obstacle to asking it.

The obstacle is one thing, not many: the keep protocol on `lower-chapter`. Six
harnesses, one contract, and the contract is written down in `opening.codex` in
two places we can copy. Until that is done the ladder cannot reach a rung that
compares anything, and the corpus census cannot be transpiled either, because
the emitter's own subject goes through the same call.

Nothing else found here is load-bearing. The renumbered backlog rows are an
annoyance to our PR text; the unreleased seed name is cosmetic; the U54 seed's
refusal of U55 source is the type language doing its job.
