# The gates reorganization

You asked for it near the end of the type review, and we're close. A read-only survey mapped `canvas_apps/safari/gates/` as it stands. Here's the plan, and the three small calls it needs from you.

## Today

- **Shale tiers:** fast, run, publish, lints, book_names, input_bits.
- **Expected values:** `proof.expected` and `page.expected`. The parked book's build also reads proof.expected.
- **Test roots:**
  - `CrossModuleExpects.roc` (CME): **2,860 lines, 240 expects, 73 imports**. It's fast.shale's only `roc test` and the hot conflict file for every lane.
  - `WidgetExpects.roc`: the widgets' one root.
- **The pixel and ride proofs:** RasterFrame, ShapesFrame, StepBack and OnRoad, plus 10 library modules (ShapesPixels, ScanlineFill, PixelGrid…). **FrameBench is built by nothing**, so it can rot unseen.

## The plan

```
gates/          the .shale tiers, proof.expected, page.expected, WidgetExpects.roc
gates/expects/  main.roc (one package root) + Fixtures.roc + six *Expects.roc
gates/pixels/   RasterFrame, ShapesFrame, StepBack, OnRoad, FrameBench + the 10 library modules
```

CME splits by topic, all 240 expects accounted for:

| module | covers | expects |
|---|---|---|
| Fixtures | the crafted roads and routes, shared helpers | 0 |
| RoadExpects | the road ahead, bends, ground patches, Spot | 23 |
| SightingExpects | trees, rails, billboards, wildlife, towers, the pond, the truck | 31 |
| SceneExpects | Scene, Pipeline, depth order | 30 |
| EncounterExpects | cats, birds, encounter plans, posed animals, stills | 65 |
| RideExpects | RideInstant, finishing, crossings, sunset and night, FrameView | 38 |
| RiderExpects | heading, lens, attention, throttle, coasting, gawking, gaze, lean search | 53 |

- **One package root** (`roc test gates/expects/main.roc`), like lib's, so the game is checked once and the time should match today's. A spike measures this first.
- **No part imports another part.** They share only Fixtures.
- **Order:**
  1. a spike (two modules) proves the package root and times it;
  2. the pixels move, which is plain renames, so it's safe beside other work;
  3. the CME split, mechanical, in one commit with no test changes, run while no lane holds CME;
  4. a pruning pass, part by part.
- **Risks:**
  - git won't follow one file split into seven, so any lane branched before the split has to redo its CME edits by hand. That's why the split waits until no lane holds CME.
  - Some docs and briefs name CME by path.

## The spike (2026-11-07): it works

A package root with package dependencies runs fine as a `roc test` root (branch expects-spike, 340c3b53, not merged). The 7 moved road expects ran exactly once overall. A failure reads `── ✗ fail ── gates/expects/RoadExpects.roc:71:1`, which run.shale and fast.shale already understand. The time is mostly running the expects, so the split costs about what CME costs today. What the full split must also do:
1. **run.shale's `SAFARI_SOURCES`** must add `:(glob)canvas_apps/safari/gates/expects/*.roc` (a git glob's `*` doesn't descend), and `EXPECT_ROOTS` plus fast.shale's root (line ~144 and its print line) must point at `gates/expects/main.roc`.
2. **Each part** declares `XExpects :: [].{}` and keeps its expects at the top level.
3. **The shared helpers** move into Fixtures and every call gets the `Fixtures.` prefix.
4. **Two traps at this Roc pin.** Unused imports never warn, so lints.shale's unused_imports must cover gates/expects. A module left off `package [...]` runs silently with 0 expects, and only run.shale's source-vs-passed check catches that.
5. **The parts together must still reach every game module whose expects only CME reached,** or those expects drop out. run.shale's "not passed from any root" check catches it.
6. **Briefs and docs that name CME** need the new path (type-review.md's "listed in game.roc before gates/CrossModuleExpects.roc can import it", among others).

## Steve's answer (2026-11-07)

"LGTM. We can scale back the agents during the CME split." So the folder is `gates/proof/`, and Fixtures may be a namespace. The CME split runs with no other lane open. **FrameBench stays** (changed the same day): the start-up stutter turned out to be the cost of computing a frame, and FrameBench is the tool for profiling that, so it moves to `gates/proof/` with the others.

## Your three calls

1. **The folder's name:** `gates/pixels/` (your word) or `gates/proof/`? StepBack and OnRoad check the ride, not pixels, and `part=proof` already runs them. *My lean:* `gates/proof/`.
2. **FrameBench:** nothing builds it. Add a build of it to part=proof, or delete it? *My lean:* delete it; it's a benchmark nobody runs.
3. **Fixtures as `Fixtures :: [].{ … }`,** the empty-type namespace form that smells.md flags. Accept it for test fixtures? *My lean:* yes; the smell is about production code.
