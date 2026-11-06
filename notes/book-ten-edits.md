# Ten edits to the book

*2026-11-06. These come from The ride instant through The stepped things, in book order. One of the ten is a plant: an edit I think makes the prose worse for you. None of them has been applied.*

## 1. The ride instant

> **Before:** Purity makes some things free. `Tour`, the whole ride, is little more than a list of past instants, so stepping back only needs an older one. The cat follows along, since it was never anywhere but where the rider's position puts it, and the sun rises again.
>
> **After:** Because the code is pure, some features come almost for free. `Tour`, the whole ride, is little more than a list of past instants, so to step back, we just go to an older one. The cat ends up in the right place, because its position only ever came from the rider's. The sun, which only reads the clock, rises again.

Each result now has its cause beside it.

## 2. The world

> **Before:** Here's the second whole module, and it's charming in a way code rarely is. `Pond` is a void module, a type with no values whose block holds definitions, and it has two record aliases and six ducks.
>
> **After:** Here's the second whole module. `Pond` is a void module: a type with no values, whose block holds definitions. This one has two record aliases and six ducks.

The book shouldn't tell the reader what to feel. The six ducks do that by themselves.

## 3. The end of The world

> **Before:** Nothing in this chapter moves, and the ride does.
>
> **After:** Nothing in this chapter moves, but the ride does. Next, we'll look at the simplest thing that moves: the sky.

The "and" makes the reader stop and work out the contrast.

## 4. The sky

> **Before:** Every function in this chapter has a `->` arrow, not `=>`. In Roc that's a promise the compiler holds: no effects, so the same clock always gives the same sky. If a function has no `=>` and no `$` in sight, there's nothing behind it to think about.
>
> **After:** Every function in this chapter has a `->` arrow, not `=>`. That tells you the function has no effects, and the compiler holds it to that. So the same clock always gives the same sky. If you don't see a `=>` or a `$`, you only have to think about what the function is given.

"Nothing behind it to think about" sounds wise, but it doesn't say what you're free to stop thinking about.

## 5. A function of the clock

> **Before:** The bottom of the tree is back in `Clock`, seen whole above. `Clock.to_f64` opens the opaque type. The `to_f64` it calls is `U32`'s, which belongs to Roc, so nothing of Safari Ride's is called.
>
> **After:** We start at the bottom of the tree, in `Clock`. `Clock.to_f64` opens the opaque type and calls `U32`'s own `to_f64`, which comes with Roc. It calls nothing else in Safari Ride, so it's a leaf.

The original makes you assemble the point. It also never says "leaf", which is why the sentence is there.

## 6. The end of The sky

> **Before:** The sun would set the same way on an empty road. A clock can't tell that a rider is coming.
>
> **After:** The sky depends only on the clock, so nothing in this chapter responds to the rider. In the next chapter, we'll look at something that does.

This says outright what the chapter covered and what comes next.

## 7. The cat

> **Before:** `Stage` is the hinge. It's a tag union where two of the tags carry a payload, and `Waiting` and `Past` aren't progress of 0 and 1, because a critter can rest somewhere no part of its animation reaches. If `Waiting` were just 0, a perched bird would show the first frame of its flight.
>
> **After:** `Stage` connects the two halves. It's a tag union, and two of its tags carry a payload. You might expect `Waiting` and `Past` to be the same as progress of 0 and 1, but a critter can rest somewhere its animation never goes. If `Waiting` were just 0, a perched bird would show the first frame of its flight.

The original denies something the reader hadn't thought of yet. The rewrite raises the expectation first, which is how the Roc tutorial answers a question. The bird sentence was already good.

## 8. The beacons and the headlights

> **Before:** The cat walked out of its place in the order. Two clock-driven things were left behind when it did, and both are brief. One of them comes round again, and the other switches once.
>
> **After:** This chapter covers the two clock-driven things we skipped to get to the cat: the towers' beacons, which blink over and over, and the truck's headlights, which switch on once.

The original is coy about its own subject. A reader landing here should see the title's two nouns right away.

## 9. The stepped things

> **Before:** Stepping has a price, and it's worth stating against the cat:
>
> - A cat can be asked about any gap. A truck at step 4,000 has to be played there, or written down by hand.
> - A wrong critter rule is wrong in the frames it touches. A wrong step moves the rider for the rest of the ride.
> - `RideInstant.next` has an order, and frames don't.
>
> **After:** Stepping has a cost, which shows up when we compare it with the cat:
>
> - We can ask about a cat at any gap. To find a truck at step 4,000, we have to play the ride that far, or write the answer down by hand.
> - A wrong critter rule only affects the frames it touches. A wrong step moves the rider for the rest of the ride.
> - The lines of `RideInstant.next` have to run in order. Frames can be worked out in any order.

The last bullet is the sharpest idea in the list, and its compression hides it.

## 10. The end of The bird

> **Before:** Nothing in this chapter is new machinery, and that's what it shows. Above their `expect`s, the four bird modules come to about 450 lines, a quarter of them coordinates for the stills, and `Animation` has nothing in it about birds.
>
> **After:** We didn't need any new machinery for the bird, and that's the point of this chapter. Above their `expect`s, the four bird modules come to about 450 lines, a quarter of them coordinates for the stills. `Animation` has nothing in it about birds.

The payoff of two chapters shouldn't be folded into a trailing clause.
