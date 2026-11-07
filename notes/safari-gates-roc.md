# What the Roc in safari/gates is for

`canvas_apps/safari/gates/` has 17 Roc files, about 2,300 lines. None of it is game code: the game never imports any of it. It's what the merge gate (`gates/run.shale`) builds and runs to check things the expects alone can't. Most of it is one job: **painting a frame into exact pixels, in Roc, so the gate can hold a frame by its hash.**

## Why a Roc rasterizer at all

The game draws by handing shapes to the browser's canvas (`web/shapes_canvas.js`). A canvas antialiases and differs a little between browsers, so its pixels can't be held exactly. The gate needs a picture that's the same on every run, so these files paint a frame themselves, pixel by pixel, with no antialiasing. The page check (`part=page`) does the browser side separately, by hashing the canvas calls.

## The files, by job

**Painting a frame into pixels (8 files, about 650 lines)**
- **`SafariFrame`** (60): paints one whole frame: the sky and grass, then the sun, then the frame's shapes in paint order, all turned by the camera's roll. Its header is the best introduction to the folder.
- **`BackdropPixels`** (60): the sky and the grass, the first layer.
- **`SunPixels`** (63): the sun's glow and disc, over the sky.
- **`ShapesPixels`** (59): every other shape in the frame, through ScanlineFill. Its twin is `shapes_canvas.js` in the browser.
- **`ScanlineFill`** (214): fills polygons and discs a row at a time, by the nonzero rule, like a canvas but exact.
- **`PixelGrid`** (120): a grid of pixels as one list, with which pixels a span covers and where each one sits.
- **`PixelColor`** (52): a pixel's color as `0xRRGGBB`, and a translucent color laid over one.
- **`ScreenRoll`** (87): the screen turned about its center by the lean, as the canvas turns it.

**The proof tools the gate runs (`part=proof`)**
- **`RasterFrame`** (72): paints held frames with SafariFrame and prints each one's hash. These are the nine held depths in `proof.expected` (step 0, 100, 1570 and so on). It can also print every pixel for a PNG (with `pixels_png.mjs`), which is how frames get looked at.
- **`ShapesFrame`** (108): checks that cutting concave polygons into triangles changes nothing on screen. The native runner, roc-ray, fills only convex polygons, so it draws ConvexCut's triangles. This paints each held frame twice, whole and cut, and requires zero differing pixels.
- **`StepBack`** (47): checks that one step back goes back exactly one step, on either side of the history's cap.
- **`OnRoad`** (106, today's): rides the whole route and fails if the rider leaves the road, a segment goes backwards, or the rider runs past a segment's end.
- **`ProofRide`** (40): a helper that takes a tool through the ride once, stopping at each held depth on the way, so no depth replays the steps before it.
- **`Hex`** (27): writes the hex digits the tools print.

**Expects that span modules**
- **`CrossModuleExpects`** (1,132): the expects that can't sit beside their code without importing modules only for the test, such as a road view, a scene, or a whole ride. Your rule from today keeps them here. The sunset and night tests landed here today.

**Not run by the gate**
- **`FrameBench`** (35): a native benchmark for profiling a frame with `perf`.

## How they fit

```
proof.expected  <-  RasterFrame  --+
                    ShapesFrame  --+--> SafariFrame --> BackdropPixels, SunPixels, ShapesPixels
                                   |                      \--> ScanlineFill --> PixelGrid, PixelColor, ScreenRoll
                    StepBack, OnRoad --> ProofRide (ride once to each depth)
part=expects    <-  CrossModuleExpects
```

## Is it all earning its keep?

Mostly, I think:
- The rasterizer is what lets the gate say "no pixel moved" with certainty, and that claim has carried every lane today.
- ShapesFrame guards a real difference between the browser and the native runner.
- StepBack and OnRoad each guard one rule cheaply.

Two things are worth a look later:
- **FrameBench isn't gated,** so nothing proves it still builds.
- **CrossModuleExpects is 1,132 lines,** and your "nuke tests that will never fail usefully" rule hasn't been applied to it yet. The tests lane queued after World will prune it.

If any of it surprises you as more than it should be, say which, and I'll have it reviewed with the same eye as the game.
