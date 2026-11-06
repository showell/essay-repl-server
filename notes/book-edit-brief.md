# Brief for the book's editing agents

*2026-11-06. Draft 2, after a cold agent attacked draft 1. It's tried on The sky, twice, before the real run.*

## The stage we're at

The book is still finding its shape. It has to read like a plausible tutorial, so that it can be judged, and it doesn't have to be finished. Steve: "we don't have to sweat every detail." Thorough passes on facts and transitions come later. So make one pass, fix what's named here, and stop. Don't polish.

## The book

You're editing `canvas_apps/safari/tutorial/tutorial.md` in the roc-apps repo, for programmers who have done the official Roc tutorial. `{{code ...}}`, `{{module ...}}` and `{{fails ...}}` lines pull source code in.

Read the whole book first, at `/home/steve/showell_repos/roc-apps/canvas_apps/safari/tutorial/build/review/book.md`, which shows the code and marks the widgets. It's long, so read it in several calls. You need all of it to know what the reader has already seen. The chapter list with line ranges is `chapters.txt` beside it. Then edit only your own chapters, in `tutorial.md`.

The book has four parts. The big picture sets things up. One frame holds one frame still, step 1,570 with the cat frozen in the lane, and walks through what's on it: nature, then man-made things, then critters that stand still. Motion lets it move: the passage of time, vehicles, critter motion and rehearsal. Under the hood is the math, the proof and the platform.

## What to fix

Cold readers called parts of the book plodding, formulaic, promissory, proud and redundant. Reviewers added more. Steve agreed with all of it. Here's what each means for you.

**Plodding.** The first half reads as "a parts catalog with no tension". The chapters stay in order, and the stillness stays. Find the interest in what's there. A reader may land on any chapter cold, because each one is its own web page, so its first sentence names the subject in plain words and needs nothing from the chapter before. Put the interest in what it says. Models: "However far the rider goes, the mountains never get any closer." and "The grass is one rectangle." Leave openers like those alone. Don't start a chapter on a pithy reframing: those are earned by the paragraph above them. A question opener must be one the reader could really ask, and you get at most one. Remove lines that apologize for being still.

In One frame, run a light question through the chapters: how much of this does the ride remember? The answers are already there: "No frame ever plants a tree", "A bend is kept nowhere". Ask it in a few words, in a few chapters, not all of them. It sets up the three fields in The ride instant.

**Formulaic.** Vary how chapters open and how they hand off. Ending on what's next is a concept Steve likes, so keep it, and fix the wording that repeats: "That's X. Next, ...", and "has to wait". A chapter now and then can just end. The "New in this chapter" lists stay exactly as they are.

**Promissory.** "A stack of IOUs." Cut a promise when the reader doesn't need it to follow along, and keep the ones that create appetite. Only cut a promise if both ends are in your chapters. If its payoff is in someone else's, leave it, and list it in your report if it irritates you.

**Proud.** "It keeps stopping to admire the program, and sometimes tells you how to feel." Cut the admiration, and let the code show it. No staged contrasts with an unnamed worse world, such as "normally takes some doing". No closing maxims of the form "X doesn't do A. It does B."

**Redundant.** Cut a sentence only if it repeats text the reader can see on the same screen, it isn't the sentence that teaches an item in this chapter's "New in this chapter" list, and it doesn't name or define a term. If it might be the lesson, leave it, or make it say why. An idea from an earlier chapter is never redundant.

**The reader is missing.** The book reports to you where the Roc tutorial walks with you. Across three chapters, "we" and "you" appear on two or three lines. Change the subject of a few sentences per chapter, where the reader's eye moves to something new: "Let's look at the step." This adds no length.

**Fact bags.** After a big listing, short sentences can add up to a paragraph with five unrelated ideas. Pick the one thing the code is there to show, and say that. Move the others to their own short sentence, or cut them.

**Walking the call graph.** From about The beacons on, chapters follow callers: "Its caller gives...", "It's called through a smaller function...". Give a long chapter one claim. A caller hop stays only if it carries an idea. You may drop a `{{code}}` listing that serves nothing, and say so in your report.

## Repetition

Steve: "Use the most restraint when it comes to avoiding repetition. Repetition can serve a very important purpose--it's how people learn. This is one area where we should use a little bit of cleverness and humor in the prose. Expressions like 'Once again, our old friend comes to the rescue: nominal types rule!'. To relieve boredom, make the user guess on occasion with phrases like 'Guess which technique comes up again?'. This is another tricky thing to balance, but I trust the agents here."

So when an idea comes back, the book can enjoy it. It has to be a real recurrence the reader has seen. Keep it rare, and let it replace a sentence that's already there. Warm and slightly corny beats witty. A few exclamation marks are fine, at these moments only. A guess has to come before its answer. Zero is a fine result for a chapter, and a flat sentence beats a strained joke.

Places that suit it, as suggestions:

| Chapter | Where | |
|---|---|---|
| Herds | "It's the same record again" | "By now you can guess what it's made of." |
| The sky | "another small opaque type" | |
| The throttle | "places and distances again" | "Places and distances have followed us to the throttle." |
| The bird | "Beside it, again, is the cat's rule." | |
| What a cat does to the rider | "`Attention` is another opaque type." | A guess |
| The math layer | "the opaque type doing the job of a unit" | "The opaque type that refused to add 7 to a clock now does the job of a unit." |

Avoid these: "old friend", "you guessed it", "sound familiar", "look who's back", "trusty", "strikes again", and safari puns. "Sighting", "step", "still", "gate", "rule" and "track" are terms in this book, so no jokes on them. The book's word is *opaque*. *Nominal* means `:=`, first met in The ride instant. "Places and distances" is named in The beacons, so don't use it earlier.

## Words

- **Sighting** is the record. For the thing that makes one, use the module's name.
- **Unwrap** an opaque type. **Open** is for open records.
- **Chain** is the `Chain` module. The throttle's pattern is *the line of limits*. Change it everywhere it appears, including the appendix.
- **Frame** is the whole picture. Say "pose" for a still, as in "the first pose of its flight".
- **Sum** is real addition. Otherwise say "calculation" or "arithmetic".
- **Stretch** is a part of a timeline. Say "part" or "span" for the ruler, and "length of road" for the road.
- **Beat** is the animation's unit. For wings, say "flap".

## Don't touch

- Any fact, number or claim about the code. You aren't checking facts or changing them. New sentences may only say what the book says elsewhere.
- `{{...}}` lines, except to drop one, and widget and `dot` fences, tables of values, chapter and section titles, and the "New in this chapter" lists.
- The sentences that name the patterns, "Call this *...*". They define what the appendix lists.
- "A rule turns an `Approach` into a `Stage`, and a timeline turns a `Stage` into an `Instant`."
- "A tour of a tour".
- `[check: ...]` notes.
- These, which reviewers said must survive: "This is the module that stops that line, all of it." "The grass is one rectangle." "The grass is whatever hasn't been painted over." "Nothing has to be undone." "Holding the first 2,048 instants was a perfectly consistent thing for a list to do." "though `Bike` has never heard of a gaze". "The JS knows nothing of cats, and the Roc knows nothing of canvases." The pretend riders in Rehearsal.

## The voice

These describe the sentences you write. They aren't a sweep of the book. Plain and warm, like the official Roc tutorial. Short sentences, one idea each. Plain and tight beats charming, outside the humor above. American spelling, except metres.

Replace, don't add. The book should stay about the same length or get shorter.

## When you're done

Make one pass, and change a sentence only for a reason above. Then read each chapter's first sentence with the chapter before it hidden, check that each item in each "New in this chapter" list is still taught, and stop.

Work in your own worktree on your own branch, from the commit you're given. Commit there, and don't merge or push. Touch only `tutorial.md`. Run `shale canvas_apps/safari/tutorial/build.shale <<'TAG'` with a bare `TAG` line to check that it still builds, and leave the gates to the orchestrator.

Report, briefly: the branch head, how many sentences you changed, every humor line, before and after, and your best five other changes, before and after. Then list anything you left alone on purpose.
