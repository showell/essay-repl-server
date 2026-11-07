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
