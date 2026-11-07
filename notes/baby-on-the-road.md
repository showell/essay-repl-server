# Where the baby animal stands

A review of the scenery makers (Wildlife, Pond, Trees) found eight things. I decided seven of them; this one is yours.

## The facts

At a bend with an animal, Wildlife plants an adult beyond the guard rail and a baby whose doc says it stands "in the middle of the road a little past the bend".

It doesn't. The baby is placed 14 m past the segment's end, measured straight on along the segment before the bend. At a 50° turn, that point is about 10.7 m outside the next segment's road. So the baby stands dead ahead of the rider as they come up to the bend, in the middle of the view, but off the road they're about to take.

## The choice

- **(a) It's meant to be in the view.** Keep the place and fix the doc: "straight on past the bend, dead ahead of the rider as they come". No pixels move.
- **(b) It's meant to be on the road.** Place it on the next segment, in the middle of the road 14 m past the bend (`Geom.point_in_segment_before`). Every baby moves onto the road after the turn, so pixels move, and you'd eye-test it.

I lean to **(b)**, since "in the middle of the road" sounds like the intent, and a baby on the road the rider is about to take is the better picture. But it's how the scene looks, so it's your call.

## Decided without you, for the record

- Wildlife asks `BendView` which side is the outside of the bend, instead of working it out again. That's the guard rail's own rule, and the animal stands beyond the rail.
- **Pond mirrors on a left turn.** Today every pond point is on the right-turn side, which works only because the one pond sits at a right turn. A pond planted at a left turn would put water on the road.
- `Billboard.half_width` names the fact that a still is square. Wildlife and CowHerd each used half the height for it.
- Pond hands GroundSighting whole outlines, water first, rather than four constants to pair up. The bank's inner edge is the water's far shore, named once.
- Wildlife's helpers go private, and Trees' insets and the gold tree's ×4 are documented as chosen by eye.

## Steve's answer (2026-11-07)

**(a): the babies stay**, and the doc says where they actually are. "I don't remember my original intent, but dead ahead would probably feel unnatural."
