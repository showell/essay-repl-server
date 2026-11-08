# Connections across Safari: a riff

*2026-11-08. A thinking note that follows on from four-moving-things.md and your reply to it. Nothing here is a proposal to act on. Where an idea seems like a real win, I say so.*

## Your RiderEffects thought, from both sides

The rider is the one thing everything else is measured against, and the influence runs both ways. Listing both directions makes the shape plain:

| The rider affects the world | The world affects the rider |
|---|---|
| when a cat's crossing starts (`EncounterPlan`, once a segment) | a crossing cat holds the throttle at steady (`EncounterReaction`) |
| when a bird's flight starts (the same plan) | a bend's speed limit and the brake for it (`VehicleLimits`, `Throttle`) |
| where the truck aims to be (`tease_position`, every step) | a distracting pig slows the rider to gawk (`Gawking`) |
| | where the eye goes: a bend, a pig, the cat (`Gaze`) |
| | how hard the eye is held, which sets the lens (`Rider.attention`) |

The left column is all hand of god: the story bending the world around the rider. The right column is all the rider's own reactions: the rider's body and eye answering the world. Today the right column has two homes, `EncounterReaction` for the encounters and `Gawking`, `Throttle` and `Gaze` for the rest. The left column has two homes too, `EncounterPlan` and `TruckJourney`.

So a `RiderEffects` type would cut across the cleanest line the code has, the line between what the world does to the rider and what the rider does about it. I'd keep that line, and if anything gather the left column: "the ways the story reads the rider" is a short, telling list, three entries long. That's a candidate for one paragraph of the book, not a module.

## What the ride actually stores

Every frame is worked out from very little. `RideInstant` holds the clock, the rider (bike and eyes), the truck's journey, and the encounter plan for the current segment. That's the whole of the state. Everything else is a function of those and the route: the sun, the sky, the beacons, the lamps, the cat's pose, the bird's place, every tree, tower and herd.

That's why StepBack is cheap, and why any frame can be checked cold. It's also the best one-line summary of the whole design I can think of: "four things are remembered; everything else is worked out." The book's Motion part could open with it, right before the four-at-a-glance table.

## The clock-driven family

The sun, the sky, the beacons and the headlights form a chain, with nothing stored anywhere along it:
- the clock sets the sun;
- the sun sets the sky's darkness;
- the darkness sets the headlights.

The beacons hang off the clock directly. This is the cheap end of motion. Every link is a pure function, so it steps back for free.

The truck's brake lights are the one lamp that isn't on this chain. They read the journey's last step. That's exactly the split the lights chapter already teaches, seen from outside the truck.

## Two kinds of "lit"

`Truck.headlights` and the tower's `LitBeacon` are both "how bright is this lamp right now", and both come from the clock, one through the sky and one directly. They're shaped differently: a lamp is `On` or `Off`, while a beacon has a brightness `Fraction`. That's honest: a beacon fades and a headlight switches. I wouldn't unify them, but the comparison is a nice two-line aside for the lights chapter, since the beacons chapter comes first.

## The cheats, all in one list

| Cheat | Its one home |
|---|---|
| the sun and the mountains at infinity | `FarHeight`, `Lens.far_point` |
| towers sink over a 20 km earth | `EarthCurve.exaggerated_drop` |
| the ground's own curve, 100 km | `EarthCurve.ground_drop` |
| an hour of sun in 1,000 steps | `SunPath` |
| the truck's tease | `TruckJourney.tease_position` |
| the cat's and the bird's timing | `EncounterPlan` |
| the bike turns the same at any speed | `Motorcycle.turn_per_lean` |
| keyframes and arcs by eye | `CatCrossing`, `BirdFlight` |

Each has one home, and that's the axis we named. One thing the list shows: the truck sinks over the ground's honest 100 km curve, while the towers sink over the exaggerated 20 km one. The truck is never far enough away for that to matter, so it's correct, but a reader could ask why the two differ. One sentence in the truck chapter would cover it, if anything does.

## Placement, two clocks

Things are placed in two ways:
- **Placed once,** when the world is built: trees, herds' shapes, the bend animals, the route itself.
- **Placed each frame,** from the segment: towers, and the encounter animals from their timelines.

The truck is a third way: it's placed by its journey, which is the one stored position besides the rider's. So "where is it?" has three answers: the world, the frame, or the state. That's a crisp table for the placement part of the book.

## What covers what, three mechanisms

- the backdrop's fixed order: sky, then sun, then grass;
- the frame's layers: skyline, ground, scene;
- one depth sort inside the scene, ties broken by `Scene`'s field order.

After today's frame-layers lane, each has one home. The sun lives entirely in the first mechanism. That's why "the sun has no depth" in the comparison.

## Sparked by the four

- **The sun is the only one of the four with no record of its changing facts.** Under the naming rule, `Sun` would be its kind. Its one changing fact is where it is, and that's already the sighting. So the sun may be the honest exception: a thing whose look this frame is only its place. I'd leave it, and say so in the sun chapter in one line.
- **The cat and the bird share an engine, and the code already says so** in `Encounter*` and `Animation`. Your "CrossingCritter in an OO world" is exactly what `EncounterPlan` plus `Animation.Timeline` are as values and functions instead of a base class. That contrast might be worth a sentence in the cat chapter, for readers coming from OO: the shared part is a module you call, not a class you extend.
- **The table for the Motion part.** Agreed. It reads best with the "four things are remembered" line above it, and the pair sections stay here as background.

## The real wins, if any

None are urgent. The two I'd keep in mind for the book:
1. "Four things are remembered; everything else is worked out", followed by the at-a-glance table, as the opening of Motion.
2. The two-column table of what the rider affects and what affects the rider, somewhere in the rider's chapters.
