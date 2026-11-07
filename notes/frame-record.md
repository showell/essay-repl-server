# The frame's top, and the walk's depth

Two short questions. A review of `Tour`, `RideInstant` and `Scene` turned up eight findings. I decided five; three are yours, and two of those fit one answer. The second question is about the type walk.

## 1. What a frame is

Today `RideInstant` does two jobs. It holds and steps one moment of the ride, and it also builds the frame from that moment: ten of its 17 imports serve only the frame. Painting a frame then takes three calls on Tour (`frame_content`, `roll`, `sky_colors`), and SafariApp, RasterFrame and ShapesFrame each put the three back together.

Decided: the frame-building moves out of RideInstant into a module of its own, and RideInstant keeps `initial`, `next_or_restart` and a private `next`.

**(a) The new module's name.** It answers "what the camera shows at one instant". `Frame` is the obvious word, but the web platform already has a `Frame` module (`Frame.Shape`), so a reader would meet two. I'd take **`View`**:

```roc
View :: { shapes : List(Shapes.Shape), sun : Sun.Sighting, sky_colors : Sky.Colors }.{
    view_at : List(World.Segment), RideInstant -> View
}
```

Other words would be `Shot` or `Picture` (taken: `Picture` is the kinds' drawing).

**(b) Is the roll part of it?** Bundling the sky with the shapes and the sun is clear-cut, since all three follow the clock. The roll is less clear: it's how the camera is turned, not something in the frame.
- **In:** one call per frame, with nothing left to reassemble.
- **Out:** the record is "what's seen", and the roll is "how it's held".

I'd keep the roll **out** as its own call. That leaves two calls per frame instead of three.

**(c) One camera record.** Later, not now. The camera is packed two ways today: `Lens.CameraAim { heading, cam_focal }` for the sky side, and `RoadAhead.CameraView { road, cam_focal }` for the road side. Both come from the same rider through ViewYaw. One `{ heading, vantage, cam_focal }` record would be honest, but it reaches Lens, RoadAhead, the backdrop and every sighting. I'd revisit it after the SceneShapes lane and the route split, rather than decide it now.

## 2. The walk's default depth

You asked to hear if depth 3 felt noisy or incomplete. The last three reviews (SceneShapes, the truck, and this one) all said **depth 2 was enough**. The truck and this review ran at 2, and none of them needed 3. The noise they all named is the same: walking anything that holds the scene drags in every kind's closure (stills, emoji stills, poses, Tower's corners).

I'd make **2 the default** (`WALK_MAX_DEPTH`), with `max_depth=3` still there to ask for. Yes or no is enough.

## Decided without you, for the record

- `RideInstant.next`, `lit_truck`, `shapes` and `Tour.past_instants_cap` go below their blocks.
- The rider's distance along the route was worked out twice. The frame side works out the truck's `lead` once and passes TruckSighting's own record through, so Scene drops its World import.
- Tour's "never empty" comment is wrong, since the history list starts empty. The comment gets fixed.
- RideInstant's expects that restate starting constants, and the hand-made copy of `next`, go.
- `BillboardSighting.billboards_in_view` joins its family's naming.
