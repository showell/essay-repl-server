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


## Your answers (2026-10-14), and what they change

- **Rank order is a misfeature.** Dogs sometimes look paralysed by a
  pecking order you can't see, instead of just reacting to the dog beside
  them. CC may relax it. What must survive: **a chain still follows the
  leashed dog,** rather than everyone clumping into one mass.
- **A packed crowd isn't a real problem for B.** Breeds repel, so a crowd
  loosens until a dog drifts toward its own kind. And herds *shouldn't*
  form on their own: **the leashed dog is the catalyst.** What matters
  most is that **a herd, once formed, is fairly stable.**
- **Try Chebyshev** (Option C).
- **Hidden physics is bad game design** unless the player has a fair way
  to discover it. Today nothing on screen says which dog is more alpha,
  yet rank decides who follows whom and who yields to whom.
- **Measure the herds.** You can spot them on the page at a glance, but
  there's no number for them yet.

## What a herd is, as a number

A proposal for CC to refine:
- **The herd graph:** join two dogs of the same breed when their centres
  are within the herd band's outer edge plus a little slack (say 120 px,
  against the band's 100). A **herd** is a connected group of that graph
  with at least three dogs.
- **What to measure:**
  - **Herds per breed** in the awake area. The goal is about one each:
    four distinct herds.
  - **A herd's size** (dogs) and its **length:** the most hops between
    two of its dogs along the graph (its diameter).
  - **Chain or clump:** the average number of same-breed neighbours per
    dog. A chain is about 2; a clump is 4 or more. Length divided by size
    says the same: near 1 is a chain, small is a clump.
  - **Stability:** after the human lets go, how much of each herd's
    membership is the same 10 and 30 seconds later. Herds that come apart
    on their own fail this.
  - **Catalysed, not organic:** the same measures on a park nobody has
    touched for a minute should show few or no herds.
- **How to use it:** a few fixed play scripts (recorded drags: gather
  breed 0 along a line, swing it round, let go). Run each script under
  every variant below, and report the numbers, so a rule change is judged
  on the same play every time and not only by eye. Your eye stays the
  final judge.

## A progression toward B

Each step is one build knob, measured with the herd numbers and played on
:9103 before the next. Each can be kept or thrown away alone.

1. **The herd numbers and the play scripts,** on today's physics. This is
   the baseline every later step is compared with.
2. **Chebyshev distance** (`-Dmetric`): squares instead of circles, no
   roots. Measure, then you play it.
3. **Everyone thinks at once.** Each pixel-tick, every awake dog works out
   its wish from the same snapshot, and only then do they move. Rank
   survives only as the tie-break for who yields when two would step into
   each other, which is invisible and harmless. This removes the
   paralysis: a dog reacts to its neighbour, not to its neighbour's rank.
   It needs watching for back-and-forth jitter, which the 1 px dead zone
   should damp.
4. **Follow upstream, not up the ranks.** A dog's anchor becomes the
   nearest dog of its breed that is **closer to the herd's head along
   the herd**, instead of the nearest more-alpha one.
   - **The head is the dog you last leashed in that herd.** That's
     visible, and you made it so. While leashed, the leashed dog is the
     head.
   - Chains still point at the leashed dog, because every link follows a
     dog nearer the front.
   - Herds stay stable, because a dog keeps its anchor until another is
     clearly better: nearer by a margin, say 20 px. That stops anchors
     flickering.
   - **Discoverable:** the head could wear a small mark, a collar or a
     ring, so the player sees which dog leads each herd. Then rank is
     gone from the rules entirely.
5. **Bounded attention (B itself).** A dog heeds:
   - its anchor;
   - its **nearest few strangers** (say 3) within the wary distance,
     instead of all of them;
   - its **nearest cow.**

   Measure whether herds hold together better in a crowd, and play it.
   Your point stands that a crowd loosens anyway, so this step may turn
   out unnecessary. The herd numbers will say.
6. **Then the speed pass (Option A):** only dogs whose neighbourhood
   changed re-think. It's done last because steps 2-5 change what "a
   neighbourhood changed" means, and the exactness test only proves a
   speed-up against rules that have stopped moving.

**What stays true throughout:**
- **The tests still state properties:**
  - no overlaps;
  - symmetry and translation;
  - page and server agree to the bit;
  - `-Dknobs=alt`.
- **The reference changes deliberately:** each step that changes the
  rules updates `physics_reference.zig` in the same commit, and the
  physics hash moves with it.
