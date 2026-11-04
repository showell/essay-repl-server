# Review: roc-apps `canvas_apps/safari/SunPixels.roc`

56 lines in 2 chunks, as of commit 82f22a6 safari: the sun moves to SunPixels; ScreenRoll.pixel_point is shared. Reply under any chunk; this paragraph is for the file as a whole.

```roc
## SunPixels paints Safari's sun into a frame's pixels for SafariFrame, so it
## is test code too: the game never runs it. It paints the sun's glow and then
## its disc, as SafariShapes describes them, and clips both to the sky. The
## frame paints the sun before the draw commands, so the mountains can hide it.
import lib.Brush
import PixelGrid
import SafariShapes
import Screen
import ScreenRoll
import Sky

SunPixels :: [].{

	## The sun, if it is in view and big enough to show.
	paint : List(U32), { roll : ScreenRoll, sun : Sky.SunPos } -> List(U32)
	paint = |pixels, { roll, sun }|
		match sun {
			InView(place) if SafariShapes.is_sun_shown(place) => paint_glow_and_disc(pixels, { roll, sun: place })
			InView(_) | OutOfView => pixels
		}
}
```

**Lines 1–21**: `SunPixels`, `paint`

```roc
paint_glow_and_disc : List(U32), { roll : ScreenRoll, sun : Sky.SunPlace } -> List(U32)
paint_glow_and_disc = |pixels, { roll, sun }| {
	fills = SafariShapes.sun_fills(sun)
	on_screen = roll.to_screen(ScreenRoll.ScenePoint.({ x: sun.x, y: sun.y }))
	rows = PixelGrid.pixels_between({
		from: on_screen.y - fills.glow_radius,
		to: on_screen.y + fills.glow_radius,
		count: roll.height_px(),
	})
	columns = PixelGrid.pixels_between({
		from: on_screen.x - fills.glow_radius,
		to: on_screen.x + fills.glow_radius,
		count: roll.width_px(),
	})
	var $px = pixels
	for row in rows.start.until(rows.end) {
		for column in columns.start.until(columns.end) {
			p = roll.to_scene(ScreenRoll.pixel_point({ row, column }))
			$px = if p.x >= 0.0 and p.x < Screen.width and p.y >= 0.0 and p.y < Screen.horizon_y {
				at = PixelGrid.pixel_index({ row, column, width: roll.width_px() })
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

**Lines 23–56**: `paint_glow_and_disc`

