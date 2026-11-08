# Should a sighting know how far the ground has dropped?

*2026-11-08. This answers your question. Short version: yes. It's a better design than the one I pushed for this afternoon, and the numbers say it costs nothing you could see.*

---

## What a sighting holds today

`Pipeline.sighting_of` is the one place every object's `Spot` is made:

```roc
Spot :: { place, road_point, lift, foot : RiderView.RiderPointAhead }
```

The `foot` is where the object stands in the rider's view, and it gives the distance ahead. So the sighting already holds everything the earth's curve needs, and it throws that away. Each kind then deals with the curve on its own, or doesn't:

| Kind | What it does about the curve |
|---|---|
| The truck (body, headlights, brake lights) | lowers **every corner** through `EarthCurve.raised_ground_point`, which is why TruckBody imports EarthCurve |
| Towers | work out the drop **once, at the foot** (`exaggerated_drop`, a tighter curve on purpose), and lower the whole tower by it |
| Trees, critters, billboards | ignore it: at 300 m they stand about 0.45 m too high, roughly a pixel |
| The ground patches | lower every point, through `EarthCurve.ground_point` |

That's four answers to one question. Your instinct says it should have one home, and that the home is the sighting.

## The numbers say one drop per object is enough

The drop is `distance² / (2 × 100 km)`. What matters is how much it changes across one object. For something `w` metres deep at distance `d`, the change is about `d × w / 100 km`:

| Object | Distance | Drop at the foot | Change across the object |
|---|---|---|---|
| The truck, 12 m long | 300 m | 0.45 m | 3.6 cm |
| The truck | 50 m | 1.3 cm | 6 mm |
| A tree | 300 m | 0.45 m | nothing (it's a card) |

At 300 m a pixel covers well over half a metre, so lowering the truck's corners one by one buys nothing you could see. Towers already prove the pattern works: one drop at the foot, applied to the whole thing.

The ground patches are different. A patch reaches hundreds of metres across the curve, so its points really do drop by different amounts. The ground keeps lowering point by point, and that's the one place `EarthCurve.ground_point` belongs.

## The design

- **`Spot` gains `drop : Distance`:** how far the ground has curved away beneath the foot. `Pipeline.sighting_of` works it out once, from the foot it already has.
- **`Spot.base()` lowers by it.** Every card (trees, the cat, the bird, the billboards) then sits on the curved ground for free, which settles the old open call about the ground curve "only if it simplifies". It does simplify.
- **Solids use `spot.drop` for every corner.** The truck's body and lamps lower each point by the spot's one drop. They still place corners on the road themselves, since a truck can stand across a bend, but they stop importing EarthCurve. `EarthCurve.raised_ground_point`, which I made the "one home" this afternoon, goes away. That was the wrong home.
- **Towers:** they use the tighter curve on purpose, so a far tower sinks out of sight by 1.8 km. They could keep doing that in their own sighting, or be told the plain drop if the exaggeration is no longer wanted. That's your call on the look; the code is simpler without it.

## Below the horizon

As you say, there's nuance, but the sighting now has both halves:

- the **drop**, from the distance;
- the **height**, from the kind: `Pipeline.scenery_sighting_of` already asks each kind for `scenery_height`, which is how it refuses `TooSmall`.

So the general refusal becomes `BelowHorizon` when the object's top, its lift plus its height, is still under the line from the rider's eye that grazes the ground. That's a few lines in one place, and every kind with a height gets it. The truck and towers come through `sighting_of`, which has no height, so they'd either gain one or keep today's rule. The lane now refusing sunk towers is doing exactly this for towers alone, and its rule would become the general one.

## Cost

- **Pixels move.** Cards drop by up to about a pixel near the far end of the view, and the truck by under a pixel. The held hashes get re-pinned once, in the commit that does it, with the frames looked at by eye.
- **Reach:** Spot, Pipeline, TruckBody, TruckHeadlights, TruckBrakeLights, TruckShape, EarthCurve, Tower (if towers join), and the book: the truck chapter's placement paragraph and the math layer's curve paragraph get simpler.

## Lean

Yes: the drop goes in the sighting, and solids use one drop per object. Towers would keep their exaggerated curve for now, set in their own sighting. After that, the general `BelowHorizon` in `scenery_sighting_of`.

One question: should towers keep their exaggerated curve (a far tower vanishes at 1.8 km), or take the plain drop like everything else (it would stay visible to about 4 km)?
