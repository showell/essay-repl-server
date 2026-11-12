# Chapter 2: two free-style drafts, with an editor's notes

Two cold writers each saw the Introduction and our two drafts, the reflective one and the beginner one, and wrote a chapter 2 of their own. Each had a goal:

- **Writer 1:** hook a second- or third-year computer science student who knows Python and Java and has never used a functional language, so that they click "next".
- **Writer 2:** convince a programmer with five years of TypeScript, mildly skeptical of functional-programming pitches, that the book is worth one free evening, without talking down to them and without naming another language.

Both had a 450-word limit, no code, and only the facts in the brief. The texts are verbatim below, each followed by my notes as editor.

---

## Writer 2, for the professional skeptic: "Moments"

> The ride you just watched never stops changing. The rider rolls on, the sun sinks, the truck turns on its headlights, and a cat crosses the road. Yet a Roc value stays exactly as it was made, for as long as the program holds it. This chapter shows how both can be true, and what the ride gains from it.
>
> Pause the ride and press the left arrow key. The ride steps back a frame. Press it again, and it steps back another. Run it twice with the same keys, and every frame matches. Neither trick is bolted on. Both fall out of how the program is built.
>
> It is built like a flip book. Each page of a flip book is a still drawing, and the motion comes from the flipping. In Safari Ride, each page is a moment, and a moment is a value. It holds just four things: the rider, the truck, the clock, and the plan for when the cat or the bird ahead starts to move. Everything else in a frame comes from those four and the road. The sun's place in the sky comes from the clock.
>
> Two functions do the work. One takes a moment and gives back the next one, a new value beside the old. The other takes a moment and gives back its picture, a list of shapes. Neither one touches the screen. Under the Roc code sits the platform, which does. Thirty times a second, it asks for the next moment and paints that moment's picture.
>
> Because no moment ever changes, the ride can keep the moments behind it, and stepping back is turning to an earlier page. Because the same moment always gives the same picture, this book can hold a page still beside the text, drawn by the ride's own code.
>
> The other half is types. Every value has a type, and the compiler checks the whole program against its types. A type describes exactly the values that may exist. On the road, a length is a `Distance`, in metres. On the screen, a length is in `Pixels`. Both are numbers underneath, and the compiler keeps them apart. A length on the road becomes a length on the screen only where the code says how. In a ride full of near and far things, the code crosses that line often, and it says how each time.
>
> That is the shape of the book. The ride poses a problem, and Roc shapes the answer: a fresh value for each moment, a type for each kind of length. Each answer is the real code behind the ride you watched. The next chapter breaks the ride into the pieces we build.

**Its own note:** it opens on something the skeptic can check in ten seconds, so the idea of values that stay put arrives as the reason for behavior the reader has just seen, rather than as a philosophy to take on trust.

### My notes

**The big idea is the order: evidence first, then philosophy.** This is the best idea either writer had, and it answers your "reads like a conclusion" directly. Our reflective draft opens with a thesis, "Every programming language makes a bet", which is how you talk to someone who already agrees. "Moments" opens with an experiment: pause, press left, watch it step back. The design then explains something the reader has just seen. That's an introduction's posture, not a conclusion's.

**It has a mechanical flaw.** The ride isn't on this page. It runs in the Introduction, so "Pause the ride and press the left arrow key" sends the reader back a page. The flaw points at an opportunity. This chapter has no picture yet, and the book already has a step widget, a frame with stepping controls. Put it here, and the experiment happens in place. The chapter gets a picture of its own (H9), and its reason to exist is right there on the page.

**"Run it twice with the same keys, and every frame matches"** belongs with the claims, not the experiment. Nobody checks that in ten seconds.

**Voice:**
- "Neither trick is bolted on. Both fall out of how the program is built." is good and a little aphoristic. I'd keep the second sentence alone.
- "Neither one touches the screen" and "Because no moment ever changes" are negatives (D2), and each has an easy positive.
- "drawn by the ride's own code" is the imprecise "draw" (D11).

**The last paragraph is the weak one.** "That is the shape of the book" is a summary, and "Each answer is the real code behind the ride" promises code this chapter never shows. It has the same closing-moral problem the reflective draft had.

**It's a remix more than a new draft.** Most of its sentences are our reflective draft's, reordered. That's fine: the reordering is the contribution.

---

## Writer 1, for the college student: "The flip book"

> In Java, you would probably build this ride out of objects. A rider object would hold a position, and each time through the game loop you would add a little to it. The old position would be gone, overwritten.
>
> Roc works another way. A Roc value stays exactly as it was made, for as long as the program holds it. Yet the ride you just watched is change from start to finish: the rider rolls on, the sun sinks, the truck turns on its headlights, and a cat crosses in front of the bike.
>
> The answer is a flip book. Each page is a still drawing. The motion comes from the flipping.
>
> In Safari Ride, each moment is a value. One function takes a moment and gives back the next one, with the rider a little farther down the road. The old moment stays as it was, and the new one sits beside it. A second function takes a moment and gives back its picture: the sky, the road, the cows and the trees, as a list of shapes. The platform under the Roc code, the part that talks to the screen, does the flipping. Thirty times a second, it asks for the next moment and paints that moment's picture.
>
> This buys things that are hard to get from objects that change in place. The same moment always gives the same next moment and the same picture, so if you run the ride twice with the same keys, every frame matches. The ride keeps its old moments, so the left arrow key steps a paused ride back a page. Any page can also be held still, and this book does that often, building pictures beside the text from the ride's own code.
>
> Roc's other big idea is types: every value has one, and the compiler checks the whole program against them. On the road, a length is a Distance, in metres. On the screen, a length is in Pixels. Both are numbers underneath. As two plain floats in Python, you could add one to the other and never hear about it. In Roc, the compiler keeps them apart, so a road length becomes a screen length only where the code says how.
>
> Now look at how little a moment holds. It has just four things: the rider, the truck, the clock, and the plan for when the cat or the bird ahead starts to move. The ride works out everything else in a frame from those four and the road. The sun's place in the sky comes from the clock.
>
> The next chapter breaks the ride into the pieces we build.

**Its own note:** it opens on the game loop the student already knows, so that values which stay put read as a real puzzle with the ride as the evidence. It ends on how little a moment holds, which gives the student a concrete reason to click "next".

### My notes

**It breaks the mission's hardest rule twice.** It names Java and Python, and "objects that change in place" edges toward disparaging another style. For a student, the contrast is the hook, and I see why the writer reached for it. Our beginner draft reached for the same thing more quietly. But the book never compares Roc to another language, so the opening can't stand as written.

**Two ideas worth stealing.**
- **The ending.** "Now look at how little a moment holds." Four things, and the whole ride comes out of them. That's an ending that makes a reader want the next chapter, a question rather than a summary. It's the strongest last paragraph of the four drafts so far. "Moments" buries those same four things in its middle.
- **The bug made concrete.** "You could add one to the other and never hear about it." That's the reason types matter, said as something that would actually happen to the reader. It needs no language name: "As two plain numbers, a road length and a screen length add without complaint" keeps the force.

**"The answer is a flip book."** This three-sentence paragraph is the tightest statement of the image in any draft.

**The rest** is close to our beginner draft, and it runs long. The student version came in at about 440 words, as long as the reflective one.

---

## What I take from the pair

**Given a free hand, both writers converged on the same skeleton:** the paradox, the flip book, two functions, the platform flipping, the payoffs, types, and the four things. Neither found a different shape. That's evidence the skeleton is right. It's also evidence that the skeleton is about 430 words long. "It's kinda long" won't be fixed by tightening sentences. It needs a section to leave.

**The section that can leave is types.** The pieces as types arrives two chapters later and opens with types as "the heart of every Roc program", `Distance` included. Chapter 2's types paragraph previews that chapter, and it's the paragraph the think-aloud reader lost the thread on. Without it, the chapter is one idea, values that stay put, which suits a chapter built on one image.

**A chapter 2 assembled from all four drafts:**

1. **Open on the experiment** ("Moments"), with the step widget on the page: step back, step forward.
2. **The paradox in two sentences:** the ride is all change, and a Roc value stays as it was made.
3. **"The answer is a flip book."** (Writer 1's three sentences.)
4. **The two functions and the platform turning the pages** (all drafts agree).
5. **Why the experiment worked:** the ride keeps its old moments, and the same moment gives the same picture.
6. **End on "how little a moment holds"** (Writer 1), the four things, as the question the next chapter takes up.

That's perhaps 250 words, with a picture, no thesis up front, and no named language. Its audience is the working programmer from the mission, who gets evidence rather than a pitch. A student can follow it too.
