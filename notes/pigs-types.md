# Pigs, by its types

*2026-11-07. The output of Shale's new `cookbook:roc/type_walk.shale` on Safari's `Pigs`: every type `Pigs` depends on, the most primitive first and `Pigs` last, with each type's functions as doc and annotation and every body left out. Run from canvas_apps/safari as `shale cookbook:roc/type_walk.shale module=Pigs packages=lib=repos:roc-apps/canvas_apps/lib`. My review, made with `docs/smells.md` fresh, follows the listing. Nothing has been changed.*

```roc
# The types of Pigs and every type they depend on, the most primitive first.
# Builtin leaves, not expanded: Bool, F64, I64, List, Str, U32, U64
# Type variables, not followed: context (Picture.Setting); kind (Geom.Placed)

#### Billboard.Facing   (Billboard.roc:18)
## Which way a billboard faces on screen.
Facing : [FacesLeft, FacesRight]

#### Brush.Rgba   (repos:roc-apps/canvas_apps/lib/Brush.roc:14)
# Red, green and blue in 0..255, alpha in 0..1.
Rgba : { r : F64, g : F64, b : F64, a : F64 }

#### Brush.Fill   (repos:roc-apps/canvas_apps/lib/Brush.roc:16)
Fill : [
	Skip,
	Flat(Brush.Rgba),
	# Mode 1: edge, middle, edge, across [x0, x1].
	Span({ edge : Brush.Rgba, middle : Brush.Rgba, x0 : F64, x1 : F64 }),
	# Mode 2: from radius r0 to r1 about (x, y).
	Radial({ inner : Brush.Rgba, outer : Brush.Rgba, x : F64, y : F64, r0 : F64, r1 : F64 }),
	# Mode 3: two stops along a..a+d, at offsets o0 <= o1.
	Linear({ c0 : Brush.Rgba, c1 : Brush.Rgba, o0 : F64, o1 : F64, ax : F64, ay : F64, dx : F64, dy : F64 }),
	# Mode 4: two stops out from (x, y) through the ellipse whose inverse is
	# ia ib / ic id, taking a scene offset to the unit circle.
	Ellipse({ c0 : Brush.Rgba, c1 : Brush.Rgba, o0 : F64, o1 : F64, x : F64, y : F64, ia : F64, ib : F64, ic : F64, id : F64 }),
	# The sun's glow: stops at 0, 0.4 and 1, from radius r0 to r1 about (x, y).
	Glow({ c0 : Brush.Rgba, c1 : Brush.Rgba, c2 : Brush.Rgba, x : F64, y : F64, r0 : F64, r1 : F64 }),
]

#### Distance   (Distance.roc:5)
## A length in metres: how long a segment is, how tall a tree stands, how far
## the rider is from a cat. A length measured toward something can run past it,
## so a gap goes negative once the rider is beyond what it is measured to.
Distance :: F64.{
	metres : F64 -> Distance

	to_metres : Distance -> F64

	plus : Distance, Distance -> Distance

	minus : Distance, Distance -> Distance

	times : Distance, F64 -> Distance

	divided_by : Distance, F64 -> Distance

	## This length measured the other way.
	opposite : Distance -> Distance

	## How many of `whole` this is, which can pass 1.
	ratio_to : Distance, Distance -> F64

	## The smaller of this length and `other`.
	min : Distance, Distance -> Distance

	## The larger of this length and `other`.
	max : Distance, Distance -> Distance

	is_gt : Distance, Distance -> Bool

	is_gte : Distance, Distance -> Bool

	is_lt : Distance, Distance -> Bool

	is_lte : Distance, Distance -> Bool
}

#### Across   (Across.roc:7)
## A place across the road, in metres from the middle of the road, growing to the
## right. A distance added to a place gives a place, and two places give the
## distance between them, but two places can't be added. A place across the road
## can't be passed as a place along it.
Across :: F64.{
	metres : F64 -> Across

	to_metres : Across -> F64

	## The place `distance` to the right of the middle of the road.
	right_of_middle : Distance -> Across

	## The place `distance` to the left of the middle of the road.
	left_of_middle : Distance -> Across

	## How far this place is from the middle of the road, to either side.
	distance_from_middle : Across -> Distance

	## The place `distance` further right.
	plus : Across, Distance -> Across

	## The place `distance` further left.
	minus : Across, Distance -> Across

	## How far this place is to the right of `other`: negative when it is to
	## the left.
	distance_from : Across, Across -> Distance

	## This place, its distance from the middle of the road scaled by `factor`.
	times : Across, F64 -> Across

	## The place further left of this one and `other`.
	min : Across, Across -> Across

	## The place further right of this one and `other`.
	max : Across, Across -> Across

	is_gt : Across, Across -> Bool

	is_gte : Across, Across -> Bool

	is_lt : Across, Across -> Bool

	is_lte : Across, Across -> Bool
}

#### Along   (Along.roc:9)
## A place along the road, in metres from an origin its holder names, most often
## the start of a segment.
## `Along` and `Across` mirror `Angle.Bearing` and `Angle.Turn`: a distance added
## to a place gives a place, and two places give the distance between them, but
## two places can't be added. A place along the road can't be passed as a place
## across it.
Along :: F64.{
	metres : F64 -> Along

	to_metres : Along -> F64

	## The place this far from the segment's start.
	at : Distance -> Along

	## How far this place is from the segment's start.
	from_start : Along -> Distance

	## The place `distance` further along.
	plus : Along, Distance -> Along

	## The place `distance` back along.
	minus : Along, Distance -> Along

	## How far this place is ahead of `other`: negative when it is behind.
	distance_from : Along, Along -> Distance

	is_gt : Along, Along -> Bool

	is_gte : Along, Along -> Bool

	is_lt : Along, Along -> Bool

	is_lte : Along, Along -> Bool
}

#### Geom.Placed   (Geom.roc:40)
## An object standing on one segment of the road, and what kind of object
## it is. A tree or a cow is placed once for the whole ride; a cat, a tower or
## the truck is placed anew for each frame. `Pipeline.sighting_of` turns it
## into a `Pipeline.Sighted` for a frame.
Placed(kind) : {
	along : Along,
	across : Across,
	kind : kind,
}

#### Geom.RaisedPoint   (Geom.roc:27)
## A point in the rider's view, at a height above the level of the rider.
## All three parts are signed: `right` and `forward` as on a `RiderPoint`,
## and a negative `height` is below that level, where the ground curves
## away.
RaisedPoint : {
	right : Distance,
	forward : Distance,
	height : Distance,
}

#### Geom.AheadPoint   (Geom.roc:171)
## A point in the rider's view at or past the near plane, so the camera can
## put it on the screen. Only `ahead_point` and the near-plane cut build
## one.
AheadPoint :: Geom.RaisedPoint.{
	right : Geom.AheadPoint -> Distance

	forward : Geom.AheadPoint -> Distance

	height : Geom.AheadPoint -> Distance

	to_raised : Geom.AheadPoint -> Geom.RaisedPoint

	## The point at `height` instead. It is as far ahead, so still in view.
	at_height : Geom.AheadPoint, Distance -> Geom.AheadPoint

	## The point at `right` instead. It is as far ahead, so still in view.
	at_right : Geom.AheadPoint, Distance -> Geom.AheadPoint
}

#### Pixels   (Pixels.roc:9)
## A length on screen, in pixels, whole or not: how tall a cat stands, where a
## point lands, how long the camera's lens is. It is signed. A place on screen
## is measured from the corner, so a point off the left of the screen is
## negative, and so is the height of a sun below the horizon.
##
## Pixels stop at the edge of `lib.Shapes`, which takes plain numbers, and at
## trigonometry.
Pixels :: F64.{
	of : F64 -> Pixels

	to_f64 : Pixels -> F64

	plus : Pixels, Pixels -> Pixels

	minus : Pixels, Pixels -> Pixels

	times : Pixels, F64 -> Pixels

	divided_by : Pixels, F64 -> Pixels

	## This length measured the other way.
	opposite : Pixels -> Pixels

	## This length, whichever way it is measured.
	abs : Pixels -> Pixels

	## How many of `whole` this is, which can pass 1 or go negative.
	ratio_to : Pixels, Pixels -> F64

	## The larger of this length and `other`.
	max : Pixels, Pixels -> Pixels

	is_gt : Pixels, Pixels -> Bool

	is_gte : Pixels, Pixels -> Bool

	is_lt : Pixels, Pixels -> Bool

	is_lte : Pixels, Pixels -> Bool
}

#### Picture.Setting   (Picture.roc:14)
## What a kind of object draws its picture from: where its foot stands from
## the camera, on the rider's level and past the near plane, the camera's
## focal length, and `context`, which is whatever else that kind needs. A
## kind that needs nothing more takes `{}`.
Setting(context) : {
	foot : Geom.AheadPoint,
	cam_focal : Pixels,
	context : context,
}

#### Shapes.Align   (repos:roc-apps/canvas_apps/lib/Shapes.roc:55)
Align : [Left, Center]

#### Shapes.Face   (repos:roc-apps/canvas_apps/lib/Shapes.roc:53)
## `Prose` is the viewer's own sans serif, for words. `Code` is a monospace, for
## what a program says.
Face : [Prose, Code]

#### Shapes.Line   (repos:roc-apps/canvas_apps/lib/Shapes.roc:41)
## A line of type. `y` is its baseline, `x` its left end or its middle as `align`
## says, and `size` the height of its em square, as in CSS. The viewer's machine
## chooses the typeface and measures the words, so nothing in Roc knows how wide
## the line came out: `Font.room_for` is the room to leave for it.
Line : {
	text : Str,
	x : F64,
	y : F64,
	size : F64,
	face : Shapes.Face,
	align : Shapes.Align,
	color : Brush.Rgba,
}

#### Shapes.Mode   (repos:roc-apps/canvas_apps/lib/Shapes.roc:59)
## `Over` paints over what is there. `Add` adds light to it, which is what a glow
## is.
Mode : [Over, Add]

#### Shapes.Space   (repos:roc-apps/canvas_apps/lib/Shapes.roc:64)
## The space the shapes after a `View` mark are in. `Screen` is the game's own
## pixels, where every frame starts. `World` carries plain numbers rather than a
## Camera, because the mark crosses to JavaScript, which has no such type.
Space : [
	Screen,
	World({ target : { x : F64, y : F64 }, offset : { x : F64, y : F64 }, rotation : F64, zoom : F64 }),
]

#### Shapes.Shape   (repos:roc-apps/canvas_apps/lib/Shapes.roc:9)
## One thing in a frame. A later shape in the list paints over an earlier one.
Shape : [
	## A polygon, as x0, y0, x1, y1 and so on. It can be any polygon, until `cut_shapes`
	## leaves only convex ones for a painter that fills nothing else.
	Poly({ coordinates : List(F64), fill : Brush.Fill }),

	## The triangles of one concave polygon, six numbers each. Only `cut_shapes` makes these.
	Pieces({ tris : List(F64), fill : Brush.Fill }),

	Disc({ x : F64, y : F64, r : F64, fill : Brush.Fill }),
	Rect({ x : F64, y : F64, w : F64, h : F64, fill : Brush.Fill }),

	## A mark, not a shape: how the shapes after it combine, until the next `Blend`.
	## A painter holds this as a mode, so a mark in the list says it directly.
	Blend(Shapes.Mode),

	## A mark, not a shape: the space the shapes after it are in, until the next
	## `View`. It is a mark for the same reason `Blend` is.
	View(Shapes.Space),

	## `cols` by `rows` pixels stretched over the box without smoothing. It carries
	## the pixels, not a handle, so there is no second copy of them to keep in step.
	Image({ x : F64, y : F64, w : F64, h : F64, cols : U64, rows : U64, pixels : List(Brush.Rgba) }),

	## A line of words in a real typeface. `Font.plotted` gives a painter that has
	## no typefaces the strokes of the same line.
	Text(Shapes.Line),
]

#### Picture   (Picture.roc:8)
## A Picture is how one object looks in one frame: the shapes that paint it,
## in order. Outside this module a picture is a single thing, handed along
## whole until something paints it.
Picture :: List(Shapes.Shape).{
	from_shapes : List(Shapes.Shape) -> Picture

	to_shapes : Picture -> List(Shapes.Shape)
}

#### Billboard   (Billboard.roc:11)
## A billboard is a critter that stands in one place and always faces the
## camera: the emoji still for its codepoint, at a height, facing left or right.
Billboard := {
	codepoint : I64,
	height : Distance,
	facing : Billboard.Facing,
}.{
	scenery_height : Billboard -> Distance

	## How a billboard looks. An emoji faces left, so a billboard facing right
	## is its still mirrored. One less than a pixel tall isn't drawn.
	scenery_picture : Billboard, Picture.Setting({}) -> Picture
}

#### Pigs.PigInterest   (Pigs.roc:18)
## What a built segment's pigs are to the rider: there are none, the rider
## passes them by, or this one of them catches the eye.
PigInterest : [NoPigs, Unnoticed, Distracting(Geom.Placed(Billboard))]

#### Pigs.PigPresence   (Pigs.roc:14)
## Whether the route plans pigs along a segment.
PigPresence : [WithPigs, NoPigs]

#### Pigs   (Pigs.roc:11)
## Pigs graze on the right of the road near the end of a segment. On the
## first few segments with pigs they are a big herd, and one pig of that herd
## catches the rider's eye. After that, they stand in two short rows.
Pigs :: [].{
	has_pigs : Pigs.PigPresence -> Bool

	## How the pigs of a segment `length` long strike the rider, when
	## `pig_segments_so_far` of the route's segments, this one included, have pigs.
	## The pig that catches the eye is the third in the row nearest the road.
	interest_of : {
		presence : Pigs.PigPresence,
		pig_segments_so_far : U32,
		length : Distance,
	} -> Pigs.PigInterest

	## The pigs on a segment `length` long: a big herd where they catch the
	## rider's eye, and two rows where they don't.
	pigs_along : { interest : Pigs.PigInterest, length : Distance } -> List(Geom.Placed(Billboard))

	## The big herd on a segment `length` long, row by row from the road.
	big_herd_pigs : Distance -> List(Geom.Placed(Billboard))

	## The two rows of pigs on a segment `length` long, front row first.
	two_rows : Distance -> List(Geom.Placed(Billboard))
}

# 22 types, 69 functions, 10 modules, 7 leaves, 2 type variables
```

## What smells

**1. `PigInterest` names the rider's reaction, and it's really the herd's layout.** This is the one I'd fix first.

- `Distracting` is always a big herd and `Unnoticed` is always two rows: `pigs_along` maps one to the other and nothing else. So the type's real meaning is how the pigs stand, and the names describe the rider's attention instead. That's *one word carries two meanings*, and *knowledge in the wrong module*: whether something is distracting is Gaze's business.
- `NoPigs` is a tag of both `PigPresence` and `PigInterest`.
- `has_pigs : PigPresence -> Bool` exists only so World can count segments with pigs. It turns a two-tag union straight back into a Bool.
- `interest_of` takes `pig_segments_so_far`, "this one included", even when `presence` is `NoPigs`, where the count means nothing. An inclusive count is also an off-by-one waiting to happen, and the novelty test is `<= pig_novelty_count` because of it.
- The pig that stands out is placed twice: once by `interest_of`, as `herd_pig(row: 0, column: 2)`, and again inside `big_herd_pigs`. An expect checks that the two agree.

**2. `Billboard.codepoint : I64`.** An emoji's codepoint is never negative, and nothing says it's a codepoint but the field name. *A bare type hides a concept*: it wants `U32` at least, or a small type of its own that the Stills look up by.

**3. `two_rows` gives a list of pigs**, beside `big_herd_pigs`. The name says rows, not pigs, and breaks the pair. `two_row_pigs` matches.

**4. `Picture.Setting` says the foot is "on the rider's level", and its type is `Geom.AheadPoint`, which has a `height`.** *A wrong state can be written down*: a setting with a raised foot type-checks. Small, but it's the same smell the opaque point type just fixed one level down.

**5. `Along` has an origin "its holder names".** Most holders mean the segment's start, and `Along.at` and `from_start` assume it, but Pond measures from the segment's end. One type, two origins (the drawing-half review's finding 15).

**6. Shared lib types have field names a reader can't decode:** `Brush.Fill`'s `c0`, `o0`, `ia`, `ib`, `ic`, `id`, with "Mode 1" comments. They cross to JavaScript, which may be why, but the Roc side could still say what they are.

**About the tool:** it leaves out constants, so `pig_codepoint : I64` and `big_herd_columns : I64` beside `pig_novelty_count : U32` (signed counts beside unsigned ones) don't show. A constant's annotation is part of a module's types, and I'd add them in v2.

## The fix I'd make: the herd, not the reaction

Before:

```roc
## Whether the route plans pigs along a segment.
PigPresence : [WithPigs, NoPigs]

## What a built segment's pigs are to the rider: there are none, the rider
## passes them by, or this one of them catches the eye.
PigInterest : [NoPigs, Unnoticed, Distracting(Geom.Placed(Billboard))]

has_pigs : Pigs.PigPresence -> Bool

## How the pigs of a segment `length` long strike the rider, when
## `pig_segments_so_far` of the route's segments, this one included, have pigs.
## The pig that catches the eye is the third in the row nearest the road.
interest_of : {
	presence : Pigs.PigPresence,
	pig_segments_so_far : U32,
	length : Distance,
} -> Pigs.PigInterest

pigs_along : { interest : Pigs.PigInterest, length : Distance } -> List(Geom.Placed(Billboard))
big_herd_pigs : Distance -> List(Geom.Placed(Billboard))
two_rows : Distance -> List(Geom.Placed(Billboard))
```

After:

```roc
## Whether the route plans pigs along a segment.
PigPresence : [WithPigs, NoPigs]

## How a built segment's pigs stand. The route's first few herds are big, and
## one pig of a big herd, the third in the row nearest the road, stands out.
## After that, pigs stand in two short rows.
PigHerd : [NoPigs, TwoRows, BigHerd({ standout : Geom.Placed(Billboard) })]

## How the pigs of a segment `length` long stand, after `earlier_herds`
## segments of the route have had pigs.
herd_of : PigPresence, { earlier_herds : U32, length : Distance } -> Pigs.PigHerd

herd_pigs : Pigs.PigHerd, Distance -> List(Geom.Placed(Billboard))
big_herd_pigs : Distance -> List(Geom.Placed(Billboard))
two_row_pigs : Distance -> List(Geom.Placed(Billboard))
```

- The type says how the pigs stand, which is what Pigs knows. Gaze matches `BigHerd({ standout })` and decides for itself that a standout pig catches the eye.
- `has_pigs` goes: World counts with `plan.pigs == WithPigs`.
- `earlier_herds` counts the herds before this one, so the novelty test reads `earlier_herds < pig_novelty_count`, and a segment with no pigs never has a count to misread.
- `herd_pigs` places the big herd, and `herd_of` takes its standout from that same list, so there's one placement of that pig.
- `NoPigs` still names "no pigs" in both unions, but now it means the same thing in both.

No pixel should move. Gaze, World and Pigs' own expects change their tag names.

## After the fix

*Built as Steve shaped it: `PigInterest` stays the rider's setting, `[Unnoticed, Distracting]`, decided apart from the herd's shape. Each layout is a type holding its own constants, and each answers its own pigs and standout pig. `has_pigs` is gone, the count of earlier herds no longer includes this one, and `Billboard.codepoint` is a `U32`. The setting's foot is now a `Geom.LevelPoint` with no height, and Pond's points hold `past_end : Distance`, so `Along` has one origin. No pixel moved. The types tool now shows constants, marked `# constant`.*

```roc
── budgets from the script's header: steps=800000000, output_bytes=8000000, arena_bytes=2000000000
# The types of Pigs and every type they depend on, the most primitive first.
# Builtin leaves, not expanded: Bool, F64, List, Str, U32, U64
# Type variables, not followed: context (Picture.Setting); kind (Geom.Placed)

#### Billboard.Facing   (Billboard.roc:18)
## Which way a billboard faces on screen.
Facing : [FacesLeft, FacesRight]

#### Brush.Rgba   (repos:lanes/pig-herds/canvas_apps/lib/Brush.roc:15)
# Red, green and blue in 0..255, alpha in 0..1.
Rgba : { r : F64, g : F64, b : F64, a : F64 }

#### Brush.Fill   (repos:lanes/pig-herds/canvas_apps/lib/Brush.roc:17)
Fill : [
	Skip,
	Flat(Brush.Rgba),
	# Mode 1: edge, middle, edge, across [x0, x1].
	Span({ edge : Brush.Rgba, middle : Brush.Rgba, x0 : F64, x1 : F64 }),
	# Mode 2: from radius r0 to r1 about (x, y).
	Radial({ inner : Brush.Rgba, outer : Brush.Rgba, x : F64, y : F64, r0 : F64, r1 : F64 }),
	# Mode 3: two stops along a..a+d, at offsets o0 <= o1.
	Linear({ c0 : Brush.Rgba, c1 : Brush.Rgba, o0 : F64, o1 : F64, ax : F64, ay : F64, dx : F64, dy : F64 }),
	# Mode 4: two stops out from (x, y) through the ellipse whose inverse is
	# ia ib / ic id, taking a scene offset to the unit circle.
	Ellipse({ c0 : Brush.Rgba, c1 : Brush.Rgba, o0 : F64, o1 : F64, x : F64, y : F64, ia : F64, ib : F64, ic : F64, id : F64 }),
	# The sun's glow: stops at 0, 0.4 and 1, from radius r0 to r1 about (x, y).
	Glow({ c0 : Brush.Rgba, c1 : Brush.Rgba, c2 : Brush.Rgba, x : F64, y : F64, r0 : F64, r1 : F64 }),
]

#### Distance   (Distance.roc:5)
## A length in metres: how long a segment is, how tall a tree stands, how far
## the rider is from a cat. A length measured toward something can run past it,
## so a gap goes negative once the rider is beyond what it is measured to.
Distance :: F64.{
	metres : F64 -> Distance

	to_metres : Distance -> F64

	## No length at all.
	zero : Distance   # constant

	plus : Distance, Distance -> Distance

	minus : Distance, Distance -> Distance

	times : Distance, F64 -> Distance

	divided_by : Distance, F64 -> Distance

	## This length measured the other way.
	opposite : Distance -> Distance

	## How many of `whole` this is, which can pass 1.
	ratio_to : Distance, Distance -> F64

	## The smaller of this length and `other`.
	min : Distance, Distance -> Distance

	## The larger of this length and `other`.
	max : Distance, Distance -> Distance

	is_gt : Distance, Distance -> Bool

	is_gte : Distance, Distance -> Bool

	is_lt : Distance, Distance -> Bool

	is_lte : Distance, Distance -> Bool
}

#### Across   (Across.roc:7)
## A place across the road, in metres from the middle of the road, growing to the
## right. A distance added to a place gives a place, and two places give the
## distance between them, but two places can't be added. A place across the road
## can't be passed as a place along it.
Across :: F64.{
	metres : F64 -> Across

	to_metres : Across -> F64

	## The middle of the road.
	middle : Across   # constant

	## The place `distance` to the right of the middle of the road.
	right_of_middle : Distance -> Across

	## The place `distance` to the left of the middle of the road.
	left_of_middle : Distance -> Across

	## How far this place is from the middle of the road, to either side.
	distance_from_middle : Across -> Distance

	## The place `distance` further right.
	plus : Across, Distance -> Across

	## The place `distance` further left.
	minus : Across, Distance -> Across

	## How far this place is to the right of `other`: negative when it is to
	## the left.
	distance_from : Across, Across -> Distance

	## This place, its distance from the middle of the road scaled by `factor`.
	times : Across, F64 -> Across

	## The place further left of this one and `other`.
	min : Across, Across -> Across

	## The place further right of this one and `other`.
	max : Across, Across -> Across

	is_gt : Across, Across -> Bool

	is_gte : Across, Across -> Bool

	is_lt : Across, Across -> Bool

	is_lte : Across, Across -> Bool
}

#### Along   (Along.roc:9)
## A place along the road, in metres from an origin its holder names, most often
## the start of a segment.
## `Along` and `Across` mirror `Angle.Bearing` and `Angle.Turn`: a distance added
## to a place gives a place, and two places give the distance between them, but
## two places can't be added. A place along the road can't be passed as a place
## across it.
Along :: F64.{
	metres : F64 -> Along

	to_metres : Along -> F64

	## The segment's start.
	start : Along   # constant

	## The place this far from the segment's start.
	at : Distance -> Along

	## How far this place is from the segment's start.
	from_start : Along -> Distance

	## The place `distance` further along.
	plus : Along, Distance -> Along

	## The place `distance` back along.
	minus : Along, Distance -> Along

	## How far this place is ahead of `other`: negative when it is behind.
	distance_from : Along, Along -> Distance

	is_gt : Along, Along -> Bool

	is_gte : Along, Along -> Bool

	is_lt : Along, Along -> Bool

	is_lte : Along, Along -> Bool
}

#### Geom.Placed   (Geom.roc:40)
## An object standing on one segment of the road, and what kind of object
## it is. A tree or a cow is placed once for the whole ride; a cat, a tower or
## the truck is placed anew for each frame. `Pipeline.sighting_of` turns it
## into a `Pipeline.Sighted` for a frame.
Placed(kind) : {
	along : Along,
	across : Across,
	kind : kind,
}

#### Geom.RaisedPoint   (Geom.roc:27)
## A point in the rider's view, at a height above the level of the rider.
## All three parts are signed: `right` and `forward` as on a `RiderPoint`,
## and a negative `height` is below that level, where the ground curves
## away.
RaisedPoint : {
	right : Distance,
	forward : Distance,
	height : Distance,
}

#### Geom.AheadPoint   (Geom.roc:171)
## A point in the rider's view at or past the near plane, so the camera can
## put it on the screen. Only `ahead_point` and the near-plane cut build
## one.
AheadPoint :: Geom.RaisedPoint.{
	right : Geom.AheadPoint -> Distance

	forward : Geom.AheadPoint -> Distance

	height : Geom.AheadPoint -> Distance

	to_raised : Geom.AheadPoint -> Geom.RaisedPoint

	## The point at `height` instead. It is as far ahead, so still in view.
	at_height : Geom.AheadPoint, Distance -> Geom.AheadPoint

	## The point at `right` instead. It is as far ahead, so still in view.
	at_right : Geom.AheadPoint, Distance -> Geom.AheadPoint
}

#### Pixels   (Pixels.roc:9)
## A length on screen, in pixels, whole or not: how tall a cat stands, where a
## point lands, how long the camera's lens is. It is signed. A place on screen
## is measured from the corner, so a point off the left of the screen is
## negative, and so is the height of a sun below the horizon.
##
## Pixels stop at the edge of `lib.Shapes`, which takes plain numbers, and at
## trigonometry.
Pixels :: F64.{
	of : F64 -> Pixels

	to_f64 : Pixels -> F64

	## No length at all.
	zero : Pixels   # constant

	plus : Pixels, Pixels -> Pixels

	minus : Pixels, Pixels -> Pixels

	times : Pixels, F64 -> Pixels

	divided_by : Pixels, F64 -> Pixels

	## This length measured the other way.
	opposite : Pixels -> Pixels

	## This length, whichever way it is measured.
	abs : Pixels -> Pixels

	## How many of `whole` this is, which can pass 1 or go negative.
	ratio_to : Pixels, Pixels -> F64

	## The larger of this length and `other`.
	max : Pixels, Pixels -> Pixels

	is_gt : Pixels, Pixels -> Bool

	is_gte : Pixels, Pixels -> Bool

	is_lt : Pixels, Pixels -> Bool

	is_lte : Pixels, Pixels -> Bool
}

#### Picture.Setting   (Picture.roc:14)
## What a kind of object draws its picture from: where its foot stands from
## the camera, on the rider's level and past the near plane, the camera's
## focal length, and `context`, which is whatever else that kind needs. A
## kind that needs nothing more takes `{}`.
Setting(context) : {
	foot : Geom.AheadPoint,
	cam_focal : Pixels,
	context : context,
}

#### Shapes.Align   (repos:lanes/pig-herds/canvas_apps/lib/Shapes.roc:56)
Align : [Left, Center]

#### Shapes.Face   (repos:lanes/pig-herds/canvas_apps/lib/Shapes.roc:54)
## `Prose` is the viewer's own sans serif, for words. `Code` is a monospace, for
## what a program says.
Face : [Prose, Code]

#### Shapes.Line   (repos:lanes/pig-herds/canvas_apps/lib/Shapes.roc:42)
## A line of type. `y` is its baseline, `x` its left end or its middle as `align`
## says, and `size` the height of its em square, as in CSS. The viewer's machine
## chooses the typeface and measures the words, so nothing in Roc knows how wide
## the line came out: `Font.room_for` is the room to leave for it.
Line : {
	text : Str,
	x : F64,
	y : F64,
	size : F64,
	face : Shapes.Face,
	align : Shapes.Align,
	color : Brush.Rgba,
}

#### Shapes.Mode   (repos:lanes/pig-herds/canvas_apps/lib/Shapes.roc:60)
## `Over` paints over what is there. `Add` adds light to it, which is what a glow
## is.
Mode : [Over, Add]

#### Shapes.Space   (repos:lanes/pig-herds/canvas_apps/lib/Shapes.roc:65)
## The space the shapes after a `View` mark are in. `Screen` is the game's own
## pixels, where every frame starts. `World` carries plain numbers rather than a
## Camera, because the mark crosses to JavaScript, which has no such type.
Space : [
	Screen,
	World({ target : { x : F64, y : F64 }, offset : { x : F64, y : F64 }, rotation : F64, zoom : F64 }),
]

#### Shapes.Shape   (repos:lanes/pig-herds/canvas_apps/lib/Shapes.roc:10)
## One thing in a frame. A later shape in the list paints over an earlier one.
Shape : [
	## A polygon, as x0, y0, x1, y1 and so on. It can be any polygon, until `cut_shapes`
	## leaves only convex ones for a painter that fills nothing else.
	Poly({ coordinates : List(F64), fill : Brush.Fill }),

	## The triangles of one concave polygon, six numbers each. Only `cut_shapes` makes these.
	Pieces({ tris : List(F64), fill : Brush.Fill }),

	Disc({ x : F64, y : F64, r : F64, fill : Brush.Fill }),
	Rect({ x : F64, y : F64, w : F64, h : F64, fill : Brush.Fill }),

	## A mark, not a shape: how the shapes after it combine, until the next `Blend`.
	## A painter holds this as a mode, so a mark in the list says it directly.
	Blend(Shapes.Mode),

	## A mark, not a shape: the space the shapes after it are in, until the next
	## `View`. It is a mark for the same reason `Blend` is.
	View(Shapes.Space),

	## `cols` by `rows` pixels stretched over the box without smoothing. It carries
	## the pixels, not a handle, so there is no second copy of them to keep in step.
	Image({ x : F64, y : F64, w : F64, h : F64, cols : U64, rows : U64, pixels : List(Brush.Rgba) }),

	## A line of words in a real typeface. `Font.plotted` gives a painter that has
	## no typefaces the strokes of the same line.
	Text(Shapes.Line),
]

#### Picture   (Picture.roc:8)
## A Picture is how one object looks in one frame: the shapes that paint it,
## in order. Outside this module a picture is a single thing, handed along
## whole until something paints it.
Picture :: List(Shapes.Shape).{
	from_shapes : List(Shapes.Shape) -> Picture

	to_shapes : Picture -> List(Shapes.Shape)
}

#### Billboard   (Billboard.roc:11)
## A billboard is a critter that stands in one place and always faces the
## camera: the emoji still for its codepoint, at a height, facing left or right.
Billboard := {
	codepoint : U32,
	height : Distance,
	facing : Billboard.Facing,
}.{
	scenery_height : Billboard -> Distance

	## How a billboard looks. An emoji faces left, so a billboard facing right
	## is its still mirrored. One less than a pixel tall isn't drawn.
	scenery_picture : Billboard, Picture.Setting({}) -> Picture
}

#### Pigs.BigPigHerd   (Pigs.roc:24)
## A big herd: rows of columns, each pig strayed a little from its place.
## The first row is nearest the road, and each row behind it stands
## `row_depth` farther from the road and as far again along it.
BigPigHerd := {
	columns : U64,
	rows : U64,

	## Where the first column is along the road, from the pigs' place.
	first_column : Distance,

	## The distance between columns, along the road.
	column_spacing : Distance,
	row_depth : Distance,

	## How far a pig strays from its place, along the road and across it.
	jitter_along : Distance,
	jitter_across : Distance,

	## Which pig of the row nearest the road stands out, counting from 0.
	standout_column : U64,
}.{
	## The herd's pigs about `herd_along`, row by row from the road.
	big_herd_pigs : Pigs.BigPigHerd, Along -> List(Geom.Placed(Billboard))

	## The herd's pig that stands out, about `herd_along`.
	standout_pig : Pigs.BigPigHerd, Along -> Geom.Placed(Billboard)
}

#### Pigs.PigInterest   (Pigs.roc:19)
## How the rider takes a herd, whatever its shape.
PigInterest : [Unnoticed, Distracting]

#### Pigs.PigPresence   (Pigs.roc:13)
## Whether the route plans pigs along a segment.
PigPresence : [WithPigs, NoPigs]

#### Pigs.TwoRowPigHerd   (Pigs.roc:62)
## Two short rows of pigs, the back row farther from the road.
TwoRowPigHerd := {
	## Where the pigs of each row are along the road, from the pigs' place.
	front_offsets : List(Distance),
	back_offsets : List(Distance),

	## How much farther from the road the back row stands than the front.
	back_row_offset : Distance,
}.{
	## The herd's pigs about `herd_along`, front row first.
	two_row_pigs : Pigs.TwoRowPigHerd, Along -> List(Geom.Placed(Billboard))

	## The herd's pig that stands out, about `herd_along`: the middle pig of
	## the front row, the later of the two middle ones when the row is even.
	standout_pig : Pigs.TwoRowPigHerd, Along -> Geom.Placed(Billboard)
}

#### Pigs.PigHerd   (Pigs.roc:16)
## How a segment's pigs stand.
PigHerd : [NoPigs, BigHerd(Pigs.BigPigHerd), TwoRows(Pigs.TwoRowPigHerd)]

#### Pigs   (Pigs.roc:10)
## Pigs graze on the right of the road near the end of a segment, in a big
## herd or in two short rows. One pig of each herd stands out from the rest.
Pigs :: [].{
	pig_codepoint : U32   # constant

	pig_height : Distance   # constant

	## How far before the end of its segment the pigs are.
	pig_distance_before_end : Distance   # constant

	## The route's big herd, seven rows of seven.
	big_pig_herd : Pigs.BigPigHerd   # constant

	## The route's two-row herd, four pigs in front and six behind.
	two_row_pig_herd : Pigs.TwoRowPigHerd   # constant

	## The pigs of `herd` on a segment `length` long.
	herd_pigs : Pigs.PigHerd, Distance -> List(Geom.Placed(Billboard))

	## The pig of `herd` that stands out on a segment `length` long.
	standout_pig : Pigs.PigHerd, Distance -> [Standout(Geom.Placed(Billboard)), NoPigs]
}

# 25 types, 70 functions, 9 constants, 10 modules, 6 leaves, 2 type variables
```
