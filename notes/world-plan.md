# World's plan

World.roc is 917 lines: the route plan, the segment type and its build, questions asked of one segment, and route-wide arithmetic, all in one empty `World :: [].{` namespace. The World review (on roc-apps master dc0648cc) turned up a set of findings that only make sense together. Most are clear calls I've made. Two are yours: the `Route` type, and the word "crossing". Nothing is built yet. This lane runs after the spot lane, because both reach nearly every module.

## What I've decided

**Split World in two.**
- `World.roc` keeps the plan: `SegmentPlan`, the plans, the herd shapes and counts, and the resolving of each segment's route-level choices (big herd or two rows, distracting or not).
- `Segment.roc` holds `Segment`, its build and the questions asked of it. The build takes resolved choices, so Segment never imports World. Where a cat or a bird starts goes there too (`nearest_tree_ahead`, `cat_along`, `fifth_left_tree`), along with where a herd stands.
- The 235 lines of herd-layout expects move to PigHerd and CowHerd, with fixture herds of their own.

**The segment stops storing what it can work out.**

```roc
# before
exit_turn : Angle.Turn, commit_along : Along, mid_tower : [MidTower, NoMidTower],
ending : [Continues({ next : World.SegmentIndex }), Terminates],
bend_life : Scenery.BendLife,
# after
ending : [Bends({ turn : Angle.Turn, bend_life : BendLife }), RouteEnds],
commit_along : Segment -> Along      # Geom.commit_along, or the end of a RouteEnds
has_mid_tower : Segment -> Bool
```

The last segment carries a planned 0° turn that every reader matches past, and its planned bend life is overridden to `Quiet`. Once the bend lives inside `Bends`, the route's end has no bend to fake. `next` is always the segment's own index plus one, so it becomes `index.next()` where it's used. That also breaks the one import cycle the split would have.

On making the last segment `Continues`: the reviewer recommends against it, and I agree. Its `next` would name a segment that doesn't exist, and the rider would stop stopping. The route really does end. What was wrong is that the end carried bend data.

**A wrong pig state goes.** Today `{ pig_herd: NoPigs, pig_interest: Distracting }` can be written, and Gaze handles it quietly.

```roc
# after
PigHerd := [BigHerd(..), TwoRows(..)]                                     # no NoPigs: absence is the route's
pigs : [NoPigs, Herd({ herd : PigHerd, interest : PigInterest })]         # on the segment
standout_pig : PigHerd, Along -> Geom.Placed(Billboard)                    # always one
```

**Names:**
- `World.segments` becomes `route_segments`, the style guide's own example.
- `plans` becomes `segment_plans`.
- `World.standout_pig` becomes `segment_standout_pig`.
- The fixture-only `route_segment(n)` goes.

The expects that restate constants go too.

## Yours: a `Route` type

`List(World.Segment)` appears in about 40 signatures, always as `route_segments`. It's a bare type hiding "the route". And it lets fixtures write a route that can't exist: `[World.route_segment(0)]` alone is a segment that says `Continues(next: 1)` past its own end, and a mid-route plan can say `Terminates`.

```roc
Route :: List(Segment).{ segment_at, route_length, distance_along_route, indices_ahead }
```

The route is built from the plans, and whether a segment ends the route comes from its position, as the last one. `ending` leaves `SegmentPlan`, and with it the last plan's dead turn.

- **For:** one home for "the last segment" and "the next index", and an index can't go wrong.
- **Against:** it's wide. Everything that holds the route moves, and every fixture moves onto a builder.

It also settles a RoadAhead redundancy: `segments_ahead : List(SegmentIndex)` is always a consecutive run from the rider's index, so it restates a start and a count.

I recommend building it in the same lane as the split. The split moves every one of those signatures anyway.

## Yours: the word "crossing"

The segment's `crossing` slot holds a cat, a bird or nothing. A perched bird that sits crosses nothing, yet lives there. "Crossing" also means the cat's path (`Cat.Crossing`, soon `CatCrossing`) and the cat's act in time (`crossing_stage`, `crossing_steps`). With the decided `CatCrossing` type, the slot would read `CatCrosses(CatCrossing)`.

Keep "crossing" for the cat's path and act, and give the slot a word for what it holds. The reviewer offers `crosser : [Cat(CatCrossing), Bird(Habit), QuietRoad]`. Others would be `visitor` or `encounter`. I'd take `encounter`: it's what the rider has there, "one experience at a time", as the slot's own comment says. CrossingSighting and CrossingReaction would then become EncounterSighting and EncounterReaction. Your word.

## Smaller questions for you

- **`big_herd_count` and `pig_novelty_count` are both 2.** Is that one rule ("the first herds are new, so they're big and catch the eye") or two choices that happen to agree?
- **`mid_tower_min_length` (1000 m)** lets only segment 6 (1200 m) through. Is it a rule of the world, or a way to pick that segment?
- **Both herds' standout pigs land at +2 m**, only because -6 + 2 × 4 = 2. If the standout's place is what matters to Gaze, the herds should be laid out from it.
