# The truck, from first principles

**Steve, 2026-11-08:** not `TruckChase`. "Chase" describes the rider as much as the truck. He offered `TruckJourney`, `TruckItinerary` or `TruckPath`, preferring an evocative name in the spirit of Crossing and Flight over a uniform `Path` suffix. The truck and the sun are animations too, but ones that last the whole ride, so don't force them into the cat and bird's structure. Mostly settle the names, with restraint, and watch for small moves such as a field here or there. **Chosen: `TruckJourney`.** It's the truck's own travel over the whole ride, and it's evocative, like Crossing and Flight.

*2026-11-08. A design note, so we can talk it through. Nothing is built yet. TruckChase is agreed.*

## What a truck is

A truck has a body, tires, headlights and brake lights. Each frame raises two questions about it:

1. **Where is it, and how is it moving?** That's the chase: position along the route, speed, and whether the last step slowed it. The driver's tease and the road's bends decide it. This is **`TruckChase`**, and it is stepped motion.
2. **How does it look right now?** The body and tires never change. What changes is whether each lamp is on. Two rules decide that: the headlights have a sensor that reads the sky, and the brake lights follow the chase's last step.

Drawing then takes the second answer, plus where the truck stands, and turns it toward the camera.

## The smell you named

`LitTruck` names the truck after one fact about its look this frame. That's composition by adjective: if the truck also honked, we'd be on the road to a `HonkingLitTruck`. The fix is composition by field. The truck as seen this frame is a record, and each fact that can change is one field of it:

```roc
Truck :: { headlights : Lamp, brake_lights : Lamp }   # the kind the scene draws
Lamp : [On, Off]
```

A horn would be a third field, and its name stays `Truck`. The rules that set the fields stay where they are: `Truck.at(pace, darkness)` is today's `LitTruck.at`. The parts that never change are modules the truck draws with: `TruckShape` (the box, and moving a point from the truck's frame into the rider's view), `TruckBody` (faces and tires) and `TruckLights` (beams and lamps).

So the change is two renames, in order:
- `Truck` becomes `TruckChase`;
- `LitTruck` becomes `Truck`.

Plus the `Lamp` name for `[On, Off]`. The code is already shaped this way; only the names are lying.

## The precedents

The four things that move through the world all have the same two halves. The names disagree:

| Thing | How it moves (the hand of god or the clock) | How it looks this frame (the kind the scene draws) |
|---|---|---|
| sun | `SunPath` | `Sun` |
| cat | `CatCrossing` | `PosedCat` (`{ pose }`) |
| bird | `BirdFlight` | `PosedBird` (`{ pose }`) |
| truck | `TruckChase` (today `Truck`) | `LitTruck` → `Truck` |
| tower (doesn't move) | none | `Tower` (`{ yaw, beacon }`) |

The pattern the sun and the tower already follow is the one I'd make the rule:
- **The motion module is named for the activity:** Path, Crossing, Flight, Chase.
- **The kind is the plain noun,** and its changing facts are its fields.

By that rule, `PosedCat` and `PosedBird` have the same adjective smell as `LitTruck`. A cat that also blinked would push toward `PosedBlinkingCat`. Since `Cat` folded into `CatCrossing` today, the name `Cat` is free. So the same move works there:
- `PosedCat` becomes `Cat`;
- `PosedBird` becomes `Bird`.

Each is still `{ pose }`, and ready for a second field if one ever comes.

One more, smaller: the tower's field is `beacon : Beacon.LitBeacon`, its brightness this frame, so "Lit" shows up there too. It reads less badly, because a beacon really is lit or dim. I'd leave it unless you'd rather it match.

## What it would take

Renames only. Pixels hold.
- **Code:** game.roc, the scene and the sightings, the widgets that name these types (the cat, bird, stills, step and truck widgets), and the expects.
- **The book:** includes are re-pointed by the rename tool. The prose names (`LitTruck`, `PosedCat`, `PosedBird`) need a pass in the truck, cat and bird chapters. The truck chapters are the ones you're about to read.

## My lean, and one question

Do the truck now, so your read sees the final names: `TruckChase`, then `LitTruck` to `Truck`, plus `Lamp`. Do the cat and the bird in the same lane, so the rule holds everywhere at once.

**The question:** should the rule be "the kind is the plain noun, with its changing facts as fields", applied to the cat and the bird as well as the truck?
