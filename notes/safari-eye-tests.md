# Safari eye tests

The dev page always shows master after a green gate: **http://143.244.172.148:9210/safari/**

The newest entry is at the top. Each one says what should look different, and where. Anything else that looks different is a regression, so tell me.

## 2026-11-07, master 6c0029c7: the pond, and the camera built once

**Steve: passes.**

This deploy has the makers lane, lib's third pass, the widget gate and `RiderCamera` in it. Every held frame kept its hash (no held frame shows the pond, so the pond was checked by hashing frames 5000 to 5400 against master). The one thing you should see:

1. **No line between the pond's water and its bank.** The bank is now drawn under the water, with no shared edge, so the browser no longer antialiases a seam between them. The pond is in view around steps 5000 to 5400.

The rest (the pond mirroring on a left turn, `Billboard.half_width`, the baby's doc, lib's crash checks) changes nothing on screen.

## 2026-11-07, master 50306f59: the new rider physics

**Steve: passes** (and with it the entries below that weren't marked: 63f60b48 with the road seams, 8db6237b with the stills, fd32d1a5 with the World split, 7447a4ef with the widget kit).

**This is the one where the ride changes.** It has your seven physics decisions in it, and the held frames moved on purpose. Watch a whole ride once, at normal speed:

1. **The weave is gone.** The rider aims at the road's middle instead of a target that moved with it (`lean_target` deleted). The line through bends should look steadier.
2. **No throttle hold when leaned** (`lean_hold` deleted), and **no sudden lift to the bend's exit speed.** Speed through and out of bends should change more smoothly.
3. **The gaze returns at one even rate,** with no ease-then-snap. Watch the head come back after a look (the pigs, the cat): it should glide home, not settle and then jump.
4. **The ride's end.** The rider brakes to a stop instead of jumping to the end. Watch the last few seconds.
5. **The timing moved:** the ride finishes at step 6779, not 7071. The sunset's climax still falls on the long road west (the new test holds it), and full night comes before the end (the other new test).
6. **The road margin:** the rider's widest point is now 1.97 m of the road's 2 m half-width, against 1.9996 m before (0.4 mm from the edge).

Kept on purpose: the 60 m bend approach. Every firmest-brake option moved the whole ride, so it waits for the Motion chapter.

## 2026-11-07, master 63f60b48

This deploy has several lanes in it: World's second half, FrameView, the backdrop cleanup, the sunset and night tests, `RiderCamera`, and **the road seams**. Every held frame kept its hash. The one change you should see:

1. **No white seams across the road.** Each segment's road and each bend's paving is now one polygon, so the browser no longer antialiases a line between chunks. Watch the road near and far, and on bends. The pond's water and bank can still show a faint line where they meet; a lane is fixing that.

Everything else (the encounter renames, the camera built once a frame, the sky and sun unchanged in their math) should look exactly as before.

## 2026-11-07, master 8db6237b

This deploy has the stills lane in it. The still data was rewritten by script: thousands of negative numbers and every color, plus the gradients and fills reshaped. Every held frame kept its hash. Glance at the critters:

1. **The bull,** whose 40 gradients became 18 linear and 22 radial tags. Its shading should look as it did.
2. **The cat, the birds, the cows, pigs, elephants, giraffes, zebras, rhinos and ducks.** Their colors are now written in hex, and they should all look as before.
3. **Shapes that might have flipped.** A sign lost in the negatives rewrite would mirror or smear part of a critter. Look for anything inside out.

## 2026-11-07, master fd32d1a5

This deploy has the first World lane in it: World split into the route plan and `Segment`, a `Route` type, and placed things carrying a whole road point. That reaches nearly every module, but every held frame kept its hash. Watch the whole ride once at normal speed:

1. **The route's end.** The last segment no longer carries a fake 0° turn or a forced quiet stretch. The ride should still end and restart as before.
2. **The herds.** Their layout moved home to the herd modules, and the pig state was reshaped. The pigs, the standout pig and the cows should stand where they did.
3. **Anything placed beside the road,** such as trees, billboards, the pond's ducks and the animals at the bends. Every placed thing now carries its point whole, so check that nothing has jumped.

## 2026-11-07, master 7447a4ef

This deploy has the widget-kit lane in it: the widgets' shared code, and `Brush.flat` across the apps. The ride itself is unchanged, and every held frame kept its hash. Nothing in the ride needs a look. If you open a widget page later, its readouts (numbers with a minus sign, such as the sky widget's sun height below the horizon) should read as before.

## 2026-11-07, master db1777b9

**Steve: passes.**

This deploy has the Polygon lane in it. Every held frame kept its hash. These are the places to glance at:

1. **The bull's shading.** Its 40 gradients now take their offsets as checked fractions instead of being clamped quietly. The bull's billboard should look as it did.
2. **The truck's headlight beams and brake glow,** whose gradient makers were renamed (circular and elliptical).
3. **The mountains and the tower,** which now pass corners first to the flat-polygon maker.

## 2026-11-07, master d67bc638

**Steve: passes.**

This deploy has the leftovers and Pipeline lanes in it. Every held frame kept its hash. These are the places to glance at:

1. **The truck's brake glow.** Its outer edge color is now built with `ArgbColor.from_rgb`, not by reading an RGB number as an ARGB one. The glow should fade out to nothing at its edge, just as before.
2. **The radio tower's translucent part** (the one at a quarter alpha) is now made with `Brush.with_alpha`. It should look the same.
3. **The lean's effect on the lens.** The focal length's lean factor goes through the new `Lean.portion`. A hard lean should zoom just as before.

## 2026-11-07, master 75db5c6a

**Steve: passes.**

This deploy has the truck, SceneShapes, units and trees lanes in it. Every held frame kept its hash, so nothing should change. These are the places to glance at:

1. **The truck.** Its faces, lights and brake lamp were rebuilt from one strip helper, and the headlight beam's center is now computed directly. Look at it up close: the body's faces, the brake lamp's glow when it slows, and the headlight beams at dusk.
2. **The trees.** The cones are measured from the tree's foot now, and the crown's top is computed the short way. Near trees' shaded cones and crowns should look the same.
3. **Billboards and rails** are ordered by the rewritten frame code. The guard rails and the billboards should sit in front of and behind things just as before.

## 2026-11-07, master 6d2245ef

**Steve: passes.**

This deploy has the rider, tuning and lib lanes in it. Every held frame kept its hash, so almost nothing should change. These are the places no check sees:

1. **The perched bird over its tree.** A bird is perched near the route's start. Its feet should sit on the crown, drawn over the tree, not tucked behind it. Before, they tied in depth, and the tie order happened to paint the tree over the bird's feet.
2. **The ellipse gradients in a real browser.** The browser's ellipse-gradient path was rewritten to use `ctx.transform`, and no check runs the JS. Stills with soft round shading, such as the bull's billboard, should look as they did, with no smears, stretched blobs or missing shading.
3. **The roll margin on a hard lean.** In a sharp bend, at full lean, the sky's and grass's rectangles should still reach past every corner of the screen, with no bare corner showing.

Things that changed underneath and shouldn't show: the motorcycle's state (Motorcycle and RiderEyes), the herds' shared scatter, the trees' height written as parts × 36 mm, and lib's colors and shapes.
