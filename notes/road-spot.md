# Where a thing stands, when it's drawn

This is the one finding from the truck review I held for you. It's about location having two homes at the moment an object becomes a picture. The code is on roc-apps master 3e706210.

## What happens now

A sighting knows where the thing is, once, as `Pipeline.Sighted(kind)`:

```roc
Sighted(kind) : { place, along, across, foot, kind }
```

`place`, `along` and `across` say where it is on the road, and `foot` is where that puts it in the rider's view, worked out from them.

To draw it, `Pipeline.rendering_of` hands the kind a `Picture.Setting`:

```roc
Setting(context) : { foot : Geom.LevelPoint, cam_focal : Pixels, context : context }
```

Most kinds (trees, billboards, cats, birds) need nothing more. The tower and the truck need the road as well, because their outlines are measured on it: a tower's four footprint corners and the truck's box. For them, `SceneShapes.road_context` copies the sighting's place into the context:

```roc
RoadContext : { road : RoadView, place : SegmentPlace, along : Along, across : Across }
road_context = |view, sighting| { road: view.road, place: sighting.place, along: sighting.along, across: sighting.across }
```

So a road kind receives where it stands twice: as `foot` in the setting, and as `place`, `along` and `across` in the context.

- **In production** both come from the same sighting, so they agree.
- **In a test** they can disagree. Tower's own test writes the foot and `context_along` separately, with the 20 m typed twice.
- **The truck** ignores `foot` (`{ cam_focal, context, .. }`) and rebuilds its position from the context.

It's the smell "a stored value restates another", one level up from the kind. The pipeline was built to remove exactly this kind of second home.

## Three ways it could go

**A. Leave it.** Production can't disagree, and only a test can. The cost is a second home that a reader has to trust.

**B. Name the triple and narrow the context.** Name the triple `RoadAhead.RoadSpot : { place, along, across }`. Its second user is already there: `rider_point_at` takes exactly that record inline. Then make the road context `{ road : RoadView, spot : RoadSpot }`. This is tidier, and its reach is small (RoadAhead, SceneShapes, Tower, TruckAhead), but the second home stays.

**C. One spot, built once, carried whole.** The sighting builds one opaque value holding both where it is on the road and where that puts it in the view:

```roc
Pipeline.Spot := { place : SegmentPlace, along : Along, across : Across, foot : Geom.LevelPoint }   # only a sighting builds one
Sighted(kind) : { spot : Pipeline.Spot, kind : kind }
Setting(context) : { spot : Pipeline.Spot, cam_focal : Pixels, context : context }
```

- Road kinds' context shrinks to `RoadView` alone.
- A kind that needs the foot asks `setting.spot.foot()`. A road kind also asks `spot.road_spot()`.
- Tower's test has to build a spot the way a sighting does, so it can no longer disagree with itself.
- `SceneShapes.road_context` and `RoadContext` go.

The cost is that every kind's setting now carries a spot, and most ask only for its foot. Its reach is Pipeline, Picture, RoadAhead, SceneShapes, and every kind's `scenery_picture`, since a kind that unpacks `foot` now reads `spot.foot()`. Pixels hold.

## My recommendation

C. It's the one where the wrong state has nowhere to live. It also makes `Setting` say what the book will want to say: a kind is drawn from where it stands, the camera, and whatever else it needs. One call to `spot.foot()` per kind is a small price. I'd make it a single lane holding Pipeline, Picture, RoadAhead and SceneShapes, after the billboard lane merges, since that lane touches the sightings too.

If C feels like too much of the pipeline for one finding, B is the safe half-step. It moves nothing that C would have to undo.
