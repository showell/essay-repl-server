# Review: roc-apps `canvas_apps/safari/SafariFrame.roc`

194 lines in 6 chunks, as of commit 989debb safari/SafariFrame: a header a newcomer can follow; README points to it. Reply under any chunk; this paragraph is for the file as a whole.

```roc
## SafariFrame is test code: the game never runs it. It paints one Safari
## frame into a list of 0xRRGGBB pixels, in Roc: the sky and the grass, the
## sun, then every draw command in paint order, all turned by the camera's
## roll (the rider's lean, which tilts the whole picture about the centre of
## the screen). Its pixels are exact and the same on every run.
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
import Paint
import Sky
import SafariBrush
import SafariShapes
import Screen
import lib.Brush
import PixelColor
import PixelGrid
import ScanlineFill
import ScreenRoll
```

**Lines 1–35**

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
		sky = {
			top_color: Brush.opaque(scene.sky_top),
			horizon_color: Brush.opaque(scene.sky_horizon),
		}
		var $px = backdrop(roll, sky)
		$px =
			match scene.sun {
				InView(sun) if SafariShapes.is_sun_shown(sun) => paint_sun($px, { roll, sun })
				InView(_) | OutOfView => $px
			}
		for draw_command in scene.commands {
			$px = paint_command($px, { roll, draw_command })
		}
		$px
	}
```

**Lines 37–66**: `SafariFrame`, `Scene`, `paint`

```roc
	## Safari's screen, seen through the camera's roll.
	screen_roll : F64 -> ScreenRoll
	screen_roll = |roll|
		ScreenRoll.of({
			roll,
			width: screen_width,
			height: screen_height,
		})
}

## Safari's screen, in pixels across and down.
screen_width : PixelGrid.Coordinate
screen_width = PixelGrid.Coordinate.from_i64(Screen.width_px)

screen_height : PixelGrid.Coordinate
screen_height = PixelGrid.Coordinate.from_i64(Screen.height_px)

grass_pixel : U32
grass_pixel = I64.to_u32_wrap(SafariShapes.grass_color)

## The sky's colour at the top of the screen and at the horizon.
SkyColors : { top_color : Brush.Rgba, horizon_color : Brush.Rgba }

## The centre of a pixel, as a point on the screen.
pixel_point : { row : PixelGrid.Coordinate, column : PixelGrid.Coordinate } -> ScreenRoll.ScreenPoint
pixel_point = |{ row, column }|
	ScreenRoll.ScreenPoint.(
		{
			x: PixelGrid.pixel_center(column),
			y: PixelGrid.pixel_center(row),
		},
	)
```

**Lines 68–99**: `screen_roll`, `screen_width`, `screen_height`, `grass_pixel`, `SkyColors`, `pixel_point`

```roc
## The sky holds its top colour to SafariShapes' stop on the way down to the
## horizon, then fades to the horizon colour; the grass is below it. The fade
## divides by the horizon rather than shading a Linear brush, whose arithmetic
## rounds differently.
backdrop : ScreenRoll, SkyColors -> List(U32)
backdrop = |roll, sky| {
	var $px = List.with_capacity(screen_width.to_u64() * screen_height.to_u64())
	for row in PixelGrid.Coordinate.first.until(screen_height) {
		for column in PixelGrid.Coordinate.first.until(screen_width) {
			y = roll.to_scene(pixel_point({ row, column })).y
			pixel = if y >= Screen.grass_top_y {
				grass_pixel
			} else {
				t = Brush.clamp01(y / Screen.horizon_y)
				stop = SafariShapes.sky_top_stop
				color = if t <= stop {
					sky.top_color
				} else {
					Brush.mix(sky.top_color, sky.horizon_color, (t - stop) / (1.0 - stop))
				}
				PixelColor.pack({ r: color.r, g: color.g, b: color.b })
			}
			$px = $px.append(pixel)
		}
	}
	$px
}
```

**Lines 101–127**: `backdrop`

```roc
## The sun's glow and then its disc, as SafariShapes paints them, both
## clipped to the sky, before the commands, so the mountains set the sun
## behind them.
paint_sun : List(U32), { roll : ScreenRoll, sun : Sky.SunPlace } -> List(U32)
paint_sun = |pixels, { roll, sun }| {
	fills = SafariShapes.sun_fills(sun)
	on_screen = roll.to_screen(ScreenRoll.ScenePoint.({ x: sun.x, y: sun.y }))
	rows = PixelGrid.pixels_between({
		from: on_screen.y - fills.glow_radius,
		to: on_screen.y + fills.glow_radius,
		count: screen_height,
	})
	columns = PixelGrid.pixels_between({
		from: on_screen.x - fills.glow_radius,
		to: on_screen.x + fills.glow_radius,
		count: screen_width,
	})
	var $px = pixels
	for row in rows.start.until(rows.end) {
		for column in columns.start.until(columns.end) {
			p = roll.to_scene(pixel_point({ row, column }))
			$px = if p.x >= 0.0 and p.x < Screen.width and p.y >= 0.0 and p.y < Screen.horizon_y {
				at = PixelGrid.pixel_index({ row, column, width: screen_width })
				lit = PixelGrid.blend($px, { at, color: Brush.shade(fills.glow, p.x, p.y) })
				distance = F64.sqrt((p.x - sun.x) * (p.x - sun.x) + (p.y - sun.y) * (p.y - sun.y))
				if distance < fills.disc_radius {
					PixelGrid.blend(lit, { at, color: Brush.shade(fills.disc, p.x, p.y) })
				} else {
					lit
				}
			} else {
				$px
			}
		}
	}
	$px
}
```

**Lines 129–165**: `paint_sun`

```roc
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

**Lines 167–194**: `paint_command`

