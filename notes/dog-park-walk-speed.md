# How the walk got four times faster

*2026-10-15. CC's QUEUE 210, dog-park `aa5dee1`..`9130db4`, live on :9103.*

The busiest drag in the park used to cost about 25 ms of a 62.5 ms tick
on this box. It now costs about 6–9 ms. In the browser a tick went from
1.1 ms to 0.24 ms. Not one line the physics writes changed. This essay
explains how, and what it suggests for the rest of Dog Park.

## Where the time went

A cold agent profiled the busiest spot, where the physics sees 270
critters:

- **42%:** each critter the walk visits looks for its 3 nearest
  neighbours (`lineUp`). It did that by measuring the distance to **every**
  critter the physics sees.
- **42%:** every step checks whether the critter would overlap anyone
  (`stepWhole`, `sweep`). That also meant checking **every** critter.
- **Under 6%:** all the poop code. The poops were already grouped by tile.

The cost was simple arithmetic. A full drag is about 200 pixel-ticks. In
each, up to 40 critters move, and each one compared itself against all
270 others, twice. That is about 2 million distance checks per tick, and
almost all of them were against critters a whole park away.

## The fix: a grid of cells

CC cut each 500 px tile into four 250 px cells. Each cell keeps a
**bitset**: one bit per seen critter, set if the critter stands in that
cell. Every move updates it (`Scene.put`), including shoves and
crossings of the world's seam. A critter outside the region the physics
sees goes in one extra set that every query includes.

A question like "who could my square overlap?" now asks only the cells
the square could reach (`Scene.critters`). It ORs their bitsets together
and walks the set bits. That is usually one to four cells, a dozen
critters instead of 270.

CC also measured the cell size. A whole tile per cell was slower (too
many critters per cell), and so were 4 cells a side (too many cells to
OR). Two a side won.

## The subtle part: order

The physics is deterministic, and the page and server must agree to the
bit. The old code checked critters **in index order**, and that order
mattered:

- which kin gets nudged first;
- which chicken gets shoved;
- which blocker steers a sidestep.

A typical spatial index (a quadtree, a hash grid with lists) hands back
neighbours in whatever order it stores them, and that would have
silently changed the game.

Bitsets avoid this for free. Walking the set bits of the OR goes in
**index order**, the same order the full scan took, just with the far
critters skipped. That is why the change could promise "no line
changes" and keep it.

## Nearest neighbours, ring by ring

For `lineUp`'s "3 nearest", CC searches outward from the critter's own
cell, one **ring** of cells at a time.

- A critter in ring *r* is more than (*r* − 1) × 250 px away.
- So once 3 candidates are found, and the farthest of them is no farther
  than that, no later ring can hold anyone nearer, and the search stops.
- Since candidates now arrive in ring order rather than index order,
  ties compare by **(distance, index)** explicitly.

That keeps the old tie-breaking, which used to come implicitly from the
scan order. CC turned a rule the old code obeyed by accident into a rule
it states.

## The smaller win: poop lines

Each tick used to copy all 2,048 poop slots (positions and states), run
the tick, and diff all 2,048 to find which poop lines to write.

Now the scene remembers which slots it saw at the start, and the old
point of any of them a new poop overwrites. It walks only those slots
plus the ones laid this tick. A page tick dropped from about 270 µs to
235 µs.

## The proof that nothing changed

This is the best part of the work, and the part to copy.

1. **A lines dump** (`zig build physics-bench -- lines`, new). It runs
   898 ticks:
   - every one of the 400 dogs leashed, with the full drag;
   - on the park as laid out, and moved across the seam;
   - 96 ticks of poop laid, eaten and reused;
   - the packed herd;
   - the server's re-run.

   All 106,298 lines were byte-identical before and after.
2. **A differential cold review.** A separate agent ran the old physics
   and the new side by side on about 94,000 ticks of nasty boards: the
   seam, the region's edges, points exactly on cell boundaries, ties on a
   20 px grid, up to 2,048 poops, the `laid` counter near its wrap. It
   compared every line and the whole board, and found no difference. It
   also planted four mutations, and each was caught within 31 boards.
3. **An invariant in the tests:** `bucketsHold()` runs after every
   pixel-tick and every chicken's turn. It checks that each critter's bit
   is in exactly its own cell. A planted shove that forgets to move its
   bit fails it.
4. **A test fixed that had proven nothing.** The slot-reuse test never
   checked the reused slot's line, so a planted bug (`was = at`) passed
   every test. CC added the check first and saw it fail.

A rewrite of the core with no behaviour change is exactly when "the tests
pass" means least. The lines dump and the differential run mean a lot.

## The numbers

| | before | after |
|---|---|---|
| busiest spot, full drag (native) | 18.9 ms (CC) / ~25 ms (box) | ~5.9 ms (CC) / ~9 ms (box, busy) |
| 500 poops in view, full drag | 19.6 ms | ~7.0 ms |
| packed herd, full drag | 9.2 ms | ~6.3 ms |
| server re-run of 8 ticks | 22.9 ms | ~8.0 ms |
| a page tick (wasm under node) | 1.10 ms | 0.24 ms |
| a 32-tick replay (wasm) | 35 ms | 8.0 ms |

The packed herd gains least: with dogs 45 px apart, every cell is full.

## Lessons for the rest of Dog Park

**1. The physics now has two spatial indexes. Make it one.**
- Poops by tile are linked lists of slots, with "listed" bits.
- Critters by cell are bitsets, walked in index order.

Two structures do the same job: "who is near this square?". By "an
abstraction earns its keep on the second user", this is the second user.
- One `Grid` (cells, bitsets, the outside set, `near(p, reach)` in index
  order) could serve both.
- A poop set is 2,048 bits, so a poop grid would cost about 50 KB a
  scene. Measure it.
- The win isn't speed, which poops already have. It's one mechanism to
  understand, one invariant (`bucketsHold`) to check, and one place where
  "in index order" is guaranteed.

**2. The server's invariant check is still quadratic.**
- `physics.overlaps` compares every pair of seen critters: about 36,000
  checks, after every tick the server re-runs (`physics_judge.zig` ~434).
- It also builds a whole second `Scene` from scratch to do it.
- The seeded invariant test runs the same check after every tick of its
  drag, in Debug. That is a likely reason the fast test tier grew from
  6 s to 12 s.
- With the grid, each critter checks only its own and neighbouring cells,
  and the check can reuse the tick's scene instead of building another.

**3. A full scan is the smell; "a scan in index order" is what to keep.**
- The pattern to look for: a loop over every critter, or every slot,
  inside a loop over moves. The ones left:
  - `chickensTurn` walks every seen critter to find the chickens;
  - `onPoops` checks every critter against the poops;
  - `Scene.init` rebuilds everything each tick (fine: once a tick).
- Each should either ask the grid or say why a full scan is right.
- In every case, keep the order and make tie-breaks explicit.

**4. Every speed change ships with the lines dump.**
- `physics-bench -- lines` is now the standard proof that a refactor
  changed nothing.
- It's a tool, not a test. It would break on every retune, and Steve
  retunes by playing. But any change claimed "behaviour-neutral" should
  quote it: identical before and after.

**5. Make the fast tier fast again.** After lessons 1–3, re-measure
`zig build test` and attribute its time. The README says ~12 s today. We
want to stay nimble while the game is still changing.

These go to CC as QUEUE 212.
