# Review: roc-apps `canvas_apps/safari/Speed.roc`

67 lines in 3 chunks, as of commit 9da646a safari: an opaque Speed. Reply under any chunk; this paragraph is for the file as a whole.

```roc
## Safari's speeds. A speed is how many metres something covers in one step
## of the ride; the rider and the truck each hold one.
##
## Acceleration stays a plain F64, in metres a step for each step. It passes
## from one of the throttle's gates to the next and ends on a speed, and no
## speed can be mistaken for it: `accelerated_by` takes one, and
## `acceleration_to` and `change_from` give one.
##
## Each operation does the plain float arithmetic its name says, so code
## moved onto this type computes exactly what it did before.
import lib.DeviceMath

Speed :: F64.{

	metres_a_step : F64 -> Speed
	metres_a_step = |metres| Speed.(metres)

	to_metres_a_step : Speed -> F64
	to_metres_a_step = |Speed.(s)| s

	## Standing still.
	at_rest : Speed
	at_rest = Speed.(0.0)
```

**Lines 1–23**: `Speed`, `metres_a_step`, `to_metres_a_step`, `at_rest`

```roc
	## This speed after `acceleration`, the change over one step.
	accelerated_by : Speed, F64 -> Speed
	accelerated_by = |Speed.(s), acceleration| Speed.(s + acceleration)

	## The acceleration over one step that took `earlier` to this speed.
	change_from : Speed, Speed -> F64
	change_from = |Speed.(s), Speed.(earlier)| s - earlier

	## The steady acceleration that brings this speed to `target` over
	## `within` metres.
	acceleration_to : Speed, { target : Speed, within : F64 } -> F64
	acceleration_to = |Speed.(s), { target: Speed.(t), within }| (t * t - s * s) / (2.0 * within)

	times : Speed, F64 -> Speed
	times = |Speed.(s), factor| Speed.(s * factor)

	## How many metres this speed covers in `steps` steps.
	distance_in : Speed, F64 -> F64
	distance_in = |Speed.(s), steps| s * steps

	## How many steps this speed takes to cover `metres`.
	steps_to_cover : Speed, F64 -> F64
	steps_to_cover = |Speed.(s), metres| metres / s
```

**Lines 25–47**: `accelerated_by`, `change_from`, `acceleration_to`, `times`, `distance_in`, `steps_to_cover`

```roc
	## The smaller of this speed and `other`.
	min : Speed, Speed -> Speed
	min = |Speed.(s), Speed.(other)| Speed.(DeviceMath.real_min(s, other))

	## The larger of this speed and `other`.
	max : Speed, Speed -> Speed
	max = |Speed.(s), Speed.(other)| Speed.(DeviceMath.real_max(s, other))

	is_gt : Speed, Speed -> Bool
	is_gt = |Speed.(s), Speed.(other)| s > other

	is_lt : Speed, Speed -> Bool
	is_lt = |Speed.(s), Speed.(other)| s < other

	is_lte : Speed, Speed -> Bool
	is_lte = |Speed.(s), Speed.(other)| s <= other

	is_eq : _
}
```

**Lines 49–67**: `min`, `max`, `is_gt`, `is_lt`, `is_lte`, `is_eq`

