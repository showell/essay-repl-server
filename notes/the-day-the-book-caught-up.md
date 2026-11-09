# The day the book caught up

*2026-11-09. An open-ended look back at a very long working day, mostly at what went well.*

---

## The shape of the day

The day started with a proofread of three truck chapters and ended with the code describing itself the way a database schema does. In between, the work kept making the same move at different scales: find where a fact lives, make it live in one place, and let everything else ask.

By the numbers, roughly: thirty-odd lanes merged into roc-apps, every one through the full gate. The expects went from about 830 to 955. The book's stale-name count went from 80 to zero, and then the gate started holding it there. Every chapter got written, including the closing one, and every chapter got an accuracy round, a promote/demote round and a clarity round. roc-chat lost a bug that could quietly create a second account. Dog Park's gates stopped letting a skipped test pass. Shale's lints lost a dozen blind spots. Through all of it, the picture held exactly, pixel for pixel, except for one deliberate change that you approved and I eye-checked first.

## What went well

### Your questions were the best design tool in the room

The biggest changes of the day each started as one of your questions, usually a short one:

- **"Returning a TruckJourney from a TruckJourney feels kinda funny."** That led to `TruckProgress`, and then to noticing that the truck is the one mover carried forward rather than worked out from the clock. The book's spine showed up in a type signature.
- **"Why does a Sighting just not include the elevation?"** That one reversed a design I had pushed for that same afternoon (`raised_ground_point` as the "one home"). The better answer was that the sighting already had everything it needed and was throwing it away. Cards got the earth's curve for free, the truck lost a strange import, and one `BelowHorizon` rule replaced a tower-only one.
- **"If I'm trying to draw a truck, I need to know what our truck looks like!"** That gave the shape-first truck. It also turned up a nice surprise: rigid placement moved zero pixels, because the old code was already rigid and just didn't say so.
- **The database thought experiment.** It produced the most useful vocabulary of the day: views take only the columns they read, derived values aren't stored, constraints live with the data. Both smells are now in docs/smells.md, so every future reviewer carries them.

In each case the question didn't ask for a change. It asked why the code was the shape it was, and the honest answer was usually "no good reason".

### The essay surface did its job

Decisions went to notes, not the console. Each note ended with a lean and, often, one question, and you could answer with a word inline: "rigid", "yup", "Strongly agree with your B choice". The calls that needed real thought, like the beacon's three shapes, heights in a 3D world, or sightings knowing the ground, got a page of signatures and numbers instead of a paragraph of opinion. Most of the time you were reading one thing while five lanes worked on others, which is the single-threaded rhythm you asked for.

### Cold agents were good at the work that suits them

Agents were best at three kinds of task:

- **Adversarial checks with a narrow brief.** Fact-checking a chapter against the code, auditing one cluster of types, or proving lints blind each came back with specific findings, line numbers and proposed fixes. The lint audit's eleven confirmed blind spots, each with a snippet that `roc fmt` accepts, was the cleanest example.
- **Decided changes with a strict gate.** "Here are seven items, keep the pixels held" worked again and again, because the gate made "done" unambiguous. Several agents planted a fault once to prove their own test could fail, which is exactly the habit you want.
- **Finding what I'd have missed.** A book agent noticed that a tree changes sort, from card to solid, as the rider gets close. A merge agent noticed that one more beacon came into view after the curve change. The widget audit found the beacon readout ignoring each segment's stagger.

### The gate kept getting stricter, and stayed green

Ratchets only moved one way: book names held at zero, every module named in the book, a skipped Zig test now fails Dog Park's gate, the `stack` lint now sees wrapped signatures, and constraints on the static world are now expects. Each tightening landed with zero findings, because the fixes for its hits landed with it. Nothing was loosened to make a gate pass.

### The book caught up with the code

At the start of the day the book was badly stale in its opening chapters: diagrams that didn't match the imports, dead module names, numbers from an older ride. By the end it states the spine early (four things remembered, everything else worked out), says what the three sorts of object are, shows the step's order once and in full, and every number it states about step 1,529 is pinned by an expect, so it can't drift silently again.

## What went wrong, briefly

- I wrote the truck "bends across a bend" in a design note. It didn't, and an agent found that out by measuring.
- One fact-check reported dead code that a widget was using. I caught it before the deletion landed.
- Some lane briefs left out the reviewer's exact text, so agents had to write their own versions. Saving the review to a file fixed that.
- The Roc bisect may be chasing an intermittent crash, which means some of the day's "good" results need repeats before they mean anything.
- I spent your tokens fast. Five lanes at once is effective, and it's expensive. Scaling back for a couple of days is in memory.

## What it adds up to

The day's real product isn't any one refactor. It's that the program, its book and its gates now agree with each other more tightly than they did in the morning, and they're checked by machines rather than by memory. The truck says what it looks like before it says where it is. The sightings say what they read. The world says what it holds. The book says what's remembered. And when any of them stops agreeing with the others, the gate says so before anyone has to notice.

The parts I'd most like to repeat: short questions from you that start with "why", leans written down before they're needed, and agents given narrow briefs and strict gates.
