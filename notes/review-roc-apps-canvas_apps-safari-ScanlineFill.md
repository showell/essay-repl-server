# Review: roc-apps `canvas_apps/safari/ScanlineFill.roc`

172 lines in 7 chunks, as of commit 1b1e46c safari: split Raster into SafariFrame and four generic modules. Reply under any chunk; this paragraph is for the file as a whole.

```roc
## Polygons and discs filled into a grid of 0xRRGGBB pixels a row at a time.
## A shape's points are in the scene, and a ScreenRoll turns them onto the
## screen. A pixel is painted when its centre is inside the shape, and a
## polygon fills by the nonzero rule, as a canvas fills one. There is no
## anti-aliasing. The colour a point gets is its Brush's.
##
## Every store lands in place: the pixels are a `var` list, and each store is
## PixelGrid's `blend`. A list threaded down a recursion would be copied on
## the next store (docs/roc-notes.md, "Speed and copying").
import lib.Brush
import PixelGrid
import ScreenRoll
```

**Lines 1–12**

```roc
ScanlineFill :: [].{

	## A polygon, as scene coordinates x0, y0, x1, y1, ..., filled by the
	## nonzero rule.
	fill_polygon : List(U32), { roll : ScreenRoll, pts : List(F64), fill : Brush.Fill } -> List(U32)
	fill_polygon = |pixels, { roll, pts, fill }| {
		corners = pts.chunks_of(2).map(
			|pair|
				match pair {
					[x, y] => roll.to_screen(ScreenRoll.ScenePoint.({ x, y }))
					_ => crash "ScanlineFill.fill_polygon: a polygon's coordinates come in pairs"
				},
		)
		match corners {
			[first, _, _, ..] => {
				next_corners = corners.drop_first(1).concat(corners.take_first(1))
				edges = corners.map2(next_corners, |from, to| { from, to })
				rows = PixelGrid.pixels_between({
					from: corners.fold(first.y, |top, corner| F64.min(top, corner.y)),
					to: corners.fold(first.y, |bottom, corner| F64.max(bottom, corner.y)),
					count: roll.height_px(),
				})
				var $px = pixels
				for row in I64.until(rows.start, rows.end) {
					crossings = row_crossings(edges, PixelGrid.pixel_center(row))
					$px = fill_row($px, { roll, fill, row, crossings })
				}
				$px
			}
			# Fewer than three corners enclose nothing.
			_ => pixels
		}
	}
```

**Lines 14–46**: `ScanlineFill`, `fill_polygon`

```roc
	## A disc of one colour: the pixels whose centres are strictly inside.
	fill_disc : List(U32), { roll : ScreenRoll, center : ScreenRoll.ScenePoint, radius : F64, color : Brush.Rgba } -> List(U32)
	fill_disc = |pixels, { roll, center, radius, color }| {
		on_screen = roll.to_screen(center)
		rows = PixelGrid.pixels_between({
			from: on_screen.y - radius,
			to: on_screen.y + radius,
			count: roll.height_px(),
		})
		var $px = pixels
		for row in I64.until(rows.start, rows.end) {
			dy = PixelGrid.pixel_center(row) - on_screen.y
			half_squared = radius * radius - dy * dy
			$px = if half_squared > 0.0 {
				half = F64.sqrt(half_squared)
				paint_span($px, { roll, fill: Flat(color), row, from: on_screen.x - half, to: on_screen.x + half })
			} else {
				$px
			}
		}
		$px
	}
}
```

**Lines 48–70**: `fill_disc`

```roc
## Where a row of pixels crosses a polygon's edge, and which way the edge
## runs on the screen.
Crossing : { x : F64, direction : [Down, Up] }

## A polygon's edge, on the screen.
Edge : { from : ScreenRoll.ScreenPoint, to : ScreenRoll.ScreenPoint }

## A stretch of a row, from one crossing to the next.
RowSpan : { from : F64, to : F64 }

## A walk along a row's crossings: the winding so far, and the stretches
## found inside.
WindingWalk : { winding : I64, spans : List(RowSpan) }

## Where the row at `y` crosses the polygon's edges, left to right. An edge
## holds its upper end and not its lower.
row_crossings : List(Edge), F64 -> List(Crossing)
row_crossings = |edges, y|
	edges.join_map(|edge| crossing(edge, y)).sort_with(
		|a, b| if a.x < b.x {
			Before
		} else if a.x > b.x {
			After
		} else {
			Same
		},
	)
```

**Lines 72–98**: `Crossing`, `Edge`, `RowSpan`, `WindingWalk`, `row_crossings`

```roc
crossing : Edge, F64 -> List(Crossing)
crossing = |edge, y|
	if edge.from.y <= y and y < edge.to.y {
		[{ x: edge_x_at(edge, y), direction: Down }]
	} else if edge.to.y <= y and y < edge.from.y {
		[{ x: edge_x_at(edge, y), direction: Up }]
	} else {
		[]
	}

## Where the edge is across the screen at the height `y`, which is between
## its ends, so the division is by a height that isn't zero.
edge_x_at : Edge, F64 -> F64
edge_x_at = |{ from, to }, y| from.x + (y - from.y) * (to.x - from.x) / (to.y - from.y)

## One row of a polygon: the spans between its crossings where the winding is
## not zero.
fill_row : List(U32), { roll : ScreenRoll, fill : Brush.Fill, row : I64, crossings : List(Crossing) } -> List(U32)
fill_row = |pixels, { roll, fill, row, crossings }| {
	var $px = pixels
	for row_span in inside_spans(crossings) {
		$px = paint_span($px, { roll, fill, row, from: row_span.from, to: row_span.to })
	}
	$px
}
```

**Lines 100–124**: `crossing`, `edge_x_at`, `fill_row`

```roc
## The stretches between neighbouring crossings, left to right, where the
## winding is not zero.
inside_spans : List(Crossing) -> List(RowSpan)
inside_spans = |crossings| {
	neighbours = crossings.map2(crossings.drop_first(1), |left, right| { left, right })
	neighbours.fold({ winding: 0, spans: [] }, walk_crossing).spans
}

## The walk after one more pair of neighbouring crossings.
walk_crossing : WindingWalk, { left : Crossing, right : Crossing } -> WindingWalk
walk_crossing = |so_far, { left, right }| {
	turn =
		match left.direction {
			Down => 1
			Up => -1
		}
	winding = so_far.winding + turn
	spans =
		if winding == 0 {
			so_far.spans
		} else {
			so_far.spans.append({ from: left.x, to: right.x })
		}
	{ winding, spans }
}
```

**Lines 126–150**: `inside_spans`, `walk_crossing`

```roc
## The pixels of `row` whose centres fall in [from, to).
paint_span : List(U32), { roll : ScreenRoll, fill : Brush.Fill, row : I64, from : F64, to : F64 } -> List(U32)
paint_span = |pixels, { roll, fill, row, from, to }| {
	columns = PixelGrid.pixels_between({ from, to, count: roll.width_px() })
	width = roll.width_px()
	y = PixelGrid.pixel_center(row)
	var $px = pixels
	for column in I64.until(columns.start, columns.end) {
		at = PixelGrid.pixel_index({ row, column, width })
		color = match fill {
			Flat(flat) => flat
			Span(_) | Radial(_) | Linear(_) | Ellipse(_) | Glow(_) => {
				p = roll.to_scene(ScreenRoll.ScreenPoint.({ x: PixelGrid.pixel_center(column), y }))
				Brush.shade(fill, p.x, p.y)
			}
			Skip => crash "ScanlineFill.paint_span: no caller fills with a Skip brush"
		}
		$px = PixelGrid.blend($px, { at, color })
	}
	$px
}
```

**Lines 152–172**: `paint_span`

