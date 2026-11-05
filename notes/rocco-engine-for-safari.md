# Could rocco-engine sit under safari?

*2026-11-05. A short look at [Pixelsprout/rocco-engine](https://github.com/Pixelsprout/rocco-engine) at commit 6a436bf, one day after its v0.11.0 release.*

## Verdict

**Worth watching. Not worth a spike now.**

The Roc side fits better than expected, and the Roc pin is probably not the deciding problem. But safari can't run on the engine as it stands, because the engine has no way to draw a polygon that a Roc app computes each frame. Running safari properly means adding a new drawing pass to the Odin engine, then keeping that patch alive in a one-author engine that shipped four releases in the last three days. The result could only be judged on your Windows machine.

Three facts decide it:

1. **The frame doesn't fit.** A rocco `Scene` is meshes loaded from files plus a UI of upright rectangles and text. Safari's frame is a list of polygons with gradients, all leaning through a rotation. Nothing in the `Scene` carries that.
2. **The pin mostly doesn't matter, as far as a type check can tell.** Rocco's Roc code checks under our 11-03 compiler with 0 errors. A small adapter holding safari's real `SafariApp` under rocco's real platform also checks with 0 errors. Linking and running are untested.
3. **Rocco is native only, and web is out of scope on its roadmap.** Safari's page would stay on the wasm runner, so stops off the road would exist only in the native build.

The trigger to look again would be rocco gaining 2D drawing, or runtime meshes, or game shaders. Its roadmap lists world-space sprites and game shaders as later work. If you'd like to play with the stop-off idea sooner, there is a cheap experiment below that needs no engine change, but it has to run on Windows.

## What rocco is (facts)

- It's a 3D engine in Odin on sokol, and it is a true Roc platform. A game is a Roc app with five functions: `launch`, `init`, `step`, `loaded` and `view`.
- The split is the same idea as safari's. The app is a pure model and returns a description of the picture. In the design doc's words, "Roc never calls a draw function."
- It has PBR lighting, cascaded shadows, skinned meshes from `.glb`, bloom, fog, tone mapping, cubemap skies, audio and collision queries.
- It builds for macOS (Metal), Linux (GL core) and Windows (D3D11). Each machine builds its own target.
- The license is UPL, the same as ours.
- It has one author, Braeden Foster: 910 commits since 2026-09-22, 11 stars, and a second game (Kula) in its own repo. The last 100 commits all came in the last two weeks. Releases v0.8.0 through v0.11.0 came out between 11-02 and 11-04.
- The repo is run with AI agents and a task file, much as ours are. It has a stray macOS binary named `main` in its root. I didn't run it.

## 1. Running safari as is

The seam is the one you'd guess: a new runner beside `native/CanvasAppRunner.roc`, with `lib` and `safari/` untouched. Most of it fits well.

| Safari gives | Rocco takes | Fit |
|---|---|---|
| `fps`, `advance(model, input, 1/fps)` | `step_hz`, `step` with a fixed `dt` | Direct |
| `init`, `size`, `title` | `init`, `launch` | Direct |
| `Input.Snapshot` | `Input` with key codes, pointer and wheel | Mechanical, like the roc-ray key bridge |
| `sounds`, `tones` | Sound files only | Doesn't matter: safari reports no sounds |
| `frame : model -> List(Shape)` | `view : Model -> Scene` | **Doesn't fit** |

Rocco's `Scene` has two ways to put something on screen, and neither is a shape:

- **`Scene.ui`** is a tree of `Panel` and `Text`. A Panel is an upright rectangle with a corner radius, laid out by Clay, capped at 16,384 quads. It can't rotate, and it has one flat color. That covers `Rect` and perhaps `Disc`, but safari wraps the whole frame in a `View` that rotates it for the rider's lean.
- **`Scene.nodes`** holds `Draw`s of a mesh id. Meshes come from `.glb` files or the cube, sphere and plane primitives. `Command` has no way to hand the engine vertices, and an Image is a loaded file, so there are no runtime meshes and no runtime pixels.

Safari's fills are the rest of the gap. It uses `Radial`, `Linear`, `Ellipse`, `Span` and `Glow` gradients, and `Flat` is only part of the picture. A `Draw` has a `tint` with no alpha, so translucent fills are out too.

So the honest answer has two halves. The Roc runner is a small adapter, under 100 lines for the parts I wrote and probably a few hundred with every key. The drawing is not small, because the engine's model has no slot for it.

There are two ways to fill that slot:

- **A real shape pass (faithful).** Add `Scene.shapes` to the vocabulary, regenerate the glue, and add an Odin pass with a streamed vertex buffer and a brush shader. `engine/ui_render.odin` is a 140-line model for the streaming, and `lib/BrushGlsl` already holds the gradient math. Roc's `Shapes.cut` already reduces everything to convex pieces. This needs a fork or the author's agreement.
- **A hack with no engine change (a rough look only).** Ship a one-triangle `.glb` with an unlit material. A `Draw`'s `scale`, `scale_rot` and `rot` together can produce any 2D linear map, so one `Draw` can place any triangle on a plane. That gives flat colors only: no gradients, no alpha, no additive glow, and the tone map still touches the colors. It would look wrong, but it would prove the plumbing.

## 2. The Roc pin and how safari builds

Rocco pins `nightly-2026-10-11-7d256b9`. We're on `nightly-2026-11-03-34bd006`, which is 2,521 compiler commits later. I expected this to decide everything, and so far it doesn't.

What I checked (facts):

- `roc check` under our 11-03 compiler: `platform/main.roc`, `packages/linalg` and `examples/pong` all give 0 errors. The only complaint is a warning that the header pins another version. The compiler says `roc fmt` updates the pin.
- A scratch adapter app, with `lib` and `safari` copied beside rocco's platform and `ui` package, gives 0 errors on 11-03 and on 10-29. I planted one wrong argument to confirm the check reaches safari's types, and it went red with a mismatch against `Input.Snapshot`.
- Safari's own `web.roc` checks clean on the 10-29 nightly.
- `src/builtins/host_abi.zig` has no changes between the two nightlies.
- Rocco's target names (`x64glibc`, `x64win`) are all valid on our compiler.

What I couldn't check:

- `roc check` stops before code generation, so nothing here proves a working build.
- `src/glue/glue.zig` changed a lot (192 lines added, 518 removed), and `builtins/str.zig`, `list.zig` and `utils.zig` all changed. What I skimmed looks like refactoring, but I read only a filtered part of the diff. Rocco's Odin glue is a submodule I didn't clone or run, so whether `roc glue` still works on 11-03 is unknown.
- The v0.11.0 release notes say to use the same nightly. A host built for 10-11 may or may not work with an app built on 11-03.
- We don't have the 10-11 compiler here, so I don't know whether safari compiles on it. Going down to rocco's pin is the wrong direction anyway: roc-ray and the rest of roc-apps sit on 11-03.

My guess: the likely route is rocco moved up to 11-03 in a fork, which is a glue and host rebuild, not a Roc rewrite. Rocco last moved its pin on 10-15. Before that it moved roughly every two weeks.

## 3. The mixed-art idea

This is the part that fits best, because rocco already layers things the way you imagined.

Facts:

- One `Scene` already holds 3D `nodes` and a flat `ui` drawn over them, after the tone map.
- One Roc `Model` can hold both worlds. The type-checked adapter does exactly this:

```roc
Model : { place : [Road, Stop], safari : SafariApp.Model, room : U32 }

view = |model| {
	the_frame = game.frame
	match model.place {
		Road => { ..Scenes.empty, ui: List.join(the_frame(model.safari).map(panel_of)) }
		Stop => {
			room : Node
			room = Draw({ ..Draw.default, id: 1, mesh: model.room })
			{ ..Scenes.empty, nodes: [Light(Light.ambient({ r: 1.0, g: 1.0, b: 1.0 })), room] }
		}
	}
}
```

- While the place is `Stop`, `step` doesn't call `advance`, so the tour freezes and resumes on the same tick. Safari's determinism survives, and safari's code doesn't change.
- A full-window Panel with alpha can fade between the two. `Load` and `Unload` bring a room's assets in and out.
- Only the trigger needs a small Roc change: safari has to say that a place on the road is a place to stop. Until then, a key will do.

Guesses:

- The hand-over is the natural place to soften the clash of styles: a fade, or the road's last frame shrinking into a doorway.
- A room doesn't have to mean a pile of assets. Safari today has no asset files, and that's part of its character. Rocco's cube, sphere and plane primitives, with real lights, shadows, fog and bloom, could build an interior entirely from Roc code. That may suit safari better than a Blender pipeline, and it's the first thing I'd try. Trees and animals with real shape would need `.glb` files.
- A shape pass would need care with color. Rocco's UI colors are linear and encoded by a shader, while safari's are canvas colors with gradients mixed unencoded.

### The smallest real experiment

No engine change, no Odin, about a day of agent time (a guess). On Windows, with Roc only:

1. Point the adapter's `pf` and `ui` at the v0.11.0 bundle URLs and build with our 11-03 compiler. This answers the open pin question in one try. If it fails, the fallback is a host rebuild with Odin and the Visual Studio Build Tools.
2. Draw the road with flat triangle `Draw`s, as above. Ugly is fine.
3. Press Enter to fade into a room made of primitives, with a sun and shadows. Press Enter again to return.

It passes if the ride resumes on the same tick, and if you like how the two looks sit together. That second test is the real one, and only your eyes can run it. If it charms you, the shape pass becomes worth doing. My guess for that pass is 300 to 600 lines of Odin and shader code plus the vocabulary and glue changes.

## 4. What this box can't do

Facts:

- There's no Odin, Docker, Xvfb or display here. I installed nothing. glibc is 2.39, which meets rocco's Linux minimum. `/dev/dri` has entries, but I didn't look at what's behind them, and this droplet has no display.
- So here I could read the code and run `roc check`, and that's all I did. No rocco code was built or run.

Possible here with installs (a guess at effort, and against the rules of this look):

- Build the host with Odin. `ROCCO_HEADLESS=1` runs with no window and no GPU, so game logic could be tested.
- Software GL under Xvfb is how rocco's own Linux check runs. Its Bridge can take screenshots, so frames could be inspected slowly. On 2 cores this would be a poor way to judge anything that moves.

Windows only:

- Seeing it. Shaders, bloom and motion at real frame rates, and whether the two styles work together, need a real GPU. Rocco's D3D11 backend is the one that would run there.
- The first build. Rocco doesn't cross-compile. The Windows host comes prebuilt in the release bundle, so step 1 needs only Roc. Rebuilding the host needs Visual Studio Build Tools.

## 5. How the facts and guesses divide

Checked here: rocco's model and its lack of a polygon path; the type checks on two compilers; the unchanged `host_abi.zig`; the native-only roadmap; the activity numbers.

Guessed: that a 10-11 host can link to an 11-03 app; that the rest of the compiler diff is harmless; every effort number; the styling ideas; and how many `Draw`s a safari frame would cost, which I didn't measure.
