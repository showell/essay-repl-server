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

## How it's made

- **Snippets are real code.** Shale constructs the document from the source, rather than a gate checking hand-pasted copies.
- **The author writes prose with named includes:** one Markdown file with lines like `{{code Cat.moment_at}}`. Shale swaps in the function, type or doc comment by name, through the roc-ast parse trees. A name that's gone fails the build.

## Where it lives

- **The page is on roc.lynrummy.com, beside the game,** embedding safari's wasm, built by the site build.
- **The source and builder are in roc-apps,** in `canvas_apps/safari/tutorial/`. Safari's gate runs the builder, so renaming a quoted function fails the gate until the tutorial is fixed.

## The first slice

One whole slice, so Steve can judge the idea before the long writing: the builder with named includes, the live ride, the three fields, and the cat's chapter with a gap-dragging widget. The cat comes out of its place in the order for this, because it's the best scene, and it proves the hardest widget.
