# Heights in a 3D world

*2026-11-08. This is the essay you asked for in your reply to open-calls-10: the ride is truly 3D, but height is mostly an afterthought.*

---

## What you said

The difference between two heights isn't a length. It's a distance constrained to the z axis. Most of the time we think about places on the ground, and height comes after. Our 2D objects lack depth, not height. And most objects stand on the ground, but birds and beacons perch.

All of that matches the code, and it suggests a sharper way to see it.

## The ground is where the types live

Every space in Safari has a record, and every record is flat:

| Space | Record | Fields |
|---|---|---|
| On the road | `Geom.RoadPoint` | `along`, `across` |
| From the rider | `RiderView.RiderPoint` | `right`, `forward` |
| On the screen | `Screen.Point` | `x`, `y` |

The horizontal axes got real types. `Along` and `Across` are places, and two places give a `Distance`, which is the book's "places and distances". You can't pass an `Along` where an `Across` is wanted.

Height arrives as one more field on top:

| Where | Field | Type | What it means |
|---|---|---|---|
| `Geom.Placed`, `Spot` | `lift` | `Distance` | how far off the ground an object stands |
| `RiderView.RaisedPoint` | `height` | `Distance` | above the rider's level, negative where the ground curves away |
| each kind | `scenery_height` | `Distance` | how tall the thing is |
| far scenery | `FarHeight` | its own type | how high above the horizon, in pixels at rest |

So near heights are bare `Distance`s. The type doesn't say "vertical". Only the field name does.

## Three kinds of object, by what they're missing

Your "lack depth, not height" gives a clean three-way split:

| Kind | Examples | Has | Lacks |
|---|---|---|---|
| Solids | the truck, the towers, the guard rails, the ground patches | every corner has its own along, across and height | nothing |
| Cards | the cat, the bird, the billboards, the trees | a foot on the road, a width and a height on screen | depth: they're flat, and always face you |
| Far scenery | the sun, the mountains, the rolling land | a bearing and a `FarHeight` | distance: they never come nearer |

That table could go in the book, near the projection chapter. It says why a card is drawn from one projected foot plus a size, while a solid is projected corner by corner.

## Standing and perching

Most things stand: their `lift` is zero. A few perch:

- The bird's perch is a tree top, and the code says so directly: `tree_top = { road_point, lift: tree.kind.scenery_height() }` (BirdFlight.roc:116). A tree's *height* becomes the bird's *lift*. They're the same type, so that line needs no conversion, and it reads right.
- The beacon sits on top of its tower. Its height is the tower's lift plus the height on the tower, minus how far the tower has sunk (Tower.roc:211).
- The cat's leap lifts it 0.27 m off the road for a frame.

So "lift" already is the elevation of an object's foot, and "height" is the size of the thing standing on it. Add a size to an elevation and you get an elevation: the bird's perch is the tree's foot raised by the tree's height.

## Your point about differences

The horizontal axes are places and distances: an `Along` minus an `Along` is a `Distance`. Followed through for the vertical axis, that gives an elevation type as the vertical place, and the difference of two elevations is a distance along z, as you said.

There are two ways to say that in types:

- **A. Keep `Distance`, and let the field name carry the axis.** This is what we have. It costs nothing, and the field names (`lift`, `height`) are consistent. The risk is the classic swap: a height passed where an along-the-road distance is wanted would type-check. I haven't seen that bug in this code.
- **B. Give the vertical axis its own types,** the way `Along` and `Across` work for the horizontal ones. An `Elevation` would be a place above the ground. Two elevations would give a `Rise`, a vertical distance. An elevation plus a rise would give an elevation, and `scenery_height` would be a `Rise`. Then a rise couldn't be passed as a distance along the road. The reach is wide: every `lift`, `height` and `scenery_height`, the camera, EarthCurve, the solids and the cards.

**Lean: A for now, B noted for after the book.** The horizontal types earned their place because the code mixes along and across constantly. Heights are rarer, and their field names have kept them straight.

## Far heights, where the mixing has really happened

`FarHeight` is the one spot where position and size do get mixed, and the code shows it:

- **Places:** the sun's height above the horizon, and a range's height at a bearing (`Skyline.range_height`).
- **Sizes:** `snow_dip` (10), `thinnest_snow` (0.01), and the sun's disc. These are spans, not places.
- `Lens.size_on_screen : { size : FarHeight, ... }` takes a far "height" that is really a size.

That's the same split as above, in the far space. `FarHeight` is the place, and the difference of two far heights is a far span. Your objection to calling it a length stands: it's vertical, and it's measured at infinity.

**Lean:** split it, because here the mixing is real. `FarHeight` stays the place. A new type, `FarRise` (by analogy with B's `Rise`), is the span: `FarHeight.minus` gives a `FarRise`, and `Lens.size_on_screen` takes one. It's small: SunPath, Sun, Skyline, Lens and the sky. The name is yours if `FarRise` doesn't sit right.

## One question

Do you want the three-kinds table (solids, cards, far scenery) in the book? I'd put it where projection first comes up, so the cards' "one foot plus a size" is explained before the truck chapter shows a solid projected corner by corner.
