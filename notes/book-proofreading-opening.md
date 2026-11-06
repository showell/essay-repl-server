# Proofreading the book: the opening chapters

*2026-11-06. This covers the opening page and the first three chapters: The problem, One whole module, and The modules. It's prose only, since fact-checking waits for the dust to settle. Nothing here has been applied yet. The chapter agent is editing the same text, so these changes go in after it lands.*

I read the official Roc tutorial cover to cover first. Its prose does a few simple things. It shows code, then says in a plain sentence what the code does. It talks to you. It gives the reason right after the fact, using everyday words like "that's because" and "this means". It takes one idea at a time.

Our text is accurate and mostly clear, but it sounds written by someone pleased with a sentence. Five habits cause nearly all of the agent-speak in these chapters.

## 1. Every chapter ends on the same trick

All three chapters end with a sentence pointing at what hasn't been said yet, phrased as an absence. One of these would be fine. Three in a row is a tic, and the reader starts to hear the formula.

> **Before:** So far that's all boxes and arrows. What a box looks like in Roc is still missing.
>
> **After:** Next, let's look at what one of those boxes looks like in Roc.

> **Before:** That's one module of about eighty, and nothing yet says how the rest fit together.
>
> **After:** That's one module out of about eighty. In the next chapter, we'll see how the rest fit together.

> **Before:** All of that is about one frame, and a frame is gone by the next one. What lasts from one step to the next hasn't come up yet.
>
> **After:** Everything in this chapter happens within a single frame, and none of it survives to the next one. So what does carry over from step to step? That's the next chapter.

## 2. Maxims

These sentences try to be memorable. The Roc tutorial never does this: it states the point and moves on. A maxim also tends to hide the actual reason.

> **Before:** The rule is simple: a sighting decides, and drawing paints.
>
> **After:** So a sighting decides what's visible, and the drawing code only paints what it's told.

> **Before:** A claim about a clock is one line, because a clock is a value. The `expect` that starts at step 5,699 gets there with `Clock.at_step`, and nothing has to ride that far.
>
> **After:** Because a clock is an ordinary value, a test about one fits on a single line. The `expect` above that starts at step 5,699 uses `Clock.at_step` to get there directly, so the test doesn't have to run the ride for 5,699 steps first.

> **Before:** The middle box is the heart of it.
>
> **After:** The most interesting box is the middle one: looking around.

## 3. Too many ideas in one sentence

This is the biggest difference from the Roc tutorial. We pack three or four facts into a sentence joined by commas and colons. It reads efficiently to the writer and takes work from the reader. The fix is to give each idea its own sentence, and to split paragraphs at each new idea.

> **Before:** Most of Safari Ride's small modules have this shape: a comment saying what the thing is, its imports, and one type named after the module. `Clock :: U32.{ ... }` is an opaque type: a `U32` underneath, with its methods in the block after it. `Clock.(n)` wraps a number, and in a parameter list it unwraps one, and only this module can do either. Nothing else can add 7 to a clock or pass a tree count as one. `is_eq : _` asks Roc to derive equality. Below the type, each `expect` is a check that `roc test` runs.
>
> **After:** Most of Safari Ride's small modules look like this: a comment saying what the thing is, some imports, and one type named after the module.
>
> `Clock :: U32.{ ... }` defines an opaque type. Underneath, a `Clock` is a `U32`, and the block after it holds its methods.
>
> `Clock.(n)` wraps a number into a `Clock`. In a parameter list, it does the opposite and unwraps one. Only this module can do either, which means no other module can add 7 to a clock, or pass a count of trees where a clock is expected.
>
> `is_eq : _` asks Roc to derive equality for us. Below the type, each `expect` is a test, and `roc test` runs them all.

> **Before:** There are two halves. The ride is `Rider`, `Truck` and `World`, with `World` composing the route from its scenery and critters. It knows nothing of drawing. The view is everything that turns the ride into a picture: the sightings find what's in sight, and the drawing paints it. The dotted arrow is the view reading the ride, and no arrow goes the other way. `RideInstant` sits over both, holding one instant of the ride and stepping to the next, and the browser only sees `SafariApp`, which hands it a list of shapes each frame.
>
> **After:** There are two halves. The ride is `Rider`, `Truck` and `World`. `World` puts the route together from its scenery and critters. Nothing in the ride knows anything about drawing.
>
> The view is everything that turns the ride into a picture. The sightings work out what's visible, and the drawing code paints it. The dotted arrow shows the view reading the ride. No arrow goes the other way.
>
> `RideInstant` sits above both halves. It holds one instant of the ride and steps to the next. The browser only ever sees `SafariApp`, which gives it a list of shapes each frame.

> **Before:** An arrow points from a module to one it imports, so a module is composed of what it points at. Dashed boxes each stand for a family of modules. Roc doesn't allow import cycles, so nothing here can point back up.
>
> **After:** Each arrow points from a module to a module it imports. A dashed box stands for a family of modules. Roc doesn't allow import cycles, so no arrow can point back up the diagram.

## 4. Written from the writer's side

These sentences make sense if you already know the outline. You flagged the first one yourself. The cure is to say what we're doing and why, as if the reader had just arrived. Now that "we" is allowed, this gets much easier.

> **Before:** Before the map, here's a whole module, so you know what the boxes on it look like up close.
>
> **After:** Let's start by reading one module from top to bottom. We'll use `Clock`, because it's small and every step of the ride depends on it.

> **Before:** This is the clock from the second box above, all of it.
>
> **After:** Here's all of it:

> **Before:** Here's how they fit: the whole system, simplified.
>
> **After:** Safari Ride has about eighty modules. This chapter shows how they fit together, starting with a simplified map of the whole system.

> **Before:** The problem is simple to state. Design a world once. Then, each time the clock steps, move what moves, find everything near enough to see, and draw it against the backdrop.
>
> **After:** Here's the problem Safari Ride has to solve. We design a world once. Then, each time the clock steps, we move what moves, find everything near enough to see, and draw it against the backdrop.

> **Before:** It's called like this, once a step:
>
> **After:** Safari Ride calls it once a step, like this:

## 5. Cleverness about the book itself

The opening spends its energy on the idea of zooming and tours. A reader who has just watched the ride wants to know what they're getting, and "a tour of a tour" and "Each chapter zooms too" ask them to admire the framing first.

> **Before:** A safari is a guided tour, so this is a tour of a tour. It starts with the big picture, zooms in on a few parts of the program, and zooms back out at the end. Safari Ride is about eighty modules of Roc, which is enough to show how Roc holds up in a program with a lot going on. The tour assumes you can already read Roc. Each chapter points out a few Roc ideas as they come up, and the useful ones come up more than once.
>
> **After:** This book is a tour of that program. We'll start with the big picture, zoom in on a few parts, and zoom back out at the end. Safari Ride has about eighty modules of Roc, so you'll get to see how Roc holds up in a program with a lot going on.
>
> We assume you can already read Roc. If you can't yet, the official tutorial is the place to start. We'll point out a few Roc ideas in each chapter as they come up.

> **Before:** Each chapter zooms too, on a smaller scale. A title line sits above each block of code and each diagram, and it can carry a marker. Two markers call out a change of direction, and two say what a quoted function calls.
>
> **After:** Each block of code and each diagram has a title line above it. A title line can carry one of these markers:

The sighting paragraph has a milder form of the same thing, where the metaphor is doing the explaining:

> **Before:** Each of those is a sighting, true for that instant and gone the next. Safari Ride takes its sightings the same way, fresh on every page.
>
> **After:** We'll call each of those a sighting. A sighting is only true for the moment it's made, so Safari Ride throws them all away and makes new ones for every page.

## What's already good

I wouldn't touch these. They're concrete, and they sound like a person:

- The first description of the ride, through "the truck turns on its headlights."
- "It doesn't have game mechanics yet. Nothing keeps score."
- The flipbook paragraph.
- "The JS knows nothing of cats, and the Roc knows nothing of canvases." It's balanced like the maxims, but it's specific, it's funny, and it's literally true.
- "Nothing else can add 7 to a clock", which is why the rewrite above keeps it.

## Hooray

These chapters don't need one yet, since the reader hasn't done anything. If we want one small lift, the `Clock.at_step` sentence can take it: "...so the test doesn't have to run the ride for 5,699 steps first!" A later chapter, where a compile error catches a real mistake or the frame hashes all hold after a refactor, would earn one better.

## Two decisions for you

1. **The "New in this chapter" lists.** They're the most machine-sounding thing in these chapters, and the Roc tutorial has nothing like them. I'd drop them and let each chapter's first sentences say what's coming. They do help a reader scanning for a Roc feature, though, so this could go either way.
2. **"A tour of a tour".** I've cut it above. It's the sort of line you may like more than I do, so tell me if it should stay.

## For the fact-check pass, not now

- "About eighty modules": the notes last counted 72, and `Pixels` makes 73.
- "The JS keeps the clock" sits oddly beside `Clock` being a Roc module. It probably means real time, and it should say so.

## Next

Once the chapter agent lands, I'd apply these to the opening chapters, rebuild the book, and show you. If the direction looks right, the same five habits give a checklist for the remaining chapters.
