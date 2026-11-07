# Where a module's tests live

A review of the six sighting modules (Tree, Tower, Billboard, Crossing, Truck, Rail) found nine things. I decided eight of them; one is a rule only you can set.

## The facts

Two rules pull against each other, and the sightings follow both.

- **Tests beside their code.** The smells guide now says "a module's tests live in another module" is a smell. A lane moved TreeSighting's and TruckSighting's expects home from SceneShapes for that reason. TreeSighting, TowerSighting and TruckSighting keep their expects beside the code.
- **No import only a test uses.** The header of `gates/CrossModuleExpects.roc` says: "the game shouldn't import a module for a test, so they sit here." BillboardSighting's and CrossingSighting's expects (about 300 lines) live there.

So each half breaks the rule the other half keeps. To test beside their code, TreeSighting imports Across, Along, Angle, Distance and World only for its tests, TowerSighting imports Steps and World, and TruckSighting imports Angle and World. Each also builds its own small test road. Counting Pipeline's and CrossModuleExpects', there are five copies of that fixture.

## The options

- **(a) Tests beside the code; accept test-only imports.** One test road gets one home that every module's tests can call, such as a small `TestRoad` module. CrossModuleExpects shrinks to the checks that really span modules (the scene, a finished ride).
- **(b) Tests beside the code, in a sibling file.** Each module gets a `<Module>Spec.roc` beside it, which the gate runs. The module imports nothing for tests, and its tests are still next to it in the folder.
- **(c) Keep CrossModuleExpects as the home** for any test that needs imports the module doesn't, and move the sightings' own tests back there.

I'd take **(a)**. An import that only a test uses costs nothing at run time, and a reader finds a function's tests right under it. The guide's smell already leans that way, and one shared test road ends the five copies.

## Decided without you, for the record

- **One home for "tall enough through the camera's lens":** `Pipeline.scenery_sighting_of`. TreeSighting and CrossingSighting each wrote it out, and Tree's `sighting_of` meant something different from Pipeline's.
- **One naming pattern** for the per-segment helpers: `segment_trees`, `segment_towers`, `segment_billboards`, `segment_cat`, `segment_bird`, each private unless an outside test calls it.
- **The beacon owns its blink:** `Beacon.brightness_at`, with the "opposite blink" rule moving to Beacon.
- **The truck takes its route position whole,** and works out its own lead, so Scene stops doing truck arithmetic.
- **Three docs say why their module breaks the family.** Tower and Truck have no size test, and the rails don't go through Pipeline. Towers and the truck stay drawn whatever their size, so no pixels move.
- The restated constants' expects go, `rails_in_view` becomes `rail_quads_in_view`, `run_up` gets one spelling, and the cat's crossing is built like the bird's.
