# The safari tutorial: design so far

*Decided by Steve in Q&A, 2026-11-05. Nothing here is built yet.*

## Reader and point

- **The reader is the Roc community:** people who know Roc well, so we don't teach the language.
- **The main point is that Roc scales to a real program.** It also has to be fun, because the program is fun.

## Shape

- **The opening is the ride itself, live on the page.** Then the three fields of `Ride`: this is all that's stored, and everything you just saw comes from these three. Then the three kinds of moving thing.
- **The middle goes by the three kinds, simplest first:** things that never change (trees, cows), then clock-driven (sky, beacons), then rider-driven (cat, bird), then stepped (truck, rider). Each part adds one idea to the last.
- **It's quite long,** mixing prose, dependency diagrams and small snippets.

## How it's made

- **Snippets are real code.** Shale constructs the document from the source, rather than a gate checking hand-pasted copies.
- **The author writes prose with named includes:** one Markdown file with lines like `{{code Cat.moment_at}}`. Shale swaps in the function, type or doc comment by name, through the roc-ast parse trees. A name that's gone fails the build.

## Where it lives

- **The page is on roc.lynrummy.com, beside the game,** embedding safari's wasm, built by the site build.
- **The source and builder are in roc-apps,** in `canvas_apps/safari/tutorial/`. Safari's gate runs the builder, so renaming a quoted function fails the gate until the tutorial is fixed.
