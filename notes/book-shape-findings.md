# What the canaries found: the book's shape

*2026-11-06. From eleven cold reviews and four adjective readers. No prose has changed because of this yet.*

## How the briefs did

All six reviewers passed. A planted wrong number sat in every copy, and no reviewer reported it, so the fact-checking line held. Every planted fault was caught: the sales line, the "point of this chapter" line, a padding paragraph, an untaught `where`, and a conductor-and-orchestra metaphor. Paired runs agreed with each other on their main findings.

I'd skip the full run of the reviewers for now. The two editors and names already read the whole book, and they've given us more than we can act on. Better to fix the shape, then run them on the result.

Adjectives from the reviewers, for flavor: *patient, dutiful, clever, airless; patient, sturdy, list-like, withholding; dense, remote, assured, clipped; capable, self-assured, earnest, scoreboard-minded; plain, sure-footed, dutiful, name-heavy.*

## The shape: five decisions for you

The two editors worked independently and landed on nearly the same list.

### 1. Hold a real frame

Both editors said the same thing: the part called One frame never holds a frame. It's 14 chapters and a third of the book, and only three have a widget, none of which shows a frame. "They're given an inventory and told it's a picture."

The material is there. Step 1,570, with the cat frozen in the lane, already comes back in The modules, The rider, Proving it and The platform.

**The proposal:** name step 1,570 as the frame we're holding. A cold agent builds one paused picture of it with layers. Each chapter of One frame switches on its own layer: the grass, then the sun, the sky, the mountains, the trees, the road, and so on. A running count of shapes climbs toward the frame's real total, so that the table in The platform lands as a number the reader watched grow.

Nothing moves, and it answers "plodding" directly. **I recommend this.**

### 2. Name the book's big idea, and keep asking its question

Both editors gave the same one-line summary of the book: keep three fields, and work everything else out each frame. Both then said a reader wouldn't give that answer. They'd say "a tour of a game with a lot of opaque types".

Two things go underground. "How Roc holds up" is asked in the Introduction, and isn't asked again for 4,400 lines. The big idea, "worked out, not stored", is the one main pattern that never gets a "Call this" moment. Its name appears only in the appendix.

**The proposal:** give it its moment in The ride instant. In One frame, run a light question through the chapters: how much of this does the ride remember? The answers are already scattered around: "No frame ever plants a tree", "A bend is kept nowhere". Then the three fields land as the payoff. **I recommend this too.**

### 3. Give Rehearsal its own chapter

Both editors called it the book's best idea, and it's buried as the fifth section of a 602-line grab-bag. The rider's chapters open a tab for it, and the answer arrives 2,100 lines later.

One editor would put it right after What a cat does to the rider, to close Motion. The other would put it right after The math layer, which changes less. The math chapter itself says the rider's family and the camera's family "don't otherwise meet", so the first should work.

**I'd close Motion with it.** The math layer then shrinks to the geometry floor, which is what it really is.

### 4. Make Proving it show a change

Every reviewer who saw this chapter said the same thing. It asks the book's most important question, and then lists tools. "The biggest event in the program's life gets three sentences."

The skeptics add the missing costs. What happens when the picture is *meant* to change? Who re-blesses a hash? What does a player get when a crash fires?

**The proposal:** tell one real story, in which a change is made, the compiler catches one thing, a hash catches another, and something gets through. We have one running right now. The math agent is replacing hand-written math with builtins, and frame hashes may move, so that's a real re-blessing with real numbers. Costs get a few flat sentences.

"Holding the first 2,048 instants was a perfectly consistent thing for a list to do" came up three times as the most trusted line in the chapter. It admits a failure. More of that voice is the fix.

### 5. Cut the markers, or most of them

Names called this "the next score". Safari Ride has real trees, so 🌳 on a block about the sky first reads as tree stuff. `match` has real branches, so "it's a branch" means two things in the sentence where the book is at its sharpest. "The bottom of the tree" is where the leaves are, which is upside down. The markers also fade: 8 of 34 chapters use them, while the Introduction ends on their legend, which three reviewers marked as a place to stop.

**I'd remove all four,** keep "leaf" as a plain word where it helps, and let the Introduction end on the tour. The other choice is to keep them only in The cat, and introduce them there.

## Smaller shape notes

**Walking the call graph.** From the gaze on, chapters follow callers, not the thing. "Its caller gives…", "It's called through a smaller function…". Fix: one claim per long chapter, and a listing stays only if it serves that claim. The rider's gaze is the worst case, at 247 lines for a glance at a pig, so that's on me. Meanwhile "This is the only feedback loop in the design" gets four sentences, and could use the space.

**The reader is missing.** Across three chapters, "we" and "you" appear on two or three lines. The Roc tutorial has them on 73 of 226. That's the gap between plain and warm. It can be fixed by changing the subject of a few sentences per chapter, without adding any length.

**Fact-bag paragraphs.** After big listings, short sentences add up to a paragraph with five unrelated ideas. Both tone runs ranked this first. The fix is one point per block.

**Recurrences come back flat.** Both editors noticed that the humor you asked for has nowhere to land yet: "It sits below the block, so it's private" appears three times, as a footnote. Patterns also get named too late, all after line 1,966, so the first half has nothing to call back to.

**The throttle.** The chain is taught out of chain order, and most of its links are deferred. The graduate never got to hold one whole limit. Take `bend_brake` first.

## Names

- **Sighting** slides between the record and the thing that looks. Keep it for the record.
- **Chain:** the "chain of limits" collides with the `Chain` module. The chapter already says "a line of limits".
- **Open** means both unwrapping an opaque type and an open record. Say "unwrap" for the first.
- **Stretch** has four jobs. **Beat** clashes with wing beats. **Frame** is used for a pose in "the first frame of its flight".
- **Sum** is used for any calculation, and it hints at sum types.
- **"Score"** is still in the code, as a binding in `Animation.Timeline`, and it shows on the page. That one's a small rename.

## Zooming back out

Both editors said what it has to deliver, and they mostly agree:

- a verdict on how Roc held up, with the costs;
- the name of the one idea, showing that step back, the stateless cat, the frame hash and rehearsal are all the same idea;
- one tick of step 1,570, end to end, through real names;
- a reason to go back to the widget, with a few moments to watch for;
- the "yet" from "It doesn't have game mechanics yet". What would it take to add a game? Keeping score would be a fourth field.

And it should be short.

## Must not be broken

"This is the module that stops that line, all of it." The cat and the bird as a test of `Animation`. "The grass is one rectangle." The tiny chapters as rests. "Nothing has to be undone." "`Bike` has never heard of a gaze." The pretend riders. "The JS knows nothing of cats, and the Roc knows nothing of canvases."

## One order question

One editor asks whether Proving it should come after The platform, so the reader goes into the ending straight from the proof. I'd leave it, but you'd asked to hear this kind of thing once.
