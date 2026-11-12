# The book's problem statement

## What the book is

Safari Ride is a book about building a non-trivial, highly animated program in Roc. That sentence is the whole problem statement, and each of its parts carries weight.

*Non-trivial* is the promise Aurélien named back to us without being asked. A reader who has finished the official tutorial knows what a record is and what `match` does. What that reader can't get from the tutorial is how a program of a hundred modules is structured, and how Roc's larger ideas, such as opaque types, type variables and `where`, earn their place by solving a concrete problem. Aurélien called that "the main value for a Roc beginner who has gone through the tutorial". It's our mission, in a reader's words. A toy can show a feature. Only a real program can show why the feature is there.

*Highly animated* picks the kind of program. We could have picked a compiler, a chat server or a spreadsheet. We picked a ride because every frame of it can be seen. When the code is right, the cow stands on the grass; when the code is wrong, the cow floats. The reader can judge the program with their eyes before they can judge it with their Roc. No other kind of program gives a learner that check for free.

*In Roc* is the center. The animation is the subject matter; Roc is the subject.

## Two threads

The book runs on two threads at once, and the reader pays attention to both.

The first thread is the animation: what a frame is, why far things look small, why the near tree covers the far one, how a step moves the world on. The second is Roc: how you say any of that in a language with no mutation, with tags instead of class hierarchies, and with types that leave a wrong state nowhere to live.

The threads are in tension because attention is finite. A paragraph that teaches perspective and a type variable at once teaches neither well. Anton saw that first, and C13's "two new ideas a paragraph, and an animation idea counts" is our answer to him.

The threads are also synergistic, and the synergy matters more. The animation supplies the *need* for each Roc idea. A reader doesn't care about a type variable in the abstract. They care when trees, cows and towers all have to go through the same camera, and `Placed(kind)` lets one type serve all of them. In the other direction, Roc gives the animation its *shape*. The pipeline is easy to understand because each stage is a type: placed, sighted, rendered. A TypeScript reader would build the same ride with the same math, but the program would come out shaped differently. The book is about that shape. It never says "as opposed to TypeScript". The rule against comparisons stands. Still, the contrast is in the reader's head the whole time, and every chapter quietly answers it.

So the book's unit of value is a moment where the threads meet. An animation problem makes a Roc idea necessary, and the Roc idea makes the animation readable. "Asking a kind" is that moment: one function renders five kinds of thing, because a `where` clause constrains a type variable. Those moments are what we're selling.

## What the opening owes

The first chapter has a job big enough on its own, and you put it well: say what the book is about, show the app, and describe it. The description repeats what the reader just watched, and the repetition is deliberate. It hands the reader the book's vocabulary (the rider, the truck, the herds, the frame) before any code uses those words. Syntax on page 1 competes with that job, and the cow snippet proved it: it read as clutter. The Introduction is the book's prologue, and a prologue doesn't need code.

The opening does owe the reader both threads, though, and today it pays only one of them. The Introduction pays in animation: the ride runs. The problem pays in animation and engineering: five pieces, a plan. Platforms pays in Roc, but in Roc's dullest coin, the wiring. The first Roc that shows any of the language's character arrives in The pieces as types, and the first Roc that shows Safari's character arrives in Things. A reader who came for Roc, which is everyone who came, goes four chapters without the thing they came for. That's the debt Aurélien felt. He described it as "the code starts too late", and his cure was a tiny scene. The real problem is narrower than "too late": the Roc thread sits silent while the animation thread speaks.

That's why "Roc at a glance" as a second chapter is an interesting idea. It isn't a syntax lesson, and it isn't hello world. It's the Roc thread's equivalent of the running ride: the reader sees what this language feels like before the book asks them to learn it. The ride says "this is what we'll build". Roc at a glance would say "this is what it's built with". Then the two threads have both been introduced before The problem sets them to work together.

## Moby Dick

The whale doesn't surface until chapter 133 of 135, and the book works anyway. It's worth being precise about why, because it's also why the Zulip criticism is fair.

Melville never lets the whale be absent. In chapter 3, Ishmael stands in the Spouter-Inn in front of a dark, smeared painting he can barely make out, and it turns out to be a whale. In chapter 36, Ahab nails a gold doubloon to the mast and names Moby Dick, and from then on the promise is spoken aloud and the crew is sworn to it. The whale is present as a promise, a rumor and a picture long before it is present in the water. The reader waits willingly because the wait is filled with the thing waited for.

Each chapter also pays on its own. Queequeg, the sermon, the try-works, the squeeze of the hand: each is a vignette, and a reader who opened the book there would be rewarded. Melville spends the reader's patience freely, but he never spends it for nothing.

The cautionary half: Moby Dick also holds "Cetology", one of the most famously skipped chapters in American literature, a taxonomy of whales placed early, at chapter 32. Readers forgive Melville for it because his voice carries them through. Our Platforms chapter is our Cetology: necessary, honest and tedious. We shouldn't count on our voice to carry a reader through it the way Melville's does. notramo's complaint was about voice, and some humility is in order there.

So the Moby Dick lesson isn't "the payoff can wait". It's "the payoff can wait if the promise is present and every chapter pays something now". Read that way, our pushback on Zulip and our agreement with it are the same position. We keep the vignette structure, and the chapters before the code still have a place. But every one of them has to pay the reader in a currency the reader came for, and Roc is the currency nearly every reader came for.

## The problem statement, in one paragraph

The book shows a programmer who knows a little Roc how a real, highly animated program is built in Roc. It runs on two threads, the animation and the language. The animation supplies the problems, and Roc gives their solutions a shape; the book's best moments are where one thread makes the other necessary. Each chapter is a vignette that pays on its own, and the whole book is the long ride from a running app to an understanding of every frame. The opening's job is to make the reader want that ride. It shows the app, names what's in it, and introduces both threads early enough that a reader who came for Roc can see what they came for before the work begins.

## What this leaves open

Two questions this framing raises, without settling them:

- Whether The problem's five-piece plan is a vignette that pays, or "the whole journey upfront" that Aurélien found daunting. I've argued both sides now. The honest answer may be that it pays an engineer and daunts a learner. That's a question about who our reader is, more than about the chapter.
- What "at a glance" can honestly show. Real Safari code that a reader can enjoy without knowing the syntax is a high bar, and the cow snippet didn't clear it. A glance at Roc's *character* (a type that makes a wrong state impossible, a tag union the compiler checks, a pure function the platform calls thirty times a second) may matter more than a glance at its syntax.
