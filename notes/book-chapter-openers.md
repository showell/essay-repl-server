# Safari Ride: something to look at, at the top of every chapter

*Plan, 2026-11-06. The book is at http://143.244.172.148:9210/tutorial/ and its source is `canvas_apps/safari/tutorial/tutorial.md`. Nothing in the book has changed yet: it waits for the renames merge. Numbers quoted here come from the book and from `gates/proof.expected`.*

## The rule

Each chapter opens with a very brief intro, then the thing to look at, then the text that follows from it. Each section gets a widget, a diagram or both near its top. Where a widget would be forced, the section opens on something real the code did: a compiler message, a table of real values, a worked number, a before and after, or a frame from a proof depth.

Three changes do most of the work:

- **Four existing widgets move up.** Sky, cat, beacon and bird all sit below a dependency diagram today. They go first, and the diagram follows.
- **Four new widgets fill the chapters that have none:** route, step, rehearsal and proof. The widgets table below says what each shows.
- **"New in this chapter" moves below the opener.** It sits between the intro and the first picture in every chapter, which is exactly where the reader should be looking at something. It becomes the first thing after the widget.

## Chapters and sections

The last column says what kind of opener it is: **W** a widget, **D** a diagram, **C** a compiler message, **T** a table of real values, **N** a worked number, **B** a before and after, **F** a frame from a proof depth.

| Chapter or section | Opens today with | Should open with | Kind |
|---|---|---|---|
| **Safari Ride** (front page) | The ride, live | No change | W |
| **The problem** | One sentence, then the loop diagram | No change | D |
| **One whole module** | A sentence, a list, the module | The line that can't compile: `clock + 7`, as a new `fails/` program with the compiler's message, then "here's what stops it" and the module | C |
| **The modules** | A list and a paragraph, then the system diagram | The system diagram straight after the first sentence | D |
| The part that isn't Roc | Prose only | A new diagram of one tick crossing the line: keys, `advance`, `frame`, shapes, canvas, with JS on one side and Roc on the other | D |
| What's a sighting? | Prose, then a type | A table of one real `CatItem` at step 1,570, field by field, beside the frame it was found in | T, F |
| **All that's stored** | Prose, then the record | The step widget: three fields, read out live. Then the record, which the reader has just watched | W |
| **What never changes** | A sentence, a list, the modules diagram | The route widget: a map of all nineteen segments, drag along it, and each stretch reads out its record | W, then D |
| **The sky** | The modules diagram, with the widget below it | The sky widget, then the diagram | W, then D |
| A function of the clock | Prose | A chart of the three curves against the clock: sun height, dusk, warmth, with the marks at 3,980, 4,730 and 5,490 | D |
| From curves to colours | Prose | A table of real values: five steps, each with its dusk, its packed integer and a swatch of the colour | T |
| Angles that can't be mixed up | Prose; the compiler message is at the end | The compiler message `turn_as_bearing` moves to the top of the section | C |
| **The cat** | The modules diagram, with the widget below it | The cat widget, then the diagram | W, then D |
| When it plays | Prose | A worked number: where the crossing starts at 1, 1.5 and 2 metres a step, showing that a faster rider sets it off sooner. A three-row table | N |
| What it looks like | Prose | A diagram of the score: the two tracks on one line of beats, with the cuts at 0.8, 2.8 and 3.8 against 1 and 3 | D |
| What it does to the rider | A sentence, then the modules diagram | Add the loop as a small diagram above it: speed sets the cat, and the cat holds the speed | D |
| Getting it on screen | A sentence, then the modules diagram | No change | D |
| **The beacons and the headlights** | Prose, with no picture until the first section | The beacon widget moves to the very top of the chapter, ahead of "A blink" | W |
| A blink | The modules diagram | The diagram stays, directly under the widget | D |
| One switch | The modules diagram | A before and after from two proof depths: step 3,742 with the lights off, step 5,700 with them on. Step 6,520 shows the brake lights | F, B |
| **The bird** | The modules diagram, with the widget below it | The bird widget, then the diagram | W, then D |
| Two rules | Prose; the comparison table is halfway down | The `over_gap` and `over_beats` table moves to the top of the section | T |
| A score one beat long | Prose | The same score diagram as the cat's, drawn for the flight. Side by side, they show one shape | D |
| Finding a tree | Prose | The route widget's map shows where the three flights go; a small plan of the near tree, the far tree and the rule between them | D |
| **The stepped things** | Prose, then the modules diagram; the widget note is halfway down | The step widget again, with the other half of its lesson: forward has to be played, and back is a list lookup. Then the diagram | W, then D |
| The rider | Prose | A table of a real `RiderState` at step 1,570: eight opaque types, each with its value | T |
| The bike | The modules diagram | A worked number: one degree of lean through `yaw_per_tilt` to a turn in a step, and how far that moves the bike | N, then D |
| The throttle | The modules diagram | The gate chain as a left-to-right diagram, then a table of one real step showing the acceleration after each gate | D, T |
| The truck | The modules diagram | The step widget's truck line covers this. A table of its schedule at five points on the route, to show the 500 metres closing to 100 | T |
| **The math layer** | Prose and a five-point list | The rehearsal widget, which is the chapter's best idea. The reader then knows what all the geometry is for | W |
| The workhorses | Prose, then a table | Rename to "The most imported modules", with the word workhorse gone. The table goes first | T |
| Numbers with units | The table of types | A compiler message first: a `Speed` added to a `Distance`, as a new `fails/` program, then the table | C |
| One record per space | Prose, then types | A compiler message: a `RoadPoint` where a `RiderPoint` is wanted. The draft already asks for this program. Then one real point written in all four spaces | C, T |
| Round the bends | Prose | The route widget again. Its map comes from folding the turns, which is the one thing the game itself never does | W |
| Cutting a polygon | Prose | A before and after: one real ground patch with a corner behind the camera, its corners before and after `clip_near`, and the frame it would have spoiled | B, T |
| Rehearsal | The widget note | A worked number: 12 arcs plus 1, about 44 simulated steps each, so about 570 per real step and four million a ride. Then a diagram of the call down from `Rider.decide` to `Bike.simulate_rider_step`. The widget has already been seen at the top of the chapter | N, D |
| Arithmetic all the way down | Prose | A table of real values: `Num_.exp_real` at three inputs, term by term, against the true value | T |
| **Proving it** | Prose, then a diagram, then the widget note | The proof widget: ride to a step, ride there again, and compare the shapes. Then the diagram | W, then D |
| A fixture is a value | Prose | The fixture itself, as two lines of code, before the explanation | code |
| The frame hash | Prose, then the table | The table first, with a hash column from `proof.expected` and a contact sheet of the nine frames | T, F |
| Two more proofs | Prose | The gate's own output, quoted: `differ 0 of 576000`, with the triangles and shapes at each step. And StepBack's before and after: a step back from 3,000 landing on 2,047, then on 2,999 | T, B |
| `expect` | Prose | The real summary line of a `roc test` run: how many passed, and how long it took | N |
| Crashes that help | Prose | A real crash, quoted: `Fraction.of(1.5)` and the sentence it stops with | C |
| The page itself | Prose | A real failure of the book's build: a quoted function renamed, and what the builder says | C |
| **The platform** | Prose and a list, then the diagram | The diagram first, then a table of the same modules built three ways: page, gates, native, with what each runs on | D, T |
| An app is a value | Prose | The record first | code |
| Keys | Prose | A table of each key and the function from `Tour` to `Tour` that it runs | T |
| A frame is a list | Prose | A real frame as data: step 1,570's 2,712 shapes counted by tag, then the first few written out | T |
| Where the effects went | Prose | A diagram of one tick as a sequence, with thin arrows on the Roc side and the only effects on the JS side | D |
| **Zooming back out** | A placeholder | The ride again, then the first diagram with each box labelled by the chapter that opened it | W, D |
| **Appendices, Credits** | Tables | No change | |

## Chapters that don't suit a widget

**One whole module, The platform, and the sections of Proving it** are about code as an object rather than about the ride. A slider there would be decoration. What these sections can show instead is the code doing what the prose claims: the compiler refusing a line, a gate printing a number, a crash stopping with a sentence, a frame as data. Every one of those comes from a real run, and the builder can hold it to one, the way `{{fails ...}}` already does.

**The math layer's sections** are mostly a formula each. A worked number with real inputs does more than a widget for `Num_`, `Geom.clip_near` and units.

## The new widgets

| Widget | The one idea | What you drag | Chapters it frames |
|---|---|---|---|
| `route` | The world is a list of records | Along the route, on a map of the nineteen segments | What never changes; Round the bends; Finding a tree |
| `step` | Three fields are the whole state, and forward has to be played while back is a lookup | The clock. Dragging right plays the ride up to the pointer, and it lags. Dragging left reads the list, and it doesn't | All that's stored; The stepped things; The truck |
| `rehearsal` | The rider chooses a lean by trying futures | Through the twelve tries of one real step's search, with each coasting arc drawn on the lane | The math layer; Rehearsal |
| `proof` | A frame is a value, so two rides can be compared exactly | To a proof step. It rides there twice and compares the shapes | Proving it |

Considered and left out, for now:

- **The truck's lights at dusk.** A widget would need the whole drawing code to show a lamp. Two frames from proof depths say the same thing.
- **The rider's lean.** The rehearsal widget already shows a lean bending an arc, and the chapter has room for one such picture.
- **The road's bends.** The route widget covers them.
- **A pinhole widget for One record per space.** Dragging a post down the road, reading out one point in all four spaces, would be small and cheap. It's the first one I'd add if a fifth is wanted.

## What this needs from outside the widgets

- **`game.roc`** has to list the modules a widget imports. `rehearsal` needs `Arc`, `Bike` and `LeanSearch`, which aren't there. That's a three-line change, held until the renames merge.
- **The frames from proof depths** need the book to show an image: a small fence or include in `BookFence.roc`, and a step in the build that renders the frames. The `F` rows above and the contact sheet depend on it. Without that, those rows fall back to their tables.
- **New `fails/` programs:** `clock + 7`, a `Speed` added to a `Distance`, and a `RoadPoint` as a `RiderPoint`.
- **Quoted output** (a real crash, a builder failure, a `roc test` line) should go through the builder the way `{{fails ...}}` does, or it will go stale. Hand-pasted, it's the first thing in the book that can be wrong without anything failing.
