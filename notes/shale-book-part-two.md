# Part Two: four languages, one workflow

Part One ends with a working essay surface: a Go server, a plain-JavaScript front end, and Shale holding it all together with gates. Part Two makes the surface richer. Notes gain dot diagrams and small widgets, and the features that render them are written in Roc, with types designed first.

## The same premise, one level up

Part One's theme is building your own workflow. Part Two keeps it, and the workflow simply gets better at its own job: a note that can draw its diagram or embed a widget is a better place for an agent to explain something to you. Graphviz drawing the book's dot code blocks at build time is already how this book works, so Part Two gives the surface the same power.

It also moves the book into app territory, which is where most readers live. Part One was a small server with careful gates. Part Two is a real feature roadmap, with a design language for it.

## Every language doing its job

The app ends up with four languages, each in its lane:
- **Shale is the glue.** The agent builds, checks, refactors and ships in it, as in Part One. Shale doesn't appear in the app; it's in everything around the app.
- **Go does the plumbing:** HTTP, files, the watcher, the comment store. It's boring, and that's its job.
- **Roc expresses the features:** what a note means, what a diagram block is, what a widget may say and do. Pure functions over well-designed types, with a compiler that checks the design.
- **JavaScript does what JavaScript always does:** the page, the clicks, the reply box.

A team of humans rarely does this on purpose. Each language costs hiring, onboarding and a style guide, so teams settle on one or two and bend them to fit. For an agent, a language costs about what a Shale dialect costs: it reads the docs and the code every session. Part One makes that argument about dialects. Part Two takes it to its conclusion: with agents, true multi-lingual development becomes practical. You pick each language for what it's best at, and pay little for the switch.

## Where the risk moves

The bugs move to the seams. Go hands Roc a note and gets back HTML, and Roc hands JavaScript a widget's state. Each seam is a contract, and a contract is a natural place for a gate. That gives Part Two its thread the way gates gave Part One theirs: **type-driven design** puts the contract into Roc's types, where the compiler holds it on every build. A type is a standard the language enforces for free, a gate you never have to write. That fits MISSION AH: a session's prompt sets its mission, and in Part Two the first thing a mission produces is types.

## The open design question

How Roc sits on Go is the first real decision of Part Two. It's the right decision to show the reader, since it shapes everything after:
- **Roc on the server,** where Go calls Roc to turn a note into HTML. Diagrams and widget markup render once, and the browser stays plain.
- **Roc in the browser,** compiled to WebAssembly, the way the Safari book's widgets already run. Widgets become live, and Go stays pure plumbing.
- **Both,** with rendering on the server and interaction in the browser, sharing the same types.

The book should show the agent weighing these options, and the decision we make.

## Three tweaks to choose from

1. **Open Part Two with a port, against an oracle (scope).** Before any new feature, the first session moves the markdown renderer from Go to Roc. The Go renderer stays as the oracle: every one of your 500-odd real notes must render byte for byte the same. That gives Part Two a gate on day one, a large real corpus, and the reader's first look at Roc doing a job they already understand. Diagrams and widgets come after, on a renderer we trust.
2. **Types as the prompt (method).** Every Part Two session opens with the types, not the feature. The prompt gives the mission, and the agent's first report is a proposed set of Roc types for you to reply to on the surface, before any code. The book shows that exchange each time, so type-driven design becomes the reader's main habit: argue about the types, and let the compiler hold the rest.
3. **Read Roc, rarely write it (the reader).** Mirror Part One's premise exactly. As with Shale, the reader reads Roc and judges it, and the agent writes it. A short "Meet Roc" interlude opens Part Two, like Meet Shale, with one real function quoted from the project. Roc stays a language the reader can follow at scroll speed, and its unusual features are introduced only when a session needs them. That keeps Part Two open to readers who will never write Roc.

**My recommendation is 1, with 3's interlude.** The port gives Part Two the same opening shape as Part One, a real gate before any new feature, and it's honest about how we'd really do it: we wouldn't let a new renderer anywhere near your notes without the old one as a judge. Tweak 2 then arrives on its own, the first time a feature needs new types.
