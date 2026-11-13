# Looking back on the Safari Ride book

The book ships today: 39 chapters, about 25,000 words of prose and 2,150 lines of quoted Roc. Fifteen diagrams, 19 images and 10 widgets go with it, along with four appendices and an index built from the book itself. It is not parked. Another round of feedback from the Roc Zulip comes next, and the plan for teaching more Roc in the second half is still on the table. But this is a good moment to look back. The next book starts soon.

## What carried the book

**One home for the rules.** MISSION.md held every rule, each with its reason and the date Steve gave it. Every cold agent read it, and so did I after every compaction. It grew from a page of axes into a rulebook: voice, order, truth, pictures, and lately the crash principle (C16), the 900-word limit (A7) and tight transitions (E6). Without it, a 39-chapter book written across many sessions and many agents would have had many voices.

**The code came first.** "When a sentence is hard to write, fix the code" (G1) was the rule I leaned on most. The encounter, rehearsal and truck refactors each began as a chapter that wouldn't come out clean. Rewriting the chapter from a new spine after the fix worked better than patching the old one. Steve's "err on the side of rewrites" was right.

**Readers, each with one job.** No single reader catches everything, so we used many, each with a narrow brief:
- truth and order;
- the animation reader;
- think-aloud;
- the voice reader;
- nitpick rounds;
- flow maps;
- promise hunters;
- the second-half inventory;
- the whole-book cold read.

The voice reader is the clearest lesson. The blind nitpicker read past "Everyone knows what a clock does. The news is what this one refuses to do." A reader armed with the voice rules caught it, along with seventeen of its siblings.

**One voice, many hands.** Late in the run, the fixes went to forks of me, each in its own worktree with one shared rule for borderline cases, and I cherry-picked their commits. Six forks applied about 210 voice fixes in parallel, and the book still reads as written by one author. Readers report, and only one voice writes the book.

**Gates for prose, not just code.** The tutorial build refuses a stale include and a module the book never names. `book_negatives` holds negatives at zero, and its voice mode does the same for disguised negatives and verbs that give code a will. `book_stats` holds every chapter to 900 words. The index flags terms used before they're taught. Each gate turned a rule into a number that can't quietly slip.

## What went wrong, and what it taught

- **Stale builds.** Cold readers who read the main checkout's build were reviewing yesterday's book. Now every brief names the lane's build path.
- **One-shotting.** Drafting much of the book in one shot moved fast and cost us a spine for the whole book. Foundations came late, and the first chapters got crowded. Steve's reply to the cold review names the root cause: not enough time spent on the book's spine.
- **A polish habit that turned into padding.** Ending each section on a "So …" theme sentence made each chapter stronger and the book monotonous. The whole-book reader saw it at once, though no chapter-level reader had.
- **Code quoted twice, and hard code held back.** Each chapter's includes were sensible on their own, but no gate looked across the book. With a large program, the hard functions show up only as annotations.
- **The icons.** Emoji in the contents looked cheap beside the book's own pictures, and a bigger layout didn't help. We cut them within the hour. A short, cheap experiment was the right way to find that out.
- **Small mechanical traps.** A `&` in a sed replacement mangled a test fixture. A stopped job had already committed. A retired page blocked a deploy. Each was caught by a gate or a refusal, and none reached a reader.

## For the next book

MISSION's new section, "Lessons for the next book", has the details. The short version:

1. Define the spine of the whole book before drafting any chapter, and give that step real time.
2. Choose a codebase small enough to quote in full, and quote each definition once.
3. Keep the language's thread strong in every chapter, including the ones about the program.
4. Teach what the language makes unique, at full strength. The floor reader is ready to learn.
5. Write tight transitions from the start: two sharp sentences often suffice.
6. Build the prose gates on day one: negatives, voice, names, length and the index. They're cheap and they work.

## The Shale book

The next book is about Shale, for humans whose agents work in Shale. Its premise is a fun inversion: the reader learns a language they will mostly read, not write. That fits a point Steve made in his reply to the cold review: humans read more code than ever now that agents write much of it. Some of Safari's tools carry straight over: MISSION as a template, the readers, the forks and the prose gates. The difference is the reader's job. The Safari book taught someone to write Roc by reading it. The Shale book has to teach someone to judge what an agent wrote. That makes a spine worth settling first, before a single chapter.
