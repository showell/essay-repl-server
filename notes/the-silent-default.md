# The silent default

*2026-09-02. Four hours into Update 54, six defects, and all of them the same shape.*

---

## A vocabulary, once

Four words, because the rest of this leans on them.

The compiler allocates memory in two ways. A **deck** is scratch space a phase
takes, scribbles in, and hands back whole when it finishes — cheap, because
nothing is freed individually. The **bivy** is ordinary allocation that is
never handed back. An **extent** is the stretch of code during which
allocations go to the deck rather than the bivy; the compiler marks one by
wrapping a call in `deck-record`.

And a **harness** is our stand-in for the compiler's own driver — the ladder
compiles small programs by calling the compiler's phases directly, rather than
by running `opening.codex`, because we need the intermediate values that the
real driver throws away.

That's the whole glossary. The story is not really about memory.

## What actually happened

Six things broke today. Here they are with the vocabulary stripped out:

1. A function had a rule about how it must be called. Nothing said so at the
   function. We called it wrong.
2. A shared helper had been fixed in one place and not in the other place that
   did the same job by hand.
3. A file we bundle grew a new dependency in Update 54 on a file we don't
   bundle.
4. Turning on a safety check for the first time revealed we were missing two
   of the things it checks for.
5. A gate whose whole job is to stop a crash-dump being saved as a correct
   answer had never once run. Not "was wrong sometimes" — had never run, in
   its entire life.
6. Two modules each had a self-test that proved their gates worked. Nothing
   ran either self-test.

Only one of those is a *bug* in the ordinary sense. The rest are absences.

## The shape

Every one of them shares a property, and it took me most of the day to see it
as one thing rather than six.

**When the precondition was missing, the mechanism picked a plausible default
instead of refusing.**

- The deck marker, in a program that didn't carry the memory chapter, compiled
  down to a four-byte "do nothing" — a legal, sensible default. The program
  ran. It just quietly stopped reclaiming memory.
- The safety check on memory overrun was, in our harnesses, *unarmed* — because
  arming it requires a reservation, and we had never made one. The check was
  present in the source, compiled into the binary, and could not fire.
- The crash-dump gate looked for the file at the wrong path, failed to open it,
  and reported "no crash found". Not an error — a clean bill of health, from a
  file it never read.
- The capture code that reads a program's output treated a network error and a
  timeout exactly like the program finishing normally. A truncated answer came
  back looking like a complete one.
- Twelve provenance files were tracked in git while every run rewrote them, so
  "the tree is clean" stopped meaning anything.

In each case the honest behaviour was available and cheap: *say you couldn't
do the thing*. In each case the code instead produced the most reasonable
output it could and said nothing. And "the most reasonable output it could" is
exactly what makes these expensive — a refusal costs you a minute, a plausible
wrong answer costs you a morning.

## Why the bill landed on this Update

Every Update moves things and we pay a tax. This one was worse, and I think
the reason is specific rather than bad luck.

**Update 54 changed the memory discipline itself** — the one subsystem our
harness *reimplements* rather than calls. The lexer started reclaiming memory
after every token. The type-checker gained a hand-written pair of
enter/exit-the-extent calls. Two phase functions gained arguments. All of that
is invisible to anyone who just runs the compiler, and all of it is load-bearing
for anyone who stands in for its driver.

So the harness didn't rot faster than usual. The thing it stands in for moved
underneath it, in the exact place where standing in for something is hardest.

## The mechanism that made it slow

There's a second-order effect worth naming, because it's what actually burned
the hours.

The bug was in the type-checker call. It surfaced in the *lowering* rung — a
different phase, later, after a few hundred megabytes of unrelated work. The
checker itself was green and printed correct output; it had quietly written its
results somewhere that got reused, and the damage only appeared when something
read them back.

**The step that fails is not the step that is wrong.** It's the first step
that *reads* what the wrong step left behind. And our instinct — mine, and the
morning's written record — was to debug the step that failed. Yesterday's notes
said "it dies inside lowering," and it didn't; lowering had finished before the
first line of output was printed. That single misreading cost the most.

The thing that finally cracked it wasn't cleverness, it was reading the
compiler's own source until I could say why a register held a particular
garbage value. Two of my three hypotheses were wrong, and both would have
looked plausible in a summary.

## The thesis I want to sharpen

There's a question sitting in `HARNESS_FIDELITY.md` that I opened this morning
and couldn't answer: **why is there a harness at all?**

Today is the strongest evidence yet, and it points one way. Of the six defects,
**zero were bugs in our own logic.** Not one. Every single one was a place
where our stand-in had drifted from what the real driver does — a missing
wrapper, a stale argument list, a reservation not taken, a chapter not bundled.
We are not bad at writing harnesses. We are being asked to maintain a hand copy
of a thing that changes every Update, and the copy is where all our bugs live.

The honest counter-case, which I don't want to wave away:

- The harness exists because a rung needs the *intermediate* values — the token
  list, the parse tree, the type table — and the real driver returns only its
  final artifact. That reason is real.
- A rung deliberately bundles a *slice* of the compiler, and the driver assumes
  the whole thing. Also real.
- The harness must be deterministic, and the driver has a clock in it. Real,
  and already worked around.

None of those requires us to *re-type the driver's setup*. They require us to
open the phases up and see inside them. Those are different things, and today
we paid for treating them as the same thing.

**So the sharpened version:** the harness should not be a reimplementation of
the driver with the phase calls copied out. It should be the driver's own
sequence with the phase calls *instrumented*. Concretely — one shared piece of
generated setup, derived from `opening.codex` rather than transcribed from it,
that every rung includes and no rung edits. Then an Update that moves a
reservation moves it in one place instead of twelve, and the checklist I wrote
this morning gets shorter instead of longer.

I don't think that's a day's work, and I don't think we should do it now. But
it's the first time I can argue for it from evidence rather than from taste.

## On four hours

You said it's frustrating that we're four hours in. It is. I want to be
straight about what the four hours bought, because I don't think it was four
hours of spinning.

We found one real thing in *their* compiler worth reporting — a function whose
calling rule exists only in prose, plus three cousins — and it's filed. We
found five places where *our* side had drifted from Update 54 and fixed all
five. And we found that two of our safety nets had never been load-bearing:
the gate that stops a crash-dump becoming a banked answer, and the self-tests
that were supposed to prove such gates work.

That last one is the part I'd have been most unhappy to keep. A gate that has
never fired and a gate that *cannot* fire look identical from the outside,
forever, until the day you actually need it. We were one bad run away from
banking a register dump as the correct output of a compiler phase, and then
diffing against it for an Update or two while it made every arm look broken.

The tax is real, though, and it's worth saying what it's a tax *on*. It's the
cost of maintaining a copy. Six defects, six divergences, one copy. That's not
a coincidence and it's the argument above.

## Where it stands

Ten of twelve rungs bank clean at Update 54. The eleventh trips the memory
guard during code emission, and I've been wrong about it twice, so the next
move is to instrument rather than guess a third time: print where the memory
cursor and the ceiling actually are, on either side of the step that fails,
and read the numbers instead of reasoning about them.

That's one guest, and it's the right kind of cheap.
