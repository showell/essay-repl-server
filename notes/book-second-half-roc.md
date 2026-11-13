# Teaching Roc again in the second half

You marked the cold review's fourth weakness the one to address: the second half drifts from Roc into the app's details. A cold reader then mapped every Roc idea in chapters 20 to 39 and marked each one as taught, passed over in a sentence, or used and never explained.

## What it found

A handful of ideas carry real weight and get one sentence each, chapter after chapter:

- **Functions as values.** A function sits in a record field (`height_at`, the cat's `frame_instant`, the math layer's `Region`), is passed by name (`held_to` in the throttle's `fold`, `Sprite.to_shapes`), or is returned (`untimed_model_at_next_step` in The platform). Closures turn up in the road, the cat, the bird and the platform. That's the heaviest gap.
- **`fold`.** It's in the throttle, the math layer and Proving it, and it's never taught.
- **`..` means three things:** a record update, an open record type (`sun_in_view`, which never explains it), and the rest of a record in a pattern. The book never puts the three side by side.
- **Patterns.** Guards, `|` alternatives, `_`, nested payloads and tuples are scattered over eight chapters, one sentence each. `Ok({ segment, end })` in The truck's motion is never explained at all.
- **`is_eq : _`.** It's in four quoted types and never explained. `==` on a `Clock` or a `Speed` depends on it. The old Types chapter explained it, and that sentence was cut in the trim to 900 words.

## The plan

Two new interludes, one extension, and one paragraph. Each builds on code the book already quotes, so it ties back to what the reader has seen, and each lets nearby chapters cut their one-sentence glosses.

1. **"Functions as values"**, a new interlude just before The throttle. That's the first chapter in the second half to pass a function, `limits.fold(offered, held_to)`, and the cat, the bird, the math layer and the platform all lean on the idea after it. It teaches:
   - passing a function by name, and writing one in place;
   - closures;
   - a function in a record field, and why calling it takes parentheses;
   - `fold`, properly.

   It builds on `blend`, `height_at` and the throttle's `fold`. The cat, the bird, the math layer, Proving it and The platform then drop their glosses for a short pointer back.
2. **"Patterns"**, a new interlude just before The rider's gaze. By then the reader has met a tuple match, `Green | SmallGreen`, `Animal(animal)`, `EndsAt(_)` and `Leaves({ side: Left, .. })`, and the gaze brings the first guard. It teaches payloads, nested patterns, `_`, `|` alternatives, tuples and guards. It ends on why `noticed_pig` still needs its last branch: a guard doesn't count toward covering every case.
3. **Records gains "`..`, three ways"**: update, open record type, and rest pattern, plus renaming a field. That's about 250 more words on a chapter that's now 182. Mountains, the rider, the rehearsal, the bird and the math layer drop their glosses.
4. **One paragraph in the clock chapter on `is_eq : _`**: the type keeps the equality the compiler writes from the number inside, so `==` compares two clocks.

That takes the book to 41 chapters. Five of the second half's titles would then name a Roc idea: Records, Pure functions and effects, Opaque types, Functions as values, and Patterns. I'd write each interlude from a spine, in the way we did Functions. Each would go through the cold readers, and each must stay within 900 words.

## Left as they are

`Box`, string interpolation, the number conversions and `Animation.Timeline.of` are each used once. They read plainly where they come, and teaching them would add weight without payoff.
