# Dog Park: the day the dog herded the cows

*2026-10-14, at dog-park `1b9a26e`, written before a compaction and the
next step (cows herding among themselves).*

## What you did in your last game

You played one long session on :9103: 5,619 ticks, 1,521 of them with
a drag, and dog 344 was the last on the leash. At the end, seven cows
stood within about 225 px of it:

| cow | started at (px) | ended at (px) | travelled (larger axis) |
|---|---|---|---|
| 26 | 15250, 16250 | 14988, 16594 | 344 px |
| 31 | 14750, 16750 | 14927, 16609 | 177 px |
| 16 | 15250, 15250 | 14915, 16443 | 1,193 px |
| 21 | 14750, 15750 | 14987, 16393 | 643 px |
| 22 | 15750, 15750 | 14866, 16532 | 884 px |
| 32 | 15750, 16750 | 14855, 16412 | 895 px |
| 27 | 16250, 16250 | 15089, 16351 | 1,161 px |

Those seven began one per white tile, spread over a 1,500 px square. You
brought them into a knot about 250 px across, the nearest two 61 px apart
centre to centre. Cows are 60 px squares, so they ended almost touching,
and none overlapping.

Nothing in the code says "herd the cows." A cow only keeps 225 px from
any dog that is moving, and moves at half a dog's pace. Herding came out
of you, playing: walking the dog round the far side of a cow, pushing it
inward, going back for the next. That's the first time the game has had
a verb you didn't put in the rules. It's worth celebrating.

## How we got here

Two days ago Dog Park was a page that drew dogs. Today's physics would be
unrecognisable to this morning's:
- **The walk** (decision 20) replaced "everyone thinks at once." A pull
  ripples out from the leashed dog, shortest link first, through at most
  40 critters per pixel of drag.
- **Only critters in motion matter** (decision 21). A dog reacts to the
  leashed dog and to the dogs the walk already moved. Still dogs are
  furniture. This is what let the leashed dog lead instead of the pack
  clumping by mutual liking.
- **Cows walk with the dogs** (decision 22). No scoot and no push, just
  the same walk, mutual room, half pace, and the veto: a step is taken
  whole or not at all.
- **Nothing moves unless you drag.** It made the park calm enough to
  watch, and to debug.

Each step was one rule changed and played within minutes. The tooling
that made that possible was simple: labels under each dog (its number,
its place in the walk), and a way to rebuild any moment of your play from
the server's log and replay it through the real wasm in node. "Dog 289
seems disinterested" became, ten minutes later, "it follows 165, a still
bystander 66 px away, because rank said so." I could see what you were
seeing without seeing your screen.

## What we threw away

We deleted more than we wrote:
- `physics.zig` went from 2,213 lines to 990, and PHYSICS.md from 1,495
  to 573.
- The slow tier went from 9 minutes 51 seconds to 39 seconds.
- Gone too: the identity test, the alternate tuning, the symmetry tests,
  the herd census, the scoot, pushes and jumps, and CC's whole layer of
  exact optimisations, the wish grid, room lists and vector paths.

Some of that was good work in its day. CC's speed-ups were real and
proven exact. But they optimised rules we no longer play, and every one
of them taxed the next change. Your rule, now in memory: a test needs a
purpose you can state, and it goes the moment it stops proving
anything. The tests left are the invariant, page and server agreeing,
the protocol, and the torus. How the critters move is tested by playing.

## The invariant, honestly

You asked about it, and it's the right question. **It broke once in your
game,** and not between cows:
- At tick 129,407, dog 250 stepped onto dog 254.
- Dog 254 stood 1,646 px from the leashed dog, just outside the region's
  tiles, so the physics never saw it. The veto checks only critters the
  physics sees, and nothing stopped dog 250.
- The server noticed: it checks for overlaps after every report and logs
  a "finding". Because the pair then stayed overlapped inside the
  region, it logged one in almost every report afterwards: 1,053 of
  them.

That was the only overlapping pair in 5,619 ticks.

So the induction has a gap at the region's edge. A critter just outside
can poke its square up to 30 px into the region's tiles. Neither the
veto nor the leashed dog's sweep sees it. My new invariant test drags
from the first layout and never reached that edge, which is a lesson
about where invariant tests should look.

The fix is small and deterministic, because the page and the server know
the same region: a walked critter may not step to within one critter's
half of the region's outer edge. Nothing it can't see can then be under
its square. I haven't made it yet; it belongs with the next step.

## The nudging you see

As far as the log shows, **no cow ever overlapped another cow.** The
minimum gap among your seven was 61 px against a touching distance of
60. What looks like nudging is, I think, the walk's order:
- a cow moving away from a dog is vetoed by the cow in its way, and
  stays put;
- the cow in the way moves at its own turn;
- on the next pixel the first cow can move, and does.

From the outside, that looks like one cow pushing the other along. It
isn't a push, but you say you want it, and that matters more than how
it works. It's a cheap, honest kind of cow-to-cow contact. It costs
nothing, it keeps the invariant, and it happens only when cows are
already touching.

## The next step: cows that herd

You want cows to herd among themselves, but only when they're close.
Some shapes this could take, roughly from least to most invented:

1. **A cow follows the nearest moving cow, within a short reach.** This
   is the dogs' anchor rule, with a reach of maybe 120 px, a band of
   about 70 to 90 px, and no breeds. A cow on its own still only flees
   dogs. A cow next to a fleeing cow drifts after it. Cows would move as
   small groups once the walk sets one moving.
2. **Cows prefer the walk's cow links.** The walk already lines up a
   cow's nearest critters. If cows anchored on the cow that lined them
   up, a group would hang together as a tree, the way dog herds do.
3. **A herd as a thing.** Cows within some distance of each other form a
   herd, the herd has a centre, and a cow wants to stay near it. This is
   more "flocking", and harder to keep honest in integer, step-by-step
   physics.

I'd start with 1. It's the smallest change, and it reuses the dogs'
anchor code. It also keeps the property that made today work: a cow
reacts only to critters in motion, so a still herd stays still until
you come for it.

## Open questions, for later

- **What is the game?** Today you herded seven cows into a corner of the
  park because it was fun. That could become the goal: a pen, a score, a
  clock. Or it could stay a toy, like a sandbox you like returning to.
- **What should a player be able to see?** Ranks are gone from the rules
  except for ties, so there's no hidden pecking order left. The walk
  numbers show the cascade, but they're a debugging aid. A finished game
  might show something gentler, such as a faint line from each dog to
  the dog it follows.
- **Speed is fine, for now.** The busiest spot of the starting park costs
  about 19 ms a tick natively, and the packed herd 17 ms in the page,
  against a 62.5 ms tick. The walk scans every critter it can see at
  every visit. That's the first thing to fix if the region or the walk
  grows.
- **Persistence and a droplet of its own** are still waiting. They're
  boring and necessary, and nothing about today's physics changes them.
- **The protocol is the stable part.** The report, the judge, the log,
  the snapshots and the page's engine haven't changed shape in two days
  of physics churn. That's the client-drives design doing its job: the
  physics can be rewritten every hour, and the server just re-runs
  whatever the page ran.

It's day two, the herding is fun to watch, and a dog just herded cows.
