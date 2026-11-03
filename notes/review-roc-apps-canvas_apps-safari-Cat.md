# Review: roc-apps `canvas_apps/safari/Cat.roc`

255 lines in 9 chunks, as of commit f1c9540 safari/Cat: poses as tags, the rider's approach as a record. Reply under any chunk; this paragraph is for the file as a whole.

```roc
## A cat that crosses the road ahead of the rider. It waits by a roadside
## tree, then, as the rider comes, walks out into the lane, freezes there,
## and leaps clear to the far verge. How far through its crossing it is
## depends only on how far ahead it is and how fast the rider comes: it
## starts when the rider is `cross_frames` steps away, and is across when the
## rider is `road_buffer` metres from it. The rider's eye is drawn to it while
## it crosses, and lets it go after.
import lib.DeviceMath
import Num_
import lib.Trig

Cat :: [].{

	## Where a cat crosses: how far along its segment, and its place across
	## the road at the start, in the middle of the lane, and at the end.
	Crossing : {
		along : F64,
		start_across : F64,
		mid_across : F64,
		end_across : F64,
		height : F64,
	}

	## How the cat holds itself: walking, it is at rest or mid-stride; then
	## frozen; then its leap, from the coil through flight and landing to the
	## collapse after.
	Pose : [Rest, Stride, Frozen, Coil, Flight, Land, Collapse]

	## The cat at a moment: its pose, where it is across the road, and how
	## high it is off the ground.
	CatState : { pose : Cat.Pose, across : F64, lift : F64 }
```

**Lines 1–31**: `Cat`, `Crossing`, `Pose`, `CatState`

```roc
	## How the rider comes on a cat: the gap from the rider ahead to it, in
	## metres, and the rider's speed, in metres a step.
	Approach : { gap : F64, speed : F64 }

	cat_height : F64
	cat_height = 1.7

	## How far along its segment the cat waits, before it is moved to just
	## past the nearest tree.
	cat_along : F64
	cat_along = 105.0

	## How far out from its tree, towards the road, the cat starts.
	cat_road_gap : F64
	cat_road_gap = 1.5

	## How far past its tree, along the road, the cat crosses.
	cat_beyond_tree : F64
	cat_beyond_tree = 2.0

	## Where the cat's head is across its body, in cat heights; it freezes
	## with its head in the middle of the lane.
	cat_head_x : F64
	cat_head_x = (0.0 - 0.48)

	## How far the cat's hind feet land past the grass's edge.
	land_hind_reach : F64
	land_hind_reach = (0.7 * cat_height)
```

**Lines 33–60**: `Approach`, `cat_height`, `cat_along`, `cat_road_gap`, `cat_beyond_tree`, `cat_head_x`, `land_hind_reach`

```roc
	## How far onto the far verge's grass the cat's landing reaches.
	grass_toehold : F64
	grass_toehold = 0.3

	## The crossing of a cat by the tree `tree_offset` out from the lane's
	## edge and `tree_along` along the segment.
	crossing : { lane_half_width : F64, tree_offset : F64, tree_along : F64 } -> Cat.Crossing
	crossing = |{ lane_half_width, tree_offset, tree_along }| {
		tree_across = (lane_half_width + tree_offset)
		{
			along: (tree_along + cat_beyond_tree),
			start_across: (tree_across + cat_road_gap),
			mid_across: ((0.0 - cat_head_x) * cat_height),
			end_across: ((0.0 - (lane_half_width + grass_toehold)) - land_hind_reach),
			height: cat_height,
		}
	}

	## The crossing's three stages, in steps.
	enters_road_steps : F64
	enters_road_steps = 10.0

	frozen_steps : F64
	frozen_steps = 24.0

	escapes_steps : F64
	escapes_steps = 4.0

	cross_frames : F64
	cross_frames = ((enters_road_steps + frozen_steps) + escapes_steps)
```

**Lines 62–91**: `grass_toehold`, `crossing`, `enters_road_steps`, `frozen_steps`, `escapes_steps`, `cross_frames`

```roc
	## How far short of the cat the rider is when it is across.
	road_buffer : F64
	road_buffer = 3.0

	## A rider this slow, in metres a step, is standing still.
	standstill : F64
	standstill = 0.000001

	## Whether the cat is crossing in front of the rider now.
	is_in_danger : Cat.Approach -> Bool
	is_in_danger = |{ gap, speed }| {
		gap_left = (gap - road_buffer)
		gap_left > 0.0 and gap_left <= (cross_frames * speed)
	}

	clamp01 : F64 -> F64
	clamp01 = |x|
		if (x < 0.0) {
			0.0
		} else if (x > 1.0) {
			1.0
		} else {
			x
		}

	lerp : { from : F64, to : F64, fraction : F64 } -> F64
	lerp = |{ from, to, fraction }| (from + ((to - from) * fraction))
```

**Lines 93–119**: `road_buffer`, `standstill`, `is_in_danger`, `clamp01`, `lerp`

```roc
	## How far through its crossing the cat is, from 0 to 1. A cat the rider
	## has reached is across; for a rider standing still, a cat ahead hasn't
	## started.
	crossing_progress : Cat.Approach -> F64
	crossing_progress = |{ gap, speed }| {
		gap_left = (gap - road_buffer)
		if (gap_left <= 0.0) {
			1.0
		} else if (speed <= standstill) {
			0.0
		} else {
			clamp01((1.0 - (gap_left / (cross_frames * speed))))
		}
	}

	## How hard the cat holds the rider's eye at its strongest.
	focus_peak : F64
	focus_peak = 1.8

	## Over how many steps, after the rider reaches the cat, its hold fades.
	focus_ramp_down : F64
	focus_ramp_down = 83.0

	smoothstep : F64 -> F64
	smoothstep = |t| ((t * t) * (3.0 - (2.0 * t)))
```

**Lines 121–145**: `crossing_progress`, `focus_peak`, `focus_ramp_down`, `smoothstep`

```roc
	## How hard the cat holds the rider's eye: rising as it crosses, then
	## fading once the rider is past.
	focus : Cat.Approach -> F64
	focus = |approach| {
		gap_left = (approach.gap - road_buffer)
		if (approach.speed <= standstill) {
			0.0
		} else if (gap_left > 0.0) {
			(smoothstep(crossing_progress(approach)) * focus_peak)
		} else {
			steps_past = (((0.0 - gap_left) / approach.speed) / focus_ramp_down)
			((1.0 - smoothstep(DeviceMath.real_min(steps_past, 1.0))) * focus_peak)
		}
	}

	## A stride is about this many steps.
	stride_steps : F64
	stride_steps = 5.0

	## Where in its stride cycle a cat walking for `steps` is, `progress` of
	## the way through, as an angle: a whole number of strides, at least one.
	stride_angle : { progress : F64, steps : F64 } -> F64
	stride_angle = |{ progress, steps }| {
		strides = Num_.round_real((steps / stride_steps))
		((progress * (if (strides < 1.0) 1.0 else strides)) * Trig.two_pi)
	}
```

**Lines 147–172**: `focus`, `stride_steps`, `stride_angle`

```roc
	## The cat's pose at `progress` through its leap.
	leap_pose : F64 -> Cat.Pose
	leap_pose = |progress|
		if (progress < 0.2) {
			Coil
		} else if (progress < 0.7) {
			Flight
		} else if (progress < 0.95) {
			Land
		} else {
			Collapse
		}

	## The number CatStills draws a pose by.
	pose_index : Cat.Pose -> I64
	pose_index = |pose|
		match pose {
			Rest => 0
			Stride => 1
			Frozen => 2
			Coil => 3
			Flight => 4
			Land => 5
			Collapse => 6
		}

	## The top of the leap, in metres.
	leap_height : F64
	leap_height = 0.18

	three_quarter_power : F64 -> F64
	three_quarter_power = |x| DeviceMath.real_sqrt((x * DeviceMath.real_sqrt(x)))
```

**Lines 174–205**: `leap_pose`, `pose_index`, `leap_height`, `three_quarter_power`

```roc
	## The cat as the rider comes on it.
	state : Cat.Crossing, Cat.Approach -> Cat.CatState
	state = |cat, approach| {
		step = (crossing_progress(approach) * cross_frames)
		escape_at = (enters_road_steps + frozen_steps)
		if (step <= enters_road_steps) {
			entering(cat, step)
		} else if (step <= escape_at) {
			{ pose: Frozen, across: cat.mid_across, lift: 0.0 }
		} else {
			escaping(cat, (step - escape_at))
		}
	}

	## The cat `step` steps into its walk out to the middle of the lane.
	entering : Cat.Crossing, F64 -> Cat.CatState
	entering = |cat, step| {
		progress = (step / enters_road_steps)
		{
			pose: if (Trig.r_sin(stride_angle({ progress, steps: enters_road_steps })) > 0.0) Stride else Rest,
			across: lerp({ from: cat.start_across, to: cat.mid_across, fraction: progress }),
			lift: 0.0,
		}
	}
}
```

**Lines 207–231**: `state`, `entering`

```roc
## The cat `step` steps into its escape: a step coiled, two in the air, then
## landed.
escaping : Cat.Crossing, F64 -> Cat.CatState
escaping = |cat, step| {
	clamped = if (step > Cat.escapes_steps) Cat.escapes_steps else step
	pose = Cat.leap_pose((clamped / Cat.escapes_steps))
	if (clamped < 1.0) {
		{ pose, across: cat.mid_across, lift: 0.0 }
	} else if (clamped < 3.0) {
		airborne(cat, { pose, flown: ((clamped - 1.0) / 2.0) })
	} else {
		{ pose, across: cat.end_across, lift: 0.0 }
	}
}

## The cat `flown` of the way through its flight, from 0 to 1: across the
## road on an arc.
airborne : Cat.Crossing, { pose : Cat.Pose, flown : F64 } -> Cat.CatState
airborne = |cat, { pose, flown }| {
	pose,
	across: Cat.lerp({ from: cat.mid_across, to: cat.end_across, fraction: Cat.three_quarter_power(flown) }),
	lift: (((Cat.leap_height * 4.0) * flown) * (1.0 - flown)),
}
```

**Lines 233–255**: `escaping`, `airborne`

