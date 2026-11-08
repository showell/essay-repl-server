# Axes of difficulty in Safari Ride

*2026-11-08. A thinking note, not a plan. Steve's five axes first, then what I'd add, then where I'd sharpen the lines.*

## Your five

1. **Building shapes.** Billboards are easiest (an emoji at a size), cats hardest (traced stills, poses, a crossing), and trucks have the most moving pieces (a box, six faces, tires, beams, lamps).
2. **Placing objects in the world.**
3. **The passage of viewed objects in time** (motion).
4. **The camera** (trigonometry).
5. **Rider physics** (lots of math).

## What I'd add

**6. What covers what.** Depth sorting, the painter's order, clipping at the near plane, a perched bird drawn over its tree, a tower sinking below the earth's curve. None of that is shape, placement or projection. It's the step after all three, where the scene decides the order and how much of each thing survives. It's a real source of bugs: the tie rule had five homes until today.

**7. Who owns a behavior.** This is the axis you exercised this afternoon. The beacon should own its blink, not the tower. The headlights own a sensor. The brake lights follow the truck's pace. The cat crosses by the hand of god, and the rider reacts. It isn't a technical problem like trigonometry; it's a design problem, and it cuts across all the others. I'd guess it's where most of the remaining code smells live, because each fix on the other axes can quietly put a rule in the wrong owner.

**8. Honest cheats.** The sun and the mountains sit at infinity, and they're projected by a different rule on each axis. Towers sink at an exaggerated earth's curve so you can watch them go. The truck teases the rider. Each is a deliberate departure from physics, and the hard part is keeping each cheat in one place, named, so it doesn't leak into the honest code around it. FarHeight and EarthCurve are two of those homes.

**9. The platform edge.** Roc on one side and the browser on the other: the wasm export names, the shape protocol the JS draws, frame timing, and today's compiler crash, which only the wasm build hit. It's small in lines of code, and it's where the worst surprises come from.

**10. Proving it.** The held frames, the ride's held finish, StepBack, the widgets as real clients, and the book's own build. In most codebases that would be overhead. Here it's a design force: worked out, not stored, exists partly so any frame can be checked cold.

## Sharper lines

**Shape, placement and projection are three coordinate frames, not three topics.** A shape is drawn in the object's own frame: the truck's box, the cat's still. Placement maps that frame onto the road: a `RoadPoint`, a lift, a `Spot`. The camera maps the rider's view onto the screen. The difficulty of each is how far its frame is from the next one. A billboard faces the camera, so its shape needs almost no mapping, and that's why it's easy. A truck is a real 3-D box, so every corner goes through all three maps, and that's why it has the most moving pieces. The cat is hard for a different reason: its shapes are many and change every frame, so it's hard on the time axis, not the frame axis.

**Motion is three problems with three costs.** The book's table already names them:

| Kind | Examples | What makes it hard |
|---|---|---|
| Clock-driven | sun, sky, beacons, headlights | Almost nothing: a pure function of the step |
| Stepped | rider, truck | State, and a history so you can step back |
| Rider-driven | cat, bird | Coupling: the encounter has to be planned against the rider's approach, which is the hand of god |

"Motion" as one axis hides that the first kind is nearly free and the third is the hardest thing in the game.

**The camera is two problems.** One is where it points, which is the rider's head: lean, gaze, attention. That makes it downstream of the physics and the rider's mind. The other is how it projects: the pinhole, the near plane, the far-field cheat. The trigonometry is mostly in the second; the coupling is in the first.

**Rider physics is dynamics plus decisions.** The bike's dynamics are speed, lean, braking and turning. The rider's decisions are when to brake, how far to lean (LeanSearch), where to look, and how to react to a cat. Those are different kinds of code. The dynamics are equations; the decisions are search and rules. The decisions are the harder half to test and to explain.

## For the book

These axes could be the book's spine. Each chapter would mostly add one axis, or a harder case on an axis already met. The order roughly follows difficulty:

- shapes, from billboards to trees to the truck to the cat;
- placement;
- time, clock-driven first (the beacons and the sunset);
- the camera;
- stepped motion and physics (the rider and the truck);
- rider-driven motion (the cat and the bird).

"Who owns a behavior" isn't a chapter; it's the question each chapter answers again, which suits the book's habit of letting ideas recur.

One question to start: does the frames framing (shape, placement and projection as three maps) match how you think about it, or do you see placement as a bigger problem than that?
