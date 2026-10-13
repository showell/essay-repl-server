# Dog Park's math, read cover to cover

*2026-10-13, night. A study of the committed Zig at `176fe14`, about 2,900
lines without tests, read for its arithmetic, its units and its frames of
reference, plus the JavaScript where numbers cross into the page. While I
read, an agent was rewriting the tests and dropping the old routes, so I
read the committed code and left that work alone.*

## The verdict

The core representation is right: positions are integer 256ths of a pixel
in `i32`, with every product in `i64`. Integer arithmetic keeps the page's
wasm and the server's native build identical to the bit, which floats would
not guarantee across targets and compilers. The headroom is large: the
world's far corner is 8.2 million 256ths, about 260 times inside `i32`. The
largest squared length, a full-world diagonal, is about 1.3 × 10¹⁴, far
inside `i64`. A 256th of a pixel is finer than anything on screen, and it
keeps a wire number short (`d80.40`). I would not change it.

What needs work is everything around that core:

- **The knobs are stated in the machine's units, not yours.** The code
  says 120 where you said 7.5 px a second, and 320 where you said 20
  seconds.
- **Three position frames survive** where one would do.
- **Pixel-ticks broke two assumptions** that were safe before tonight:
  the page's 50 px snap, and the cost of checking for overlaps.
- **Some code isn't ready for the torus,** despite the promise that only
  `delta` would need to change.

## Findings

### 1. Say the knobs in your units

`physics.zig` holds `speed = 120` with the comment "7.5 px a second", and
`let_go_ticks = 320` with the comment "20 s". Both numbers are right, but
only the comments say what they mean. Tonight every request you made was
in px, px per second, seconds or percent, and I converted each one by
hand. That conversion is where a slip would hide.

**Proposal:**
- **One named `ticks_per_second = 16`** in Zig, exported to the page.
  Today the page has its own `tick_ms = 62.5`, which makes two sources of
  truth.
- **Small converters,** so the knobs read as you speak them:
  `speed = pxPerSecond(7.5)`, written as `perTick(px(15), 2)` to stay
  integer; `let_go_ticks = seconds(20)`; `wary = px(225)`.
- **Every test reads the knob,** never the literal.

### 2. One frame for a position, not three

Today a critter's place exists in three units:
- **256ths:** the physics, the wire and the snapshot;
- **whole pixels:** `dogs.zig`'s `ParkPoint`, which `dogs.json` stores;
- **half pixels:** `cows.zig`'s `CowPoint`, which `cows.json` stores. This
  was the old cow rule's trick for keeping half of a 1 px step exact.

The old rule is being deleted with the old routes. And since tonight, every
`/load` resets the park to `Board.laidOut()`, so **`dogs.json` and
`cows.json` no longer seed anything a player sees.** They seed only the
first board of a fresh data folder, and the first load replaces it at once.

**Proposal:**
- lay the park out directly in 256ths;
- retire both JSON files, along with `ParkPoint` and `CowPoint` as
  position types;
- keep whole pixels only where a person reads them: the page's labels
  and the knobs.

Each frame that goes is one fewer conversion to get wrong. (I told the
agent that is working now to keep the JSON files as the seed. Tonight's
reset-on-load made that call moot, so this would be a follow-up.)

### 3. Pixel-ticks broke the page's snap

`scene.js` draws any move over `snap_px = 50` on either axis as a jump to
the new place rather than a glide. That threshold existed to tell a push's
jump apart from walking. Under pixel-ticks, a drag at the cap moves the
leashed dog up to 100 px a tick, and every follower moves about as far, so
they **snap instead of gliding** during exactly the fast drags you were
playing with. Distance no longer tells a jump from a walk.

**Proposal:** the physics already knows which moves were jumps (the
out-from-under step and the push's nearest spot). Have it flag them in the
tick's result, and have the page snap only those. That replaces a
distance guess with a fact.

### 4. The cost of pixel-ticks is mostly one defensive check

A tick at a fast drag went from 21 µs to about 5 ms. Reading the loops
explains it. In each pixel-tick, each awake dog runs:
- `outFromUnder`, which scans every critter ranked above it in the
  region, awake or not;
- two sweeps, each scanning every critter in the region;
- its wishes, which scan the awake critters only.

At up to 200 pixel-ticks a tick, the scans dominate. Yet an overlap can
only come from a cow's push, and the push already jumps the critter it
lands on.

**Proposal, in order:**
- **(a)** Check out-from-under once a tick, not every pixel-tick. The
  rule only promises it at the dog's turn.
- **(b)** Give each awake dog a neighbour list per tick: every critter
  within twice the largest square plus the most anything can move in a
  tick. Sweep against that list. It is exact, because nothing outside it
  can be reached within the tick.
- **(c)** Count the pair checks as a number the tests can bound, so the
  cost cannot creep back without a test noticing. That is the metal-vmm
  rule: test the logic, not the wall time.

I'd expect (a) and (b) together to bring a tick back under a millisecond.

### 5. Manhattan for the leashed dog, straight lines for the rest

The leashed dog's motion is cut into 1 px steps per axis, so a diagonal
drag of (10, 10) px gives the others 20 pixel-ticks, while the leashed dog
travelled only 14.1 px in a straight line. Each other dog's step is capped
by its straight-line length. So on a diagonal, a follower can cover about
1.4 times the leashed dog's distance. This matches what you asked for
("Manhattan distance"), and it may be part of why the packs keep up so
well. It is a choice, not an accident. A one-line comment should say so,
in case it ever looks like a bug.

### 6. The torus promise is only half kept

`delta` is the one difference function for centre to centre, as decision 14
wants. But the rectangle code subtracts coordinates directly, in absolute
world terms:
- `Rect.holds` and `Rect.overlaps`;
- the region's `TileSpan`;
- the jump's `gapOn` and its search box;
- `inWorld`.

A torus will need rectangles taken relative to a centre (the region's or
the jump's) through `delta`. That doesn't need doing now; it is decision
14's later work. But the doc says "the wrap will change that one function",
and that is not true today.

**Proposal:** fix the doc's sentence now. When the torus comes, start by
re-expressing `Rect` relative to a centre.

### 7. Rounding: checked, and fine

- **`wishAlong` divides by `isqrt` rounded down,** so a wish is very
  slightly longer than asked: by a factor of at most 1 + 1/l, where l is
  the distance in 256ths. Critters never come closer than about 40 px
  (10,240 256ths), so the error is under 0.01%. Coinciding centres go east,
  as specified.
- **Truncation toward zero is symmetric,** so mirror images of a scene get
  mirror-image wishes, exactly. That is worth a test (below).
- **At 7.5 px a second, the dog's step (0.47 px a tick) is smaller than the
  1 px dead zone.** So a dog moves only when its wishes total at least
  1 px, and then by at most 0.47 px. That is coherent. It is the doc's "the
  first branch never runs", still true.
- **The cows' rule now runs per pixel.** Halving a step that is not a
  whole 256th loses half a 256th each time: under 0.2 px over a 100 px
  drag. Negligible.
- **Ticks cross into the wasm as `f64`.** That is exact up to 2⁵³, which at
  16 a second is about 18 million years.
- **The page's pointer carries the fraction of a 256th** it did not send,
  so a drag never drifts. The edge band's push rounds without carrying.
  That is a tiny inconsistency, harmless, but it should match the pointer.

### 8. The doc's derivation of the region is stale

PHYSICS.md derives the region from the rules' reaches: 890 px, rounded up
to 1000. Since tonight, three things in that derivation changed:
- dogs can move up to 200 px in a tick (pixel-ticks);
- the scare box is 280 px;
- the sphere is 800 px.

I widened the region to 1500 by judgment, not by redoing the table. It has
room to spare: about 1000 px of reach plus a 20 px half-square. But the
table should be redone, because the doc says every reach is tuned against
it.

## Unit-testing themes

Each theme is a property, so it survives the next tuning.

1. **Mirror and rotation symmetry of the wishes.** Reflect a random scene
   across x, across y, or both, or rotate it 90°. A dog's wish total
   should reflect or rotate exactly, because truncation toward zero and
   `isqrt` of the same squared length are symmetric. The cascade's order
   and the x-then-y sweep are not symmetric, so test the wishes, not the
   whole tick. This one property checks most of the arithmetic.
2. **Arithmetic bounds:**
   - `isqrt(v)²` ≤ v < (`isqrt(v)` + 1)², up to the largest squared length
     the world allows;
   - `wishAlong` lies within [length, length × (1 + 1/l)] and points the
     right way;
   - `stepAtMost` never exceeds its limit and is zero inside the dead zone;
   - `delta(a, b) = −delta(b, a)`.
3. **Invariants after every tick,** fuzzed over random drags in a crowded
   park:
   - no two seen critters overlap;
   - every square is in the world;
   - asleep critters never move;
   - a cow moves only across the dog's axis of travel (apart from a
     push's jump);
   - **the pixel-tick bound:** no awake dog moves farther than the leashed
     dog's Manhattan move this tick, plus the tick's own step, plus a jump.
4. **Behaviour as properties, stated in the knobs:**
   - a lone dog of another breed inside `wary` ends the tick farther away;
   - in a long straight drag, a follower of the same breed stays within
     `band_outer` of its anchor, plus a small slack (it keeps pace);
   - a cow in the lane is clear of the lane before the dog arrives.
5. **Tuning-proof tests.** Compile the property suite a second time with
   every knob changed by ±50% (a build option, `-Dknobs=alt`). A test that
   fails only under the other knobs has pinned a number. This makes your
   "don't pin the knobs" rule something a machine checks.
6. **Frames at their edges:**
   - wire hex ↔ `i32` round trips at 0, 255, 256, a tile's edge and the
     world's edge;
   - `tileOf` and the half-open `TileSpan` at exact multiples of the tile;
   - the region's tiles plus a large display's tiles never exceed
     `most_subscribed`;
   - the pointer's carried fraction: a thousand random sub-pixel moves add
     up to the total, within one 256th.
7. **Agreement across targets, kept small:** the native and wasm builds
   give the same lines for the same session. And one corpus test: a real
   session from tonight's logs, replayed under its own physics hash, must
   reproduce exactly. That tests the log, the snapshot and the judge on
   real play, not invented play.
8. **Cost as a count, not a clock:** pair checks per tick, bounded by a
   multiple of (awake dogs × neighbours). Deterministic, fast, and it
   would have caught finding 4 the moment pixel-ticks landed.

## What I'd do first

When Dog Park resumes, I'd do findings 3 and 4 first: the snap is visible
now, and the cost decides how big the park can grow. Then 1 and 2, since
they make the knobs your language and remove two frames. The test themes go
to whichever agent next touches the tests, starting with 5, the tuning-proof
build, because it enforces the rule you set tonight.
