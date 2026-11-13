# A cold reader on the whole book

One cold agent read all 39 chapters and the appendices, from first line to last. It read the built book with no notes on how it was written, and judged it as a working programmer who has done a little Roc. It was asked for five strengths, five weaknesses, five questions for the authors, and who the book is for. Its findings are below, close to verbatim. My comments follow each list, in italics.

## Five things the book does well

1. **One real program, held still, as an anchor.** "Step 1,529 of the ride, held still" grows layer by layer, from sky and mountains through the road, rails, towers and herds. That gives the first half a visible spine, and the reader always knows what's been built.
2. **Compiler errors shown verbatim, from real failing programs.** The `Rock` without a `scenery_sprite`, `turn_as_bearing.roc` and `Clock.start + 7` make the type-safety claims concrete. "These are some of the most convincing pages."
3. **Each Roc idea arrives where the code needs it.** The titles pair a concept with a part of the program, so `where` turns up as the answer to "how does one `rendering_of` render every kind?", not as syntax for its own sake.
4. **Design wisdom, not just syntax.** Carried and derived, the chain of limits, rehearsal on a pretend motorcycle, and the `scenery_` prefix as a defense against accidental `where` matches are "lessons a working programmer keeps".
5. **Honest, plain explanation.** It admits shortcuts ("That's a cheat, chosen by eye"), explains why the order of a float sum matters for exact hashes, and points out pitfalls like `(timeline.frame_instant)(frame)`. The piece-by-piece tables for `darkness_at` and `stopped_at` are "excellent".

*All five are things we set out to do: the held frame, `{{fails}}` for real compiler errors, the renamed titles, the patterns, and "fix the code first". Point 3 is the contents work paying off, and nobody prompted it.*

## Five things it could do better

1. **The prose cadence is monotonous.** "Nearly every section ends with a 'So ...' restatement." Over 39 chapters, the summaries read as padding rather than reinforcement.
2. **Code is repeated, while key code is withheld.** `RideInstant` is quoted four times, and `Placed`, `Setting` and `Stage` twice each. Meanwhile `range_height`, `lowest_visible_height`, `trunk_shape`, the cones and `ConvexHull` appear only as annotations or mentions. "The reader is asked to take the hard parts on trust."
3. **The foundations come late.** Perspective drives every sighting from The pipeline on, but the math layer arrives at chapter 36. Loops arrive around chapter 29, and immutability after the first half. Types front-loads `:`, `::` and `:=` before the reader has a reason to care.
4. **The second half drifts from Roc into domain detail.** The gaze, throttle, truck and herds chapters pile up tuned constants with little new Roc. Several Roc ideas get one sentence each: closures, tuples, guards, `..` in record types, `Box`.
5. **The project's internal workings leak through.** "The gate", `gates/proof.expected` and lints held at zero assume the reader knows the repo. The index's entry for "Static dispatch" points at a term the text never uses.

*1 is fair, and partly my doing. Today's polish of Types, Functions, Things and Tag unions ended every section on a "So …" theme sentence, as you asked, and the voice pass already leaned that way. Across four chapters in a row the pattern shows. For the next book: state a section's theme in its heading, and end on it only where the ending earns it.*

*2 is the sharpest. The repeats come from includes added chapter by chapter, which no gate ever checked across the book. A gate could flag any definition included more than once. The withheld code is the other side of the 900-word limit and of C8 (annotations first). I'd keep that trade, but say plainly when a body is skipped.*

*3 is a choice we made on purpose: the axes of difficulty put the camera late. The reader is right that "on trust" is a long IOU. A one-paragraph intuition of perspective in The pipeline would pay part of it early.*

*4 is the real tension of the second half. Those chapters are app chapters by design, but the five one-sentence Roc ideas are a fair catch. They're candidates for the patterns appendix or the index, not for new chapters.*

*5: half artifact, half fair. The chapters are numbered on the pages ("Chapter 34"); the agent read the markdown build, which has no numbers. "Static dispatch" is a real index bug. Its pattern matches "method call", and the prose never says "static dispatch". I'll rename the term to "Method call" once the publish gate is done. The repo talk in Proving it is the chapter's subject, but "gates/expects/" could become "a folder of tests" for a reader outside the repo.*

## Five questions for the authors

1. **Why hold the frame still for the whole first half?** A reader waits about twenty chapters before any code moves. Did you try bringing in a small piece of motion early, say the beacon or the clock?
2. **Who is the floor reader?** You send beginners to the official tutorial, then teach `if`, annotations and `==` from scratch, yet drop in `Box`, `where` clauses and the nominal-versus-opaque split with little framing.
3. **Why no invitation to run, change or break the program?** No build command, no `roc test` output, no exercises. The live widgets suggest a hands-on book, but the reader only ever watches.
4. **Was the uniform, humorless voice deliberate?** And why "we" for design decisions, but an impersonal voice for the code?
5. **Why compare Roc to no other language?** One-line anchors would help a working programmer: "a `Try` is Rust's `Result`", or "`::` is Haskell's newtype with a hidden constructor".

*These are the ones to carry to the next book. 1 and 5 are rules from MISSION (C6, and "the book never compares Roc to another language"), so the answer is "yes, on purpose". The question is whether the rules still earn their cost. 3 is the one I'd act on first: a short "run it yourself" page, with the checkout, `roc test` and one change to make, would fit the Introduction or an appendix. 2 is the hardest, and it shapes every chapter, so it's worth settling before the next book starts. 4 is MISSION E1 and E2 working as written ("dry, plain and technical"). The reader felt the cost too.*

## Who it's for

"This book is for a working programmer who has done the official Roc tutorial and wants to see how Roc scales to a multi-module program." It suits "especially readers who care about design habits like carried versus derived state and invariants enforced with `crash`". The reader would recommend it, with two caveats: expect to skim the domain-heavy second half on a first read, and "the slow, plain, repetitive cadence rewards patience more than it rewards speed". It sums up: "A reader who wants to learn to think in Roc's types will get real value."

*That's close to the reader MISSION names. The two caveats line up with weaknesses 1 and 4.*
