# Dog Park's tests, and how fast they run

*2026-10-14, at dog-park `db5c908` (the one-move step, decision 18).*

You asked for this after the test review: tests should be fast, and a slow
test needs a load-bearing reason. The goal is to stay nimble while the
game's design is still moving. Every number below was measured on the box
with nothing else computing: v30's gates had just finished, and no agent
was running. The run used a fresh clone and an empty Zig cache. The box
has 2 cores.

## The short version

| what you do | wall time |
|---|---|
| edit `engine.js` or another page file, then `zig build test` | **4.9 s** |
| edit `physics.zig`, then `zig build test` | **9.3 s**, now **6.6 s** (see below) |
| edit `physics.zig`, then `zig build check` (before a commit) | **18 s** |
| `zig build test` with nothing changed | 4.7 s |
| `zig build test` from an empty cache | 19 s |
| `zig build slow` (before calling a physics change done) | **100 s** |

A tuning change, like "make the dogs 50% slower", takes a one-line edit,
9 seconds of tests and a redeploy. That's the loop we've been running all
day, and it's fast enough not to get in the way.

## The three tiers

**`test`: after every edit.** It runs every Zig unit test natively in
Debug (113 tests, the fuzz loops at a tenth of their size) and the node
tests that need no server: the page's modules and the engine.
- The test run itself takes 3 s.
- The rest of the 9 s after a physics edit is compiling, and the biggest
  piece of that is the page's wasm (4 s, ReleaseSafe). The server tests
  embed the wasm the page gets, so they need it built.

**`check`: before a commit.** `test`, plus:
- the physics tests compiled to wasm32 and run under node (6 s to compile,
  3 s to run). This is how we know the page's arithmetic gives the
  server's answers;
- the node tests against a scratch server on tmpfs: the page driving the
  real physics, and the report route end to end.

**`slow`: before calling a physics change done.** Three things run side
by side, so on 2 cores the wall time is less than their sum:

| what | why it's slow | time |
|---|---|---|
| the identity test: today's physics against `physics_reference.zig` over long seeded sessions | it **proves an optimisation exact**. The neighbour lists, the wishes' grid and the one-move step's early exits all claim to change no outcome, and this is the only test that would catch one that does | 48 s |
| every unit test with the full fuzz | ten times the fast tier's random scenes | 34 s |
| the physics tests under `-Dknobs=alt` (every knob moved by about half), full fuzz | catches a test that pins your current tuning instead of stating a property | 26 s |
| the physics tests compiled to wasm32 in ReleaseSafe, as served, and run under node | the page runs ReleaseSafe; Debug wasm alone could hide an optimiser difference | 9 s compile, 9 s run |

Each of those has a load-bearing reason, and none of them is in the
edit loop.

## What the tests hold

These are properties, not pinned numbers, so that tuning by playing doesn't
break them:
- **Determinism and agreement.** The page and the server run the same
  compiled physics, and the server re-runs every report and acks it. The
  wasm tests and the scratch-server tests hold that.
- **No two critters share space.** This is checked after every tick in
  the fuzz, through drags into packed herds.
- **Symmetry (new today).** A scene mirrored, transposed or turned a
  quarter plays out exactly mirrored, transposed or turned. The only
  exceptions are the named tie-breaks: a cow on the dog's line goes to its
  right, and a jump tries east first. The symmetry tests found the x-then-y
  step, which is what decision 18 fixed.
- **Tuning-proof (new today).** `-Dknobs=alt` runs the physics tests with
  every knob moved by about half. The relations a retune must keep are
  compile errors now, listed in PHYSICS.md under "What a retune must keep":
  the region outreaches the rules, a cow's room is more than touching, the
  wishes' grid fits, and the scare box spans two lanes.
- **The worked example** in PHYSICS.md is a byte-for-byte golden of your
  tuning. It's the one deliberate exception to "properties, not pins". It
  skips under alt, by name.

## What could make the loop faster, if it ever matters

- **The page's wasm in the edit loop: DONE (Steve asked).** `test` now
  builds and uses a Debug wasm (`zig-out/web-debug`, about 1 s to compile
  against 2.5 s); `check`, `slow` and the server keep the served
  ReleaseSafe build. The physics edit loop went from 9.3 s to 6.6 s,
  measured with another agent building alongside (dog-park `6843e26`).
- **`slow` in ReleaseSafe natively.** The identity test and the full fuzz
  run in Debug, and they would probably run several times faster in
  ReleaseSafe, at the cost of a few seconds more compile. I'd try it if
  `slow` starts to feel like a wait. Today you rarely run it yourself.

## How this compares with the kernel

The same day, v30's gates failed only because tier 0's three biggest test
binaries took 52–60 s each against a 45 s budget, on the same 2 cores.
That's one binary of the kernel's fastest tier taking about as long as
Dog Park's whole slowest one.

That isn't a criticism of the kernel. It's a judge of a real disk under
faults, and that costs time. But it is why Dog Park is cheap to change:
its fast tier is under 10 seconds, so trying a new rule costs less than
arguing about it.
