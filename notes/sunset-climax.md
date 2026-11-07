# What the sunset's climax is

You asked for a test that the sunset's climax happens on the long road heading west, measured on master with a margin, and a test that the ride reaches full night. Both are written, and both pass on today's physics and on the new rider physics. But whether the sunset one passes depends on what "the climax" means, and that's your call.

## The road

It's segment 6: 1200 m, the longest on the route, the one with the mid tower. The rider faces 7° off the sun along it. The old TypeScript version had the same test (angry-gopher `games/driving/test/test_model.ts`, check "1c"). There the road had to face the sun within 20°, with the sun above the range as the rider turns onto it and partly behind the range by the road's end. The new test follows that.

## The catch: the mountains hide the "official" sunset

The west range stands about 43 px above the horizon where the sun sets, so every horizon event happens behind the mountains, out of sight:

| What | Step | Rider (today) | Rider (new physics) |
|---|---|---|---|
| on segment 6 | | 2307–2988 | 2254–2938 |
| **the sun's lower edge meets the west range** | **2537** | **segment 6** | **segment 6** |
| the sun touches the horizon | 3233 | segment 7 | segment 7 |
| the sky at its reddest | 3984 | segment 9 | segment 10 |
| the sun fully hidden by the range | 4039 | segment 9 | segment 10 |
| the sun fully set | 4735 | segment 11 | segment 11 |
| full dusk | 5487 | segment 13 | segment 14 |
| the ride finishes | | 7071 | 6779 |

## The choice

- **(a) The climax is what the rider sees: the sun starting to sink behind the west range** (step 2537). That's the old test's idea, and it lands on segment 6 with room to spare on both physics: 230 steps after the turn, 451 before the next bend. The test as written checks this, with a 150-step margin either side.
- **(b) The climax is the sky at its reddest, or the sun fully set.** Then the rule is broken today and on the new physics: the rider is three to five segments past the long road. Fixing it means setting the sun earlier (`Sun.fully_set_at`) or changing the route, and the colors would move.

I'd take **(a)**: it's what's on screen, and it's what the old test checked. If (b) is what you remember as the climax, it's a real change to the sunset's timing, and I'd write it up separately.

## Night

Strict and loose, as you asked: the ride must reach full dusk (exactly 1.0) by its last step, with no step pinned. Full dusk comes at step 5487 on both physics, which is 1,584 steps before the finish today and 1,292 on the new physics.

## What this unblocks

If (a) stands, the new rider physics passes both rules, and I'll merge it. The held steps that no longer show their scenes, like the cat at 1570, get re-picked as you said.

## One more physics question, for whenever

The rider lane left out one change, braking from the firmest brake. The rule had no memory: the rider would leave the braking zone, open the throttle, and near a bend get asked for a brake firmer than its own speed, which crashes. The ways out are to clamp the brake at the exit speed, to give the rider a braking state, or to measure braking distance in whole steps. I'd leave it for the Motion chapter, where the brake fade and turn speeds get derived anyway. Say if you'd rather have it sooner.
