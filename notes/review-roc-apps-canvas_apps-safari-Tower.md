# Review: roc-apps `canvas_apps/safari/Tower.roc`

294 lines in 11 chunks, as of commit dfdec4e safari/Tower: a mast as types, not ten positional floats. Reply under any chunk; this paragraph is for the file as a whole.

```roc
## A radio mast: a square lattice that tapers from a 12 m footprint to a
## point 80 m up. It is drawn as rods (four legs, a ring every 20 m, and
## crossed braces in the lowest two stages) with a blinking beacon on top.
## The earth curves away under a far mast, so it sinks below the horizon
## from the bottom up.
import Camera
import lib.DeviceMath
import Geom
import Num_
import Paint
import lib.Trig

Tower :: [].{

	tower_height : F64
	tower_height = 80.0

	tower_half : F64
	tower_half = 6.0

	stage_height : F64
	stage_height = 20.0

	brace_stages : I64
	brace_stages = 2

	rod_half : F64
	rod_half = 0.12

	rod_w : F64
	rod_w = (rod_half * 2.0)

	tower_metal : I64
	tower_metal = 10133672
```

**Lines 1–34**: `Tower`, `tower_height`, `tower_half`, `stage_height`, `brace_stages`, `rod_half`, `rod_w`, `tower_metal`

```roc
	## The earth's radius for sinking masts. It is far smaller than the real
	## one, so a mast sinks visibly as it recedes.
	earth_radius : F64
	earth_radius = 20000.0

	beacon_radius : F64
	beacon_radius = 3.0

	beacon_color : I64
	beacon_color = 16723942

	beacon_period : F64
	beacon_period = 120.0

	## A corner of the mast's square footprint, as seen along the route.
	Corner : [BackLeft, BackRight, FrontRight, FrontLeft]

	## Where the footprint's four corners stand in the rider's view.
	Footprint : {
		back_left : Geom.RiderPt,
		back_right : Geom.RiderPt,
		front_right : Geom.RiderPt,
		front_left : Geom.RiderPt,
	}
```

**Lines 36–59**: `earth_radius`, `beacon_radius`, `beacon_color`, `beacon_period`, `Corner`, `Footprint`

```roc
	## How a rod is drawn: its width on screen, and the camera.
	RodView : {
		rod_width_px : F64,
		cam_focal : F64,
		view_w : F64,
	}

	## One mast, ready to draw: where it stands, how far the earth's curve
	## has sunk it, and how its rods are drawn.
	Mast : {
		footprint : Tower.Footprint,
		center : Geom.RiderPt,
		sunk : F64,
		view : Tower.RodView,
	}

	## The corners in drawing order, going round the square.
	corners : List(Tower.Corner)
	corners = [BackLeft, BackRight, FrontRight, FrontLeft]

	## The corner after this one, going round the square.
	next_corner : Tower.Corner -> Tower.Corner
	next_corner = |corner|
		match corner {
			BackLeft => BackRight
			BackRight => FrontRight
			FrontRight => FrontLeft
			FrontLeft => BackLeft
		}
```

**Lines 61–89**: `RodView`, `Mast`, `corners`, `next_corner`

```roc
	## Which way a corner lies from the footprint's centre, across the route
	## and along it.
	corner_offset : Tower.Corner -> { across : F64, along : F64 }
	corner_offset = |corner|
		match corner {
			BackLeft => { across: -1.0, along: -1.0 }
			BackRight => { across: 1.0, along: -1.0 }
			FrontRight => { across: 1.0, along: 1.0 }
			FrontLeft => { across: -1.0, along: 1.0 }
		}

	footprint_corner : Tower.Footprint, Tower.Corner -> Geom.RiderPt
	footprint_corner = |footprint, corner|
		match corner {
			BackLeft => footprint.back_left
			BackRight => footprint.back_right
			FrontRight => footprint.front_right
			FrontLeft => footprint.front_left
		}

	beacon_offset_for : I64 -> F64
	beacon_offset_for = |n| I64.to_f64(((n * 37) - (I64.div_trunc_by((n * 37), 120) * 120)))

	beacon_brightness : F64 -> F64
	beacon_brightness = |phase| {
		wrapped = Num_.mod_real((Num_.mod_real(phase, beacon_period) + beacon_period), beacon_period)
		((1.0 - Trig.r_cos((((2.0 * Trig.pi) * wrapped) / beacon_period))) / 2.0)
	}
```

**Lines 91–118**: `corner_offset`, `footprint_corner`, `beacon_offset_for`, `beacon_brightness`

```roc
	## Where a footprint corner stands on the map, for a mast centred at
	## `along` and `across` and turned by `yaw`.
	base_corner_ax : Tower.Corner, F64, F64, F64 -> Geom.AX
	base_corner_ax = |corner, along, across, yaw| {
		offset = corner_offset(corner)
		du = (offset.across * tower_half)
		dv = (offset.along * tower_half)
		cy = Trig.r_cos(yaw)
		sy = Trig.r_sin(yaw)
		{ a: (along + ((du * sy) + (dv * cy))), x: (across + ((du * cy) - (dv * sy))) }
	}

	## How far the earth's curve hides the bottom of a mast standing at `p`.
	sunk_below_horizon : Geom.RiderPt -> F64
	sunk_below_horizon = |p| (((p.right * p.right) + (p.forward * p.forward)) / (2.0 * earth_radius))

	## The point `fraction` of the way from `from` to `to`.
	point_between : { from : Geom.Vec3, to : Geom.Vec3, fraction : F64 } -> Geom.Vec3
	point_between = |{ from, to, fraction }| {
		right: (from.right + ((to.right - from.right) * fraction)),
		forward: (from.forward + ((to.forward - from.forward) * fraction)),
		height: (from.height + ((to.height - from.height) * fraction)),
	}
```

**Lines 120–142**: `base_corner_ax`, `sunk_below_horizon`, `point_between`

```roc
	## A corner of the mast at height `h`: drawn in toward the centre as the
	## mast tapers, and lowered by how far the mast has sunk.
	corner_at : Tower.Mast, Tower.Corner, F64 -> Geom.Vec3
	corner_at = |mast, corner, h| {
		t = (h / tower_height)
		bottom = footprint_corner(mast.footprint, corner)
		{
			right: (bottom.right + ((mast.center.right - bottom.right) * t)),
			forward: (bottom.forward + ((mast.center.forward - bottom.forward) * t)),
			height: (h - mast.sunk),
		}
	}

	## A rod between two points on screen, `width_px` wide.
	screen_rod : { from : Camera.ScreenPt, to : Camera.ScreenPt, width_px : F64 } -> List(Paint.DrawCmd)
	screen_rod = |{ from, to, width_px }| {
		dx = (to.x - from.x)
		dy = (to.y - from.y)
		raw = DeviceMath.real_sqrt(((dx * dx) + (dy * dy)))
		len = if (raw < 0.0001) 1.0 else raw
		rod_quad(from, to, ((((0.0 - dy) / len) * width_px) / 2.0), (((dx / len) * width_px) / 2.0))
	}

	rod_quad : Camera.ScreenPt, Camera.ScreenPt, F64, F64 -> List(Paint.DrawCmd)
	rod_quad = |a, b, ox, oy| Paint.push_poly(tower_metal, [{ x: (a.x + ox), y: (a.y + oy) }, { x: (b.x + ox), y: (b.y + oy) }, { x: (b.x - ox), y: (b.y - oy) }, { x: (a.x - ox), y: (a.y - oy) }])
```

**Lines 144–168**: `corner_at`, `screen_rod`, `rod_quad`

```roc
	## A rod between two points in the rider's view. A rod with one end
	## behind the near plane is cut there; one with both ends behind it is
	## not drawn.
	rod : Tower.RodView, { from : Geom.Vec3, to : Geom.Vec3 } -> List(Paint.DrawCmd)
	rod = |view, { from, to }|
		match (sight_of(from), sight_of(to)) {
			(InView, InView) => rod_on_screen(view, { from, to })
			(InView, BehindCamera) => rod_on_screen(view, { from, to: cut_at_near({ from, to }) })
			(BehindCamera, InView) => rod_on_screen(view, { from: cut_at_near({ from, to }), to })
			(BehindCamera, BehindCamera) => []
		}

	sight_of : Geom.Vec3 -> [InView, BehindCamera]
	sight_of = |point| if (point.forward >= Geom.near) InView else BehindCamera

	## Where the line from `from` to `to` crosses the near plane.
	cut_at_near : { from : Geom.Vec3, to : Geom.Vec3 } -> Geom.Vec3
	cut_at_near = |{ from, to }| point_between({ from, to, fraction: ((Geom.near - from.forward) / (to.forward - from.forward)) })

	rod_on_screen : Tower.RodView, { from : Geom.Vec3, to : Geom.Vec3 } -> List(Paint.DrawCmd)
	rod_on_screen = |view, { from, to }|
		screen_rod({
			from: Camera.project(from, view.cam_focal, view.view_w),
			to: Camera.project(to, view.cam_focal, view.view_w),
			width_px: view.rod_width_px,
		})
```

**Lines 170–195**: `rod`, `sight_of`, `cut_at_near`, `rod_on_screen`

```roc
	## How many pixels one metre across spans at distance `forward`.
	metre_px : { forward : F64, cam_focal : F64, view_w : F64 } -> F64
	metre_px = |{ forward, cam_focal, view_w }| {
		p1 = Camera.project({ right: 1.0, forward: forward, height: 0.0 }, cam_focal, view_w)
		p0 = Camera.project({ right: 0.0, forward: forward, height: 0.0 }, cam_focal, view_w)
		(p1.x - p0.x)
	}

	## A rod's width on screen at distance `forward`.
	rod_width_at : { forward : F64, cam_focal : F64, view_w : F64 } -> F64
	rod_width_at = |camera| (rod_w * metre_px(camera))

	## The four legs, from the footprint's corners up to the apex.
	legs : Tower.Mast, Geom.Vec3 -> List(Paint.DrawCmd)
	legs = |mast, apex| List.join_map(corners, |corner| rod(mast.view, { from: corner_at(mast, corner, mast.sunk), to: apex }))

	## The ring of rods round the mast at height `h`.
	ring : Tower.Mast, F64 -> List(Paint.DrawCmd)
	ring = |mast, h| List.join_map(corners, |corner| rod(mast.view, { from: corner_at(mast, corner, h), to: corner_at(mast, next_corner(corner), h) }))

	## A ring at every stage below the top, bottom first, leaving out those
	## the earth has hidden.
	rings : Tower.Mast -> List(Paint.DrawCmd)
	rings = |mast| List.join_map(ring_heights_from(stage_height), |h| if (h <= mast.sunk) [] else ring(mast, h))

	ring_heights_from : F64 -> List(F64)
	ring_heights_from = |h| if (h >= tower_height) [] else List.concat([h], ring_heights_from((h + stage_height)))
```

**Lines 197–223**: `metre_px`, `rod_width_at`, `legs`, `ring`, `rings`, `ring_heights_from`

```roc
	## The crossed braces of the lowest stages, bottom first. A stage the
	## earth has partly hidden starts its braces at the horizon.
	braces : Tower.Mast -> List(Paint.DrawCmd)
	braces = |mast| List.join_map(brace_stages_from(0), |stage| brace_stage(mast, stage))

	brace_stages_from : I64 -> List(I64)
	brace_stages_from = |stage| if (stage >= brace_stages) [] else List.concat([stage], brace_stages_from((stage + 1)))

	brace_stage : Tower.Mast, I64 -> List(Paint.DrawCmd)
	brace_stage = |mast, stage| {
		stage_bottom = (I64.to_f64(stage) * stage_height)
		stage_top = (stage_bottom + stage_height)
		if (stage_top <= mast.sunk) {
			[]
		} else {
			hidden_fraction = ((DeviceMath.real_max(stage_bottom, mast.sunk) - stage_bottom) / stage_height)
			List.join_map(corners, |corner| brace_pair(mast, { corner, stage_bottom, stage_top, hidden_fraction }))
		}
	}
```

**Lines 225–243**: `braces`, `brace_stages_from`, `brace_stage`

```roc
	## The two braces crossing the face from `corner` to the next corner: one
	## rising each way.
	brace_pair : Tower.Mast, { corner : Tower.Corner, stage_bottom : F64, stage_top : F64, hidden_fraction : F64 } -> List(Paint.DrawCmd)
	brace_pair = |mast, { corner, stage_bottom, stage_top, hidden_fraction }| {
		next = next_corner(corner)
		brace_up = rod(
			mast.view,
			{
				from: point_between({ from: corner_at(mast, corner, stage_bottom), to: corner_at(mast, next, stage_top), fraction: hidden_fraction }),
				to: corner_at(mast, next, stage_top),
			},
		)
		brace_down = rod(
			mast.view,
			{
				from: point_between({ from: corner_at(mast, next, stage_bottom), to: corner_at(mast, corner, stage_top), fraction: hidden_fraction }),
				to: corner_at(mast, corner, stage_top),
			},
		)
		List.concat(brace_up, brace_down)
	}
```

**Lines 245–265**: `brace_pair`

```roc
	## The beacon on the apex, at its brightness; too dim or too small, it
	## isn't drawn.
	beacon : Tower.Mast, Geom.Vec3, F64 -> List(Paint.DrawCmd)
	beacon = |mast, apex, brightness| {
		apex_on_screen = Camera.project(apex, mast.view.cam_focal, mast.view.view_w)
		if (brightness < 0.02) {
			[]
		} else {
			radius = (beacon_radius * metre_px({ forward: mast.center.forward, cam_focal: mast.view.cam_focal, view_w: mast.view.view_w }))
			if (radius < 0.5) [] else Paint.push_beacon(beacon_color, apex_on_screen.x, apex_on_screen.y, radius, brightness)
		}
	}

	## The whole mast: legs, rings, braces and beacon, in that order. A mast
	## behind the camera, or sunk wholly below the horizon, draws nothing.
	draw : { footprint : Tower.Footprint, center : Geom.RiderPt, cam_focal : F64, view_w : F64, beacon_phase : F64 } -> List(Paint.DrawCmd)
	draw = |{ footprint, center, cam_focal, view_w, beacon_phase }| {
		sunk = sunk_below_horizon(center)
		if (center.forward < Geom.near or sunk >= tower_height) {
			[]
		} else {
			view = { rod_width_px: rod_width_at({ forward: center.forward, cam_focal, view_w }), cam_focal, view_w }
			mast = { footprint, center, sunk, view }
			apex = { right: center.right, forward: center.forward, height: (tower_height - sunk) }
			List.join([legs(mast, apex), rings(mast), braces(mast), beacon(mast, apex, beacon_brightness(beacon_phase))])
		}
	}
}
```

**Lines 267–294**: `beacon`, `draw`

