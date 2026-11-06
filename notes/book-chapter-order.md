# The book: a new chapter order

*2026-11-06. A proposal, with nothing moved yet.*

You gave me three rules: progressive difficulty, motion postponed through about the first half, and categories to temper the first rule. I reread the first half with those in mind. Here's the order I'd use, and what it costs.

## The idea

The book has one question for its first half: what's on one page of the flipbook? "The problem" already says the ride is a stack of pages, so the reader knows early that it's frames. Then we hold still and walk through what's on a page, by your categories. Motion gets its own part after that, and the mechanics of `RideInstant` wait for it.

Your note that the rider is implicit helps a lot here. In the first half the rider is just where we're standing. "So many metres to the right, and so many ahead" is all the reader needs. The rider gets no chapter until motion does.

The book's current spine is the table of kinds of moving thing: stepped, rider-driven, clock-driven and unchanging. That table would move to the start of Part Three. It's a good map of the motion, but it's the wrong map for the first half.

## The order

**Part One: The big picture**

1. Introduction
2. The problem. This is where frames are established.
3. One whole module
4. The modules, with sightings

**Part Two: One frame**

5. The world, with the route and the pond

Nature:

6. Trees *(new)*
7. Grass *(new, taken partly from The road)*
8. Mountains *(new)*
9. The sky and the sun

Man-made:

10. The road
11. Rails *(split from The road)*
12. Radio towers *(new, taken from the beacons, without the blink)*

Critters that stand still:

13. Stills: how we draw a critter
14. The elephant
15. Rhinos, giraffes and the other corner critters
16. A pig
17. Herds: cows and pigs

**Part Three: Motion**

18. The ride instant, with the kinds of moving thing, and pausing and stepping
19. The beacons
20. The cat
21. The bird
22. The stepped things
23. The rider
24. The bike
25. The throttle
26. What a cat does to the rider
27. The rider's gaze
28. The truck, with its headlights

**Part Four: Under the hood**

29. The math layer
30. Proving it
31. The platform
32. Zooming back out
33. Appendices and credits

## Where the rules pull against each other

**The road is harder than anything around it.** It's man-made, so it comes after nature, and the billboard critters that follow it are much easier. Difficulty dips there. I think that's the temper you meant, and a dip gives the reader a rest. Splitting off Rails also makes the bend chapter shorter.

**The cat and the bird lose their place as critters.** Your earlier plan was a long run of critters, each with a new idea. This order breaks that run in two: the billboards in Part Two, and the cat and bird in Part Three. I think that follows from "all the billboard critters before the cat and the bird", plus postponing motion. They'd still sit side by side, and the transition from cat to bird stays.

**The stills chapter has to serve two audiences.** It now opens on the cat and the bird, and they'd be seven chapters away. I'd keep it whole, lead with the emoji-based animals, and mention the poses as something still to come. The gallery widget would stay, since a reader can enjoy a cat before it does anything. The skip link would point to The elephant.

## What it costs

- **Four new chapters:** Trees, Grass, Mountains and Radio towers. The code is all there, and each should be short. They're easy reading, which is what this stretch of the book needs.
- **Roc ideas change order.** This is the biggest job. `Fraction` and `Angle` arrive in The sky, `Along` and `Across` in The road, and the "New in this chapter" lists are built on that order. Trees would come first, so it has to introduce `Along` and `Across`. I'd go through the book once and move each idea to where it's first needed.
- **Every transition between moved chapters gets rewritten.** That's about twenty, and many of them are the ones you've approved one by one. "The cat and the bird both move. The elephant doesn't." has to go, for example.
- **The critter chapters lean on each other.** The elephant's and pig's records are explained against the cat's, so those need rewriting in the other direction.

All of this is prose, so it's mine. Cold agents could do the new widgets if the new chapters want any.

## One question

**Where does the sky go?** This is the one place where the rules really collide. It's nature, so your categories want it in Part Two. It's also the simplest thing that moves, so "postpone motion" wants it in Part Three.

I'd keep it whole in Part Two, as chapter 9. Asking "what color is the sky at step 3,000?" is a question about one frame. It's a function of a number, and it needs none of the mechanics of stepping. Dragging the clock in the widget doesn't feel like motion so much as trying different pages. It's also where the book teaches `->` and `Fraction`, and everything later leans on those.

The other choice is to split it: the sky's colors in Part Two, and the sunset in Part Three beside the beacons. That's a purer version of your rule, and it costs a chapter that gets cut in half.

## A smaller question

The truck isn't on your list. I've left it with the rider in Part Three because it moves, and its headlights go with it. They'd leave the beacons chapter, which then has only the blink. Does that fit how you think of the truck?
