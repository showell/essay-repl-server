# Four questions about lib

A review of canvas_apps/lib (Brush, Shapes, the color types, Font and the rest) is in. The clear fixes are decided, and a lane is doing the first part now:
- `Brush.Fill` gets full field names, with Linear and Ellipse holding their source points. That also fixes a bug: the browser painted large ellipse gradients flat.
- The glow's 0.4 stop becomes a field.
- `Skip` goes.
- The shapes' one-letter fields get full names.

All of it changes the Roc side, the JS painter and the native runner together. A second lane comes after:
- `Brush.translucent`, to mirror `opaque`
- records for long runs of float arguments
- the convex cut as its own module
- bracket makers so nobody writes a bare `Blend`
- the color types crashing on out-of-range values

Four questions are yours. Each has my recommendation.

**1. `lib/Color`: keep the roc-ray shim?** Pong, camera, workshop and breakout use `lib/Color`. It's a port of roc-ray's color module, with its own `Color.Rgba` (U8 channels, alpha 0 to 255) and a `brush` conversion. There are now two types named `Rgba` on different scales, and it's a third way to write a color beside RgbColor and ArgbColor. The case for keeping it is port fidelity: those apps were ported from roc-ray with "change the import line and nothing else". *Recommend: move the four apps to RgbColor/ArgbColor and delete `lib/Color`. The one-way-to-write-a-color decision is worth more than fidelity to a port that's done.*

**2. Make `Brush.Rgba` opaque?** It's a plain record anyone can write, which is how raw float colors keep appearing (Safari's sun glow `a: 0.85`, camera's `a: 90.0 / 255.0`, breakout and workshop). Opaque, it could only come from `Brush.opaque`, `Brush.translucent` or `mix`. One unknown: the web platform's `Frame.roc` is a structural copy of the shape types for the JS glue, and it counts on structural unification. An opaque type nested inside might not unify. *Recommend: yes, if a quick compiler probe says it unifies; otherwise drop it. Moving apps off raw colors (question 1) gets most of the benefit either way.* Safari's glow alphas (0.85 and 0.32) aren't n/255, so that change moves the glow by a hair and joins your eye-test list.

**3. Give the convex cut's pieces their own type?** `Shapes.Shape` includes `Pieces`, the triangles of a concave polygon. Only the native runner's convex cut makes them, and the JS painter throws on one. So an app can build a shape that the browser refuses. A type of its own for the cut's output would close that, at the cost of one more type at the native seam. *Recommend: yes, but low priority. It fits the second lane.*

**4. Two meanings of "View".** `lib/View.roc` is a movie's eye, used only by trick_or_treat. `View(...)` is also a mark in `Shapes.Shape`, setting the space for the shapes after it. *Recommend: rename the module (`Eye`?). It has one user, while the mark crosses to JS.*

A word per item is enough.
