# One camera record

You said one camera record is "something we should definitely do". A design agent mapped every place a camera fact is built, packed and passed. Here is the shape, with my recommendation. Three questions are yours.

## Today

The camera is one thing seen five ways, all from one RiderState at one instant, but it's built piecemeal:
- **`heading`**, for the sky only: the sun and the mountains read it.
- **`vantage`**, for the road: where the camera stands on the current segment. It doesn't say which segment, which only `RoadView` knows.
- **`cam_focal`**, which depends on the lean and the rider's attention.
- **The roll**, which lives on Tour.
- `ViewYaw` works out the same turn twice a frame, once for the heading and once for the vantage.

RideInstant builds a `Lens.CameraAim { heading, cam_focal }`, takes `cam_focal` back out, and builds a `RoadAhead.CameraView { road, cam_focal }`. The frame widget repeats all of it.

## The shape

```roc
RiderCamera := {
    segment_index : Route.SegmentIndex,
    vantage : Geom.Vantage,
    heading : Angle.Bearing,
    cam_focal : Pixels,
    roll : Angle.Lean,
}.{
    of : RiderState, Route -> RiderCamera     # the view's turn worked out once
}
```

- **Built once per frame,** in a new module above the rider. It replaces ViewYaw.
- **Consumers read what they need.** The sun and the mountains take an open record, `{ heading, cam_focal, .. }`, so the widgets' test literals still work. The kinds and the ground keep taking `cam_focal` alone. FrameView reads the roll here.
- **The billboards' `resting_focal` stays.** It's deliberately not the camera's lens, and its comment says so.

Decided without you: the roll is in the camera, since it's how the camera is held; consumers take open records rather than a named alias; and the field stays `cam_focal`, matching `Picture.Setting` and dozens of functions.

## Your three calls

**1. The name.** Safari already has a `Camera` module (the pinhole: eye height, projection, clipping), and so does lib. So this one can't simply be `Camera`.
- `RiderCamera`: whose camera it is.
- `FrameCamera`: when it's built.
- Rename Safari's projection module (say, `Pinhole`), and let this one be `Camera`.

I'd take **`RiderCamera`**. It follows your rule that an abstract thing gets two words, and it says whose eyes these are.

**2. Should the vantage leave `RoadView`?** With the camera holding the vantage, `RoadView { route, segments_ahead, vantage }` would carry a second copy of it.
- **Out:** `RoadView` becomes pure road, `CameraView` dies, and the sightings take the camera plus the road. One home for the vantage. The reach is large: RoadAhead, Pipeline, Geom, every sighting, the bends widget and the cross-module tests.
- **In:** the camera makes the `RoadView` (`camera.road_view(route)`), and the vantage lives in two per-frame values.

I'd take **out**. You've said the cost of a change doesn't matter if the result is better, and here it is: the road stops pretending to know where the camera is. It would land as its own lane after the camera itself.

**3. Should `heading` be worked out rather than stored?** `Motorcycle.heading` is the route's bearing plus the yaw, which are kept in step by hand. That's a stored value restating another. Working it out from the route removes the stored copy, but the sum runs in a different order, so the sky moves in its low bits: at most a pixel's edge on the mountains and the sun.

I'd take **yes**, since an eye test is cheap now. It would be its own commit.

## The order

1. The camera itself, pixels holding, right after the World split and with FrameView.
2. Then the vantage out of `RoadView`, if you say so.
3. Then the worked-out heading, with an eye test, if you say so.

A word per question is enough.

## Steve's answers (2026-11-07)

1. **`RiderCamera`:** "yup, excellent name! Even though Camera is fairly unique in the app, I think RiderCamera just immediately orients you."
2. **The vantage leaves `RoadView`:** "100%".
3. **The heading is worked out from the route:** "yup" (an eye test for the sky).

Three lanes, in order, after FrameView merges: the camera itself (pixels hold), then the vantage out of RoadView (pixels hold), then the worked-out heading (the sky may move in its low bits).
