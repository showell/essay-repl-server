# Shapes, from first principles

## What a shape is

A shape is a region of the screen and a way to fill it. That's all. The ride needs four kinds of region:

- a triangle (every tree tier, and the cones);
- a rectangle (every trunk, the sky, the grass);
- a disc (the beacons, the sun, the brake glows);
- any other polygon (the road, the truck's faces, the traced emojis, the mountains).

It needs a handful of fills: flat, shaded, and three kinds of gradient (linear, circular, elliptical).

Region and fill are independent. Any region can take any fill, so the code should have one place for regions and one place for fills, and a shape should pair one of each.

## What we have instead

- **`Shapes.Shape`** (in `lib`) does pair a region with a `Brush.Fill`, which is right. But its regions are uneven: `Poly`, `Disc` and `Rect`, with no triangle. Its numbers are bare `F64`s, so it can't speak the ride's `Pixels`.
- **Safari's `Polygon` module** has nine functions and about 30 calls. Each one is "a `Poly` from these screen points, with this kind of fill": `flat_polygon`, `shaded_polygon`, `linear_gradient_polygon`, `elliptical_gradient_polygon`, `circular_gradient_polygon`, `triangle` and so on. It tangles three jobs:
  1. it turns `Screen.Point`s in `Pixels` into bare numbers;
  2. it builds fills, which is a `Brush` job;
  3. it cuts polygons at the camera's near plane (`clipped_polygon`), which is a camera job.

  Because it pairs regions and fills in its function names, it grows as region times fill, and it duplicates `Shape`'s own job. That's the redundancy you smelled: `Polygon` exists to make up for what `Shape` can't say.

## The proposal

1. **`Shape` says regions in full words and in typed points:**
   ```
   Shape : [
       Triangle({ first : Point, second : Point, third : Point, fill : Brush.Fill }),
       Rectangle({ top_left : Point, width : Pixels, height : Pixels, fill : Brush.Fill }),
       Disc({ center : Point, radius : Pixels, fill : Brush.Fill }),
       Polygon({ corners : List(Point), fill : Brush.Fill }),
       ...the marks, Image and Text, as now
   ]
   ```
   A `Triangle` has three corners by construction, so `Polygon.triangle` disappears and the book shows the tag itself. `Pixels` and the screen `Point` move from Safari into `lib`, beside `Shape`, because they're the screen's units and the platform is the screen's owner. The ride then builds shapes straight from its own points, with no conversion layer.
2. **Fills live in `Brush`:** one function per kind of fill, such as `Brush.flat`, `Brush.shaded` and `Brush.linear_gradient`, each giving a `Brush.Fill`. Any region takes any of them.
3. **Clipping moves to the camera code** that owns the near plane. It gives back a `Polygon` shape.
4. **Safari's `Polygon` module is deleted.** Every call becomes a tag plus a fill, for example `Triangle({ first, second, third, fill: Brush.flat(green) })`.

The book's Shapes chapter becomes: a shape is a region and a fill; here are the four regions; here's a triangle, a `Triangle`; here's a rectangle, a `Rectangle`. There's nothing to explain away.

## What it costs

- **`lib.Shapes` changes,** so every painter changes: the web JS, native roc-ray, the proof's scanline painter, `ConvexCut`, and `Shapes`' own transforms.
- **The other canvas apps change too,** because they build shapes: pong, snake, breakout and the rest. The book never mentions them, but they must still compile and pass their gates. Moving `Pixels` into `lib` means each of them builds its shapes in `Pixels`. That's mechanical (`Pixels.of(x)`), but it touches every app.
- **About 30 Safari call sites change,** plus the widgets and the expects. The pixel proofs judge it: a painted frame should come out the same, pixel for pixel, except where a native triangle paints a pixel edge differently from a path, and each of those gets explained, not waved through.

That's one agent's careful job, done in steps, each step green: (1) add `Triangle` and the full-word names, (2) move `Pixels` and `Point` to `lib`, (3) move the fills to `Brush`, (4) move clipping and delete `Polygon`.

## The one question

Do the screen's units (`Pixels` and the screen `Point`) move into `lib`, so that `Shape` speaks typed points and every canvas app builds its shapes in `Pixels`? I recommend yes. The alternative keeps `lib` in bare `F64`s and keeps a thin conversion layer in Safari. That's cheaper, but it leaves part of the redundancy you're objecting to in place.
