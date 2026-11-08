# The bird, the cat, the truck and the sun

*2026-11-08. Written by a cold agent from the code, then checked by me. For Steve, to see the connections; some of it may feed the book. Safari's four moving things are compared under the new names: `TruckJourney` (today `Truck`), `Truck` (today `LitTruck`), `Cat` (today `PosedCat`) and `Bird` (today `PosedBird`). Citations are to the files as they were when it was written, so `Truck.roc` is the journey, `LitTruck.roc` the truck as seen, and `PosedCat.roc` and `PosedBird.roc` the cat and bird.*

One thing the comparison turns up that the naming rule hasn't reached yet: the sun's kind. The cat, bird and truck each have a record of the facts that change, but the sun has only `Sun.Sighting`, where it lands on screen. Under the rule, the plain `Sun` would be the kind. That's a note for later, not a proposal now.

## All four at a glance

| | Cat | Bird | Truck | Sun |
|---|---|---|---|---|
| Motion module | `CatCrossing` | `BirdFlight` | `TruckJourney` | `SunPath` |
| The kind the scene draws | `Cat { pose }`, 7 poses | `Bird { pose }`, 6 stills | `Truck { headlights, brake_lights }` | `Sun.Sighting`: `InView({ x, y, focal_length })` or `OutOfView` |
| What drives it | the hand of god, planned once against the rider | the hand of god, planned once against the rider | stepped state, which reads the rider every step | the clock alone |
| How long it lasts | an encounter of 38 steps | an encounter of 36 steps | the whole ride | the whole ride |
| Stored between steps | `EncounterPlan` (`StartsAt(clock)`), shared with the bird | the same `EncounterPlan` | `{ route_position, speed, pace }` | nothing |
| Placed at | a road point and a lift on its segment | a road point and a lift: tree tops and an arc | a route position, lift zero | a bearing and a `FarHeight` |
| Drawn as | traced stills | traced stills | a real 3-D box, tires and lamps | a glow and a disc |
| Asks of the rider | the throttle held, and the eye | nothing | nothing | nothing |

The counts: the cat's 10 walking frames, 24 frozen and 4 leaping (CatCrossing.roc:90-121, 139-148); the bird's 4 side-on frames, 28 seen from behind and 4 diving (BirdFlight.roc:105-110, 135-139).

## Cat and bird

| | Cat | Bird |
|---|---|---|
| Motion module | `CatCrossing { tree }` | `BirdFlight { from, to }`, two `RoadsideTree`s |
| Kind | `Cat { pose : CatPose }` | `Bird { pose : BirdPose }` |
| Span planned by | `crossing_span`, ends at `clear_gap`, 3 m | `flight_span`, ends at `landing_gap`, 15 m |
| Planned along | just past its tree (CatCrossing.roc:56-57) | the tree it leaves (BirdFlight.roc:50-51) |
| Path | straight lines: out, frozen, a leap with keyframed lift | one eased line, raised by a 4t(1-t) arc of 5 m (BirdFlight.roc:148-154) |
| Height | 1.7 m (PosedCat.roc:17-18) | 2.2 m (PosedBird.roc:54-55) |
| Before and after | at rest behind its tree; collapsed on the far verge | perched on one tree; perched on the next |
| Rider's reaction | throttle held at steady, attention to 1.8 (EncounterReaction.roc:21-30, 63-66) | none (EncounterReaction.roc:29, 38) |
| Depth tie | after the towers and billboards | right after the trees, so a perched bird covers its tree (Scene.roc:85-101) |

They are the same machine. `EncounterPlan` starts each one once, the `Animation.Timeline` plays a frame a step, `EncounterPoses` places it, and `EncounterSighting` sees both through one generic `animals_in_view`. The difference is all in what the rider does: the cat holds the throttle and the eye, and the bird asks nothing. The bird's one quirk is that its stills are never mirrored, so it always starts on the left (BirdFlight.roc:81-87).

## Cat and truck

| | Cat | Truck |
|---|---|---|
| Driven by | `EncounterPlan`, which reads the rider's gap and speed once (EncounterPlan.roc:43-67) | `truck_at_next_step`, which reads the rider's distance every step (Truck.roc:35-47) |
| Lasts | one encounter on one segment | the whole ride |
| Kind's fields | `pose` | `headlights`, `brake_lights` |
| What sets the fields | the timeline's frame | `Truck.at(pace, darkness)` (LitTruck.roc:20-31) |
| Drawn as | a still scaled from its foot (StillShapes.roc:53-68) | every corner of a box, its faces sorted far to near (TruckBody.roc:15-23) |
| Projected by | `Camera.upright_on_screen` from its spot's base | `raised_point_on_truck`, lowered by `EarthCurve.ground_drop` (TruckShape.roc:92-112) |
| Size test | 2 px, by `scenery_sighting_of` | none: drawn however small (TruckSighting.roc:1-4) |
| Reacts to the rider | once, at planning | every step: the tease |
| Rider reacts to it | yes | no |

Both are planned against the rider, and that is the honest cheat in each. The cat looks at the rider once and then ignores him, so its timing is a single guess. The truck looks every step and chases a mark that the rider's progress sets (`tease_position`, Truck.roc:109-114). So the cat bends the rider, and the rider bends the truck.

## Cat and sun

| | Cat | Sun |
|---|---|---|
| Driven by | the hand of god | the clock: `SunPath.direction_at(clock)` |
| Lasts | 38 steps | the whole ride, setting at `fully_set_at` |
| State | `EncounterPlan` | none |
| Placed at | a road point and a lift | a bearing and a `FarHeight` |
| Projected by | the camera, from its foot | `Lens.far_point`, by turn and height (Sun.roc:35-58) |
| Depth | depth-sorted among the scene | the backdrop: after the sky, before the grass, which covers what has set (FrameView.roc:87-95) |
| Honest cheat | keyframes set by eye (CatCrossing.roc:108-111) | an infinitely far direction; up the screen a far height is scaled, not a pinhole's (Lens.roc:6-10) |

These two are the hardest and the easiest motion in the game. They still meet through the lens. A crossing cat raises the rider's attention, attention shortens the focal length (RiderCamera.roc:88-132), and the sun is sized and placed by that same focal length (Sun.roc:113-114). So while the cat crosses, a sun in view draws smaller and nearer the horizon.

## Bird and truck

| | Bird | Truck |
|---|---|---|
| Motion | a flight between two trees, planned once | a journey along the whole route, stepped |
| Stored | the shared `EncounterPlan` | `TruckJourney { route_position, speed, pace }` |
| Lift | the tree's height plus the arc | zero; the box carries its own heights |
| Shape | one still a frame, from `BirdStills` | `TruckShape`'s box, built by `TruckBody` and `TruckLights` |
| Covers | its tree, by the tie order | itself: beams, then the body far to near, then the brake lights (LitTruck.roc:46-60) |
| Reacts to the rider | once | every step |
| Rider reacts to it | no | no |

Neither asks anything of the rider. They are the two things the rider only watches. The bird is cheap to draw and planned like an encounter, while the truck is expensive to draw and planned like physics: it brakes for bends with the same `VehicleLimits` as the rider, outdone by 10% (Truck.roc:74-85, 116-137).

## Bird and sun

| | Bird | Sun |
|---|---|---|
| Driven by | the hand of god | the clock |
| Placed at | a tree top, at a real distance | infinity: it never comes nearer |
| Height measured in | metres of lift | `FarHeight`, pixels through the lens at rest |
| Shown when | in front of the camera and at least 2 px tall | in front, within a quarter turn, and its glow reaches the drawn screen (Sun.roc:116-124; Lens.roc:47-49) |
| Path | a hand-shaped arc, by eye | spherical trig: latitude 45°, declination -23.44° (SunPath.roc:23-37, 75-85) |
| Asks of the rider | nothing | nothing |

Both move through the sky, and both follow a curve. The bird's curve is a cheat chosen by eye, a 5 m arc over a straight line. The sun's curve is the one piece of honest astronomy in the game. The sun's cheat is in the clock instead: 1,000 steps an hour (SunPath.roc:89-90).

## Truck and sun

| | Truck | Sun |
|---|---|---|
| Lasts | the whole ride | the whole ride |
| Motion module | `TruckJourney`, stepped | `SunPath`, a pure function of the clock |
| State | `{ route_position, speed, pace }` in `RideInstant` | none |
| Kind | `Truck`, built each frame in `FrameView.ride_facts` | `Sun.Sighting`, built each frame in `FrameView.frame_view_at` |
| Projected by | `raised_point_on_truck`, the camera's pinhole | `Lens.far_point` |
| Through `Pipeline` | yes | no |
| Lit by | the sun: headlights on at sky darkness 0.412 (LitTruck.roc:40-44) | itself |

These are the two whole-ride things, and the design note's point holds here: neither fits the cat and bird's encounter structure. They are linked by a chain: the sun's height sets `Sky.darkness_at` (Sky.roc:20-28), and that darkness turns on the truck's headlights. The truck's look this frame reads both its own last step (`pace`) and the clock, so it is the one kind that depends on two motions.

## What the four share, and where they part

- All four have the same two halves: a motion module for how it moves, and a kind for how it looks this frame. The sun's second half is the odd one. It has no record of facts like `{ pose }`, only a sighting, and its look (`Sun.look`) is worked out from where it lands.
- The kinds hold how a thing looks, and the forms around them hold where it is. Cat, bird and truck go through `Pipeline` as a `Geom.Placed`, a `Sighted` and a `Rendered`. The sun skips `Pipeline` and paints in the backdrop.
- The split by duration is clean. The cat and bird are encounters, one per segment, sharing one `EncounterPlan` that is forgotten at each new segment (RideInstant.roc:67-72). The truck and sun last the whole ride.
- The split by driver isn't the same as the split by duration. The cat and bird are hand of god. The truck is stepped, and the sun is the clock. So the whole-ride pair is two kinds of motion, not one.
- Only `RideInstant` stores motion state, and only for two of the four: the truck's journey and the encounter plan. The sun and the cat's and bird's poses are worked out from the clock and that plan.
- Who reacts to whom differs for each. The rider reacts to the cat only. The truck reacts to the rider every step, the cat and bird once, and the sun never.
- Each has its honest cheat in one place: the sun's `FarHeight`, the truck's tease, the cat's keyframes and the bird's arc. The towers' exaggerated curve isn't the truck's: the truck sinks by the ground's honest curve.
- Depth meets in one sort for three of them, by the forward distance of the foot, with ties broken by `Scene`'s field order. The sun has no depth: it is drawn before the mountains, and the grass covers what has set.
