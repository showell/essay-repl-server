# The Shale book, draft 1

**Read it here:** http://143.244.172.148:9210/shale-book/

This is a rough first draft, eight chapters long, with prose and code only. A cold agent proposed the spine. I wrote the book in one pass, and two cold reviewers read it: one as the target reader, one checking every claim against the code. I applied the truth fixes. The structural ideas are below for you to decide.

## Steve's direction for draft 2

- **Keep:** the practical focus. The book walks the reader through real work.
- **Stronger:** "this is how you should work". Put the reader in a work situation, guiding an agent to write scripts, so the book stops reading like a collection of Steve's useful scripts. The voice is close.
- **Quote code, not header comments.** Header comments help agents search for a script, and an agent reads the whole script before it runs one. A human reads the code, so the code has to be readable. Polish a recipe whose structure is poor before quoting it.
- **Work habits come early.** The tiers and the three reading speeds now wait for chapter 8. They move up front.
- **Done:** the left sidebar, as in the Roc book.

### The one question before draft 2

What is the work situation? My candidate: **a week on a small project.** The reader and their agent take over a modest codebase with a small doc beside it.
- Monday's heredocs answer questions about the code.
- By midweek the questions that came back are recipes.
- Thursday a rule the reader cares about gets plants and a gate.
- Friday the tiers run, from one edit to a release.

Each chapter is a day or half a day. The reader says what they want, the agent writes the Shale, and the reader reads it at the right speed and decides what to keep. The real scripts on this box are the evidence that it works, quoted as code.

The alternative is to keep the work on this box's real projects (the Roc book, the cookbook) and frame each chapter as a task the reader hands the agent. That's more authentic, but less like the reader's own work.

## The spine

The ladder sets the book's order, with gates from page one:

1. **A book published by a script.** This morning's publish tier. Gates are defined, and the ladder and the three reading speeds are previewed.
2. **Reading a heredoc as it scrolls by.** Three questions at scroll speed, the shape of a stop, Lua's look on purpose, bash honestly. `must` is the smallest gate.
3. **A recipe is a heredoc that came back.** rename_words.shale, whole, read at review speed. The wants log is where recipes come from.
4. **Refactoring with the language's own tools.** zig_rename vs sed, `edit` that pins its text down, the conflicts library. The build judges the move.
5. **Plants: proving a judge is watching.** unused_imports, its plants on both sides, its self-test table, check_plants.
6. **A gate holds a count.** book_negatives (held at zero, an exceptions table checked from both sides), and the 900-word rule that became a gate the same day.
7. **A book whose code can't go stale.** Safari's includes and `{{fails}}`, this book's own `{{function}}` include, book_names.
8. **From one edit to publish.** The three tiers, CPU budgets, and the three reading speeds as one habit.

## How it's built

The book lives in the shale repo, on branch `book` (worktree `lanes/shale-book`): `book/book.md`, `book/build.shale` and `book/book.css`. The build pulls every quoted script from its file with `{{file PATH:A-B}}` or `{{function PATH NAME}}`. It renders pages with the essay surface's roc-markdown renderer and gates each chapter at 900 prose words. The longest chapter is 697. The build caught two of its own bugs while I drafted, which the book can tell as a story.

## What the reviewers said

**The target reader** (curious about languages, never seen Shale):
- **Best chapter:** plants. "A check no plant fires could be blind" is where gates first clicked.
- **Locked in:** "A rule in a day", the 900-word rule that became a failing build the same day.
- **Keep as is:** "The shape of a stop", the plants section and "A rule in a day".
- **Over their head:** publish.shale in chapter 1, the maintainer-style headers of run.shale and Safari's build.shale, `keep` vs `fix` kinds, and check_plants' first loop. Mounts went undefined (fixed).
- **The ladder:** it works for chapters 2, 3, 5 and 6. Chapter 4 steps sideways, and 7 and 8 apply gates without climbing (now said in chapter 1).

**The truth reviewer** found 18 problems, all fixed except where noted:
- Chapter 1 said publish.shale carried the book to staging. Its own header says it moves nothing, so it now says the script had to declare the book ready.
- The zig_rename example would leave qualified uses behind, which break the build. It now includes the qualified edit.
- The counts were off: about 60 recipes plus libraries, and about 75 scripts elsewhere.
- The negatives table keeps no sentences today, so the "kept sentence" example now illustrates a kind instead.
- Smaller fixes: the hook also lets an escape through, `edit` needs its text exactly once, check_plants is shared only by the Roc judges, and regexes are a subset.
- **Named in the book as gaps:** quotes by line range aren't anchored, the inline examples are unchecked, and the book's own lints have no plants.
- **Unverified:** 2,214 links and the stage timings come from this morning's publish output, which no repo keeps.

## Proposals for you

1. **Open on a small gate.** The reader suggests leading chapter 1 with the 900-word rule (your sentence, then four lines that fail the build) and moving publish.shale to chapter 8, where the reader can read it. I agree: it puts the gates up front in their most convincing form. The cost: "A rule in a day" leaves chapter 6, which then rests on book_negatives alone.
2. **Make chapter 4 a real rung, or fold it.** As it stands it's a catalogue, and it names move_judge and same_tests without showing them.
3. **Simpler excerpts over maintainer headers.** run.shale's and Safari's build.shale headers are written for a maintainer. The book wants either a reader's excerpt or a header rewrite.

## Improving Shale as we go

The draft has already turned up work for the recipes and the tools, the theme you named:
- **Anchored includes.** Quote by text anchors, as Safari's build does, so a quote can't drift.
- **Run the inline examples** at build time, as SHALE-AGENTS.md's blocks already are.
- **Plants for the book lints** (book_negatives, book_names), so the chapter 6 trust question has an answer.
- **The `**CAPS**:` headers** in look.shale and run.shale, fixed before any chapter quotes them.
- **This book's own prose gates.** It has the 900-word gate so far. Negatives and names come next.

Your note on Python is saved: the book won't push Shale, and a later draft may show a few Python recipes as valid tools for readers who aren't ready to switch.
