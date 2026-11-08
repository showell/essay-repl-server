# Truck chapters: replies to your harder questions

*2026-11-08. These answer your comments on truck-proofread. The easy ones are listed at the end, and I'll just make those changes. Each hard one below has a lean. Comment inline.*

---

## 1. TruckJourney → TruckJourney

You're right, and only the truck has this problem. Here's what the other three return:

| Module | Its type is | One step returns |
|---|---|---|
| `SunPath` | nothing: an empty namespace | the sun's direction, worked out from the `Clock` alone |
| `CatCrossing` | the plan (which tree) | a `CatCrossing.CatInstant`, a different type |
| `BirdFlight` | the plan (from tree, to tree) | a `BirdFlight.BirdInstant`, a different type |
| `TruckJourney` | the truck's progress | a `TruckJourney`, the same type |

The sun, the cat and the bird are each worked out fresh from the clock. Their modules hold a plan, and each frame asks the plan "where are you now?" The truck can't be worked out from the clock. Where it is depends on where the rider has been, so it has to be remembered and carried forward one step at a time. That's the spine of the book showing up in a type signature: it's one of the four things the ride remembers. The cat doesn't return a new crossing, because nothing about the crossing changes. The truck has no plan to hold, only progress.

**Lean:** keep `TruckJourney` as the module, an empty namespace like `TruckShape`. Put a nested type `TruckJourney.TruckProgress` in it, which mirrors `CatInstant` and `BirdInstant`. The signatures then read as English:

```roc
progress_at_next_step : TruckProgress, { rider_distance : Distance, route : Route } -> TruckProgress
```

`RideInstant.truck` becomes a `TruckJourney.TruckProgress`. The book can then say outright why the truck is the one mover whose step takes its own type and returns it.

## 2. braking_ and chasing_truck_at_next_step

With item 1, both signatures become `TruckProgress, X -> TruckProgress`. Each computes three intertwined facts, the new speed, the new position and the pace, and that's honest for progress. The names still have to go. As you said, the truck is the one being chased. What it chases is the tease mark.

**Lean:** name them for what the truck does on that step: `progress_braking_for(progress, bend)` and `progress_toward_tease(progress, tease)`.

## 3. ComingBend should hold the turn angle

Agreed. There's one wrinkle: the angle-to-speed table (`VehicleLimits.turn_speed`) isn't the truck's. `Throttle` uses the same table for the rider's bend brake. Sharing it is the point of `VehicleLimits`: both vehicles keep to the same limits.

So the truck's own rule is the shared limit times its caution.

**Lean:**

- `ComingBend : { distance : Distance, turn : Angle.Turn }`
- one function in TruckJourney, `cautious_turn_speed : Angle.Turn -> Speed`, defined as `VehicleLimits.turn_speed(turn).scaled_by(turn_caution)`

`next_bend` then just reports the road, and the braking step decides how to take the bend. The only thing that changes is where the code lives. The pixels hold.

## 4. raised_point_on_truck does two maps

It already works one point at a time, so that half of your question has a clean answer: maps 1 and 2 are per point. Map 3 (projection) has to be per face, for two reasons:

- clipping at the near plane can add or drop corners, so it needs the whole polygon;
- the depth sort orders faces, not points.

The two maps inside the function really are three steps:

1. **placement:** truck frame to road point (the two `plus` lines);
2. road point to the rider's view (`RoadAhead.rider_point_at`);
3. lowering by the earth's curve.

Steps 2 and 3 aren't about the truck at all. `EarthCurve.ground_point` already does step 3 for a point on the ground, but the truck has its own copy of it, with a raise added.

**Lean:** split it.

- `TruckShape` keeps only the placement: `road_point_on_truck : TruckSetting, TruckPoint -> { road_point, height }`.
- Steps 2 and 3 become one shared function, `EarthCurve.raised_ground_point(point, height)`, and `ground_point` is that function at height zero.

A cleanup lane would check whether Tower and the billboards have the same copy. This is the "one home for a rule" kind of finding, so I'd treat it as a code change first and a book change second.

## 5. TruckHeadlights and TruckBrakeLights

I agree. The two lamps share nothing but `strip_corners` and the truck box. One reads the sky and paints beams at the nose. The other reads the truck's pace and paints glowing lamps at the back. Today the rules live in `Truck.at`, and the painting lives in `TruckLights`, so each lamp is split across two modules. That's backwards.

**Lean:** two modules, each owning its state and its picture:

```roc
TruckHeadlights := [On, Off].{
    at : Fraction -> TruckHeadlights            # the light sensor
    picture : TruckHeadlights, TruckSetting -> Picture
}
TruckBrakeLights := [On, Off].{
    at : TruckJourney.Pace -> TruckBrakeLights
    picture : TruckBrakeLights, TruckSetting -> Picture
}
```

`Truck` becomes `{ headlights : TruckHeadlights, brake_lights : TruckBrakeLights }` and only composes the three pictures in order: beams, body, brake lights. `TruckLights` and `Truck.Lamp` go away. This follows your naming rule, compose by field, and it gives the lights chapter one module per rule.

## 6. The opaque picture type

Yes, it exists: `Picture :: List(Shapes.Shape)` (Picture.roc). Only the outer edge uses it today. `Truck.scenery_picture` wraps the list once, and inside the truck everything passes bare `List(Shapes.Shape)`: `body_shapes`, `headlight_beam_shapes`, `brake_light_shapes`.

**Lean:** with item 5, each part answers a `Picture`, and `Truck` joins pictures. That needs a `Picture.layered : List(Picture) -> Picture` (beams, then body, then brake lights). Bare shape lists then stay inside the module that builds them.

## 7. `lit_truck`

It's gone. I searched every file under canvas_apps, the book included, and no `lit_truck` or `LitTruck` turns up. I think your copy of the page came from before the rename sweep landed. If you still see it on a fresh load, tell me which paragraph.

---

## The easy ones (I'll just do these)

- "The sky knows" becomes "The `Sky` module tells us".
- Three maps: replace the paragraph with a three-row table (shape, placement, projection), and stop calling them "maps".
- Show `TruckSetting` and `Picture.Setting` in the types section.
- Lights chapter: open by saying the ride runs into the night, so the headlights show near the end, and the truck brakes for bends, so the brake lights show whenever you're close, even by day.
- `next_bend : Route, Distance -> NextBend`: kept, as you said. The book can point at it as the model for what a signature should say.

## Order

If you agree, items 1–6 go to one cleanup lane as a single truck refactor, and the three chapters get rewritten after it merges. Items 1–2 have a twin question: should the cat's and bird's step functions be named the same way (`instant_at`, which they already are)? I'd leave those alone.
