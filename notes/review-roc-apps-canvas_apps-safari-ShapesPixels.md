# Review: roc-apps `canvas_apps/safari/ShapesPixels.roc`

65 lines in 2 chunks, as of commit 25cdb45 canvas_apps: shapewire.js becomes shapes_canvas.js; its Roc twin is safari/ShapesPixels.roc. Reply under any chunk; this paragraph is for the file as a whole.

```roc
## ShapesPixels paints a frame's shapes into exact pixels with ScanlineFill.
## It is test code: the game never runs it (see SafariFrame for more context).
## Its twin is web/shapes_canvas.js, which paints the same shapes onto the
## browser's canvas in the game. ShapesFrame paints a frame from its draw
## commands, paints it again from the shapes the browser is given using this
## module, and the gate requires the two to agree pixel for pixel.
##
## It paints only what Safari's draw commands become: polygons, triangle
## pieces and unclipped flat discs, each laid over what is there. Any other
## shape crashes, naming what it got.
import lib.Brush
import lib.Shapes
import ScanlineFill
import ScreenRoll

ShapesPixels :: [].{

	## The shapes, in order, painted onto `pixels`.
	paint : List(U32), { roll : ScreenRoll, shapes : List(Shapes.Shape) } -> List(U32)
	paint = |pixels, { roll, shapes }| {
		var $px = pixels
		for shape in shapes {
			$px = paint_shape($px, { roll, shape })
		}
		$px
	}
}
```

**Lines 1–27**: `ShapesPixels`, `paint`

```roc
paint_shape : List(U32), { roll : ScreenRoll, shape : Shapes.Shape } -> List(U32)
paint_shape = |pixels, { roll, shape }|
	match shape {
		Poly(p) => ScanlineFill.fill_polygon(pixels, { roll, pts: p.pts, fill: p.fill })
		Pieces(p) => paint_pieces(pixels, { roll, tris: p.tris, fill: p.fill })
		Disc(d) => {
			color = match d.fill {
				Flat(flat) => flat
				Skip | Span(_) | Radial(_) | Linear(_) | Ellipse(_) | Glow(_) => crash "ShapesPixels: a command's disc with a gradient"
			}
			match d.clip {
				Anywhere => ScanlineFill.fill_disc(pixels, { roll, center: ScreenRoll.ScenePoint.({ x: d.x, y: d.y }), radius: d.r, color })
				Within(_) => crash "ShapesPixels: a command's disc clipped to a rectangle"
			}
		}
		Rect(_) => crash "ShapesPixels: a command cut into a rectangle"
		# ScanlineFill lays every pixel over what is there, so Over is the mode
		# it is always in, and Add is light it can't paint.
		Blend(Over) => pixels
		Blend(Add) => crash "ShapesPixels: a command lit in Add mode"
		Image(_) => crash "ShapesPixels: a command cut into an image"
		# The roll is the caller's; the game's lean mark is not a command.
		View(_) => crash "ShapesPixels: a command cut into a view mark"
	}

## The triangles, six numbers each, all filled with one brush.
paint_pieces : List(U32), { roll : ScreenRoll, tris : List(F64), fill : Brush.Fill } -> List(U32)
paint_pieces = |pixels, { roll, tris, fill }| {
	count = tris.len() // 6
	var $px = pixels
	var $k = 0
	while $k < count {
		$px = ScanlineFill.fill_polygon($px, { roll, pts: tris.sublist({ start: 6 * $k, len: 6 }), fill })
		$k = $k + 1
	}
	$px
}
```

**Lines 29–65**: `paint_shape`, `paint_pieces`

