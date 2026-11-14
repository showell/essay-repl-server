# Shale, read cold: an initiative

*2026-11-14. A proposal for your replies. The book reads Shale through a newcomer's eyes, and that newcomer is usually you, a little earlier. So the book becomes a forcing function: nuisances too small for you to notice get fixed in Shale itself.*

## The rule, as I understand it

When you stand in for the reader, you're mostly speaking for yourself. A complaint that would help you too goes into Shale. A complaint that only a newcomer would have stays in the book. Short variable names are the counterexample: you don't mind them, so the book explains them and Shale keeps them. Verb names for scripts are the other kind. They're better for everyone, so the files get renamed.

So the test for each nuisance is: **would a fix help Steve, or only the reader?**

## What today already turned up

Every item below came up today, from the book, a reviewer or a cold agent. None was invented for this note.

- **Names.** Runnable scripts are named for their topic, not their action: `disk.shale`, `http.shale`, `audit.shale`. And the commit check printed `fast: PASS` after it had been renamed. *Fixed for the commit check; the rest is the sweep that's queued next.*
- **A doc that contradicts itself.** The agent guide said one capture group, and also nine. *Fixed.*
- **A value that lies when you print it.** A regex match's `groups` held two entries, but `json_write` showed `[]`. *Fixed.* The agent that fixed it named the deeper hazard: a table's kind is stored apart from its contents, so the two can disagree again somewhere else.
- **`lines` takes a string, not a file.** It cost Session 1's very first script, and it's in memory as a known trap. The name invites the mistake.
- **`now()` is when the run started,** the same at every call. The cold agent nearly missed that.
- **`shale_tokens` takes a path, not text,** so the highlighter writes each code block to a scratch file just to lex it.
- **Cookbook headers** like `**THE DISK'S FREE SPACE, A RUN STOPPED BEFORE IT FILLS**:` break the comment style you set for every language.
- **`roc/findings.shale`** is general, but it lives under `roc/`.
- **There's no cookbook index.** A cold agent finds recipes with `glob` and by reading headers, and it can't tell a recipe it runs from a library it loads until it opens the file.
- **The consumers gate** took 575 s against a 590 s timeout.
- **Starting a Shale lane** fights the harness. Today's agent got around its refusals by using the gate's escape.

## The initiative, in five passes

1. **The name pass** (queued next). Runnable scripts get verbs and libraries get nouns, in the cookbook and in essay-surface, with every reference in every repo. Output lines match the new names.
2. **The cookbook pass.** A `cookbook/README.md` gives one line per recipe and marks whether you run it or `use` it. Headers move to the plain comment style. General helpers move out of language folders. The gate's refusal already names the docs; it can name the cookbook's index too.
3. **The doc-truth pass.** A cold agent reads every Shale doc and checks each claim by running it, the way the `groups` bug was found. It reports contradictions and stale lines, and fixes them.
4. **The trap pass.** The language-level nuisances, each a small lane with tests and the full gates:
   - `lines` that takes a file by mistake should stop with a clear message, or the name should change;
   - `now()` should say in its name or its docs that it's the run's start;
   - `shale_tokens` should accept text;
   - a table's kind should follow from its contents.
   These change the language, so I'll bring each to you one question at a time before building it.
5. **The cold-start benchmark.** Today's onboarding test becomes a recipe we rerun after each pass, with harder tasks added: write a recipe, and fix a small Shale bug. Each pass should make the next cold agent faster. The time and the number of calls are the measure.

## My recommendation

Start with passes 1 and 2 together, since both touch the same files and neither changes the language. Then pass 5, to set the baseline before the doc and trap passes, so we can see whether they helped. Passes 3 and 4 follow. Each pass is a cold agent in its own lane, with Shale's tests, consumers and the doc check before it merges.

The book benefits directly. Session 6, "the language gets better", already tells one such change, and this initiative supplies more real ones. It also covers the theme you raised earlier: agents fix compilers well for the same reason they write them well.
