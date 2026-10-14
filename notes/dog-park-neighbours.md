# Dog Park: who a critter needs to know about

*2026-10-14, at dog-park `a8a9935` (the torus and CC's 202 speed-up, live
on :9103).*

You asked for options on two ideas:
- a structure built around each critter's nearest neighbours, so the
  cascade after a leash pull propagates cheaply;
- distances in Manhattan instead of straight lines.

You also asked whether the first is a quadtree.

## The short answer

- **It isn't a quadtree.** What you describe is a *nearest-neighbour graph*
  kept up to date as critters move. The physics already does half of it:
  each critter keeps a list of who is near it, rebuilt only when someone
  has moved far enough to matter.
- **The half it doesn't do is the interesting part:** using that graph to
  decide *who needs to think at all*. Today every awake dog re-thinks after
  every pixel of a drag, whether anything near it changed or not.
- **Manhattan distance would change how the park looks more than how fast
  it runs.** Squared distances are already cheap. The real win is a
  simpler, root-free physics, and there is a cousin of Manhattan that fits
  square critters better.
- **Speed isn't urgent right now.** After CC's work, the worst drag
  through the packed herd costs about 9 ms in the page, against a 62.5 ms
  tick. So these options are mostly about shape and simplicity, with speed
  as a bonus, and the first step is a measurement.

## What a quadtree is, and what you proposed

A **quadtree** answers "who is near this point?" by cutting the world into
four squares, cutting each crowded square into four again, and so on. A
search walks down only the squares that could hold an answer. It shines
when crowding varies wildly: a few dense clumps in a mostly empty world, at
every scale.

Dog Park doesn't need that. Every rule has a fixed, short reach (wary
225 px, follow 600 px, the scare box 280 px). Critters also never get
denser than touching. For that, a **flat grid** of equal squares is simpler
and faster than a tree, and it's what the physics uses: a 250 px grid for
the wishes and a finer one for contact.

What you proposed is different. Each critter remembers its **k nearest
critters** (you said 4). When one moves, its neighbours ask their
neighbours to repair their lists. That's a *k-nearest-neighbour graph,
maintained locally*.

**What the physics keeps today** is close to that, but by distance, not
by count. Each critter has a list of everyone within a margin of touching
(the "skin", 48 px), and a list of everyone within its rules' reach. The
lists are rebuilt only when someone has drifted more than the margin
allows, about four times in a heavy drag tick. So "remember who's near,
and refresh lazily" is already there.

## Option A: think only when your neighbourhood changed (same physics)

**The idea.** A dog that is content (every wish satisfied, so it rests)
stays content until something within its reach moves. The graph already
knows who is within its reach. So instead of every awake dog wishing after
every pixel of a drag (61 passes over the herd in the heaviest tick),
keep a **to-do set**:
- the dogs near anything that moved in this step;
- the dogs whose wish wasn't satisfied last step.

Only they think. A dog that moves puts its neighbours on the to-do list
for the next step. That's your "propagate the motion cascade" exactly. A
pull ripples outward through the graph, and a herd far down the chain
costs nothing until the ripple reaches it.

**Why it's attractive:**
- **The physics doesn't change at all,** so exactness is cheap to prove:
  the identity test against `physics_reference.zig` holds as is, and so do
  the symmetry and translation tests.
- **Resting dogs cost nothing,** and in a packed herd most dogs rest
  through most pixel-ticks.

**The catches:**
- **Order matters.** Dogs think in rank order and each sees the others
  above it already moved. The to-do set has to be walked in rank order
  too, not in ripple order. That's easy with a bitset by rank.
- **"Content" must be exact.** A dog skipped because nothing near it moved
  must be one that *would* have stayed put. That holds if every input to
  its wish (the positions within its reach, and the step limit) is
  unchanged. The step limit changes every pixel-tick, so that needs care: a
  dog with an unmet wish is always on the to-do list.

**What it buys is unknown until measured:** how many of today's wish
evaluations end in no move at all. If it's 80%, this option could cut the
herd drag several-fold. If it's 30%, it isn't worth the bookkeeping. **The
first step is that one number,** and it's cheap to get.

## Option B: a dog sees only its nearest few (new physics)

**The idea.** Change the rules themselves to your graph. A dog reacts only
to:
- its **nearest few strangers** (say 3), instead of every stranger within
  225 px;
- its **anchor**, the nearest more-alpha dog of its breed, as today;
- its **nearest cow**.

Everything is bounded by count instead of by distance, so each dog's
thinking costs the same whatever the crowd.

**How it would feel.**
- **Herds:** a dog in a crowd ignores most of it, so herds would push
  through each other more easily and form longer, cleaner chains.
- **Cows:** the leashed dog's scare box stays as it is, so the cows'
  getting out of the way doesn't change.

That fits "four distinct herds that form chains", but it's a guess until
you play it.

**The catches:**
- **The nearest k overall isn't enough.** A dog in a packed crowd of other
  breeds might have no dog of its own breed among its 4 nearest. Then it
  loses its anchor and its herd. The graph needs a list per role:
  - k nearest strangers;
  - the anchor;
  - the nearest cow.

  Each comes from the grid, with a reach cap so nothing is ever far away.
- **Repairing by asking neighbours of neighbours can miss a newcomer.** A
  cow walking in from outside isn't anyone's neighbour yet. So the repair
  still has to look at the grid squares around a dog, not only at its
  friends' lists. The grid stays; the graph sits on top of it.
- **Ties need a fixed order** (the nearer, then the lower rank), so the
  page and the server agree to the bit. That's no different from the
  anchor rule today.
- **It's a new physics:** a new reference, a re-tune by playing, and the
  worked example rewritten. The tests (symmetry, translation, no overlaps,
  alt knobs) carry over unchanged, because they state properties.

## Option C: a different distance

You suggested Manhattan: |dx| + |dy|. There's a cousin worth putting
beside it, **Chebyshev**: the larger of |dx| and |dy|.
- **The current physics:**
  - **Distance:** straight-line (Euclidean), compared squared, so no root
    is needed to compare.
  - **Cost:** the remaining cost is an integer square root, used to point
    a wish in the right direction and to cap a step at the speed. CC
    already made it cheap (202.9).
- **Manhattan:**
  - **What a "circle" looks like:** a diamond. Wary distance, herd bands
    and room around cows would all be diamonds.
  - **Movement:** a dog stepping "toward" something moves along whichever
    axis has more left to go, or both evenly. Herds would look slanted and
    diamond-shaped.
- **Chebyshev:**
  - **What a "circle" looks like:** a square, the same shape as the
    critters themselves. The overlap test is already Chebyshev.
  - **Movement:** a step is one pixel on each axis that needs it, eight
    directions. Herds would settle into squares and rows: a tidier, more
    board-game look.

**What either one changes:**
- **Speed:** modest, probably 10–25% of the wish cost, not several-fold.
  The squared comparisons are already as cheap as sums.
- **Simplicity:** large. There are no roots, and the long proofs that the
  integer arithmetic is exact (202.9, 202.20, 202.22) go away. Every
  step's length is a whole number of 256ths.
- **Look:** that's the real question. Eight-direction movement can look
  mechanical. On the other hand, the park is already a checkerboard of
  square tiles with square critters, and Chebyshev might feel at home in
  it.

**How to find out:** a build-time knob, `-Dmetric=euclid|chebyshev|manhattan`,
so you can play each on :9103 side by side. The property tests already
hold under any of the three. The symmetry tests, for one, hold because all
three distances look the same mirrored or turned.

## What I'd hand to CC

1. **Measure first:** in the packed-herd drag, the share of wish
   evaluations that end in no move, and how many dogs a ripple actually
   reaches per pixel-tick. That's one bench run and decides whether
   Option A pays.
2. **If it pays, Option A:** the to-do set walked in rank order, on top
   of today's lists. It must stay exact, so the identity test holds
   unchanged. It's the pure speed option.
3. **The metric knob (Option C)** as a build option, for you to play.
   Chebyshev first, since it matches the squares.
4. **Option B only after you've played C,** because B is the biggest
   change to how herds behave and the hardest to undo. We could also try a
   small version of it first: a cap on how many strangers a dog heeds,
   without changing anything else, as one more knob.

**What I need from you:** which of these to send to CC. My pick is 1 and
2 as one item, and 3 as a second, with B waiting on how the park feels
under Chebyshev.
