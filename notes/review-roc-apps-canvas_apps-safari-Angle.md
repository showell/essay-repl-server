# Review: roc-apps `canvas_apps/safari/Angle.roc`

141 lines in 5 chunks, as of commit e054794 safari: the rider's angles as nominal types. Reply under any chunk; this paragraph is for the file as a whole.

```roc
## Safari's angles, in radians, as three types. A bearing is a direction in
## the world: 0 is north, and a bearing grows to the rider's right. A turn is
## the angle between two directions, such as how far the rider's gaze is
## from straight ahead. A turn added to a bearing gives a bearing, and two
## bearings give the turn between them, but two bearings can't be added. A
## lean is how far the bike rolls from upright. It turns the bike only
## through a rate (`steer`), never by being added to a direction. Each operation does the plain float arithmetic its name says,
## so code moved onto these types computes exactly what it did before.
import lib.DeviceMath
import lib.Trig

Angle :: [].{

	Bearing := F64.{

		radians : F64 -> Angle.Bearing
		radians = |r| Angle.Bearing.(r)

		to_radians : Angle.Bearing -> F64
		to_radians = |Angle.Bearing.(r)| r

		## The bearing `turn` to the right of this one.
		plus : Angle.Bearing, Angle.Turn -> Angle.Bearing
		plus = |Angle.Bearing.(b), Angle.Turn.(t)| Angle.Bearing.(b + t)

		## The shortest turn from `from` round to this bearing, between minus
		## and plus a half turn.
		turn_from : Angle.Bearing, Angle.Bearing -> Angle.Turn
		turn_from = |Angle.Bearing.(b), Angle.Bearing.(from)| Angle.Turn.(Trig.wrap(b - from, 64))

		## The shortest turn from north round to this bearing.
		turn_from_north : Angle.Bearing -> Angle.Turn
		turn_from_north = |Angle.Bearing.(b)| Angle.Turn.(Trig.wrap(b, 64))

		## Whether this bearing is further right than `other`, read without
		## going round: for a sweep across a stretch of bearings.
		is_gt : Angle.Bearing, Angle.Bearing -> Bool
		is_gt = |Angle.Bearing.(b), Angle.Bearing.(other)| b > other

		is_eq : _
	}
```

**Lines 1–41**: `Angle`, `Bearing`

```roc
	Turn := F64.{

		radians : F64 -> Angle.Turn
		radians = |r| Angle.Turn.(r)

		to_radians : Angle.Turn -> F64
		to_radians = |Angle.Turn.(r)| r

		plus : Angle.Turn, Angle.Turn -> Angle.Turn
		plus = |Angle.Turn.(t), Angle.Turn.(other)| Angle.Turn.(t + other)

		minus : Angle.Turn, Angle.Turn -> Angle.Turn
		minus = |Angle.Turn.(t), Angle.Turn.(other)| Angle.Turn.(t - other)

		times : Angle.Turn, F64 -> Angle.Turn
		times = |Angle.Turn.(t), factor| Angle.Turn.(t * factor)

		## The same turn taken to the right.
		abs : Angle.Turn -> Angle.Turn
		abs = |Angle.Turn.(t)| Angle.Turn.(DeviceMath.real_abs(t))

		## The smaller of this turn and `other`.
		min : Angle.Turn, Angle.Turn -> Angle.Turn
		min = |Angle.Turn.(t), Angle.Turn.(other)| Angle.Turn.(DeviceMath.real_min(t, other))
```

**Lines 43–66**: `Turn` (part 1 of 2)

```roc
		## This turn, held to no more than `limit` either way.
		within : Angle.Turn, Angle.Turn -> Angle.Turn
		within = |Angle.Turn.(t), Angle.Turn.(limit)| Angle.Turn.(DeviceMath.real_max(0.0 - limit, DeviceMath.real_min(limit, t)))

		## How many of `whole` this turn is: negative for a turn to the left.
		fraction_of : Angle.Turn, Angle.Turn -> F64
		fraction_of = |Angle.Turn.(t), Angle.Turn.(whole)| t / whole

		is_gt : Angle.Turn, Angle.Turn -> Bool
		is_gt = |Angle.Turn.(t), Angle.Turn.(other)| t > other

		is_gte : Angle.Turn, Angle.Turn -> Bool
		is_gte = |Angle.Turn.(t), Angle.Turn.(other)| t >= other

		is_lt : Angle.Turn, Angle.Turn -> Bool
		is_lt = |Angle.Turn.(t), Angle.Turn.(other)| t < other

		is_lte : Angle.Turn, Angle.Turn -> Bool
		is_lte = |Angle.Turn.(t), Angle.Turn.(other)| t <= other

		is_eq : _
	}
```

**Lines 68–89**: `Turn` (part 2 of 2)

```roc
	Lean := F64.{

		radians : F64 -> Angle.Lean
		radians = |r| Angle.Lean.(r)

		to_radians : Angle.Lean -> F64
		to_radians = |Angle.Lean.(r)| r

		plus : Angle.Lean, Angle.Lean -> Angle.Lean
		plus = |Angle.Lean.(l), Angle.Lean.(other)| Angle.Lean.(l + other)

		minus : Angle.Lean, Angle.Lean -> Angle.Lean
		minus = |Angle.Lean.(l), Angle.Lean.(other)| Angle.Lean.(l - other)

		## The lean halfway between this one and `other`.
		halfway_to : Angle.Lean, Angle.Lean -> Angle.Lean
		halfway_to = |Angle.Lean.(l), Angle.Lean.(other)| Angle.Lean.((l + other) / 2.0)

		## The same lean taken to the right.
		abs : Angle.Lean -> Angle.Lean
		abs = |Angle.Lean.(l)| Angle.Lean.(DeviceMath.real_abs(l))

		## The turn this lean makes at `rate` radians of turn for each radian
		## of lean.
		steer : Angle.Lean, F64 -> Angle.Turn
		steer = |Angle.Lean.(l), rate| Angle.Turn.(rate * l)

		is_gt : Angle.Lean, Angle.Lean -> Bool
		is_gt = |Angle.Lean.(l), Angle.Lean.(other)| l > other

		is_gte : Angle.Lean, Angle.Lean -> Bool
		is_gte = |Angle.Lean.(l), Angle.Lean.(other)| l >= other

		is_lt : Angle.Lean, Angle.Lean -> Bool
		is_lt = |Angle.Lean.(l), Angle.Lean.(other)| l < other

		is_lte : Angle.Lean, Angle.Lean -> Bool
		is_lte = |Angle.Lean.(l), Angle.Lean.(other)| l <= other

		is_eq : _
	}
```

**Lines 91–131**: `Lean`

```roc
	north : Angle.Bearing
	north = Angle.Bearing.(0.0)

	straight_ahead : Angle.Turn
	straight_ahead = Angle.Turn.(0.0)

	upright : Angle.Lean
	upright = Angle.Lean.(0.0)
}
```

**Lines 133–141**: `north`, `straight_ahead`, `upright`

