# Review: roc-apps `canvas_apps/safari/BirdFlight.roc`

180 lines in 7 chunks, as of commit 67d08a6 safari: the bird flies on an Animation timeline. Reply under any chunk; this paragraph is for the file as a whole.

```roc
## Where a Roc bird is and how it looks. A bird sits on the fifth tree on the
## left of a segment until the rider comes near, then flies diagonally ahead,
## across the road, to the next tree on the far side, and perches there. Where
## it is depends only on how far the rider is from the tree it left, as the
## cat's crossing does, so stepping back through a ride shows the same bird.
## A bird's spots are places on its segment, as its trees' are, because its
## flight is its own and no other bird shares it.
import Animation
import Scenery

BirdFlight :: [].{

	## The tree a bird leaves, and the one it flies to.
	Flight : { from : Scenery.Tree, to : Scenery.Tree }

	## What a segment's bird does: flies from one tree to another, or sits,
	## when there's no tree to fly to.
	Route : [Flies(BirdFlight.Flight), Sits(Scenery.Tree)]

	## Where the wings are in a beat.
	WingBeat : [WingsUp, WingsDown]
```

**Lines 1–21**: `BirdFlight`, `Flight`, `Route`, `WingBeat`

```roc
	## How the bird looks: sitting; side on as it takes off; seen from behind
	## as it flies off; and dropping onto its tree.
	Pose : [
		Perched,
		Side(BirdFlight.WingBeat),
		Away(BirdFlight.WingBeat),
		Diving,
	]

	## How far the rider is from the bird's tree when it takes off.
	takeoff_gap : F64
	takeoff_gap = 60.0

	## How far the rider is from that tree when the bird has landed.
	landing_gap : F64
	landing_gap = 15.0

	## The bird flies to a tree at least this far along from the one it left,
	## so that its path runs ahead of the rider as well as across the road.
	shortest_hop : F64
	shortest_hop = 25.0

	## How far above a straight line the top of its path is, in metres.
	flight_arc : F64
	flight_arc = 5.0
```

**Lines 23–47**: `Pose`, `takeoff_gap`, `landing_gap`, `shortest_hop`, `flight_arc`

```roc
	## How many times the wings beat in a flight.
	wing_beats : F64
	wing_beats = 9.0

	## The share of a flight spent side on, taking off.
	takeoff_share : F64
	takeoff_share = 0.12

	## The share of a flight spent dropping to land.
	landing_share : F64
	landing_share = 0.12

	## The tree a bird starts on, the fifth with a negative `across`. Those are
	## on the left, and an unflipped still's beak points toward +x, so from
	## there the bird faces the road.
	fifth_left_tree : List(Scenery.Tree) -> [Found(Scenery.Tree), NoTree]
	fifth_left_tree = |trees|
		match trees.keep_if(|tree| tree.across < 0.0).drop_first(4).first() {
			Ok(tree) => Found(tree)
			Err(ListWasEmpty) => NoTree
		}
```

**Lines 49–69**: `wing_beats`, `takeoff_share`, `landing_share`, `fifth_left_tree`

```roc
	## The route of a bird on the tree at `from`: to the first tree on the
	## other side of the road far enough along, or none, and it sits.
	route_from : List(Scenery.Tree), Scenery.Tree -> BirdFlight.Route
	route_from = |trees, from| {
		is_far_enough = |tree| tree.along >= from.along + shortest_hop
		far_side = trees.keep_if(|tree| tree.across > 0.0 and is_far_enough(tree))
		match far_side.first() {
			Ok(to) => Flies({ from, to })
			Err(ListWasEmpty) => Sits(from)
		}
	}

	## The bird of a segment with `trees`, if one has a tree to start on.
	crossing_among : List(Scenery.Tree) -> [BirdFlies(BirdFlight.Route), QuietRoad]
	crossing_among = |trees|
		match fifth_left_tree(trees) {
			Found(tree) => BirdFlies(route_from(trees, tree))
			NoTree => QuietRoad
		}

	## Where the tree the bird starts from is along its segment.
	start_along : BirdFlight.Route -> F64
	start_along = |route|
		match route {
			Flies(flight) => flight.from.along
			Sits(tree) => tree.along
		}
```

**Lines 71–97**: `route_from`, `crossing_among`, `start_along`

```roc
	## Where the bird's flight has got to, with the rider `gap` metres from the
	## tree it left.
	flight_stage : F64 -> Animation.Stage
	flight_stage = |gap| Animation.over_gap({ starts_at: takeoff_gap, ends_at: landing_gap }, gap)

	## The bird on `route` with the rider `gap` metres from the tree it starts on.
	state_on : BirdFlight.Route, F64 -> Animation.Moment(BirdFlight.Pose)
	state_on = |route, gap|
		match route {
			Flies(flight) => state(flight, gap)
			Sits(tree) => sitting_on(tree)
		}

	## The bird with the rider `gap` metres from the tree it left.
	state : BirdFlight.Flight, F64 -> Animation.Moment(BirdFlight.Pose)
	state = |flight, gap| flight_timeline(flight).moment(flight_stage(gap))

	## The bird as it sits on top of `tree`.
	sitting_on : Scenery.Tree -> Animation.Moment(BirdFlight.Pose)
	sitting_on = |tree| { pose: Perched, spot: tree_top(tree) }

	## A flight's timeline is one step long, so a cut on it is a share of the
	## flight.
	whole_flight : F64
	whole_flight = 1.0
```

**Lines 99–123**: `flight_stage`, `state_on`, `state`, `sitting_on`, `whole_flight`

```roc
	## The whole of a flight: side on as it takes off, then seen from behind,
	## beating its wings all the way until it dives, on one smooth path that
	## rises in the middle.
	flight_timeline : BirdFlight.Flight -> Animation.Timeline(BirdFlight.Pose)
	flight_timeline = |{ from, to }|
		Animation.Timeline.(
			{
				steps: whole_flight,
				before: sitting_on(from),
				after: sitting_on(to),
				looks: {
					stretches: [
						{
							until: Before(takeoff_share),
							plays: wings_beating({ up: Side(WingsUp), down: Side(WingsDown) }),
						},
						{
							until: Through(1.0 - landing_share),
							plays: wings_beating({ up: Away(WingsUp), down: Away(WingsDown) }),
						},
					],
					finally: Holds(Diving),
				},
				path: {
					stretches: [],
					finally: Arc({
						line: {
							from: tree_top(from),
							to: tree_top(to),
							ease: Smooth,
						},
						rise: flight_arc,
					}),
				},
			},
		)
}
```

**Lines 125–161**: `flight_timeline`

```roc
## The spot on top of `tree`.
tree_top : Scenery.Tree -> Animation.Spot
tree_top = |tree| {
	along: tree.along,
	across: tree.across,
	lift: tree.height,
}

## A bird that shows `up` and `down` in turn, as its wings beat through the
## flight.
wings_beating : { up : BirdFlight.Pose, down : BirdFlight.Pose } -> Animation.Looks(BirdFlight.Pose)
wings_beating = |{ up, down }|
	Alternates({
		up,
		down,
		count: BirdFlight.wing_beats,
		over: BirdFlight.whole_flight,
	})
```

**Lines 163–180**: `tree_top`, `wings_beating`

