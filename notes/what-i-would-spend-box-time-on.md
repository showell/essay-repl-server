# What I would spend box time on, if it were my budget

*2026-08-30. Steve asked: for an emitter change specifically, with finite time,
what would I actually do? The honest answer starts with an economic fact we have
been ignoring, and most of the strategy falls out of it.*

## One fact does most of the work

**You never need to RUN a program whose emitted zig is byte-identical across the
two arms.** Same source text, same zig version, same binary, same output. Its
verdict cannot have moved. Running it is not a weak test — it is a guaranteed
tautology, paid for at full price.

We already believe this. `corpus_run.py --changed` carries a banked verdict when
"the emitted zig is byte-identical to the banked hash AND the toolchain that
produced the banked verdict is the toolchain that would rerun it." The mechanism
exists. It is pointed at a **bank** — the same tree yesterday — instead of at
**the other arm**, which is the comparison we actually care about.

Look at what that cost on the bitcast change. The sweep ran 326 programs per
arm. Three emitted files differed. **323 of those 326 runs were provably
unnecessary before they started**, and the information needed to skip them —
the transpile stage's `zig_sha` per program — had already been computed, in the
cheap stage, minutes earlier.

The two stages have wildly different prices. Transpiling all 1,704 programs is
native-only: no QEMU, no zig compilation, minutes. Running them is zig build plus
execute, per program, and it is the whole cost. So:

**Transpile everything. Run only what differs.**

Cost then scales with the *blast radius of the change*, not with the size of the
corpus. A narrow emitter fix pays for three programs. A prelude change that
touches every file pays for everything — correctly, because that change really is
global. The budget self-adjusts, and nobody has to guess.

## Select by emitted output, not by source

Derived selection from `cites` is real and I built it today: the arc tangent
affects 5 of 1,704 programs, computed in a second, where a full sweep took 28
minutes to say nothing. But for the change Steve is asking about it gives
nothing. A `ZigEmitter` edit writes every program's output; no cite relationship
narrows it. `affected.py` says `SCOPE: all` and it is right.

The move that *does* work for emitter changes is to select on the **artifact**
rather than the source. We have 1,704 emitted `.zig` files on disk from the last
sweep. If a change touches the emission of `IrMulRealTrapping`, the programs that
can possibly reveal it are the ones whose previous zig contains that construct.
That is a grep over cached text — free — and it converts "I have no idea which
programs matter" into a named list, before the box is touched.

Source-based selection asks *what does this program cite*. Output-based selection
asks *what does this program actually emit*. For a plug change only the second
question has an answer, and we have never asked it.

## The middle tier nobody uses: compile without running

Right now there are two stages, transpile and run, and "run" means build **and**
execute. But the most common emitter defect is not a wrong answer — it is zig
refusing the file. Shadowed declarations, undeclared identifiers, a type that
contains itself. Every one of those is caught by `zig build-exe` alone, at a
fraction of execution cost, with no `.expected` needed and no oracle involved.

Three tiers, three prices, three yields:

| stage | cost | catches |
|---|---|---|
| transpile | minutes, all 1,704 | emission changed at all; `@compileError` markers |
| compile | seconds each, only what differs | invalid zig — the commonest emitter defect |
| execute | seconds each, only what compiles | wrong answers |

Splitting build from execute gives a rung we do not currently have, and it is the
rung where most emitter bugs die.

## What a targeted test can and cannot do

Steve's instinct is right: for an emitter change the first and most direct thing
is a well-written test in the depot's corpus, settled on bare metal. That answers
the question that matters most — *does this construct emit correctly* — exactly,
cheaply, and permanently.

But it answers it **in isolation**, and that is the limit worth naming. The
author writes the construct the way they are imagining it. The corpus exercises
it in **composition**: nested inside a closure, inside a match arm, under a self
tail call, as an argument to something that was itself inlined away.

The bitcast run showed this concretely. The targeted test used `real-to-bits` on
literals. The corpus used it inside `vec-array`, in an expression already full of
`@compileError` for three *other* missing emitters, and inside `sparkplug-encode`
beside `real-approx-to-bits` which still refuses. Neither is a case anybody would
think to write by hand, and both are exactly where an emitter's assumptions get
tested.

So: **targeted test proves the construct; corpus proves the composition.**
Neither substitutes for the other, and knowing which one you are buying is how
you decide whether to buy it.

## Never write a probe you throw away

A one-off probe and a depot test cost the same to write. The probe dies with the
sandbox; the test becomes Damian's regression forever *and* enters our corpus
permanently, so every future change gets it free.

We have been doing this right by accident on the outbound work — `real-bitcast-f64`
and `real-int-conversions` are depot tests, not probes — and wrong everywhere
else. The four `zz-*` probes that diagnosed the inlining rule no longer exist,
which is why that finding could not be re-checked today and had to be
re-derived from the compiler source.

The rule I would enforce: **if it is worth running twice, it goes in
`codex/test/`.** No exceptions for "this is just to check something."

## Full corpus is drift detection, not a gate

This is the part I would change most.

A full corpus run answers *has anything in this tree drifted* — a question about
the tree, not about your change. Running it per-change pays for the same answer
repeatedly. If it ran nightly and was green at 3 a.m., a full run at 10 a.m.
against a small emitter change tells you almost nothing you did not already know.

Move it. Full sweep once per Update, or nightly when the box is idle, as a
**background** activity whose job is catching accumulated drift. Per-change
spending goes to the targeted test, the transpile byte-diff, and the differing
set. The expensive instrument gets pointed at the question only it can answer,
instead of being used as an anxiety reducer on every commit.

## Measure the yield, and retire what stops catching

`BOX.md` says an item that stops catching anything should be deleted rather than
kept for completeness. That principle applies to test tiers and we have never
applied it, because we do not record what each tier caught.

We should. One line per run in the result artifact: what did the full sweep find
that the targeted test did not? If the answer is "nothing, eleven runs in a row,"
that is an argument to move it to weekly, made of evidence instead of feel. If it
catches a real regression every third run, that is an argument to keep paying.
Right now we cannot answer the question at all, which means the budget is set by
whoever is most nervous.

## The policy I would actually run

**Per emitter change, always, ~10 minutes:**

1. A depot test for the construct, `.expected` settled on bare metal with an
   untouched control. This is the deliverable, not the scaffolding.
2. Full transpile, both arms. Byte-diff the emitted zig.
3. **Read the diff set.** If it is empty and you expected it not to be, stop —
   that is the presence check failing, and it is the most valuable signal you
   will get all day.

**Then, proportional to what moved:**

4. Compile the differing programs. Then run them, both arms.
5. Bare-metal any program whose verdict moved. Never wholesale — two guests each.

**Periodically, not per change:**

6. One full corpus run per Update, or nightly on an idle box. Its job is drift.
7. The tier set and the fixed point stay where they are: they answer a different
   question and they are cheap relative to what they cover.

**Always:**

8. Every result is a committed artifact, and the yield line goes in it.

The shape of this is that **cheap and total beats expensive and sampled**.
Transpiling everything costs minutes and tells you exactly where to spend the
expensive stage. We have been doing the reverse — running an expensive stage
across a corpus we had already narrowed by accident, and reading the result
through `tail`.

*— Claude*
