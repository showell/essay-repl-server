# Verifying an Update with a second front end

`rust-codex-compiler` is about to meet its first Update. This is what it is
for, how to point it at U56, and what specifically to watch.

## What a second implementation is actually good for

The ladder could not find front-end defects because both its arms were
Damian's front end. Everything above the IR was invisible to it — which is
why finding 74, Real literals off by one ULP, needed an independent front end
and not a fourteenth rung.

`rust-codex-compiler` is that independent front end. When it and `codexir`
disagree about a program, exactly one of three things is true:

1. **We are wrong.** Today this is most of them, and each one is a gap in our
   own port. Useful, but it is our to-do list, not theirs.
2. **They are wrong.** Rarer, and the whole reason the arm exists.
3. **The Update changed something.** We agreed at the last pin and we do not
   agree at this one.

The third is the release instrument, and it is the one nothing else provides.
A regression suite tells you a program's output changed. It cannot tell you
whether the change was *intended*, because the suite was written by the same
people who made the change and its expectations move with it. Our compiler was
not told what U56 was trying to do. It cannot rationalise. It just reports the
delta, and the delta is attributable.

That property is fragile, and the rest of this is mostly about not breaking it.

## The protocol

**Phase 0, before the Update lands: bank a baseline.** A delta is unreadable
without one. At the current pin, record:

- the five graded counters on the 3.44 MB self-host
- the per-definition byte-identity count against `codexir` (2,845 of 2,846)
- the corpus refusal list, **by name and reason**, not just the count
- the corpus diagnostic agreement, by CDX code
- the corpus *counter* agreement, per unit — which nothing measured until
  today, and which turns out to be the densest signal of the four
- the set of units that are byte-identical

Bank it as a dated artifact. Do not track a file that every run rewrites; the
point is a frozen photograph, not a live number.

**Phase 1: repin, and change nothing else.** This is the discipline that makes
everything downstream work, and it is the one under the most pressure, because
the moment you repin you will see things you know how to fix. Do not fix them.
Every diff measured in this phase is caused by the Update. The instant we
also change our own code, attribution is gone and we are back to guessing.

**Phase 2: triage every delta into one of three buckets before closing any of
them.**

- *(a) They changed the IR on purpose.* Does our output move the same way? If
  we move identically, we have independently confirmed their change — which is
  worth saying out loud, because confirmation from outside is not free. If we
  do **not** move, either we do not implement the thing that changed (ours) or
  their change reaches further than intended (theirs).
- *(b) They changed their own source.* The subject is also the largest program
  we compile. New constructs in their compiler mean new constructs we must
  handle. Refusals here are our gap and nothing more.
- *(c) We agreed, we now disagree, and nothing in the Update says why.* This is
  the highest-value bucket and the one to work first.

**Phase 3: only now close our own gaps**, re-measure, and send what survives.

The ordering matters more than any single measurement in it.

## The subject is both the specification and the input

`codexcheck-subject.codex` is their compiler's own source at the pin we grade
against. We *port from* it and we *compile* it. On a repin, both change at
once.

The trap is obvious once stated: if we read the new subject and port from it
before measuring against it, we have thrown away the independent read. We
would be conforming to the new answer rather than testing it.

**Measure first. Port second. Every time.**

## Four instruments, and what each is blind to

No single one of these is sufficient, and today's work showed why in a way I
would not have predicted.

**The counters** (`substitutions`, `next-row-id`, `expr-types`, `next-id`,
`check-errors`) are cheap, and they are sensitive to allocation *order*, which
is the hardest property to hold. They are also blind to names, and to
anything a later pass prunes.

That blindness is not theoretical. A change landed today that synthesised two
definitions per `unit family` member. The first cut named every member
`"    "` — our CST keeps trivia, so a member's first token is whitespace, and
I took it. **Four units went byte-identical and all five counters were exact
anyway**, because those definitions are unreachable in those programs and get
pruned before emission. Only their mints showed, and mints do not care about
names. A program that actually called `Microsecond` would have emitted
nonsense.

Counter agreement is a necessary condition that can be satisfied for entirely
the wrong reason. Treat it as a filter, never as a verdict.

**The IR bytes** are decisive and noisy. A single early divergence renumbers
everything after it, so byte counts overstate. Diff by *definition*, not by
file: 2,845 of 2,846 is a sentence; "412 differing lines" is not.

**The diagnostics** catch what neither of the above can — a program both sides
accept but only one should. `corpus_check_gate.sh` answers the one question
nothing else does: *did we invent an error the oracle does not raise?* Today
that is none in 1,246 units, and it is the number that would go first if we
started guessing.

**The refusal list** is the fourth, and crashes are the finding. A refusal
with a reason is inventory; a crash is a defect.

## Attribution before closure

The failure mode that would quietly destroy this arm is closing divergences
without understanding them. Match every new output and we become a mirror of
their compiler, which measures nothing.

The rule: **every divergence gets attributed before it gets closed.** Three
outcomes, all of them worth writing down —

- ours, and here is the upstream line we were not following
- theirs, and here is the evidence
- *neither* — the construct is genuinely ambiguous and we chose

The non-findings sections in the cold reviews are this discipline in written
form. "This looks wrong and is faithful to subject line N" is as valuable as a
finding, because it stops the next reader from breaking a deliberate match.
One of them today reversed a thread I had handed the reviewer myself:
`flatten_app`'s arity-dishonest `Vec` is real, and it is upstream's, and
"fixing" it would move us away from the file we grade against.

## What to watch in U56, concretely

**The `deck-record` prediction.** We are 2,845 of 2,846 on the self-host, and
the one is PR 134 / COMPILER-55. Damian says the emitted half landed on their
main 23732 — `lower-def` now emits the already-stripped type, so sort order
stops mattering for emission, census 3 foralls to 0.

So: **on repin, expect 2,846 of 2,846.** If it does not go clean, that is the
first thing to report, and it means either the repair is narrower than
believed or we depend on the old shape. A prediction registered before the
measurement is the strongest test we have; do not let it pass unremarked if it
holds, either.

**COMPILER-66 stays open.** The ambiguous `all-bindings` table, about twenty
readers. Expect its order to still be unstable. If U56 touches `sort-by`, that
is our cue — Damian named our peak-linear-memory arm as the instrument they
would want if a stable sort becomes the repair.

**The seed moved to 12B76F40.** We do not use the seed, which makes us a clean
control: if their golds move and our IR does not, the change was in the
bootstrap path and not in the language.

**New or changed diagnostics.** We now know exactly which CDX codes we do not
implement — CDX6002 `[HardRealtime]`, 6101, 2033, 2068, 2090, 2031, 2050,
2001, 1000, 1021/1022, 1060, 3002. The corpus gate's `ours[0] oracle[N]` rows
are that inventory. **Rows that appear** are new diagnostics to port. **Rows
that disappear** are more interesting: a diagnostic removed, or a program they
now accept, and worth asking about either way.

**Synthesised definitions — now a known failure mode with a known signature,
and the richest vein we have.** Four instances so far: `unit family` members
(closed today), `deriving Eq` on records and units, `class` members, and
`instance` methods — the last of which is *named* in our own desugarer as
`synth-instance-defs` and was never written. One instance method costs the
oracle sixteen type variables and thirteen rows that we do not mint. The
signature is specific and worth committing to memory:

> `next-id` and `next-row-id` diverge by a constant while `expr-types` agrees.

That is a registration-time mint we are missing, not an ordering bug in the
walk, because every synthesised span is synthetic and `record-expr-type` skips
those. Any new `deriving`, unit, family, class or instance feature in U56 will
land here first.

The reason this vein is rich is structural rather than accidental. Upstream's
desugarer manufactures definitions the author never wrote, they are registered
before any body is walked, and they are usually *unreachable* in the program
under test — so they are pruned before emission and leave no trace on the
wire. They are invisible to every instrument except the counters, and the
counters cannot say what caused them. That is exactly the gap the tooling
below is for.

**Effect rows.** Row ids are where order sensitivity bites hardest. Anything
U56 does to effect handling, scopes, or `with-timeout` shows there before it
shows anywhere else.

**The shapes we just ported are fresh and therefore fragile.** `punctual` and
its wcet budget on the def line, `unique-params`, `revised` as a
`__record-set` spine, unit families. These are new tests and new code at the
same time. If U56 tweaks any of them, we will not have the intuition yet.

**Real literals, issue 125.** Correct to 15 significant digits and wrong above
2^53. If U56 touches the literal path, we are the only thing that can tell
"fixed" from "moved".

## What would make the next Update cheaper

Three things, and all of them are affordable.

**Reaching the minimal reproducer in one move.** The technique that works is
already known: shrink the program until the delta is a line you can read. What
was missing was a way to get there without an hour of grep-and-correlate. It
turns out the checker walks definitions in file order and the counters only
grow, so truncating a chapter after definition *k* and differentiating
reconstructs the oracle's mint log at definition granularity — and bisecting
on the same fact localises a divergence in O(log N) probes. A 2.7 MB unit with
8,298 definitions and a fourteen-second oracle run came down to a two-line
reproducer in fourteen probes. That is forty lines of shell and no Rust, and
it should exist before the repin, not after.

The caveat has to travel with it: truncation is legitimate because both sides
see the same program, **not** because per-definition cost is stable under
truncation. Someone will eventually quote a row as evidence of what one
definition costs, and it is not that.

**Speed is an asset worth defending.** `irdump whole` reads the 3.44 MB
self-host in 2.6 seconds where the oracle takes 38. That is what makes running
the entire corpus both ways on every release a coffee break rather than a
project. Do not spend it.

**The lossless CST is an underused advantage.** Upstream throws trivia away;
we keep spans, formatting and exact provenance. Every question of the form
"where in the source did this come from" is one we can answer and they
structurally cannot. Nothing in the release protocol above uses that yet, and
something should.

## The one-line version

Bank a baseline; repin and change nothing; attribute every delta before
closing any of it; and never port from the new subject until after you have
measured against it.
