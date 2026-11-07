# Animation: what drives a frame

You decided that an animation is a list of frames landing on successive steps. The list part is done: `Cut`, `Stretch`, `Track` and `Alternates` are gone, and each critter's timeline is a plain list of poses and spots. The successive-steps part isn't done. Three reviews (cat, bird, Animation) agree on why.

## What happens now

Animation is stateless. Each step it asks only "how far is the rider from the critter, and how fast are they going?", and works the frame out from that.

```roc
Approach : { gap : Distance, speed : Speed }
Stage : [Waiting, Playing(Fraction), Past(Distance)]
```

**The bird plays by the road.** `stage_over_gap` maps the rider's progress from 60 m to 15 m onto the flight's 360 frames. A frame is an equal share of road, not a step.
- The wings beat faster when the rider rides faster.
- "Eight frames a metre" holds only because 360 = 40 × 9 flaps and the gap is 45 m. Change any of those and the claim fails silently.
- The bird's expects test tuned boundaries (0.1112, 0.8888).

**The cat estimates the steps.** `stage_over_step_span` guesses where the leap must start: `ends_at + speed × length`. That assumes the rider's speed stays steady, then reuses the road mapping.
- If the rider slows mid-leap, what's left of the gap shrinks, and the cat falls back a little: frames repeat, or the cat slides backward.
- The fraction is turned back into a frame number with a fudge: `progress × count + 0.000000001`, "a billionth of a frame counts as having arrived".

So the cat's "one frame a step" holds only while the speed is steady, and only within a billionth. It's a heuristic coincidence: it works because the rider usually rides steadily.

## Why it's this way

Stateless was chosen for a real reason: stepping back has to show the same critter. A frame worked out from where the rider is can't disagree with itself.

But stepping back doesn't need that, as it turns out. `Tour.step_back` restores a whole saved `RideInstant` from its history. Anything the instant remembers comes back with it, exactly.

## Three ways to go

**A. Everything by the road (the bird's way, for the cat too).** An animation is a function of where the rider is: a flipbook glued to the road. It's honest and simple, with no estimate and no fudge, but a slow rider sees the cat leap in slow motion and a fast one sees it snap. That is "frames on successive metres", not steps.

**B. Keep the estimate (today).** It's closest to steps while the speed is steady. It falls back when the rider slows, and it needs the billionth.

**C. The ride remembers when it began.** When the rider first comes within an encounter's trigger gap, the instant records the step: `started_at : Clock`, per encounter, in `RideInstant`.
- After that, the frame is `clock - started_at`. That's exactly one frame a step, whatever the speed.
- No estimate, no fraction, no fudge. `Stage` can answer the frame number directly.
- Stepping back is exact, because the memory is part of the saved instant.

The cost is a piece of state, and one rule for when an encounter starts. The cat's "however fast the rider comes, it finishes in time" no longer comes free: a leap that starts at a fixed gap takes a fixed number of steps, so a fast rider may reach the cat before it lands. The trigger gap has to be chosen for the fastest rider (top speed × the leap's length), and that's a named rule rather than a guess.

## My recommendation

**C for both the cat and the bird.** It's what you decided an animation is. It removes the last tuned fractions and the billionth. It answers the book's open question "how much does the ride remember?" with something concrete: each encounter's first step. The bird's flight then becomes so many steps of flapping, and stops being so many metres of road.

**A** is the fallback, if you'd rather the ride remember nothing.

**The leap's keyframes** (shares 0, 0.4, 0.85, 1 and lifts 0, 0.27, 0.17, 0, "set by eye") are a drawing, like the stills, which were traced by eye too. Under C they become the leap's frames on successive steps. I'd keep them as keyframes, honestly labeled.

**Pixels:** the cat's and bird's frames move under C or A, so you'd eye-test both critters. The rest of the frame holds.
