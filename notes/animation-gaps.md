# What the animation design leaves open

You chose option C for the animals: each encounter records the step it starts at, chosen once from the rider's speed when it's planned ("the hand of God"), and the animal then plays at its own pace. A review of the animation code ahead of that lane found three things C doesn't settle. My recommendation follows each; a word apiece is enough.

## 1. Where the start step lives

The ride's state (`RideInstant`) holds the rider, the truck and the clock. The start has to live there too.

- **(a) One slot, reset at each new segment:** `encounter_start : [Unplanned, StartsAt(Clock)]`. This is enough because only one encounter is ever live: a gate already proves the cat's crossing starts on its own segment even at top speed, and the rider only reacts to its own segment.
- **(b) A list keyed by segment.** More general, but it needs a rule for when an entry is dropped.

I'd take **(a)**, with a new gate proving the same for the bird: its flight starts on its own segment.

## 2. How fast the bird flaps

Today the bird's 360 frames (9 flaps of 40) are played by distance: 8 frames a metre. Under C they play one a step, so a flight would last 360 steps and stretch far past its segment. The flap needs a length in steps.

I'd keep **the look you have now at cruising speed**: work out how many frames a step the rider sees today at a typical speed, and set the flap length so that stays the same. That's the "preserve behavior" choice. The flight then gets its planning gap from that length, as the cat's does.

## 3. The rider's throttle while the cat crosses

Today the rider may not speed up while a cat crosses. The code's own reason was the old estimate's crutch: a step mustn't skip more than one frame. Under C that reason is gone.

- **Keep it, as a story rule:** the rider eases off while a cat crosses. That's the rider reacting to the cat, which fits your model, since the cat never reacts to the rider.
- **Drop it:** the ride moves a little.

I'd **keep it**, since it preserves behavior, and give it the story as its reason.

## Decided without you, for the record

- The cat's attention fade counts steps too: `Past(Steps)` rather than a distance turned back into steps with the current speed.
- An animal's place is `Geom.Placed`, not a flattened copy, so `Animation.Location`'s three ways of carrying one point go.
- A bird's habit is `[FliesTo(Flight), StaysPut(tree)]`, so the flight isn't rebuilt in two places.
- The start step's rounding gets one home, with ceil or floor chosen and tested on both sides.
- The test-only imports in PosedBird (9 of 13), PosedCat and Cat go, along with tests that restate constants or test StillShapes.
- Cat and BirdFlight stay as they are, not methods on the encounter.
