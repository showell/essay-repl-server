# Postmortem: the first four chapters

## What works

- **Hard problems.** When you pose a real dilemma, such as the order of the five pieces, Picture versus Sprite, or where the platform goes, the riffs and essays find a good answer quickly. The whys are the most productive part of the loop.
- **Paragraph-level prose.** Read one paragraph at a time, the prose is good: plain, confident, short sentences.
- **The book as an object.** Real widgets, color-coded Roc, diagrams with labeled edges, a three-chapter build in the real format. It looks like a book, and that keeps us honest about what a reader sees.
- **Gates.** Nothing false about a name or an include reaches you, because the build refuses it.

## What doesn't work

The problem is attention to detail, and the readability report shows it's systematic, not bad luck. Four habits cause it.

**1. I edit locally after a structural change.** Every big change this session (cutting the four small things, turning chapter 3 into a types chapter, splitting off the platforms chapter) was done by surgery on the old text. Each surgery left something behind:
- the "small story / rich picture" paragraphs, with nothing left to lead to;
- a title, "A small story, a rich picture", that no longer matched;
- the frame widget sitting under an opening that no longer introduced it;
- "Now we take the programmer's seat" surviving into a chapter that had already taken it.

MISSION already says to write a clean draft every time. When the structure changed, I edited instead.

**2. I fix by adding.** Each cold-reader finding of the form "X is used before it's explained" got a new clause. So the "Things" section grew to eight Roc ideas in two paragraphs (the readability reader's item 2), and the types chapter's three ways to define a type ended up spread over three sections (item 3). The right first question was "can X leave this page?" I never asked it.

**3. Nobody reads the whole chapter as a reader before you do.** The gates check names, and the cold readers check the axes I give them. I read the paragraphs I touched. Only you read the chapter top to bottom, in order, as one piece. That's how "frame" ended up meaning two things four times in one paragraph. I wrote that paragraph, and no check of mine reads for that.

**4. Pulled-in parts aren't re-fitted.** The flipbook readout, the route widget's plan readout and the 960 by 700 embed were all made for the old book. Each one looked fine, so I never asked whether it fit this page. H6 now covers this, but it's the same habit as 1: something reused without being re-read in its new place.

**5. I ran a narrower gate than the change touched.** When I removed the frame widget's panel, I ran that widget's own check and tests, not `part=widgets`. A gate test, `WidgetExpects`, still looked for "Added: The moving things", so I pushed a red master (d5269d4c). The widgets agent found and fixed it. The rule I broke is in memory already ("a green is a claim": read what ran). The fix is mechanical: a change under a widget runs `part=widgets` before the push.

**What the habits share:** I treat the draft as a set of paragraphs to keep correct, not as a path for a reader to walk. That's also the flow problem.

## Flow, the stumper

Flow breaks where one paragraph doesn't hand off to the next. A chapter flows when each paragraph answers the question the one before it raised. Our chapters were built the other way round: from a structure (five pieces, five sections), then filled in. The structure was sound, but nothing forced each paragraph to earn the next one, which is why chapter 4 read like "a random sampling of types" until we spun it.

Three moves that would help, all cheap:

1. **Draft the spine first.** Before any prose, write the chapter as one sentence per paragraph, typically six to ten. Each sentence after the first has to follow from the one before with "so" or "but", never "and also" (the screenwriters' "therefore/but" test). If the spine doesn't flow, the prose won't either, and a spine takes two minutes to fix where a draft takes an hour. The spine also gives the opening and the closing their content (C12: say what's coming, then what you said).
2. **The hand-off test.** For each paragraph, read its first sentence right after the previous paragraph's last one. If the join needs a reader to scroll back, or the new paragraph doesn't say why it's here, it fails. A paragraph that nothing leads into, or that leads nowhere, is an orphan, and it goes.
3. **A think-aloud reader instead of a checklist reader.** Not more agents, but a different brief. One cold reader narrates its understanding paragraph by paragraph: "Now I know X. I expect Y next. This paragraph gave me Z instead." Where expectation and page part, there's a flow break. It finds the problem without proposing prose, so the voice stays one voice.

## Proposed changes to MISSION.md

**Loop step 3 becomes three steps:**

- **3a. The spine.** Write one sentence per paragraph, each joined to the one before by "so" or "but". The first sentence orients, and the last says what the reader now has. When a chapter's structure changes, write a new spine and a clean draft from it, never surgery on the old text.
- **3b. The draft,** written from the spine, as now.
- **3c. The author's read.** Read the whole chapter top to bottom, in the built page, as a reader who has read only what's above. Check:
  - every hand-off;
  - every widget, its caption and anything it draws, against this page;
  - the title against the chapter;
  - any word used in two senses (F1);
  - the opening against the close.

  This read happens after every change, not just the first draft.

**A new rule, G6 or C13: fix by subtraction first.** When a reader stumbles on something unexplained, first ask whether it can leave the page, then whether it can move to where it's needed, and only then explain it in place. Count the new ideas in a paragraph: two Roc ideas is the most a paragraph carries.

**Cold readers:** keep the promise check and the truth-and-order reader, and add one think-aloud read of the whole chapter. Three readers, one voice: I phrase every fix. The readability reader I just ran does this job, and it found more than the axis readers did.

**C12's sync check:** the opening's promises and the closing's summary are written together, from the spine, and re-checked against each other in the author's read.

## What this costs

The spine takes minutes, and the author's read takes about ten minutes for a chapter this size. The think-aloud reader is one agent. Against that, every chapter so far has gone back to you at least twice for things these steps would have caught.

## The decision for you

Do these MISSION changes go in as written: the spine, the author's read, fixing by subtraction, and the think-aloud reader? Then I'd apply them first to the readability report's findings on chapters 2 to 4, starting with a spine for "The pieces as types".
