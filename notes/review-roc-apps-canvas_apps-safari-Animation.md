# Review: roc-apps `canvas_apps/safari/Animation.roc`

257 lines in 9 chunks, as of commit c506171 safari: Animation, the stages and the timeline a critter plays. Reply under any chunk; this paragraph is for the file as a whole.

```roc
## How a critter plays out as the rider comes. Animation holds two ideas that
## know nothing of each other. A rule, `over_gap` or `over_steps`, turns where
## the rider is into a stage: waiting, playing, or past. A timeline turns a
## stage into a moment: how the critter looks and where it is. A timeline is
## data, so a critter's whole animation reads in one place, as a score.
##
## A timeline runs on two tracks, one for how the critter looks and one for
## where it goes, because the two change at different points. Each track's
## cuts are in steps from the start of the timeline. The moments before and
## after are the timeline's own, because a critter can rest somewhere no
## stretch of a track ever reaches.
##
## A spot is relative to the critter's home, which only its owner knows, so
## critters with different homes can share a timeline.
import Easing
import Speed
import lib.Trig

Animation :: [].{

	## How the rider comes on a thing: the gap from the rider ahead to it, in
	## metres, and the rider's speed.
	Approach : { gap : F64, speed : Speed }
```

**Lines 1–23**: `Animation`, `Approach`

```roc
	## Where an animation has got to: not begun, playing and this far through,
	## from 0 to 1, or over, with the rider this many metres beyond its end.
	Stage : [
		Waiting,
		Playing(F64),
		Past(F64),
	]

	## A rider this slow is standing still.
	standstill : Speed
	standstill = Speed.metres_a_step(0.000001)

	## An animation that plays while the rider closes from `starts_at` metres
	## to `ends_at`, however fast. It is playing only strictly between the two,
	## so a critter is at rest at both ends.
	over_gap : { starts_at : F64, ends_at : F64 }, F64 -> Animation.Stage
	over_gap = |{ starts_at, ends_at }, gap| {
		progress = Easing.clamp01((starts_at - gap) / (starts_at - ends_at))
		if progress <= 0.0 {
			Waiting
		} else if progress >= 1.0 {
			Past(ends_at - gap)
		} else {
			Playing(progress)
		}
	}
```

**Lines 25–50**: `Stage`, `standstill`, `over_gap`

```roc
	## An animation that takes `steps` steps at the rider's speed, and ends
	## with the rider `buffer` metres short, however fast the rider comes. It
	## is playing from the moment the rider is that many steps away, and a
	## rider standing still inside that stretch holds it at its start.
	over_steps : { steps : F64, buffer : F64 }, Animation.Approach -> Animation.Stage
	over_steps = |{ steps, buffer }, { gap, speed }| {
		gap_left = gap - buffer
		stretch = speed.distance_in(steps)
		if gap_left <= 0.0 {
			Past(0.0 - gap_left)
		} else if gap_left > stretch {
			Waiting
		} else if speed <= standstill {
			Playing(0.0)
		} else {
			Playing(Easing.clamp01(1.0 - gap_left / stretch))
		}
	}
```

**Lines 52–69**: `over_steps`

```roc
	## A place, relative to a critter's home. What `lift` measures is the
	## critter's own affair.
	Spot : {
		along : F64,
		across : F64,
		lift : F64,
	}

	## How a move spreads over its stretch.
	Ease : [Steady, Smooth, ThreeQuarterPower]

	## A move in a straight line.
	Line : {
		from : Animation.Spot,
		to : Animation.Spot,
		ease : Animation.Ease,
	}

	## Where a critter goes over one stretch of a timeline. An arc's top is
	## `rise` above its line, halfway through the stretch, however it is eased.
	Path : [
		StaysAt(Animation.Spot),
		Line(Animation.Line),
		Arc({ line : Animation.Line, rise : F64 }),
	]
```

**Lines 71–95**: `Spot`, `Ease`, `Line`, `Path`

```roc
	## How a critter looks over one stretch of a timeline. One that alternates
	## shows `up` while the sine of its cycle is positive, and `down` otherwise.
	## It goes through `count` cycles in `over` steps counted from the
	## timeline's start, so a beat runs on across a cut without restarting.
	Looks(pose) : [
		Holds(pose),
		Alternates(
			{
				up : pose,
				down : pose,
				count : F64,
				over : F64,
			},
		),
	]

	## Where a stretch ends, in steps from the timeline's start: the cut's own
	## step belongs to the stretch that ends `Through` it, and to the next one
	## after a stretch that ends `Before` it.
	Cut : [Through(F64), Before(F64)]

	## One stretch of a track, and what plays over it. It begins where the
	## stretch before it ended, or at the timeline's start.
	Stretch(kind) : { until : Animation.Cut, plays : kind }

	## One track of a timeline. The last stretch needs no cut, so a track always
	## has something to play: it runs to the timeline's end.
	Track(kind) : { stretches : List(Animation.Stretch(kind)), finally : kind }

	## A critter at one moment: how it looks, and where it is.
	Moment(pose) : { pose : pose, spot : Animation.Spot }
```

**Lines 97–127**: `Looks`, `Cut`, `Stretch`, `Track`, `Moment`

```roc
	## A whole animation: how many steps long it is, the critter at rest before
	## and after, how it looks, and where it goes.
	Timeline(pose) := {
		steps : F64,
		before : Animation.Moment(pose),
		after : Animation.Moment(pose),
		looks : Animation.Track(Animation.Looks(pose)),
		path : Animation.Track(Animation.Path),
	}.{

		## The critter at `stage`.
		moment : Animation.Timeline(pose), Animation.Stage -> Animation.Moment(pose)
		moment = |timeline, stage| {
			Animation.Timeline.(score) = timeline
			match stage {
				Waiting => score.before
				Playing(progress) => timeline.at_step(progress * score.steps)
				Past(_) => score.after
			}
		}

		## The critter `step` steps into the animation.
		at_step : Animation.Timeline(pose), F64 -> Animation.Moment(pose)
		at_step = |Animation.Timeline.(score), step| {
			looks = playing_at(score.looks, { step, steps: score.steps })
			path = playing_at(score.path, { step, steps: score.steps })
			{
				pose: pose_of(looks.plays, step),
				spot: path_spot(path.plays, (step - path.from) / (path.to - path.from)),
			}
		}
	}
}
```

**Lines 129–161**: `Timeline`

```roc
## What a track plays over one stretch, and the steps it begins and ends at.
StretchPlaying(kind) : {
	plays : kind,
	from : F64,
	to : F64,
}

## What a track plays at `step`, of `steps` in all.
playing_at : Animation.Track(kind), { step : F64, steps : F64 } -> StretchPlaying(kind)
playing_at = |track, { step, steps }| {
	var $from = 0.0
	for stretch in track.stretches {
		to =
			match stretch.until {
				Through(cut) | Before(cut) => cut
			}
		if is_short_of(step, stretch.until) {
			return {
				plays: stretch.plays,
				from: $from,
				to,
			}
		}
		$from = to
	}
	{
		plays: track.finally,
		from: $from,
		to: steps,
	}
}

is_short_of : F64, Animation.Cut -> Bool
is_short_of = |step, cut|
	match cut {
		Through(last) => step <= last
		Before(first_past) => step < first_past
	}
```

**Lines 163–200**: `StretchPlaying`, `playing_at`, `is_short_of`

```roc
## The pose `looks` shows `step` steps into the timeline.
pose_of : Animation.Looks(pose), F64 -> pose
pose_of = |looks, step|
	match looks {
		Holds(pose) => pose
		Alternates(
			{
				up,
				down,
				count,
				over,
			},
		) =>
			if Trig.r_sin((step / over) * count * Trig.two_pi) > 0.0 {
				up
			} else {
				down
			}
	}

## The spot `fraction` of the way through a stretch of `path`.
path_spot : Animation.Path, F64 -> Animation.Spot
path_spot = |path, fraction|
	match path {
		StaysAt(spot) => spot
		Line(line) => line_spot(line, fraction)
		Arc({ line, rise }) => {
			on_line = line_spot(line, fraction)
			{ ..on_line, lift: on_line.lift + rise * 4.0 * fraction * (1.0 - fraction) }
		}
	}
```

**Lines 202–232**: `pose_of`, `path_spot`

```roc
## The spot `fraction` of the way along `line`.
line_spot : Animation.Line, F64 -> Animation.Spot
line_spot = |line, fraction| {
	eased = eased_fraction(line.ease, fraction)
	between = |start, end|
		Easing.lerp({
			from: start,
			to: end,
			fraction: eased,
		})
	{
		along: between(line.from.along, line.to.along),
		across: between(line.from.across, line.to.across),
		lift: between(line.from.lift, line.to.lift),
	}
}

eased_fraction : Animation.Ease, F64 -> F64
eased_fraction = |ease, fraction|
	match ease {
		Steady => fraction
		Smooth => Easing.smoothstep(fraction)
		ThreeQuarterPower => Easing.three_quarter_power(fraction)
	}
```

**Lines 234–257**: `line_spot`, `eased_fraction`

