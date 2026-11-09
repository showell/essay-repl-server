# Proofread: Shapes, a simple tree

*For Steve's read, 2026-11-10. The chapter now builds `SimpleTree`: the foliage (a triangle, its image, then its code), the trunk (a rectangle, its image, then its code), and then the tree, the first `Picture`. It goes one way: the polygon and why it's the primitive, points, the triangle, the rectangle, the tree. The widget fences show here as captions. The three images are on the dev channel, at http://143.244.172.148:9210/tutorial/shapes.html, once the rebuild finishes.*

---

## Shapes

Thirty times a second, Safari Ride answers one question: what goes on the canvas? The answer is a list of shapes. Roc builds the list, and a painter on the other side, JavaScript on this page, paints it from the first shape to the last. A painter is a bit like a printer: it does exactly what the list says. That split is the whole drawing model. Roc decides every corner and every color, and the painter follows orders.

In this chapter we build a simple tree: a green triangle of foliage on a brown rectangle of trunk. Every far tree in the ride grows from this one. We start from the one shape the painter knows best, the polygon. Then we make the triangle, then the rectangle, and then we put the two together as one tree. The code is the plainest Roc there is, made of types, records and functions.

New in this chapter:

- Roc: a record taken apart in a parameter list
- Modules: `Shapes`, `Screen`, `Pixels`, `Polygon`, `SimpleTree`, `Picture`

### Get the types right

Three types carry the chapter, in the order we meet them:

| Type | What it is |
|---|---|
| `Shapes.Shape` | One item in the painter's list, such as a polygon |
| `Screen.Point` | A place on the canvas |
| `Picture` | The shapes that form one full object, in painting order |

### The polygon

The painter's list holds `Shapes.Shape` values, and a shape is one of a handful of tags:

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

Each tag carries its data in parentheses, its payload. The tag that matters here is `Poly`, a polygon. Its payload has two fields. `coordinates` is the corners, as one flat list of numbers: an `x` and then a `y` for each corner. `fill` is how to color the inside.

`Poly` is the primitive because a polygon can stand for any flat surface: a tier of a tree, a stretch of road, a face of the truck. A painter fills a polygon in one call, and the payload is nothing but numbers and a color, the painter's own terms. So Safari Ride builds nearly everything out of polygons. A frame often holds more than 2,000 shapes, and nearly all of them are `Poly`.

A fill is a `Brush.Fill`. `Flat` is a single color, and the other fills are gradients, running from one color to another across the shape. Of the other tags, `Disc` is a circle, and `Blend` and `View` are marks that change how the shapes after them are painted.

### Points on the screen

A polygon's corners are places on the canvas. The canvas is measured from its top left corner, and `y` grows downward. A place on it is a `Screen.Point`, an `x` and a `y`:

```roc Screen.roc
## A point on the screen, in pixels from its top left corner. Either can be
## negative, or past the far edge, for a point off the screen.
Point : { x : Pixels, y : Pixels }
```

Both are `Pixels`, a length on the screen. `Pixels` is opaque, like `Clock`, so the compiler keeps screen lengths and road lengths apart. Underneath it's an `F64`, because a corner can land between two pixels. `Screen.point(x, y)` makes a point from two plain numbers.

### A triangle

Here is the tree's foliage, one green triangle:

```widget shapes foliage
The simple tree's foliage, a triangle, on a plain background.
```

`SimpleTree` makes it with one call:

```roc shapes_widget/SimpleTree.roc
## The tree's foliage, one green triangle.
foliage : Shapes.Shape
foliage = Polygon.triangle(
	{
		first_corner: Screen.point(180.0, 240.0),
		second_corner: Screen.point(420.0, 240.0),
		third_corner: Screen.point(300.0, 40.0),
	},
	RgbColor.of(0x2e8b57),
)
```

A color is a whole number in hex, the same six digits a web page writes after its `#`. `0x2e8b57` is a sea green.

`Polygon.triangle` does the work:

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

The body is the `Poly` itself. Its six coordinates are the three corners, an `x` and a `y` each, and `to_f64` takes the plain number out of each `Pixels`. Its fill is the color, made fully opaque by `Brush.flat`.

`triangle` is a thin wrapper around `Poly`, and it carries weight. A `Poly`'s coordinates are a bare list of numbers, which says nothing about how many corners there are or which number belongs to which. A call to `triangle` names its three corners, and the type fixes their count.

### A rectangle

Next, the trunk, one brown rectangle:

```widget shapes trunk
The simple tree's trunk, a rectangle, on a plain background.
```

It's one call too:

```roc shapes_widget/SimpleTree.roc
## The tree's trunk, one brown rectangle.
trunk : Shapes.Shape
trunk = Polygon.rectangle(
	{ top_left: Screen.point(285.0, 200.0), bottom_right: Screen.point(315.0, 300.0) },
	RgbColor.of(0x8b5a2b),
)
```

`0x8b5a2b` is a brown. A rectangle's sides run along the screen's edges, so two opposite corners pin it down, and `Polygon.rectangle` takes just those two:

```roc Polygon.roc
## Makes a rectangle of one flat color. Its sides run along the screen's edges.
rectangle : { top_left : Screen.Point, bottom_right : Screen.Point }, RgbColor -> Shapes.Shape
rectangle = |{ top_left, bottom_right }, color| {
	left = top_left.x.to_f64()
	top = top_left.y.to_f64()
	right = bottom_right.x.to_f64()
	bottom = bottom_right.y.to_f64()
	Poly({
		coordinates: [
			left,
			top,
			right,
			top,
			right,
			bottom,
			left,
			bottom,
		],
		fill: Brush.flat(color),
	})
}
```

The rectangle names its four edges, `left`, `top`, `right` and `bottom`. Then it lists its corners clockwise from the top left, each one an edge for its `x` and an edge for its `y`.

### A simple tree

Now the two shapes become one object:

```widget shapes tree
The simple tree, its trunk and its foliage, on a plain background.
```

```roc shapes_widget/SimpleTree.roc
## The whole tree, trunk first.
tree : Picture
tree = Picture.from_shapes([trunk, foliage])
```

The tree is a `Picture`: the shapes that form one full object, in the order they're painted. The trunk comes first and the foliage second, so the foliage paints over the top of the trunk, and the trunk shows only below the branches.

```roc Picture.roc
from_shapes : List(Shapes.Shape) -> Picture
to_shapes : Picture -> List(Shapes.Shape)
```

`Picture` is opaque, with a `List(Shapes.Shape)` underneath. Outside its module, a picture is a single thing, passed along whole, so the code that draws a tree hands back one value, the tree. Only `Scene`, as it builds the frame's list, opens a picture to take out its shapes.

A frame paints the backdrop, the mountains and the ground first. Then it paints a series of pictures, from the farthest object to the nearest, so that near trees cover far ones.

Every object along the road takes the same few steps on its way to a picture, and those steps come next. After them, this little tree grows its foliage into eight tiers.

