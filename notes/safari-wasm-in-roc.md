# What the wasm target would take

*2026-09-11, late. A plan, written before any code, from reading Roc's
platform tests and safari's browser harness side by side. Nothing here is
built.*

## The two sides, as they are

**The browser side already exists and does not need to change.** Safari's
`web/blitter.js` fetches `/driving/safari.wasm`, binds sixteen exports, and
paints. Per frame it calls `renderFrame`, which answers a byte length, and
reads that many bytes from `bufPtr` as a stream of 32-bit words: a tag, a
colour, a point count, then x,y pairs as `f32` bit patterns, with a
six-word form for a disc and a gradient form for tags two to six. Between
frames it calls `advance` and `back`, and it asks for readouts: `clock`,
`riderSeg`, `riderTilt`, `skyTop`, `skyHorizon`, the sun's position and
scale, `riderV`, `truckLead`, `truckV`. The JavaScript is the oracle for
"looks ok", and it stays the fork it is.

Today those sixteen exports are `poc/drive_shim.zig`, appended to the
Codex-to-zig transpile. The shim holds the state the pure program cannot,
because Codex records live in a bump arena the shim rewinds every frame: a
flat rider, a flat truck, a clock, a 2048-deep history ring for the down
arrow, and the world built once. Its `renderFrame` calls `ride-frame` then
`blit-expand` and packs the commands into words itself.

**The Roc side has the pattern in its own test tree.** A Roc app sits on a
platform; the platform is a Roc header plus a *host* in another language.
For wasm the host is zig compiled to `wasm32-freestanding`, and `roc build
app.roc --target=wasm32 --output=x.wasm` links the two into one module whose
exports the platform header lists. `test/wasm/platform/host.zig` is a
working host of a few hundred lines: the allocator, the panic hooks, an
exported `wasm_main` that calls into Roc. And `test/provided-callable-host`
shows the shape we want: the platform `provides` half a dozen named
functions that take and return `Box(...)` values, the host declares them as
C externs and calls them as often as it likes, and a boxed value crosses as
one pointer whose identity the host keeps. `boxed_model_update` is that
shape with a model: `update : Box(Model) -> Box(Model)`.

## The shape

One platform, one app, and the chapter modules we already have.

**The model is a Roc value, boxed.** The rider, the truck, the clock, the
history as a `List` of past rides, and the world. Roc's reference counting
keeps it alive between calls, so the arena rewind and the flat copies the
zig shim needed disappear. `Safari.ride_next` and `Safari.ride_frame` are
already emitted modules; the app is a hundred lines that hold the model and
call them.

**The word packing moves into Roc.** `renderFrame`'s loop over commands is
pure: `List(DrawCmd) -> List(U32)`, with `F32.to_bits` for the coordinates.
Done in Roc it is graded like everything else, by comparing the words the
Codex shim produces for the same ride, frame for frame, which is what the
harness's `paint_probe.js` already does for three hundred frames.

**The platform header provides sixteen functions**, one per blitter export,
most of them `Box(Model) -> F64` readouts, plus `init`, `advance`, `back`,
and `render : Box(Model) -> List(U32)`.

**The host is a copy of Roc's test host** with the sixteen exports written
over it: each keeps the one boxed pointer in a static, calls the Roc extern,
and answers. `renderFrame` hands the `List(U32)`'s pointer and length
straight to the blitter, no copy.

## What it takes, in order

1. **Hello, wasm.** Roc's own `test/wasm/app.roc` on its platform, built
   with our compiler, opened in a browser with a five-line page. Proves the
   toolchain end to end on this box before any safari is involved: the
   wasm32 LLVM path in the debug compiler, the host build, the exports.
2. **The packing, graded.** A `Blit`-adjacent Roc module that packs
   `List(DrawCmd)` into words, and a spec-shaped check that the words for
   `ride_frame(world, ride_initial)` equal the Codex shim's. The verdict is
   a byte comparison, so it is a `.expected` like the other 54.
3. **The platform and the app**, with the model. `emitted.sh` keeps grading
   the chapters; this adds the app on top of them.
4. **The browser.** `serve.py` from safari-codex against the Roc module at
   the same path, the same blitter.

## Where the risk is

- **Speed.** The transpiled zig runs at frame rate; Roc's LLVM output for
  the same chapters is unmeasured. The 60-fps budget is the number to get
  early, in step 3, before polishing anything.
- **The emitted chapters as an app's imports.** The sweep proves each
  chapter compiles and computes in the Echo platform; a platform with a
  host is a different link. Step 1 is what removes that unknown cheaply.
- **The debug compiler.** wasm32 goes through LLVM, which is where the
  ReleaseFast build ran out of memory at link; the debug compiler links
  small modules in its tests, and safari is not small. If the link is the
  wall, the one-line checker fix and a ReleaseSafe build are the way round
  it, and that is the same investigation already on the table.

| repo | revision | role |
|---|---|---|
| roc (roc-lang/roc) | main @ 68267ddd, debug build | `test/wasm/platform`, `test/provided-callable-host` are the templates |
| roc-apps | 5fed0d0 | the chapter modules the app imports |
| safari-codex | units of 2026-09-10 | `web/blitter.js`, `poc/drive_shim.zig`, `harness/serve.py` |
