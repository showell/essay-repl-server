# Open calls, round 6: the rider and the trees

*2026-11-08. Two more type audits came back: the rider's modules and the trees. I decided the clear findings, and they go to lanes as slots free up. Every one holds every pixel. These six are yours, each with my lean; a word per item is plenty.*

**The rider.** The audit used the dynamics-and-decisions split from the axes note. The dynamics are equations: the bike's speed and lean, and the eyes' swivel. The decisions are search and rules: when to brake, how far to lean, where to look. These are the clear fixes I'm making:
- The bike integrates its own speed. Today Throttle, a decision, does the arithmetic.
- The eyes stop deciding where to look. They're handed a target, as the bike is handed its controls.
- The camera stops working out the rider's attention and head turn, and reads them from the rider.
- The steps take the one segment they use, instead of the whole route.
- The gawking brake uses the same "brake to a speed within a distance" rule as the bends and the truck.

1. **Where does noticing live?** "That pig is eye-catching" is the rider's noticing. Both the eye (where to look) and the brake (slowing to gawk) need it. Today it lives in Gawking, the speed module, so the eye depends on the brake's module.

   *Lean:* the eye owns noticing. It moves into Gaze, and Gawking reads it from there.

2. **A home for the decisions.** `RiderMind` is an empty namespace with one function, the bike's controls. The gaze decision happens elsewhere.

   *Lean:* make RiderMind the home of every per-step decision: the controls, and the gaze target once it moves out of the eyes. That's the axes note's split, made visible in the module list.

3. **The bike's lean rate.** How fast the bike can change its lean is a bound inside LeanSearch, the search's own business.

   *Lean:* the bike owns it, since a real bike can only lean so fast. The controls would carry a lean change, and the bike would clamp it. It's a little more churn than leaving it, so say no if you'd rather not.

4. **The bike turns the same amount per step at any speed.** `turn_per_lean` makes the turn independent of speed. Is that an honest cheat or a physics gap?

   *Lean:* name it as an honest cheat, chosen by eye, and say why beside the constant. Fixing the physics would change the ride.

**The trees.** The clear fixes are already merged: one maker for a tree tier's inputs, `Camera.Upright`, one name for the tree's detail record, and CowHerd asking for the near tree line by name.

5. **Scene counts trees.** Scene is meant to be free of any one kind of object once each is turned into a rendering. It still counts how many trees are nearer than each tree, because the nearest four get a round trunk. It imports Conifer only for that.

   *Lean:* move the count beside `trees_in_view` in TreeSighting. Seeing which trees are near is part of sighting them, and Scene goes back to being free of kinds.

6. **The cone reach.** Trees from 80 to 200 metres away get cones with no shading. Those may look the same as the plain triangles drawn beyond 200 metres, and if they do, the two distances could be one.

   *Lean:* leave it. Merging the two would move pixels for no reader-visible gain, and it isn't book work.
