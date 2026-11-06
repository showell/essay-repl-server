# What Rocco's tutorial can teach ours

*2026-11-06. Braeden Foster's tutorial in [Pixelsprout/rocco-engine](https://github.com/Pixelsprout/rocco-engine) at commit 6a436bf: `guide/tutorial/` (ten chapters), `examples/tutorial/` (their apps) and the rest of `guide/`, against `canvas_apps/safari/tutorial/tutorial.md` and `notes/safari-tutorial-design.md`. File names are given so that anything taken can be credited to him. One idea is Luke Boswell's, and it's marked.*

## Top ideas

Rocco's is a how-to for someone building a game, and ours is a tour of a finished program, so the voice doesn't transfer. The structure does. Six ideas are worth taking, in order of value.

1. **End each chapter on what's still missing, and open the next one there.** Our chapters mostly end by summing up. His end by pointing forward.
2. **Open each chapter with the same short list: what you'll meet here.** It gives a scanner the chapter's contents before the code starts.
3. **Show a behavior as an `expect` at the end of each chapter,** not only in "Proving it". Naming an `expect` by its `##` comment fills a gap our builder has marked with a `[check:]`.
4. **Say what a widget should show.** He pairs every "run this" with what you'll see and what a wrong result means.
5. **Let a chapter need a thing before it appears.** Groups arrive because a Speaker has to rise with a door.
6. **Publish a page of surprises.** `guide/defaults.md` has no counterpart in ours, and it would be the tour's most useful appendix.

## Worth taking

### Each chapter ends on a gap, and the next one fills it

This is the strongest idea, and it's why his order reads as necessary. A chapter opens on what the last one left undone, and the later ones close on what's still wrong.

> You can't yet see how many pickups are left, or that you have won. Next, read 7. A HUD. It puts the count and a message on the screen.
> (`guide/tutorial/06-door.md`)

> The game works, but it tells the player nothing.
> (`guide/tutorial/07-hud.md`, its first line)

> Pip walks, but it looks pasted onto the ground, because nothing in the game casts a shadow.
> (`guide/tutorial/04-lights.md`)

Chapters 2 to 10 all open this way, and chapters 6, 7 and 9 close this way too. The order of ideas is the order of wants, not the order of the API.

**For us:** the kinds give our order, and that stays. What can change is the seam between chapters. Ours has one fine example already: "The rider's lean has been passed over twice now... That needs the math." Most of our chapters end by closing instead: "That's every box on the diagram", "That's the clock-driven things." Each could end on what the last chapter's kind can't do. Clock-driven things can't react to the rider, and that's what opens the cat. The cat can be asked about any gap, and a truck can't, and that's what opens the stepped things. The second one is already written, in the first line of "The stepped things". It only needs to move up to the end of the chapter before.

### A fixed opening: the gap, a list of what's new, the picture

Every chapter opens the same way, and the middle piece is a two or three item list naming each new thing by its job:

> In this chapter, you put five pickups on the ground, and Pip collects each one that it touches. You use:
>
> - Colliders, the shapes that the host can test,
> - a `ContactsOf` Query, which asks which Colliders touch Pip,
> - the Contacts, which the next `step` gets.
>
> (`guide/tutorial/05-pickups.md`)

A screenshot of the finished chapter follows, before any code. The reader knows the destination and the vocabulary in a few seconds. Each page also carries a one-sentence `summary:` in its frontmatter, which the site uses (`README.md`, "Docs").

**For us:** the design says each chapter introduces a few Roc concepts, but a reader can't see which until they arrive. A short list at the top of each chapter, "Roc ideas here: opaque types with arithmetic, `var` in a pure function, record update", would suit a reader who is scanning for what they care about. It costs three lines a chapter. The live widget takes the screenshot's place, which is a better version of it.

### Every chapter ends with a test, and the tests make points

His chapters run: the change, then "Test the X", then "Run the game". The tests aren't an afterthought, and some teach the chapter's best idea:

> A test can pass any `dt`. A `dt` of 10 seconds would walk Pip far past the edge in one step, so the third test checks that Pip stops at the edge.
> (`guide/tutorial/03-moving.md`)

> A test makes the Contacts by hand, so it needs no host.
> (`guide/tutorial/05-pickups.md`)

> A test can set any field of the Model, so the win test starts with the door already open.
> (`guide/tutorial/06-door.md`)

Each of those shows purity paying off in one line, and it happens in chapter 3, not at the end.

**For us:** we keep tests for "Proving it", and the design wants it that way, so the fun chapters stay fun. A single `expect` under a critter could still be fun, and it's our main point in miniature: the cat is a function, so a claim about the cat is one line. This doesn't replace the proving chapter. It gives that chapter something to point back at.

**Our builder can't quote an `expect` today.** `tutorial.md` line 1240 has a `[check:]` saying an `expect` "has no name for an include to find" and wants "an include form of its own". Rocco's `packages/ui` shows the way: a `##` line directly above each `expect`.

```roc
## A closed dropdown ignores a click on an item.
expect closed.update([Clicked(12)]) == { dropdown: closed, selection: Unchanged }
```

That rule is **Luke Boswell's**, in his Roc Style Guide, which Rocco copies as `docs/roc-style.md`: "`roc test` prints it with the failure, so it is the test's name." Credit goes to Luke. None of safari's 1,379 top-level `expect`s has such a comment, so `{{expect "..."}}` would need one added wherever the tour quotes an `expect`. By his guide's account, the failure output improves too.

### Say what the reader should see, and what a wrong result means

Each chapter ends by running the game, and it never stops at the command:

> Walk Pip into a pickup. The pickup disappears.
> (`guide/tutorial/05-pickups.md`)

> Pip stands in the middle of a green ground. If you see a magenta cube instead, check that the file is at `pip/assets/meshes/pip.glb`.
> (`guide/tutorial/02-character.md`)

> If you hear nothing, read the log. If the host can't open the audio device, it says so once, and the game runs with no sound.
> (`guide/tutorial/08-sound.md`)

Chapter 10 adds a neat move for a silent failure: "add `expect idle != 0` and `expect walk != 0` to `loaded`", and read the log.

**For us:** our widgets are placeholders, so this can be built in from the start. Each widget gets one instruction and one prediction, such as "Drag the gap down until the cat freezes in the lane. Keep dragging, and it leaps." A widget with a stated result is an experiment, and without one it's a toy. The design's "drag the rider's gap" stops one sentence short of this.

### An idea arrives when the program needs it

Nothing in his tutorial appears for its own sake. Groups aren't a chapter. They arrive in chapter 8 because a Speaker has to rise with the door. `Cam.follow` arrives there too, for a reason you wouldn't guess:

> Who hears the hum? In rocco, the Listener is the camera of the Scene.
> (`guide/tutorial/08-sound.md`)

He also refactors in front of the reader, as the program grows. Chapter 5 renames `ground` to `cube` once there are two meshes. Chapter 10 says "first pull the direction out of `walk` into its own function". The code visibly changes as the design learns something.

**For us:** the design already has "repetition is important" and picks concepts by the kinds. What it could use is this question at each new concept: which thing in this chapter can't be written without it? `var` could then enter because `playing_at` needs a loop, which is how it reads now. Another check: the tour has no moment where code changes. The units work was a real refactor of a real program. One before and after in "Proving it", the same function with `F64` and with `Speed`, would show the program learning something. It would also carry the chapter's point better than the paragraph that says it.

### Answer the question the reader just had

He stops and asks it out loud, then answers in plain terms.

> When the door opens, the hum stops. Why not take it out of the list at once? A Speaker that leaves the Scene stops in 5 milliseconds. That is fast enough to sound like a cut, but it keeps the sound from clicking.
> (`guide/tutorial/08-sound.md`)

And he names the trap in the code he just wrote, right after writing it:

> If you give a new Collider an id lower than `pip_id`, Pip becomes `b` in its Contacts. Then `touched` misses it. Keep Pip's id the lowest, or check both sides of each Contact.
> (`guide/tutorial/05-pickups.md`)

**For us:** this fits our habit of stating limits flatly, and it adds one move: state the limit where the reader is standing. The bird's hanging case does this well already. A flat "Why not store the cat?" as an opening question would suit the dry voice.

### Guide pages open on a stance, then a real example

`guide/` pages keep one shape: what other engines do, what's wrong with it, what this one does, and "A first X" from a real game.

> In many engines, game code draws things: it calls a draw function for each object, every frame. [...] In rocco, your game never draws.
> (`guide/scene.md`)

> So rocco has no physics. It moves nothing and pushes nothing apart. Instead, it answers questions about shapes.
> (`guide/collisions.md`)

`guide/calls.md`, `guide/input.md` and the rest do the same, and the sections are called "A first Scene" and "A first Query". The snippets come from pong and the entity game, never from a toy.

**For us:** "Rehearsal" already has this shape: "In a language with mutable objects, this function has a problem to solve before it starts." Other chapters could open that way. "Worked out, not stored" is the obvious one: in most games a cat is an object with a position, and here it isn't. A neutral voice can carry that, and it doesn't need an opponent to be unkind to.

### A page of surprises

`guide/defaults.md` is the cleverest page in the guide. It's a flat list of everything likely to bite, sorted by area, each linking to the page that explains it.

> Most of rocco's defaults are chosen so that a small game works with little code. A few of them can still catch you out, usually as a black screen, a magenta cube or an object that slides across the scene.

> **Draws pair by id.** [...] If a new thing reuses an old id, it slides from the old thing's place.

It's sorted by what the reader sees, not by how the engine works.

**For us:** a Roc reader who wants to write something like this meets real surprises, and we earned them: float order under exact hashes, static dispatch on an operator, what `?? crash` means here, the `expect` that only sees its module's imports, `..others` needing a name when it appears twice. An appendix called "What catches you out", beside "the patterns", would be useful to the Roc community beyond this program. The patterns appendix says what works. This would say what bites.

### Say what didn't change

Every chapter says what it leaves alone, up front.

> The imports and `pip.glb` stay the same, and so does the header.
> (`guide/tutorial/06-door.md`)

> Only the lights change.
> (`guide/tutorial/04-lights.md`)

It costs a line and removes a worry. It's the same habit as our "say what the reader can stop thinking about", applied to the chapter's scope. Our chapters could open with one sentence on what the rest of the program does while this one is on stage. Chapter 4 is also only 95 lines, between two much longer ones, and it reads as a rest. "The beacons and the headlights" plays that role for us.

### A recap at the point you could stop

Chapter 8 is where a reader could reasonably leave, and it marks that:

> You have made a whole game: a character that you load from a file, moves with the keys, collects pickups and wins, with lights, a shadow, a HUD and sound.
> (`guide/tutorial/08-sound.md`)

It then gives a map of where to read next, by topic. Chapters 9 and 10 go on as extras, and chapter 10 repeats the recap and the map.

**For us:** "Zooming back out" is still a stub, and this is one shape for it: one sentence that lists everything the tour built up from three fields, then a map by interest. Reading for the types? Go here. For the physics? Go there. It also suggests a marked exit after the cat, for a reader who won't finish a tour this long.

### The chapter's full code, and a way to see the change

Each chapter has a whole app, and each chapter gives the command to see what changed:

```sh
git diff --no-index examples/tutorial/04-lights/main.roc examples/tutorial/05-pickups/main.roc
```

Ten full apps cost a lot of duplication, and for a how-to that's the right price: "If you get lost, compare your file with it." (`guide/tutorial/01-window.md`)

**For us:** we have one program, so this doesn't transfer directly. The small version is a link from each title line to the file at the pinned commit, so "from Cat.roc" can be followed. That's cheap in the builder.

### Tutorials under test

Two things keep his tutorial true, beyond the regions (below). `scripts/bridge_check.py` drives the chapter apps: Pip must move in chapter 3, the `Play` of the blip must come in chapter 8, the Pose must fade to Walk in chapter 10, and a screenshot of Pip walking must differ from one of Pip standing (`README.md`, "Screenshots"). CI runs it. And `scripts/DocCheck.roc`, under `docs --check` in `release.yml`, fails on any exposed item with no `##` comment.

**For us:** the first has an obvious version. Each widget's prediction, from the idea above, can be an `expect` or a gate line. "The cat freezes at this gap" is then checked, and the prose can't drift from the program.

### A glossary with an "avoid" list

`CONTEXT.md` defines each domain word and says what not to call it:

> **Element**: [...] _Avoid_: widget, Node (the 3D tree), Ui.Node (the package tree), control, view (the call), parent index

The tutorial then capitalizes those nouns (a Clip, the Manifest, a Pack), so a reader can tell a term from a plain word. The "avoid" list is the good part. We have `vocabulary.shale` for the code, and this is the same idea for prose. The tour coins words like sighting, score, beat, rule and rehearsal, and a short list saying what each is and isn't would keep a long draft consistent. The capitals we can skip, since backticks do that job.

## What we already do better

- **Named includes beat regions.** He marks `# region: x` in the source and `<!-- region: file#x -->` in the page, and `build.roc docs` copies the text. It's solid, and `--check` fails on a stale page in CI. Our `{{code Cat.instant_at}}` needs no marker in the source, and a renamed function fails the gate at once. Regions do reach what names can't: gate code, `lib/`, an `expect`, part of a function. Line 1182 of our draft has that open question.
- **Failing code, with the real message.** `{{fails turn_as_bearing}}` shows the compiler stopping a bug. His tutorial never shows a compiler failure, and a beginner doesn't need one. For a reader weighing Roc, it's the most convincing thing on the page.
- **Short snippets.** He repeats the whole of `view` in chapters 2, 3, 5, 6, 7, 8 and 10, with most lines unchanged and many of them long. It's right for typing along. Ours are cut to the point, and they show a function with its caller.
- **Live widgets, not screenshots.** Dragging the gap makes the argument. A picture can't.
- **Diagrams and direction markers.** His tutorial has no diagrams. The ten-box limit and the 🔭 and 🐾 markers are ours, and the call-tree walk is what lets a reader keep their place in 80 modules.
- **A program that's actually large.** Pip's game is 656 lines at its end, tests included, and chapter 10's point is reached by adding. The workhorse table, the patterns appendix and "Proving it" can only exist in a program of our size.

## What not to copy

- **Second person and the imperative.** "Add `Contact` to the exposed types", "In `pip/`, run". Our reader isn't building anything, and the design says neutral voice.
- **The very plain sentences.** They're right for his reader, and very consistent, but they'd flatten the dry tone that's working. "A safari is a guided tour, so this is a tour of a tour" has no place in his, and "Each Draw has its own id" has none in ours.
- **Explaining Roc.** "A tag union such as `Phase` names each phase of the game." His reader may be new to Roc. Ours isn't, and the design says so.
- **The mascot.** Pip suits a how-to. The tour's intro is dry, and its rider needs no personality.
- **"Next, read..." as a formula.** The gap is the idea. The sentence that links to the next page belongs to a site of separate pages, and ours is one long page, so the gap should be stated and the chapter should simply begin.
- **Whole-file repetition and the ten copies of the app.** See above.
- **The narrative "you" of a game being finished.** The tour has no win state, and the intro says so: "Nothing keeps score."

## How his README leads in

It mostly doesn't, and that's a choice. The first lines are the best of it:

> Odin manages the systems: window, clock, input, GPU, memory, audio, collision. Roc manages the game: its state and its rules, as pure functions. The engine is a Roc platform. The game is a Roc app.
> (`README.md`)

Those four sentences are a model of our "The part that isn't Roc" section. After them, the README turns to the people building the engine: platform tables, requirements, build steps, 600 lines. It sends other readers to the project page in line 3. `guide/install.md` is the reader's real start, and it runs on to `defaults.md`, then `calls.md`.

One gap, which could be a small thing to mention to him: neither the README nor any top-level `guide/` page links to chapter 1. `README.md`'s Layout table names the folder, and the site's navigation may cover the rest, but I didn't look at the site. Our equivalent decision is where roc-apps' README and roc.lynrummy.com point a reader at the tour.

## Credits, if any of this is used

| Idea | Credit | Source |
|---|---|---|
| The gap between chapters | Braeden Foster | `guide/tutorial/`, the openings of chapters 2 to 10 and the endings of 6, 7 and 9 |
| The "You use:" opening | Braeden Foster | `guide/tutorial/02-character.md` to `07-hud.md` |
| A test that teaches | Braeden Foster | `guide/tutorial/03-moving.md`, `05-pickups.md`, `06-door.md` |
| What you should see, and what a wrong result means | Braeden Foster | `guide/tutorial/02-character.md`, `08-sound.md` |
| A page of surprises | Braeden Foster | `guide/defaults.md` |
| An `expect` named by its `##` comment | Luke Boswell | His Roc Style Guide, copied as `docs/roc-style.md` |
| A glossary with an "avoid" list | Braeden Foster | `CONTEXT.md` |
| A tutorial driven by a test tool | Braeden Foster | `scripts/bridge_check.py`, described in `README.md` |
