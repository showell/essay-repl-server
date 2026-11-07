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
