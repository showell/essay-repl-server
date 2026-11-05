*Second draft for Steve's review, 2026-11-05: the opening, the sky and the cat, in a neutral voice, with code expanded by the builder. The bracketed notes are where the live ride and the widgets go.*

# Safari Ride: a tour of a real Roc program

*[The live ride goes here, running as you read.]*

This is Safari Ride. A rider cycles down a long road through open country, past trees, cows and pigs, with a truck somewhere ahead. Radio masts blink in the distance. A bird takes off as the rider comes near. A cat walks into the lane, freezes, and leaps for the far verge. The sun goes down behind the mountains, and the truck turns on its headlights.

Safari Ride has the important parts of a game's world: terrain, physics, a camera, things that react to the player, and a day that ends. It doesn't have game mechanics yet. Nothing keeps score.

This tour reads the program from the bottom up. It's about seventy modules of Roc, which is enough to show how Roc holds up in a program with a lot going on. It assumes you can already read Roc. Each chapter points out a few Roc ideas as they come up, and the useful ones come up more than once.

## All that's stored

A record alias is the plainest way to name a shape in Roc, and it's all this needs. `Safari` itself is a module written as a type: `Safari :: [].{ ... }` holds the definitions other modules can reach.

```roc
## All that is kept from one step to the next: the rider and the truck, each
## moved once a step from where it was, and the clock, which counts the steps.
## Everything else that changes is worked out from these three.
Ride : {
	rider : Pose.RiderState,
	truck : Truck.TruckState,
	clock : F64,
}
```

Those three fields are the whole of what Safari Ride keeps from one step to the next. The cat has no state, and neither does the bird, the sun or the beacons. Each frame works them all out again from the rider, the truck and the clock.

That gives three kinds of moving thing, and the tour is organized around them:

| Kind | Things | How it works |
|---|---|---|
| Stepped | The rider, the truck | Stored in `Ride`, and moved once a step from where it was |
| Rider-driven | The cat, the bird | Worked out from how the rider is approaching, with nothing stored |
| Clock-driven | The sun, the sky, the beacons, the headlights | Worked out from the clock, with nothing stored |

Trees and cows are a fourth kind, the easiest of all: they never change.

Purity makes some things free. Safari Ride can pause and step backward, because a step back only needs an older `Ride`. The cat follows along, since it was never anywhere but where the rider's position puts it, and the sun rises again.

## The sky

The sky is the simplest thing that moves, because it depends on one number.

*[The sky widget goes here: drag the clock and watch the sun set.]*

### A function of the clock

Every function in this chapter's arrow is `->`, not `=>`. In Roc that's a promise the compiler holds: no effects, so the same clock always gives the same sky.

```roc
## How high the sun stands above the horizon at `clock`, in pixels at
## rest; below it once negative.
sun_height_px : F64 -> F64
sun_height_px = |clock| (sun_start_px - (sun_drop_px_per_step * clock))
```

The sun's height is a straight line. It starts at 244 pixels, reaches the horizon around step 3,980, and has fully set around step 4,730.

Dusk is a curve and then a line, which means two cases. `Sky` keeps the two halves below its block. Anything outside `Sky :: [].{ ... }` is private to the module, so a helper stays a helper without any keyword.

```roc
## How far toward dusk the sky is at `clock`, from 0 (day) to 1 (dusk).
dusk_at : F64 -> F64
dusk_at = |clock| {
	height = sun_height_px(clock)
	if (height >= sun_fully_set_px) dusk_while_up(height) else dusk_after_set(height)
}
```

```roc
## How far toward dusk the sky is while the sun, `height` pixels up, is
## still above the line where it has fully set.
dusk_while_up : F64 -> F64
dusk_while_up = |height| {
	set_so_far = ((Sky.sun_start_px - height) / (Sky.sun_start_px - Sky.sun_fully_set_px))
	(Sky.dusk_at_set * set_so_far) * set_so_far
}
```

```roc
## How far toward dusk the sky is once the sun has fully set, darkening on
## to full dusk as it sinks a further radius.
dusk_after_set : F64 -> F64
dusk_after_set = |height| {
	sunk_past_set = ((Sky.sun_fully_set_px - height) / Sky.sun_radius_px)
	DeviceMath.real_min(1.0, (Sky.dusk_at_set + (sunk_past_set * (1.0 - Sky.dusk_at_set))))
}
```

The horizon's warmth is a third shape, a tent centred on the moment the sun touches the horizon. Three curves come off one number, and they're plain functions rather than anything more general. Nothing else in the game needs them.

```roc
## How warm the horizon is at `clock`: most while the sun touches it, none
## once the sun is `warmth_falloff_px` above or below.
sunset_warmth : F64 -> F64
sunset_warmth = |clock| DeviceMath.real_max(
	0.0,
	(1.0 - (DeviceMath.real_abs(sun_height_px(clock)) / warmth_falloff_px)),
)
```

### Angles that can't be mixed up

The sun is the one thing here that also depends on where the rider is looking. Two tags say the two answers, so there's no `null` and no off-screen sentinel value. A caller has to handle `OutOfView`, because `match` must cover every tag.

```roc
## The sun in a frame: in view at its place, or out of view, too far to
## the side of where the rider faces.
SunPos : [InView(Sky.SunPlace), OutOfView]
```

Opaque types do the most work in this next function. `Angle.Bearing` is a direction in the world and `Angle.Turn` is a change of direction. Both are floats underneath, but they're opaque types (`::`), so only the `Angle` module can build or open one, and a `Turn` can't be passed where a `Bearing` is wanted. `sun_bearing.turn_from(heading)` is static dispatch: the method comes from the type of `sun_bearing`, with no import needed at the call. The function also takes one record argument, destructured in its parameter list, so callers name every field.

```roc
## The sun in a frame, for a rider facing `heading`.
sun_pos : {
	heading : Angle.Bearing,
	clock : F64,
	view : Camera.View,
} -> Sky.SunPos
sun_pos = |
	{
		heading,
		clock,
		view,
	},
| {
	turn_from_view = sun_bearing.turn_from(heading)
	if turn_from_view.abs() >= visible_turn_limit {
		OutOfView
	} else {
		InView(
			sun_place({
				turn_from_view,
				clock,
				view,
			}),
		)
	}
}
```

`turn_from_view.abs() >= visible_turn_limit` compares two `Turn`s. The code never touches radians until `sun_place` has to do trigonometry.

## The cat

The cat is the best scene in Safari Ride. It walks out, freezes in the lane as the rider bears down on it, and leaps clear at the last moment.

*[The cat widget goes here: drag the rider's gap and watch the crossing play.]*

The slider isn't scrubbing a video. Every position of it is a call to this function. The arrow is `->` again, so the type already says there's no hidden cat being updated somewhere. Method syntax chains the two halves of the job: `.moment(...)` is defined on the `Timeline` that `crossing_timeline` returns.

```roc
## The cat as the rider comes on it.
moment_at : Cat.Crossing, Animation.Approach -> Animation.Moment(Cat.Pose)
moment_at = |cat, approach| crossing_timeline(cat).moment(crossing_stage(approach))
```

A crossing and an approach go in, and a moment comes out. The same crossing at the same approach gives the same cat, a thousand frames apart. `crossing_stage` decides how far along things are, and `crossing_timeline` decides what that looks like. They know nothing of each other.

### When it plays

`Approach` is a plain record alias. Its `speed` field isn't a plain number, though. Like `Angle`, `Speed` is an opaque type.

```roc
## How the rider comes on a thing: the gap from the rider ahead to it, in
## metres, and the rider's speed.
Approach : { gap : F64, speed : Speed }
```

`Speed` wraps an `F64`, and its methods live in a block after the type. `Speed.(s)` in a parameter list is how the module opens one. Outside this module, nothing can, so a distance can't be passed as a speed.

```roc
## How many metres this speed covers in `steps` steps.
distance_in : Speed, F64 -> F64
distance_in = |Speed.(s), steps| s * steps
```

`Speed` also defines `is_lte`, which is what lets `speed <= standstill` work in the next snippet with an ordinary operator.

The stage is a tag union where two of the tags carry a payload. `Waiting` and `Past` aren't progress of 0 and 1, because a critter can rest somewhere no part of its animation reaches.

```roc
## Where an animation has got to: not begun, playing and this far through,
## from 0 to 1, or over, with the rider this many metres beyond its end.
Stage : [
	Waiting,
	Playing(F64),
	Past(F64),
]
```

```roc
## Where the crossing has got to. A cat has to finish before the rider
## reaches it however fast the rider comes, so it plays over steps.
crossing_stage : Animation.Approach -> Animation.Stage
crossing_stage = |approach|
	Animation.over_steps({ steps: cross_frames, buffer: road_buffer }, approach)
```

The rule lives in `Animation`. Its first argument is destructured in place, and so is the `Approach` after it, so the body reads in plain names.

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

The cat plays over steps rather than over a stretch of road because it has to finish before the rider reaches it, however fast the rider comes. A faster rider makes it start earlier. The bird uses `over_gap`, because a bird simply reacts to how close the rider is. Each critter picks the rule that suits it.

### What it looks like

A timeline is data, so the cat's whole performance reads in one place, like a score. Tags with payloads do almost everything here: `Through` and `Before` say where a stretch ends, `Holds` and `Alternates` say how the cat looks, and `Line`, `StaysAt` and `Arc` say where it goes. `Animation.Timeline.( ... )` wraps a record in the nominal type `Timeline`. Nominal (`:=`) is the middle ground: unlike an alias it can carry methods, and unlike an opaque type anyone can build one, which is right for data that needs no guarding.

```roc
## The whole of a crossing: the cat walks out to the middle of the lane,
## freezes there, and leaps clear to the far verge. Each leap pose's cut
## sums to a float just under the step it stands for, so that float goes
## with the pose before it, which is why those cuts are `Through`.
crossing_timeline : Cat.Crossing -> Animation.Timeline(Cat.Pose)
crossing_timeline = |cat| {
	start = spot_across(cat.start_across)
	middle = spot_across(cat.mid_across)
	end = spot_across(cat.end_across)
	Animation.Timeline.(
		{
			steps: cross_frames,
			before: { pose: Rest, spot: start },
			after: { pose: Collapse, spot: end },
			looks: {
				stretches: [
					{
						until: Through(enters_road_steps),
						plays: Alternates({
							up: Stride,
							down: Rest,
							count: strides_in(enters_road_steps),
							over: enters_road_steps,
						}),
					},
					{ until: Through(escape_at), plays: Holds(Frozen) },
					{ until: Through(escape_at + coil_ends_steps), plays: Holds(Coil) },
					{ until: Through(escape_at + flight_ends_steps), plays: Holds(Flight) },
					{ until: Through(escape_at + land_ends_steps), plays: Holds(Land) },
				],
				finally: Holds(Collapse),
			},
			path: {
				stretches: [
					{
						until: Through(enters_road_steps),
						plays: Line({
							from: start,
							to: middle,
							ease: Steady,
						}),
					},
					{ until: Before(escape_at + leaves_ground_steps), plays: StaysAt(middle) },
					{
						until: Before(escape_at + touches_down_steps),
						plays: Arc({
							line: {
								from: middle,
								to: end,
								ease: ThreeQuarterPower,
							},
							rise: leap_height,
						}),
					},
				],
				finally: StaysAt(end),
			},
		},
	)
}
```

There are two tracks because a cat's looks and its movement change at different moments. Its body moves just ahead of its path, so the `looks` track cuts at 0.8, 2.8 and 3.8 steps into the escape while the `path` track cuts at 1 and 3. One list of phases tying them together wouldn't fit the cat or the bird.

`Timeline(pose)` takes a type parameter, which is how a cat and a bird share it. A cat's pose is a closed tag union, and nothing outside `Cat` needs to know its tags. Because it's closed, a `match` on it that misses a pose won't compile.

```roc
## How the cat holds itself: walking, it is at rest or mid-stride; then
## frozen; then its leap, from the coil through flight and landing to the
## collapse after.
Pose : [Rest, Stride, Frozen, Coil, Flight, Land, Collapse]
```

A cut has to say which side of it its own step falls on, and two tags say that better than a boolean would. `crossing_timeline`'s comment says why it matters: those leap steps sum to a float just under the step they stand for.

```roc
## Where a stretch ends, in steps from the timeline's start: the cut's own
## step belongs to the stretch that ends `Through` it, and to the next one
## after a stretch that ends `Before` it.
Cut : [Through(F64), Before(F64)]
```

Finding the stretch that's playing shows one more Roc idea. `var $from` is a local variable that a `for` loop reassigns, inside a pure function. Roc allows that because nothing outside can see it: `playing_at` still has a `->` arrow, and the `$` marks what changes. An early `return` ends the loop.

```roc
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
```

### What it does to the rider

So far the cat hasn't touched the rider. That's a separate question, answered in one place. `..others` in the argument's type makes it an open record: this function needs `along` and `speed`, and accepts any record that has them, so it doesn't depend on `Pose.RiderState`. `speed` here is the opaque `Speed` again, and `match` on `segment.crossing` has to name every tag.

```roc
## The reaction to `segment`'s crossing of a rider on that segment.
reaction_to : World.Segment,
{
	along : F64,
	speed : Speed,
	..others,
} -> CrossingReaction.Reaction
reaction_to = |segment, rider|
	match segment.crossing {
		CatCrosses(crossing) => {
			approach = { gap: crossing.along - rider.along, speed: rider.speed }
			{
				throttle: if (Cat.is_in_danger(approach)) NoAcceleration else MayAccelerate,
				eye_pull: Cat.focus(approach),
			}
		}
		BirdFlies(_) | QuietRoad => { throttle: MayAccelerate, eye_pull: 0.0 }
	}
```

A cat in the lane stops the rider opening the throttle, without braking, and widens the view as it pulls the rider's eye. Two tags, `MayAccelerate` and `NoAcceleration`, stand where a boolean might have gone, so the call site reads as a sentence.

This is the only loop in the design. The rider's speed decides where the cat has got to, and the cat holds the rider's speed down. It settles, and it's also why `over_steps` has to stay the cat's rule. A bird asks nothing of the rider, so it falls through to the same answer as an empty road.

Each stretch of road has exactly one `crossing`: `CatCrosses`, `BirdFlies` or `QuietRoad`. A cat and a bird in the same place can't be written down.

### Getting it on screen

The last step is finding the cat in the rider's view. `CatPlan` asks for the moment, places it, and decides whether it's big enough to draw. An empty list or a list of one is how it says "maybe", because the caller flattens them with `join_map`.

```roc
## The cat crossing the segment at `position` in the chain, as far through its
## crossing as the rider's approach has brought it, if it is in view: one
## item, or none.
cat_in_view : CatPlan.View,
{
	position : Frame.ChainPosition,
	crossing : Cat.Crossing,
} -> List(CatPlan.CatItem)
cat_in_view = |view, { position, crossing }| {
	gap = CatPlan.gap_to_segment(view, position)
	moment = Cat.moment_at(crossing, { gap: (gap + crossing.along), speed: view.speed })
	seen = Frame.rider_point_ahead(
		{
			world: view.world,
			chain: view.chain,
			pose: view.pose,
		},
		{
			position: position,
			along: (crossing.along + moment.spot.along),
			across: (moment.spot.across + (Scenery.lane_width / 2.0)),
		},
	)
	if seen.forward <= Geom.near_plane {
		[]
	} else if ((crossing.height / seen.forward) * view.cam_focal) < SceneLimits.min_scenery_px {
		[]
	} else {
		[
			{
				right: seen.right,
				forward: seen.forward,
				height: crossing.height,
				pose: moment.pose,
				lift: moment.spot.lift,
			},
		]
	}
}
```

A plan decides how a thing looks, and drawing only paints it. That rule runs through all of Safari Ride.

Notice what isn't in this chapter: a cat in `Ride`, an update loop, or a flag saying the cat has already crossed. Roc doesn't force that, but pure functions make the stateless version the easy one to write, and every `->` shows it stayed that way.

## Credits

Safari Ride was designed by Steve Howell. Claude wrote most of the code and this tutorial under his direction.
