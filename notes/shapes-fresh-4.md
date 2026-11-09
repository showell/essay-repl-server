# Proofread: Shapes, a triangle in one function

*For Steve's read, 2026-11-10. A triangle is three corners and a color, and `Polygon.triangle` builds its `Poly` directly: six coordinates, one fill, correct by construction, with no list, no check and no crash. The rectangle is one function too: it names its four edges and lists its corners. Neither touches `flat_polygon` or `polygon_coordinates` any more, and the chapter never mentions them.*

---

## Shapes

Thirty times a second, Safari Ride answers one question: what goes on the canvas? The answer is a list of shapes. Roc builds the list, and a painter on the other side, JavaScript on this page, paints it from the first shape to the last. A painter is a bit like a printer: it does exactly what the list says.

That split is the whole drawing model. Roc decides every corner and every color, and the painter follows orders.

In this chapter we build the two most essential shapes in Safari Ride, the triangle and the rectangle. A far tree is just these two: eight triangles of foliage on a rectangle of trunk. The code is the plainest Roc there is, made of types, records and functions.

New in this chapter:

- Roc: a record taken apart in a parameter list
- Modules: `TwoShapes`, `Shapes`, `Polygon`, `Screen`, `Pixels`, `Picture`

### Get the types right

Three types do the work. One says where, one says what, and one says which shapes belong together.

| Type | What it says |
|---|---|
| `Screen.Point` | Where: a place on the canvas |
| `Shapes.Shape` | What: one item in the frame's list, such as a polygon |
| `Picture` | Which belong together: the shapes that form one full object, in painting order |

The canvas is 960 pixels wide and 600 tall. Its points are measured from the top left corner, and `y` grows downward. A `Screen.Point` is an `x` and a `y`:

```roc Screen.roc
## A point on the screen, in pixels from its top left corner. Either can be
## negative, or past the far edge, for a point off the screen.
Point : { x : Pixels, y : Pixels }
```

Both are `Pixels`, a length on the screen. `Pixels` is opaque, like `Clock`, so the compiler keeps screen lengths and road lengths apart. Underneath it's an `F64`, because a corner can land between two pixels. `Screen.point(x, y)` makes a point from two plain numbers.

A frame is a list of `Shapes.Shape`, and a shape is one of a handful of tags:

```roc lib/Shapes.roc
## One thing in a frame. A later shape in the list paints over an earlier one.
Shape : [
	## A polygon, as x0, y0, x1, y1 and so on. It can be any polygon. A painter
	## that fills only convex ones has `ConvexCut` cut the rest into triangles.
	Poly({ coordinates : List(F64), fill : Brush.Fill }),

	Disc({ x : F64, y : F64, radius : F64, fill : Brush.Fill }),
	Rect({ x : F64, y : F64, width : F64, height : F64, fill : Brush.Fill }),

	## A mark, not a shape: how the shapes after it combine, until the next `Blend`.
	## A painter holds this as a mode, so a mark in the list says it directly.
	## `Shapes.added_light_shapes` writes the pair of marks around a run of shapes.
	Blend(Shapes.Mode),

	## A mark, not a shape: the space the shapes after it are in, until the next
	## `View`. It is a mark for the same reason `Blend` is. `Shapes.shapes_in_space`
	## writes the pair of marks around a run of shapes.
	View(Shapes.Space),

	## `cols` by `rows` pixels stretched over the box without smoothing. It carries
	## the pixels, not a handle, so there is no second copy of them to keep in step.
	Image({ x : F64, y : F64, width : F64, height : F64, cols : U64, rows : U64, pixels : List(Brush.Rgba) }),

	## A line of words in a real typeface. `Font.plotted_shapes` gives a painter that has
	## no typefaces the strokes of the same line.
	Text(Shapes.TextLine),
]
```

Each tag carries its data in parentheses, its payload. A `Poly` is a polygon, and its payload is the coordinates of its corners and its fill. A fill is a `Brush.Fill`. `Flat` is a single color, and the other fills are gradients, running from one color to another across the shape. `Blend` and `View` are marks in the list that change how the shapes after them are painted.

Safari Ride paints nearly everything as polygons. A frame often holds more than 2,000 shapes, and nearly all of them are `Poly`.

### A frame of two shapes

Here is a frame small enough to read whole:

```widget shapes
The list `TwoShapes.shapes`, painted over a plain background, on a smaller canvas than the ride's.
```

And here is the whole module behind it:

```roc shapes_widget/TwoShapes.roc, the whole file
## A frame is a list of shapes, painted first to last. The rectangle comes second
## in the list, so where the two overlap it paints over the triangle.
import game.Polygon
import game.Screen
import lib.RgbColor
import lib.Shapes

TwoShapes :: [].{

	shapes : List(Shapes.Shape)
	shapes = [triangle, rectangle]
}

triangle : Shapes.Shape
triangle = Polygon.triangle(
	{
		first_corner: Screen.point(120.0, 300.0),
		second_corner: Screen.point(360.0, 300.0),
		third_corner: Screen.point(240.0, 60.0),
	},
	RgbColor.of(0x2e8b57),
)

rectangle : Shapes.Shape
rectangle = Polygon.rectangle(
	{ top_left: Screen.point(270.0, 120.0), bottom_right: Screen.point(520.0, 250.0) },
	RgbColor.of(0xe8a33d),
)

expect TwoShapes.shapes.last() == Ok(rectangle)
```

`shapes` is the frame: a list of two values. The order of the list is the order of painting. The rectangle comes second, so where the two overlap, it covers the triangle. The widget puts one more shape at the front of the list, the plain background, so both paint over it.

Colors are whole numbers in hex, the same six digits a web page writes after its `#`. `0x2e8b57` is a sea green, and `0xe8a33d` is an amber.

### A triangle

`triangle` and `rectangle` each call a maker in `Polygon`. A maker returns a value that describes a shape, and the painter draws it later.

Let's draw the triangle first. A triangle is three corners and a color:

```roc Polygon.roc
## Makes a triangle of one flat color.
triangle : {
	first_corner : Screen.Point,
	second_corner : Screen.Point,
	third_corner : Screen.Point,
},
RgbColor -> Shapes.Shape
triangle = |{ first_corner, second_corner, third_corner }, color|
	Poly({
		coordinates: [
			first_corner.x.to_f64(),
			first_corner.y.to_f64(),
			second_corner.x.to_f64(),
			second_corner.y.to_f64(),
			third_corner.x.to_f64(),
			third_corner.y.to_f64(),
		],
		fill: Brush.flat(color),
	})
```

The bars, `|…|`, hold the function's parameters. The first parameter, `{ first_corner, second_corner, third_corner }`, takes the record apart into three names. A caller names all three corners, in any order, and the compiler checks that all three are there. So every triangle has exactly three corners, by construction.

The triangle is a `Poly` with two fields. `coordinates` lists the corners the way the painter reads them, an `x` and then a `y` for each, six numbers in all. `to_f64` takes the plain number out of each `Pixels`. `fill` is the color, made fully opaque by `Brush.flat`.

### A rectangle

Next, let's build a rectangle. Its sides run along the screen's edges, so two opposite corners pin it down:

```roc Polygon.roc
## Makes a rectangle of one flat color. Its sides run along the screen's edges.
rectangle : { top_left : Screen.Point, bottom_right : Screen.Point }, RgbColor -> Shapes.Shape
rectangle = |{ top_left, bottom_right }, color| {
	left = top_left.x.to_f64()
	top = top_left.y.to_f64()
	right = bottom_right.x.to_f64()
	bottom = bottom_right.y.to_f64()
	Poly({
		coordinates: [left, top, right, top, right, bottom, left, bottom],
		fill: Brush.flat(color),
	})
}
```

The rectangle names its four edges, `left`, `top`, `right` and `bottom`. Then it lists its corners clockwise from the top left, each one an edge for its `x` and an edge for its `y`.

### Pictures

One object is often many shapes. A tree is nine: a trunk and eight tiers of foliage. Those nine travel together, from the code that draws the tree to the frame that paints it, as one `Picture`:

```roc Picture.roc
from_shapes : List(Shapes.Shape) -> Picture
to_shapes : Picture -> List(Shapes.Shape)
```

`Picture` is opaque, with a `List(Shapes.Shape)` underneath. Outside its module, a picture is a single thing, passed along whole. Only `Scene`, as it builds the frame's list, opens a picture to take out its shapes.

A frame paints the backdrop, the mountains and the ground first. Then it paints a series of pictures, from the farthest object to the nearest, so that near things cover far ones.

The rest of the book is about choosing those corners, and choosing their order. Every object along the road takes the same few steps on its way to a picture, and those steps come next.

