# Ten more edits to the book

*2026-11-06. These come from The stepped things through The platform, in book order. As before, one of the ten is a plant: an edit I think makes the prose worse for you. None of them has been applied.*

## 1. The stepped things

> **Before:** `Bike` is under 60 lines above its `expect`s, and it's the physics. Its type is the first one in the tour that names the rest of a record.
>
> **After:** `Bike` holds the physics, and it's under 60 lines, not counting its `expect`s. Its type is the first one in the tour that names the rest of a record.

The surprise is that physics fits in 60 lines, so the physics should come first.

## 2. The math layer

> **Before:** These are the core utility modules, and there being so few says something about the program. Everything else is a small module that takes one of these and adds a single idea. Six of the ten are nothing but numbers with rules, and the top three are under 80 lines each. Composable is the right word for this, and it isn't a slogan: a cat, a tower and a truck are all found on the road through `Chain`, and all reach the screen through `Camera`.
>
> **After:** These are the core utility modules. There are only ten, and nearly everything else is a small module that takes one of these and adds a single idea. Six of the ten are nothing but numbers with rules, and the top three are under 80 lines each. A cat, a tower and a truck are all found on the road through `Chain`, and all reach the screen through `Camera`.

"Says something about the program" and "it isn't a slogan" both tell you an insight is coming. The example is the insight.

## 3. Units

> **Before:** There's no `Bearing.plus(Bearing)`, because that sum has no meaning, and the omission is a feature with a compiler behind it.
>
> **After:** There's no `Bearing.plus(Bearing)`, because that sum has no meaning. If you try to write one, the compiler stops you.

This is a maxim where a plain fact does more.

## 4. Rehearsal

> **Before:** The call is the same `Bike.advance` that moves the real rider, with no lean change and steady speed. That's the whole trick, and it's why `Bike` has to be a function and not a method that writes to a bike.
>
> **After:** The call is the same `Bike.advance` that moves the real rider, with no lean change and steady speed. That's why `Bike` has to be a function. A method that changed a bike in place couldn't be tried out like this.

The reason gets its own sentence, and "the whole trick" goes.

## 5. Why rehearsal is cheap here

> **Before:** Here, those worries have nowhere to live. `Bike.advance` has a `->`, so it can't reach anything but its arguments. The old rider is intact because every rider is. Being wrong about a future costs nothing, and `LeanSearch` is 105 lines.
>
> **After:** In Roc, none of that comes up. `Bike.advance` has a `->`, so it can't reach anything but its arguments, and the old rider stays intact because every rider does. A rehearsal that goes wrong costs nothing, and all of `LeanSearch` is 105 lines.

"Nowhere to live" and "a future" are the writer enjoying the idea. The argument is strong enough without them.

## 6. Proving it

> **Before:** There's nothing to mock, because nothing was injected. No clock has to be faked, because the clock is a field. There's no browser to start, no window to open and no delay to wait out, and two runs can't disagree. A step of the ride takes nothing from outside it.
>
> **After:** Testing here is just calling a function. There are no mocks, no fakes, no browser and no waiting, and two runs can't disagree.

Four sentences make one point, so this says it once.

## 7. Which frames are held

> **Before:** The list grows by a rule: if a thing can be wrong without any listed frame changing, the gate is blind to it. A brake light wired to `Off` would pass every hash until 6,520 was added. A green hash means nothing for what no frame shows.
>
> **After:** We add a frame whenever something could go wrong without any listed frame changing. A brake light wired to `Off`, for example, would have passed every hash until we added step 6,520.

The rule becomes something we do, and the closing maxim only repeats it.

## 8. What the hashes bought

> **Before:** A language with no hidden state doesn't make a refactor safe by itself. It makes it possible to write a test strict enough to be trusted.
>
> **After:** Having no hidden state doesn't make a refactor safe by itself, but it does let us write a test strict enough to trust.

"Doesn't X. It makes Y." is a habit of mine. Joined into one sentence, it's just a claim.

## 9. The platform

> **Before:** Early on, the tour said the game has no effectful functions. It's fair to ask where they went, and the answer is that they never got as far as Roc.
>
> **After:** The game has no effectful functions, so where did the effects go? They never got as far as Roc.

The question can simply be asked. This is also how the Roc tutorial would do it.

## 10. Three builds

> **Before:** The same modules are compiled three ways, which is about the strongest statement of the line between the game and the platform that a program can make.
>
> **After:** The same modules are compiled three ways, which shows how cleanly the game is separated from the platform.

The three ways are the evidence, and they're listed right after this. The sentence doesn't need to grade them.
