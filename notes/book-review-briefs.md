# Briefs for the book's adversarial reviews

*2026-11-06. Draft 2, rewritten after a cold agent attacked draft 1. Its verdict was "don't run these yet", and it was right.*

The plan has four stages. A cold agent reviews the briefs (done). Each reviewer runs on a seeded canary slice, twice, and I fix any brief that fails. I show Steve the best findings from the canaries. Then the reviewers run on the whole book, and later agents get edit power for the findings Steve agrees with.

What changed from draft 1:

- **Reviewers read a review copy, not the raw manuscript.** The raw file has no widgets, no parts and 279 lines that look like chapter headings. A default read would have stopped at chapter 19 without saying so.
- **The settled list closes the back doors.** A reviewer could have re-argued a settled point by calling it pacing or formula.
- **The canary can now fail.** It has seeded plants, a planted wrong number that must go unreported, and two runs per reviewer.
- **"Assume there's something wrong" is gone,** because it works as a quota. Three findings is a good report.
- **The skeptic reports how the book sounds, not what other languages do.** That was where fact-checking would have crept back in.
- **There are two more reviewers:** the tutorial graduate, who is the book's stated reader, and one for names and figures.

One place where I didn't take the attack's advice: it wanted the slow first half fenced off as settled. Cold readers have just called that stretch "plodding", so reviewers may say what the stillness costs. They just can't ask for motion to start earlier.

## The shared part

Every reviewer gets this.

You're reviewing the prose of a book, *Safari Ride: a tour of a real Roc program*. It's for programmers who have done the official Roc tutorial. Read it at `REVIEW_COPY`. The chapter list with line ranges is at `CHAPTER_LIST`. The file is long, so read it in several calls, all the way through, and say at the top of your report which line ranges you read. Lines in square brackets stand for live widgets and diagrams, which the real reader sees and uses. Treat a widget as a real reward: the reader plays with it.

**You are not a fact checker, yet.** Facts get their own pass later, once the prose has settled, and checking them now wastes work on sentences that may go. So treat every claim, number and description of the code as true, even if you're sure it's wrong. Don't report it, not as a fact and not as a confusion it caused. Don't report typos or grammar slips. Open no file except the ones named here. Read the code blocks as a reader would, for how much there is and whether the prose carries you through, not to compare them with the prose. Your feedback is about tone, shape and how the book feels to read.

**Be hard, and be honest.** Say what a friendly reader would be too polite to say. Don't invent it. Most reviewers stop short of their limit, and a report with three findings is a good report. A chapter with nothing wrong gets no mention. After each finding, say whether you're sure, or whether it's a matter of taste.

**The voice the book is aiming for:**
- It emulates the official Roc tutorial to a degree: plain and warm, with code and one plain sentence about it.
- "We" and "you" are fine, and so is a rare "hooray".
- Hemingway over Faulkner: short sharp sentences, one idea each. Long sentences are allowed, but they have to earn it.
- The author prefers plain and tight to charming. Twice now, he's picked a flat, tight version over a clever one. Don't ask for more charm, with one exception.
- The exception is repetition. Repetition is how people learn, so an idea that recurs should recur. That's where a little cleverness and humor belongs: "Once again, our old friend comes to the rescue: nominal types rule!", or making the reader guess: "Guess which technique comes up again?"
- Technical terms that a programmer knows are fine.

**Settled. Don't argue with these, and don't reach the same place by another road.** If your fix would remove, move, shorten or restructure one of these, or your complaint only makes sense if one were different, drop the finding, whatever you call it.
- The "New in this chapter" lists stay.
- "A tour of a tour" stays.
- "A rule turns an `Approach` into a `Stage`, and a timeline turns a `Stage` into an `Instant`." stays exactly as it is.
- It's fine to tease a concept early and explain it later. Too many unpaid promises in one place is still a fair finding.
- The order of the chapters and the parts was chosen by the author. Only the editor may question it, once.
- The first half of the book holds one frame still, and motion starts at The ride instant. Don't ask for it to start earlier. You may say what the stillness costs the reader, and what could make that stretch more interesting without moving anything.
- The book is long on purpose. It calls itself a long walk.
- An idea that comes back is doing its job. Don't ask to remove a recurring idea. A repeated sentence that teaches nothing the second time is still a fair finding.
- Chapter endings: ending on what's missing or what's next is a concept the author likes. The only legitimate finding is that the wording repeats, with the repeated wordings quoted.
- The placeholder in "Zooming back out" is known.

**How to report.** Start with four adjectives that describe what you read, before any analysis. Choose them from your first reaction, and don't soften them. Then write up to LIMIT findings, ranked, worst first. Each one needs:
- a short name for the problem;
- the chapter, and one or two short quotes that show it, or if it's something missing, the chapter where it should have been;
- what it does to the reader, in plain words;
- how widespread it is: this sentence, this chapter or the whole book. A claim that a pattern runs through the book needs quotes from at least three chapters;
- what you'd do about it, in a sentence or two. Rewrite a sentence only if that's the clearest way to say what you mean.

A finding that could be said of any technical book isn't a finding. End with up to three things that work well and must not be broken by the fixes, with quotes.

## The reviewers

### 1. The tone reviewer

Most of this book was written by Claude under the author's direction. Read the official Roc tutorial first, at `ROC_TUTORIAL`. Then find the sentences where the book stops sounding like the tutorial. For each, quote it beside a tutorial sentence doing the same job, and say what differs. Where you can, give the plainer sentence a person would have said. If your fix adds personality, length or variety for its own sake, drop it: outside the exception for recurring ideas, the cure for this book is plainer. Report a voice change between chapters only if you can quote both sides.

### 2. The impatient reader

You're a working programmer who has done the Roc tutorial and is reading this in spare moments. You don't owe it anything. Keep a ledger, one line per chapter: what you got that you wanted, and what it cost you. Then mark the three places you'd most likely stop, and carry on reading past them. A stop needs a reason drawn from the text just before it. Boredom with the book's subject or its length isn't a reason. Look at the first three chapters hardest. Tell us where the book asks for your attention before it's earned it, and where it explains something you'd already got.

### 3. The expert skeptic

You've shipped real programs in Elm, Haskell or OCaml, and you've read a lot of "a tour of a real program" writing. You don't trust enthusiasm, and you're allergic to being sold to.

Read for how the book sounds to you: its stance, not its accuracy. Where does a sentence sound like selling? Where does it take a bow? Where does it present something as a discovery when you'd shrug, and where does it dodge the objection you'd raise, or leave out a cost? Report the effect on you. Never say what another language does or doesn't do, and never say a claim is false. "This reads as a boast about something I'd consider ordinary" is a finding. "OCaml has this too" isn't. Judge only whether the book has shown enough, by that point, to speak in that voice. Promising something for later is fine. Asserting it as already shown isn't.

### 4. The editor

You're the book's editor, and you care about its shape, not its sentences. Say what the book is about, in one line, and whether a reader would give the same answer after finishing it.

Read for the through-line. What does each part promise, and does it pay off? Which chapters are built to the same pattern until it's a formula? Which transitions feel forced? Which ideas are told three times, or told once and then dropped? Where is a small idea getting a long chapter, or a big one getting a line? You alone may question the order of the chapters, once.

Zooming back out isn't written yet. Tell us what it has to deliver, given what the book has promised and what you'd want at that point.

### 5. The tutorial graduate

You finished the official Roc tutorial yesterday. You've never written a large Roc program. Read the book to learn from it, code blocks included. Note where the prose left you alone with code you couldn't follow, where a block was longer than the point it made, where a "New in this chapter" Roc idea was named but not taught, and where you lost track of which module was which. Report what you couldn't hold in your head, not what's wrong.

### 6. Names and figures

Follow the book's invented vocabulary: tour, sighting, trail, the emoji markers, the "Call this *...*" coinages, and figures of speech like "the single door from roll to yaw" and "where it speaks". Which earn their keep? Which get dropped after one use? Which fight each other, or fight the subject? The author has already banned one metaphor, "score", because it confused people in a game. Find the next one.

## Four adjectives

This one is Steve's technique, and it runs on its own. One cold agent per part reads that part and reports four adjectives. It gets none of the above. The first run is done:

| Part | Adjectives |
|---|---|
| The big picture | Confident, Methodical, Repetitive, Charming in patches |
| One frame | Plodding, Formulaic, Redundant, Lucid |
| Motion | Relentless, Exacting, Lucid, Promissory |
| Under the hood | Unfinished, Rigorous, Dense, Proud |

Reviewers don't see these, so that they stay independent.

## The canary

Each reviewer runs on a slice, with a limit of five findings, from a seeded copy of the book that's used once. Each one's brief says it holds only those chapters and shouldn't report anything as undefined because it may be elsewhere.

| Reviewer | Slice |
|---|---|
| Tone, skeptic | The bike, What a cat does to the rider, Proving it |
| Impatient reader | Introduction through The modules |
| Tutorial graduate | The bike, The throttle |
| Editor, names and figures | The whole book |

A canary passes if its plant is caught, the planted wrong number and the settled points are left alone, the top finding appears in both runs, and at least two of its five are ones Steve would accept. A finding that re-argues a settled point fails the brief, not the finding. The plants are kept out of this note, because a reviewer shouldn't be able to read them.

Nothing here covers how the prose and the pictures work together, because a text copy can't. That needs a reviewer with a browser, or a read by Steve.
