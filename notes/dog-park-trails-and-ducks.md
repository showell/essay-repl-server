# Dog Park: trails, ducks, and an ecosystem in layers

*2026-10-14, late. Eleven rounds with cold agents on poop and chickens,
after "the poop and chickens are still way too much of an obstacle".
Nothing is built yet; dog-park `main` is still `cc3af66` (decision 28).*

## Where the rounds landed

The result is a design built in **three layers**, each one played before
the next:
- **Layer 1 (the next build): trails without obstruction.** It adds no new
  state at all.
- **Layer 2: eggs and ducklings.** Ducks lay after eating, and eggs hatch
  into ducklings that follow their mother in a line.
- **Layer 3: equilibrium.** Hungry ducks leave, founder ducks stay, and
  the flock grows where you herd and thins where you don't.

**Chickens become ducks**, in one mechanical commit before layer 1
(sprites, code, docs, and the `chicken N` lines on the wire). The agent's
reason: each layer 1 line written about chickens would be one more thing
to rename later.

## Layer 1, the spec

**The trail.**
1. **When:** the herd poops once each time the leashed dog's walk passes
   another 700 px, after that pixel-tick's walk.
2. **Who:** the deepest dog of the leashed dog's breed in that walk.
   - The leashed dog has depth 0.
   - A visited dog whose anchor is dog j has depth j's depth + 1. The
     anchor is the one `wishOf` already picks.
   - The greatest depth wins; ties go to the dog visited later.
   - If no dog follows, the leashed dog poops.
   - Depth lives only for that one walk; nothing is stored.
3. **Where:** 30 px *behind* the pooper.
   - "Behind" means away from its anchor. For the leashed dog, it is the
     reverse of its step.
   - If that spot is taken, the search moves out in 4 px rings to 200 px.
   - A spot must be clear of critters and poop, and of the edge of the
     region the physics sees.
   - If nothing fits, there is no poop.

**Going around things.**

4. **Poop blocks dogs and cows.** Nothing pushes poop.
5. **The sidestep.** A step blocked by a poop, or by a duck that can't be
   shoved, is retried once:
   - Zero the step on the axis where the blocker is farther away (a tie
     zeroes x).
   - On the other axis, keep the step's own part. If that part is zero,
     step its full size away from the blocker (a tie steps +).
6. **The shove.** A dog or cow stepping into a duck knocks it:
   - the duck moves by the same step, plus the same amount sideways, away
     from the mover's centre line;
   - this counts only if the duck lands clear of everything: critters,
     poop and the edge;
   - otherwise the step is blocked, then sidestepped.

   So a duck slides off the front of a dog within about 30 px instead of
   being plowed ahead.
7. **The leashed dog.**
   - If a poop stops it, it slides 1 px sideways.
   - If a duck stops it, it shoves the duck. If the shove fails, it slides
     1 px sideways.
   - It bumps only when the slide fails too.
   - The 6 px setback goes.

**Ducks.**

8. **Ducks leave the walk.** They no longer take any of the 40 slots.
9. **Once per tick,** after the drag, and only if the leashed dog moved,
   every duck the physics sees takes a turn in number order. Each steps at
   most half the leashed dog's net move, and at most 8 px:
   - **forage:** toward the nearest *ripe* poop within 500 px, with the
     sidestep;
   - **otherwise go home:** toward its layout spot if more than 32 px away
     (blocked: it just waits);
   - **otherwise stay put.** A resting duck writes no line, so the report
     stays small.
10. **Eating.** A duck eats every ripe poop it overlaps.
11. **Ripe.** Every poop is ripe except the newest. Ripeness comes free
    from the slot counter and needs no new field. The newest poop also
    blocks ducks.

**Constants:**
- poop every 700 px, 30 px behind, rings 4 px apart out to 200 px;
- duck sight 500 px; a duck's step at most min(half the net move, 8 px);
- home deadband 32 px.

## Layers 2 and 3, in a sentence each

- **Layer 2:** a fixed pool of 200 duck slots, half of them unborn.
  - A duck lays an egg after 3 meals.
  - An egg hatches 2000 px of dragging later, if its tile has fewer than
    4 ducks; otherwise it vanishes at 6000 px.
  - A duckling follows its mother for 3000 px, using the dogs' follow
    rule scaled down to 20-40 px.

  This needs a park-wide drag odometer, egg slots, and a meal count and
  mother per duck.
- **Layer 3:** a hatched duck that goes 10000 px of nearby dragging
  without a meal leaves, and its slot goes back to unborn. The 100 founder
  ducks never starve. The equilibrium:
  - the founders, plus roughly a dozen ducks along the trails you herd;
  - capped at 4 a tile and 200 overall;
  - falling back to the founders where you stop herding.

## How we got here

**Rounds 1-4: obstruction.**
- Poop blocked the followers walking in the leader's track.
- Chickens used up walk slots.
- Every bump ended your drag.

The fixes that stuck:
- **the trail comes from the tail of the herd**, not the leashed dog;
- **chickens leave the walk**;
- **things in the way are gone around**, not stopped at.

One idea died in testing: **chickens fleeing dogs.** In round 4's
scenarios they formed a bow wave ahead of the leashed dog, which made them
the main event.

**Rounds 5-7: the ecosystem**, after you said the game is about
equilibrium.
- **Loops that settle:** lay after meals, leave when hungry, founders that
  never starve.
- **Conservation:** one "nutrient" flowing between grass, poop, chickens
  and eggs.
- **Per-tile grass and pasture rotation:** cows strip a tile bare, so you
  move the herd on; a green park is the score.
- **Game of Life neighbour counts were cut.** Chickens blinking in and
  out for no reason you can see is noise. What survives of Life is
  "chickens spread toward empty tiles".

**Round 8: a fresh skeptical reviewer.** It found:
- **The report budget:** chickens moving every pixel would write about
  2 KB of lines a tick and freeze the page in about 24 ticks. Hence one
  duck turn per tick, and resting ducks write nothing.
- **Free ripeness** from the slot counter.
- **Flutter is a jump,** which an earlier decision forbids. Hence the
  shove.
- **Eggs change the population,** which the code fixes at compile time.
  Hence the fixed pool with unborn slots.

Two of its points ran against your calls (poop blocking nobody, and
protocol worries you'd waved off), and the design agent overruled them.

**Rounds 9-11: practical.** A second fresh reviewer read layer 1 against
the code and found two real bugs, both now in the spec:
- **A deep follower could poop outside the region the physics sees.**
- **Chickens could end up standing on unripe poop.** That would trip the
  server's no-overlap check.

## Open questions for you

- **The rename:** ducks everywhere, now, as one commit before layer 1?
- **Grass and pasture rotation** (layers 5-6 in round 7's ladder) are
  parked, not cut. They're the most interesting game in the rounds, and
  the most state.
- **Open ground:** founder ducks live only in the park's blue tiles. Trails
  far out on open ground get eaten only by a duck within 500 px. Layer 2's
  "hatch where you ate" would spread ducks there over time.
- **Cost:** every blocked step still scans every poop in view. The agent
  says measure first (a 100 px drag with 500 poops in view), then bucket
  poops by tile if it's slow.

## What to watch in the first eye test

- **Crossing a trail:** does a chain lag or fray where it crosses its own
  trail (up to 26 px of sidestep per poop)?
- **Shoving ducks:** do ducks slide aside naturally, or look plowed?
- **Trail life:** do trails stay visible for a while and then get cleaned?
  The knobs are poop every 700 px, ripe when not the newest, and the
  ducks' 8 px step.
