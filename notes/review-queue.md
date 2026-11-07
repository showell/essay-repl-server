# The review queue

This is the orchestrator's state for the type review, so it survives a compaction. The workflow is in roc-apps `docs/review-workflow.md`. Every item here is decided. None needs Steve until the eye-test note.

## Running now (2026-11-07)

| Lane | Branch | What |
|---|---|---|
| rider | roc-apps `rider` | Motorcycle and RiderEyes, a Gawking module, CrossingReaction split into throttle and attention, one `Limit` shape, `Angle.LeanChange`, private helpers, `starting_speed`, RideFocal's argument order. Pixels hold. |
| lib-tidy | roc-apps `lib-tidy` | delete `lib/Color`, `Brush.translucent`, an opaque `Brush.Rgba` if it unifies, Pieces as its own type, a ConvexCut module, records for float runs, bracket makers, range crashes, the glow's middle offset, rename `lib/View`, plain headers |
| walk-clients | shale `walk-clients` (mounts file `~/showell_repos/lanes/walk-clients.mounts`) | type_walk's `clients=` setting, so a package's use counts see its apps |

## Next lanes, in order (each waits on the lanes it shares modules with)

1. **World** (after rider; kinds-names has merged): split World into the route plan and Segment, a `Route` type, the slot renamed `encounter` (with EncounterSighting and EncounterReaction), a `CatCrossing` type with one builder, `cat_along` and `fifth_left_tree` moved beside `nearest_tree_ahead`, a planned bird with no tree crashing, the segment's derived fields worked out (`Bends({ turn, bend_life })` / `RouteEnds`, `commit_along`, `has_mid_tower`), `pigs : [NoPigs, Herd({ herd, interest })]` with no `NoPigs` in PigHerd, names (`route_segments`, `segment_plans`, `segment_standout_pig`), the herd expects moved to their herds, Scenery dissolved into its users, and `heading`'s entry bearing per segment. See notes/world-plan.md.
2. **Animation** (after World, which shares Cat and BirdFlight): each encounter records `started_at : Clock`, chosen once from the rider's speed (the hand of God). The frame is the clock minus the start. `stage_over_step_span`, the bird's gap playback and the billionth fudge go. **Pixels move.** See notes/animation.md.
3. **Units** (after rider): `portion` on Distance, Pixels, Speed and Turn; Clock's `steps_since` with `plus` and `minus` taking Steps; Attention and Speed crash by name below zero; `Fraction.from_ratio` private and `Fraction.less`; the bird widget's `distance_from`; Bearing drops `is_eq` if unused.
4. **Tuning** (kinds-names has merged, so it can start): "chosen by eye" docs; `small_height = tree_parts × 36 mm`; one Scatter function for both herds; a critter perched on a tree drawn over it, as a named DepthSort rule. **Pixels move.**
5. **Rider, pixel part** (after rider): stop at the route's end with no teleport, `Motorcycle.Controls` with no round trips, Coast counting from 1, delete the lift to exit speed, delete `lean_target`, delete `lean_hold`, one gaze return rate, `firmest_brake`. **Pixels move.** See notes/rider-physics-decisions.md.
6. **Small leftovers:** `SceneShapes` `nearer_tree_count.to_u16_wrap()` wraps silently. RailSighting's `runup_points` and `run_out_points` are public for nobody.

## The eye-test note (Steve tests carefully, one note with before and after renders)

- every pixel item in lanes 2, 4 and 5 above
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

Merged since the queue was written: kinds-names (LitTruck, Green, EmojiStill, standing_still). Small leftover: EmojiStills' `still_facts` uses I64 counts.
