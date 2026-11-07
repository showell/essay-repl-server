# Safari eye tests

The dev page always shows master after a green gate: **http://143.244.172.148:9210/safari/**

The newest entry is at the top. Each one says what should look different, and where. Anything else that looks different is a regression, so tell me.

## 2026-11-07, master 6d2245ef

**Steve: passes.**

This deploy has the rider, tuning and lib lanes in it. Every held frame kept its hash, so almost nothing should change. These are the places no check sees:

1. **The perched bird over its tree.** A bird is perched near the route's start. Its feet should sit on the crown, drawn over the tree, not tucked behind it. Before, they tied in depth, and the tie order happened to paint the tree over the bird's feet.
2. **The ellipse gradients in a real browser.** The browser's ellipse-gradient path was rewritten to use `ctx.transform`, and no check runs the JS. Stills with soft round shading, such as the bull's billboard, should look as they did, with no smears, stretched blobs or missing shading.
3. **The roll margin on a hard lean.** In a sharp bend, at full lean, the sky's and grass's rectangles should still reach past every corner of the screen, with no bare corner showing.

Things that changed underneath and shouldn't show: the motorcycle's state (Motorcycle and RiderEyes), the herds' shared scatter, the trees' height written as parts × 36 mm, and lib's colors and shapes.
