# Safari eye tests

The dev page always shows master after a green gate: **http://143.244.172.148:9210/safari/**

The newest entry is at the top. Each one says what should look different, and where. Anything else that looks different is a regression, so tell me.

## 2026-11-07, master d67bc638

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
