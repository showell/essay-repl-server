# The review queue

This is the orchestrator's state for the type review, so it survives a compaction. The workflow is in roc-apps `docs/review-workflow.md`. Every item here is decided. None needs Steve until the eye-test note.

## Running now (2026-11-07)

| Lane | Branch | What |
|---|---|---|
| scene-shapes | roc-apps `scene-shapes` | lane 6 below |
| truck | roc-apps `truck` | strip_corners, the setting like the tower's (Steve, notes/truck-setting.md), TruckFace gone, private helpers and `Screen.distance`, the beam's middle, restated tests |
| units | roc-apps `units` | lane 3 below |
| lib-tidy | roc-apps `lib-tidy` | delete `lib/Color`, `Brush.translucent`, an opaque `Brush.Rgba` if it unifies, Pieces as its own type, a ConvexCut module, records for float runs, bracket makers, range crashes, the glow's middle offset, rename `lib/View`, plain headers |
| tuning | roc-apps `tuning` | lane 4 below: the "chosen by eye" docs, `small_height` from the tree's parts, one Scatter function, the perched critter drawn over its tree (its own commit; pixels move). `brake_decay` stays with the rider. |

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
7. **Small leftovers:**
   - RailSighting's `runup_points` and `run_out_points` are public for nobody.
   - `VehicleLimits.base_speed` should be `starting_speed` (Truck and CrossModuleExpects use it).
   - `Gaze.look_swivel_rate` and `Motorcycle.turn_per_lean` are public but used only in their own files.
   - Rider looks up the segment twice a step; `cross_if_on_road` could return the one it ends on (put this in the rider pixel lane).
   - `roc_commas.shale` over the whole safari folder runs out of steps and leaves files half-rewritten. It must fail before writing anything, or write each file whole.

## The eye-test note (Steve tests carefully, one note with before and after renders)

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

Merged since the queue was written: rider (Motorcycle, RiderEyes, Gawking, one Limit, LeanChange; pixels held); kinds-names (LitTruck, Green, EmojiStill, standing_still); type_walk's `clients=` (walk lib with `root=lib clients=*` from canvas_apps).

Housekeeping: clear `~/.cache/roc` (14 GB on 2026-11-07) when no lane is checking. Small leftover: EmojiStills' `still_facts` uses I64 counts.
