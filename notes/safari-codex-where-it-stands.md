# Safari-codex: where it stands, and the two ways forward

*2026-08-30, written at the second parking. The project is a port of the driving
screensaver from Zig to Codex — 26 chapters, 5,701 lines of port, 3,098 lines of
checks, 17 graded seams, 50 commits. It runs in a browser. The essay is about what
that does and does not prove, and about the two things worth doing next, which
happen not to collide.*

## The deliverable, stated plainly

A 728 KB wasm module, computed entirely in Codex, driving the driving game's **own
unmodified `blitter.js`** — symlinked rather than copied, fetching the same
absolute `/driving/safari.wasm` path the real game fetches. The road, its corners,
the conifers, the intersection towers, the guard rails, the pond, eight species of
animal, a cat that crosses and leaps, a truck that brakes into corners and lights
the road at dusk. 2,430 draw commands in the opening frame.

**It looks like the game.** That is the claim, and it is the one that was in doubt
when this started: not whether Codex could compute geometry, but whether a real
interactive program — one somebody would actually watch — could be carried across
and still be the same thing at the far end.

Every file in `games/driving/wasm` has a chapter. Twenty game files, twenty-six
chapters — the difference is where the port found structure the original had left
implicit, and split it.

## What "by eye" is worth, and what stands behind it

The eye test is the deliverable and it is also the weakest possible evidence, which
is why almost all the work went into the other kind.

Seventeen checks in `judge/`, each grading a seam where the game computes something
a probe can read. The probes `@import` the **real, unmodified** game module, so the
hand-written Zig is the oracle and never a copy of it. The whole sweep is 6.5
seconds warm, ninety seconds cold, and it prints GREEN or RED.

Behind that, three arms — the game, the port through the zig plug, and the same
Codex source through the Codex compiler's own x86-64 emitter as a kernel image
under QEMU. All seventeen checks agree on bare metal. The five spike entries agree
**bit for bit** on 523,414 IEEE-754 patterns, which became possible only this week,
when the plug learned `real-to-bits` and coordinates stopped going out as scaled
decimals.

I wrote about the limits of that apparatus separately — [the three arms of
safari](the-three-arms-of-safari.md) — and the short version is that redundancy is
blind to everything upstream of where the paths fork, which this project proved the
hard way by finding a defect both arms shared.

## What was actually hard, which was not the graphics

Almost nothing difficult was about drawing. The interesting difficulties were three.

**The toolchain had holes exactly where a real program leans on it.** Codex `Real`
had no conversion to Integer at all when this started, so the port could not report
a computed number, let alone round one. Filling that took two emitter rows; the
bitcasts took two more. Both were declared in the language and tested in its own
test suite, and simply had no zig emitter — a shape you only discover by writing a
program big enough to need them.

**Calibrating a tolerance is a research task, not a constant.** The port computes
in f64 where the game computes in f32, so every value differs somewhere in the last
bits, and every gate had to be measured rather than chosen. The loosest is 8e-5
relative, and it is set by a single vertex: a tree trunk projected 270,939 pixels
off the side of a 960-pixel canvas, where the perspective divide multiplies a
micron of depth disagreement by five million.

**Some differences are the port being right.** The depth sort is the sharpest case.
`render.zig` insertion-sorts a mutable array; carried literally onto persistent
Codex lists that goes cubic in allocations and exhausts four gigabytes. A stable
merge sort produces the identical order — and *stable* is load-bearing, because two
depths closer than an f32 ulp are the same number to the game and orderable to the
port. A rail post and a rail bar swapped places in a 3,091-command stream before
that was understood, and no per-module check could see it, because both modules
were right.

## The honest limits

**The port will never be bit-identical to the game**, and this week that stopped
being an assumption and became a measurement. The whole ride finishes in 6,960
frames where the game takes 7,000. Running the game's own f32 code against itself:
a one-ulp perturbation at the start is absorbed completely, a persistent relative
bias does nothing at 1e-8 — and at 1e-7, which is f32's own resolution, the total
swings to 7,061 or 6,971. **The ride's length is not a property of the model; it is
a property of evaluating the model in f32.** The port sits inside the family the
game produces for itself.

**The driven page is off every arm.** The checks grade seams and the spike entries
grade stills at fixed route positions. `DriveMain`'s frame loop and its wasm shim
have no witness at all, because that program's output is a wasm module rather than
a line of text. It is the largest uncovered surface left and the fix is known
rather than novel.

**The whole-frame check grades two states.** Chosen as branches — a hard lean, and
a long straight with the truck close.

## Next, (a): put it on a GPU

The seam is already cut, and it was cut for other reasons.

`NOTES` §5 decided at the outset that the blitter and the rasterizer stay on the
far side — the port computes a **draw-command buffer** and hands it over, and
everything downstream of that is somebody else's problem. That decision was made to
bound the work. It happens to be exactly the boundary a GPU backend wants.

The buffer is a flat, typed, per-frame list: a tag, a colour, a strength, a point
count, then coordinates, with the gradient tags trailing a second colour and their
own geometry. It is already the thing the whole-frame check grades command for
command, and already the thing the third arm compares bit for bit. **Nothing in
`port/` should have to change** — the buffer is the API, and a shader consuming it
is no more exotic than a Canvas 2D context consuming it.

What needs deciding is how much of the blitter's own shading maths moves across.
There are four gradient forms in play: the horizontal round gradient that gives
cones and trunks their volume, the bull's two-stop linear and radial gradients, and
the truck's headlight radial with alpha in both stops. `harness/spike_svg.py`
already reimplements three of them approximately and says in its own header exactly
where it is not faithful — "if a spike and the browser disagree about a colour,
believe the browser" — which makes it a decent map of the territory and a bad
specification.

The other question is whether a GPU path wants the buffer at all, or wants the
scene one level up. The buffer is already flattened and depth-sorted on the CPU;
a GPU could take the depth sort itself. That is a real design choice and not one to
make from here.

## Next, (b): send the findings

Eight, written up, none sent. They came out of *ordinary use* — writing a program,
not hunting for defects — which is the only reason they are interesting.

Two are silent wrong answers, which is the worst category a toolchain has. A
declared trapping multiply is emitted as a wrapping one, so `4000000000 *
4000000000` returns a plausible negative number with exit status 0. And a `Real`
literal wider than an i64 is read as a *different number*: written out longhand,
`1e18` arrives as `-8.4467e17`, silently. That second one is the front end rather
than any plug — both arms print the same wrong constant, and the value reaches the
emitter as a bit pattern with the digits nowhere in the file — and it was found
because it corrupted **our own oracle**, making a check red at a value the port had
computed correctly.

One is a test that cannot fail. `Math chapter Cordic` documents ~0.1% accuracy and
delivers 0.45%, and its entire test is

    Chapter: FwdCordicTest
      cites Math chapter Cordic

    Section: Entry
      opening : [Console] Nothing = act
        print-line-uni "Math/Cordic OK"
      end

It cites the chapter and prints a string. It passes whether or not Cordic works.

`FINDINGS.md` now opens with how each of the eight should travel, because the
routing is the part that is easy to get wrong: two are small mechanical PRs, one is
an *offer* rather than a defect (there is no Real arc tangent anywhere in the
foreword's thirteen directories, and ours is measured to 1e-9), two are issues
rather than patches because the fix is a policy call we should not make from
outside, two want investigating first, and two belong to angry-gopher — one of
which is a one-line buffer fix already on a live path.

## Why the two parallelise

They do not touch the same things. (a) lives in `web/` and downstream of the
draw-command buffer; it needs no Cobblestone change and no `port/` change. (b)
lives in Cobblestone and angry-gopher and needs no browser at all.

They also fail differently, which matters more. The GPU work is exploratory —
nobody knows yet how much of the blitter moves — so it will spend time in states
that do not render. The findings work is finite and well-specified: eight items,
each with a repro, and the queue empties. Running an open-ended task beside a
bounded one is a better use of two attentions than either alone.

## What the project turned out to be about

It was proposed as a port and it has been, mostly, a study of how you *know* a port
is right — and of how much of that knowledge has to be measured rather than
reasoned.

The pattern recurred so often it stopped being surprising. A tolerance that seemed
principled was 17× out until someone computed `r^13/13!`. A chapter's docstring
said the foreword had no join and the foreword had a join. Entries were split twice
to fit a heap that was never the constraint — the printers were allocating a
quadratic amount, and an allocator that never frees is very good at hiding an
algorithmic mistake behind itself. A claim that two compilers agreeing on a
knife-edge computation proved something deep turned out to be wrong by eight orders
of magnitude, and the data refuting it was already in the same file.

Every one of those was found by running something rather than by reading it. The
port passes the eye test, and the eye test is the deliverable — but the reason to
believe it is that seventeen checks, three arms and 523,414 exact values were
willing to say otherwise and did not.

---

*`~/showell_repos/safari-codex`, pushed to `showell/safari-codex`. `README.md`
orients and its "Where to pick this up" is written for a cold start;
`PORTING_NOTES.txt` is sixty-one numbered notes; `FINDINGS.md` is the eight and
their routing; `PLUG_WORK.md` is the emitter work and its lineage.*
