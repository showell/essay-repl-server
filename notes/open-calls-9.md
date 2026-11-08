# Open calls 9: five more design calls

*2026-11-08. These are the next five from the audits, weightiest first. Each has a lean; a word inline is enough.*

---

## 1. The ride borrows from the drawing side

The book's system chapter wants a one-way arrow: the view reads the ride, and the ride knows nothing about drawing. The code almost has it. The exceptions:

- `CatCrossing` imports `Cat` for `Cat.CatPose` and two reach constants (`collapsed_hip_reach`, `frozen_head_reach`).
- `BirdFlight` imports `Bird` for `Bird.BirdPose`.

The book now says that, honestly, with a dotted arrow. But that arrow is the only exception, and it's small enough to remove.

**Lean:** move the pose types and the reaches to the ride side, so that `CatCrossing.CatPose` is the cat's pose. `Cat { pose }` then imports `CatCrossing` for the type, and the drawing imports the ride, never the reverse. Your naming rule still holds: the kind the scene draws is the plain noun, with its changing facts as fields. Pixels hold, and the book gets its one-way arrow back.

## 2. Attention has no ceiling, but the lens has one

`Attention` is "from 0 upward", and `Attention.of` checks only that it isn't below zero. The lens's focal length is `resting × (1 − 0.39 × attention)`, which reaches zero at an attention of about 2.56. Past that it goes negative and flips the picture. Today's peak is the cat's, 1.8, so nothing breaks yet. The limit exists only in RiderCamera's arithmetic.

- **A:** give Attention a ceiling. That's an eye limit, but its number would really come from the lens.
- **B:** RiderCamera crashes with a reason on a focal length that isn't positive. That's a lens limit, enforced where the lens is.

**Lean:** B. The lens is what breaks, so the lens says so.

## 3. RoutePlace holds a RoadPoint

`RoutePlace` is `{ segment_index, along, across }`, and `Geom.RoadPoint` is `{ along, across }`. So `RoutePlace.road_point()` rebuilds a RoadPoint, `route_place_past_bend` takes one apart, and RiderCamera copies the two fields out. Your "compose by field" rule says `{ segment_index, road_point : Geom.RoadPoint }`.

The cost is about 35 lines that read `place.along` today, which would read `place.road_point.along`. They're in Motorcycle, Gaze, Throttle, Gawking, RideInstant, PigHerd, RiderCamera, three widgets and the tests.

**Lean:** yes. The extra word says exactly which space the coordinates are in, which is the book's "one record per space" idea. Pixels hold.

## 4. RiderMind.gaze_target

`RiderMind.gaze_target` is a one-line pass-through to `Gaze.desired_gaze`, with one caller. It keeps the book's sentence "every decision the rider makes is RiderMind's" true. But the gaze widget and the tests call `Gaze.desired_gaze` directly, so the decision has two names.

- **Keep it:** RiderMind is the rider's whole mind, and the book can say so in one line.
- **Inline it:** RiderMind becomes "the lean and the acceleration", and the eyes ask Gaze themselves.

**Lean:** keep it, and have the gaze widget and tests call `RiderMind.gaze_target`, so there's one name for the decision.

## 5. A FocalLength type

`focal_length : Pixels` is bare. A focal length longer than the resting one crashes in `Lens.lens_scale`, and the tests use 800 and 1000, so the rule shows up only as a crash, far from where the value is made. A `FocalLength` type would make the rule the only way in, which would also cover call 2.

The reach is wide: every `Picture.Setting`, the camera, the lens and the proof tools.

**Lean:** not now. Do call 2's lens check first, since it's cheap. Revisit FocalLength when the book is done, if the crash still feels far from its cause.

---

Still queued behind these: the SegmentPlace rename, FarHeight's two meanings, the widget palette and captions, the platform items, and a few smaller ones.
