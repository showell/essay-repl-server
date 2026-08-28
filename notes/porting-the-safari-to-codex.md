# Porting the Safari to Codex

*For Steve. 2026-08-28. First impressions after reading `wasm/`, reading the
Codex side, and running the whole loop end to end on a spike. Ideas about how
to break the problem up — not a plan you have to agree to yet.*

---

## The short answer

**The loop works and it is fast.** I built it in this session: a Codex chapter
went through the bundler, through `codexzig`, through `zig build-exe`, and its
output was graded against numbers produced by a zig probe that imports the
real `wasm/camera.zig` and `wasm/geom.zig`. The projected pixel agreed to
1e-4. Round trip is **under five seconds** and **never boots a guest** — this
is nothing like the ladder's usual cadence.

**Three walls are in the way, and one of them is a real blocker.** The zig
plug has no emitter for `real-to-int` or `real-from-int`. That is fine for
`pond`, `camera`, `geom`, `critter` — and it stops the port dead at
`sky`, `world`, `rider`, `mountains`, `render`. Closing that hole is a small
PR against `ZigEmitter.codex` and it is squarely the mission we are already
on.

**Order of work:** two modules and a harness first (a few hours), then the
plug PR, then the bulk. The TS→zig port took a day; I would not promise this
in a day, because the target language is pure and the source is a
buffer-writing imperative core. Call it a week of sessions to a full-frame
match, with something honest on the board on day one.

---

## What I actually ran

Not a sketch. This all executed:

```
pwsh build/bundle-app.ps1 -Src spike2.codex -Out spike2-unit.codex   # 3 deps + root
native/codexzig < spike2-unit.codex 2> spike2.zig                    # 0.064 s
zig build-exe spike2.zig -O ReleaseFast                              # ~1 s
./spike2
```

The Codex chapter carried a hand-ported `camera.FOCAL` and `camera.project`,
plus a Taylor sine lifted from `Gpu chapter DeviceMath`. A separate zig probe
— `@import("wasm/camera.zig")`, the real file, unmodified — printed the gold:

```
focal 685.510900        px 582.826660        py 341.130650
camfocal 574.115360     rider.right -3.797166  rider.forward 7.199412
```

and the transpiled Codex graded itself against those literals:

```
focal      ok
px         ok      (tolerance 1e-4 on a 582.82666 pixel)
sin1       ok
cos100     ok
tight-px   ok
```

So: **Codex reals arithmetic transpiles and runs, and a hand port of the
camera agrees with the zig to four decimal places on a screen pixel.** That is
the feasibility question answered.

---

## The three walls

### 1. The plug cannot convert between Real and Integer *(the blocker)*

My first spike used `real-to-int` to print scaled integers. It does not
compile:

```
error: zig plug: no emitter for real-to-int
error: zig plug: no emitter for real-from-int
```

`ZigEmitter.codex` has 52 builtin emitters; of the whole real-conversion
family only `bits-to-real-approx` is there. Everything else falls to the
generic refusal at line 1145. This is a hole, not a considered refusal — the
considered refusal is `show` on a Real, which says so in its own words.

Two consequences worth stating separately:

- **The port stops at module three.** `pond`, `camera`, `geom`, `critter`,
  `paint`, `safari_critter`, `guard_rail` need no conversion. `sky`,
  `mountains`, `world`, `rider`, `tower`, `tree`, `truck`, `render`, `safari`
  all do — colour ramps, the dusk clock, the flipbook index, segment counts.
  That is 80% of the program.
- **`Gpu chapter DeviceMath` cannot be transpiled at all today.** `real-sin`
  calls `dm-reduce`, which calls `real-from-int`. So the chapter that gives
  Codex its sine, and the accuracy test that grades it, are both dark to the
  zig arm. That is a finding on its own, and a good one — it is the kind of
  thing that only shows up when somebody tries to be a customer.

The fix is small and I think it is unambiguous. Bare metal is
`cvttsd2si` / `cvtsi2sd` (`X86_64Builtins.codex:1663-1679`) — truncate toward
zero, and the x86 "integer indefinite" result (INT64_MIN) on NaN or overflow.
Zig's `@intFromFloat` truncates the same way but is UB out of range, so the
honest emission is a small prelude helper with the three guards, not a bare
cast. That is a PR with a clear argument and a checkable claim.

### 2. `show` on a Real is refused, on purpose

`@compileError("zig plug: show on a Real needs __real_to_text, which this
plug does not have")`. The emitter explains why: `std.fmt` would agree with
bare metal on some values and not others, so it refuses rather than guess. I
think that is right and I would not touch it.

It does mean **a transpiled Codex program cannot print a float**, which sounds
fatal for an oracle and isn't. Two ways around it, and we should use both:

- **The grading pattern** (what I ran above, and what Codex's own
  `device-math` test does): the zig side emits the gold, the Codex side
  computes and prints `ok` / `BAD` against a stated tolerance. No float ever
  crosses the wire. Works *today*, with no plug change.
- **Scaled integers**, once `real-to-int` lands: print `real-to-int (x *
  1000.0)` and plain-diff the two dumps. Better for a thousand-value frame
  dump, where `BAD` alone tells you nothing.

Start with grading, move to scaled integers when the plug allows it.

### 3. Codex `Real` is f64 in the plug; the game is f32

`ZigEmitter.codex:297` maps every `RealTy` to `f64`, whatever width the Codex
type asked for. So there is no way to make the port compute in f32, and **a
bit-exact oracle is off the table** — every comparison is a tolerance
comparison, forever. Fine for geometry (we agreed to 1e-4 on a pixel today),
and it has a sting in the tail; see the chaos note below.

(Worth noticing in passing: the plug quietly widening `Real approximate` to
f64 means a Codex program using f32 reals computes *different numbers* on the
zig arm than on bare metal. That is a DDC-shaped question and not mine to
answer this week, but somebody should write it down.)

---

## Where the seams are

You asked for seams that can be driven by a zig program printing to stdout.
There are four, and they are already cut — the architecture did this for us.

**Seam 1 — the leaf math.** `geom.zig` and `camera.zig` are pure functions of
scalars. A probe walks a table of inputs and prints the outputs. This is the
one I ran. Cheapest, and it catches the arithmetic-shaped mistakes.

**Seam 2 — the static data.** `pond.zig` is *nothing but* data: an outline, a
bank, six ducks, three colours. So is most of `world.zig`'s route table and
the tree/tower dimension tables. A probe dumps them; the comparison is exact,
integer, and boring. This is the right *first* port because it has no
arithmetic at all — it tests the harness, not the math.

**Seam 3 — the draw-command buffer.** This is the money seam and it is
already a flat, serialisable artifact: `paint.zig` writes
`[tag][color][nPoints][x f32][y f32]…` and `paint.frameWords()` hands the
whole frame over as `[]const u32`. A zig probe decodes one frame to text; the
Codex port — which will *return* a list of commands rather than write a
buffer, being pure — prints the same list. Tags and colours compare exactly,
coordinates compare with tolerance. **When this matches for a frame, the
scene core is ported.** Everything else is the blitter's business.

**Seam 4 — the fold over time.** `safari.zig` is the only module with mutable
state; everything upstream is pure. So the whole ride is
`state → state`, and a probe can dump the rider and truck state per step.

### The hazard in seam 4, and what to do about it

`decide()` picks the lean by **binary search over a simulated path** — twelve
probes, each a float comparison. A 1e-7 difference in an f64-versus-f32
projection will eventually flip one of those comparisons, and from there the
two rides are on different trajectories. A long trace comparison **will** go
red, and it will not mean the port is wrong.

So don't compare trajectories. Compare **one step at a time from a shared
state**: the zig probe dumps state *N* and state *N+1*; the Codex side is fed
state *N* and must produce *N+1*. Drift cannot accumulate, and a failure
points at one step and one module instead of at frame 4000. Same trick for the
truck. If you want a whole-ride check on top of that, check *invariants*
(stayed on the road, never looped, sunset monotone) rather than coordinates —
which is exactly what `test/test_model.ts` already does for the TS.

---

## What I would not port

- **The blitter and the rasterizer.** `blitter.js` and `native/raster.zig` are
  the display, and the architecture already declares them the far side of the
  seam. The draw-command buffer is the contract; port the side that computes
  it. That is the same call the project made for Delivery (zig solver, TS
  display), for the same reason.
- **`cat_frames.zig` and `emoji_frames.zig` by hand.** 615 KB of baked
  polygons, and they are *generated* — `ops/bake_cat` runs the real TS drawing
  code through a recorder. Teach the baker a Codex emitter and the data ports
  itself. Do it late; nothing depends on it until the cat crosses.
- **A browser build.** The transpiled zig is a hosted program — `std`,
  `ArrayListUnmanaged`, a 4 GB bump region reserved from `page_allocator`. It
  is not going to `wasm32-freestanding` without work nobody has asked for. The
  Codex port's deliverable is *the same scene, verified*, not a second live
  site. If we want to look at it, the honest path is: Codex emits the command
  list, and the existing native rasterizer draws it into the same PNG contact
  sheet `native/main.zig` already writes per segment. **A picture, from a
  Codex program, that you can put beside the zig's.**

---

## The bump heap, before it bites us

The emitted prelude reserves a 4 GB region and bump-allocates from it; nothing
is ever reclaimed. Every list, every record, every frame. A pure port that
rebuilds the scene each frame will chew through that in a few thousand frames
and then `@panic("oom")`. Not a blocker — it means **one probe process per
short horizon**, not one process that drives the whole route. Worth designing
for from the start rather than discovering at frame 3000.

---

## How I would break it up

Sizes are hand-written zig lines, baked data excluded (3,374 lines total).

**Phase 0 — the harness, on `pond` alone.** (49 lines, no arithmetic.)
Build the four scripts: bundle, transpile, build, grade. Pick where the port
lives. Get one `ok` per duck. The point of this phase is that the *loop* is
committed and repeatable before any math is in question.

**Phase 1 — the leaf math.** `geom` (110) + `camera` (67), with the sine and
sqrt cited from `Gpu chapter DeviceMath` rather than rewritten. Seam 1
probe with a real input table. Ends with the projection agreeing on a few
hundred points. *This is where I'd stop and show you something.*

**Phase 2 — the plug PR.** `real-to-int` / `real-from-int` in
`ZigEmitter.codex`, with the three out-of-range guards, plus the
`DeviceMath`-is-dark finding written up. Unblocks everything below and is
worth sending on its own merits. Half a day, most of it the ceremony.

**Phase 3 — the scene furniture.** `sky` (100), `mountains` (169), `tree`
(174), `tower` (186), `guard_rail` (108), `critter` (55), `safari_critter`
(52), plus `paint` as a command-list builder (199). Each one is seam 2 or
seam 3 on a single object. Highly parallel, low risk, mechanical.

**Phase 4 — the world and the ride.** `world` (329), `rider` (262), `truck`
(305), `gaze` (106), `cat` (187). The one-step oracle carries this phase. The
binary search in `decide()` is the hard part of the whole project and I expect
to spend real time on it.

**Phase 5 — the frame.** `render` (661) and the state fold from `safari`
(255). Ends at a full draw-command match for a frame, then a PNG.

Phases 0-1 are a session. Phase 2 is a session. Phases 3-5 are the week.

---

## What I'd want you to decide

1. **Where does the port live?** `games/driving/codex/` beside the zig (the
   probes want a relative `@import` of `../wasm/*.zig`, and the port *is* of
   that program) — or its own repo like the transpiler got. I lean toward
   living beside the zig; nothing there is built by `ops/build_safari_wasm`,
   so gopher's deploy is untouched.
2. **Do we spend Phase 2's half-day on the plug**, or work around it? The
   workaround is a fixed-point port in integer milli-units, the way every
   Codex foreword math chapter already works (`Geodesic`, `Matrix3`, `Complex`
   — all integers, no reals). That would be a more *idiomatic* Codex port and
   a much less *faithful* one, and it would rewrite every formula. I would
   rather fix the plug.
3. **Is "a PNG from Codex, beside the zig's" the finish line?** It is the one
   I would aim at, because it is the only artifact in this whole project you
   can judge by looking at it — which is how the Safari has always been
   judged.
