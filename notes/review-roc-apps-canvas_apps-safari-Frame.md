# Review: roc-apps `canvas_apps/safari/Frame.roc`

164 lines in 7 chunks, as of commit 2bd7b6a safari: a segment's index and a chain position are types of their own. Reply under any chunk; this paragraph is for the file as a whole.

```roc
## Frame finds where the road lies from where the rider is. The chain is the
## line of segments the rider can see, the rider's own first, and a point on
## any segment of it, or on the segment just behind the rider, is carried
## back round the bends between to the rider's own segment and into the
## rider's view.
import Geom
import Scenery
import World

Frame :: [].{

	Pose : Geom.Pose

	## The road in view: the world's segments, the chain of them ahead of
	## the rider, and the rider's pose.
	RoadView : {
		world : List(World.Segment),
		chain : List(World.SegmentIndex),
		pose : Frame.Pose,
	}
```

**Lines 1–20**: `Frame`, `Pose`, `RoadView`

```roc
	## A segment's place in the chain, counted from the rider's own at 0. It
	## says how many segments ahead of the rider that segment is, where a
	## World.SegmentIndex says where it is in the route.
	ChainPosition :: U32.{

		number : U32 -> Frame.ChainPosition
		number = |n| Frame.ChainPosition.(n)

		to_i64 : Frame.ChainPosition -> I64
		to_i64 = |Frame.ChainPosition.(n)| n.to_i64()

		## The rider's own segment.
		first : Frame.ChainPosition
		first = Frame.ChainPosition.(0)

		next : Frame.ChainPosition -> Frame.ChainPosition
		next = |Frame.ChainPosition.(n)| Frame.ChainPosition.(n + 1)

		## Every position in `chain`, the rider's own first.
		all_in : List(World.SegmentIndex) -> List(Frame.ChainPosition)
		all_in = |chain|
			List.from_iter(U32.until(0, chain.len().to_u32_wrap())).map(Frame.ChainPosition.number)
```

**Lines 22–43**: `ChainPosition` (part 1 of 2)

```roc
		## The segment at this position in `chain`.
		index_in : Frame.ChainPosition, List(World.SegmentIndex) -> World.SegmentIndex
		index_in = |Frame.ChainPosition.(n), chain|
			chain.get(n.to_u64()) ?? crash "Frame.ChainPosition.index_in: past the chain's end"

		## The segments of `chain` before this position, the rider's own first.
		before_in : Frame.ChainPosition, List(World.SegmentIndex) -> List(World.SegmentIndex)
		before_in = |Frame.ChainPosition.(n), chain| chain.take_first(n.to_u64())

		## Whether this position is the last one in `chain`.
		is_last_in : Frame.ChainPosition, List(World.SegmentIndex) -> Bool
		is_last_in = |Frame.ChainPosition.(n), chain| n.to_u64() + 1 >= chain.len()

		## Whether `chain` stops before this position.
		is_past_end_of : Frame.ChainPosition, List(World.SegmentIndex) -> Bool
		is_past_end_of = |Frame.ChainPosition.(n), chain| n.to_u64() >= chain.len()

		## Whether this position is among the first `count` of a chain.
		is_within_first : Frame.ChainPosition, U32 -> Bool
		is_within_first = |Frame.ChainPosition.(n), count| n < count

		is_eq : _
	}
```

**Lines 45–67**: `ChainPosition` (part 2 of 2)

```roc
	## Where a segment lies from the rider: at a position in the chain, or
	## just behind the rider, round the bend into the rider's segment.
	SegmentPlace : [InChain(Frame.ChainPosition), JustBehind(Geom.Bend)]

	## The most segments a chain holds.
	look_ahead : U32
	look_ahead = 7

	## The chain from the segment at `start`: as far as the rider can see, or
	## to the route's end.
	chain_ahead : List(World.Segment), World.SegmentIndex -> List(World.SegmentIndex)
	chain_ahead = |world, start| chain_onto(world, { index: start, chain: [] })

	## The bend at the end of `segment`.
	bend_out_of : World.Segment -> Geom.Bend
	bend_out_of = |segment| {
		segment_length: segment.length,
		turn_angle: segment.exit_angle,
		turn_side: segment.exit_side,
		lane_width: Scenery.lane_width,
	}

	## The place of `segment`, which is just behind the rider.
	place_behind : World.Segment -> Frame.SegmentPlace
	place_behind = |segment| JustBehind(bend_out_of(segment))
```

**Lines 69–93**: `SegmentPlace`, `look_ahead`, `chain_ahead`, `bend_out_of`, `place_behind`

```roc
	## A point on the segment at `position` in the chain, in the rider's view.
	rider_point_ahead : Frame.RoadView,
	{
		position : Frame.ChainPosition,
		along : F64,
		across : F64,
	} -> Geom.RiderPoint
	rider_point_ahead = |
		road,
		{
			position,
			along,
			across,
		},
	| {
		on_rider_segment = position.before_in(road.chain).fold_rev(
			{ along, across },
			|index, point| Geom.in_segment_before(point, bend_out_of(index.segment_in(road.world))),
		)
		Geom.to_rider_point(on_rider_segment, road.pose)
	}
```

**Lines 95–115**: `rider_point_ahead`

```roc
	## A point on the segment at `place`, in the rider's view.
	rider_point_at : Frame.RoadView,
	{
		place : Frame.SegmentPlace,
		along : F64,
		across : F64,
	} -> Geom.RiderPoint
	rider_point_at = |
		road,
		{
			place,
			along,
			across,
		},
	|
		match place {
			InChain(position) =>
				rider_point_ahead(
					road,
					{
						position,
						along,
						across,
					},
				)
			JustBehind(bend) =>
				Geom.to_rider_point(Geom.in_segment_after({ along, across }, bend), road.pose)
		}
}
```

**Lines 117–145**: `rider_point_at`

```roc
## `chain` with the segment at `index` and those after it added, up to the
## limit. An accumulator is linear, where appending a recursive call's answer
## is quadratic.
chain_onto : List(World.Segment),
{
	index : World.SegmentIndex,
	chain : List(World.SegmentIndex),
} -> List(World.SegmentIndex)
chain_onto = |world, { index, chain }|
	if chain.len() >= Frame.look_ahead.to_u64() {
		chain
	} else {
		longer_chain = chain.append(index)
		match index.segment_in(world).ending {
			Continues({ next }) => chain_onto(world, { index: next, chain: longer_chain })
			Terminates => longer_chain
		}
	}
```

**Lines 147–164**: `chain_onto`

