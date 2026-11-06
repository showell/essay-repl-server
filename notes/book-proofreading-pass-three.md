# Proofreading the book: the whole pass

*2026-11-06. This pass covers The ride instant through The platform. I applied 22 small fixes directly, and the book is rebuilt. The four questions at the end are the things I left alone. No plant this time.*

## What I changed

Most of the 22 are the same few repairs.

**Run-ons split.**

> **Before:** Taken together the calls form a tree, a function that calls none of Safari Ride's own is a leaf, and a walk through them is a trail.
>
> **After:** Together the calls form a tree. A function that calls none of Safari Ride's own is a leaf, and a walk through the tree is a trail.

> **Before:** `pack` gets there with method calls on plain numbers, and static dispatch finds `to_i64_wrap`, `shl_wrap` and `bitwise_or` on Roc's own types, so this is a leaf, the only one on the diagram.
>
> **After:** `pack` gets there with method calls on plain numbers. Static dispatch finds `to_i64_wrap`, `shl_wrap` and `bitwise_or` on Roc's own types. That makes `pack` a leaf, the only one on the diagram.

**Announcements cut.** "It's worth saying why" and "it's composable in the plain sense" went, and the reason now just follows.

> **Before:** The truck has no `Animation`, and it's worth saying why. A timeline has a known length...
>
> **After:** The truck has no `Animation`. A timeline has a known length...

**Sentences that hid their meaning.**

> **Before:** It settles, and it's also why `over_beats` has to stay the cat's rule.
>
> **After:** The loop settles, and it's why `over_beats` has to stay the cat's rule.

> **Before:** Adding two clocks means nothing, so `Clock` has no `plus`, and no code can.
>
> **After:** Adding two clocks means nothing, so `Clock` has no `plus`, and no other code can add one.

**Two chapter endings made plain.**

> **Before:** There's no effect anywhere in that sentence. What that's worth when the program has to change is still an open question.
>
> **After:** None of it has any effects. In the next chapter, we'll see what that's worth when the program has to change.

> **Before:** That's the last of the parts. Each has been seen alone, and the loop from the start of the tour hasn't been looked at since.
>
> **After:** That's the last of the parts. Next, we'll put them back together by returning to the loop from the start of the tour.

## Four questions

**1. "Call this *rule and score*."** Six times the book stops to name a pattern this way: places and distances, the step function, rule and score, a narrow view of a wide record, the chain of limits, and rehearsal. The names feed the patterns appendix, so they earn their place. The phrase itself may read as a tic by the sixth time. I could vary it ("We call this...", or just use the name in italics), or leave it as a recognisable signal. I'd leave it, because a reader scanning for patterns learns to spot it.

**2. "Door".** The book calls a function that wraps or unwraps a value a door: "the clock's one door to a float", "the doors in and out of these types", "the right door". It's short and consistent, but it's a metaphor doing a technical job. "Wraps" and "unwraps" are plainer, and the book already uses them. I'd keep "door" only where it's about there being exactly one, as in the clock's one door, and use plain words elsewhere.

**3. Spelling.** The prose says colour, centre, metres and tyres. The code says `color_between` and `sky_top_color`, but also `metres` and `centre`. So the reader sees "colour" next to `color`. Your audience is mostly American, and the Roc tutorial writes American English. Switching the prose to "color", "center" and "tires" is easy. "Metres" is harder, because `Distance.metres` is in the code. I'd switch everything except metres, unless you'd also like a rename.

**4. "It's the best scene in Safari Ride."** This is the book giving an opinion, at the top of The cat. You've told me not to say what the reader should feel, but this one is about the program and not about the reader, and it reads like an enthusiastic guide. I'd keep it.
