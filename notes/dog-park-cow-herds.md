# Dog Park: the cows learn to herd

*2026-10-14, evening, at dog-park `9fae6a9` (decisions 23 to 25), live on
:9103.*

## Where the evening ended

Your last board has a herd of twelve cows: 0, 5, 10, 11, 15, 16, 17, 20,
21, 22, 23 and 27. They're packed into a block about 360 by 200 px, with
14 pairs touching. Here it is, one cell per cow's width (60 px):

```
 .  . 23  .  .  .  .
20 10 22  .  .  .  .
 . 16 27 17 11  .  .
 . 15 21  .  .  5  0
```

The herd is out on open ground, about 700 px west of where the park's
tiles begin. Those twelve started one per white tile, about 1,000 px
apart, across the park's western half. Four more pairs have formed
elsewhere (1+6, 2+12, 8+13, 26+31), and 35 of the 50 cows have left
where they started. In 16,548 ticks of play, the server logged no
overlap at all.

This afternoon's essay ended with a dog that could push seven cows into
a corner, one at a time, while the cows ignored each other. Tonight the
cows hold together on their own. You gather them, and they stay
gathered.

## Three rules, one evening

**Decision 23: the edge.** This was the one bug in this afternoon's
game. Dog 250 stepped onto dog 254, which stood just outside the tiles
the physics sees. A critter whose point is outside those tiles can
still poke its square up to 30 px in. Now no step may come within 30 px
of the edge of the seen tiles. The page and the server compute the same
tiles, so they agree on every veto. Since then, no overlaps have been
logged.

**Decision 24: a cow heeds its nearest moving critter.** My first try
at cow herding was the dogs' rule copied over: follow the nearest moving
cow within 120 px, and keep 70 to 90 px from it. You saw cows scatter
around dog 146. The log said why: the inner edge of the band, 70 px,
pushed touching cows apart every time one of them moved. Cows 17, 22 and
23 ended up spaced at 96 to 102 px instead of in a herd.

Your replacement is simpler. A cow looks only at its nearest moving
critter:
- if that's a cow, it closes in until they touch;
- if that's a dog, it keeps 225 px away from it.

That's all. You called it "another breed of dog, but slower," and that's
how it plays. There's no band and no reach. It also fixed the old
code's quiet asymmetry: a cow used to add up its fear of every dog near
it, but now only the nearest critter counts.

**Decision 25: the nudge.** You predicted the next problem, and the
board showed it: cows 27, 23 and 28 sat in a touching row and wouldn't
move. The scared cow's step was vetoed by the cow in its way. That cow
was already touching its nearest moving kin, so it wanted nothing. Both
rules were working as written, and together they deadlocked.

Your idea was for a blocked critter to ask its kin in the way to move
forward. In code:
- When a step is blocked by kin (a cow for a cow, a dog of its own
  breed for a dog, never the leashed dog), the kin take the same step
  with it.
- Anyone they in turn would bump into is nudged too, up to 8 critters in
  all.
- **All or none:** if any of them would hit a critter that isn't kin, or
  come too close to the edge of the seen tiles, nobody moves.

The guarantee stayed simple, which is why this was safe to build in one
go. The group moves by one shared vector, so its members can't overlap
each other. Everyone else was checked before anyone moved. The induction
from decision 22 still holds, with "one critter" replaced by "one group."

Your test was the right size: one dog, an empty board, and a row of
three touching cows. After 20 ticks of dragging at them, all three have
moved west together, still exactly 60 px apart, and not a 256th off
their row. The same test is red against the version before the nudge.

## Why it works, as far as I can tell

Three things combine, and none of them alone makes a herd:
- **The dog supplies the push.** A cow runs only from the nearest moving
  dog, so a herd is pushed from whichever side you come at it.
- **Kin attraction supplies the cohesion.** A cow next to a moving cow
  closes in instead of drifting off. That keeps a herd a herd as you
  push it, and it's what the band was getting wrong.
- **The nudge supplies the transmission.** Without it, a push stopped at
  the first cow behind the scared one. With it, the push carries
  through a row.

What I'd most like to understand next is how a herd of 12 moves when the
nudge carries at most 8. My guess is that it doesn't move as one piece:
it moves as overlapping waves, with each cow the walk visits nudging the
row in front of it, so a big herd shuffles rather than slides. That
might be part of why it looks alive. It's worth watching for before
tuning anything.

## Two corrections from tonight

- **Where 225 px comes from.** You asked, and the answer was less
  interesting than it sounded. It's `wary`, from the play tuning on
  2026-10-13 (dogs' reach on other breeds, +50%). Cows borrowed it in
  decision 22 rather than getting a number of their own. It has never
  been tuned for cows.
- **The 16 cows.** I warned you that the no-reach rule would gather
  cows from across the region, citing 16 cows moving in one tick. That
  came from the worked example, a contrived board where every dog near
  the leashed one has been moved away. On the real starting park, the
  walk's 40 visits are mostly dogs. A probe over 58 ticks of dragging
  found about 3 or 4 cows per walk, and about 3 cows moving per tick.
  You were right that the dogs in between would soak up the walk. The
  lesson for me: check a claim about play against the played board, not
  the test fixture.

## What changed in how we work

The loop this evening ran like this:
1. You played and named a symptom with critter numbers ("dog 146 makes
   the cows disperse", "the three cows next to dog 185 can't move").
2. I rebuilt the board from the server's snapshot or log and found the
   mechanism.
3. You stated the rule; I built it with one small test that is red
   against the old code.
4. The fast tier ran (about 8 s), and I deployed to :9103.

Each round took minutes. The snapshot file turned out to be the quickest
way in: it holds every critter's current position, so "look at my board"
is one small script, with no replay needed.

The tests stayed honest. Tonight added four, and each states one rule
with a small hand-built board: the edge, the cows' nearest critter, the
nudge carrying a row, and the nudge stopping at a stranger. Nothing
tests how herds *feel*; you do.

## Open questions

- **Should dogs nudge?** They do now, because your definition said "same
  species and breed." A follower blocked by a dog of its own breed now
  carries it along. If dog herds start to look pushy or bulldoze
  through, this is the first suspect. It would be a one-line change to
  make the nudge cows-only.
- **Does a herd ever break up?** Kin attraction pulls toward the
  nearest moving cow only, so a still herd stays put until a dog comes.
  That's the stability you asked for in the neighbours essay. Whether
  you can split a herd on purpose, say to cut out one cow, is a
  question for play.
- **Does cow attraction need a reach?** On the played board it hasn't
  mattered so far, because dogs fill the walk. If you ever see a lone
  cow walk a long way to join a group it can't see on screen, that's
  the cause.
- **What is the game?** Twelve cows in a block west of the park now looks
  like something a player did on purpose. A pen with a gate, a count of
  cows inside, and maybe a clock would make it a game. Nothing in the
  physics would have to change for that.
