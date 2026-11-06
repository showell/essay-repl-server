# Keeping an impatient reader through The cat

*2026-11-06. This is the book's longest chapter: 30 code blocks and 6 diagrams. Nothing here is applied yet, apart from the new "elaborate" sentence at the top. These are structural changes, so they're yours to call. No plant.*

## Where the reader gets lost

The sentences are mostly fine now. The trouble is the order. There are four places I'd expect a reader to give up.

**1. Too much vocabulary before anything happens.** Right after the widget, the reader gets `instant_at`, then three type definitions, then a diagram of calls. By then they've met *job*, *half*, *rule*, *timeline*, *stage*, *approach* and *instant*, and later come *strand*, *track*, *score*, *beat* and *cut*. That's twelve terms, and several overlap: job and half mean the same thing, and so do timeline and score.

**2. "When it plays" starts at the wrong end.** The reader has just learned that a faster rider sets the cat off sooner, and wants to see that rule. They get `Beats.to_f64` and `Distance.metres` first, two one-line wrappers. The rule arrives five code blocks later. Climbing from the leaves worked well in The sky, which is short. Here the climb is too long for the view at the top.

**3. The best code is buried.** The `looks` track is the fun of the chapter: it reads like stage directions. It comes after `spot_across`, the opening of `crossing_timeline`, `Pose` and `Cut`.

**4. The playing machinery.** `Beat.is_lte`, `is_short_of`, `playing_at`, `at_beat` and `Timeline.instant` are five blocks in a row about how a timeline finds its place. It's good Roc, with `var`, `for` and operators on opaque types. But a reader who has just enjoyed the score hits a wall here, in the middle of the chapter, with the rider's reaction still to come.

## What I'd do

**A map right after the widget.** It would replace "The trail now goes down to the leaves", and it tells the reader the chapter's size up front:

> This chapter has four parts. First, we'll see when a crossing plays. Then we'll read the score, which says what the cat does at each point. After that, we'll see how the cat slows the rider down, and how it gets on screen.

**Two jobs, one name each.** "When it plays" and "what it looks like" are already the section titles, so the text can use those. *Half* and *strand* go, and *timeline* and *score* get one sentence that says they're the same thing.

**Type definitions where they're used.** `Approach` moves to "When it plays", and `Instant` moves next to `Timeline.instant`. `Stage` stays up front, because it's where the two jobs meet.

**"When it plays" from the top down.** Start with `Cat.crossing_stage`, then `Animation.over_beats`, then one sentence saying `distance_in` multiplies speed by beats. `Beats.to_f64` and `Distance.metres` go. That removes three blocks, and the reader gets the rule at once:

> **Before:** The bottom of this half is arithmetic on opaque types. Neither field of an `Approach` is a plain number: like `Clock` and `Angle`, `Distance` and `Speed` are opaque types.
>
> **After:** `Cat.crossing_stage` calls the rule with the cat's own numbers. A crossing takes 38 beats: 10 to walk out, 24 frozen, and 4 for the escape. A beat is the animation's own unit of progress, and it's tied to no clock.

**"What it looks like" starts with the score.** Show the `looks` track straight after the two-track diagram, then explain `Pose`, `Through` and `Before` as things the reader has just seen. `spot_across` comes down to the `path` track, where it's used.

**A new section for the machinery, with an honest way past it.** Give it the title "How a timeline plays", and tell the reader what's in it:

> The score is data, so something has to play it. This section shows how, and it's where Roc's `var` and `for` appear inside a pure function. If you'd rather get back to the cat, you can skip to "What it does to the rider".

The Roc tutorial is frank like this, and I think it would keep more readers than it loses.

**Split "What it does to the rider" into its own chapter?** It's a separate question, with its own diagrams and trail, and it would bring the longest chapter down by a quarter. The cost is that the feedback loop is the cat chapter's best payoff. I'd keep it in, and only split if the chapter still feels long after the rest.

## Not changing

The opening, the widget's walkthrough, "The slider isn't scrubbing a video", the perched bird example, and the closing point about what isn't in the chapter all work well.

## Questions

1. Is top-down right for this chapter, even though The sky climbs from the leaves? Your earlier plan was to bring later chapters to the Sky and Cat shape, so this is a real change. I'd go top-down wherever a climb has more than a few steps, and I'd keep the 🐾 and 🍃 markers for the blocks that remain.
2. Are you happy with the book telling readers they can skip a section?
3. Should "What it does to the rider" stay in this chapter?
