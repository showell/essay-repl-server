# Where the mountains belong

A review of the backdrop left one question of shape. It's a small one; a word is enough.

## The facts

A frame is painted in two layers:
- **The backdrop** (`Backdrop.frame_shapes`): the sky, the sun, the grass. Backdrop's doc says it builds "what is behind the ride".
- **The ride's shapes:** everything else, in depth order.

The mountains are the first entry in the *ride's* shapes (`FrameView`), not part of the backdrop, though Mountains' own doc says the skyline is "behind the rest of the ride". Mountains imports Backdrop only for the grass color.

## The choice

- **(a) Move the skyline into the backdrop:** `BackdropShapes` gains a `skyline` field after `grass`. The paint order is the same, so no pixels move.
  - "Behind the ride" gets one home.
  - The frame widget gets a Skyline layer of its own.
  - The cost: Backdrop then needs the camera's heading and the dusk, and the exact pixel gate, which paints the backdrop pixel by pixel and the ride as shapes, would have to paint the mountains' polygons as part of the backdrop.
- **(b) Leave it:** the mountains stay first among the ride's shapes. The docs get fixed to say so: the backdrop is the sky, the sun and the grass, and the skyline is the farthest of the ride's shapes.

## My recommendation

**(b).** The mountains turn with the camera and darken with the dusk, like the ride's things and unlike the flat sky. Treating them as the farthest of the ride's shapes is honest, and it keeps the pixel gate simple. The real smell is the two docs disagreeing, and (b) fixes that.

## Steve's answer (2026-11-07)

**(b).** The mountains stay the farthest of the ride's shapes. Backdrop's and Mountains' docs get fixed to agree: the backdrop is the sky, the sun and the grass.
