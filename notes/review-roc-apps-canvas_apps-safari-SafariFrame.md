# Review: roc-apps `canvas_apps/safari/SafariFrame.roc`

105 lines in 3 chunks, as of commit 19ea037 safari: the sky and grass move to BackdropPixels; SafariFrame is the glue. Reply under any chunk; this paragraph is for the file as a whole.

```roc
## SafariFrame is test code: the game never runs it. It paints one Safari
## frame into a list of 0xRRGGBB pixels, in Roc: the sky and the grass
## (BackdropPixels), the sun (SunPixels), then every draw command in paint
## order, all turned by the camera's roll (the rider's lean, which tilts the
## whole picture about the centre of the screen). Its pixels are exact and the
## same on every run.
##
## That is what Safari's gate needs. The gate is a script we run before a
## change lands (gates/run.shale), and it builds two programs on SafariFrame
## to check the drawing pixel for pixel. RasterFrame prints a hash of a
## frame's pixels, so we can confirm that a change which shouldn't alter the
## picture leaves the hash the same. ShapesFrame paints a frame from its draw
## commands, paints it again from the shapes the browser is given, and counts
## the pixels that differ; the gate requires none.
##
## The game itself paints differently. In the browser, the Roc program (built
## to wasm) hands each frame to the page as shapes, and shapewire.js paints
## them with the browser's canvas. Wasm reaches a canvas only through JS in
## any case, and a canvas paints paths and gradients natively and
## anti-aliased, far faster than Roc could fill every pixel and copy the
## frame out. This painter has no anti-aliasing.
##
## What is generic lives in modules that know nothing of Safari: ScreenRoll
## turns points by the roll, PixelGrid finds the pixels that a stretch of a
## row or column covers, PixelColor packs and blends pixels, and ScanlineFill
## fills polygons and discs.
import BackdropPixels
import Paint
import Sky
import SafariBrush
import Screen
import lib.Brush
import PixelGrid
import ScanlineFill
import ScreenRoll
import SunPixels
```

**Lines 1–36**

```roc
SafariFrame :: [].{

	## What a frame shows, in SafariRide's terms.
	Scene : {
		commands : List(Paint.DrawCmd),
		roll : F64,
		sky_top : I64,
		sky_horizon : I64,
		sun : Sky.SunPos,
	}

	## The frame: the sky and the grass, the sun, then every command.
	paint : SafariFrame.Scene -> List(U32)
	paint = |scene| {
		roll = SafariFrame.screen_roll(scene.roll)
		var $px = BackdropPixels.paint(roll, { sky_top: scene.sky_top, sky_horizon: scene.sky_horizon })
		$px = SunPixels.paint($px, { roll, sun: scene.sun })
		for draw_command in scene.commands {
			$px = paint_command($px, { roll, draw_command })
		}
		$px
	}

	## Safari's screen, seen through the camera's roll.
	screen_roll : F64 -> ScreenRoll
	screen_roll = |roll|
		ScreenRoll.of({
			roll,
			width: screen_width,
			height: screen_height,
		})
}
```

**Lines 38–69**: `SafariFrame`, `Scene`, `paint`, `screen_roll`

```roc
## Safari's screen, in pixels across and down.
screen_width : PixelGrid.Coordinate
screen_width = PixelGrid.Coordinate.from_i64(Screen.width_px)

screen_height : PixelGrid.Coordinate
screen_height = PixelGrid.Coordinate.from_i64(Screen.height_px)

## A beacon is a disc at the command's strength; every other command is a
## polygon filled with its brush.
paint_command : List(U32), { roll : ScreenRoll, draw_command : Paint.DrawCmd } -> List(U32)
paint_command = |pixels, { roll, draw_command }|
	if draw_command.tag == Paint.beacon_tag {
		match draw_command.geom {
			[x, y, radius] => {
				opaque = Brush.opaque(draw_command.color)
				ScanlineFill.fill_disc(
					pixels,
					{
						roll,
						center: ScreenRoll.ScenePoint.({ x, y }),
						radius,
						color: { ..opaque, a: draw_command.strength },
					},
				)
			}
			_ => crash "SafariFrame.paint_command: a beacon's geometry is its x, y and radius"
		}
	} else {
		fill = SafariBrush.of_command(draw_command)
		match fill {
			Skip => pixels
			Flat(_) | Span(_) | Radial(_) | Linear(_) | Ellipse(_) | Glow(_) =>
				ScanlineFill.fill_polygon(pixels, { roll, pts: draw_command.pts, fill })
			}
	}
```

**Lines 71–105**: `screen_width`, `screen_height`, `paint_command`

