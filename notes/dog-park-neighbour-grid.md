# Dog Park's neighbour grid, and where it should live

*2026-10-19. How the data structure that finds a critter's neighbours
works, and what two cold agents found trying the two homes you asked
about: Roc, with a 20% slowdown allowed, or a better-packaged Zig.*

## How it works

**The world** is a torus of 6 × 6 tiles, each 350 pixels a side. Positions
are integers in 256ths of a pixel. The park holds 64 dogs, 8 cows and 16
chickens, 88 critters in all. Each tick the physics numbers the critters
it can see, 0 to 87; that number is the *seen index*.

**The grid** cuts each tile in two both ways, giving 12 × 12 = 144 cells,
each 175 pixels a side. A cell holds a **bitset over the seen indexes**:
bit `j` is set if critter `j` stands in that cell. At 88 critters, that's
two 64-bit words a cell, 288 words for the whole grid, about 2.3 KB.

Three operations use it:

- **Move.** When a critter steps, its cell is worked out from its point
  (`cellOf`: divide by the cell size, after wrapping). If the cell
  changed, its bit is cleared in the old cell and set in the new one. Most
  steps stay in the same cell and cost nothing.
- **Who might I touch?** To find everyone within `reach` of a point, take
  the cells a square of that reach overlaps, wrapping round the torus edges
  (`Wrapped`), and OR their bitsets together. The result is a superset:
  everyone actually close, plus some who merely share a cell. The caller
  checks the real distance.
- **Who are my three nearest?** The walk lines up each critter's three
  nearest dogs and cows. That search goes **ring by ring**: first the
  critter's own cell, then the eight around it, then the sixteen around
  those, and so on. It stops once it has three and the third is closer
  than anything the next ring could hold.

**Why bitsets and not lists:** iterating a bitset visits critters in
seen-index order, whatever cell order they were found in. That order
decides who gets nudged, shoved or blocked first. So the grid finds
neighbours fast, and the result is the same as if every critter were
scanned in index order. That's what keeps the 14,800 lines byte-identical
whatever the grid does.

**The poops** have a sibling index: a linked list per tile, kept by Zig.
It's lent to Roc flattened, sorted by tile (a counting sort: count per
tile, prefix sums, fill), with a `from` table of where each tile's poops
start.

## Where it lives today

**There are two copies.**

- **Zig's** (`Scene.seen_cells` in physics.zig) is the authoritative one.
  It's kept by `put` on every move.
- **Roc's** (`Park.cells` in Walk.roc, a flat `List(U64)`) is rebuilt from
  Zig's on every pixel-tick: cleared, then one bit per critter. Roc then
  keeps it up to date during the walk and does the ring search on it.

Both agents noticed the same thing. **Since 239 and 240, nothing in Zig
asks Zig's grid a question.** `Scene.critters()`, the "who might I touch"
query, has no callers. Zig keeps its grid only to rebuild Roc's from it,
and to check it in the tests (`bucketsHold`). Zig is a bookkeeper whose
books only Roc reads.

## Option 2, packaged in Zig: done, green, no speed change

Branch `box/neighbours-in-zig`.

- **A module of its own:** `src/play/grid.zig`, a generic grid on a torus.
  It's generic over capacity, cell size and side, knows nothing of dogs or
  poops, and has its own tests.
  - Operations: `add`, `move`, `near` (the square query), `holds` (the
    invariant) and `cellOf`.
  - `Scene` uses it, and the dead `critters()` and `SeenSet` are gone.
- **The rebuild is gone.** The grid stores its cells in exactly the
  memory Roc is lent, so Zig keeps the grid and Roc reads and changes the
  same words in place. No more clearing and refilling every pixel-tick.
- **All the judges pass,** the 14,800 lines byte-identical included.
- **Speed:** unchanged within noise on all six bench workloads. The
  rebuild it removed was 2.3 KB of clearing plus 88 bit-sets, which is
  nothing next to a 6-12 ms tick.

**One trap it found:** the grid's words had to be made 64-bit on purpose.
Zig's standard bitset uses 32-bit words on wasm32, so its layout matched
Roc's `List(U64)` only because the sizes happened to work out. With the
storage shared, that's now a type, not a coincidence.

**Its recommendation:** take it.

## Option 1, owned by Roc: the design holds, the build doesn't (yet)

Branch `box/neighbours-in-roc`, one commit marked WIP and red.

**What it tried:**
- Zig lends the critters once a tick, not once a pixel-tick.
- A new mode of the one export, `settle`, files every critter into its
  cell.
- From then on only Roc touches the grid. Zig's grid is deleted outright:
  `seen_cells`, the cell bookkeeping in `put`, and `critters()`.
- `bucketsHold` becomes a test-only check of Roc's grid against Zig's own
  `cellOf`.

**The overlap judge stays independent.** `overlaps` scans every pair and
never used the grid, so Zig's referee doesn't depend on Roc's bookkeeping.

**Where it stands:**
- `roc-test` passes, and `check` passes in Debug.
- **The release bench crashes** in `roc_alloc`. The host refuses to let
  Roc allocate, so this means some lent list got copied instead of updated
  in place. The agent ran out of time before finding which list.

### The challenges, which are the interesting part

**1. A separate Roc module seemed to cost a copy.** The agent wrote
`roc/Grid.roc`, a general bitset grid with its own tests. That's what
"general-purpose data structure in pure Roc" would look like. But calling
`Grid.move(cells, ...)` from Walk.roc copied the lent list (34 tests
crashed), and inlining the same code into Walk.roc made the copy go away.

I'd treat this as **a phenomenon, not yet a finding**. It might be a rule
of Roc's (uniqueness isn't proven across a module boundary), a bug in a
young compiler, or something about how the agent called it. But if it is
a rule, it matters for your stretch goal: a reusable Roc data structure
that can't be called without a copy is reusable only by copy and paste.

**Update, same day: it isn't a rule.** I built the smallest version
possible: a Zig host lends Roc one unique list, and Roc sets one bit three
ways.
- written inline;
- through a function in the same module;
- through `Grid.set_bit` in another module.

All three update the list in place, with no allocation, in both Debug
and ReleaseSafe. To check the probe can see a copy at all, I planted a
fourth way that keeps the old list alive after the set. That one
allocates and hands back a new list.

So a module boundary costs nothing. The agent's copy came from sharing
somewhere in its own code (challenge 2's trap, or a list carried in a
record), and **a reusable `Grid.roc` is possible.**

**2. Uniqueness is fragile in ordinary-looking code.**
`var $crits = crits0` followed by reading `crits0.len()` leaves two names
for one list. The next `set` then copies it. Nothing in the source looks
wrong; you have to know.

This is ROC-SPEED.md's rule ("one variable owns each list") biting again.
In Zig the equivalent mistake is impossible, because there's only one
pointer.

**3. Lists that live across calls are a new kind of risk.** Today every
list Roc gets is lent fresh, used, and handed back in one call. If Roc
owns the grid, the same list goes out and comes back many times a tick.
The release-only crash looks like it lives there: the Debug build
passes, which suggests the optimizer changes what counts as "still
shared."

**4. The host turns a slowdown into a crash.** That's a good property.
Because Dog Park's `roc_alloc` panics, a lost in-place update fails
loudly. On a normal platform it would just be a quiet copy of 2.3 KB per
move, and the bench might never show it. It's the "fail, never warn"
doctrine, enforced by the platform.

**Its recommendation:** the design is right, and Zig really can hold no
grid at all. But don't go further until a minimal ReleaseSafe
reproduction shows whether a list mutated across a module call can stay in
place. If it can't, the grid stays written inline in Walk.roc, and
"Grid as its own Roc module" waits on Roc.

## Comparing them

| | Zig, packaged | Roc, owning |
|---|---|---|
| State | green, pushed | red in release |
| Copies of the grid | one, shared memory | one, Roc's |
| Rebuild per pixel-tick | gone | gone |
| Speed | same | not measurable yet |
| Reusable piece | `grid.zig`, generic | `Grid.roc`, blocked by the copy |
| Zig knows about cells | yes, via a small module | only `cellOf`, in a test |

They aren't really rivals. **The Zig option is the safe first step toward
the Roc one.** Once the storage is shared, "Roc owns the grid" means
deleting `add`/`move` calls from the Zig side and having Roc do them.
The memory, the layout and the invariant check stay where they are.

Speed won't decide this either way. The thing being optimized away was
already invisible. What's at stake is the seams you asked to keep clean,
and whether Roc can host a reusable data structure at all.

## A side finding: two ways to name a poop's tile

`Scene.headOf` files a poop under its tile *counted from the span's first
tile*; `Scene.near` reads tiles *counted from the world's origin*. Those
disagree whenever the span doesn't start at tile 0. Today it always
does: `region` returns the whole world, so the offset is 0 and nothing is
wrong. But it's a latent bug held off by a constant, the sort of thing
"make state honest" says to remove. Putting the poops on the same grid
module would remove it.

## What I'd do next

1. **Take the Zig packaging.** Rebase `box/neighbours-in-zig` onto
   today's main (it predates the Roc reformat, but touches only Zig),
   re-judge, and merge.
2. **Fold the poop index's tile naming** into one, via the grid module or
   just `headOf`.
3. **Pin down the Roc copy** with a tiny reproduction. *Done (see the
   update above):* a call into another module does not copy. Nothing to
   ask upstream yet. The release-only crash on the Roc branch is a
   sharing bug in that branch, still to be found.
4. **Only then** let Roc own the grid. Steps 1 and 3 make that a small
   change.

## Questions for you

- **Is "Roc owns its bookkeeping" a goal for its own sake,** or a means to
  "new kinds of critters in Roc alone"? 240 already got the second without
  the first. If it's the means, the shared-storage Zig grid may be where
  this settles for a long while.
- ~~Would you want the Roc copy question asked upstream?~~ The
  reproduction says there's nothing to ask.
