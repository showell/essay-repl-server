# A riff on the Shale book

Your replies on the openings moved the center of the book. Safety is table stakes. "A better bash" is part of the premise, though it isn't the point. The point is what piles up: recipes. Here I riff on that, loosely, to find a spine. Nothing here is decided.

## Shale in the first sentence

> Shale is a programming language written by agents, for agents.

That sentence holds two true things. Agents write Shale scripts, and agents also built the language: the interpreter, the prelude and the cookbook. A human set the taste and said no a lot, and the reader should meet that human early. It also sets up the turn the book needs. If agents write it and agents run it, why should a human learn it? Because the human reads it as it scrolls by. You said you don't read the scrollback, you read the Shale as it passes. That's the real reading speed the book has to teach: a script read at scroll speed, judged in a few seconds, then trusted or stopped.

## Actions speak louder

I counted what Shale does on this box today. There are about 130 Shale scripts across eight repos:

- **The cookbook, about 80 recipes.** These are general tools:
  - finding and showing code (`look`), and running a program to get its verdict (`run`);
  - resolving merge conflicts (`conflicts`), building on GitHub (`gh_build`), reading Zulip (`zulip`);
  - word renames across a tree (`rename_words`);
  - a whole shelf of hunts over Zig and Roc: names, nesting, dead code, clones, seams, unused imports, stacked arguments, type walks.
- **The Safari book, 18 scripts.** Shale builds it (`build.shale`), indexes it (`book_index`), counts it (`book_stats`), lints its prose (`book_negatives`, `book_names`), gates it (`run.shale`) and publishes it (`publish.shale`). This morning's deploy was one Shale run of five minutes covering gates, the compiler check over 59 apps, the book build and a link check of 2,214 links.
- **Every other project, a handful each.** roc-chat deploys and verifies with Shale. angry-gopher lints with it. The essay surface reviews code with it.

That list is the book's argument. Nobody would call a Python replacement the tool that publishes a book. Shale is the language an agent's habits harden into.

## The ladder

Watching the cookbook grow, I see one shape repeat:

1. **A heredoc.** An agent needs an answer once: every line holding `job_alive`. It writes ten lines, runs them, reads the output, and the script is gone.
2. **A recipe.** The same question comes back a third time, so the ten lines get a name and a file, with arguments: `look.shale find=job_alive`.
3. **A recipe with plants.** The recipe starts making judgments (this name is vague, this import is unused), and a judgment needs proof. So it gets plants: small files that must trip it and small files that must stay quiet. `name_hunt` alone has dozens.
4. **A gate.** The judgment becomes a count held at zero, run on every commit. The Safari book's negatives lint climbed this ladder in about a week.

Each rung is a small, readable step up from the last, and each one is something a human reads and approves. That could be the book's spine: one ladder, climbed several times, with a different task each time. A codebase task, a docs task, a book task, a deploy.

It also answers lesson 2 from the Safari retrospective: choose a codebase small enough to quote in full. Recipes are naturally small. Most fit on a page, so the book can quote each one whole.

## Reading, in this light

The reading knowledge (opening 3) gets sharper here. The reader learns to read Shale at three speeds:

- **At scroll speed:** a heredoc going by. What does it touch, what does it run, how did it end?
- **At review speed:** a recipe the agent proposes to keep. Is it named well? Does it fail loudly? Would I want this again?
- **At trust speed:** a gate. What does it hold, and do the plants prove it's watching?

Each speed needs different knowledge of the language. Scroll speed needs `run`, its keep and its timeout, and the shape of a stop. Review speed needs functions, arguments and `fail`. Trust speed needs plants and held counts. So the language can unfold in the order the reader needs it.

## Familiar on purpose

You noted that our rule about comparisons flips here. In the Safari book we kept other languages out. In this one, Shale borrows from languages the reader already knows, and saying so is honest and fast:
- It looks like Lua: `local`, `for … in … do`, `..` for joining.
- `run` does the job of a shell's backticks, with a timeout, a keep and an exit code.
- The text functions fill the space where `grep` and `sed` would go.

Every difference from Lua is a deliberate choice, and those choices are where the book should spend its words: no closures, functions declared above their use, a missing key stops the run, no floats. Each choice makes a script easier to read at scroll speed, and the book can show how.

Bash stays in the book as the foil, mostly in the first chapters: a hung test, a flooded screen, a `sed` that ate a fixture. After that, the recipes carry the argument.

## The reader

Someone curious about programming languages and open to agents. They may never have run an agent with real permissions. The book gives them a working picture of what that looks like on a box where it's routine, and one language to read it in.

## What the book promises

A tour of useful recipes for building codebases and books, each one read in full, with the language taught along the way at the speed each reading needs.

## Where I'd go next

An inventory of the recipes that matter, done the way Safari's flow maps were. Which recipes earn a chapter? Which rung of the ladder does each one show? Which Shale feature does each one teach first? Out of that table, the spine should be visible.
