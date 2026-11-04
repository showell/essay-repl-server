# Review: roc-apps `canvas_apps/safari/BackdropPixels.roc`

51 lines in 2 chunks, as of commit 19ea037 safari: the sky and grass move to BackdropPixels; SafariFrame is the glue. Reply under any chunk; this paragraph is for the file as a whole.

```roc
## BackdropPixels paints the sky and the grass, the first layer of a frame's
## pixels for SafariFrame, so it is test code too: the game never runs it (see
## SafariFrame for more context). The mountains are not part of it: they are
## draw commands, which the game and SafariFrame both paint on top.
import lib.Brush
import PixelColor
import PixelGrid
import SafariShapes
import Screen
import ScreenRoll
```

**Lines 1–10**

```roc
BackdropPixels :: [].{

	## The sky and the grass, given the sky's colour at the top of the screen
	## and at the horizon, as 0xRRGGBB.
	##
	## The sky holds its top colour to SafariShapes' stop on the way down to
	## the horizon, then fades to the horizon colour; the grass is below it.
	## The fade divides by the horizon rather than shading a Linear brush,
	## whose arithmetic rounds differently.
	paint : ScreenRoll, { sky_top : I64, sky_horizon : I64 } -> List(U32)
	paint = |roll, { sky_top, sky_horizon }| {
		top_color = Brush.opaque(sky_top)
		horizon_color = Brush.opaque(sky_horizon)
		width = roll.width_px()
		height = roll.height_px()
		var $px = List.with_capacity(width.to_u64() * height.to_u64())
		for row in PixelGrid.Coordinate.first.until(height) {
			for column in PixelGrid.Coordinate.first.until(width) {
				y = roll.to_scene(ScreenRoll.pixel_point({ row, column })).y
				pixel = if y >= Screen.grass_top_y {
					grass_pixel
				} else {
					t = Brush.clamp01(y / Screen.horizon_y)
					stop = SafariShapes.sky_top_stop
					color = if t <= stop {
						top_color
					} else {
						Brush.mix(top_color, horizon_color, (t - stop) / (1.0 - stop))
					}
					PixelColor.pack({ r: color.r, g: color.g, b: color.b })
				}
				$px = $px.append(pixel)
			}
		}
		$px
	}
}

grass_pixel : U32
grass_pixel = I64.to_u32_wrap(SafariShapes.grass_color)
```

**Lines 12–51**: `BackdropPixels`, `paint`, `grass_pixel`

