# Safari naming nitpicks

*A reader's list for Steve, dated 2026-11-05, from roc-apps master at fb43c5d. No code was changed and nothing was compiled. Specs and `tutorial/` were left alone. Counts are from the non-spec sources, and they include the expects that sit inside modules. Each new module name was checked as free in `safari/` and `lib/`.*

Items 1 to 16 are renames, ranked by how much each would help a reader who doesn't know the program. Items 17 to 20 are checks for every Roc project, ranked the same way. `name_hunt` is held at zero on safari today, so none of this is caught now.

| # | Now | Rename to | Kind |
|---|---|---|---|
| 1 | `Frame` | `Chain` | Unhelpful module name, one word for two things |
| 2 | `Pose` (three meanings) | `RiderState`, `Geom.Vantage`; critters keep `Pose` | One word for three things |
| 3 | `Tour` | `Ride` | Two words for one thing |
| 4 | `Arc`, `frames`, `no_frames` | `Coast`, with the billion gone | Stale, wrong promise |
| 5 | bend, corner, turn, joint, intersection | bend for the place, turn for the angle | Five words for one thing |
| 6 | `across` from two origins | one origin, or two types | Wrong promise |
| 7 | `tilt` | `lean` | Two words for one thing |
| 8 | `CatItem`, `TruckAt`, `all_rails`, `cow_items` | one shape for every sighting | Several words for one thing |
| 9 | `Render`, `ItemDraw`, `SafariShapes` | `Scene`, `SceneDraw`, `Backdrop` | Unhelpful module names |
| 10 | `Critter`, `Creature`, `Billboards`, `SafariCritter` | `StillDraw`, `Cutouts`, `Wildlife` | Wrong promise |
| 11 | `BirdFlight.Route`, `BirdFlies(Sits(tree))` | `BirdFlight.Habit` | Wrong promise |
| 12 | `Tree`, `RocBird`, `Herd`, mast | `TreeDraw`, `BirdDraw`, `Cows`, tower | Broken family pattern |
| 13 | focus, world, lane, quad and others | one word each | Two words for one thing |
| 14 | stage, `RoadPoint`, `Outline`, approach | a second word for each | One word for two things |
| 15 | leftovers from the retyping | table below | Stale |
| 16 | leftovers from the emitter | table below | Stale |

## The renames

### 1. `Frame` becomes `Chain`

`Frame.roc` isn't about a frame. Its doc says it "finds where the road lies from where the rider is", and its next sentence defines the chain, which is the module's real subject. Everywhere else a frame is the picture of one instant (`SafariFrame`, `RasterFrame`, "in a frame" in every sighting's doc), and in `Critter`'s and `BirdStills`' docs it is a coordinate system ("a unit frame"). `Frame.` is on 164 lines in 20 files, usually in `Frame.ChainPosition`, which holds two nouns and leaves the reader to work out which is the subject.

- `Frame` becomes `Chain`, and `Frame.ChainPosition` becomes `Chain.Position`.
- `Frame.look_ahead` is a constant, "the most segments a chain holds". It reads as an act, so it becomes `Chain.max_length`.
- `Frame.Pose` goes (see item 2).
- Those docs' "unit frame" becomes "units of its height", the phrase `Stills`' doc already uses.

### 2. `Pose` means three things, and only one of them is a pose

| Where | What it is |
|---|---|
| `Cat.Pose`, `BirdFlight.Pose`, `pose` in `Animation` | How a critter holds itself. This one fits |
| `Pose.roc` | The rider's whole state: `Pose.RiderState`, on 52 lines in 7 files |
| `Geom.Pose`, with `Frame.Pose` as its alias | The camera's place and yaw, plus the lane's `half_width` |

A reader learns the word from `Animation`, then meets a module called `Pose` that has no pose in it.

- `Pose.roc` becomes `RiderState.roc`, and `Pose.initial_rider_state` becomes `RiderState.initial`. It stays apart from `Rider` because `Gaze` and `Throttle` use the type and `Rider` imports both.
- `Geom.Pose` becomes `Geom.Vantage`, `RoadView.pose` becomes `vantage`, and `ViewYaw.pose_for` becomes `vantage_for`. The alias `Frame.Pose` goes.

### 3. `Tour` becomes `Ride`

`Tour` holds the current instant and the instants behind it, which is what a ride is. With `RideInstant` in place, a reader looks for `Ride` and finds no such module. The same thing has four names: tour in the code, "journey" in `Tour`'s doc, "drive" in `SafariApp`'s header, and ride everywhere else.

- `Tour` becomes `Ride` (55 lines in 7 files), and `tour` becomes `ride`.
- "Journey" and "drive" go from the docs.
- `RideInstant.next` returns `initial` once the rider has finished, so it promises less than it does, while `RideInstant.step` is the true next instant. `step` becomes `next`, matching `Clock.next`, and `next` becomes `next_or_restart`.
- `Tour.advance` and `Tour.back` aren't a mirrored pair, which `docs/roc-style.md` asks for. They become `step_forward` and `step_back`, matching the gate `StepBack`.

### 4. `Arc`: `no_frames` is a billion, and it isn't frames

`ArcOutcome.frames` is a `Steps`, and `Arc.no_frames` is `Steps.of(1000000000)`. Three things are wrong with that.

- A frame is a picture, and this counts steps of a simulated coast that is never drawn.
- "No frames" reads as zero, and the value is a billion.
- `docs/roc-style.md` cites `no_frames = 1e9` as its example of a number kept to mean none. The one production read, `Throttle.roc:129`, runs only after `has_stayed_on_road` has ruled the billion out, so no arithmetic ever sees it.

The renames:

- `Arc` becomes `Coast`. `LeanSearch` already calls this a coasting arc and the record holds a `coasting_rider`. The word arc also means a bird's path in `Animation.Path`.
- `project_arc` becomes `Coast.project`, `ArcOutcome` becomes `Coast.Outcome`, and `ArcCourse` becomes `Coast.Bounds`, because it holds edges, not a course.
- `shoulder` and `frames` merge into `[StaysOn, Leaves({ side : [Left, Right], after : Steps })]`. That removes `no_frames` and `ShoulderNone`.
- `frame_count` becomes `steps_run`.
- `sim_from` moves the bike and `sim_step` judges where it got to, so the names are the wrong way round. They become `coast_from` and `judge_place`.
- `min_forward_progress` is used as a ceiling (`forward.min(...)`), and reaching it ends the coast as safe. It becomes `clear_distance`.
- `turn_danger_steps` is how long a coast may run. It becomes `longest_coast`.
- `has_crossed` and `start_side` only feed `crossed`, and only expects read `crossed`, so all three can go.

### 5. Where two segments meet has five names

| Word | Used for |
|---|---|
| bend | `Geom.Bend`, `Joint.PlacedBend`, `bend_out_of` |
| corner | `Throttle.corner_brake`, `SafariCritter.corner_critters`, `corner_sightings`, and "corner" in many docs |
| turn | `Truck.ComingTurn`, `Truck.NextTurn`, `TurnAhead`. It is also `Angle.Turn`, an angle |
| joint | `Joint`, `joint_apex` |
| intersection | `VehicleLimits.approach_intersection_dist`, though the road has no intersection |

The rule I'd adopt is that a bend is the place, a turn is its angle, and a corner belongs to a polygon or a footprint, which is where most of the word's 296 code uses already are.

- `Joint` becomes `BendView`, and `Joint.PlacedBend` is that module's own type, in the pattern of `RoadView`. `joint_apex` becomes `BendView.apex`.
- `Truck.ComingTurn`, `NextTurn` and `TurnAhead` become `ComingBend`, `NextBend` and `BendAhead`.
- `corner_brake` becomes `bend_brake`, `corner_critters` becomes `bend_critters`, and `corner_sightings` becomes `bend_sightings`.
- `approach_intersection_dist` becomes `bend_approach`.
- `Frame.bend_out_of` and `Joint.bend_out_of` share a name and return different types. The second becomes `BendView.of_segment`.

### 6. `Across` has two origins inside one type

`Across`'s doc promises that places can't be confused, then says a place is measured from one of two origins. `Across.middle` and `Scenery.left_edge` are both 0.0, both typed `Across`, and they mean spots two metres apart. A forgotten `Scenery.from_left_edge`, which has 8 calls in 6 modules, compiles and draws in the wrong place. Its name also describes the result, while reading as if it describes the input.

- The better fix removes the second origin: `Geom.RoadPoint` measures from the middle of the lane, as the rider does. `from_left_edge`, `Geom.Pose.half_width` and the 0.0 `left_edge` all go. `(x + half) - (y + half)` may round differently from `x - y`, so the frame hashes have to judge this.
- If the hashes refuse it, give the second origin its own type, `Geom.FromEdge`, made only by `Across.from_edge`. Then a forgotten call is a compile error, and the name says which way it goes.

### 7. `tilt` becomes `lean`

`Angle` defines one word, lean, for this angle. The type is `Angle.Lean`, and the word tilt still has 115 code hits. The two meet at `Rider.roc:126`, in `{ lean_step: dec.tilt_step, ... }`, where one value changes names as it is passed.

- `RiderState.tilt` and `Bike.Motion.tilt` become `lean`.
- `tilt_step` and `lean_step` become one `lean_step`.
- `with_tilt` becomes `with_lean`, and `Throttle.tilt_hold` becomes `lean_hold`.
- `Bike.yaw_per_tilt` becomes `turn_per_lean`.
- `max_tilt_correction` becomes `max_lean_change`.
- `best_tilt_correction` returns a lean, not a correction, and `Rider.decide` has to subtract to get the change. It becomes `best_lean`.

### 8. Every sighting should have the same shape

Today's `XSighting` modules are one idea, but each spells its answer differently.

| Module | Finds | Depth keys | Its answer's type |
|---|---|---|---|
| `CatSighting` | `in_view` | `depth_keys` | `CatItem` |
| `TreeSighting` | `in_view` | `depth_keys` | `TreeItem` |
| `TowerSighting` | `in_view` | `depth_keys` | `TowerItem` |
| `BirdSighting` | `in_view` | `depth_keys` | `RocBird.PlacedBird` |
| `TruckSighting` | `in_view` | `depth_keys` | `TruckAt` |
| `RailSighting` | `all_rails` | `depth_keys` | `GuardRail.RailPoly` |
| `CritterSighting` | `sightings` | `cow_items` | `Billboards.Billboard` |

- `all_rails` becomes `in_view`.
- `CritterSighting.sightings` becomes `in_view`.
- `cow_items` becomes `depth_keys`. It handles every critter, not only cows, and its doc says so.
- `Item` is a container word in the style guide's own sense. A `CatItem` is a sighting of a cat, so the module's own type can carry it: `CatSighting.in_view` answers `List(CatSighting)`, as `Tour := {...}.{...}` does. The same goes for `TreeSighting`, `TowerSighting` and `TruckSighting`. `BirdSighting` needs its record moved out of `RocBird`, which reverses one import.
- `Sky.SunPos`, `Sky.sun_pos` and `sun_position` hold `[InView(...), OutOfView]`, which is a sighting by today's rule. They become `SunSighting` and `sun_sighting`, and that also retires the abbreviation.
- `TowerSighting.View`, `TruckSighting.View` and `Frame.Viewpoint` all mean "what this is seen from", so they should share a word. `View` and `Viewpoint` differ only by accident: use `Viewpoint` for all three.

### 9. `Render`, `ItemDraw` and `SafariShapes` don't say what they do

- `Render` renders nothing. Its doc says it "gathers what one frame shows", and its one function is `collect`. It becomes `Scene`, with `Render.Scene` as the module's own type and `collect` as `Scene.in_view`.
- `Render.MovingParts` holds a speed, a clock and the truck, and a speed isn't a part. It becomes `Scene.RideFacts`.
- `ItemDraw` paints the scene, and `Item` says nothing. It becomes `SceneDraw`.
- `SafariFrame.Scene` in the gates is a second `Scene`. It becomes `SafariFrame.Picture`.
- `SafariShapes` knows what's behind the ride, as its doc says, and every module here is Safari's. It becomes `Backdrop`, which pairs with `gates/BackdropPixels`.
- Three functions are called `frame`, and each gives something different. `RideInstant.frame` gives the ride's shapes and becomes `RideInstant.shapes`. `SafariShapes.frame` puts the backdrop behind them and becomes `Backdrop.behind`. `SafariApp.frame` stays, because `CanvasApp` names that field.
- `SceneLimits` holds three drawing thresholds and has no doc. It becomes `Detail`, which frees the word scene.

### 10. `Critter`, `Creature`, `Billboards` and `SafariCritter`

- `Critter.roc` draws stills, including the bird's, and `Scenery.Critter` is a placed animal. `Animation` calls cats and birds critters, while `CritterSighting` and `Render.Scene.critters` mean every animal except those two. So the word has three scopes.
- `Critter.roc` becomes `StillDraw`.
- `Billboards` is the worst fit. On a road, a billboard is an advertising hoarding, and this module has none. The graphics sense of the word is exact, but a newcomer won't reach for it. It becomes `Cutouts`, with `Billboard` as `Cutout`: a flat figure standing by the road.
- That also solves the scope problem. `CritterSighting` becomes `CutoutSighting`, `Scene.critters` becomes `cutouts`, and "critter" keeps the broad meaning it has in `Animation`.
- `Billboards.Sighting` holds `[InView, BehindCamera, TooSmall]`, which is a result, not a sighting. It becomes `Cutouts.Placement`.
- `Scenery.Creature` counts `DuckPond` as a creature, and `NoCreature` as one too. It becomes `Scenery.BendLife : [Quiet, Animal(...), DuckPond]`, and `exit_creature` becomes `bend_life`.
- `SafariCritter` uses safari to mean wild animals, where `SafariShapes` and `SafariApp` use it to mean this program. It becomes `Wildlife`, and `safari_reach` and `safari_sightings` become `wildlife_reach` and `wildlife_sightings`.
- `Scenery.Critter.face_right : Bool` becomes `facing : Cutouts.Facing`, the type the same value turns into later.

### 11. `BirdFlight.Route`: a bird that flies while sitting

`World.Segment.crossing` holds `BirdFlies(BirdFlight.Route)`, and a `Route` is `[Flies(...), Sits(...)]`. So `BirdFlies(Sits(tree))` is a value `crossing_among` can build. I didn't check whether any segment of the real route reaches it. Route is also the road's word, and the word has 96 code hits in all. The plan record calls the same case `BirdCrosses`, which is a third name, and a sitting bird doesn't cross either.

- `Route` becomes `Habit`, from its own doc, "what a segment's bird does".
- `route_from` becomes `habit_from`, and `route_instant_at` becomes `habit_instant_at`.
- Both tags become `BirdHere(BirdFlight.Habit)`, in `World.Segment` and in `SegmentPlan`.

### 12. The family pattern breaks in four places

`Cat` and `CatDraw` teach that the bare noun holds the rules and `XDraw` paints.

- `Tree` draws one tree and `Trees` plants them, with one letter telling the two apart. `Tree` becomes `TreeDraw`, and `Trees` stays beside `Pigs` and `Cows`.
- `RocBird` is the bird's `CatDraw`, and it's the one member of the family not spelled `Bird...`. It becomes `BirdDraw`.
- `Herd` is cows only, and `Pigs` has a herd of its own (`fill_pig_herd`, `big_herd_cols`). It becomes `Cows`.
- Docs say mast 42 times and tower once, and code says tower 165 times and mast 73 times. A lattice on four legs is a tower, so tower wins. `Tower.Mast` becomes `Tower.TowerInView`, matching `Tree.TreeInView` and `TruckShape.TruckInView`.

### 13. Two words for one thing, the smaller cases

| Now | Rename to | Why |
|---|---|---|
| `RiderState.focus`, `Cat.focus`, `focus_peak`, `focus_ramp_down`, `Gaze.gaze_focus`, `focus_decay`, `eye_pull` | `attention`, `peak_attention`, `attention_fade`, `gaze_attention`, `attention_decay` | The type is `Attention`, and focus sits beside `focal` in `Lens`, where a reader takes it for the camera's. `Pigs.PigAttention` is a third thing and becomes `PigInterest` |
| `world`, `route`, `segs`, `w`, `road_segment` | `route` for the built `List(World.Segment)`, `World.plans` for today's `World.route`, `segment` for one | `Tour`'s doc calls its `world` field "the route", and `World.route` is a different list, of plans |
| `lane_width`, `lane_half_width`, `Pigs.road_edge` | `road_width`, `road_half_width` | The road has one lane. `Pigs.road_edge` is literally `lane_half_width` under another name |
| `Sky.sky_color`, `Tour.sky_top`, `sky_top_color` | `sky_top_color` throughout, and `sky_horizon_color` for its partner | One value has three names on its way to the screen |
| `GuardRail.RailPoly`, `quads_along`, `rail_quad`, `max_rail_polys` | `RailQuad`, `max_rail_quads` | The docs and the functions say quad |
| `RailPoly.forward`, `TruckFace.depth` | `forward` | Both are the mean of a polygon's distances ahead |
| `Gaze.gawk_engaged`, `GazeBrake.engaged` | `is_gawking` for both | It answers a Bool, and the second is the same fact |
| `tire` in code, tyre in docs | `tyre`, or `tire` in the docs | The docs' spelling, colour and centre, disagrees with `color` and `center`, so pick per word |

### 14. One word for two things, the smaller cases

| Word | Its meanings | Rename |
|---|---|---|
| stage | `Animation.Stage`, a lattice storey in `Tower` (`stage_height`, `brace_stages`), and the crossing's parts in `Cat`'s doc | `Tower`'s becomes `storey`. `Cat`'s doc says "parts" |
| `RoadPoint` | `Geom.RoadPoint`, and `TruckShape.RoadPoint`, a point on the truck with a height | `TruckShape.TruckPoint` |
| `Outline` | `Tree.Outline` is a tree's size on screen. `Tree`'s docs also say outline for a hull | `Tree.TreeOnScreen` |
| approach | `Animation.Approach`, and `GroundSighting.approach`, the road before a bend | `GroundSighting.lead_in`, `lead_in_length` |
| `segment` | `RiderState.segment` is an index, and `segment` elsewhere is a `World.Segment` | `RiderState.segment_index` |
| `Anchor` | `Critter.Anchor` and `CatDraw.Anchor` are near copies, with `screen_point` in both | The word is right, but `CatDraw` should use the one in `StillDraw` |
| `SpacePoint` | Reads as a point in the world, and is relative to the rider | `Geom.RaisedPoint`, beside `RiderPoint` |
| `earth_radius` | `Tower.earth_radius` is 20,000 and `Geom.ground_radius` is 100,000, and both docs say the earth | `Tower.mast_sink_radius` |

### 15. Left over from today's retyping

| Now | Rename to | Why |
|---|---|---|
| "The truck a frame on", three times in `Truck.roc` | "one step on" | The truck moves by the clock, and frames play no part |
| `RailSighting.leg_steps`, `evenly_spaced`'s `steps` | `leg_pieces`, `pieces` | These are spatial pieces of a rail, not steps of the clock: the same catch as `Beat` |
| `TowerSighting.mid_tower_beacon_step : U32` | `mid_tower_key_offset` | Its doc says it's a key offset |
| `Herd.bull_dist : Along` | `bull_along` | It's a place, and `Cat.cat_along` is the model |
| `TruckSighting.truck_from`'s `remaining : Along` | `along` | A remaining amount is a length, and this is a place |
| `route_position`, `rider_distance`, `segment_start`, `distance_along_route`, all `Distance` | a new type, `RoutePlace`; `rider_place`, `segment_start`, `route_place` | These are places typed as lengths, on 18 lines for `route_position` alone. The design table has `Along` for a segment and nothing for the route |
| `Along`'s doc, "from the segment's start" | "from an origin its holder names" | `Animation.Spot.along` is from a home, and `Pond.PondPt.along` from a corner |
| `Angle.Turn.fraction_of : ... -> F64` | `ratio_to` | It can go negative, so it isn't a `Fraction`, and `Distance` and `Beats` call this `ratio_to` |
| `ViewYaw.head_yaw_frac` | `head_turn_per_lean` | It's a rate, and it goes in the same `steer` as item 7's `turn_per_lean` |
| `cab_axle_fraction`, `cab_roof_fraction : F64` | keep the names, type them `Fraction` | Their values are 0.55 and 0.3, and the name promises the type |
| `Looks.count`, `BirdFlight.wing_flaps`, `Cat.strides_in`, all F64 | `U32`, converted where it's used | Each is a whole number by its doc |
| `Steps.one_step` | `Steps.one` | It sits beside `Steps.zero` |
| `PigLook.dist` | delete, and make `PigLook` a tag | It's read only by expects, and `no_look` needs a placeholder for it |
| `Beats`, as a place and as a length | a question for you: `Beat` for a place, `Beats` for a length | `Clock` and `Steps`, `Along` and `Distance`, and `Bearing` and `Turn` all split the two. `at_beat : Beats` is the visible seam, and two places can be added today |

The `_px` names aren't stale yet: `Pixels` hasn't landed, so they carry the only unit there is.

### 16. Left over from the emitter

| Now | Rename to | Why |
|---|---|---|
| `Num_`, `round_real`, `floor_real`, `exp_real`, `mod_real` | `Float`, `round`, `floor`, `exp`, `mod` | The underscore says nothing, and real is Codex's word for F64 |
| `VehicleLimits.a_accel`, `v_base`, `v_max` | `cruise_acceleration`, `base_speed`, `top_speed` | These are physics letters from before the types. `Truck.top_speed` shows the plain word |
| `Throttle.get_forward_accel_decel` | `Throttle.acceleration` | It's one `Acceleration`, of either sign |
| `Throttle.clamp_v` | `allowed_speed` | It answers a speed, and `v` is a physics letter too |
| `Bike.simulate_rider_step` | `Bike.advance` | The doc says the bike, and `Rider` and `Truck` both say `advance` |
| `Rider.rider_state_for_next_segment`, `resolve_cross`, `finish_clamp` | `on_next_segment`, `cross_if_on_road`, `stop_at_route_end` | Each says less than the act it does |
| `eq_Shoulder`, `eq_Scheme`, `eq_Creature` | delete | They have no callers in safari, and their name breaks the snake case around them |
| `# X -- originally emitted from Codex` on 7 modules | a plain top comment | It's history, which `CLAUDE.md` §11 keeps out of code. `Arc`, `Num_`, `SceneLimits`, `Scenery`, `Throttle` and `VehicleLimits` have no doc at all as a result |
| `SafariApp`'s `**THIRTY, BY EYE.**`, "per tick" | a plain sentence, "per step" | Tick is another word for the step, and the caps header is what the comment style rules out |

`Scenery` also holds the road's width and edges, which a reader wouldn't look for there. Once item 6 is settled, those belong in a small `Road` module.

## The checks

Each should have plants and be held at zero, as the other hunts are. Ranked by what it would have caught here.

### 17. A vocabulary gate: `cookbook/roc/vocabulary.shale`

**The rule.** A repo keeps a file of decided words, and no identifier or comment may use a word it retires.

```
# canvas_apps/safari/vocabulary.txt
lean: tilt
tower: mast
ride: tour, drive, journey
step: tick
```

**How.** Read `kept: retired, retired` lines. Split each identifier from `roc_tree` on `_` and on capitals, and read each `#` and `##` comment as words. A match prints `path:line: vocabulary: tilt is lean here`. Strings don't count. Take `glob=` and `words=`.

**Why it's first.** It's the only way to hold these catches after they land, because `Plan`, `frames` and `tilt` will otherwise come back with the next agent. The file also doubles as the tutorial's glossary. **The limit:** a word with a good second meaning can't go in it, so `corner` (item 5) has to stay out.

### 18. A name that disagrees with its type: extend `name_type`, and add two siblings

The existing check is at `name_hunt.shale:842`. It knows two words, `count` and `path`, and reads only top-level names and members. Three additions:

- **`name_type` with a project table.** A file `name_types.txt`, `dist: Distance`, `steps: Steps`, `fraction: Fraction`, `frames: none`. A name's last word must have that type. Run it on fields too, from the list `container` already builds at line 305. It finds `frames`, `frame_count`, `no_frames`, `bull_dist`, `steps : U32`, `leg_steps`, `mid_tower_beacon_step`, and the two `cab_*_fraction`s.
- **`bare_beside_unit`,** judged across the tree as `container` is at line 760. One field name declared as a bare number in one record and a nominal type in another means a retyping stopped halfway. A text prototype listed 35 names with two or more types, most of them harmless (`from`, `to`, `zero`). Filtering that list by hand to a bare number beside a nominal type leaves `forward` (`Distance`, `F64`), `height`, `lift` and `right` in the game, and a few more such as `color`, `roll` and the gates' `width`. So the filter is essential, and I haven't run it as code.
- **`no_value`, in `errors.shale` beside `placeholder`.** A constant whose first word is `no`, `none` or `unset`, whose type isn't a Bool or a tag. The guide states this rule, quoting `no_frames`, and nothing checks it. It finds `Arc.no_frames` and `Gaze.no_look`.

### 19. Family and twin checks: `cookbook/roc/families.shale`

- **`family`.** Group modules by their last CamelCase word. Where three or more share it, take the public names most members expose, and report each member that lacks one. On safari, grouping by hand, `Sighting` gives `in_view` and `depth_keys`, which finds `RailSighting.all_rails`, `CritterSighting.sightings` and `CritterSighting.cow_items`. `GroundSighting` lacks `depth_keys` for a good reason, so a module answers in a `##` doc, as `boundaries`' `single` already allows.
- **`twin_name`.** A public type name declared in two modules. The prototype found 10: `Anchor`, `Critter`, `Line`, `Model`, `Pose`, `Rgb`, `RoadPoint`, `Scene`, `Tree` and `View`. Nine are real. `Model` is the app runner's, and skipping files with an app header clears it.

### 20. Word lists and a top comment: additions to `name_hunt`

- **`pure_mutator`.** A pure function whose first word is `push`, `fill`, `set`, `append` or `add`, and whose result isn't its first argument's type, because nothing is being added to. `get` always counts. It finds six `Paint.push_*`, which build a fresh list, plus `Herd.fill_cows`, `Pigs.fill_pig_herd`, `fill_pig_row`, `TruckShape.fill` and `get_forward_accel_decel`. `ScanlineFill.fill_polygon` passes, because it takes the pixels and gives them back. I checked these by reading the signatures, not by running a recipe. The renames that follow for safari are `Paint.polygon`, `Paint.beacon` and so on, and `Cows.with_bull`, `Pigs.big_herd` and `Pigs.two_rows`. `fill_pig_row` makes two rows, so its name is wrong twice.
- **`abbreviation`.** A new `cookbook/words/abbreviations.txt` holding `dist`, `pts`, `vis`, `frac`, `accel`, `iters`, `sim`, `pos`, `col`, `poly`, `grad`. Any `_`-separated part of a top-level name, member or field that's in the list is a finding. The guide already says to prefer the plain word. On safari it would find `max_vis_cats`, `lean_frac`, `sun_pos` and the rest, dozens of names. `pts` also comes from `lib.Shapes`, so the sweep starts there.
- **`module_doc`.** A module with no `##` doc above its type, or a top comment holding `originally`, `used to` or `emitted`. The prototype finds six modules with no doc (see item 16), plus `SafariApp` and `gates/StepBack`, which use `#`, and the three app roots, which it should skip.

## Left out on purpose

- `Grade` clashes with a road's slope, but only specs use it, and the specs are moving.
- `Herd.herd_size`, `Sky.sky_at` and other names that repeat their module stay, because the style guide allows it.
- `World.SegmentPlan` is a true plan, made ahead of the ride. It isn't the `Plan` you removed.
- `Rider`, `Truck`, `Sky`, `Mountains`, `Angle` and `Speed` are fine as they are. `Mountains` also holds the rolling land, which a one-line doc already covers.

## Two rules I tried and dropped

- **A backticked name in a comment must exist in the file.** It found 8 hits in safari, and none was a real fault. They were a parameter, a method's name, a program's name and `Stills`' field letters.
- **A module's name must appear in its own doc.** It found 44 of 82 files, nearly all harmless, because `CatDraw` and `Distance` don't need to repeat themselves. It did flag `Frame`, `Render` and `Tour`, but they can't be told apart from the noise.

## Limits of this review

- Counts come from text scans. A comment-stripped word count can't tell a field from a local, so treat them as sizes, not exact totals. The prototypes were throwaway heredocs, and the real recipes should read `roc_tree` instead.
- I read the signatures and docs of every non-spec module, including `gates/`. I read the bodies of `Arc`, `Gaze`, `Throttle`, `RideInstant`, `Scenery` and `VehicleLimits`, and spot-checked the others.
- Any rename touching a spec's expected output, or a tutorial chapter, will need coordinating with the agents working there.
- Roc has no shadowing, so a new name can collide with a local (`best_lean` is one today). The compiler will say so.
- Items 1, 2, 3, 5, 7, 9, 12 and 16 are close to mechanical. Items 4, 6, 8, 10 and 11 change a type, so the frame hashes should judge them. The `Beats` split in item 15 is a design question, and it's yours.
