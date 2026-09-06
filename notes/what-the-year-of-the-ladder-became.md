# Four repos, one sentence each

Update 55 went out three days ago. Today it got stress-tested by four
independent things, and it held. That is worth saying plainly before anything
else, because it is the whole point of the exercise and it is easy to lose
under the day's fixes: **the compiler is in good shape, and we now have the
instruments to say so with evidence rather than confidence.**

Tomorrow Damian's agents get fourteen issues and ten pull requests from us. That
is the output. What follows is about the machine that produced it, because the
machine changed shape this cycle in a way I do not think anyone planned.

## The sentence test

Every repo we still work in can say what it is in one sentence:

- **rust-codex-compiler** — a completely independent implementation of the
  Codex front end.
- **codex-zig-transpiler** — Codex source in, Zig out, and the emitter emits
  the same bytes for its own source on two roads.
- **codex-wasm-transpiler** — the same claim, in WebAssembly.
- **safari-codex** — a real application in the language, with four arms holding
  it to one answer.
- **codex-qemu** — run Codex on real x86.
- **cobblestone-curated-tests** — twenty-eight programs that answer in under a
  minute.

`codex-zig-ladder` could not pass that test, and it is now deprecated. It was
the repo that started all of this and it earned its retirement rather than
failing into it: fourteen rungs, hundreds of findings, and a structural blind
spot it could never fix. **Both of its arms were Damian's front end.** Anything
wrong above the IR was invisible to it by construction, which is why finding 74
— Real literals off by one ULP — took an independent front end and not a
fifteenth rung.

The sentence test is not a style preference. A repo you can describe in a
sentence is a repo you can decide about. The ladder accumulated the QEMU
transport, the corpus resolver, the findings archive, the outbound queue and the
bank because there was nowhere else to put them, and once they were all in one
place, no one could say what any of it was for without a paragraph. The split
was not tidying. It was making the pieces decidable again.

## Inside out and outside in

The strategy that emerged — and I want to be honest that it emerged rather than
being designed — is that we test Cobblestone from two directions at once.

**From the outside in: Rust.** A second implementation that shares no code with
the first. It reads the same source and must reach the same answer, and when it
does not, exactly one of the two is wrong and neither gets to vote on which. A
year ago there was no Rust tooling here at all. Today it is a compiler, a linter
and an interpreter; it handles safari perfectly; and it can interpret the entire
Codex front end against real subjects — which is to say it runs Damian's
compiler, faithfully enough to produce byte-identical IR, as an interpreted
program. The check, scope and emit layers still have gaps. The structure does
not.

**From the inside out: the plugs.** The zig and wasm transpilers are written in
Codex and compiled by Codex, and each ends in a fixed point — the emitter
emitting the same bytes for its own source on two roads. That is a much
stronger claim than "the tests pass," because it is a claim the artifact makes
about itself, and it fails loudly when it stops being true.

The two directions catch different things, and neither could catch the other's.
A fixed point cannot tell you the front end typed something wrong, because both
roads go through the same front end. An independent implementation cannot tell
you the emitter is inconsistent with itself, because it never runs the emitter.
Having both is not redundancy. It is the only reason the coverage joins up.

**The Rust arm has no fixed point, and it should not pretend to.** What it has
instead is that it self-compiles in a sense: it interprets the compiler that
compiles it. That is a different kind of claim and a weaker one, and calling it
a fixed point would be borrowing credibility the artifact has not earned. It is
also *fast*, which turns out to matter more than the extra rigour would have.

## Speed is a correctness property

The thing I would most want to carry forward from this cycle: **turnaround is
not a convenience, it is part of whether the instrument works.**

Every repo we kept can do real work in under ten minutes. The curated set
answers in under a minute. Safari's cheap tiers are two minutes and its
expensive ones fifteen. The transpilers each check their fixed point in about
nine.

Contrast that with what the corpus sweep became: six hours, the whole box, and
a day of guessing in between answers. The week's worst mistakes all came from
that gap — a bisection run against contaminated rungs, a claim that the native
arm was flat when it was under its own noise floor, a cost measured on the wrong
workload. None of those were reasoning failures exactly. They were what
reasoning does when it cannot check itself often enough.

So we cut seventeen hundred corpus programs to twenty-eight. By coverage that is
a catastrophic loss. By *questions answered per day* it was the single most
valuable thing we did, because it converted "I think this is right" into "I
know, I just ran it" — and it did that for every subsequent change, compounding.

The trade has a real cost and it should be named: the twenty-eight were selected
for being easy to run, so they are a regression suite and not a conformance
suite. They tell us we have not broken what worked. They cannot tell us we are
right. The seventeen hundred can, and they are still there for the day we want
that answer badly enough to spend a day on it.

## Safari earned a role nobody assigned it

Safari began as a port of a Zig screensaver, for the narrow purpose of having a
non-trivial program to compile. The port finished months ago and the program has
not evolved since. By the original plan it should be finished and idle.

Instead it turned out to be the most demanding customer the toolchain has, and
for a reason that has nothing to do with driving or giraffes: **it is a
functional, immutable flavour of Codex, written at real scale, with four
independent arms held to one answer.** The zig plug, the compiler's own x86-64
emitter under QEMU, and two separate roads to WebAssembly all compile the same
source and must print the same bytes. The specs check fifty-four chapters three
ways. Between them they have found more toolchain defects than anything else in
this ecosystem.

That is a role no one designed. It came from the arms, not from the program, and
the arms are cheap to keep because the program stopped moving. A frozen subject
with four live arms is a better oracle than a moving subject with one.

The Night Walk — our first Codex written from scratch, from the position of
Damian's actual audience — is still unwritten. That is fine. It is a different
question and it will keep.

## Today's fix, and the shape of it

Today's actual defect is a good illustration of why the structure matters more
than any individual finding.

Safari's two transpiler pins pointed at private worktrees, created so that work
next door could not rebuild a transpiler underneath a running sweep. Reasonable
intent. What it bought was a **silently stale oracle**: both worktrees still
held binaries built from a commit two Updates old, while the language pin had
moved on. Every arm was grading today's source through yesterday's compiler and
reporting green.

Note what did *not* catch it. Not the sweep — it passed. Not the specs — they
passed. Not the fixed points — they held, because a fixed point is a claim about
internal consistency and a stale binary is perfectly self-consistent. What
caught it was regenerating a tracked artifact and noticing that the emitted Zig
had changed from wrapping arithmetic to trapping, which is an Update 55 feature
that should have been there all along.

The lesson is not "check your pins." It is that **a pin which drifts without
complaining is worse than one that moves**, and the protection people think they
get from freezing a dependency is usually being provided by something else
entirely — here, the fingerprint check and the per-run provenance, both of which
survived pointing the pins at the live trees.

My first attempt at fixing it was to pass the right paths on my own command
line. That made my runs correct and left the pins wrong for everyone else, which
is not a fix; it is a fix-shaped thing that makes the problem harder to see next
time. Steve caught it. The correction is in the repo now, and the rationale went
into the file rather than into a commit message nobody will read again.

## What is left

The Rust arm should reach typed IR on all twenty-eight curated programs. It is
at nineteen. Eight are named gaps — `FieldAssign`, `NumLit`, if-branch
unification, `Lambda` — each an afternoon rather than a mystery. The last one is
`negation-abutment`, and it differs for an interesting reason: **upstream
inlines a definition at a call site whose arguments are all literals**, one
level deep, then prunes what that orphans. We do not have that pass. We found it
by diffing rather than by reading, which is the entire argument for having a
second implementation — nobody told us there was an inliner.

Matching it means mimicking someone else's optimiser exactly, which is real work
for one program's worth of agreement. But twenty-eight of twenty-eight is a
different kind of statement than twenty-seven, and the curated set exists
precisely so that going after the last one is cheap to try.
