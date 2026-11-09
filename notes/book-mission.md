# The Safari Ride book: a mission statement, and a plan to finish it today

*For Steve, 2026-11-10. This pulls together what you've told me about the book over the last week. Your words are scattered across a dozen memory files, so they don't make it through a compaction intact. Part 1 is the mission. Part 2 is the requirements, sorted along nine axes, each numbered so you can comment on one line. Part 3 is a plan for finishing today. Part 4 is where this document should live once you've corrected it.*

---

## 1. The mission

The book walks a programmer through one real Roc program, Safari Ride, from the whole down to the details and back out. A reader should finish it knowing two things. First, how a program with a lot going on can stay simple: a small state carried from step to step, everything else derived from it, and types that leave a wrong state nowhere to live. Second, how Roc makes that natural, mostly with vanilla code.

The reader is a working programmer, probably coming from TypeScript or something like it, who can read a little Roc. The book never compares Roc to another language. It explains each Roc idea on its own terms, where it first bites.

The book is honest about the code. It quotes the real code, its numbers come from the real program, and when a sentence is hard to write, we fix the code first.

## 2. The requirements, axis by axis

I picked these axes so that each one fails in its own way, and catching each failure takes a different kind of read. Truth needs the code open beside the page. Order needs a reader who has seen only the pages before. Voice and tone need an ear. Vocabulary needs the glossary. The code axis needs a smell-hunter. Pictures need eyes. Completeness needs a checklist. Purpose needs the whole book in view.

### Axis A. Purpose: every chapter teaches something real

- **A1.** A chapter teaches one idea about writing clear Roc, or one axis of difficulty from the axes note, or a harder case of one. The axes are shapes, placement and projection; motion; the camera; rider physics; what covers what; honest cheats; the platform edge; proving it.
- **A2.** "Who owns this behavior?" is the question every chapter answers again. It is not a chapter of its own.
- **A3.** The spine shows through every chapter:
  - each step carries four things, and the program derives the rest;
  - within a step, the world and the rider change each other, and order matters;
  - there are three sorts of thing: solids, cards and far scenery;
  - each tick is a pipeline.
- **A4.** "Really teach something without forcing the issue." Most of the code is vanilla, and that's a feature. Don't invent a new Roc concept for every chapter.
- **A5.** Say what Roc *is*. Don't bash OO or any other style.

### Axis B. Truth: every sentence matches the code today

- **B1.** Code comes in by include (`{{code M.f}}`), never pasted. The gate holds stale names at zero, and the book must name every module.
- **B2.** Every number in the prose is the program's number, pinned by an expect or a table the gate builds. Nothing is "about right".
- **B3.** No old bugs, no history and no "used to". Write in the present tense. "By construction" says enough.
- **B4.** No complicated design reasons inferred for simple choices. Give a constant its plain reason, and a computed one its calculation.
- **B5.** An argument is earned by what the reader has seen. Don't defend a feature the book hasn't shown.

### Axis C. Order: a reader who has read only what's above

- **C1.** Top-down and simplest first. The forest comes before the trees. Lead with the function that frames the problem, as `Truck.truck_picture` does for the truck chapter.
- **C2.** Inside a chapter: the problem first, as needs. Then "Get the types right", with the flowchart right after it. Then the functions.
- **C3.** Never lean on something unseen. A forward pointer names what's coming and why, or it goes.
- **C4.** Every chapter's opening stands alone, usually by restating the premise. A chapter's end may leave a question hanging. Readers land anywhere, so avoid "remember the first chapter" callbacks for simple ideas: explain them in place.
- **C5.** Handle each job discretely. One job gets one section, and the job comes before its details.
- **C6.** Difficulty rises, tempered by categories: nature, man-made, critters. One frame is held still for the first half, and motion starts at The ride instant. Teasing an idea early is fine.

### Axis D. Voice: the sentences themselves

- **D1.** **Active voice.** "We carry a small amount of state… we derive values from it", never "four things are remembered" or "everything else is worked out".
- **D2.** **Say what happens.** Never define a thing by what it isn't, can't do or doesn't remember ("can't go stale", "has never heard of a tower"). Say what it does.
- **D3.** Short sentences: Hemingway, not Faulkner. A strong sentence stands alone. Don't join two sentences that could stand on their own with a comma or ", but".
- **D4.** Talk to the reader with "we", "you" and contractions. Start the book, and each chapter, with a full sentence, never a fragment.
- **D5.** Code first, then one plain sentence on what it does, then why, in ordinary causal words ("That's because…").
- **D6.** Use plain verbs (is, does, gives, takes), not abstract nouns. Keep prepositions ("For each frame it calls", not "Each frame it calls").
- **D7.** No agent-speak:
  - appositives ("`truck_blue`, a navy, paints…");
  - "the way from X to Y is…";
  - "and that's the point of this chapter";
  - "worth saying again";
  - a "this" or "that" where a name belongs. After the cat's code, "This is why the cat waits" makes the reader hunt for what "this" is. "`plan_crossing` is why the cat waits" names it;
  - aphorisms, "not X but Y" drumbeats, or a closing moral.
- **D8.** Explain a type precisely rather than apologizing for its name.

### Axis E. Tone: how it feels to read

- **E1.** Dry, plain and technical, with the jargon the audience already knows ("completely deterministic"). Some cleverness is charming ("a tour of a tour"), but don't overdo it.
- **E2.** Humor is restrained: at most one exclamation mark a chapter, and a rare "hooray".
- **E3.** Repetition teaches, so keep a returning idea. A returning idea is the place for a wink ("Guess which technique comes up again?"). A guess is about an idea, never about arithmetic.
- **E4.** No bragging that simple code is simple. No presumed reactions from the reader.
- **E5.** Vary the chapter endings. Ending on what's still missing is a good move, but it isn't a template.

### Axis F. Vocabulary: one word for one thing

- **F1.** These words keep their meanings: frame, step, sighting, spot, kind, picture, rendering, segment, critter (an English word, never a type), solid, card, far scenery, carried, derived.
- **F2.** Every term goes in the glossary, and the book uses the glossary's word.
- **F3.** Write "math", not "maths". "Metres" and "colour" are fine. Write "forward" and "backward", never the "-s" forms.
- **F4.** Types name numbers. Never say a `Pixels` isn't a number.
- **F5.** "Picture" means one thing: the program draws a series of pictures for each step, against a backdrop.

### Axis G. The code behind the prose

- **G1.** The book is a code review. A sentence that's hard to write, or that exposes an odd design, is a code finding first, and the chapter follows the fix.
- **G2.** Quote code that reads more or less like English. Code should answer to its name.
- **G3.** Coordinate transforms belong in one home. A chapter that has to explain the same transform twice is a smell.
- **G4.** The smells in `docs/smells.md` apply: a fat API, a derived value stored beside its source, a name that needs a comment to translate it.

### Axis H. Pictures: diagrams, tables and widgets

- **H1.** Put a diagram early. Every edge has a label, a verb and often the function that does the work ("finds it with truck_in_view"). An edge whose only honest verb is "imports" is worth a look.
- **H2.** In the One frame half, a widget is a static frame. VCR controls come only once time passes. There are no sliders.
- **H3.** A widget gets one sentence of explanation, not a listing of its code. It says which call it adds and what it shows.
- **H4.** A table is welcome wherever it shows data the program really produced.

### Axis I. Completeness: what "done" means for a chapter

- **I1.** It has a problem, its types, its functions and an ending, plus "New in this chapter" when it introduces something new.
- **I2.** Every sentence in book-parked-sentences.md that points at it is fixed or struck out.
- **I3.** The gate is green, and the book is rebuilt on the dev channel.
- **I4.** You've read it, and your replies are answered.
- **I5.** For the whole book: the glossary is current, the appendices match the chapters, and Zooming back out sums up exactly what the chapters showed.

## 3. A plan for finishing today

The book has 43 chapters and about 34,000 words. Every chapter has a draft that has had at least one round. The opening, the sunset, the beacons and the truck have had your line-by-line reads. So today is a linear pass, not a rewrite from nothing.

**The loop, for one chapter at a time, in book order:**

1. I read the chapter and the code it quotes.
2. If the prose exposes a smell (G1), I fix the code first. Only small fixes today. A bigger one goes in the queue, and the chapter describes the code as it stands.
3. I rewrite the chapter myself against axes B through I.
4. Gate, commit, push, rebuild the book.
5. Every four or five chapters, I post a proofread note with the new text, and you read it while I go on. Your replies come first whenever they arrive.

**The parts, as your reading batches:**

| Batch | Chapters | State |
|---|---|---|
| 1 | Introduction through The world (5) | done today; your replies in |
| 2 | Shapes, Nature types, the two tree chapters, Roadside trees, Grass (6) | rounds done; needs voice pass |
| 3 | The sun, The sky, Mountains, The road, Rails, Radio towers (6) | sun and sky polished earlier |
| 4 | Stills, The elephant, the corner critters, Herds (4) | |
| 5 | The ride instant, The beacons, The setting sun, Stepping through the ride (4) | beacons and sunset read by you |
| 6 | The rider, The bike, The throttle, The rider's gaze (4) | |
| 7 | The truck, its motion, its lights (3) | read by you |
| 8 | The cat, The bird, What a cat does to the rider, Rehearsal (4) | |
| 9 | The math layer, Proving it, The platform, Zooming back out, appendices, credits (7+) | the last pass sweeps the vocabulary (F1) |

**Cold agents.** You asked for none while I rebuild context, and I'd keep it that way for the writing. One cheap exception: after each batch, one cold reader checks just two things, truth against the code (B) and order for a reader who has seen only the pages before (C). Those are the two axes where I'm blind to my own outline. I take its findings with restraint. You can veto this.

**The vocabulary sweep.** The carried-and-derived wording reaches the later chapters as each batch comes up, not in one sweep. That keeps every change in a chapter you're about to read.

**Being honest about "today".** Nine batches in a day is a lot. If the day runs short, batches 7 and 5 (the chapters you've already read) get the lightest pass, and the rest wait for tomorrow at the same standard. I won't lower the standard to make the date.

## 4. Where this lives

Memory is the wrong home. It's scattered, it records what you said when you said it, and a compaction drops the detail. I'd move this document, once you've corrected it, into the repo as `canvas_apps/safari/tutorial/MISSION.md`, beside the book it governs. One memory file would point at it and say "read this before touching the book". The book-voice memories would then shrink to pointers, so the rule has one home.

---

**Questions for you:**

1. Are these the right nine axes? Is any axis missing, or two that should be one?
2. One cold reader per batch, for truth and order only: yes or no?
3. Should this document live in the repo as `tutorial/MISSION.md`, with memory pointing at it?
