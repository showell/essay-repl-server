# raytrace-on-screen: where a traced frame goes

A case study of one framebuffer demo, to learn what makes emitted Codex slow
in Roc. raytrace-on-screen traces `codex/test/raytracer-test`'s scene, two
spheres over a floor, at 160 x 120 with Cobblestone's Raytracer, and copies
the trace onto the screen. On the page it takes about 105 ms a frame.

## The instruments

- **The page's profile.** `node --cpu-prof` over `frames.mjs`, twelve frames
  of the page's wasm. Roc names a wasm function by id, so each hot id was
  matched to a source name from `ROC_LIR_DUMP=` by the constants it holds and
  the functions it calls. (The record is `framebuffer/PERF.md`.)
- **A minimal program.** `framebuffer/bench/RayBench.roc`, hand-written beside
  the modules rocemit emits for the demo: the demo's scene and camera, traced
  for 30 frames, built natively with Roc's dev backend, as the page is.
  `trace` finds every pixel's closest hit and nothing else; `render` is the
  whole `rt-render`, shading included. Each prints a checksum, which must not
  move when the time does. `framebuffer/bench/raybench.sh` builds and times it.
- **The machine code.** `perf` over the native bench, and `objdump` of the
  hottest functions.

## What the page's frame is

| what | share of the page's frame |
|---|---|
| `rt-intersect-obj`: the sphere and plane tests | 22% |
| `rt-closest`: the walk over the scene for a ray | 17% |
| `geo-sqrt`: a square root, written in Codex as Newton's method | 11% |
| the demo's copy onto the screen, one `poke-32` a pixel | 11% |
| `rt-shade` | 6% |
| the small vector functions and `List.get` | 11% |
| the zig host | about 1% |

It is Raytracer's own Roc. The host's memory and screen are not where the
time goes.

## Step 1: the square root is the machine's

Geometry's `geo-sqrt` and Quaternion's `quat-real-sqrt` are the same loop:
guess, refine, stop when two guesses are within `~`, four ULPs. rocemit now
writes both as Roc's `sqrt` behind the same guard (zero for an argument that is
not positive), keyed by chapter and name, beside its existing rule that writes
DeviceMath's `real-sqrt` as `F64.sqrt`. A test runs the loop against the
instruction from a millionth to a trillion and on the first 2,000 perfect
squares: they never differ by more than four ULPs.

| 30 frames, native | `trace` | `render` | checksum |
|---|---|---|---|
| the Newton loop | 0.86 to 1.12 s | 1.26 to 1.35 s | unchanged |
| Roc's `sqrt` | 0.57 to 0.64 s | 0.82 to 0.88 s | unchanged |

A third of the frame, and not one pixel moves.

## Step 2: what rt-closest carries

`rt-closest` walks the scene's objects and keeps the best hit so far, and a
hit is a whole `RtHit`: a flag, a distance, a position and a normal (two
3-vectors), and the material (a colour and three integers). Every object, for
every ray, returns one, and the walk compares it and carries one forward. In
the LIR, each step of the loop takes the best hit apart into its twelve
scalars and builds it again. A sphere's hit also normalizes its normal, a
square root, even when the sphere is not the closest.

Two hand-edited variants of the emitted Raytracer test what that costs. Both
find the nearest object by its distance alone, then build one `RtHit`, for
that object; the comparison is the original's, so the same object wins every
time.

- `dist-calls` computes the distance with the vector functions, as the emitted
  code does.
- `dist-inline` writes their arithmetic out, in the same order of operations.

| 30 frames, native, fastest of five, interleaved | `trace` | `render` |
|---|---|---|
| as emitted, with Roc's `sqrt` | 0.600 s | 0.859 s |
| `dist-calls` | 0.527 s | 0.767 s |
| `dist-inline` | 0.549 s | 0.778 s |

The checksums are the emitted build's in all three. **Carrying distances
instead of hits saves about 12%. Inlining the vector functions saves nothing**
that five runs can tell apart from noise.

## Step 3: what is left

After both changes a ray costs about 900 nanoseconds against three objects,
which is slow for native code. `perf` over `dist-inline`'s `trace` finds no
copies through libc and under 1% in reference counting. The time is in the
functions' own code, and the disassembly says what that code is:

| function | share of `trace` | instructions | moves to or from a stack slot | f64 arithmetic |
|---|---|---|---|---|
| `roc__proc_343`, the nearest-object walk with the distance tests folded in | 48% | 1,749 | 1,503 | 54 |
| `roc__proc_321`, the bench's pixel loop, with `rt-trace` folded in | 12% | 1,936 | 1,712 | 0 |
| `roc__proc_342`, called by the walk | 11% | 233 | 181 | 0 |

**Eighty-six percent of the hottest function's instructions move a value to or
from the stack.** The dev backend gives a value a stack slot, not a register,
and a record moves field by field from slot to slot. The hottest instructions
in `perf annotate` are `movsd` to a slot. That is the dev backend's code, not
Raytracer's shape: no rewrite of the program removes it.

## What this leaves to decide

1. **The `sqrt` rule** is built; its gates are running (the ladder, safari's
   units, the smoke tests, `verify.sh`). It lands when they pass.
2. **Distances before hits** in `rt-closest` is Raytracer's change, not the
   emitter's: about 12% natively, the same images, and it would help every
   backend. It could go upstream as a PR.
3. **The rest is the dev backend.** An optimizing build (`--opt=speed`, LLVM)
   is what keeps values in registers. By the standing rule that is for a
   finished page, not for exploring, so measuring it here is your call.
4. **For Zulip**, this adds a second concrete question to the profiling one:
   whether the dev backend's register allocation is planned, since for
   floating-point code like this, stack moves are most of what it emits.
5. **Renderer3D** is the scene demos' version of this question, and the same
   minimal-program approach applies to `r3d_scan_cols_sh!`.
