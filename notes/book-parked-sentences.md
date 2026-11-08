# Book sentences the code cleanup made false

*Started 2026-11-07, while the book is parked. A worklist for when it unparks. Line numbers are `tutorial.md`'s at the time and will drift, so search by the words. The `book_names` gate holds 35 stale backticked names on top of these (The cat 21, The bird 12, What a cat does to the rider 1, Appendix 1); run it to list them.*

## The cat and the bird

- About 158-164: the table gives `pose` and `lift` as `CatSighting`'s fields. They now sit under `kind`.
- 169: "the names say which half is which" is weaker, because the kind lives in the shapes half. The pair for the truck is now `TruckSighting` and `TruckAhead`.
- 171: the "plain record with no drawing in it" is still true, but its `kind` has a picture method.
- 1872: "`CatSighting` and `CatShapes` never import each other... `SceneShapes` is what carries a sighting's answer to the drawing." `CatSighting` imports `CatShapes`, and `Pipeline` carries the answer.
- 1858-1867, dot graph: `SceneShapes -> CatShapes` is gone. `CatSighting -> CatShapes`, `-> Pipeline` and `-> Animation` are missing, and `Animation -> Geom` is new (also about 1699).
- 1874: "An empty list or a list of one" was already false.
- The bird's excerpt `{{code BirdShapes.PosedBird from "feet = Camera.project(" ...}}` is now one line, so check it still earns its place.

## Towers and the truck

- 1045: "Modules: `Steps`" under New in this chapter. `Beacon` is new there too.
- 1055: `SceneShapes -> TowerSighting`. `SceneShapes` no longer imports it.
- 1059-1060, beacon diagram: `TowerSighting -> Steps` and `-> Fraction` are gone. It needs `TowerSighting -> Beacon`, `Beacon -> Steps`, `Beacon -> Fraction`.
- 1088: "`beacon_brightness` on a `TowerSighting`" is now a field of `Tower`. "A beacon's blink is decided in the same place as whether the tower is in view at all" is false: the rules live in `Beacon`.
- 1643-1644: `SceneShapes` no longer imports the truck's picture module directly.
- 1664: "`TruckAhead` leaves the painting to two modules" needs a look after the rename from `TruckPicture`.
- The `mid_tower` include now shows `MidTowerFate`, and `tower_if_ahead` shows the `kind:` nesting, with no prose about either.

## Elsewhere

- 484: `OutOfView` for a tree was already false.
- 2156: says 79 modules, and there are 83. `Geom`'s importer count in the table says 20, and it's about 31.
- The items already parked in the project memory: Pond, `TreeAhead`, TreeSighting as a type, `{{module Conifer}}` showing `scenery_picture` early, `where` in the tree chapter, the glossary's "cutouts", the truck's lead table.

## The drawing substrate

- 290: the empty-list example, "`Ground.patch_shape` knows...". It answers a `Try` now.
- 637: "`pack` gets there with method calls ... `shl_wrap` and `bitwise_or` ... That makes `pack` a leaf". It calls `pack_rgb`.
- 656: "A range is highest in its middle" was already false.
- 670: "`snow_color` uses the sky's own `color_between`". It's HexColor's now.
- 718: "`before` and `after` say where the two segments lie". There is no `after` field; `BendView.place_after(bend)` answers it.
- 2312: "`Ground`, `GuardRail` and `TruckShape` call it the same way...". Only `Camera.clipped_polygon` calls it.
- The sky chapter now quotes HexColor, and the Mountains chapter still lists it as new.

## Location out of kinds

- "Those two lives are two records, and each says where the tree stands in a different way", with its table row saying `Sighted` is `right` and `forward`. `Pipeline.Sighted` also holds the road place.
- The table under "This is what `CatSighting` answers" lists `right`, `forward`, `pose` and `lift`. The record also has `place`, `along` and `across`.
- `Sighted` moved from `Geom` to `Pipeline`, and `sighting_of` split in two: `tall_sighting_of` adds the size test.

## The object half's fixes

- About 1233: "`Ahead(position)` is a tag carrying a payload…" now sits beside `{{code TowerSighting.end_tower_of}}`, which shows `place: in_view.place`.
- 169 and 171: `CrossingSighting` and `PosedCat` don't pair by name, and `CrossingSighting` finds birds too.
- 2023: "`CrossingSighting` and `PosedCat` never import each other" is false.
- 2052: `CrossingSighting` is listed as new in the bird chapter; the cat chapter introduced it.
- Dot diagrams around 97-104, 1844-1846, 2008-2018 and 2060-2065 still name CatSighting, CatShapes, BirdSighting and BirdShapes. book_names doesn't read diagrams.

## The opaque point type

A sighting holds `foot : Geom.AheadPoint` in place of `right` and `forward`, and `Picture.Setting` carries `foot`. False in Nature types and the tree chapters: the `Pipeline.Sighted` and `Picture.Setting` rows and the Sighted box's label; "hands the sighting's `right` and `forward`"; the `TreeAhead` row; "The tree's `right` and `forward` go on to `tree_picture`"; "`{ ..tip, height: Distance.zero }`", now `tip.at_height(Distance.zero)`; `tier_shape`'s guard, now gone; the ring and `base_height`, now in `cone_ring_points`; a spot exactly on the near plane is now in view; `PosedBird`'s feet are `foot.at_height(bird.lift)`; a clipped list is a list of `Geom.AheadPoint`.

## From the Pigs split (Pig, PigHerd, the route's herds in World)

- tutorial.md:1161, "Modules: `Pigs`": the module is gone, and it's now `Pig` and `PigHerd`, with the route's herds in World.
- tutorial.md:203 and 210, the diagram edges `World -> Pigs` and `Pigs -> Scenery`.
- The prose after `{{code Pig.pig_billboard}}` (formerly `Pigs.pig`) still says "two places, an emoji, a height and a way to face", but the billboard holds no places.
- The paragraph after `{{code PigHerd.herd_pigs}}` describes a three-branch match on the rider's interest, which never matched that code.
- `PigInterest` is now `World.PigInterest`, and `PigPresence` is `World.PigPresence`.

## From the truck cleanup (TruckAhead holds the lights, Truck is its state)

- `Truck.truck_state_at_next_step` at tutorial.md:1483, 2647 and 2807: now `Truck.at_next_step`.
- `TruckState` at 1840 and 2647: the state is now `Truck` itself, and `brake_lights` is `pace : [Slowing, NotSlowing]`. The prose near 1840 still calls `brake_lights` the truck's state.
- `Truck.Lights` at 1875: the lights are `TruckAhead`'s own fields.
- The diagram at 1867 still shows `TruckAhead -> Truck`, which is no longer an import.

## From the Tower cleanup

- `{{code Tower.rod_shapes}}` now includes `Geom.ahead_line`, the near-plane cut of a line. The prose after it still describes the four-way match, which still holds.

## From the Conifer cleanup

- `TreeShapes.TreeAhead` at tutorial.md:456, in the types table: deleted. `tree_picture` now takes the `Picture.Setting` whole, plus `{ height, foliage_color }`.
- tutorial.md:498: "the bars take the setting apart ... in the record that function wants" describes the old `scenery_picture`. Every name still exists, so the lint can't see it.
- `Trees.distance_from_middle` is now `Trees.tree_line_distance` (include repointed).
- `TreeOutline` is `{ foot : Screen.Point, height : Pixels }`. Any prose naming `base_x`, `base_y`, `height_px` or `crown_top_y` as fields is stale.

## From the billboard cleanup (Species, CowHerd, segment descriptions)

- `Cows` at tutorial.md:1176 and in the diagram at 202, 207 and 208: the module is now `CowHerd`, with the route's herd in World.
- `inward` at 1134: Wildlife picks left or right of the middle instead of a float sign.
- "Both herds are worked out once, when the world is built" is no longer true: `World.segment_cows` and `segment_pigs` place them when asked, and the segment holds only `bull` and `pig_herd`.
- Each kind's look is a `Billboard.Species` (`codepoint`, `adult_height`); young ones are `Billboard.young_billboard`, half height.

## From the cat and bird cleanup, and the Geom cleanup

- `BirdFlight.BirdPose` at tutorial.md:2197: now `PosedBird.BirdPose`. `Cat.CatPose` is now `PosedCat.CatPose`; each kind owns its pose and its pose-to-still match.
- `Sits` at 2215: the bird's habit is `{ perch, leaves_for : [FliesTo(tree), StaysPut] }`.
- The diagrams near 1919, 2091 and 2138 still draw `CatStills -> Cat` and `BirdStills -> BirdFlight`; those edges are now wrong (the checker doesn't see edges).
- 1935: `cat_in_view` no longer adds the gap itself; `CrossingSighting.crossing_in_view` does, for the cat and the bird.
- `Geom.ground_curve_radius` at 2512: the earth's curve is in Ground now (`Ground.ground_curve_radius`, `Ground.ground_drop`).

## From the spot lane

- tutorial.md:380-381 describe `Sighted` and `Setting` by their old fields; both now carry a `spot`.
- tutorial.md:390, a diagram, lists "place, along, across, right, forward, kind".
- tutorial.md:639: a tower now reads its place and road point from the spot, and its context is only the road.
- `RoadAhead.Position` at 2442: now `SegmentPlace.Position`, in a module of its own below World.
- `Animation.Spot` is now `Animation.Location`; "spot" means only the sighting's `Spot`.
- The glossary has a Spot row, and its Sighting and Placed rows were updated (the one prose change made on purpose).

## From the kinds lane (LitTruck, Green, the still as the value)

- `TruckAhead` at tutorial.md:169, 1794 and 1887, and in diagrams at 1804, 1866 and 1867: now `LitTruck`.
- `BigGreen` at 373, 454, 494 and 496: now `Green`.
- 1163: a critter's codepoint no longer "finds its still" through a match. Each kind names its `EmojiStills.EmojiStill` directly.
- Near 2480: the prose says `PosedBird.scenery_picture` calls `Camera.project`. The still is now drawn on its feet by `StillShapes.standing_anchor` and `standing_still_shapes`, for the cat, the bird and the billboards alike.

## From the rider lane (Motorcycle, RiderEyes, Gawking, one Limit)

- `Bike` (tutorial.md:1546-1578, 2329, 2416, 2637, and the diagrams at 1466-1570 and 2403-2406): now `Motorcycle`, with `RiderEyes` beside it in `RiderState`. `Bike.Motion` (2281, 2333, 2808) and its "others" fields are gone: Motorcycle holds the six fields the physics reads and writes, and `segment_index` stays on RiderState.
- `Bike.bike_motion_at_next_step` (2322, 2329, 2353): now `motorcycle_at_next_step`, taking a `LeanChange` and an acceleration. `Bike.with_lean` (1522, 2337) is `Motorcycle.with_lean`.
- `NoAcceleration` and `MayAccelerate` (1632, 2285): the limits are one shape, `VehicleLimits.Limit : [NoLimit, AtMost(Acceleration)]`, folded with `min`.
- `bend_brake`, `crossing_limit` and `pig_limit` (1640, 1648, 1757, diagrams 1621 and 1701): `pig_limit` is gone (`Gawking.gawk_brake`), and the crossing gives `CrossingReaction.crossing_throttle`. `CrossingReaction.reaction_to` (2281) is split into `crossing_throttle` and `crossing_attention`.
- `Throttle.shoulder_brake_at` (2541) is private; Throttle's only public function is `acceleration`.
- A lean minus a lean is now a `LeanChange` (`Lean.change_from`), not a Lean.

## From the lib lane

- Near tutorial.md:2739, "builds a camera out of nested tags and puts it at the front" is loose now: `SafariApp.lean_space` builds a `Shapes.Space`, and `Shapes.in_space` wraps the frame's shapes in it. The include is repointed.
- `lib/View` is `lib/Eye`, and `lib/Color` is gone (RgbColor and ArgbColor hold colors). `Camera.view` is `Camera.space`.

## From the SceneShapes lane

- tutorial.md:713 says the tree count "wraps around past 65,535" (`to_u16_wrap`). It now crashes by name instead.
- `ThingLists` and `things_in_tie_order` are gone: `SceneShapes.scene_renderings` gives the things far to near, with the tie order written once. The rail's rendering is `GuardRail.quad_rendering`.
- TreeSighting's and TruckSighting's expects live in their own modules now.

## From the units lane

- tutorial.md:1291 says `Clock.minus` turns two clocks into Steps and that Clock has no `plus`. Now `Clock.steps_since` does that, and `plus` and `minus` take Steps. Line 1301's `clock.minus(Clock.start)` is `clock.steps_since(Clock.start)`.
- `complement` (518) is `Fraction.less`, and `ratio_to` (1435) is `portion`, on Distance, Pixels, Turn and Speed.

## From the World split, stills, widget-kit and polygon lanes

- `World.segments`, `World.plans` and `World.SegmentIndex` (189, 1499, 2441, 2498, 2815): the route is `World.route : Route`, the plans are `World.segment_plans` (with `bending_plans` and `last_plan`), and the index is `Route.SegmentIndex`. The segment is `Segment` in its own module, and its ending is `[Bends({ turn, bend_life }), RouteEnds]` (1518's `Continues`). `MidTower` (1028) is `Segment.has_mid_tower`.
- `Stills` and `StillPolygon` (1069, 1111, diagrams 2139-2140): `Still := List(Still.Polygon)`, with `Still.Vertex` and a gradient tag.
- tutorial.md:316: "The triangle takes two arguments: a color, and a record of three corners" has the order backwards now: the corners come first.
- `Detail` (177, 590): its tree thresholds are TreeShapes' own, and the smallest height on screen is Pipeline's.

## From the boundary, stills, follow-ups and widget-game lanes

- About 728-730: "Modules: `Backdrop`" and "`Backdrop` paints what's behind the ride". Backdrop is gone; Sky, Sun and Grass own their shapes, and `Grass.grass_top_y` and `grass_shape` moved out of Screen.
- About 2337: the loop has "`$low` and `$high` closing in on each other". It now uses `$bounds` (`LeanSearch.search_tries`).
- About 469: the `TreeShapes.tree_outline` row now takes a `Spot`.
- Billboard's still field is `emoji`, and so is `Billboard.Species`'.
- About 1826: "Finding the next turn shows a list pattern... Recursion walks the list, carrying where the current segment starts." `Truck.next_bend` is now a `find_first` over `Route.segments_with_ends`; no list pattern is left. The include was repointed to `Route.segments_with_ends`.
- About 1830: "It's called through a smaller function, which supplies the 0 so nobody else has to." `next_bend_on` is gone.

## From the Scene lane (SceneShapes folded into Scene; the scene holds renderings)

- :175 "`SceneShapes` renders each one through `Pipeline.rendering_of`", :707 "So `SceneShapes` counts them", :2095 "`SceneShapes` is what carries a sighting's answer to the drawing", :1311 "neither `Tower` nor `SceneShapes` imports `Clock`" (Scene imports Clock).
- The module list (:123) and diagrams (:103, :662, :666, :1277-1279, :1862-1866, :2082-2084) still name SceneShapes.
- Includes repointed: `Scene.tree_renderings`, `Scene.nearer_tree_count`.

## From the ground lane (GroundPatch split out; Ground is the earth's curve)

- :332 "A `Ground.Patch` is a patch of ground … So `Ground.patch_shape` answers a `Try`": both live in `GroundPatch` now (include repointed).
- :959 "That's what `Ground` paints": GroundPatch paints.
- Lines 912-975 were already stale: `BendView`, `bend_patches`, `on_map`. `BendInView.inner_edge` is gone too.
- Ground is now `EarthCurve` (the earth's curve, one of the "honest cheats"): :253, the 923 diagram (`GroundSighting -> Ground`), :959 and :2535 still say `Ground`.

## From the sky-frame and Scene-reaction lanes

- `Sky.dusk_at` is `Sky.darkness_at` (:848, :1403, :1407, :1441); :893 the rock darkens "with `dusk`", now `darkness`; `Sky.sunset_warmth` is `horizon_warmth_at` (:1425, :1431, the :1365-1370 dot graph, already stale with `Sun.height_px`); `Sun.height` is `height_at`; `Lens.cam_focal` is `focal_for`.
- :1879 RideInstant puts the lights together: `LitTruck.at` does. :1383 Tour hands the clock to Sun and Sky (already stale).
- FrameView now holds `backdrop` and `ride_shapes`; Screen has `drawn_left`/`drawn_right`/`margin_rect`, with no `width_with_margins`.
- `EncounterPoses` is new (the animals' poses from the ride's plan, with no camera); EncounterSighting is camera work only; Scene's truck is `trucks`, a list of zero or one. The parked names-every-module check will want EncounterPoses and EncounterSighting.

## From the route-tour, scenery-types and opaque-cheap lanes

- "A fixture is a value": "it also trims the list of past instants. An `if` chain does the trimming…". `step_forward` is now a two-arm match on `[Continued, Restarted]`, and the trimming is in `past_instants_after`. The quoted `next_or_restart` returns those tags too.
- :1130 `Wildlife.bend_critters` is now `bend_billboards`. The glossary (:2860, :2863) defines a billboard as "A critter that…"; Billboard.roc now says "an animal that stands in one place and always faces the camera".
- :2043 "`Timeline` is nominal … unlike an opaque type anyone can build one", :2058 "opens the nominal type", and :2199 "wraps a record in the nominal type" are false: Timeline is opaque, built with `Timeline.of`. :433 "the rails make their `Rendered` by hand": now `Rendered.of`. Still, GroundPatch, Beacon and BendInView are opaque too.

## From the units and boundary-moves-2 lanes

- tutorial.md:1644 `allowed_speed` "holds the speed between rest and the top speed": only to the top speed now (a Speed is never negative).
- 1512 lists `CanvasRoll` (folded into RiderCamera); 1540 "The last `expect` is a table of pairs…" refers to a listing the page no longer shows; 2737 "`SafariApp.frame_shapes` builds a camera out of nested tags" (`FrameView.lean_space` does) and "The rest is `Tour` answering questions"; ~2484 the lens passage presents `focal_for_lean` and `focal_for` as Lens's (they're RiderCamera's; it already named a nonexistent `RideFocal.ride_focal`); 610 introduces the hull from TreeShapes (it's `ConvexHull`'s).

## From the small-rules lane

- tutorial.md:769 "`scale` is how large the sun is drawn, because a wider view makes it look smaller": `Sun.Place` holds `cam_focal` now, and `Lens.size_on_screen` draws a resting-lens length. `Lens.x_for_turn`/`turn_at_x` moved to Camera; `Geom.herd_front_distance` is gone (each herd owns its own).

## From the shell-tidy lane

- ~:1241 "the model, which is the `Tour` and a pause flag": it's `motion : [Playing, Paused]`. ~:2720 "moving four steps or one … is one helper with a function in a record field" and ~:2724 "`Tour.step_forward` and `Tour.step_back` are plain values to pass here": it's `Tour.steps_forward`/`steps_back`. Tour is opaque (`instant()`, `route()`, `past_instant_count()`); `Tour.at_next_segment` replaces SafariApp's `next_segment`.

## From the truck-draw lane

- ~1842 "`TruckSighting` calls the distance to the truck `lead`": there's no `lead`; TruckSighting places the truck with `RoutePlace.at_distance`. Truck points are in the truck's own frame; `TruckLights.brake_light_shapes`/`headlight_beam_shapes`; `Truck.Pace`; `LitTruck.at` takes a Pace. Already stale: ~1826, ~1840, ~1879, ~1887.

## From the geom-tidy lane

- ~:478-479 and :506 "`tree_outline` calls it twice…" and the `tree_outline -> Camera.project` graph edge: it's `Camera.upright_on_screen` now. ~:2478 "`PosedBird.scenery_picture` calls it with a record built on the spot for the bird's feet": the include is `Camera.upright_on_screen`; `StillShapes.Anchor` says `foot`. ~:600 names `Geom.near_plane`, now private. `Spot.straight_ahead` is gone.
- tutorial/fails/rider_point_as_road_point.roc names `Geom.to_rider_point` (now private in RoadAhead): the example fails with "does not exist" rather than the error it's meant to show.

## From the rider-step and route-place lanes

- The rider's step is `RiderState.next` and `is_finished` (not `Rider.rider_state_at_next_step`, at 1483, 1584, 1657, 1709 and the 2809 table); the mind is `Rider.controls` (not `Rider.decide`, at 1584, 2295, the 2319 dot label and 2349).
- The motorcycle holds a `RoutePlace { segment_index, along, across }`; RiderState is `{ motorcycle, eyes }`. 1499 lists `segment_index`, `along` and `across` as rider fields. 1514 "Count the opaque types…" no longer describes RiderState. 1526 and 2813: the crossing is `Motorcycle.cross_bend_if_on_road`. 1530 "record update does most of the writing in this module": `stopped_at` is Motorcycle's.

## From the whole-history, one-frame and one-size lanes

- Tour now keeps the whole ride (no cap, no halving; a restart clears it). :2590 "it also trims the list of past instants. An `if` chain does the trimming…" and :2629 "at depths either side of the history's cap" are false.
- `Animation.Timeline(frame, pose)` holds the choreography list plus a `frame_instant` function, and builds only the frame asked for. :1929 "A timeline is a record of what the cat does at each point", :1982 "all it does is build a record…", :2027 and :2049 "A timeline is data", and :2043 "`Timeline(pose, lift)` takes two type parameters" are false.
- `Pipeline.tall_sighting_of` is folded into `scenery_sighting_of`, and billboards are size-tested through the camera's lens: :393 and the 660-661 diagram, :429, :699 and :701.

## Steve, 2026-11-07: rewinding isn't free

Wherever the book suggests stepping back is free, say what it costs. Tour keeps up to 2048 past `RideInstant`s (a few hundred KB; at least 1024 kept, dropped half at a time), stepping back pops one, and each frame is redrawn from its instant, never stored. A restart clears the history. "Cheap, because a frame is its state redrawn" is the honest claim.

## From the color-shade lane

- HexColor is now `ColorShade` (`shade_color`, `color_between`), and the channel readers are lib's `RgbColor.red`/`green`/`blue`/`from_channels` (which checks each channel). :844 "`HexColor.Rgb` is a plain record alias…" (already false), :860 "`pack` … is a leaf: it calls nothing of Safari Ride's own" (the include is now `from_channels`), :873 "Modules: `Mountains`, `HexColor`", :1340 the `HexColor.Rgb` table row.

## From the segment-world, dead-lint and widget-tidy lanes

- :222 "`[WithBull, NoBull]` is written right in the field's type … with no declaration": it's `CowHerd.Bull` now. `Segment.Ending`, `Segment.Pigs` and `Segment.PlannedEncounter` are named too; `Segment.segment_ending` is the total accessor.
- :2221 `{{code Segment.fifth_left_tree}}` still expands, but shows a private helper.
- :949 "`Geom.line_crossing` finds where the two cross": deleted (it had no caller), with `Geom.Line`.
- "all of `LeanSearch` is 105 lines" (already false; 134 now). `LeanSearch.aimed_across` names the road's middle.

## From the rider-review lane

- ~2341: the search "compares the end of the coast with the target"; it's the road's middle now. ~2345: "Its caller gives the search its bounds"; `search_tries` sets them. ~2353: "all of `LeanSearch` is 105 lines".
- ~1705: "Nothing joins them… neither asks about the other": `desired_gaze` now matches `Gawking.gawked_pig`.
- ~1640: the line of physics used by "this one, `Gaze` …, and `Truck`": the bend and the truck go through `VehicleLimits.braking_to`.
- ~1584, ~1588: `{ ..s, lean }` and `s.yaw.plus(...)` are `motorcycle` now. The gaze "eases back" is "turns back" (`TurningBack`).

## From the animation lane (option C: animals on their own clock)

- Roughly 1929-2291 and 2808/2845: `Approach` feeding `Cat.instant_at`, `stage_over_gap`/`stage_over_step_span`, "38 beats tied to no clock", the bird reacting to how close the rider is, a bird that `Sits`, the hanging bird, the feedback loop "why `stage_over_step_span` has to stay the cat's rule", "adding the distance to the segment to get the gap". Every bird flies now, and the start is planned once per segment.

## The Geom split (2026-11-08)

`Geom` now holds the road frame only; the rider's view frame (`RiderPointAhead`, `RaisedPointAhead`, the near plane, `FlatPolygon`) moved to `RiderView`.

- 457: the table names `Geom.RaisedPoint`. It is now `RiderView.RaisedPointAhead`.
- 600: "`Geom` draws that line at its near plane, `Geom.near_plane`". The near plane lives in `RiderView`.
- 2370: "Modules: `Lens`, and `Geom`, `RoadAhead` and `Camera` in full" needs `RiderView`.
- 2390: `Geom`'s row says "Road points, rider points, and how to turn one into the other", and its counts are stale. Rider points are `RiderView`'s.
- 2409-2410, dot graph: `RoadAhead -> Geom` and `Camera -> Geom` need `RiderView` edges.
- 2418: the family "`Geom`, `RoadAhead`, `Camera` and `Lens`" now includes `RiderView`.
