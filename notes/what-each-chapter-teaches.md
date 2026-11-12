# What each chapter teaches

These are the fourteen published chapters, as they stand on the dev book today, with "Refused" new after The pipeline. For each chapter: the Roc ideas it really explains, with its main point starred (★), the animation ideas, and the part of the program it covers. "Again" marks an idea a chapter returns to.

## The table

| # | Chapter | Roc | Animation | Program |
|---|---|---|---|---|
| 1 | Introduction | none, by design | promised: frame and step, far is small, near covers far | the ride, running |
| 2 | One page | ★ reading a type annotation; the `# ...` cut; a platform, in one line | a flip book; a frame as one list of shapes; the roll | `FrameView`, `frame_view_at`, `leaned_shapes` |
| 3 | The problem | none, by design | frame and step; far is small; near covers far | the five pieces |
| 4 | Platforms, packages and modules | ★ the app header and its platform; ★ packages, modules and `import`; comments | the platform paints what Roc describes | `web.roc`, `SafariApp`, `WasmApp` |
| 5 | The pieces as types | ★ opaque `::` with functions in `.{ }`; ★ type variables (`Placed(kind)`); wrap and unwrap; lambdas; `##` doc comments; records; `:` vs `::` vs `:=`; a tag union in place | sprite; spot; depth; painter's order; carried and derived | `Distance`, `Billboard`, `Sprite`, the three forms, `RideInstant`, `Tour` |
| 6 | Things | ★ a function's annotation and body; ★ `if`/`else` as an expression; method calls; field access; again: only its module builds an opaque value | a billboard; mirroring; the lens; dimming | `CowHerd`, `Species`, `Sprite.Setting` |
| 7 | Billboard Critters | ★ tag unions; ★ `match` and its exhaustiveness error; a block with named values; payloads in patterns; field punning | facing right | `Facing`, `BendAnimal`, `BendLife` |
| 8 | Shapes | ★ taking a record apart in the arguments; hex literals; again: tags carrying records | shapes describe, the platform paints; y grows down; ★ list order is paint order | `Shapes.Shape`, `Shapes.rectangle` |
| 9 | A far tree | ★ `map` and `map_with_index`; ★ `expect` and `roc test`; `concat`; a crash on a bad value | paint order inside a sprite; level of detail; the upright outline | `TreeShapes` |
| 10 | Types for places | again: opaque types as units; a type that holds a fact by construction (`RiderPointAhead`), thinly | road coordinates against camera coordinates | `RoadPoint`, `Spot`, `RiderPoint` |
| 11 | The pipeline | again: type variables, the kind carried then dropped; wrap in a body, unwrap in the arguments; `join` | placed, sighted, rendered; again: depth sort | `Pipeline`, `Rendered`, `Scene` |
| 12 | Refused | ★ `Try`, `Ok` and `Err`; ★ `?`; `?` with a function that renames the tag; `keep_oks`; `match` on a `Try` | the near plane; a near horizon; a size cutoff | the three sighting functions, `TreeSighting`, the truck's `match` |
| 13 | Nature types | ★ nominal type identity, fully explained; ★ methods inside the braces vs helpers outside; or-patterns | none | `Conifer` |
| 14 | Asking a kind | ★ `where` clauses; dispatch fixed per type at compile time; the missing-method error; methods match by name | again: lens and light | `Pipeline.rendering_of` |

## What the table shows

**A title names the Roc idea in two chapters out of fourteen.** "Platforms, packages and modules" names its Roc ideas outright. "Refused" names its subject, and its subject is error handling. The rest name a part of the ride ("Things", "A far tree", "Nature types") or a step in the book ("One page", "The problem"). A reader scanning the contents for `match`, `Try` or `where` finds none of them.

**Most chapters have a clear Roc point, and it sits well with its program part.** Tag unions and `match` come with the critters, `map` with the tiers of a tree, `Try` with the refusals, and `where` with the one rendering function. A subtitle could carry each of these without a rename.

**A few chapters have a thin Roc point:**
- **One page** teaches reading an annotation, which is right for a first pass.
- **Shapes** is mostly data. Taking a record apart in the arguments is its one new idea.
- **Types for places** repeats opaque types. Its own idea, a type that holds a fact by construction (`RiderPointAhead`), is underplayed, and it could be the chapter's point.
- **The pipeline** is mostly the trip itself. Its one new Roc idea is the wrap-and-unwrap pair, and it quotes `Placed` and `Sighted` again, word for word, from chapter 5.

**Nominal `:=` is explained three times**, in chapters 5, 7 and 13, and fully only in 13.

**Roc ideas that show up in code but are never explained:**
- `!` functions such as `main!`, and `Ok({})` with the empty record;
- lambdas that use names from around them, such as `in_view.from_rider` inside `keep_oks`;
- record types written into an annotation, and annotations split over several lines;
- arithmetic and number methods on `F64`, and how a literal such as `0.35` gets its type;
- a nominal record with methods (`RideInstant := { … }.{`), and getter-style methods such as `spot.lift()`;
- `crash`, which is only mentioned.

## Sources

A cold reader listed what each chapter explains from the built book. I checked its list against chapters 2, 4, 11, 12 and 14, which I've worked in today. Steve decides the next step: renames, subtitles, or both.
