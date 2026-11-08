# Open calls, round 5: the cat, the bird and the sky

**Answered (Steve, 2026-11-08):** all leans, as written. On #5: "Love the astronomy breakout idea! Such a great concept that's underneath the hood." On #6, the bird keeps its current facing: "We pass it by quickly enough that it wouldn't turn around in time for us to see it."

*2026-11-08. Three type audits came back: the cat, the bird, and the sky with its sun and mountains. I decided the clear findings, and three cleanup lanes are making them now, every pixel held. These seven are yours. Each has my lean; a word per item is plenty.*

1. **Empty namespaces beside the real type.** Three of them:
   - `Cat :: [].{ }` holds the crossing's timeline, while `CatCrossing` holds where it happens.
   - `BirdFlight :: [].{ }` holds everything about a `BirdFlight.Flight` record.
   - `Sky :: [].{ }` holds `Sky.Colors`, plus darkness and warmth.

   The bird already keeps when and where in one home; the cat splits them.

   *Lean:*
   - Fold `Cat` into `CatCrossing`, so the crossing owns its own timeline.
   - Make `BirdFlight` the nominal type itself.
   - Leave `Sky` as it is, since darkness and warmth aren't facts about a pair of colors.
   - Do the cat and the bird together, so the two animals stay parallel.

2. **Who owns the cat's pull on the rider's eye.** `Cat` holds `cat_attention`: how hard the rider's eye is held, how fast it rises, and how slowly it fades after the crossing. The fade is 83 steps, which only makes sense at the rider's pace. That's the rider's reaction living in the cat. It's the same mistake as the tower holding the beacon's brightness.

   *Lean:* the middle path.
   - The cat keeps one fact, its peak salience: how eye-catching a crossing cat is.
   - The rise and the fade move to `EncounterReaction`, the rider's side.
   - `Cat.is_crossing` goes, and the reaction matches the stage directly, as the bird's already does.

   Pixels hold.

3. **Rename `Mountains` to `Skyline`.** The module holds the rolling land too, and `FrameView` already calls its output `skyline_shapes`. `SkyColumn` would become `SkylineColumn`, which is part of the skyline, not of the sky.

   *Lean:* yes. The book's prose can still say "mountains" where it means the mountains.

4. **Darkness is measured from the ride's start.** The sky counts how dark it is as a share of the sun's drop since the first step, so day is "wherever the ride began". The alternative is a fixed `day_height`, above which the sky is full day.

   *Lean:* keep it. It's a plain choice for the story, and the alternative adds a tuned number.

5. **Split `Sun` by axis.** Its roughly 350 lines hold three things:
   - the astronomy, which is clock-driven: where the sun is at a step;
   - the projection: where it lands on screen;
   - the look: the disc and its glow.

   `Sky` uses only the astronomy.

   *Lean:* yes. A `SunPath` module would hold the astronomy, and `Sun` would keep the sighting and the drawing. Sky would be the astronomy's second user, which earns the split.

6. **A landed bird faces away from the road.** Every bird starts on a left-hand tree, unmirrored, so it faces the road. It then lands on a right-hand tree, still unmirrored, so it faces outward. Nothing in the code chose that.

   *Lean:* the next time you ride, glance at the landed bird. If it looks wrong, mirror it whenever it lands right of where it started. That would move pixels, so it would get an eye-test note with renders.

7. **One packing for "where an object stands".** `Animation.Location` is `{ along, across, lift }`, and `Geom.Placed` is `{ road_point: { along, across }, lift, kind }`. A conversion between them is written in Animation, and written again by hand in the bird widget.

   *Lean:* yes, with `Location : { road_point, lift }`. It touches the shared Animation module and both animals, so it goes after this round's three lanes have merged.
