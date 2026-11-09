# Standing things on the road, once

*2026-11-10. Your proofread comment: "It's very smelly that all these basic transformations of coordinate systems are happening within the truck code." You're right, and it's worse than one copy.*

---

## What the code does today

Three things in the picture are solid and turned to face some way: the truck, the towers, and (in a small way) the truck's lamps. Two of them carry their own copy of the same geometry.

| Where | What it does |
|---|---|
| `TruckSighting.road_heading` | finds which way the road runs at a spot, by placing two points a metre apart and taking the angle between them |
| `TruckPlacement.raised_point` | turns a point by that heading about the truck's foot, shifts it out, lifts it, and lowers it by the ground's drop |
| `Tower.base_corner_on_road` | turns a corner by the tower's yaw about its center, but on the road, before the road brings it into the rider's view |

So "turn a point about a foot and stand it at a spot" is written twice, in two different frames, and "which way does the road run here" is a truck-only function, though it's a question about any spot.

There's no good reason for this. It grew one object at a time.

## The design

Your instinct is that this belongs to every object on the road, not to the truck. The sighting is already where that kind of knowledge lives: it made `Spot` know the ground's drop. It can know the road's direction the same way.

**1. A spot knows which way the road runs there.** The sighting works it out once, alongside the foot:

```roc
Spot.road_heading : Spot -> Angle.Turn
```

It's the road's direction at the spot, seen from the camera. Today's `road_heading` moves into the sighting, and it's computed for every spot, so it's no longer the truck's. This one is stored, not worked out on demand: its sources, the road and the camera, aren't in the spot. That's the same as the foot.

**2. One function stands a point of a solid thing at its spot:**

```roc
Spot.standing_point : Spot, { facing : Angle.Turn, offset : { ahead : Distance, rightward : Distance, height : Distance } } -> RiderView.RaisedPoint
```

- `facing` is how the thing is turned against the road: 0 for the truck, which faces along the road, and the tower's yaw for a tower.
- `standing_point` turns the offset by the road's heading plus the facing, carries it out from the foot, lifts it, and lowers it by the ground's drop. That's today's `TruckPlacement.raised_point`, made general.

**3. Every solid thing uses it.** The truck's body and lamps call `spot.standing_point(...)`, so `TruckPlacement` shrinks to "place a face", or goes. The tower turns its footprint corners with the same call, and `base_corner_on_road` goes. Cards don't need it: they face the camera, which their foot already does.

After this, every coordinate change for things on the road lives in two places, both general:
- the road → the rider's view: `RoadAhead.rider_point_at`;
- a solid thing's own frame → the rider's view: `Spot.standing_point`.

That's the "position and stance relative to the rider" you described. Object-to-object (the truck to the rider) is already done by distance along the route, in `TruckJourney`, and nothing draws one object relative to another.

## Cost

- **The truck:** pixels hold. It's the same arithmetic, moved.
- **The towers:** turning on the road and then placing each corner is the same rigid motion as placing the foot and turning in the rider's view, but the floats are summed in a different order. So the tower frames may move by a bit or two, and that would mean one re-pin after an eye check.
- **A little more work per frame:** every spot gets a heading. That's one more road lookup per sighted object, a couple of hundred a frame.
- **The book:** the truck chapter gets shorter. Placement becomes "every solid thing stands on the road the same way", and the towers chapter can point at the same function.

## Lean

Do it. It's the generic code you expected to find, it removes a duplicate, and the truck chapter loses its trig.

One question: is `Spot` the right home for `standing_point` (a spot is where a thing stands), or would you rather a small module named for the activity, such as `Standing`?
