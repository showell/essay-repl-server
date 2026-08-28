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
- **A browser build *through zig*.** The transpiled zig is a hosted program —
  `std`, `ArrayListUnmanaged`, a 4 GB bump region reserved from
  `page_allocator`. It is not going to `wasm32-freestanding` without work
  nobody has asked for. If we want to *look* at the port, the honest path is:
  Codex emits the command list, and the existing native rasterizer draws it
  into the same PNG contact sheet `native/main.zig` already writes per
  segment. **A picture, from a Codex program, that you can put beside the
  zig's.** (There is a second path I did not know about when I wrote this —
  `codex/plugs/wasm/`, 2,882 lines, emits WAT and ships a `browser-shim.html`.
  See the postscript.)

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


---

# Postscript: the f32 question

*Added after Steve asked where the f32 constraint comes from, and whether a
`ZigEmitter32` would be crazy. Short version: the game's f32 is a wire format
and nothing else, the plug's f64 is a house convention and not a zig quirk,
and the framing "a 32-bit emitter" is off in a way that makes the job smaller
rather than bigger.*

## Where the game's f32 actually comes from

One place. `paint.zig` packs each coordinate into a single `u32` word:

```zig
buf[cursor] = @bitCast(p.x);
```

and `blitter.js` reads those same words back through
`new Float32Array(mem.buffer, base, len / 4)`. **The draw-command buffer is
the f32.** One word per number, and the `@bitCast` is free only because
`camera.ScreenPt.x` is already f32.

Everything upstream — `ScreenPt`, `geom.Vec3`, `RiderPt`, every constant in
`camera.zig` — is f32 *so that* the bitcast at the wire is free. That is the
whole causal chain. Nothing in the physics, the projection, or the look asks
for it.

Two things follow that I think are worth saying plainly:

**The TypeScript original computed all of this in f64**, because JavaScript
has no other number. The zig port *narrowed* it. So a Codex port in `Real`
(f64) is arguably closer to the original than the zig is, and the f32 is the
newer of the two decisions.

**And the width does not change the picture.** I measured it this session —
same probe, same inputs, `camera.zig` and `geom.zig` copied and
`s/\bf32\b/f64/g`:

| | f32 (the game) | f64 |
|---|---|---|
| `FOCAL` | 685.510900 | 685.511043 |
| projected x | 582.826660 | 582.826656 |
| projected y | 341.130650 | 341.130663 |
| `camFocal(0.5, 0.2)` | 574.115360 | 574.115499 |

Worst gap 1.4e-4 on a 685-pixel value — 2e-7 relative, which is f32 epsilon to
the digit. On a 960×600 canvas that is a ten-thousandth of a pixel. **The
width is invisible to the product and visible only to the oracle.** And if we
ever wanted the wire back, rounding to f32 at push time restores it exactly:
the narrowing belongs at the seam, which is where the zig already puts it and
where the Codex port would put it too.

So my answer to "why is the game constrained to f32" is: it isn't. Its
*buffer* is.

## What the plugs do — and this is not a zig-plug quirk

`ZigEmitter.codex` drops the width at both type sites:

```
zig-let-annot   is RealTy (w) (m) -> ": f64"     (line 297)
emit-zig-type   is RealTy (w) (m) -> "f64"       (line 328)
```

`(w)` and `(m)` are bound and never read, with no comment either place. And
the binary-operator table collapses five distinct opcodes onto one symbol
(1270-1273):

```
is IrAddNum | IrAddVec | IrAddRealApprox | IrAddRealTrapping | IrAddRealSaturating -> "+"
```

That is three separate semantic collapses in one line: f32 computed as f64,
*trapping* silently not trapping, *saturating* silently not saturating.

Before filing that as a zig defect I checked the neighbours. **The C# plug —
our best crib, and the one their own release gate runs — does exactly the
same thing** (`CSharpEmitterExpressions.codex:1021-1024`, character for
character). And the wasm plug states it as policy rather than leaving it
implicit:

> Every real on this target is carried as f64 bits in an i64 slot, `IrNumLit`
> included, so there is one width to reinterpret and no f32 case to separate.

So: **`Real` is a double, house-wide.** With fifty-odd plugs, that is a
convention, not an oversight, and a PR that quietly made zig the exception
would be a bad citizen.

## Except that bare metal is not a double

The reference compiler picks the opcode by type
(`IR/LoweringTypes.codex:182-185`):

```
is OpAdd -> ... else if is-real-approx-type ty then IrAddRealApprox else ...
```

and `X86_64.codex:2774` emits **`addss`** for it — single-precision add, in an
XMM low lane. The reference computes f32 in f32. Every plug computes it in
f64. **A Codex program written in `Real approximate` gets different numbers
from the reference compiler than from any plug**, which is precisely the class
of thing this ladder exists to notice.

And upstream is not casual about the width. `codex/test/ops/real-approx-modes.codex`
opens with:

> THE WIDTH IS THE WHOLE RISK HERE. […] Run the f32 values through the f64
> constants and the exponent read is nonsense, the guard never fires, and
> saturating quietly stops saturating.

Its gold pins a saturating clamp to one bit: `2139095039` (largest finite
single) and not `2139095040` (+inf).

## Why nobody has tripped over it

Because you cannot run those tests through the plug. I transpiled both of
upstream's f32 ops tests this session. Neither compiles:

```
real-approx.zig:        zig plug: no emitter for to-real-approx
                        zig plug: no emitter for from-real-approx
real-approx-modes.zig:  zig plug: no emitter for real-approx-from-int
                        zig plug: no emitter for real-approx-to-bits
                        zig plug: no emitter for to-real-approx-saturating
```

There is no way to get an f32 value *into* or *out of* a transpiled program,
so the arithmetic collapse has never been observable from the zig arm. **The
missing hole hides the wrong answer.** Fix the conversions without touching
the arithmetic and you make the divergence visible — which is an argument for
doing them in that order, on purpose, and saying so.

## So: `ZigEmitter32`?

I think the framing is off, and usefully so — the job is smaller than a second
emitter.

A separate plug is right when the difference is a property of the **target**.
Width isn't. It is a property of the **type in the source program**: `Real`
and `Real approximate` can appear in the same chapter, in the same function.
`ZigEmitter32` would be a 4,000-line fork to change two arms, and it would
still be wrong for any program that used both widths — which is most programs
that use f32 at all, since you narrow at a seam and compute in the middle.

There is also nothing to configure. The information is already at every site
and is being thrown away twice:

- the declared `CodexType` carries `RwF32` (the `(w)` those two arms ignore);
- the IR opcode carries it independently (`IrAddRealApprox` vs `IrAddNum`).

Two independent channels, both already threaded to the emitter. That is the
opposite of a plug-level flag.

**What honoring the width would actually cost**, as far as I can see it from
outside:

- `emit-zig-type` + `zig-let-annot`: `RealTy RwF32 -> "f32"`. Two lines.
- **Literals — the real work.** `IrNumLit` emits `@as(f64, @bitCast(@as(i64,
  n)))`, an f64 bit pattern. Zig will reject that where an f32 is wanted, so
  the num-lit sites need the context type. The emitter already carries
  peer-type patch-ups for exactly this shape (1567, 1657, 2185) — hardcoded to
  f64. That is where the difficulty lives and I would not price it without
  trying it.
- `cx_bits_to_real_approx` in the prelude deliberately widens f32→f64, with a
  comment that says "Real is f64 here". That comment becomes false and the
  helper becomes identity.
- The conversion builtins are missing regardless, and are the same PR as
  `real-to-int`.
- **Modes are a bigger, separate job** and I would explicitly not take them
  on. The exponent guards differ per width, as their own comment says. But
  there is a cheap and strictly-better move available: make trapping and
  saturating **refuse** instead of silently degrading. It converts a silent
  wrong answer into a compile error, it costs an hour, it cannot make anything
  worse, and it is the plug's own established idiom — refusing `show` on a
  `Real` is the same move already made.

## What I would do about it, in order

1. **Add the f64 conversions** (`real-to-int`, `real-from-int`). Unblocks our
   port, and unblocks `Gpu chapter DeviceMath`, which is dark to zig today.
2. **Make trapping and saturating refuse.** Silent wrong answer → loud
   refusal. Cheapest correctness win on the board.
3. **Ask about the width; don't PR it.** It is a house convention across
   fifty plugs and their own gate follows it, so the first artifact should be
   a question with a repro attached, not a patch. The repro is free now: their
   own `real-approx.codex`, which the zig arm cannot build, and the `addss` at
   `X86_64.codex:2774` that says what the answer should have been.

And for our port: **none of this is on the critical path.** Port in `Real`,
grade against the zig f32 with a stated tolerance. 1e-4 of a pixel is a fine
gate, and it is exactly the width gap — so the oracle stays honest about what
it is and is not measuring.

## One more thing I found while looking

`codex/plugs/wasm/` — 2,882 lines, Codex IR to WebAssembly text, with a
`browser-shim.html`, a `build-page.ps1`, and an end-to-end script. I wrote
earlier that a browser build was out of reach; that was true of the *zig*
path and I did not know this existed. Whether it can carry a program this
size, and whether it could feed the existing `blitter.js`, I have not tested.
If "the Safari, in Codex, in the browser" is a finish line you want, that is
the door to knock on — and it is the one plug in the tree whose f64 policy
would cost us nothing, because the wire narrows to f32 at the buffer anyway.
