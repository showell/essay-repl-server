# Review: roc-apps `canvas_apps/safari/Mountains.roc`

209 lines in 7 chunks, as of commit 15570a1 safari: one Screen module for the screen's size, horizon and grass line. Reply under any chunk; this paragraph is for the file as a whole.

```roc
## The skyline, drawn behind everything else: a high range to the north with
## snow on its peaks, a lower range to the west, and the rolling land in front
## of both. Each is a silhouette across the screen whose height depends only on
## the bearing it is seen at, so the skyline turns with the rider but never
## comes nearer. The rock darkens at dusk, and the snow goes blue.
import lib.DeviceMath
import Lens
import Num_
import Paint
import Screen
import Sky
import lib.Trig

Mountains :: [].{

	## How the skyline is seen: the rider's heading, and the camera.
	Sight : { heading : F64, cam_focal : F64, view_w : F64 }

	rock : I64
	rock = 0x5B6A8F

	rock_west : I64
	rock_west = 0x39435F

	land : I64
	land = 0x4A8F43
```

**Lines 1–26**: `Mountains`, `Sight`, `rock`, `rock_west`, `land`

```roc
	## How much of its light the rock loses at full dusk.
	rock_night_dim : F64
	rock_night_dim = 0.5

	snow_day : Sky.Rgb
	snow_day = { r: 238.0, g: 243.0, b: 248.0 }

	snow_night : Sky.Rgb
	snow_night = { r: 70.0, g: 84.0, b: 104.0 }

	## One of a colour's channels: 16 is red, 8 green and 0 blue.
	channel : I64, U8 -> F64
	channel = |color, shift| color.shr_wrap(shift).bitwise_and(255).to_f64()

	## A rock colour at `dusk`, from 0 (day) to 1 (night).
	color_at_dusk : I64, F64 -> I64
	color_at_dusk = |color, dusk| {
		light = (1.0 - (rock_night_dim * dusk))
		Sky.pack({
			r: Num_.round_real((channel(color, 16) * light)),
			g: Num_.round_real((channel(color, 8) * light)),
			b: Num_.round_real((channel(color, 0) * light)),
		})
	}

	snow_color : F64 -> I64
	snow_color = |dusk| Sky.pack(Sky.lerp3(snow_day, snow_night, dusk))

	west_range_bearing : F64
	west_range_bearing = (0.0 - 2.0416)
```

**Lines 28–57**: `rock_night_dim`, `snow_day`, `snow_night`, `channel`, `color_at_dusk`, `snow_color`, `west_range_bearing`

```roc
	## The north range is snowy above this height.
	snow_threshold : F64
	snow_threshold = 124.0

	## How far the snowline dips below the threshold under the highest peak.
	snow_dip : F64
	snow_dip = 10.0

	## The silhouettes are sampled every `col_step` pixels across the screen.
	col_step : F64
	col_step = 2.0

	## How far past each side of the screen the silhouettes reach, so the
	## rider's roll never shows their ends.
	roll_margin : F64
	roll_margin = 200.0

	## The rolling land: low, and all the way round.
	ground_base : F64 -> F64
	ground_base = |bearing| (18.0 + (12.0 * Trig.r_sin(((Trig.wrap(bearing, 64) * 0.9) + 1.9))))

	north_range : F64 -> F64
	north_range = |bearing| range_height(north, bearing)

	west_range : F64 -> F64
	west_range = |bearing| range_height(west, bearing)

	## The height of the north range's highest peak, as its samples find it.
	snow_peak_height : F64
	snow_peak_height = highest_north_from((-0.5 + 0.01), north_range(-0.5))
```

**Lines 59–88**: `snow_threshold`, `snow_dip`, `col_step`, `roll_margin`, `ground_base`, `north_range`, `west_range`, `snow_peak_height`

```roc
	## The snowline's height at `bearing`: at the threshold, dipping lower
	## under the higher peaks.
	snowline : F64 -> F64
	snowline = |bearing| {
		above_threshold = (north_range(bearing) - snow_threshold)
		above_fraction = DeviceMath.real_max(0.0, DeviceMath.real_min(1.0, (above_threshold / (snow_peak_height - snow_threshold))))
		(snow_threshold - (snow_dip * above_fraction))
	}

	## The bearing seen at `x` across the screen.
	bearing_at : Mountains.Sight, F64 -> F64
	bearing_at = |sight, x| (sight.heading + Trig.r_atan(((x - (sight.view_w / 2.0)) / sight.cam_focal)))

	## The skyline's height at `bearing`: the highest of the land and the two
	## ranges.
	horizon_crest_px : F64 -> F64
	horizon_crest_px = |bearing| DeviceMath.real_max(west_range(bearing), DeviceMath.real_max(north_range(bearing), ground_base(bearing)))

	## Whether the sun, at `step`, has sunk behind the skyline.
	is_sun_behind_mountains : F64 -> Bool
	is_sun_behind_mountains = |step| ((Sky.sun_height_px(step) + Sky.sun_radius_px) < horizon_crest_px(Sky.sun_bearing))

	## The skyline, back to front: the west range, the north range, the
	## north's snow, then the land.
	draw : { heading : F64, dusk : F64, cam_focal : F64, view_w : F64 } -> List(Paint.DrawCmd)
	draw = |{ heading, dusk, cam_focal, view_w }| {
		sight = { heading, cam_focal, view_w }
		List.join([
			silhouette(sight, { height_at: west_range, color: color_at_dusk(rock_west, dusk) }),
			silhouette(sight, { height_at: north_range, color: color_at_dusk(rock, dusk) }),
			snow(sight, snow_color(dusk)),
			silhouette(sight, { height_at: ground_base, color: land }),
		])
	}
}
```

**Lines 90–124**: `snowline`, `bearing_at`, `horizon_crest_px`, `is_sun_behind_mountains`, `draw`

```roc
## A mountain range: the bearing of its middle, how far it reaches either
## side, its height there, and the two frequencies of the ridges along it.
MountainRange : { center : F64, half_width : F64, peak : F64, ridge_a : F64, ridge_b : F64 }

north : MountainRange
north = { center: 0.0, half_width: 0.95, peak: 150.0, ridge_a: 8.0, ridge_b: 21.0 }

west : MountainRange
west = { center: Mountains.west_range_bearing, half_width: 0.72, peak: 120.0, ridge_a: 11.0, ridge_b: 27.0 }

## A range's height at `bearing`: highest in its middle, falling to nothing at
## its ends, with two ridges along it.
range_height : MountainRange, F64 -> F64
range_height = |range, bearing| {
	from_center = Trig.wrap((bearing - range.center), 64)
	t = (from_center / range.half_width)
	if (DeviceMath.real_abs(t) >= 1.0) {
		0.0
	} else {
		envelope = Trig.r_cos(((t * Trig.pi) / 2.0))
		ridge = ((0.6 + (0.24 * Trig.r_cos((from_center * range.ridge_a)))) + (0.16 * Trig.r_cos(((from_center * range.ridge_b) + 1.0))))
		((range.peak * envelope) * ridge)
	}
}
```

**Lines 126–149**: `MountainRange`, `north`, `west`, `range_height`

```roc
## The highest the north range reaches, sampled every hundredth of a radian
## from `bearing` to half a radian, each sample's bearing the last's plus the
## step.
highest_north_from : F64, F64 -> F64
highest_north_from = |bearing, highest|
	if (bearing > 0.5) {
		highest
	} else {
		highest_north_from((bearing + 0.01), DeviceMath.real_max(highest, Mountains.north_range(bearing)))
	}

## The screen's horizon, where a height of zero is drawn.
horizon_y : F64
horizon_y = Screen.horizon_y

## The screen's y for a height on the skyline.
height_y : Mountains.Sight, F64 -> F64
height_y = |sight, height| (horizon_y - (height * (sight.cam_focal / Lens.focal)))

## The columns sampled, every `col_step` pixels from `from` up to `to`.
columns : { from : F64, to : F64 } -> List(F64)
columns = |{ from, to }| columns_onto([], { at: from, to })

columns_onto : List(F64), { at : F64, to : F64 } -> List(F64)
columns_onto = |sampled, { at, to }|
	if (at > to) {
		sampled
	} else {
		columns_onto(sampled.append(at), { at: (at + Mountains.col_step), to })
	}
```

**Lines 151–180**: `highest_north_from`, `horizon_y`, `height_y`, `columns`, `columns_onto`

```roc
## A silhouette across the screen, its top at `height_at` each bearing, closed
## along the horizon.
silhouette : Mountains.Sight, { height_at : F64 -> F64, color : I64 } -> List(Paint.DrawCmd)
silhouette = |sight, { height_at, color }| {
	left = (0.0 - Mountains.roll_margin)
	right = (sight.view_w + Mountains.roll_margin)
	crest = columns({ from: left, to: right }).map(|x| { x, y: height_y(sight, height_at(Mountains.bearing_at(sight, x))) })
	Paint.push_poly(color, crest.concat([{ x: right, y: horizon_y }, { x: left, y: horizon_y }]))
}

## The north range's snow: along its crest where the range is above the
## snowline, then back along the snowline.
snow : Mountains.Sight, I64 -> List(Paint.DrawCmd)
snow = |sight, color| {
	snowy = columns({ from: 0.0, to: sight.view_w }).keep_if(
		|x| {
			bearing = Mountains.bearing_at(sight, x)
			Mountains.north_range(bearing) > (Mountains.snowline(bearing) + 0.01)
		},
	)
	if (snowy.len() < 2) {
		[]
	} else {
		crest = snowy.map(|x| { x, y: height_y(sight, Mountains.north_range(Mountains.bearing_at(sight, x))) })
		snowline = snowy.fold_rev([], |x, back| back.append({ x, y: height_y(sight, Mountains.snowline(Mountains.bearing_at(sight, x))) }))
		Paint.push_poly(color, crest.concat(snowline))
	}
}
```

**Lines 182–209**: `silhouette`, `snow`

