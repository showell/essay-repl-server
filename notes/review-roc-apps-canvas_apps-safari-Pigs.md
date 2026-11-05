# Review: roc-apps `canvas_apps/safari/Pigs.roc`

181 lines in 6 chunks, as of commit 6f2d10d safari: the pigs' rule moves from World to Pigs. Reply under any chunk; this paragraph is for the file as a whole.

```roc
## Pigs graze on the right of the road near the end of a segment. On the
## first few segments with pigs they are a big herd, and one of them catches
## the rider's eye; after that, they stand in two short rows.
import Scenery
import lib.Trig

Pigs :: [].{

	## Whether the route plans pigs along a segment.
	PigPresence : [WithPigs, NoPigs]

	## Whether a segment's pigs catch the rider's eye.
	PigAttention : [Distracting, Unnoticed]

	pig_codepoint : I64
	pig_codepoint = 128022

	pig_height : F64
	pig_height = 1.1

	## How many segments with pigs have the big herd.
	pig_novelty_count : U32
	pig_novelty_count = 2

	## How far before the end of its segment the pigs are.
	pig_dist_before_end : F64
	pig_dist_before_end = 60.0
```

**Lines 1–27**: `Pigs`, `PigPresence`, `PigAttention`, `pig_codepoint`, `pig_height`, `pig_novelty_count`, `pig_dist_before_end`

```roc
	## How far past that the pig that catches the rider's eye stands.
	gaze_pig_along_offset : F64
	gaze_pig_along_offset = 2.0

	big_herd_cols : I64
	big_herd_cols = 7

	big_herd_rows : I64
	big_herd_rows = 7

	## The distance between the big herd's columns, along the road.
	pig_col_spacing : F64
	pig_col_spacing = 4.0

	## The distance between rows of pigs, away from the road. Each row of the
	## big herd is also moved this far along the road.
	pig_row_depth : F64
	pig_row_depth = 6.0

	## How far a pig of the big herd strays from its place, along the road
	## and across it.
	pig_jitter_along : F64
	pig_jitter_along = 1.2

	pig_jitter_across : F64
	pig_jitter_across = 1.0

	## Where the big herd's first column is, along the road, from the pigs'
	## place.
	pig_herd_first_col : F64
	pig_herd_first_col = (0.0 - 6.0)
```

**Lines 29–59**: `gaze_pig_along_offset`, `big_herd_cols`, `big_herd_rows`, `pig_col_spacing`, `pig_row_depth`, `pig_jitter_along`, `pig_jitter_across`, `pig_herd_first_col`

```roc
	## How much farther from the road the back row stands than the front.
	pig_back_row_offset : F64
	pig_back_row_offset = 6.0

	## Where the pigs of the front and back rows are along the road, from the
	## pigs' place.
	pig_row_front : List(F64)
	pig_row_front = [
		(0.0 - 6.0),
		(0.0 - 2.0),
		2.0,
		6.0,
	]

	pig_row_back : List(F64)
	pig_row_back = [
		(0.0 - 10.0),
		(0.0 - 6.0),
		(0.0 - 2.0),
		2.0,
		6.0,
		10.0,
	]

	has_pigs : Pigs.PigPresence -> Bool
	has_pigs = |presence|
		match presence {
			WithPigs => True
			NoPigs => False
		}
```

**Lines 61–90**: `pig_back_row_offset`, `pig_row_front`, `pig_row_back`, `has_pigs`

```roc
	## How a segment's pigs strike the rider, when `pig_segments_so_far` of
	## the route's segments, this one included, have pigs.
	attention_of : { presence : Pigs.PigPresence, pig_segments_so_far : U32 } -> Pigs.PigAttention
	attention_of = |{ presence, pig_segments_so_far }|
		if has_pigs(presence) and pig_segments_so_far <= pig_novelty_count {
			Distracting
		} else {
			Unnoticed
		}

	## The pigs on a segment `length` metres long: a big herd where they catch
	## the rider's eye, and two rows elsewhere.
	pigs_along : {
		presence : Pigs.PigPresence,
		attention : Pigs.PigAttention,
		length : F64,
	} -> List(Scenery.Critter)
	pigs_along = |
		{
			presence,
			attention,
			length,
		},
	|
		match (presence, attention) {
			(WithPigs, Distracting) => fill_pig_herd(length)
			(WithPigs, Unnoticed) => fill_pig_row(length)
			(NoPigs, Distracting) | (NoPigs, Unnoticed) => []
		}
```

**Lines 92–120**: `attention_of`, `pigs_along`

```roc
	## The pig that catches the rider's eye, on a segment `length` metres
	## long.
	gaze_pig : F64 -> Scenery.Critter
	gaze_pig = |length|
		pig({
			along: ((length - pig_dist_before_end) + gaze_pig_along_offset),
			across: (road_edge + Scenery.herd_road_offset),
		})

	## The big herd on a segment `length` metres long, row by row from the
	## road.
	fill_pig_herd : F64 -> List(Scenery.Critter)
	fill_pig_herd = |length| {
		herd_along = (length - pig_dist_before_end)
		columns = List.from_iter(I64.until(0, big_herd_cols))
		List.from_iter(I64.until(0, big_herd_rows))
			.join_map(|row| columns.map(|column| herd_pig(herd_along, { row, column })))
	}

	## The two rows of pigs on a segment `length` metres long, front row first.
	fill_pig_row : F64 -> List(Scenery.Critter)
	fill_pig_row = |length| {
		herd_along = (length - pig_dist_before_end)
		edge = (road_edge + Scenery.herd_road_offset)
		List.concat(
			pig_row(herd_along, { across: edge, offsets: pig_row_front }),
			pig_row(herd_along, { across: (edge + pig_back_row_offset), offsets: pig_row_back }),
		)
	}
}
```

**Lines 122–151**: `gaze_pig`, `fill_pig_herd`, `fill_pig_row`

```roc
road_edge : F64
road_edge = (Scenery.lane_width / 2.0)

pig : { along : F64, across : F64 } -> Scenery.Critter
pig = |{ along, across }| {
	along,
	across,
	codepoint: Pigs.pig_codepoint,
	height: Pigs.pig_height,
	face_right: False,
}

herd_pig : F64, { row : I64, column : I64 } -> Scenery.Critter
herd_pig = |herd_along, { row, column }| {
	i = ((row * Pigs.big_herd_cols) + column).to_f64()
	fr = row.to_f64()
	fc = column.to_f64()
	first_column = (herd_along + Pigs.pig_herd_first_col)
	in_line = ((first_column + (fc * Pigs.pig_col_spacing)) + (fr * Pigs.pig_row_depth))
	in_row = ((road_edge + Scenery.herd_road_offset) + (fr * Pigs.pig_row_depth))
	pig({
		along: (in_line + (Pigs.pig_jitter_along * Trig.r_sin((i * 2.3)))),
		across: (in_row + (Pigs.pig_jitter_across * Trig.r_cos((i * 1.7)))),
	})
}

pig_row : F64, { across : F64, offsets : List(F64) } -> List(Scenery.Critter)
pig_row = |herd_along, { across, offsets }|
	offsets.map(|offset| pig({ along: (herd_along + offset), across }))
```

**Lines 153–181**: `road_edge`, `pig`, `herd_pig`, `pig_row`

