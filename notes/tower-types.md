# Tower's types, to depth 3

Made with `cookbook:roc/type_walk.shale module=Tower max_depth=3` (Shale 0d454b8), run on roc-apps master 30051405. I read docs/smells.md fresh first. Nothing is changed yet.

The walk prints 36 types, 131 functions and 20 constants across 15 modules, and names 8 types past depth 3 without following them. Tower's own block holds 31 of those members.

## Nitpicks, worst first

**1. Tower's block is a kitchen sink, like Pigs was.** It has 31 members: 14 constants, 15 helpers, `scenery_picture` and `tower_footprint`. Only three are used outside Tower.roc:
- `scenery_picture`, through `Pipeline`
- `tower_shapes` and `corner_offset`, both by the beacon widget

The rest are private helpers (`rod_quad`, `point_between`, `metre_px`, `ring_heights` and so on), but sitting in the block makes them Tower's public surface, and the walk reads them that way. Expects in the same file can call private top-level functions, as Pigs' expects already do, so nothing needs them public. The before and after is below.

**2. The drawing inputs are packed three ways.**
- `Picture.Setting` is `{ foot, cam_focal, context }`.
- `tower_shapes` takes its own record, `{ footprint, center, cam_focal, beacon_brightness }`.
- `TowerInView` is `{ footprint, center, sunk, view : { rod_width_px, cam_focal } }`.

`center` is the setting's `foot` under a second name, and `beacon_brightness` is a field of the kind that has been unpacked. `tower_shapes` has its own record only because the beacon widget can't build a `RoadContext`. If `tower_shapes` took `Tower, Picture.Setting(Tower.Footprint)`, one shape would serve both callers (see the after).

**3. `rod_shapes` answers a list for one rod or none.** This is the "return type is wider than the truth" smell, the same as `cat_in_view` was. The four-way match on `Geom.ahead_point` is the general near-plane cut of a line, and it belongs in Geom beside `near_plane_crossing`. One possible shape is `Geom.ahead_line : { from, to } -> Try({ from : AheadPoint, to : AheadPoint }, [BehindCamera])`. It's worth checking whether the road makes the same cut.

**4. Names.**
- `rod_w` is an abbreviation, and the abbreviation lint misses `_w`.
- `tower_half` and `rod_half` don't say half of what. Each is a half-width.
- `rod_width_px : Pixels`, `width_px` and `metre_px` repeat the type in the name.
- `TowerInView` reuses "in view", which elsewhere means past the near plane (`is_in_view`, `towers_in_view`). Here it means "everything a tower needs to become shapes". Folding it into item 2 may remove the need for a name.

**5. `brace_storeys : I64` is a count.** It can't go negative, so it wants `U64`, and so does the storey index `storey_shapes` takes.

**6. Heuristics.**
- `sink_radius` (20 km) is tuned so that a tower sinks visibly: on the real ground curve it would stay in view to 4 km. It's on the open list already.
- The beacon's thresholds `Fraction.of(0.02)` and `Pixels.of(0.5)` are inline and unnamed. Half a pixel is a rule worth naming. The 2% brightness looks tuned.

**7. `sunk` is "never negative" only in a comment.** The only thing guarding it is `sunk_below_horizon`'s arithmetic.

**8. Two smaller mirrors.**
- The `Footprint` record's four fields and the `Corner` tags list the same four corners, joined by `footprint_corner` and the `corners` list.
- `base_corner_on_road` takes an unnamed `{ along, across, yaw }`, which is a pose on the road with the same fields as `Geom.Vantage`.

Both are mild, and I'd leave them.

**9. Depth 3 pulls the whole route into Tower's walk.** The walk reaches `World.Segment`, `RoadAhead.RoadView` and the rest, because Tower's context is the whole road, used only to find four corners. Making the context `Setting(Tower.Footprint)` would cut all of that, but then `SceneShapes.road_context`, which also serves the truck, would have to ask the tower for its footprint. I'd keep it as it is and note the cost.

**10. Seen outside Tower.** `World.Segment` holds both `pigs : List(Geom.Placed(Billboard))` and `pig_herd`. The list is computed from the herd, so pigs have two homes. The Pigs split running now is in that code, so this can go with it or right after.

## Before and after: Tower's surface

Before, from the walk (abridged): 31 members.

```roc
Tower := { yaw : Angle.Turn, beacon_brightness : Fraction }.{
	scenery_picture : Tower, Picture.Setting(RoadAhead.RoadContext) -> Picture
	tower_footprint : Tower, RoadAhead.RoadContext -> Tower.Footprint
	tower_height : Distance   # constant
	tower_half : Distance   # constant
	storey_height : Distance   # constant
	brace_storeys : I64   # constant
	rod_half : Distance   # constant
	rod_w : Distance   # constant
	...eight more constants...
	Corner : [BackLeft, BackRight, FrontRight, FrontLeft]
	Footprint : { back_left : Geom.RiderPoint, ... }
	RodView : { rod_width_px : Pixels, cam_focal : Pixels }
	TowerInView : { footprint : Tower.Footprint, center : Geom.LevelPoint, sunk : Distance, view : Tower.RodView }
	next_corner, corner_offset, footprint_corner, base_corner_on_road,
	sunk_below_horizon, point_between, corner_at, screen_rod, rod_quad,
	rod_shapes, rod_on_screen, metre_px, rod_width_at, legs, ring_shapes,
	rings, braces, storey_shapes, brace_shapes, beacon_shapes : ...
	tower_shapes : {
		footprint : Tower.Footprint,
		center : Geom.LevelPoint,
		cam_focal : Pixels,
		beacon_brightness : Fraction,
	} -> List(Shapes.Shape)
}
```

After: the block holds what other modules use, and the rest moves below it as private functions and types.

```roc
## A tower in a frame: how it is turned, and how bright its beacon is.
Tower := { yaw : Angle.Turn, beacon_brightness : Fraction }.{

	## A corner of the tower's square footprint, as seen along the route.
	Corner : [BackLeft, BackRight, FrontRight, FrontLeft]

	## Where the footprint's four corners stand in the rider's view.
	Footprint : {
		back_left : Geom.RiderPoint,
		back_right : Geom.RiderPoint,
		front_right : Geom.RiderPoint,
		front_left : Geom.RiderPoint,
	}

	## How a tower looks. Its footprint is measured on the road, so the road and
	## where it stands there are its context.
	scenery_picture : Tower, Picture.Setting(RoadAhead.RoadContext) -> Picture

	## Where a tower's four footprint corners stand in the rider's view.
	tower_footprint : Tower, RoadAhead.RoadContext -> Tower.Footprint

	## The whole tower, once its footprint is in the rider's view: legs, rings,
	## braces and beacon, in that order. A tower sunk wholly below the horizon
	## has no shapes.
	tower_shapes : Tower, Picture.Setting(Tower.Footprint) -> List(Shapes.Shape)

	## How far a corner lies from the footprint's centre, across the route and
	## along it. Left and back are the negative ways.
	corner_offset : Tower.Corner -> { across : Distance, along : Distance }
}
```

`scenery_picture` then becomes one line, `tower_shapes(tower, { foot, cam_focal, context: tower_footprint(tower, context) })`, and the beacon widget calls `tower_shapes` with the same `Setting` every kind uses. The private part keeps `TowerInView` (renamed, item 4) and the rod helpers, with `rod_half`/`rod_w` as `rod_half_width`/`rod_width`, `brace_storeys : U64`, and the two beacon thresholds named. No pixel should move, so the gate's hashes are the check. Before building it, I'd check whether the boundaries lint expects constants inside a block.

## The walk

````roc
# The types of Tower and every type they depend on, to depth 3, the most primitive first.
# Builtin leaves, not expanded: Bool, F64, I64, List, Str, Try, U32, U64
# Beyond depth 3, not followed: Billboard; BirdFlight.Habit; Cat.Crossing; Geom.Placed; Pigs.PigHerd; Pigs.PigInterest; Scenery.BendLife; Trees.RoadsideTree
# Type variables, not followed: context (Picture.Setting)

#### Angle.Turn   (Angle.roc:55)
Turn :: F64.{
	radians : F64 -> Angle.Turn

	## The turn of this many degrees.
	degrees : F64 -> Angle.Turn

	to_radians : Angle.Turn -> F64

	plus : Angle.Turn, Angle.Turn -> Angle.Turn

	minus : Angle.Turn, Angle.Turn -> Angle.Turn

	times : Angle.Turn, F64 -> Angle.Turn

	## The same turn taken to the right.
	abs : Angle.Turn -> Angle.Turn

	## This turn, held to no more than `limit` either way.
	clamped_within : Angle.Turn, Angle.Turn -> Angle.Turn

	## How many of `whole` this turn is: negative for a turn to the left.
	ratio_to : Angle.Turn, Angle.Turn -> F64

	## Whether this turn goes right. Straight ahead counts as right, so
	## every turn lies on one side or the other.
	is_right : Angle.Turn -> Bool

	is_gt : Angle.Turn, Angle.Turn -> Bool

	is_gte : Angle.Turn, Angle.Turn -> Bool

	is_lt : Angle.Turn, Angle.Turn -> Bool

	is_lte : Angle.Turn, Angle.Turn -> Bool
}

#### Brush.Rgba   (repos:roc-apps/canvas_apps/lib/Brush.roc:15)
# Red, green and blue in 0..255, alpha in 0..1.
Rgba : { r : F64, g : F64, b : F64, a : F64 }

#### Brush.Fill   (repos:roc-apps/canvas_apps/lib/Brush.roc:17)
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

#### Along   (Along.roc:13)
## A place along one segment of the road, in metres from that segment's start,
## which is the only origin an `Along` has. It may lie before the start or past
## the end, as a point on the next segment does when it is measured on this one.
## A place measured from anywhere else, such as the segment's end, is a
## `Distance` named for where it is from, and becomes an `Along` only through
## the segment's length.
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

#### Fraction   (Fraction.roc:10)
## A ratio from 0 to 1: how far through a move, how near dusk, how bright a
## beacon. Only this module can build one, so a value of this type is always
## in range. Anything that can pass 1 has a type of its own.
##
## There are two ways in. `of` takes a ratio that can only be in range, and a
## ratio outside it means the sum that made it is wrong, so `of` crashes.
## `clamp` takes a ratio that can rightly fall outside, such as how far a
## rider has come along a stretch they haven't reached yet.
Fraction :: F64.{
	## This ratio as a fraction. A value that is not a number is out of range.
	from_ratio : F64 -> Try(Fraction, [OutOfRange])

	## A ratio that can only be in range, as a fraction.
	of : F64 -> Fraction

	## The fraction nearest this ratio.
	clamp : F64 -> Fraction

	to_f64 : Fraction -> F64

	zero : Fraction   # constant

	whole : Fraction   # constant

	## This fraction of `other`.
	times : Fraction, Fraction -> Fraction

	## What is left of the whole after this fraction.
	complement : Fraction -> Fraction

	## The larger of this fraction and `other`.
	max : Fraction, Fraction -> Fraction

	is_lt : Fraction, Fraction -> Bool

	is_lte : Fraction, Fraction -> Bool

	is_gte : Fraction, Fraction -> Bool
}

#### Geom.Bend   (Geom.roc:55)
## The bend from one segment into the next: the length of the segment
## before it, and the turn it makes, positive to the right.
Bend : { segment_length : Distance, turn : Angle.Turn }

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
## put it on the screen. Only `ahead_point`, the near-plane cut, and raising
## a point already in view build one.
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

#### Geom.RiderPoint   (Geom.roc:21)
## A point on the ground in the rider's view. Both parts are signed: a
## negative `right` is to the rider's left, and a negative `forward` is
## behind the rider.
RiderPoint : { right : Distance, forward : Distance }

#### Geom.LevelPoint   (Geom.roc:210)
## A point on the rider's level at or past the near plane, such as where an
## object stands. It has no height, so whatever is drawn above it says how
## high with `at_height`. Only `ahead_on_level` builds one.
LevelPoint :: Geom.RiderPoint.{
	right : Geom.LevelPoint -> Distance

	forward : Geom.LevelPoint -> Distance

	to_rider : Geom.LevelPoint -> Geom.RiderPoint

	## The point raised to `height`. It is as far ahead, so still in view.
	at_height : Geom.LevelPoint, Distance -> Geom.AheadPoint
}

#### Geom.RoadPoint   (Geom.roc:34)
## A point on one segment of the road.
RoadPoint : { along : Along, across : Across }

#### Geom.Vantage   (Geom.roc:47)
## Where the camera stands on the current segment, and which way it faces.
Vantage : {
	along : Along,
	across : Across,
	yaw : Angle.Turn,
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
	foot : Geom.LevelPoint,
	cam_focal : Pixels,
	context : context,
}

#### RgbColor   (repos:roc-apps/canvas_apps/lib/RgbColor.roc:8)
# RgbColor -- an opaque colour as one whole number, 0xRRGGBB: eight bits each
# of red, green and blue, red highest. A flat fill's colour is one of these, and
# `Brush.opaque` is what turns it into a brush colour.
#
# A colour with alpha is an `ArgbColor`, a different type, so neither can be
# passed where the other belongs.
RgbColor :: I64.{
	of : I64 -> RgbColor

	to_i64 : RgbColor -> I64
}

#### Screen.Point   (Screen.roc:9)
## A point on the screen, in pixels from its top left corner. Either can be
## negative, or past the far edge, for a point off the screen.
Point : { x : Pixels, y : Pixels }

#### Shapes.Align   (repos:roc-apps/canvas_apps/lib/Shapes.roc:56)
Align : [Left, Center]

#### Shapes.Face   (repos:roc-apps/canvas_apps/lib/Shapes.roc:54)
## `Prose` is the viewer's own sans serif, for words. `Code` is a monospace, for
## what a program says.
Face : [Prose, Code]

#### Shapes.Line   (repos:roc-apps/canvas_apps/lib/Shapes.roc:42)
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

#### Shapes.Mode   (repos:roc-apps/canvas_apps/lib/Shapes.roc:60)
## `Over` paints over what is there. `Add` adds light to it, which is what a glow
## is.
Mode : [Over, Add]

#### Shapes.Space   (repos:roc-apps/canvas_apps/lib/Shapes.roc:65)
## The space the shapes after a `View` mark are in. `Screen` is the game's own
## pixels, where every frame starts. `World` carries plain numbers rather than a
## Camera, because the mark crosses to JavaScript, which has no such type.
Space : [
	Screen,
	World({ target : { x : F64, y : F64 }, offset : { x : F64, y : F64 }, rotation : F64, zoom : F64 }),
]

#### Shapes.Shape   (repos:roc-apps/canvas_apps/lib/Shapes.roc:10)
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

# Cycle: these types mention each other: World.Segment, World.SegmentIndex

#### World.SegmentIndex   (World.roc:24)
## A segment's place in the route, counted from 0. It says where a segment
## is in the route, where a RoadAhead.Position says how far ahead of the
## rider it is.
SegmentIndex :: U32.{
	number : U32 -> World.SegmentIndex

	to_u32 : World.SegmentIndex -> U32

	to_i64 : World.SegmentIndex -> I64

	## The route's first segment.
	first : World.SegmentIndex   # constant

	next : World.SegmentIndex -> World.SegmentIndex

	## The segment before this one, unless this is the first.
	previous : World.SegmentIndex -> [Previous(World.SegmentIndex), AtRouteStart]

	## How many segments come before this one.
	count_before : World.SegmentIndex -> U64

	## The segment of `route_segments` at this index.
	segment_in : World.SegmentIndex, List(World.Segment) -> World.Segment
}

#### World.Segment   (World.roc:79)
## One segment of road, built from its plan.
Segment : {
	length : Distance,
	trees : List(Trees.RoadsideTree),
	cows : List(Geom.Placed(Billboard)),
	pigs : List(Geom.Placed(Billboard)),
	pig_herd : Pigs.PigHerd,

	## How the rider takes the segment's herd. A segment with no pigs has
	## nothing to notice, so its pigs are `Unnoticed`.
	pig_interest : Pigs.PigInterest,

	## The turn into the next segment: positive to the right, negative to
	## the left.
	exit_turn : Angle.Turn,
	commit_along : Along,
	mid_tower : [MidTower, NoMidTower],

	## What crosses the road here, at most one thing, so that the rider has
	## one experience at a time. Most of the road is quiet, so that a crossing
	## stands out.
	crossing : [CatCrosses(Cat.Crossing), BirdHere(BirdFlight.Habit), QuietRoad],
	ending : [Continues({ next : World.SegmentIndex }), Terminates],
	bend_life : Scenery.BendLife,
}

#### RoadAhead.Position   (RoadAhead.roc:39)
## A segment's place on the road ahead, counted from the rider's own at 0. It
## says how many segments ahead of the rider that segment is, where a
## World.SegmentIndex says where it is in the route.
Position :: U32.{
	number : U32 -> RoadAhead.Position

	to_i64 : RoadAhead.Position -> I64

	## The rider's own segment.
	first : RoadAhead.Position   # constant

	next : RoadAhead.Position -> RoadAhead.Position

	## Every position in `segments_ahead`, the rider's own first.
	positions_in : List(World.SegmentIndex) -> List(RoadAhead.Position)

	## The segment at this position in `segments_ahead`.
	index_in : RoadAhead.Position, List(World.SegmentIndex) -> World.SegmentIndex

	## The segments of `segments_ahead` before this position, the rider's own first.
	segments_before : RoadAhead.Position, List(World.SegmentIndex) -> List(World.SegmentIndex)

	## Whether this position is the last one in `segments_ahead`.
	is_last_in : RoadAhead.Position, List(World.SegmentIndex) -> Bool

	## Whether `segments_ahead` stops before this position.
	is_past_end_of : RoadAhead.Position, List(World.SegmentIndex) -> Bool

	## Whether this position is among the first `count` of the road ahead.
	is_within_first : RoadAhead.Position, U32 -> Bool
}

#### RoadAhead.RoadView   (RoadAhead.roc:17)
## The road in view: the route's segments, the indices of those ahead
## of the rider, and the rider's vantage.
RoadView : {
	route_segments : List(World.Segment),
	segments_ahead : List(World.SegmentIndex),
	vantage : Geom.Vantage,
}

#### RoadAhead.SegmentPlace   (RoadAhead.roc:88)
## Where a segment lies from the rider: at a position on the road ahead, or
## just behind the rider, round the bend into the rider's segment.
SegmentPlace : [Ahead(RoadAhead.Position), JustBehind(Geom.Bend)]

#### RoadAhead.RoadContext   (RoadAhead.roc:29)
## What a thing measured on the road draws from: the road in view, and where
## on it the thing stands.
RoadContext : {
	road : RoadAhead.RoadView,
	place : RoadAhead.SegmentPlace,
	along : Along,
	across : Across,
}

#### Tower.Corner   (Tower.roc:88)
## A corner of the tower's square footprint, as seen along the route.
Corner : [BackLeft, BackRight, FrontRight, FrontLeft]

#### Tower.Footprint   (Tower.roc:91)
## Where the footprint's four corners stand in the rider's view.
Footprint : {
	back_left : Geom.RiderPoint,
	back_right : Geom.RiderPoint,
	front_right : Geom.RiderPoint,
	front_left : Geom.RiderPoint,
}

#### Tower.RodView   (Tower.roc:99)
## How a rod is drawn: its width on screen, and the camera.
RodView : { rod_width_px : Pixels, cam_focal : Pixels }

#### Tower.TowerInView   (Tower.roc:103)
## One tower, ready to draw: where it stands, how far the earth's curve
## has sunk it, which is never negative, and how its rods are drawn.
TowerInView : {
	footprint : Tower.Footprint,
	center : Geom.LevelPoint,
	sunk : Distance,
	view : Tower.RodView,
}

#### Tower   (Tower.roc:24)
## A tower in a frame: how it is turned, and how bright its beacon is.
Tower := { yaw : Angle.Turn, beacon_brightness : Fraction }.{
	## How a tower looks. Its footprint is measured on the road, so the road and
	## where it stands there are its context.
	scenery_picture : Tower, Picture.Setting(RoadAhead.RoadContext) -> Picture

	## Where a tower's four footprint corners stand in the rider's view.
	tower_footprint : Tower, RoadAhead.RoadContext -> Tower.Footprint

	tower_height : Distance   # constant

	tower_half : Distance   # constant

	storey_height : Distance   # constant

	brace_storeys : I64   # constant

	rod_half : Distance   # constant

	rod_w : Distance   # constant

	tower_metal : RgbColor   # constant

	## The radius a far tower sinks over, which hides it wholly at 1.8 km. It
	## is tighter than `Geom.ground_curve_radius`, so a tower sinks visibly as
	## it recedes: on the ground's curve it would stay in view to 4 km.
	sink_radius : Distance   # constant

	beacon_radius : Distance   # constant

	beacon_color : RgbColor   # constant

	## The corners in drawing order, going round the square.
	corners : List(Tower.Corner)   # constant

	## The corner after this one, going round the square.
	next_corner : Tower.Corner -> Tower.Corner

	## How far a corner lies from the footprint's centre, across the route and
	## along it. Left and back are the negative ways.
	corner_offset : Tower.Corner -> { across : Distance, along : Distance }

	footprint_corner : Tower.Footprint, Tower.Corner -> Geom.RiderPoint

	## Where a footprint corner stands on the map, for a tower centred at
	## `along` and `across` and turned by `yaw`.
	base_corner_on_road : Tower.Corner,
	{
		along : Along,
		across : Across,
		yaw : Angle.Turn,
	} -> Geom.RoadPoint

	## How far the earth's curve hides the bottom of a tower standing at `p`.
	sunk_below_horizon : Geom.RiderPoint -> Distance

	## The point `fraction` of the way from `from` to `to`.
	point_between : {
		from : Geom.RaisedPoint,
		to : Geom.RaisedPoint,
		fraction : Fraction,
	} -> Geom.RaisedPoint

	## A corner of the tower at `height_on_tower`: drawn in toward the centre
	## as the tower tapers, and lowered by how far the tower has sunk.
	corner_at : Tower.TowerInView,
	{
		corner : Tower.Corner,
		height_on_tower : Distance,
	} -> Geom.RaisedPoint

	## A rod between two points on screen, `width_px` wide.
	screen_rod : {
		from : Screen.Point,
		to : Screen.Point,
		width_px : Pixels,
	} -> Shapes.Shape

	## The quad of a rod from `from` to `to`, its sides `offset_x` and
	## `offset_y` either side of the line between them.
	rod_quad : {
		from : Screen.Point,
		to : Screen.Point,
		offset_x : Pixels,
		offset_y : Pixels,
	} -> Shapes.Shape

	## A rod between two points in the rider's view. A rod with one end
	## behind the near plane is cut there; one with both ends behind it is
	## not drawn.
	rod_shapes : Tower.RodView,
	{
		from : Geom.RaisedPoint,
		to : Geom.RaisedPoint,
	} -> List(Shapes.Shape)

	rod_on_screen : Tower.RodView, { from : Geom.AheadPoint, to : Geom.AheadPoint } -> Shapes.Shape

	## How many pixels one metre across spans as far ahead as `at`.
	metre_px : { at : Geom.LevelPoint, cam_focal : Pixels } -> Pixels

	## A rod's width on screen as far ahead as `at`.
	rod_width_at : { at : Geom.LevelPoint, cam_focal : Pixels } -> Pixels

	## The four legs, from the footprint's corners up to the apex.
	legs : Tower.TowerInView, Geom.RaisedPoint -> List(Shapes.Shape)

	## The ring of rods round the tower at height `h`.
	ring_shapes : Tower.TowerInView, Distance -> List(Shapes.Shape)

	## A ring at every storey below the top, bottom first, leaving out those
	## the earth has hidden.
	rings : Tower.TowerInView -> List(Shapes.Shape)

	## The height of each ring: a storey up, and a storey more, to the top.
	ring_heights : List(Distance)   # constant

	## The crossed braces of the lowest storeys, bottom first. A storey the
	## earth has partly hidden starts its braces at the horizon.
	braces : Tower.TowerInView -> List(Shapes.Shape)

	storey_shapes : Tower.TowerInView, I64 -> List(Shapes.Shape)

	## The two braces crossing the face from `corner` to the next corner: one
	## rising each way.
	brace_shapes : Tower.TowerInView,
	{
		corner : Tower.Corner,
		storey_bottom : Distance,
		storey_top : Distance,
		hidden_fraction : Fraction,
	} -> List(Shapes.Shape)

	## The beacon on the apex, at its brightness; too dim or too small, it
	## isn't drawn.
	beacon_shapes : Tower.TowerInView,
	{
		apex : Geom.AheadPoint,
		brightness : Fraction,
	} -> List(Shapes.Shape)

	## The whole tower: legs, rings, braces and beacon, in that order. A tower
	## sunk wholly below the horizon draws nothing.
	tower_shapes : {
		footprint : Tower.Footprint,
		center : Geom.LevelPoint,
		cam_focal : Pixels,
		beacon_brightness : Fraction,
	} -> List(Shapes.Shape)
}

# 36 types, 131 functions, 20 constants, 15 modules, 8 leaves, 1 type variables, 8 beyond depth 3
````
