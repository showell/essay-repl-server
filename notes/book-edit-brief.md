# Brief for the book's editing agents

*2026-11-06. Draft 1, to be attacked by a cold agent and tried on a canary chapter before the real run.*

These agents have edit power over the prose. Three run at once, each with its own chapters, so their edits don't collide.

## What Steve asked for

Four cold readers each gave four adjectives for a part of the book. Steve's reply: "I agree that we should address all the 'hard ones' from the agent. Use the most restraint when it comes to avoiding repetition. Repetition can serve a very important purpose--it's how people learn. This is one area where we should use a little bit of cleverness and humor in the prose. Expressions like 'Once again, our old friend comes to the rescue: nominal types rule!'. To relieve boredom, make the user guess on occasion with phrases like 'Guess which technique comes up again?'. This is another tricky thing to balance, but I trust the agents here."

## The book

You're editing `canvas_apps/safari/tutorial/tutorial.md` in the roc-apps repo. `{{code ...}}`, `{{module ...}}` and `{{fails ...}}` lines pull source code in. `build/tutorial.md` has them expanded, so read that to see what the reader gets. It's for programmers who have done the official Roc tutorial.

## The hard ones

Fix these, in your chapters only. The quotes are what the cold readers quoted.

1. **Plodding.** The first half reads as "a parts catalog with no tension". The chapters stay where they are, and the first half still holds one frame still. Find the interest in what's there. A chapter can open on a question, a surprise or something the reader wouldn't have guessed. "The grass is whatever hasn't been painted over." is the model: a plain sentence that reframes the thing. Remove lines that apologize for being still, like "Nothing in this chapter moves".
2. **Formulaic.** "By the tenth handoff I could predict the sentence." Vary how chapters open and how they hand off. Some can end with no handoff at all. The "New in this chapter" lists stay.
3. **Promissory.** "A stack of IOUs." Teasing is fine, but too many promises in a row wears the reader out. Cut a promise when the reader doesn't need it to follow along. Keep the ones that create appetite. "The cat's has to wait until we've met the cat, so we'll take the pig first" is the sort to fix.
4. **Proud.** "It keeps stopping to admire the program, and sometimes tells you how to feel." Cut the admiration, and let the code show it. "Which is the best thing in this chapter" is the sort to fix.
5. **Redundant.** "The prose often restates the docstring directly above it." Where a sentence only repeats the doc comment or the code beside it, cut it, or make it say why instead of what.

## Repetition: the most restraint

Don't remove an idea because it came up before. That's how people learn. Opaque types, places and distances, a sighting and a drawing, rule and timeline, and a plain record all come back, and they should.

When one comes back, the book can enjoy it. That's the one place for a little cleverness and humor:

- Greet it: "Once again, our old friend comes to the rescue: nominal types rule!"
- Make the reader guess: "Guess which technique comes up again?"

Each of these has to sit on a real recurrence that the reader has actually seen. Use your own wording, and don't reuse those two lines. Keep it rare, so each one is a small treat: at most four in your chapters, and no two in adjacent chapters. If one feels forced, leave it out. A flat sentence is better than a strained joke.

## Everywhere else: the voice stays

- Plain and warm, like the official Roc tutorial. "We" and "you" are fine.
- Hemingway over Faulkner: short sentences, one idea each. Don't join sentences with commas that could stand alone, and avoid ", but" where two sentences would do.
- Steve prefers plain and tight to charming, outside the exception above.
- No closing morals, no "that's the point of this chapter", no "not X but Y" drumbeat.
- American spelling, except metres.

## What you must not touch

- Any fact, number or claim about the code. You aren't checking facts, and you aren't changing them.
- `{{...}}` lines, widget fences, `dot` fences and tables of values.
- The "New in this chapter" lists, except to reword nothing.
- "A rule turns an `Approach` into a `Stage`, and a timeline turns a `Stage` into an `Instant`."
- "A tour of a tour".
- The order of the chapters.
- `[check: ...]` notes, and "Zooming back out".
- Sentences Steve wrote or praised, which are listed for you where they fall in your chapters.

Keep the book about the same length. An editing pass that adds a paragraph to every chapter has made it worse.

## How to work

Work in your own worktree on your own branch, and commit there. Don't merge or push. Touch no file but `tutorial.md`. Run `canvas_apps/safari/gates/run.shale part=tutorial` before you report.

Report, briefly: the branch head, how many sentences you changed, and a table of your best five changes and every humor line, before and after, so Steve can see the voice at a glance. Then list anything you left alone on purpose, and why.
