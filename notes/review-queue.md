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

## Roc findings, held (2026-11-07)

Repros on roc-apps branch `roc-findings` (worktree lanes/roc-findings, keep it): a misspelled package alias passes when the module is never named; a record literal's nominal methods depend on statement order (destructuring alone is fine). Steve: "Let's wait till we see these again." Report upstream only if they bite again.

## Steve's Q&A leanings (2026-11-07, learning, not action)

- Scene: one crowd of things, and no tag once it isn't actionable (folded into the Scene lane).
- The backdrop stays a layer (a flipbook: objects against a backdrop). Its line is "never gets closer": sky, sun and mountains (an infinite horizon), against curved-earth trees. Not strongly held; (b) on the skyline stands unless that changes.
- The three earths (infinite-horizon mountains, a setting sun, curved-earth trees) are "honest enough for our purposes".
- A tick's order: "Hand of god makes the cat move, then the driver reacts. So cat before driver." The sequence starts far enough out that off-by-ones don't show (sent to the Scene lane's reaction move).
- "The rider has peripheral vision and sees the cat and pigs": the rider is not limited to the camera's view.
- The rider knows the road like a local; with straight segments that's equivalent to seeing the turn (the corner creatures are another cue).
- "Rides are deterministic only for simplicity purposes": determinism is a convenience, not a principle. Also: "there's some comfort in the familiarity, like a film you rewatch with popcorn."
- The truck: "mostly hand of god, but to the rider it SHOULD feel like the truck driver sees him and is teasing him." Decided: "name the tease in code, physics underneath". **Queued lane (after rider-review, which touches Truck):** find the rule hidden in the truck's lead and pace, and give it a name that says the tease, with the physics beneath it. Pixels hold. Steve, refining: "the truck is governed by the fact that we want the rider to close in on the truck throughout the route in a non-linear fashion, so that it's more interesting. I wouldn't sweat this one too much." So the named rule is "the rider closes in over the whole route, non-linearly", and the lane is LOW priority.
- The sunset's place on the long road west: "a test is the right home". (A character's behavior gets a name in code; a timing promise gets a test.)
- A director for the hand of god: "almost more like a screenwriter has scripted the whole route. I haven't seen any code that begs this question yet." No action until code asks for it.
- The segments stay in code; the film metaphor isn't a commitment.
- "Opaque by default, nominal needs a reason" (in roc-style.md now). **Queued: a survey lane** listing every `:=` record type in Safari with its reason or none, for my decisions (e.g. Scene, which widgets and the gate build from records).
- Widgets are real clients; a maker they use is fine (in roc-style.md).
- An opaque `Focal` type: no. "Leave the crash as the guard."
- Debugging widgets: no strong opinion.

## The nominal-type survey (2026-11-07; details in /tmp/claude-1000/nominal-survey/)

33 nominal types in safari and lib: 7 keep (Conifer, SegmentPlace, PigHerd, Keys.Key, Mouse.Button, Input.Snapshot and Mouse.Snapshot, the last two by their roc-ray docs), 23 make opaque, 3 unsure (LitTruck, RiderState, Motorcycle).
- **opaque-cheap lane (queued; after scenery-tests, Scene and sky-frame land, since they're in these files):** Beacon (`of_segment`), CowHerd/BigPigHerd/TwoRowPigHerd (checked makers; folds into scenery-types), GroundPatch, Post, PosedBird/PosedCat (`of(pose)`), Rendered (`of(depth, picture)`), Animation.Timeline, Tower, Still, Billboard (CME uses `adult_billboard`), BendInView (`before()`), CatCrossing (`along()`).
- **For Steve, when questions resume:** the read-heavy records Segment, RideInstant, Tour, FrameView, RiderCamera, Scene, Truck, RiderEyes, plus RiderState/Motorcycle (a state machine whose transitions live in Rider). Does "a plain record read field by field everywhere, with no invariant" count as a reason for nominal? If not, it's dozens of getters.

## The route-family review (2026-11-07; walk at /tmp/claude-1000/review-route/walk.txt). Queued after the prod deploy.

Clear, for one or two lanes, split by file:
1. World is imported by 11 game modules only for their tests, which pin the real route ("segment 18 ends"). Tests build tiny segments (`Segment.from_choices`) or move to CME; then World's test-only members go (`first_bird_segment`, `is_distracting`, `has_cat`). Split per lane, since Tower, TreeSighting and the encounters are elsewhere.
2. `Segment.segment_ending : Segment -> [Bends({ bend, bend_life }), RouteEnds]`, a total accessor; BillboardSighting and GroundSighting match it once; `bend_out_of` stays only for callers that rely on the route's shape. `BendInView.of_in_view` is the unchecked twin of `bend_after`.
3. `Tour.at_step` loops forever past the ride's end. `RideInstant.next_or_restart` answers `[Continued, Restarted]`; `step_forward` clears its history on Restarted; `at_step` crashes with a reason. One home for the restart decision.
4. Name the repeated unions once: `Segment.Ending`, `Segment.Pigs`, the planned encounter, `CowHerd.Bull`.
5. Private: World's `big_herd_count`, `pig_novelty_count`, `big_pig_herd`, `two_row_pig_herd`, `cow_herd`, `herd_count_before`; Segment's `mid_tower_min_length`, `pig_distance_before_end`, `cow_herd_along`, `cat_along`, `fifth_left_tree` (its tests move beside Segment); `RoadAhead.most_segments_ahead`; `Clock.previous` (tests use `minus(Steps.one_step)`).
6. Delete tests that restate the route's data (World:482-514 counts, :418-432, CME:122-130, Segment:189, Clock:65-74 and :87-88, Steps:42-47 and :62-69); keep the boundary ones and the real-rule data checks (every cat by a real tree, every bird can fly). Crash text: "World.crossing_at: the segment has a cat".
9. `RoadAhead.rider_segment` becomes `rider_segment_index`.
10. `Tour.steps_kept_back : Steps`; the step widget derives its range from it.
11. `RideInstant.rider_distance : Route, RideInstant -> Distance` (RideInstant and the step widget both build it); RideInstant gets a `##` module doc first.

For Steve (with the read-heavy nominal question): 7. the invariants Segment, Tour and RideInstant can break as nominal records today (a segment's crossing by its trees, trees planted for its length, only the last segment `RouteEnds`, broken already by the bends widget's 60 m cut and `{ ..seg, ending }` in tests; Tour's route and its one-step history, broken by FrameWidgetApp:90). 8. `RoadAhead.SegmentInView` stores `index` and `segment`, which can disagree; opaque means churn across about 30 readers. 2b. A Route of `{ bending_segments, last_segment }` would remove the remaining crashes.

## Test-only imports, now visible (2026-11-07)

The type walk prints `# Imported for tests only: ...` per module (shale master, walk-test-imports). Across Safari's 94 files, 22 modules have at least one: PosedBird (9), Billboard and PosedCat (5+), and Pipeline (Across, Along, Angle, Route, World, from its post fixtures). Each is a finding under Steve's rule. **Queued:** lanes by family, after the deploy (overlaps the route review's item 1). Pending, roc-apps docs/type-review.md: add the "Imported for tests only" bullet after the "Imported but not in any printed type" bullet (wait until publish.shale is off master). walk_uses.shale (1059 lines) and type_walk.shale (1025) are past ~1000 lines; a split is for later.

## Prod deploy done (2026-11-07, b420a452)

Safari (with the third-segment bird) and camera (the ring fix) are on roc.lynrummy.com: 513 files, each staging's. Found on the way: `site/publish.sh` records a Cobblestone checkout (`cobblestone-u66rel`) that no longer exists, so its PROVENANCE line came out blank after two git errors. Fix: a canvas app's provenance skips Cobblestone, and a missing checkout fails loudly for the apps that need it. **Done** (publish-provenance, merged). Left for later:
- gpu, games, machine and framebuffer name their Cobblestone checkout four ways (`KERNELS_ROOT`, `GAMES_ROOT`, `CHECKOUT`, `quires.tsv`), all defaulting to the missing `cobblestone-u66rel`. Their builds would fail today. The real fix is for the build to record its checkout in BUILT. This matters only when those apps are next published.
- `site/deploy.sh:31`'s uncommitted-changes check passes silently if git itself fails. A small fix.

## Gate: concurrent runs share one cache (2026-11-07)

Master's gate stopped at run.shale:198 (`clear_full_caches`). `du -sm` on the shared CACHES folder failed ("cannot access ..."), because another gate in a lane worktree was clearing it, and `tonumber` then read du's error text as a number. Two problems: the gate trusts du's output without checking its exit, and every worktree's gate shares one cache folder, which one run can clear under another (a build could break the same way). Fix: check du's exit and fail by name; and either key the cache per checkout, or clear only under a lock, or never clear while another gate holds it. A small lane, after the current ones.

## Open-calls-2, answered (2026-11-08): lanes to run

- **names lane** (after frame-speed, truck-draw, shell-tidy and stills-tidy land; it touches nearly everything): `cam_focal` becomes `focal_length`; `LevelPoint` becomes `RiderPointAhead` and `AheadPoint` becomes `RaisedPointAhead`; `Fraction.less` becomes `complement`; `portion` becomes `ratio_to`. A big mechanical rename, so run it when few lanes are open, like the CME split.
- **small rules lane:** each herd (CowHerd, PigHerd) owns its own front distance, and `Geom.herd_front_distance` goes (Steve: the shared value is a coincidence); the pinhole's x rule moves into Camera (one private `x_for_slope`; Lens keeps focal lengths and `y_for_height`); `Scene.RideFacts` holds the sources `{ encounter_start, truck, clock }`; Lens gains `size_on_screen`, shared by `y_for_height` and Sun's four radii.
- **truck frame's units** (small, from truck-draw): TruckPoint and TruckBox hold truck-frame offsets as `Along`/`Across`, but Along is a place measured from the segment's start: offsets are lengths (Distance), or a named truck-frame type. Also TruckLights' brake-lamp doc restates its proportions in prose, and "painted" is left in TruckBody's doc. `Truck.next_bend` keeps its own walk on purpose (moving it onto `RoutePlace.at_distance` rounds differently and moved four frames).
- **stills data lane** (after stills-tidy): strip repeated corners from the data with a script; `Still.of` refuses a corner that repeats its neighbour; the stills widget's filter and comment go. The cat's frame is a convention: Still's and CatStills' docs say a set of poses shares one frame and may reach past it.

## Gate scripts (2026-11-08): a lane is running (gate-scripts); left for later

- Run the gate's stages in parallel on the 2-CPU box (measure first: per-tool proof build times; one combined proof binary; widget checks two at a time).
- The pinned Roc is found in six places (run, fast via `cookbook:roc/pinned.shale` `roc_bin` without a version check, tutorial build and book, check.shale, pinned-roc.sh): `roc_bin` checks `roc version` against the pin, and the scripts call it. Touches the shale cookbook.
- Shale-language backlog: (S1) `use` only takes mounts, so a gate can't share a library with its own checkout (ask for a checkout-relative `use`); (S2) an `exited_ok(r)` helper for the 16 copies of `r.ended ~= "exit" or get(r, "code", -1) ~= 0`; (S3) `job_start` has no CPU budget, so tiers can't run stages at once under budget; (S4) `remove_tree(p, {vanished_ok})` and a `tree_size(p)` builtin, so run.shale doesn't shell out to `rm -rf` and `du`.

## Units lane (queued after frame-speed and truck-draw land; it touches TreeShapes, Geom, Truck, Throttle)

From the units review (walks in /tmp/claude-1000/units-review/); decided by me:
1. Radians to degrees has three float orders: VehicleLimits uses `turn.abs().to_degrees()`; `turn_speeds` is keyed by `whole_degrees : U32` (not float `==`), and its bare_floats line goes; `degrees_per_radian` moves beside `Trig.degree` in lib; World's test uses `to_degrees()`.
2. `scaled_by : X, Fraction -> X` on Pixels, Distance, FarHeight and Speed (`x * f`, the same order as `times`), replacing 16 hand unwraps (TreeShapes, Sun, TruckBody, TruckShape, Truck, Mountains; Geom's too).
3. A Speed is never negative: `metres_a_step` crashes on a negative; Throttle's dead `.max(Speed.at_rest)` and its -1.0 expect go; `Speed.portion` (tests only) goes.
4. `Clock.to_f64` goes (a point in time isn't a length): Sun and the step and sky widgets use `clock.steps_since(Clock.start)`; CME compares with `Clock.at_step(n)`.
8. Delete `Angle.steady_lean`, `LeanChange.abs`/`is_lte`/`radians` (tests use `degrees`), `Across.times`; cut Angle's doc sentence about "two leans give the change". roc check confirms nothing calls them through an operator.
9. Delete the wrapper round-trip tests (Distance, Along, Across, Pixels, FarHeight, Fraction, Speed, Angle, Steps' `phase_of`), keeping the +0.0 opposite tests, Fraction's range/clamp/-0.0, Speed's exact brake, Clock, Acceleration, and the Lean sign test.
10. `Speed.steps_to_cover : Speed, Distance -> Steps` (floors; crashes on a negative distance or a speed at rest) replaces EncounterPlan's `portion(...).to_u32_wrap()`, a silent wrap. Callers: `steady_approach_timing`, the bird and cat widgets.
Also fold in the braking-below-zero latent bug (VehicleLimits/Throttle) here, since item 3 touches the same rule.
Steve's calls: open-calls-2 #3 (names `less` and `portion`) and #7 (the sun's radii as resting-lens sizes).

## Truck-drawing lane (queued after rider-follow, which touches Truck's tests)

From the truck-drawing review; all decided by me (walk at /tmp/claude-1000/truck-review/walk.txt):
1. Truck points in the truck's own frame, measured from the trailer's centre; `truck_box` becomes a constant; the drawing context is `{ road, vantage }`. Eye test if a pixel rounds differently.
2. `RoutePlace.at_distance : Route, Distance -> Try(RoutePlace, [PastRouteEnd])` beside `distance_along`. TruckSighting's hand-walk (`truck_from`, `TruckPlace`) goes; `Truck.next_bend` uses it if it reads better.
3. The cab's profile in one home: `hood_height` and `trailer_height` move into TruckShape, plus an expect that the headlight's span lies on the nose face.
4. `TruckLights.brake_light_shapes` and `headlight_beam_shapes` (the field `brake_lights` stays the `[On, Off]`).
5. Delete the restating tests (TruckShape :159-177, TruckBody :236-244, TruckLights :250, :252-253, CME :2807-2827) and their helpers.
6. `TruckShape.trailer_length` goes private; `point` becomes `raised_point_on_truck`.
7. Docs: `TruckPoint.height` is above the road; "draws" goes; TruckLights' ARGB note and beam constants in prose go.
8. `Truck.Pace := [Slowing, NotSlowing]` named once; `LitTruck.at : Truck.Pace, Clock -> LitTruck`; `truck_in_view` takes `facts.truck` whole.

## After RoutePlace (2026-11-07; Motorcycle holds `RoutePlace`, RiderState is `{ motorcycle, eyes }`)

Queued, in rough order:
- RiderCamera keeps its own `segment_index` plus `vantage { along, across }`: it could hold a RoutePlace too.
- Gawking, Gaze and Throttle take `(motorcycle, segment)` side by side though the motorcycle knows its segment; with the route in hand they could look it up.
- `RideInstant.distance_of_rider` is now a one-line wrapper with two callers.
- Rider, Throttle and Truck test-only imports (blocked before on the restructure; unblocked now).
- The gaze widget's table moves to the game's tests (open-calls #9, approved).
- `Geom.Bend` becomes a module of its own (pipeline-core review #2; was waiting on this lane).
- The rename: the thing (RiderState) becomes `Rider`, and the mind (Rider) becomes `RiderMind`? Ask Steve now that the types have settled.
- The braking-below-zero latent bug (below).
- Test-only imports left in all of Safari (walk fixed for shorthand fields): Throttle and Truck (in rider-follow), TreeShapes' Brush (expects ~:475-497) and World's Trig (expect ~:463-465). These last two are a tiny lane.

## Latent: braking can ask for a negative speed (2026-11-07)

Found by the rider-step lane: `RiderState.next` from 299.9 m on the last segment at 0.5 m a step crashes in `Speed.accelerated_by`, because the throttle's brake (`VehicleLimits.braking_to`, which aims at rest over the distance left) gives an acceleration larger than the speed. The real ride never reaches that state (it arrives slowly), but the rule allows it. Fix with the RoutePlace lane or on its own: braking never takes the speed below its target in one step (state it as a rule, with a test of both sides), and say how the stop at the route's end then ends. It may move the ride's last few steps; check OnRoad's finish.

## name_hunt's preposition convention is fragile (2026-11-07)

Twice today, removing names in one module flipped `preposition_split` somewhere unrelated. Deleting TowerSighting's `brightness_at` (a test helper) dropped the `_at` convention under 3 stems and flagged three pairs. Removing HexColor's `red_of`/`green_of`/`blue_of` dropped the `_of` convention and flagged CME's `road_of`/`road_from`, now renamed `crafted_road`/`world_road_at`. A rule whose verdict on file A depends on names in unrelated file B is a judge that moves on its own. Look at cookbook/roc/name_hunt.shale's CONVENTION_STEMS: count per module, exclude test helpers, or drop the convention exemption and fix the names it then flags. A shale cookbook lane.

## Small follow-ups (2026-11-07)

- FrameWidgetApp builds the camera itself, copying `frame_view_at`: one home (a FrameView camera maker).
- `ScrubWidget.ride_shapes` draws the whole frame, backdrop included, and collides in meaning with `FrameView.ride_shapes`: rename it (e.g. `frame_shapes`).
- `RoadAhead.gap_to_segment` has no production caller; only a gate expect uses it. Delete it or fold the expect.
- fast.shale misses widget breakage (a widget building a FrameView literal, game.roc missing a module); lanes that touch widget-read types must run part=widgets. Already in the brief; reinforce it.

## Queued from the scenery review (2026-11-07)

- **scenery-types lane, after scenery-tests lands** (both edit CME): BigPigHerd reshaped so the standout is always in the front row (`columns_before_standout`, `columns_after_standout`, `rows_behind_front`), CowHerd `rows` becomes `cows_per_column` with a crash at World's one constructor; `RailQuad` corners named `{ low_start, low_end, high_end, high_start }` (list built only at `Camera.clipped_polygon`; bends_widget:187 reads it), Pond's far shore `{ first, middle, last }`, the pond outline type named; `Conifer.small_height = 4.896 m` "chosen by eye", `TreeShapes.tree_parts` private; "critter" becomes billboard (`sight_billboard`, `bend_billboards`, Billboard's doc); inline `RailSighting.rails_at` (its reason is the parked book; log it).
- **For Steve:** one size rule for everything in Pipeline (critters through the camera's lens, Billboard's own 1 px cut gone). This MOVES pixels: far critters come and go at different distances when the view is wide.
- Pig/PigHerd stays split (an earlier deliberate decision). `Geom.herd_front_distance` stays in Geom for now.
- `FarHeight`: Steve, yes, "only do this if it's easy": "there's perceived height vs. actual height." He thinks of trees and radio towers in the distance; "We don't need to get that physics perfect." **Queued after sky-frame lands** (it touches Lens, Sun, Mountains): a lane that first lists every height and how it reaches the screen (metres projected through the camera with the earth's drop for trees and towers; resting-lens pixels for the sun, mountains and sky warmth), then names perceived height versus actual height in types if that's easy, and stops and reports if not. Pixels hold.
  - **Survey done (rated easy):** real heights are already `Distance` and apparent ones are already Pixels `height_on_screen`; the one straggler is `TreeShapes.TreeOutline.height`, which becomes `height_on_screen`. The new unit is `FarHeight :: F64` for resting-lens heights (Sun, Mountains, Sky's warmth), and `Lens.y_for_height` is the only place it becomes Pixels. About 8 files: FarHeight.roc, game.roc, Lens, Sun, Sky, Mountains, CME :1380, sky_widget. Keep `Sun.radius` Pixels, with a FarHeight twin for its offsets. FarHeight's ops are the same bare float ops as Pixels', so no pixel moves. **Run after sky-frame merges.**
  - **Found: two curves.** Towers sink by their own rule (`Tower.sunk_below_horizon`, a 20 km radius, tuned so the sinking shows); the truck and the ground use EarthCurve (100 km). Trees, animals, birds and rails use no curve at all. Decided: the tower's sink moves into EarthCurve as a named, exaggerated curve beside the true one, so the curve rules have one home. Pixels hold. This goes in the same lane or the next. Useful for debugging and eye feel (a bird flapping between two trees and nothing else), but rarely worth saving in the repo; widgets are quick to build. So a throwaway widget for a lane's question is fine, and it doesn't need to land.

## Next free slot

- **The kinds' closure** (Steve: "That actually feels like a code smell. Have a cold agent see if there's an alternative"). Every walk of anything that holds the scene drags in each kind's internals: stills, emoji stills, poses, Tower's corners. Have a read-only agent find out why, and whether there's a better shape.

## After the route split

- **One camera record** `{ heading, vantage, cam_focal }`, replacing `Lens.CameraAim` and `RoadAhead.CameraView` (Steve: "something we should definitely do").

## After World and FrameView

- **Scene erases its kinds** (notes/scene-kinds.md, decided): the fields hold `Rendered`, and `scene_in_view` sights and renders. SceneShapes folds in or shrinks. Steve again (2026-11-07): "no reason to tag something once the tag is no longer actionable", and "All the interaction between elements (like cat crossing because driver approaches) should NOT require any drawing code." So the lane also moves any reaction decided inside a sighting (the cats' sighting takes the rider's speed) out into the ride's state, and there is one generic place that joins pictures. READY: World and FrameView have landed; next free slot.
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

## The road substrate review (decided; mostly into camera lane 2)

- **Into lane 2:**
  - The bend behind has one home, the route: `SegmentPlace := [Ahead(Position), JustBehind]`, with `rider_point_at` looking it up. `place_behind` goes, and the hand-built "behind" tests are rebuilt on real roads.
  - `BendView.outer_corner : BendView -> { end_before, apex, start_after }` on the road, so RailSighting and GroundSighting each carry it into view once.
  - RoadView becomes opaque, with `ahead_of(route, rider_index)` as its maker. Tests wanting a shorter reach use a short route.
  - `rider_point_ahead` goes private.
  - `rider_point_at` takes a `RoadPoint`.
  - `place_after` becomes `position_after`.
- **Standalone:**
  - RoadAhead's and BendView's test-only World/Route imports go, their tests move to CrossModuleExpects, and the fixture tests and restated constants are deleted.
  - `of_in_view`, and `has_bend_in_view` folded into `bend_after`.
  - `outer_edge : BendView -> Across`, with the queued `inner_edge` in the same shape.
  - SegmentPlace keeps `is_within_first` and `is_last_in`, and `is_past_end_of` goes.
  - `segment_behind` goes private.
  - Names: `indices_ahead` becomes `segments_ahead_of`, and `BendView` becomes `BendInView`.

## The lib third pass (running as `lib-third`)

## Animation (review back; three calls with Steve, notes/animation-gaps.md)

Decided: `Past(Steps)`; Placed instead of `Animation.Location`; Habit `[FliesTo(Flight), StaysPut(tree)]`; one home for the start's rounding (`Animation.start_for`), tested on both sides; EncounterSighting's gap callback goes; test-only imports and restating tests in PosedBird, PosedCat and Cat go; `bird_height`, `segment_cat` and `flight_arc` go private; the docs describing the estimate get rewritten; Cat and BirdFlight stay namespaces.

**Tool:** type_walk refuses `Scene.roc` and `gates/CrossModuleExpects.roc` (roc-ast reports parse problems, probably `var $x` with `while`), so their callers drop out of the use counts. Fix roc-ast's syntax, or have the walk report the refused files loudly.

## Road seams (found and fixed; rebasing onto master)

- **The cause:** the browser antialiases each road polygon separately, so where two chunks share an edge, grass shows through. The exact rasterizer can't see it, but a browser-AA emulator found seams in 136 of 137 frames.
- **The fix:** one polygon per segment's road (`road_along`) and one per bend's paving (`bend_paving`). The emulator then found 0 seams in 273 frames, and no held frame moved.
- **Zig:** no road-seam fix in its history. The Zig native renderer supersamples, which may be what Steve remembers.
- **Scratch tools:** `/tmp/claude-1000/road-seams/scan/` holds `SeamScan.roc`, `conflate.mjs` (the AA emulator) and `depths.mjs`.
- **Lesson:** a lane cut from an unpushed master can carry a merge that later gets taken off. Cut lanes from `origin/master`.

## Animation lane: ready once the rider merge lands (it shares Rider; it also touches RideInstant, after the camera lane)

Steve's answers (notes/animation-gaps.md):
- One slot, `encounter_start : [Unplanned, StartsAt(Clock)]`, reset at each segment.
- The flap keeps today's look at cruising speed.
- A new end-to-end test in CrossModuleExpects: the rider never overtakes the bird.
- The throttle hold stays, as a story rule.
- Every bird flies: `StaysPut` goes, and `Habit` is the flight.
- The rest is as decided in option C and the animation review.

## Next after this wave merges: the gates reorganization (Steve, 2026-11-07)

- `gates/pixels/`: SafariFrame, BackdropPixels, SunPixels, ShapesPixels, ScanlineFill, PixelGrid, PixelColor, ScreenRoll, RasterFrame, ShapesFrame and Hex.
- `gates/expects/`: CrossModuleExpects split by subject into four or five modules: road and route, sightings and scene, the ride, the story rules (sunset, night, the bird not overtaken), and the stills. Pick the groups by what the tests share. Give one test road one home. Prune with Steve's "will never fail usefully" rule. This absorbs the queued tests lane: the test-only imports from TreeSighting, TowerSighting, TruckSighting, Pipeline and SceneShapes move here.
- `gates/` keeps StepBack, OnRoad, ProofRide, FrameBench and the shale scripts.
- Update run.shale, fast.shale, the brief, docs/review-workflow.md and notes/safari-gates-roc.md. No pixels move.
- It waits until rider-pixels, rider-camera, road-seams and lib-third merge, since they all touch CrossModuleExpects.

## From lib's third pass (follow-ups)

- **Font crashes on a byte with no glyph.** Check every widget label and readout string (they reach `Font.plotted` in the native runner) for characters outside the alphabet (`'`, `?`, `°`), and either add the glyphs or change the strings. A test over the strings that exist would hold it.
- **Zero-length Span or Linear:** `Brush.shade` gives the far color, but BrushGlsl and `shapes_canvas.js` still divide by zero. Make all three painters agree, or have Safari's makers (Polygon, Backdrop, StillShapes) crash on a zero-length gradient.
- **A gate holding the Keys/Mouse bit numbers equal** to `web/canvas_app_runner.js` (a wrong bit would silently bind the wrong key).
- The remaining `to_u32_wrap` calls in WasmApp (`tone_count`, `width`, `height`).

## Widgets (two reviews, all decided; two lanes after the rider merge)

**Lane 1, the game's side:**
- `Tour.at_step : U32 -> Tour`. Gaze and rehearsal derive `first_rider` from it, and frame's `paused_tour` uses it.
- `Coast.coast_path` and `LeanSearch.search_tries` return what they compute. The rehearsal widget's copies go; they had drifted from the game (no `longest_coast`, no edge widening). Measure that `project` stays as cheap.
- `Beacon.brightness_at` (with the sightings lane's version).
- World exposes `is_distracting`, `has_cat` and "the first cat, bird and distracting segment" lookups (Gaze and Gawking hard-code index 2 too).
- `FrameView.parts`, so the frame widget only filters.
- `Spot.straight_ahead : { forward, right, lift } -> Try(Spot, [BehindCamera])` for the tree, beacon and bird widgets and the kinds' tests.
- TreeShapes' `cone_reach` and `crown_shade_reach` become public for the tree widget.

**Lane 2, the kit and the widgets:**
- A palette and `PlanView` (ground, road and rider colors, plus a mapping). The road color is unified, so one widget's road moves.
- `ScrubWidget.picture_backdrop`.
- Click helpers (`click_point`, an `Area` with `contains`, and snapshot makers for expects).
- `ScrubWidget.still_app({ title, shapes })` at a low fps for still pictures.
- `readout` takes size, align and first-row options, for stills, tree and bends.
- Frame keeps its own layout but shares the colors.
- The sky widget's curves become one `Curve` record.
- Stills: `Pose : [Cat(..), Bird(..)]` in the model.
- Rehearsal: `Stop : [Start, Shown(U64), Choice]`, plus records for the argument runs.
- Step: `steps_a_frame : U32`, `Str.inspect`, and `Angle.Lean`.
- Frame: `last_layer_on : Layer`.
- Gaze: `shown_clock`.
- `row_height_on_screen : Pixels`.
- Delete the held and restated numbers both reviews listed, including the route's frozen record (the book is parked). Keep the rule tests both listed.

**Brief:** for a widget as the walked module, use `root=<name>_widget` with no clients.

**For Steve:** subagents report that plain `bash` (`cat`, `ls`, `mkdir`) ran without the hook refusing it.

## Merge order now (2026-11-07)

1. rider-pixels (its last master merge is in progress; nothing else merges until it lands).
2. widgets-once: WidgetExpects.roc plus a `package.roc` per widget, giving 1,516 tests in one run against ~15,000. It lowers the widget budget to 35 s and raises check.shale's APPS to 51, which master already needs because OnRoad added an app.
3. makers, then camera-road.

Possible upstream finding: Roc accepts `import sub.Foo` in an app with no package `sub`, and `roc test` says "All (0) tests passed". Reduce it to a repro in `findings/` before reporting.

## From the makers lane (follow-ups, decided)

- **The outer side moves to Geom** (`Geom.OuterSide`, `Geom.outer_side`, beside `left_edge` and `Bend`), so Wildlife can use it. Wildlife can't import BendView: Segment imports Wildlife, and BendView imports Segment. Pond then stops importing BendView too. BendView's `outer_edge` and the bends widget match on it, and GroundSighting's own inner-edge `is_right()` goes. Do it after camera-road, which reshapes BendView.
- A left-turn pond's ducks are mirrored in place but keep their facing; mirror the facing too.
- Test that `bank_under_water` keeps the bank inside the water.
- The pond seam's last 3 pixels: pull the bank's inner corners in, so its end edges cross the shore at an angle.
- The brief: a module must be in `game.roc` before CrossModuleExpects can import it.

## Small, next free moment

- The skyline's docs (Steve: (b)): Backdrop's doc says the backdrop is the sky, the sun and the grass, and Mountains' says the skyline is the farthest of the ride's shapes, painted first among them.
- The browser and lib still disagree in two corners (lib-follow): Glow and Radial with no ring return the outer color directly in the JS while Brush.shade mixes to it, and the JS `twoStops` clamps the end offset to 1. Make the JS follow Brush.shade.

## From camera lane 2 (follow-ups)

- `SegmentPlace.JustBehind` can still be written for a rider on the first segment, and then `RoadAhead.bend_behind` crashes on `AtRouteStart`. Make that state unwritable.
- The sightings' helpers aren't uniform: some take a flat `vantage`, others a `camera`. Pick one.
- `{ road, vantage }` travels together through `Pipeline.sighting_of`, the rendering contexts and `rider_point_at`, so give it a name.
- RailSighting and GroundSighting each have the same `seen_before` closure.
- Two parameters are named `seen` (BillboardSighting, RailSighting).
- **Tools:**
  - roc_commas works on whole folders; add a `files=` option.
  - Shale's `substitute` silently does nothing when it finds nothing; consider a strict form.
  - fast.shale sometimes says "no green on record" right after a green run.
- **Roc oddity:** a method call on a value built as a plain record literal (where a nominal type is expected) fails "missing method". With the earlier one (a nominal value destructured from a record parameter losing its methods), that makes two candidate findings to reduce.

## From the stills' tail (small, decided)

- The stills widget still says `polygons` for a Still in `stays_in`'s field and in the parameters of `standing_at` and `large_anchor`. Rename them `still`.
- Billboard's own `still` field becomes `emoji`, so nothing reads `billboard.still.still()`.
- StillsWidgetApp :745 (drawn shapes equal polygons) can't fail usefully, so delete it.
- **The brief:** a Shale script over the still data files needs a `-- budget: steps=100000000` header; the default (5M) runs out partway through.

## The gates reorganization: the plan is in (the CME survey, at the end of the queue)

- Six groups plus `Fixtures.roc` under `gates/expects/`, one root `Expects.roc`: Road, Encounter, Sighting, Scene, Ride and Story. The survey's report (in this session's transcript) has the exact line ranges against master's 1,525-line file, the ~60 prunes with reasons, the fixtures with their users, and the name clashes (`first_road`, `bird_at`, `tree_at`).
- Decided:
  - `SceneShapes.nearer_tree_count` takes a `List(Distance)`, so its tests stay beside it.
  - The ride's second wave (EncounterReaction, Gawking, Gaze, Throttle, Rider and Truck test-only World/Route imports) moves too, into RideExpects or a seventh group.
- **Steve's call when the lane runs:** tests beside their code that import only a unit type or a lib module (Along, Across, Brush, Camera, Steps, Trig…) just to build an input. Keep them (the import is a unit wrapper) or move them (the rule says never)? One yes/no then.
- The survey lists three expects that each ride the whole route (1117, 1214, 1236); one shared ride-trace fixture could serve them.
- Fixed line numbers will drift with the lanes merging before it; re-survey briefly at start.

## Held frames by event (Steve, 2026-11-07, twenty questions)

- Every held frame is named by the event it shows, not a step number, so physics changes can't silently empty it. The proof tools take named events, worked out from the ride (for example "the ride starts", "the first step the cat is frozen", "the cat at its leap's height", "the truck braking far", "the truck braking near", "the first step after the restart").
- Each held frame says what it's there to catch. A frame with nothing to look for goes ("we can be somewhat ruthless with tests"). One mid-ride frame is fine if it's named.
- Smells guide, structure: how to judge a split. No rule, only judgment. Mostly it's whether the code changes for its own reasons (the sky's colors are tuned apart from the sun); a distinct noun helps too. Tiny modules tend to grow.

## Boundary hints (the recipe is merged: `cookbook:roc/boundary_hints.shale`)

On Safari it gave 143 "fed to one" hints (19 drawn with in the using function) and 44 borrowed nouns. The top ten, decided:

1. The grass rectangle (`Screen.below_grass_top_rect`) and `Screen.grass_top_y` move into Grass, which owns its line and its rectangle. That's the Backdrop smell again, one level down.
2. `Grass.grass_color` used by Mountains for the rolling land: kept. Grass's doc says the land shares the color on purpose.
3. `StillShapes.screen_points` moves into the stills widget, its only user; StillShapes itself never uses it.
4. `Tower.corner_offset` for the beacon widget: already in the sightings lane (a footprint on level ground, `corner_offset` private).
5. `Sun.height_when_set` used by Sky: the sun's fall belongs to Sun, as `Sun.set_progress(height)`, and Sky maps it to dusk.
6. Merged into 1.
7. TruckShape's dimensions: shared geometry by design. Only `cab_bottom` is TruckBody's own; move it.
8. `Mountains.is_sun_behind_mountains` used by FrameView's headlights: fine, since the skyline owns it.
9. `Segment.segment_standout_pig`: the standout choice belongs with PigHerd or Gawking. A short look in the lane decides which.
10. `CanvasRoll.rider_roll`: CanvasRoll exists for one call from RiderCamera. Fold it in if the book's include allows.

These become one "boundary moves" lane.

## Steve's views from the questions (2026-11-07, learning only, no action)

- **The book rewrite's pictures:** a high bar for real widgets, a low bar for simple pictures drawn from the code. A chapter about a world thing (a mountain) shows it rendered. Don't force it: trig needs no picture. The flip side: a chapter not worth a picture probably belongs in the math section near the end.
- **Imports are only prod code:** a strong leaning, not yet a ruling. A lib import only a test uses (Ground's `lib.Brush`): move it. Unit types: undecided. The case to look at is `Cat.roc`, which imports Along and Across only to build a test crossing, a sign the test builds another module's input.

- **Test data (Steve):** tiny crafted routes, not `World.route`, so a test shows exactly what it tests and survives route changes ("quite plausible that we will change the real road layout"). Tests use carefully crafted data, a real edge case or a deliberately normal case. The gates reorganization's shared fixtures follow this.

## From the polish lane

- lib's `Brush.roc` header says "an offset outside [0, 1] is clamped as shapes_canvas.js clamps it". That's backwards now: the JS follows Brush. Fix the doc.
- On a gradient with a ring, the canvas paints the outer stop's color exactly at its far end, where `Brush.shade` mixes to it at fraction 1: the same last-bit question in one more corner. Make the JS follow Brush there too.
- **The brief:** `run` of `node`, `wc`, or an untracked scratch binary needs `want =`; `RasterFrame held <depths...>` hashes any steps; `l[#l + 1] = x` appends to a list (`append` errors).

## STATE AT SESSION END (2026-11-07, night)

**Masters.** roc-apps master is pushed, every lane merged and gated green, ride unchanged since the one-size rule (finish 6746). Prod (roc.lynrummy.com) has Safari with the third-segment bird plus camera's ring fix (deployed earlier tonight). Shale master is pushed (loud `substitute`, the walk's test-only imports and shorthand fix, boundaries' clients/tests, name_hunt's per-file convention), and the new shale binary is installed. roc-markdown has one rename (run_at is now indexed_run).

**Dev** serves the frame-timing build (`?timing=1` logs the first 120 frames' step/wasm/decode/paint ms), release. Branch `frame-timing` (lanes/frame-timing) is not merged: merge it with a full gate (part=page runs the runner against a stand-in canvas), then redeploy master to dev.

**In flight:** `frame-speed` (lanes/frame-speed, cut from `frame-profile`) cuts the frame's wasm cost with no pixel moving: tree rings and hull, one shape list, bends' cos/sin once, skyline bearings. When it reports: merge `frame-profile` (FramePartsBench) and `frame-speed`, full gate, deploy, and ask Steve to rerun `?timing=1` in Firefox (it was 11 slow of the first 30 frames cold; wasm 12.7 ms cold, 7.4 warm per drawn frame).

**Next, in order:**
1. The gates reorganization (notes/gates-reorg.md: `gates/proof/`, the CME split into gates/expects/ with one package root; the spike works). Run the split with NO other lane open (Steve). FrameBench stays.
2. The truck-drawing lane (queued above).
3. After RoutePlace: `Geom.Bend` as its own module; the braking-below-zero latent bug; World's test-only Trig import; TreeShapes' test-only Brush import (check after geom-tidy).
4. Steve's open calls 11-14 (notes/open-calls.md: herd front distance, the pinhole's x rule, `cam_focal` to `focal_length`, the point names), and the Rider/RiderMind rename question (ask him).
5. Housekeeping: the old ~/build/roc-apps/safari-gate-caches (2.5 GB) can go now that every lane uses the per-checkout caches; lanes/ has expects-spike (keep until the split lands), roc-findings (held, Steve), frame-timing, frame-profile, frame-speed.

**Rules Steve set today** (beyond the queue): agent reports wait behind his thread (memory: queue agent reports); five agents unless he says otherwise, scaled back for the CME split; types are opaque by default, and nominal needs a reason; widgets are real clients; no import only a test uses, widgets included; whole ride history kept; timelines build one frame.

