# Safari Ride tutorial: forward references and unearned openings

Findings from reading `canvas_apps/safari/tutorial/tutorial.md` front to back as a first-time reader, with the built book beside it for code in place. The test throughout: can a reader who has read only what's above follow this sentence?

There are three passes in one ranked list. Untagged findings are forward references. Those tagged **[opening]** or **[cute]** come from the second pass: a chapter or section that opens on a compact aphorism with unearned terms, or cuteness that costs clarity. Those tagged **[stands alone]** come from the third pass: readers may land on any chapter directly, and the book builds one page a chapter, so a chapter's opening has to restate its premise without the chapter before it. The end of a chapter may still leave a question hanging. The table at the end gives the verdict on every chapter's opening.

Line numbers are for the source as of its 02:04 edit, and they'll drift, so search on the quote. Each quote was checked by script against that source. Rewrites use American spelling, so `colour`, `metres` and `tyres` in the book become color, meters and tires in the prose offered here. Identifiers such as `Distance.metres` stay as they are.

## Loses the reader

### 1. "The gate" is never defined, and the word already means something else

Headings: The workhorses (line 1072), Proving it (1289), The frame hash (1307)

> Counting who imports what, leaving out the gates, a handful stand out, and the lines here are the ones above each module's `expect`s:

> The gate programs reach the game through `game.roc`, a package whose only job is to list the modules they read.

> The gate holds each hash to a line of `gates/proof.expected`, exactly.

Why it fails: Nothing ever says what the gate is, and most of Proving it leans on it: "the gate is blind", "the gate requires zero", "the gate builds the page". Worse, the reader has just learned a different gate. The throttle section defines a gate as a rule that lowers an acceleration, so "leaving out the gates", 70 lines later, points at the wrong thing.

Rewrite (workhorses): Counting who imports what, leaving out the test programs, a handful stand out, and the lines here are the ones above each module's `expect`s:

Rewrite (at line 1289, before the first use): Everything here lives in `gates/`, and the game never runs any of it. The merge gate, which has nothing to do with the throttle's gates, is the check a change has to pass before it lands. It runs the lints, every `expect`, the tutorial's build and the proof tools. Its programs reach the game through `game.roc`, a package whose only job is to list the modules they read.

### 2. "The trail" and "the tree" have no referent

Headings: The sky (292), A function of the clock (296), and onward

> The trail starts at the clock, and climbs to the colours.

> The bottom of the tree is back in `Clock`, seen whole above.

Why it fails: This is the method of the rest of the book, and it arrives unannounced. The diagram above was called "the calls inside `Sky`", never a tree, and in this book a tree is a thing by the road. "Trail" has appeared once, in the marker table, with no explanation. The clock isn't on the diagram either, since that diagram shows only `Sky`'s own functions, so the reader looks for the bottom of the tree and can't find it.

Rewrite: The rest of this chapter reads those calls from the bottom up, from where the clock becomes a number to the colors at the top. Taken together the calls form a tree, a function that calls none of Safari Ride's own is a leaf, and a walk through them is a trail.

Rewrite: The bottom of the tree isn't on the diagram, which shows only `Sky`. It's back in `Clock`, seen whole above.

### 3. "Before the map" (the author's example)

Heading: One whole module (51)

> Before the map, here's a whole module, so you know what the boxes on it look like up close.

Why it fails: No map has been mentioned. The next diagram is never called a map, and the boxes the reader has seen so far are the steps of the loop, not modules. The sentence only makes sense to someone holding the outline. The book later says "The road has no map", which makes it harder still to recover.

Rewrite: A module of Safari Ride is one file of Roc. This chapter shows one from top to bottom.

### 4. "A score" arrives before it's defined, in a game that keeps none

Heading: The cat (465)

> `Cat` reaches into `Animation` twice, once for each half. `crossing_timeline` calls nothing there, because all it does is write a score down.

Why it fails: The musical sense of "score" isn't introduced until "What it looks like", 30 lines on. The only score the reader knows is from the first page, "Nothing keeps score", so this reads as a contradiction about points in a game.

Rewrite: `Cat` reaches into `Animation` twice, once for each half. `crossing_timeline` calls nothing there, because all it does is build a record of what the cat does at each point in the crossing.

### 5. "The first table" is the wrong table

Heading: Proving it (1271)

> The answer rests on one fact, which the tour has been repeating since the first table.

Why it fails: The first table in the book is the marker legend. The table of moving things isn't the first, and it doesn't state this fact either. The pointer sends the reader to the wrong place or to nowhere.

Rewrite: The answer rests on one fact from the ride instant chapter.

### 6. The lean and `LeanSearch` are pointed at as if already discussed

Heading: The truck, closing (1051)

> The rider's lean has been passed over twice now, with `LeanSearch` doing something the last few sections kept pointing at. That needs the math.

Why it fails: This is `LeanSearch`'s first appearance in prose. Before this it's a node in two diagrams and one call inside `Rider.decide`. No section pointed at it, and the reader can't identify the two passings-over. "Doing something" withholds what the sentence should say.

Rewrite: One question about the rider is still open: how `Rider.decide` picks a lean. The module that answers it is `LeanSearch`, and it rests on the geometry and physics in the next chapter.

### 7. "What lasts from step to step" (the author's example, second pass) [opening] [stands alone]

Heading: The ride instant (137)

> What lasts from step to step fits in one record.

Why it fails: "Step" has never been defined. It has appeared only as a diagram label and in "once a step". "What lasts" has no subject, so the reader can't tell what is being fitted into a record. The chapter opens on a turn of phrase instead of saying what `RideInstant` is. The line relies on the closing sentence of the previous chapter, which has the same trouble.

Rewrite: Each time the clock ticks, Safari Ride moves the rider and the truck and draws everything again. `RideInstant` is the one record it keeps from one tick to the next, and it holds the rider, the truck and the clock. One tick is a step.

Rewrite (the closing sentence at line 133, "What lasts from one step to the next hasn't come up yet."): What the program keeps between frames hasn't come up yet.

### 8. "Its place in the order" [opening] [cute] [stands alone]

Heading: The beacons and the headlights (637)

> The cat walked out of its place in the order. Two clock-driven things were left behind when it did, and both are brief. One of them comes round again, and the other switches once.

Why it fails: No order was ever stated, so this is the author's outline talking. "Left behind" and "brief" describe the book, not the program. "One of them" and "the other" point at things the opening doesn't name, and the reader who needs the heading to decode them is doing the opening's job.

Rewrite: Some things in Safari Ride are worked out from the clock alone, with nothing stored. The sky is the largest of them. This chapter covers the other two: the beacons on the radio masts, which blink over and over, and the truck's headlights, which switch on once.

### 9. "A second critter settles that." (the author's example, third pass) [stands alone]

Heading: The bird (738)

> A second critter settles that. The bird is Roc's logo, sitting on a treetop.

Why it fails: "That" is the last sentence of the chapter before, so the chapter's first line means nothing to a reader who lands here. The premise, that `Animation` might have been written for cats alone, has to be on this page.

Rewrite: The cat is built on a shared module, `Animation`, and one critter can't show whether that module was written for critters in general or just for cats. The bird is the second critter. It's Roc's logo, sitting on a treetop.

### 10. "Here's how they fit" [stands alone]

Heading: The modules (76)

> Here's how they fit: the whole system, simplified.

Why it fails: "They" is the "rest" of the previous chapter's closing sentence. A reader who lands here isn't told what fits or what the chapter is.

Rewrite: Safari Ride is about eighty modules of Roc. This chapter shows how they fit together, starting with the whole system, simplified.

### 11. "The fourth kind" [stands alone]

Heading: The world (168)

> The fourth kind is the easiest, so it goes first. Trees, cows, the pond and the road are built once and only read after that.

Why it fails: "The fourth kind" counts from a table in the previous chapter, and "goes first" is about the book's order. Without that table the opening has no subject until its second sentence.

Rewrite: Some of Safari Ride never changes. Trees, cows, the pond and the road are built once and only read after that, which makes them the easiest part of the program to read, so the tour starts there.

### 12. "Beacons" before anyone has said what a beacon is

Heading: The ride instant (148)

> The cat has no state, and neither does the bird, the sun or the beacons.

Why it fails: The opening says "Radio masts blink in the distance" and never says beacon. The word arrives here and again in the table with no link to the masts, and the book goes on to use mast, tower and beacon for one family of things.

Rewrite: The cat has no state, and neither does the bird, the sun or the beacons, the blinking lights on the radio masts.

### 13. "Every curve", before any curve

Heading: The sky (290)

> Every curve comes down to the box in bold, which is the only one that turns the clock into a number.

Why it fails: No curve has been mentioned. The diagram shows function names, and the curves are introduced one at a time in the next section. The first of them, the sun's height, turns out to be a straight line.

Rewrite: Everything on this diagram that changes with the clock comes down to the box in bold, which is the only one that turns the clock into a number.

### 14. `Throttle` and `RideFocal` introduced by what they don't know

Heading: What it does to the rider (570)

> `Throttle` and `RideFocal` know nothing of cats. They ask `CrossingReaction`, which is the only part of the rider's code that does.

Why it fails: Neither module has been described, and neither is on the chapter's list of new modules. Saying what an unknown thing doesn't know gives the reader nothing to hold.

Rewrite: `Throttle` sets the rider's acceleration, and `RideFocal` sets how wide the rider's view is. Neither knows anything of cats. They ask `CrossingReaction`, which is the only part of the rider's code that does.

### 15. "The cat's hold on the rider's eye"

Heading: What it does to the rider (578)

> `beyond` is how far past the end of the crossing the rider has come, and the cat's hold on the rider's eye fades over that distance, counted in beats.

Why it fails: Nothing has said the cat holds the rider's eye. That fact arrives eight lines later ("widens the view as it pulls the rider's eye"), so the sentence explains the fading of an effect the reader hasn't met.

Rewrite: A cat in the lane also draws the rider's attention, which widens the view. `beyond` is how far past the end of the crossing the rider has come, and that attention fades over that distance, counted in beats.

### 16. "A cut" and "those leap beats"

Heading: What it looks like (511)

> A cut has to say which side of it its own beat falls on, and two tags say that better than a boolean would. `crossing_timeline`'s comment says why it matters: those leap beats sum to a float just under the beat they stand for.

Why it fails: "Cut" hasn't been defined, and the track it belongs to hasn't been shown. "Those leap beats" points at a code comment six lines up, which itself leans on `Through` before the reader has seen it.

Rewrite: A timeline is divided into stretches, and a cut is where one stretch ends and the next begins. A cut has to say which stretch its own beat belongs to, and two tags say that better than a boolean would. `crossing_timeline`'s comment says why it matters: the beats of the leap add up to a float just under the beat they stand for.

### 17. "One function in two halves" [opening]

Heading: The cat (381)

> From a distance, the cat is one function in two halves, with a shared module underneath.

Why it fails: The function isn't named, and the halves aren't explained until "A rule turns an `Approach` into a `Stage`", 50 lines on. "Method syntax chains the two halves of the job" leans on the same undefined halves.

Rewrite: The cat is one function, `Cat.instant_at`, with two jobs: work out how far along the crossing is, and look up what the cat does at that point. The module `Animation` sits under both.

### 18. `$` as a sign of something, 270 lines before it's explained

Heading: The sky (262)

> If a function has no `=>` and no `$` in sight, there's nothing behind it to think about.

Why it fails: `$` first gets a meaning in the cat chapter ("the `$` marks what changes"). Here it's a warning sign the reader can't read.

Rewrite: If a function has no `=>` in sight, there's nothing behind it to think about.

### 19. "Beats" named but not explained

Heading: When it plays (471)

> An animation's beats are an opaque type too, `Beats`: fractional, and tied to no clock, so a place in an animation can't be passed as a step of the ride.

Why it fails: "An animation's beats" assumes the idea of a beat. Nowhere does the book say a beat is an animation's own unit of progress, and the next section's arithmetic ("10 to walk out, 24 frozen") depends on it.

Rewrite: An animation is measured in beats, its own unit of progress, and `Beats` is an opaque type too: fractional, and tied to no clock, so a place in an animation can't be passed as a step of the ride.

### 20. `shale` appears once, unexplained

Heading: The page itself (1377)

> Lints round it out: shale's Roc lints run first, with each count held exactly, and every count is at zero.

Why it fails: Shale isn't mentioned anywhere else in the book, and nothing marks it as a tool's name.

Rewrite: Lints round it out: a set of lints for Roc source runs first, with each count held exactly, and every count is at zero.

### 21. `shapes_canvas.js` compared with before it exists

Heading: The frame hash (1307)

> The painter is `SafariFrame`, in pure Roc, and its `ShapesPixels` is the twin of `shapes_canvas.js`.

Why it fails: The file isn't named until the platform chapter, the next one. The reader can't tell what `ShapesPixels` is a twin of, and that decides what the hash proves.

Rewrite: The painter is `SafariFrame`, in pure Roc. Its `ShapesPixels` does what `shapes_canvas.js`, the JavaScript that paints the page, does on a canvas.

### 22. The first gate of the throttle is never shown

Heading: The throttle (993)

> The first gate calls it, for the distance left to the point where the rider commits to the turn.

Why it fails: The quoted chain starts at `a2`, so the reader has seen an `a1` go in and no first gate. The snippet's title says only "from Throttle.roc", and the name `corner_brake` appears nowhere on the page.

Rewrite: The first gate, `corner_brake`, makes the `a1` that the chain above starts from. It calls this for the distance left to the point where the rider commits to the turn.

### 23. Code discussed that the book doesn't quote

Heading: The throttle (997, 999)

> After the gates, `clamp_v` holds the speed between rest and the limit, and the function's last move is a small piece of bookkeeping.

> The rest of `Throttle` is plainer than this section makes it sound.

Why it fails: `clamp_v` and `.change_from(state.speed)` appear in no snippet, and "the function" was never named, so the reader is told about the last move of code that isn't on the page. The second sentence judges a remainder the reader can't see, and it isn't quite so: the last gate comes back in the math chapter.

Rewrite: After the gates, `get_forward_accel_decel` hands its result to `clamp_v`, not quoted here, which holds the speed between rest and the limit.

Rewrite: The last gate, `shoulder_brake`, has to wait for the math layer chapter, because it simulates the bike ahead of itself.

### 24. "The one at the very top", and an `if` chain ahead of its code

Heading: A fixture is a value (1295)

> `Tour.initial` is a value, and `Tour.advance` is a step function, the one at the very top, wrapped around `RideInstant.next`. The `if` chain is the only management a history needs, and its comment says why half of the list goes at once:

Why it fails: "The very top" has no stated frame: top of the book, of a diagram or of the stack. `RideInstant.next` hasn't been seen, and the `if` chain and its comment are described before they're on the page.

Rewrite: `Tour.initial` is a value, and `Tour.advance` is the outermost step function. It wraps `RideInstant.next`, quoted below, and it also trims the list of past instants. An `if` chain does the trimming, and its comment says why half of the list goes at once:

## Trips the reader

### 25. Page becomes frame, and step goes unsaid

Heading: The problem (43)

> Safari Ride draws a page about thirty times a second.

Why it fails: The flipbook's word is "page". From The modules on, the word is "frame", and the code's word for a turn of the loop is "step", and nothing connects the three. The fix belongs here, where the reader first needs it.

Rewrite: Safari Ride draws a page about thirty times a second. The code calls a page a frame, and a turn of the loop a step.

### 26. "Segments" before segments

Heading: What's a sighting? (127)

> `CatSighting` goes through the segments ahead, asks `Cat` where it is, works out where that lands in the rider's view, and drops any cat behind the camera or too small to matter.

Why it fails: Segments aren't introduced until The world. The sentence is meant to explain a concept, so it shouldn't rest on another unexplained one.

Rewrite: `CatSighting` goes through the stretches of road ahead, which Safari Ride calls segments, asks `Cat` where it is, works out where that lands in the rider's view, and drops any cat behind the camera or too small to matter.

### 27. "The lens", which is a node on a diagram so far

Heading: What it does to the rider (586)

> The next call up, `crossing_attention`, is one line, and its caller, `ride_focal`, is the lens:

Why it fails: "The lens" reads as already known. The reader has seen `Lens` only as a box in the sky diagram, and the module is explained in the math chapter.

Rewrite: The next call up, `crossing_attention`, is one line, and its caller, `ride_focal`, works out the view's focal length:

### 28. `Pose.RiderState`, in a chapter where `Pose` means the cat's

Heading: What it does to the rider (582)

> `..` in the argument's type makes it an open record: this function needs `along` and `speed`, and accepts any record that has them, so it doesn't depend on `Pose.RiderState`.

Why it fails: `Pose.RiderState` hasn't appeared before, and the only `Pose` the reader knows is `Cat.Pose`, a tag union of what the cat looks like.

Rewrite: `..` in the argument's type makes it an open record: this function needs `along` and `speed`, and accepts any record that has them, so it doesn't depend on `Pose.RiderState`, the rider's record, which has nothing to do with `Cat.Pose`.

### 29. `Camera.project` and `Critter` as if already seen

Heading: A score one beat long (836)

> `RocBird.draw` hands that to `Critter.draw_still`, which is what a cow uses, and a bird's feet go through the same `Camera.project` as a tree's top.

Why it fails: "The same `Camera.project`" claims a familiarity the reader doesn't have. That function is first quoted in the math layer chapter, and `Critter` has not been mentioned.

Rewrite: `RocBird.draw` hands that to `Critter.draw_still`, the function that also draws a cow. A bird's feet reach the screen through `Camera.project`, as a tree's top does, and the math layer chapter shows how.

### 30. "The polite end of the math chapter" [cute]

Heading: A score one beat long (828)

> This is the polite end of the math chapter.

Why it fails: The joke works only for someone who knows there's a math chapter and how far it goes. The reader is six chapters from it.

Rewrite: Delete it. The sentence before it ends the paragraph well.

### 31. "That idea gets larger soon"

Heading: The rider (918)

> That idea gets larger soon. A small version of it decides what happens at the end of a segment.

Why it fails: The pointer doesn't name what's coming or where. The reader can't use it.

Rewrite: The math layer chapter takes that idea much further. A small version of it decides what happens at the end of a segment.

### 32. Leaning is used before it's said that the rider steers by it

Heading: The rider (914)

> A decision is a record of two opaque values. There's something to notice in the last line of this next function. `Throttle` is asked about a bike that doesn't exist yet: the rider as it would be with the new lean, which `Bike.with_tilt` makes by building a new record.

Why it fails: The book hasn't said the rider steers by leaning, or what a decision decides. "The new lean" assumes both, and `Bike` and `Throttle` have no section yet. The code calls the same thing a tilt.

Rewrite: The rider steers by leaning, so a decision is a record of two opaque values: a change of lean, which the code calls tilt, and an acceleration. There's something to notice in the last line of this next function. `Throttle`, which picks the acceleration, is asked about a bike that doesn't exist yet: the rider as it would be with the new lean, which `Bike.with_tilt` makes by building a new record.

### 33. `RiderPoint` a section before it's introduced [opening]

Heading: Numbers with units (1138)

> The units stop at the road. A `RiderPoint`'s `right` and `forward` are plain `F64`s, and so is everything in pixels.

Why it fails: `RiderPoint` is introduced in the next section, One record per space. "The units stop at the road" is an aphorism that only makes sense once that section has been read.

Rewrite: Opaque units don't go past the road. Once a point is measured from the rider, its `right` and `forward` are plain `F64`s, and so is everything in pixels.

### 34. The math chapter opens on its own ending [opening] [cute]

Heading: The math layer (1055, 1062)

> The lean comes at the end of this chapter, on top of everything else in it.

> A lot of Safari Ride is math and physics, and this is the chapter that goes through the floor of the tour and looks at what's holding it up.

Why it fails: The chapter's first line is about the book's sequence, and the chapter still hasn't said what it is. "Through the floor of the tour" is a figure where a plain statement is wanted.

Rewrite: This chapter covers the geometry and physics under the game: how a point on the road reaches the screen, and, at the end, how the rider chooses a lean.

Rewrite: A lot of Safari Ride is math and physics, and most of it is geometry a reader could do on paper.

### 35. Purity, before it's been said [opening]

Heading: The ride instant (160)

> Purity makes some things free.

Why it fails: The book hasn't used the word, and the paragraph explaining the absence of effects comes after this one. "Free" doesn't say what is cheap or why.

Rewrite: Keeping so little makes some things cheap.

### 36. "The floor of this layer" [opening] [cute]

Heading: Arithmetic all the way down (1252)

> The floor of this layer is lower than it needs to be.

Why it fails: The sentence is a riddle until the next one solves it, and a section should open on the thing it covers.

Rewrite: Safari Ride computes even its basic math functions itself.

### 37. "Below the frames, the proving is plain" [opening] [cute]

Heading: `expect` (1347)

> Below the frames, the proving is plain.

Why it fails: "Below" has no meaning here, and "the proving" is an abstract noun standing in for tests.

Rewrite: The rest of the testing is ordinary `expect`s.

### 38. "Hasn't touched the rider" [opening]

Heading: What it does to the rider (555)

> So far the cat hasn't touched the rider. That's a separate question, answered in one place.

Why it fails: "Touched" suggests a collision, the question isn't stated, and the one place isn't named.

Rewrite: So far the cat only moves itself. What it does to the rider's speed and view is a separate question, and `CrossingReaction` answers it.

### 39. "The hinge" [opening] [cute]

Heading: The cat (428)

> `Stage` is the hinge.

Why it fails: A hinge between what? The two things it joins are introduced in the next paragraph.

Rewrite: `Stage` is the type where the function's two jobs meet.

### 40. "A few questions put to a clock" [opening] [cute]

Heading: The sky (234)

> From a distance, the sky is a few questions put to a clock.

Why it fails: The chapter's opening figure stands in for what `Sky` is, and the reader hasn't been told what is being asked or who is asking.

Rewrite: `Sky` is a set of functions that each take a clock and answer with a color or the sun's place.

### 41. The platform chapter's opening, a run of "this" [opening]

Heading: The platform (1383)

> The rest of the program is what puts this on a screen, and Safari Ride has very little to say about that, on purpose. The tour touched this early on. Here it is with the code.

Why it fails: Three sentences point at this, that and this without naming the platform, and "early on" is an unnamed earlier place.

Rewrite: The platform is what puts the list of shapes on a screen: the host, the JavaScript, and the modules every canvas app shares. Safari Ride has very little to say about it, on purpose. "The part that isn't Roc", in the modules chapter, gave the outline, and this chapter adds the code.

### 42. "The answer to all of this" [opening]

Heading: A frame is a list (1438)

> The answer to all of this is a `List(Shapes.Shape)`.

Why it fails: No question was asked. The section before it is about keys.

Rewrite: What the game hands back each frame is a `List(Shapes.Shape)`.

### 43. The tones, and a second `Frame`

Heading: Where the effects went (1448)

> `init`, `advance`, `frame`, `release`, `sounds`, `width`, `height` and `fps`, with the tones' `tone_count`, `tone_freq` and `tone_ms`.

> `roc glue` generates `roc_glue.js`, which knows the layout of a frame in wasm memory, from `Frame.roc`, so that file is never edited.

Why it fails: The book has never mentioned sound, so "the tones" has nothing to refer to. `Frame.roc` reads as the workhorse `Frame` from the math chapter, but this is `web/platform/Frame.roc`, a different module, and "that file" could be either file.

Rewrite: `init`, `advance`, `frame`, `release`, `sounds`, `width`, `height` and `fps`, and for sound, which Safari Ride leaves empty, `tone_count`, `tone_freq` and `tone_ms`.

Rewrite: `roc glue` generates `roc_glue.js`, which knows the layout of a frame in wasm memory, from `web/platform/Frame.roc`, not the game's `Frame`, so `roc_glue.js` is never edited.

### 44. "Which no clock can do" [stands alone]

Heading: The cat (374)

> The cat reacts to the rider, which no clock can do.

Why it fails: The contrast answers the last line of the sky chapter, "A clock can't tell that a rider is coming." It still parses alone, but a reader who lands here doesn't know why a clock has come up. The chapter also doesn't say what the cat does until two sentences later.

Rewrite: A cat walks out into the lane, freezes as the rider bears down on it, and leaps clear at the last possible instant. Unlike the sun, which follows the clock alone, the cat reacts to the rider.

## Small

### 45. "The three kinds", counted differently

Heading: The truck (1047)

> That's the three kinds of moving thing in one vehicle: the place and speed are stepped, the headlights are clock-driven, and the tyres don't change.

Why it fails: The three kinds in the table are stepped, rider-driven and clock-driven. This list drops rider-driven and brings in the fourth kind, so the pointer doesn't match what it points at.

Rewrite: That's three of the four kinds in one vehicle: the place and speed are stepped, the headlights are clock-driven, and the tires don't change.

### 46. `lead`, never shown

Heading: The truck (1049)

> `TruckSighting`'s `lead` is the same quantity as an `Approach`'s `gap`, and it has a different name because it's being chased.

Why it fails: `lead` appears in no snippet, and "it" shifts from the quantity to the truck.

Rewrite: `TruckSighting` calls the distance to the truck `lead`, the same quantity as an `Approach`'s `gap`, because the truck is being chased.

### 47. "The two helpers of `dusk_at`", ahead of `dusk_at`

Heading: The sky (268)

> Only `Sky`'s own functions are shown, without the two helpers of `dusk_at`.

Why it fails: The sentence describes an omission from a diagram the reader hasn't seen, in terms of a function the reader hasn't met.

Rewrite: Only `Sky`'s own functions are shown, and two small helpers are left out.

### 48. "The shortest hop", before any code

Heading: The bird (766)

> The only sum in `BirdFlight` is a tree's place plus the shortest hop.

Why it fails: The sentence summarizes a module the reader hasn't seen, and "the shortest hop" sounds like a known quantity.

Rewrite: `BirdFlight` does one addition, a tree's place plus `shortest_hop`, the shortest flight a bird will make.

### 49. `Along`, unglossed

Heading: What it looks like (499)

> `Along.start` is a value rather than a call, which leaves nothing of Safari Ride's being called.

Why it fails: `Along` hasn't appeared, and it isn't on the chapter's list of new modules.

Rewrite: `Along.start`, the first place on a segment, is a value rather than a call, which leaves nothing of Safari Ride's being called.

### 50. `lib` and "the other canvas apps"

Heading: The workhorses (1086)

> `lib`'s `Shapes`, `Trig` and `DeviceMath` are imported about as widely, and they're shared with the other canvas apps.

Why it fails: Neither `lib` nor any other canvas app has been mentioned. The book's only trace of them is a path in The modules.

Rewrite: `Shapes`, `Trig` and `DeviceMath` are imported about as widely. They're in `lib/`, a folder of modules shared with the repository's other canvas apps.

### 51. "The native runner"

Heading: Two more proofs (1339)

> `ShapesFrame` paints each frame twice: once with its polygons whole, as the browser gets them, and once cut into triangles, as the native runner gets them.

Why it fails: The reader knows only that the app "also runs natively". The runner is explained in the next chapter.

Rewrite: `ShapesFrame` paints each frame twice: once with its polygons whole, as the browser gets them, and once cut into triangles, as the native program gets them.

### 52. "Any root" and "the source is the count"

Heading: `expect` (1357)

> The source is the count: every line that starts `expect`, in a module any root reaches, has to print `PASS` exactly once.

Why it fails: "Root" isn't defined, and "the source is the count" is compressed past the point of reading.

Rewrite: The gate takes its count from the source: every line that starts `expect`, in a module that one of its `roc test` runs compiles, has to print `PASS` exactly once.

### 53. "This function", with none in view

Heading: Rehearsal (1244)

> In a language with mutable objects, this function has a problem to solve before it starts.

Why it fails: The nearest function is `best_tilt_correction`, two paragraphs up, and the paragraph between is about rehearsal as a whole.

Rewrite: In a language with mutable objects, a rehearsal has a problem to solve before it starts.

### 54. `while` isn't back

Heading: Keys (1426)

> `var` and `while` are back, in a function that's still pure.

Why it fails: `var` came with `for`. `while` hasn't appeared before.

Rewrite: `var` is back, this time with `while`, in a function that's still pure.

### 55. "The README", and roc-ray

Heading: Where the effects went (1454)

> And `main.roc` hands the same `SafariApp.canvas_app` to `native/CanvasAppRunner.roc` on roc-ray. That third one is the spike that proved the idea and it isn't kept current, as the README says, so the page is the maintained side.

Why it fails: roc-ray hasn't been mentioned, and no README has. The book has no reason to expect the reader to know which.

Rewrite: And `main.roc` hands the same `SafariApp.canvas_app` to `native/CanvasAppRunner.roc` on roc-ray, a Roc platform for native graphics. That third one is the spike that proved the idea and it isn't kept current, as Safari Ride's README says, so the page is the maintained side.

### 56. "The first diagram", 1,400 lines on [stands alone]

Heading: Where the effects went (1456), Zooming back out (1460)

> That's the last of the parts. Each has been seen alone, and the first diagram hasn't been looked at since.

> Every box on the first diagram has now been opened.

Why it fails: The chapter's plan means the loop, but "every box opened" fits The whole system, simplified at least as well, and that's the diagram a reader is likelier to remember.

Rewrite: That's the last of the parts. Each has been seen alone, and the loop from the start of the tour hasn't been looked at since.

Rewrite (the chapter's opening, which has to stand alone): Safari Ride is a loop. It designs a world once, and each time the clock ticks, it moves what moves, finds what's near enough to see, and draws it. Every box on that loop has now been opened.

### 57. "Depends on one number" [opening]

Heading: The sky (227)

> The sky is the simplest thing that moves, because it depends on one number.

Why it fails: The number is never named, and it's the point of the sentence.

Rewrite: The sky is the simplest thing that moves, because it depends only on the clock.

### 58. "The road has no map" [opening] [cute]

Heading: Round the bends (1178)

> The road has no map.

Why it fails: The following sentences recover it, so this one is minor. The plain statement is just as short, though, and it avoids an echo of "the map" in finding 3.

Rewrite: The road has no global coordinates.

### 59. "A claim about a clock" [cute]

Heading: One whole module (70)

> A claim about a clock is one line, because a clock is a value.

Why it fails: "A claim" stands in for a test, one chapter after `expect` was introduced by name.

Rewrite: A test of a clock is one line, because a clock is a value.

### 60. "The tour named these in passing." [stands alone]

Heading: Appendix: the patterns (1466)

> The tour named these in passing.

Why it fails: "These" points at a table below the sentence. An appendix is the page most likely to be opened directly.

Rewrite: The tour named nine patterns in passing.

### 61. "The patterns say what works." [stands alone] [cute]

Heading: Appendix: what catches you out (1484)

> The patterns say what works. This page says what bites, sorted by what shows up first.

Why it fails: It opens on the appendix before it, and "what bites" is the heading's job done less plainly.

Rewrite: This page lists what catches a reader of Roc out in Safari Ride, sorted by what shows up first.

## Every chapter's opening

Chapters are numbered from The problem. A number in the last column is the finding with the rewrite.

| Chapter | Opens | Verdict | Finding |
|---|---|---|---|
| The opening page | This is Safari Ride. A rider cycles... | Stands alone |  |
| 1. The problem | The problem is simple to state. Design a world once. | Stands alone |  |
| 2. One whole module | Before the map... | Fails | 3 |
| 3. The modules | Here's how they fit... | Fails | 10 |
| 4. The ride instant | What lasts from step to step... | Fails | 7 |
| 5. The world | The fourth kind is the easiest... | Fails | 11 |
| 6. The sky | The sky is the simplest thing that moves... | Stands alone, with one word to fix | 57 |
| 7. The cat | The cat reacts to the rider... | Fails, mildly | 44 |
| 8. The beacons and the headlights | The cat walked out of its place... | Fails | 8 |
| 9. The bird | A second critter settles that. | Fails | 9 |
| 10. The stepped things | Where the rider and the truck are depends on where they were... | Stands alone. It restates its premise, which is the model for the others |  |
| 11. The math layer | The lean comes at the end of this chapter... | Fails | 34 |
| 12. Proving it | There are no animals in this chapter. It's about what happens... | Stands alone. The joke is paid for by the next sentence |  |
| 13. The platform | The rest of the program is what puts this on a screen... | Fails | 41 |
| 14. Zooming back out | Every box on the first diagram... | Fails | 56 |
| Appendix: the patterns | The tour named these in passing. | Fails | 60 |
| Appendix: what catches you out | The patterns say what works. | Fails | 61 |

## Looked at and left alone

These are the candidates that passed, so a revision needn't touch them.

- The marker table on the opening page. It's a legend, and it explains itself. Its markers don't appear until The sky, which is why finding 2 needs its own definition.
- "the platform chapter comes back to it", "the bird chapter reads `path_spot`", and "the `Arc` module that comes later". Each names what's coming.
- "That sentence is there for a reason that belongs to the proving chapter." It's coy, but it's honest and the sentence stands alone.
- The widget paragraphs. "The ruler", "the marked stretch", and the sun, dusk and warmth lines are all on the widgets in the built book.
- The closing line of each chapter, leading into the next. A closer may leave a question hanging. The two that don't hold up are in findings 6 and 7.
- The `[check: ...]` notes and the widget placeholders, which aren't reader text yet.
