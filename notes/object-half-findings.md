# The object half: findings

*2026-11-07. A cold review of the code that draws objects relative to the rider, since every object moved onto `Pipeline`: the sightings, the kinds, the Shapes modules, `Scene`, `SceneShapes` and `RoadAhead`. Read with `docs/smells.md` and without the book. The substrate had its own review, in [the drawing half's findings](drawing-half-findings.md). My decision follows each finding.*

**Clean, per the reviewer:** Pipeline, Picture, Beacon, Trees, DepthSort's merge itself, `TruckShape.truck_box`, GuardRail's bars and posts, and RoadAhead's `Position`.

## Design, with my decisions

**1. Standing on the ground is written three times, with three height formulas.** Billboard, CatShapes and BirdShapes each project the feet, work out a height in pixels and call `StillShapes.still_shapes`. Two subtract two projections; the bird uses `cam_focal * height / forward`; only Billboard drops anything under 1 px. *Decision: one function in StillShapes. Moves pixels slightly; eye test.*

**2. "Too small to draw" has five homes.** `Detail.min_scenery_px`, a second 2 px in `BillboardSighting.min_critter_px` tested through the resting lens with an apology in its doc, Billboard's 1 px, and the beacon's own 0.5 px and 0.02 brightness. *Decision: one size test, `Pipeline.scenery_test`, for every kind, and the beacon's limits named in Detail. Moves pixels; eye test.*

**3. A kind measured on the road gets its location twice.** `rendering_of` passes only `right` and `forward`, so `SceneShapes.road_context` copies the place back out of the same sighting; the truck ignores `right` and `forward`, and the tower uses both copies. *Decision: the setting carries the sighting's road place for every kind, and `road_context` goes. No pixels move.*

**4. Two caps nobody owns.** `max_visible_towers = 16` can never bind (15 is the most), and it's applied before the cull that drops sunk towers. `max_visible_critters = 320` very likely never binds. *Decision: confirm neither binds on the whole ride, then delete both.*

**5. A tree's detail is decided by its rank, not its size.** The count of nearer trees exists only to shade the trunks of the nearest four, so a lone tree 400 m away gets a round trunk and the fifth of a near cluster doesn't. *Decision: decide the trunk by its width in pixels, as cones are decided by reach; Conifer's context becomes `{}` and the quadratic count goes. Moves pixels; eye test.*

**6. The ground drops away for the road and the truck, and nothing else.** By arithmetic, at 490 m a tree's base or a rail sits about 2 px above the road. Tower sinks by its own copy of the formula. *Decision: apply the drop once, for everything on the ground, with Tower's radius as a parameter. Moves pixels; eye test.*

**10. A perched bird and its tree tie on depth, and a field order decides it.** `birds` before `trees` in `things_in_tie_order` puts the tree over the bird, and no comment says so. `tie_slack` is about 6e-8, written as bits, with no reason given. *Decision: state the bird-and-tree rule where it's decided; drop the slack for an exact stable sort if the proof holds.*

**Rendered and Picture.** In this Roc, `:=` is nominal and `::` is opaque. *Decision: Picture stays opaque, because it's handed along whole and nobody should reach into its shapes; Rendered stays nominal.*

## Mechanical, going to an agent now

- **7.** The segment behind the rider is handled four times. RoadAhead answers the places in view, behind included, and each sighting maps over them.
- **8.** CatSighting and BirdSighting are one module with two nouns. One sighting of an animated crossing; `PosedCat` and `PosedBird` become kind modules like Conifer.
- **Known:** `tier_shape` has two branches calling `tier_triangle`; `Conifer.scenery_picture` repacks its setting and `tree_picture` rebuilds it. These wait for the book's writer to finish with the tree chapters.
- **9.** Shared geometry lives inside kinds: the hull, midpoints, `screen_rod`, `evenly_spaced`, and two circle functions that step their angles differently. Moving them is mechanical; unifying the angles moves pixels.
- **11.** The end tower is built twice; `mid_tower_key_offset = 60` stands in for a phase; Scene works out the truck's lead; `beam_shapes`, `glow_shapes` and `truck_renderings` answer lists for one or none; `critters` means billboards only; TruckShape's header names a `fill` that doesn't exist; `RailSighting` sights nothing; `RailQuad.forward` is stored beside the corners it comes from; tree and truck sightings are tested in SceneShapes.
