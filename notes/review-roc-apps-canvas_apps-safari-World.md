# Review: roc-apps `canvas_apps/safari/World.roc`

387 lines in 14 chunks, as of commit 4b40152 World.SegmentIndex: its doc claims only what holds. Reply under any chunk; this paragraph is for the file as a whole.

```roc
## The ride's world: the route, a line of road segments, each built once from
## its entry in `route`. A segment holds its scenery (trees, cows, pigs, a cat
## by a tree), how it turns into the next, where the rider commits to that
## turn, and the creature waiting at its end.
import Cat
import lib.DeviceMath
import Geom
import Herd
import Pigs
import Scenery
import Trees
import lib.Trig
```

**Lines 1–12**

```roc
World :: [].{

	## A segment's place in the route, counted from 0. It says where a segment
	## is in the route, where a Frame.ChainPosition says how far ahead of the
	## rider it is.
	SegmentIndex :: U32.{

		number : U32 -> World.SegmentIndex
		number = |n| World.SegmentIndex.(n)

		to_i64 : World.SegmentIndex -> I64
		to_i64 = |World.SegmentIndex.(n)| n.to_i64()

		## The route's first segment.
		first : World.SegmentIndex
		first = World.SegmentIndex.(0)

		next : World.SegmentIndex -> World.SegmentIndex
		next = |World.SegmentIndex.(n)| World.SegmentIndex.(n + 1)

		## The segment before this one, unless this is the first.
		previous : World.SegmentIndex -> [Previous(World.SegmentIndex), AtRouteStart]
		previous = |World.SegmentIndex.(n)|
			if n == 0 {
				AtRouteStart
			} else {
				Previous(World.SegmentIndex.(n - 1))
			}

		## How many segments come before this one.
		count_before : World.SegmentIndex -> U64
		count_before = |World.SegmentIndex.(n)| n.to_u64()

		## The segment of `world` at this index.
		segment_in : World.SegmentIndex, List(World.Segment) -> World.Segment
		segment_in = |index, world|
			world.get(index.count_before())
				?? crash "World.SegmentIndex.segment_in: the world has no segment there"

		is_eq : _
	}
```

**Lines 14–54**: `World`, `SegmentIndex`

```roc
	## One segment of the route as planned: its length and scenery, its turn
	## into the next in degrees (right is positive), what lives along it, and
	## the creature at its end.
	SegmentPlan : {
		length : F64,
		scheme : Scenery.Scheme,
		turn_degrees : F64,
		cat : [WithCat, NoCat],
		pigs : Pigs.PigPresence,
		bull : [WithBull, NoBull],
		ending : [Continues, Terminates],
		creature : Scenery.Creature,
	}

	## One segment of road, built from its plan.
	Segment : {
		length : F64,
		trees : List(Scenery.Tree),
		cows : List(Scenery.Critter),
		pigs : List(Scenery.Critter),
		pig_attention : Pigs.PigAttention,
		exit_angle : F64,
		exit_side : Geom.TurnSide,
		commit_along : F64,
		mid_tower : [MidTower, NoMidTower],
		cat : [Waits(Cat.Crossing), NoCat],
		ending : [Continues({ next : World.SegmentIndex }), Terminates],
		exit_creature : Scenery.Creature,
	}

	## A segment longer than this has a mast halfway along.
	mid_tower_min_length : F64
	mid_tower_min_length = 1000.0
```

**Lines 56–88**: `SegmentPlan`, `Segment`, `mid_tower_min_length`

```roc
	route : List(World.SegmentPlan)
	route = [
		{
			length: 500.0,
			scheme: AllGreen,
			turn_degrees: 50.0,
			cat: NoCat,
			pigs: NoPigs,
			bull: NoBull,
			ending: Continues,
			creature: Elephant,
		},
		{
			length: 320.0,
			scheme: AllGreen,
			turn_degrees: -70.0,
			cat: WithCat,
			pigs: NoPigs,
			bull: NoBull,
			ending: Continues,
			creature: Elephant,
		},
		{
			length: 400.0,
			scheme: AllGreen,
			turn_degrees: 20.0,
			cat: NoCat,
			pigs: WithPigs,
			bull: NoBull,
			ending: Continues,
			creature: Elephant,
		},
		{
			length: 300.0,
			scheme: YellowGreen,
			turn_degrees: 20.0,
			cat: NoCat,
			pigs: NoPigs,
			bull: NoBull,
			ending: Continues,
			creature: Elephant,
		},
```

**Lines 90–131**: `route` (part 1 of 7)

```roc
		{
			length: 300.0,
			scheme: AllGreen,
			turn_degrees: -70.0,
			cat: NoCat,
			pigs: NoPigs,
			bull: WithBull,
			ending: Continues,
			creature: Giraffe,
		},
		{
			length: 300.0,
			scheme: AllGreen,
			turn_degrees: -70.0,
			cat: NoCat,
			pigs: NoPigs,
			bull: WithBull,
			ending: Continues,
			creature: Elephant,
		},
```

**Lines 132–151**: `route` (part 2 of 7)

```roc
		{
			length: 1200.0,
			scheme: RedGreen,
			turn_degrees: 80.0,
			cat: NoCat,
			pigs: NoPigs,
			bull: WithBull,
			ending: Continues,
			creature: Rhino,
		},
		{
			length: 300.0,
			scheme: AllGreen,
			turn_degrees: 15.0,
			cat: NoCat,
			pigs: NoPigs,
			bull: WithBull,
			ending: Continues,
			creature: Elephant,
		},
		{
			length: 300.0,
			scheme: AllGreen,
			turn_degrees: -70.0,
			cat: NoCat,
			pigs: NoPigs,
			bull: WithBull,
			ending: Continues,
			creature: Elephant,
		},
```

**Lines 152–181**: `route` (part 3 of 7)

```roc
		{
			length: 800.0,
			scheme: AllGreen,
			turn_degrees: 15.0,
			cat: NoCat,
			pigs: NoPigs,
			bull: WithBull,
			ending: Continues,
			creature: Elephant,
		},
		{
			length: 300.0,
			scheme: AllGreen,
			turn_degrees: 15.0,
			cat: NoCat,
			pigs: WithPigs,
			bull: WithBull,
			ending: Continues,
			creature: Elephant,
		},
```

**Lines 182–201**: `route` (part 4 of 7)

```roc
		{
			length: 300.0,
			scheme: AllGreen,
			turn_degrees: 15.0,
			cat: NoCat,
			pigs: WithPigs,
			bull: WithBull,
			ending: Continues,
			creature: Elephant,
		},
		{
			length: 300.0,
			scheme: RedGreen,
			turn_degrees: 15.0,
			cat: WithCat,
			pigs: WithPigs,
			bull: WithBull,
			ending: Continues,
			creature: DuckPond,
		},
		{
			length: 400.0,
			scheme: AllGreen,
			turn_degrees: -50.0,
			cat: NoCat,
			pigs: WithPigs,
			bull: WithBull,
			ending: Continues,
			creature: Elephant,
		},
```

**Lines 202–231**: `route` (part 5 of 7)

```roc
		{
			length: 300.0,
			scheme: AllGreen,
			turn_degrees: 50.0,
			cat: NoCat,
			pigs: WithPigs,
			bull: WithBull,
			ending: Continues,
			creature: Elephant,
		},
		{
			length: 300.0,
			scheme: RedGreen,
			turn_degrees: -50.0,
			cat: NoCat,
			pigs: NoPigs,
			bull: WithBull,
			ending: Continues,
			creature: Zebra,
		},
		{
			length: 300.0,
			scheme: AllGreen,
			turn_degrees: 50.0,
			cat: NoCat,
			pigs: WithPigs,
			bull: WithBull,
			ending: Continues,
			creature: Elephant,
		},
```

**Lines 232–261**: `route` (part 6 of 7)

```roc
		{
			length: 300.0,
			scheme: AllGreen,
			turn_degrees: -50.0,
			cat: NoCat,
			pigs: WithPigs,
			bull: WithBull,
			ending: Continues,
			creature: Elephant,
		},
		{
			length: 300.0,
			scheme: RedGreen,
			turn_degrees: 0.0,
			cat: WithCat,
			pigs: WithPigs,
			bull: WithBull,
			ending: Terminates,
			creature: NoCreature,
		},
	]
```

**Lines 262–282**: `route` (part 7 of 7)

```roc
	## How many of the segments up to and including `index` have pigs.
	pig_segments_through : World.SegmentIndex -> U32
	pig_segments_through = |index|
		route
			.take_first(index.count_before() + 1)
			.count_if(|plan| Pigs.has_pigs(plan.pigs))
			.to_u32_wrap()

	## Segment `number` of the route, counting from 0.
	route_segment : U32 -> World.Segment
	route_segment = |number| {
		index = World.SegmentIndex.number(number)
		plan = route.get(index.count_before())
			?? crash "World.route_segment: the route has no segment there"
		built_segment(plan, index)
	}

	## Every segment of the route, in order.
	segments : List(World.Segment)
	segments = route.map_with_index(
		|plan, at| built_segment(plan, World.SegmentIndex.number(at.to_u32_wrap())),
	)

	## The segments' length, end to end. It is summed from the last segment to
	## the first: a float sum's rounding depends on its order, and another
	## order can move a pixel.
	route_length : List(World.Segment) -> F64
	route_length = |world| world.fold_rev(0.0, |segment, sum| segment.length + sum)

	## How far along the route a point `along` into the segment at `index` is.
	distance_along_route : List(World.Segment), { index : World.SegmentIndex, along : F64 } -> F64
	distance_along_route = |world, { index, along }|
		route_length(world.take_first(index.count_before())) + along
}
```

**Lines 284–317**: `pig_segments_through`, `route_segment`, `segments`, `route_length`, `distance_along_route`

```roc
## The segment at `index` of the route, built from its plan.
built_segment : World.SegmentPlan, World.SegmentIndex -> World.Segment
built_segment = |plan, index| {
	exit_angle = DeviceMath.real_abs(plan.turn_degrees) * Trig.deg
	trees = Trees.plant({ scheme: plan.scheme, length: plan.length })
	pig_attention = Pigs.attention_of({
		presence: plan.pigs,
		pig_segments_so_far: World.pig_segments_through(index),
	})
	{
		length: plan.length,
		trees,
		cows: Herd.fill_cows(plan.bull),
		pigs: Pigs.pigs_along({
			presence: plan.pigs,
			attention: pig_attention,
			length: plan.length,
		}),
		pig_attention,
		exit_angle,
		exit_side: if (plan.turn_degrees >= 0.0) TurnsRight else TurnsLeft,
		commit_along: match plan.ending {
			Continues => plan.length - Scenery.lane_width / 2.0 / Trig.r_tan(exit_angle)
```

**Lines 319–341**: `built_segment` (part 1 of 2)

```roc
			Terminates => plan.length
		},
		mid_tower: if (plan.length > World.mid_tower_min_length) MidTower else NoMidTower,
		cat: match plan.cat {
			WithCat => Waits(
				Cat.crossing({
					lane_half_width: (Scenery.lane_width / 2.0),
					tree_offset: Trees.tree_road_offset,
					tree_along: nearest_tree_ahead(trees, Cat.cat_along),
				}),
			)
			NoCat => NoCat
		},
		ending: match plan.ending {
			Continues => Continues({ next: index.next() })
			Terminates => Terminates
		},
		exit_creature: match plan.ending {
			Continues => plan.creature
			Terminates => NoCreature
		},
	}
}
```

**Lines 342–364**: `built_segment` (part 2 of 2)

```roc
## The nearest tree along the road at or past `along`, on the right; `along`
## itself when there is none. A segment's cat waits by it.
nearest_tree_ahead : List(Scenery.Tree), F64 -> F64
nearest_tree_ahead = |trees, along| {
	nearest = trees.fold(
		NoTreeYet,
		|best, tree|
			if tree.across > 0.0 and tree.along >= along {
				match best {
					NearestAlong(nearest_along) =>
						if (tree.along < nearest_along) NearestAlong(tree.along) else best
					NoTreeYet => NearestAlong(tree.along)
				}
			} else {
				best
			},
	)
	match nearest {
		NearestAlong(nearest_along) => nearest_along
		NoTreeYet => along
	}
}
```

**Lines 366–387**: `nearest_tree_ahead`

