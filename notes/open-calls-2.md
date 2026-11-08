# Open calls, round 2

New calls from the latest reviews, and only those. You answered round 1 (notes/open-calls.md). None of these is urgent, and lanes work around each one. A word each is enough. My lean is after each.

## Names

1. **`cam_focal` becomes `focal_length`?** It's an abbreviation in about 40 signatures (Picture.Setting, RiderCamera, Pipeline…). Large churn, but a real gain in clarity. *My lean:* yes.
2. **The point names.** `RiderPoint`, `RaisedPoint`, `LevelPoint` and `AheadPoint` form a 2×2 grid ({on the ground, raised} × {anywhere, past the near plane}), and the names hide it. Renaming `LevelPoint` to `RiderPointAhead` and `AheadPoint` to `RaisedPointAhead` would show it. The book teaches `RiderPoint`. *My lean:* yes; the book's rewrite will follow the code anyway.
3. **Two unit names that don't stand alone.** `Fraction.less` has 9 callers, and `trunk_height_share.less()` reads as a comparison. It could be `rest_of_whole`, or `complement` if you'd like the math word. `portion : X, X -> F64` is on six units, with about 22 call sites, five of which wrap it straight into a Fraction. It could be `ratio_to(whole)`. *My lean:* `complement` and `ratio_to`.

## Where a rule lives

4. **The herds' front distance.** `Geom.herd_front_distance` is used only by CowHerd and PigHerd. Either World, which sets each herd's layout, gives both herds the value, since the same distance from the road is a route-wide rule, or each herd owns its own copy. *My lean:* World gives it.
5. **The pinhole's x rule has two homes.** `Camera.project` maps a near point's slope to a screen x, and `Lens.x_for_turn`/`turn_at_x` do the same for a far direction (`tan(turn)`). One private `x_for_slope` in Camera would hold both, and Lens would keep only focal lengths and `y_for_height`. Against it: "near points in Camera, far directions in Lens" reads well today. *My lean:* move them into Camera.
6. **`Scene.RideFacts` repacks RideInstant.** Its `encounter_timing` already holds the clock, beside a separate `clock`, and the truck is repacked as `{ route_position, lit_truck }`. If Scene stored the sources (`{ encounter_start, truck, clock }`), the clock would have one home, but Scene would get wider, taking on Truck and the timing rule. *My lean:* Scene takes the sources.
7. **The sun's radii are resting-lens sizes, typed as Pixels.** `Sun.radius`, `glow_radius` and two more are measured through the lens at rest, which is FarHeight's definition. So Sun crosses units by unwrapping, and redoes the at-rest-to-drawn step by hand four times. Either widen FarHeight into a resting-lens length (renamed, since a radius isn't a height), or keep Pixels and give Lens one `size_on_screen` maker that `y_for_height` and Sun share. *My lean:* the Lens maker only.

## The still data

8. **Repeated corners.** Every emoji polygon closes on its first corner, sometimes two or three times, and so do 13 to 17 polygons of each cat still. The stills widget works around it with a filter ("A baked still repeats some corners"). A script would strip them once, and `Still.of` would refuse a corner that repeats its neighbour. No pixel should move, but the data diff is large and the widget's counts change. *My lean:* yes, strip them.
9. **The cat's frame.** Still's doc promises feet at y 0, height 1 and x measured from the middle. But the cat's stills run from x -0.78 to 1.47 and y -0.04 to 1.12, because its poses share one frame so the cat doesn't jump between stills. Is the frame a rule (normalise the cat data, which moves pixels) or a convention (the docs say a set of poses shares one frame and may reach past it)? *My lean:* a convention; fix the docs.
