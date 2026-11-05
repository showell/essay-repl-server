# The safari tutorial: design so far

*Decided by Steve in Q&A, 2026-11-05. Nothing here is built yet.*

## Reader and point

- **The reader is the Roc community:** people who know Roc well, so we don't teach the language.
- **The main point is that Roc scales to a real program.** It also has to be fun, because the program is fun.

## Shape

- **The opening is the ride itself, live on the page.** Then the three fields of `Ride`: this is all that's stored, and everything you just saw comes from these three. Then the three kinds of moving thing.
- **The middle goes by the three kinds, simplest first:** things that never change (trees, cows), then clock-driven (sky, beacons), then rider-driven (cat, bird), then stepped (truck, rider). Each part adds one idea to the last.
- **It's quite long,** mixing prose, dependency diagrams and small snippets.
- **Each chapter has a small live widget.** Roc runs on the page: drag the rider's gap to make the cat cross or the bird fly, or scrub the clock to watch the sun set.
- **One late chapter is on proving it,** after the stepped things: how a pure game lets us hash exact frames and refactor 50 modules with confidence. It's strong evidence for the main point, and it stays out of the fun chapters.
- **The voice is neutral** (Steve: "I don't like ghost writing"): no I or we, and a short credits note at the end.
- **The name is Safari Ride,** at least in the opening. The intro is dry: it has the important parts of a game's world, and no game mechanics yet. No kangaroo.
- **Each code example is prefaced by the interesting Roc concepts in it.** Each chapter introduces a few, and repetition is important: opaque types come back throughout. Mainstream things aren't belaboured.

- **Chapters:** the ride, things that never change, clock-driven, rider-driven, stepped, proving it, the platform.
- **The official Roc tutorial is a tiebreaker, not a plan** (notes/roc-tutorial-survey.md). The kinds set the chapters. When a chapter could introduce one concept or another, it picks the one the official tutorial introduces earlier.
- **Almost every example shows a function and then a call to it** (Steve). When the calling code is itself a tiny function, walk up the stack and show its caller too.
- **The framing is zoom in, then zoom out** (Steve): the big picture, then the details, then back out at the end to tie everything together. It isn't strictly bottom-up, in how it's built or how it opens.
- **An entire module appears early:** `Clock.roc`, 30 lines, right after the modules section, then `Pond.roc`, 52 lines, in "What never changes".
- **The tone is dry and restrained** (Steve, on the "tour of a tour" line: "Perfect tone."). Jokes are delivered flat, and buzzwords appear only where they're earned.
- **Good words for it** (Steve): composable, charming.
- **Metaphors are welcome** (Steve): the flipbook for the loop, sightings for what's in view.
- **Diagrams have at most 10 boxes** (Steve), collapsing modules into dashed families like "the plans" where needed.
- **Habits taken from it:** short snippets, cut where the detail isn't the point; show code that fails, with the real compiler message; say what the reader can stop thinking about; name the bug a feature prevents; state limits flatly.

## Changes to the code it asks for

- `Angle`'s types become opaque (`::`), as the draft says they are.
- Safari's specs move to `expect`, run by `roc test` (Steve's decision), so the proving chapter shows the idiomatic way. This follows the units work, because both touch every module.
- The emitter's leftover style goes before the tour quotes it: `if (x) a else b`, and whole bodies in parentheses.

## How it's made

- **Snippets are real code.** Shale constructs the document from the source, rather than a gate checking hand-pasted copies.
- **The author writes prose with named includes:** one Markdown file with lines like `{{code Cat.moment_at}}`. Shale swaps in the function, type or doc comment by name, through the roc-ast parse trees. A name that's gone fails the build.

## Where it lives

- **The page is on roc.lynrummy.com, beside the game,** embedding safari's wasm, built by the site build.
- **The source and builder are in roc-apps,** in `canvas_apps/safari/tutorial/`. Safari's gate runs the builder, so renaming a quoted function fails the gate until the tutorial is fixed.

## The first slice

One whole slice, so Steve can judge the idea before the long writing: the builder with named includes, the live ride, the three fields, and the cat's chapter with a gap-dragging widget. The cat comes out of its place in the order for this, because it's the best scene, and it proves the hardest widget.
