# The three arms of safari

*2026-08-30, written after Seam 4 closed and one of its claims was retracted the
same afternoon. Safari is the port of the driving screensaver from Zig to Codex;
it is verified by running the same question three ways and requiring the answers
to match. The essay is about what each of those three ways is actually a witness
to, and — more usefully — what each of them structurally cannot see.*

## The three arms, named

| arm | what it is | what it costs |
|---|---|---|
| **the game** | `probe/probe_*.zig` imports the real, unmodified `wasm/*.zig` and prints what it computed | a second |
| **the plug** | the Codex port through `codexzig` → zig → a native binary | 5.7 s for all 17 checks |
| **the metal** | the *same* Codex source through the Codex compiler's own x86-64 emitter, as a kernel image under QEMU | 3 m 26 s, two guests per check |

The first two compare a *port* against a *game*. The second and third compare a
*program* against *itself*, compiled two ways — Diverse Double Compiling in
Wheeler's sense, applied to a program instead of to a compiler.

Those are two entirely different questions wearing the same clothes, and most of
what follows comes from taking the difference seriously.

## What each arm is a witness to

The game arm is the only one with any claim on *what the answer should be*. It is
an oracle in the strict sense: it does not check the port, it *emits* the truth
and lets something else compare. Its authority comes from one design decision that
is easy to state and was not free — the probe imports the real module rather than
restating it. A copy can drift; an import cannot. Every temptation to "just copy
the constant over" is a temptation to build a second oracle that can disagree with
the first, silently, in the direction that makes the test pass.

The plug arm is a witness to the *port* — did the Codex say the same thing the Zig
said. This is the arm that does the work, and it is the arm that gets run
constantly, because it is cheap. Cost is not a detail here; it determines cadence,
and cadence determines whether a check is a habit or a ceremony.

The metal arm is a witness to *the plug*. It cannot tell you the port is right —
it runs the same source, so if the port is wrong both arms are wrong together and
agree beautifully. What it can tell you is that the answer the plug produced is
not an artefact of the plug. That is a narrow claim and it is worth having,
because the plug is the newest and least exercised thing in the stack.

## The shared front end, which is the structural limit

Here is where the three-arm picture is more flattering than the truth.

The plug arm and the metal arm are not independent. They share a source file, which
is intended. They also share a **front end**, which is easy to forget until it
bites — the same lexer, the same parser, the same constant folder. Only the back
ends differ.

Today that stopped being theoretical. A `Real` literal whose digits do not fit an
i64 is read as a different number: written out longhand, `1e18` arrives as
`-8.4467e17`, with exit status 0 and no diagnostic anywhere. The two arms print
*the same wrong constant*, byte for byte. And the emitted zig says why on its face
— the literal arrives as

    @as(f64, @bitCast(@as(i64, -4349576520114425037)))

with the digits nowhere in the file. The value was folded before either emitter saw
it, so no back end could have got it right and no comparison of back ends can see
it wrong.

This is the same shape as the ladder's finding 42 next door, where the zig plug's
self-tail loop read a top-level definition where the source read its own parameter
— a silent wrong answer both arms would have shared. The lesson generalises past
either project: **a redundancy check is blind to everything upstream of the point
where the paths diverge.** Two arms that fork after the front end test the back
ends and nothing else. If you want the front end checked you need an arm that
forks earlier, and there is no such arm here.

That is not a reason to stop running the metal arm. It is a reason to say what it
covers when reporting a green.

## An arm sees only what the seam prints

The second limit is subtler and I did not appreciate it properly until this
afternoon.

An arm does not compare computations. It compares *text*. Whatever the seam prints
is the entire bandwidth of the comparison, and everything finer than the last digit
printed is invisible by construction.

The checks in `judge/` print verdicts: `Grade` emits `name ok 2468`. Two arms that
both land inside a tolerance produce the identical string whatever their last bits
did. Seventeen checks agreeing "byte for byte" therefore means seventeen *verdicts*
agreeing, which is a much weaker statement than it sounds — and it is why the
`--entry` mode exists, running a poc entry chapter instead of a check so that every
coordinate of every frame goes out as a scaled integer. 523,414 values across eight
viewpoints, and the two arms produce all of them identically.

But the *scale* of that integer is the resolution of the comparison, and the scale
was chosen for a completely different reason. These entries were written to feed
`spike_svg.py`, which draws pictures at 960 by 600, so hundredths of a pixel was
already absurd overkill and the note in the chapter said so. Then the same entries
were pointed at the metal arm, where the number is not drawn but compared — and at
a hundredth of a pixel, two emitters could disagree by four orders of magnitude and
the comparison would call them equal.

Nobody decided that. It was inherited from a decision made for a drawing.

Today the scale went to millionths, which costs four digits a number and buys four
orders of agreement. It still does not reach an f64 ulp — at the far vertex the
port projects, 270,939 pixels off the side of the canvas, an ulp is 1.5e-11 — and
reaching that needs `real-to-bits`, which no plug emits. So the honest statement
about the metal arm's resolution has a number in it, and the number is not
"exact".

**The general rule worth keeping: when a value is printed for one purpose and later
compared for another, the resolution of the comparison is whatever the first
purpose happened to need.** Go and look at it, because nothing will tell you.

## Sensitivity is not resolution

This one I got wrong in writing, in a commit, and had to retract, which is the
reason it is in the essay rather than in a footnote.

Seam 4 — the whole ride, checked by invariants — reports that the port's ride
finishes in 6,960 frames where the game's takes 7,000. The two arms both produce
6,960, and both produce the same worst segment and the same final gap of 68,700 mm.

The ride is *demonstrably* a knife edge. A persistent relative bias of 1e-7 — f32's
own resolution — moves the total to 7,061 or 6,971 and moves one segment from 305
frames to 267. So it felt obvious that agreement on all three numbers meant the two
emitters agree to something far finer than f32 epsilon, over 6,960 frames of
feedback carrying a twelve-iteration binary search and a sine and a cosine per
frame. I wrote that one differing bit anywhere in that chain would very likely have
moved the count.

That was wrong by about eight orders of magnitude, and the data refuting it was
already in the same file. The sensitivity experiment also measured that a
**one-time** perturbation of 1e-7 is absorbed completely — same 7,000 frames, never
a centimetre apart over seven kilometres — and that a **persistent** bias does
nothing whatever at 1e-8. Two IEEE f64 emitters differ, if they differ at all, at
about 1e-16 an operation. Across 83,520 lean comparisons, a separation that small
gives a flip probability somewhere around 1e-10.

So the ride is blind to FMA contraction, to x87 excess precision, and to a
reassociated sum — the three faults a DDC check most wants to catch, all of which
live at 1e-16.

The error has a clean name. **A system's sensitivity is a property of the system;
a test's resolution is a property of the test.** They are measured in the same
units, which is exactly why they get confused. This ride's knife edge is calibrated
to f32 epsilon because f32 is what the *game* computes in — it is a detector tuned
precisely to the port-against-game gap, and it says nothing about the
arm-against-arm one. Reaching for "this computation is chaotic, so agreeing on it
means a lot" skips the step where you ask *chaotic with respect to what size of
perturbation*.

There is a second, cheaper lesson buried in the same run. `ride-result` depends on
no input at all — the world, the initial state and the accumulator are constants —
so an eager constant folder could legally have evaluated all 6,960 frames at compile
time and left the guest printing numbers the emitted x86 never ran. The seed's own
pipeline line says `fold-constants` is on. What rules it out is nine seconds of
guest time against one second native. **An instant agreement would have deserved
suspicion rather than a commit message**, and I would not have thought to check if
the run had been fast.

## The oracle is not an arm, and it has no redundancy at all

There is a fourth path that the three-arm framing quietly omits, and it is the one
that actually lied today.

The gold files are the oracle's transport: `gen_gold.py` runs a probe, reads
`<kind> <name> <values...>` lines, and writes them out as a Codex chapter of
literals. Every check reads gold. **No arm checks the gold**, because both arms read
the same gold, and a wrong number there looks exactly like a disagreement in the
port.

`NumCheck` went red on `n-pow2` at index 8. The port had computed 2^60 correctly by
repeated doubling. The gold carried it as a nineteen-digit decimal literal, and
nineteen digits is where the front-end defect above starts. The oracle was wrong and
the port was right, and every instinct in the room said the opposite.

The fix is the boring one and it is the right one: `gen_gold.py` now refuses to
write a value it cannot carry. Fail loud is the floor. But the general point stands
— **every verification scheme has some component with no redundancy, and it is
usually the one nobody thinks of as part of the computation.** Here it is a text
file full of literals that gets regenerated so routinely that it had become
furniture.

## Cost, cadence, and hygiene

Arms have running costs and the costs decide how they get used. The plug arm is 5.7
seconds, so it runs on every edit and its failures are found within a minute of
being created. The metal arm is two QEMU guests per check, three and a half minutes
for the set, so it runs when a chapter changes shape. That is the right split, but
it has a consequence: **the cheap arm is the one whose silences you learn to
trust**, and trust is what stops you looking.

There is a hygiene failure mode specific to multi-arm setups, and this project had
one until this afternoon. `metal.py` obtained the zig arm's answer by running
`build/<mod>` — but only rebuilt it when the binary was *missing*, never when it was
*stale*. So an edited check was compared as fresh source on bare metal against an
old binary on the plug side, and the two arms would then disagree for a reason that
has nothing to do with either emitter. That direction of failure is the safe one —
it reports a defect where there is none rather than the reverse — but it is the
expensive one to debug, because the output looks exactly like the discovery the
whole apparatus exists to make.

And the counterpart to all of this: a check whose gates never fire is not a check.
`RideCheck` reports eight invariants that all read `-1`, which is precisely what a
completely inert check would also report. It took two deliberate mutations to
establish otherwise — tightening the speed ceiling from 8.0 to 0.5 reports a
violation at frame 20, an impossible gaze bound reports one at frame 0, and both
turn the sweep red. The `-1`s are earned. Nothing about reading the source would
have told me that as convincingly as breaking it did.

## What three arms do not buy

Worth stating plainly, because the apparatus is impressive enough to be mistaken
for more than it is.

Three arms cannot tell you the game is *right*. They compare a port to a game and a
program to itself. If `render.zig` draws the road wrong, all three arms agree
enthusiastically. The only checks on that are the ones that come from somewhere
else entirely — the invariant list Seam 4 uses is ported from the TypeScript's own
`test_model.ts`, and it is the single place in this project where a *fourth*
authorship stream gets a vote. That is worth more than its size suggests, and it
is the direction with the most room left in it.

Nor does agreement mean equivalence. It means agreement on the sampled inputs, at
the printed resolution, on the paths the arms do not share. Every one of those
three qualifiers has been the interesting one at least once today.

## Open questions

- **`real-to-bits` is one plug row away**, and it is the same shape as the
  `real-to-int` / `real-from-int` rows this port already filled. With it, the metal
  arm's comparison could go to the last bit and become a genuine test for FMA
  contraction and excess precision. Without it, "the arms agree" has a resolution
  and the resolution is not exact.
- **Nothing forks before the front end.** Is there an arm that would? The C# plug
  shares it too. A second *implementation* of the front end is not a thing that
  exists — but a differential test of the literal parser against a known-good
  decimal reader is small, and would have caught today's defect the day it was
  written.
- **The driven page is still off every arm.** The spike entries are stills at fixed
  route positions, so the frame loop and the wasm shim have no witness at all. This
  is the largest uncovered surface left and it is uncovered for a boring reason:
  its output is a wasm module rather than a line of text.
- **How much of the invariant list should come from outside?** `test_model.ts`
  turned out to be the most valuable single import in the project, because it was
  written by someone who was not thinking about this port. The general form of the
  question — where do you get a specification that your implementation did not
  author — does not have a good answer here yet.

---

*Everything above is checkable in `~/showell_repos/safari-codex`: `README.md`
orients, `PORTING_NOTES.txt` C16 and D11 carry the arm and sensitivity work,
`FINDINGS.md` item 6 is the literal defect, and `probe/probe_sens.zig` is the
experiment the retraction rests on.*
