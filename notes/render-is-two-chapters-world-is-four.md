# Render is two chapters, World is four, and TruckBody is one

The instrument that found Camera's seam is **silent** on the two chapters most
obviously worth splitting:

    port/Render.codex   defs 111 ( 89 fn)  edges 158  components  4  SPLIT
    port/World.codex    defs  73 ( 30 fn)  edges  98  components  3  SPLIT

Those "SPLIT" marks are almost nothing. Render's four components are 108
definitions, one constant, one constant, and one stray index. World's three are
69, two, and two. Take away the leaves and each is a single connected blob.

That is not a failure of the tool. It is the answer to the question it asks,
and the question turns out to be the wrong one at this size. **A big chapter is
rarely two programs. It is one program with seams in it.** Camera was
genuinely two programs sharing a file, which is why counting components found
it in one pass; nothing about Render is disconnected.

So the seam needs a definition that does not depend on disconnection.

## The definition

Root the chapter's call graph at **what other chapters read** — the real
interface, which the cross-chapter index now knows — and take the dominator
tree. A definition `f` dominates the set of definitions reachable only through
`f`. Peel that set off and you have cut exactly one edge, by construction. You
do not search for a small cut; you read it off.

Two details that matter. Mutual recursion is atomic, so strongly connected
components are condensed first — two functions that call each other cannot be
separated, and saying so is more useful than pretending. And getting the roots
wrong in the obvious way, by rooting at every definition, makes every node
dominate only itself and reports nothing at all.

## World: seventy-three definitions behind four names

```
World (port/World.codex)
  73 definitions, 98 internal calls

  INTERFACE — read by another chapter (4):
      gaze-pig  build-world  course-length  route-distance

  MUTUALLY RECURSIVE — inseparable (2 groups):
      [2] fill-trees fill-trees-pair
      [2] next-tree-loop next-tree-step
```

Four exported names. The first thing the instrument says about "World is doing
WAY too much" is that from the outside it is doing almost nothing — the entire
chapter is an implementation behind a four-name façade.

Then the top seams, which are a chain rather than a split:

```
    build-world    owns 62
    segments-from  owns 61
    segment-at     owns 58
```

Nested, each inside the last. That is a funnel — one pipeline, three
storeys — and it is why component-counting saw one blob. Cutting there would
just move the roof.

The real answer is further down, and it is clean:

```
    fill-cows      owns 16 — The Cow Herd
    fill-trees     owns 12 — Palette and Dimensions + Trees and Critters
    fill-pig-herd  owns 10 — The Pigs
    cows-from      owns  9 — The Cow Herd
    herd-rows-from owns  9 — The Pigs
    cow-at         owns  8 — The Cow Herd
```

Three sibling subtrees, each owned by one function, each aligned with a section
the author already drew:

- `fill-cows` and its 16 — the herd: `bull-cp`, `cow-cp`, `cow-height`,
  `calf-height`, `bull-height`, `bull-dist`, `bull-tree-gap`,
  `herd-gap-behind-bull`, `herd-col-spacing`, `herd-row-stagger`,
  `herd-row-depth`, `herd-jitter-along`, `herd-jitter-across`, `bull-of`,
  `cows-from`, `cow-at`.
- `fill-pig-herd` and its 10 — the pigs.
- `fill-trees` and its 12 — the trees.

**And `fill-trees` straddles two sections, which is the finding inside the
finding.** It owns `conifer-green`, `conifer-gold`, `conifer-red` — which live
under `Section: Palette and Dimensions`. Those three colours are reachable only
through the tree fill. So "Palette" is not a palette; it is the tree colours,
sitting under a heading that promises something broader and delivers three
conifers. A section that owns exactly one consumer's constants is a section
that wants to be inside that consumer.

World becomes: **Trees**, **Herd**, **Pigs**, **Route**, and a thin
`build-world` that assembles them and exposes four names. Not because the name
"World" is too grand, but because the graph has four disjoint subtrees under one
funnel and the section headings already named three of them.

## Render: two chapters, disjoint

```
Render (port/Render.codex)
  111 definitions, 158 internal calls

  INTERFACE — read by another chapter (10):
      build-chain  at  prev-map  map-pt  detail-dist  crown-shade-dist
      truck-items  deeper-than  collect  frame-ground

  No mutual recursion: every group below can be cut.

  SEAMS:
    collect       owns 67 — Collection Limits and Culls + Tower Placement +
                            The Crossing Cat + Placing Billboards + Harvesting
                            a Placement List + Collecting Trees + Collecting
                            Towers + Collecting Critters + Walking the Chain +
                            The Joint Just Behind + The Guard Rail Path +
                            The Chased Truck + The Depth Sort +
                            The Frame's Collection
    frame-ground  owns 24 — The Ground + The Road Strip + A Joint's Ground +
                            The Pond's Ground + Walking the Ground
```

**Sixty-seven and twenty-four, and the two sets do not overlap by a single
definition.** I checked that specifically, because two big dominators are only a
split if they are siblings rather than nested, and these are siblings:

    overlap = 0

That is Render, structurally, in one line: **what stands in the scene**, and
**what the scene stands on**. `collect` gathers the trees, towers, critters,
cats, guard rails and the chased truck, culls them, and depth-sorts them.
`frame-ground` paints the road strip, the junction pavement and the pond. They
share the chain and nothing else.

Below them the subtrees keep separating cleanly:

```
    all-placed        owns 17     the billboard placement pipeline
    all-towers        owns  9
    all-rails         owns  9     the whole guard-rail path
    walk-ground       owns  9
    seg-ground        owns  8
    walk-billboards   owns  7
    joint-rails       owns  6
    seg-road          owns  5
```

`all-rails owns 9 — The Guard Rail Path`, and the section is exactly the nine.
That one is a chapter already; it is just spelled as a heading.

## What this says about the night walk

The interesting question is not how Render splits — it is which parts survive
into a city at night, where there are no pigs and no guard rails but there is
still a route, a depth order and a ground.

**Render's exported interface is already the reusable half, and that is not a
coincidence.** Look at the ten names other chapters read:

```
build-chain  at  prev-map  map-pt     the chain: a walk along a route, and
                                      the mapping of a point along it
deeper-than                           the depth order
detail-dist  crown-shade-dist         distance thresholds
truck-items  collect  frame-ground    the safari
```

Five of those ten are scene-independent machinery. `build-chain`, `at`,
`prev-map` and `map-pt` know about a route and a rider and nothing about what
is standing beside the road. `deeper-than` is a comparator. A night walk needs
every one of them and needs none of `seg-cat`, `place-duck`, `tower-yaw` or
`rail-run-out`.

The other chapters were already voting for this. Definitions get exported when
somebody outside wants them, and the outside wanted the chain, the mapper and
the comparator — the parts with no safari in them. **A dominator tree and an
export list are answering the same question from opposite ends**, and where they
agree is where a reusable chapter is.

So the extraction that serves the night walk is not `collect` versus
`frame-ground` at all. It is the ~10 definitions at the top that neither of them
owns: the chain, the mappers, the sort. Those are a `Scene` or `Chain` chapter,
and once they are one, `collect` and `frame-ground` become two safari-specific
consumers of it rather than the place it lives.

## TruckBody, and why the tool is worth trusting

Steve's read, before seeing any of this, was that TruckBody is big for a reason
and naturally cohesive. The instrument agrees, and agrees in the strongest form
available to it:

```
TruckBody (port/TruckBody.codex)
  65 definitions, 95 internal calls

  INTERFACE — read by another chapter (1):
      truck-draw-body

  No mutual recursion: every group below can be cut.

  SEAMS:
    truck-draw-body owns 64 — Dimensions + Colours + The Headlight Beams +
                              A Body Point + The Faces + The Tires +
                              The Painter's Sort + Filling + The Wedges And
                              The Halo + The Brake Lights
```

**One exported name owning all sixty-four others.** There is no second sibling
subtree, no second root, nothing reachable except through the one door. That is
what maximal cohesion looks like from the outside, and it is the shape a
sixty-five-definition chapter should have if it is honest. Drawing a truck is
complicated; the chapter is big and is not confused.

It is also the calibration that makes the other two readings worth acting on. An
instrument that flagged everything would be flagging nothing.

## The order to do them in

`World` first, and not because it is worse. Its three subtrees are 16, 12 and 10
definitions with one owner each and a section heading each — the cheapest
possible test of whether a cohesion-driven split survives the sweep, on a
chapter with four exported names, which is about as small a blast radius as a
73-definition chapter can have.

`Render` second and in two steps: lift the chain and the sort out first, since
that is the piece the night walk actually needs, and only then decide whether
`collect` and `frame-ground` want to be separate files or are fine as two
sections of a chapter that has stopped holding a third thing.

## What the instrument still cannot see

Types. Every seam above is a seam in the CALL graph, and a subtree that shares a
record definition with the rest of the chapter is not as free as it looks. World
is full of records — `cfg`, `route`, a segment — and `fill-cows` almost
certainly reads one that `fill-trees` reads too. The cross-chapter index counts
type references, so the data exists; the dominator tree does not yet use it, and
until it does a proposed cut should be read as "the calls permit this" and not
"nothing else objects."

The honest form of the next question is a second graph over the same vertices —
types beside calls — and a cut that is cheap across both.
