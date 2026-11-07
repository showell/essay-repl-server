# The review queue

This is the orchestrator's state for the type review, so it survives a compaction. The workflow is in roc-apps `docs/review-workflow.md`. Open questions for Steve: notes/frame-record.md. Eye tests: notes/safari-eye-tests.md.

## Running now (2026-11-07)

| Lane | Branch | What |
|---|---|---|
| world-split | roc-apps `world-split` | World lane 1 of 2: World and Segment split, `Route`, derived segment fields, the pig state, names, and `Placed` carrying a whole road point |
| pipeline | roc-apps `pipeline` | lane 8 below, without Placed |
| leftovers | roc-apps `leftovers` | `ArgbColor.from_rgb`, `with_alpha` in Tower and snake, squashed_shapes' record, lib headers, the README's Disc row, `Attention.scaled_by`, `Lean.portion`, roc-style's examples, `starting_speed`, private helpers |
| commas-whole | shale `commas-whole` (mounts `lanes/commas-whole.mounts`) | roc_commas.shale works out every file before writing any |

## Next lanes, in order (each waits on the lanes it shares modules with)

1. **World** (after rider; kinds-names has merged): split World into the route plan and Segment, a `Route` type, the slot renamed `encounter` (with EncounterSighting and EncounterReaction), a `CatCrossing` type with one builder, `cat_along` and `fifth_left_tree` moved beside `nearest_tree_ahead`, a planned bird with no tree crashing, the segment's derived fields worked out (`Bends({ turn, bend_life })` / `RouteEnds`, `commit_along`, `has_mid_tower`), `pigs : [NoPigs, Herd({ herd, interest })]` with no `NoPigs` in PigHerd, names (`route_segments`, `segment_plans`, `segment_standout_pig`), the herd expects moved to their herds, Scenery dissolved into its users, and `heading`'s entry bearing per segment. See notes/world-plan.md.
2. **Animation** (after World, which shares Cat and BirdFlight): each encounter records `started_at : Clock`, chosen once from the rider's speed (the hand of God). The frame is the clock minus the start. `stage_over_step_span`, the bird's gap playback and the billionth fudge go. **Pixels move.** See notes/animation.md.
3. **Units** (after rider): `portion` on Distance, Pixels, Speed and Turn; Clock's `steps_since` with `plus` and `minus` taking Steps; Attention and Speed crash by name below zero; `Fraction.from_ratio` private and `Fraction.less`; the bird widget's `distance_from`; Bearing drops `is_eq` if unused.
4. **Tuning** (done, merging; no pixels moved): "chosen by eye" docs; `small_height = tree_parts × 36 mm`; one Scatter function for both herds; a critter perched on a tree drawn over it, as a named DepthSort rule. **Pixels move.**
5. **Rider, pixel part** (after rider): stop at the route's end with no teleport, `Motorcycle.Controls` with no round trips, Coast counting from 1, delete the lift to exit speed, delete `lean_target`, delete `lean_hold`, one gaze return rate, `firmest_brake`. **Pixels move.** See notes/rider-physics-decisions.md.
6. **SceneShapes** (after tuning, which changes the tie order):
   - TreeSighting's and TruckSighting's expects move home from SceneShapes.roc, and the route-length expect goes.
   - One public `scene_renderings : Scene, CameraView -> List(Rendered)`, far to near, with the tie order written once. `ThingLists`, `things_in_tie_order` and `truck_rendering` go, and CrossModuleExpects stops rebuilding the order. Decided: the gate keeps a check per kind, by rendering a scene with one kind at a time, so a dropped kind still fails by name.
   - `nearer_tree_count` and `tree_rendering` become private.
   - `GuardRail.quad_rendering`, with `quad_shape` and `quad_depth` private.
   - The module doc says "orders", and the context doc names no list of kinds.
   - `nearer_tree_count.to_u16_wrap()`, which wraps silently.
7. **The frame's top** (after world-split, since both reshape RideInstant): the frame-building moves out of RideInstant into `FrameView` (Steve's name), which holds the shapes, the sun, the sky colors and the roll, so painting a frame is one call; the truck's lead is worked out once; private helpers; Tour's comment; the restated expects; `billboards_in_view`.
8. **Pipeline** (after trees, which moves `min_scenery_px` into it):
   - `SizeTest : { focal_length, smallest_height_on_screen }`, since BillboardSighting fills the focal length with `resting_focal`, not the camera's.
   - Pipeline's own expects, through a private test kind: the near plane, the size threshold, and the rendering's depth.
   - `Camera.height_on_screen`, so the size test stops projecting inline. It must keep the same order of operations.
   - Into the World lane: `Geom.Placed(kind) : { road_point, lift, kind }`, so the road point travels whole from placed to sighted, as it does in Spot.
9. **Small leftovers:**
   - `BillboardSighting.min_critter_px` (2 px) and Pipeline's `smallest_scenery_height_on_screen` (2 px) are one rule: the smallest thing worth drawing (decided). Give it one public home in Pipeline, and drop the gate's expect that holds it to 2.0. Merge after world-split, whose fixtures Pipeline's new tests use (`World.route_segment(0)`, which world-split deletes).
   - `Attention.portion : Attention, Fraction -> Attention` scales attention, but `portion` on the other units now divides (`d.portion(whole)`). Rename Attention's to `scaled_by` (decided).
   - Lens.roc:58 divides two `Angle.Lean`s by hand: give Lean a `portion` too.
   - roc-style.md:88 cites `Fraction.from_ratio`, which is now private, as its example of a conversion name. Pick a public one.
   - RailSighting's `runup_points` and `run_out_points` are public for nobody.
   - `VehicleLimits.base_speed` should be `starting_speed` (Truck and CrossModuleExpects use it).
   - `Gaze.look_swivel_rate` and `Motorcycle.turn_per_lean` are public but used only in their own files.
   - Rider looks up the segment twice a step; `cross_if_on_road` could return the one it ends on (put this in the rider pixel lane).
   - lib, second pass:
     - `ArgbColor.from_rgb(color, { alpha })`, used by the truck's `glow_edge` and the sun glow's alpha.
     - `Tower.roc:493`'s `{ ..Brush.opaque(..), a: 0.25 }` and snake's `{ ..hint_color, a }` should use `Brush.with_alpha`.
     - `Shapes.squashed_shapes` takes `List, F64, F64`; give it a record.
     - The Font, Camera, ArgbColor and RgbColor headers need plain sentences.
     - The README's Disc row is stale.
     - `Brush.Rgba` stays structural: an opaque one fails the platform's type, and a nominal record guards nothing at this pin.
   - `roc_commas.shale` over the whole safari folder runs out of steps and leaves files half-rewritten. It must fail before writing anything, or write each file whole.

## Eye tests

Steve (2026-11-07): deploy Safari often. After each green gate, master is built into the dev channel, and an entry goes at the top of notes/safari-eye-tests.md. Pixel lanes are tested as each one merges, not batched. Items still waiting for a lane:

- every pixel item in lanes 2 and 5 above
- the perched bird drawn over its tree (merged with tuning; no held frame moved, so choose a frame that shows a perched bird up close)
- one earth instead of `sink_radius`, and `most_segments_ahead` from a named reach
- the sun glow's alpha as ArgbColor
- full dusk at a whole step
- the land's seam at due south (a whole number of waves)
- the road behind the rider round a bend (drop the lead-in), and the rail's run-up as four legs
- a strong-lean frame for the backdrop's 200 px roll margin (already merged; only the page's call hash moved)
- the browser's new ellipse-gradient path (merged; no check proves the JS)

## Later

- **Motion chapter:** derive `turn_speeds`, the brake fade and `turn_per_lean`; the turn with speed (no pivot at rest).
- **Book:** every chapter is rewritten later. False sentences are logged in notes/book-parked-sentences.md.

Merged since the queue was written: lib-tidy (no lib/Color, ConvexCut, records for float runs, range crashes, lib/Eye); tuning (the perch rule, Scatter); rider (Motorcycle, RiderEyes, Gawking, one Limit, LeanChange; pixels held); kinds-names (LitTruck, Green, EmojiStill, standing_still); type_walk's `clients=` (walk lib with `root=lib clients=*` from canvas_apps).

Housekeeping: clear `~/.cache/roc` (14 GB on 2026-11-07) when no lane is checking. Small leftover: EmojiStills' `still_facts` uses I64 counts.

## Next free slot

- **The kinds' closure** (Steve: "That actually feels like a code smell. Have a cold agent see if there's an alternative"). Every walk of anything that holds the scene drags in each kind's internals: stills, emoji stills, poses, Tower's corners. Have a read-only agent find out why, and whether there's a better shape.

## After the route split

- **One camera record** `{ heading, vantage, cam_focal }`, replacing `Lens.CameraAim` and `RoadAhead.CameraView` (Steve: "something we should definitely do").

## After World and FrameView

- **Scene erases its kinds** (notes/scene-kinds.md, decided): the fields hold `Rendered`, and `scene_in_view` sights and renders. SceneShapes folds in or shrinks.
- **GroundSighting** (the ground review): its expects move home from CrossModuleExpects, with three members going private; `BendView.inner_edge`; `pond_patches` takes the SegmentInView whole and matches `bend_life`; `chunks_along` becomes `chunk_count`. After the earth work, Ground becomes `GroundPatch`.

## After the Polygon lane

- **Stills** (notes/stills-data.md, all decided), plus Polygon's tail: `triangle` and `rectangle` take corners first too (decided; `triangle` keeps its place, since the shapes widget and the book use it), with `shapes_widget/TwoShapes.roc` updated and the book's include left resolving; roc-style.md:697's `gradient_polygon`; Tower.roc:142's doc naming the now-private `Ground.ground_curve_radius`; and `Brush.clamp01`, if it has lost its last caller. The rest: `Still := List(Still.Polygon)`; the gradient as a `[Linear, Radial]` tag; the fill as `[Flat, Shaded]`; `is_drawable` goes and the data tests draw through the real path; restated expects go; private helpers; one description of the still's frame; `Point`; negatives and hex in the data; `EmojiStill` drops `codepoint`.

## After World and FrameView

- **SafariApp** (the shell review): `Tour.segment_index`, or `to_next_segment` in Tour, with a crash in place of `step_guard`; `playing : [Playing, Paused]` with a named "steps a press while playing"; `tour_stepped`; private helpers; "the next segment" in the doc. The backdrop-in-a-space step that SafariApp and ScrubWidget each write goes with FrameView: one framed-shapes maker, `ride_shapes_in` gone, and the zoom as `canvas_width / Screen.width`.

## After World (the makers review)

- **Wildlife, Pond and Billboard:**
  - Wildlife asks BendView for the outside (an outer side in BendView, matched once for across and facing).
  - Pond takes the bend and mirrors on a left turn.
  - `Billboard.half_width` (a still is square).
  - `Pond.pond_outlines`, water first, and `far_shore` named once.
  - Wildlife's private helpers.
  - Trees' "chosen by eye" docs.
  - The baby stays where it is (Steve): its doc says it stands straight on past the bend, ahead of the rider on the approach, off the next road.

## After World (the sightings review)

- **Sightings:**
  - `Pipeline.scenery_sighting_of`, with `scenery_test` private, folding into the `min_critter_px` merge.
  - `segment_<nouns>` helpers, private unless a test needs them.
  - `Beacon.brightness_at`, with the opposite-blink rule in Beacon and `tower_if_ahead` gone.
  - Docs on why Tower, Truck and Rail break the family (no size test for towers or the truck: decided).
  - The truck takes its route position whole (with the frame's top).
  - Restated expects go, and the tuned constants go private.
  - `rail_quads_in_view`, `run_up_points` and `rail_run_on` (batch the widget and the book).
  - The cat built like the bird (in the encounter lane).
  - Tests: see the tests lane below.
- **Tools, later:** a family mode for type_walk (shared types once, members' blocks side by side, private signatures too); the `families` lint can't see per-noun families.

## After World: the tests lane (Steve's rule, notes/tests-beside-code.md)

- Every module's test-only imports go: TreeSighting (Across, Along, Angle, Distance, World), TowerSighting (Steps, World), TruckSighting (Angle, World), Pipeline (World, Along, Across, Angle, from the Pipeline lane), and SceneShapes (PosedBird, for the perch expects). Their tests move to CrossModuleExpects, with one test road there in place of five copies.
- Prune with a critical eye: any test that restates, duplicates, or would never fail usefully goes. Keep the boundaries, tie orders and the near sides of crashes.
- Lanes from here on follow the rule: no import only a test uses.

## Shale

- **`shale --help` prints the mounts table, including the `keys:` line.** Agents run it to read about the language, so the secrets folder's path lands in their transcripts. Make `--help` describe the language without listing mount paths, or mask `keys:` (a separate `--mounts` could show the rest). Until then, never tell an agent to run `shale --help`.
- Agents' pain points (family-mode lane): a `use`d library can't call another library's functions; functions see only `const`s, not top-level locals; map keys must be strings; `find` takes at most 3 arguments; `wc` is refused as a text tool; there's no `now_ms`.

## Running (2026-11-07, evening)

rider-pixels, stills, world-encounter (World lane 2, without the heading), frame-view (lane 7 plus the backdrop step, the truck's lead and `billboards_in_view`). The camera waits on Steve (notes/camera-record.md).

## After World lane 2 (the stills' tail)

- `EmojiStill.codepoint` goes (Steve). Its tests are in World/Segment.
- Fields and constants that hold a `Still` but are named `polygons` (`EmojiStill.polygons`, `standing_still_shapes`' and `PoseStill`'s `polygons`, the `*_polygons` constants) become `still` (decided), so nothing reads `x.polygons.polygons()`.
- `Still.Vertex` stays (decided: a still's own units, and `Point` would twin `Screen.Point`).
- StillsWidgetApp ~738 says "StillShapes leaves out what it won't draw", which is no longer true.
- BirdStills' and CatStills' shaded count of 0 can never change, so delete it (Steve's test rule).

## From the rider pixels lane

- **A gate that the ride stays on the road** (decided): a proof tool that rides the whole route and fails if the rider passes the half width, a segment goes backwards, or the rider runs past a segment's end without crossing. Report the widest point. The rider lane checked this by hand, and item 5 came within 0.1 mm of the edge.
- **The firmest brake (item 8)** is stopped: the rule has no memory, so the rider leaves the braking zone and throttles up, then gets asked for a brake firmer than its own speed (a crash at step 5570). It needs Steve's call (clamp at the exit speed, a braking state, or braking in whole steps); the patch is at `/home/steve/build/rider-pixels-proof/item8-firmest-brake.patch`.
- run.shale's notes on what each held depth shows (the cat at 1570 and 1590, the truck at 3742 and 6553) may be wrong after the timing moved. Eye check, then fix the notes.
- The book's rehearsal step (370 → 374) and the gaze table's steps are stale (parked).

## After FrameView: the camera (Steve agreed to all three, notes/camera-record.md)

1. `RiderCamera := { segment_index, vantage, heading, cam_focal, roll }` with `of : RiderState, Route -> RiderCamera`, replacing ViewYaw and `Lens.CameraAim`. Consumers read open records. Pixels hold.
2. The vantage leaves `RoadView`: RoadView is pure road, `CameraView` dies, and the sightings take the camera and the road. Pixels hold.
3. `heading` is worked out from the route, and `Motorcycle.heading` goes. The sky may move in its low bits, so it gets an eye test.

## Bugs (lower priority than the type audit; Steve, 2026-11-07)

- **White seams in the road pavement,** seen very occasionally. The same bug was in the Zig version (angry-gopher `games/driving`), and it was fixed there. No commit message names it; start with `wasm/render.zig` and `wasm/geom.zig`'s road patches, and look at how the patches meet: overlap, shared edges, or antialiasing between adjacent polygons. Find a frame that shows a seam first, then port the Zig fix's idea.

## Eye tests

Steve is pausing eye tests for a while, since they've all passed. Keep deploying after green gates and adding entries; he'll catch up in a batch.

## The on-road gate (merged, 2026-11-07)

`gates/OnRoad.roc` rides the whole route in `part=proof` and fails if the rider passes the half width, a segment goes backwards, or the rider runs past a segment's end. On master the widest point is **1.99963 m of 2 m, at step 6736 on segment 18**: a 0.37 mm margin. That's a near miss in today's physics, not a gate problem. The rider pixels lane's last check put its widest at 1.9738 m. Watch it after that lane merges. If the margin stays thin, it's a question for the Motion chapter: the lean search, or a named road margin the rider aims inside.

Small: `canvas_apps/safari/README.md` (lines 61 and 94) lists the proof tools without OnRoad.

## The rider merge is held (branch `rider-held`, 2026-11-07)

- It waits on the sunset test (Steve's rule: the sunset's climax falls on the long westward segment, measured on master, with a margin).
- **The cats aren't a blocker** (Steve: "it's not super important which step they're on... the cats should work out from the logic that puts them relative to the rider"). On the new timing, step 1570 has no cat (it's out of view from 1547 to 1606). The frame widget's counts fix is on branch `frame-counts`.
- When the merge goes in, re-pick the held depths and the frame widget's step so each shows its scene again (the cat frozen, mid-leap, the truck's glow, the truck braking). Where cheap, define a step by its event ("the first step the cat is in the lane") rather than a number.

## Second passes (decided)

- **Tower, Beacon and TowerSighting** (merge into the sightings lane):
  - `beacon_disc` gives one shape, and `beacon_shape` a Try.
  - `SunkTower` stores `metre_on_screen`, and `rod_width_at` goes.
  - 16 restated expects go.
  - The beacon widget calls `scenery_picture` on a straight road, and `corner_offset` goes private (decided: one home).
  - TowerSighting's seven helpers go private.
  - `tower_if_ahead` takes a `road_point` and a built Tower.
  - `base_corner_on_road` takes the center whole.
  - `Beacon := U32` with `brightness_at : Beacon, Clock -> Fraction` (decided: the key is the beacon's identity), and `beacon_stagger` goes private.
  - Shape names: `leg_shapes`, `ring_shapes`/`ring_shapes_at`, `brace_shapes`/`face_brace_shapes`, `end_tower`/`mid_tower`.
- **The backdrop** (a small lane):
  - Backdrop's test-only imports go, along with its two expects.
  - Lens's Trig expect goes.
  - Mountains' `seen_bearing` and its six expects go, with the other restating expects in Mountains and Sun.
  - `Sky.dusk_at_set` goes private.
  - `FrameView.sun` becomes `sun_sighting`.
  - `Lens.scale_for` becomes the one home for the lens's scale.
  - Lens's five private helpers go with the camera lane.
  - For the camera lane to weigh: hold the focal as a Fraction of the resting focal, which rules out Sun's crash.
  - Later, maybe Steve: the skyline as part of `BackdropShapes`.
- **RoadAhead.rider_point_at** takes `{ place, along, across }`, not a RoadPoint (seen twice; with the camera's vantage lane).
