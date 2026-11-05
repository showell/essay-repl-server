# Review: roc-apps `canvas_apps/safari/CrossingReaction.roc`

30 lines in 1 chunks, as of commit 34d42e1 safari: CrossingReaction, one answer to what a crossing does to the rider. Reply under any chunk; this paragraph is for the file as a whole.

```roc
## What a segment's crossing does to the rider. The rider reacts only to the
## crossing on their own segment, though animations play along the chain ahead,
## and this is the one place that knows which crossings ask anything of them.
## A cat in the lane stops the rider opening the throttle, without braking, and
## draws their eye. A bird asks nothing. The pigs' gaze is no crossing, and is
## Gaze's.
import Cat
import Pose
import World

CrossingReaction :: [].{

	## What a crossing does to the rider now: whether they may open the
	## throttle, and how hard it holds their eye.
	Reaction : { throttle : [Free, Held], eye_pull : F64 }

	## The reaction to `segment`'s crossing of a rider on that segment.
	reaction_to : World.Segment, Pose.RiderState -> CrossingReaction.Reaction
	reaction_to = |segment, rider|
		match segment.crossing {
			CatCrosses(crossing) => {
				approach = { gap: crossing.along - rider.along, speed: rider.speed }
				{
					throttle: if (Cat.is_in_danger(approach)) Held else Free,
					eye_pull: Cat.focus(approach),
				}
			}
			BirdFlies(_) | QuietRoad => { throttle: Free, eye_pull: 0.0 }
		}
}
```

**Lines 1–30**: `CrossingReaction`, `Reaction`, `reaction_to`

