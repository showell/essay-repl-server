# Fast Track in Roc: a plan

A port of [elm-fasttrack](https://github.com/showell/elm-fasttrack) to Roc,
with a JS layer drawing the board. The first version may leave the JS fat; the
goal is for Roc to own the UI, through something we build ourselves, fitted to
this game rather than general.

Nothing is built yet. This is the proposal, plus the four questions only you
can answer.

## What there is to port

About 4,900 lines, in three unequal parts.

| part | files | lines | what it does |
|---|---|---|---|
| rules | Type, Config, Setup, Piece, Graph, LegalMove, Player, Move, Game, History, Color, WhatIf | ~3,400 | pure: the board graph, legal moves, turns, the deck, undo |
| view | View, Polygon, Main | ~900 | Html + Svg, plus the polygon geometry |
| tests | tests/Example.elm | 749 | elm-test over the rules |

The only effects in the whole program are two:

- **`Time.now`**, read once to seed the deck.
- **`elm/random`**, which draws a card from the hand.

Everything else is a pure function of a message and a model. The Elm
architecture carries over almost directly: `init(seed)`, `update(model, msg)`,
`view(model)`.

Two Elm libraries need a decision in Roc:

- **`AssocList` / `AssocSet`** keep insertion order, and that order reaches the
  screen: it decides the order of the moves, the highlighted starts and the
  cheat sheet. Roc's `Dict` has its own order. A faithful port needs a small
  ordered-list module of our own, a few dozen lines.
- **`elm/random`** is a PCG variant. If we port its `initialSeed`, `int` and
  `step` exactly, a seed deals the same game in Roc as in Elm. That makes the
  Elm build an oracle for the whole rules layer. `canvas_apps/lib/Random.roc`
  is an LCG, and deliberately not faithful, so it doesn't serve here.

## The structure that makes a small "virtual DOM" enough

Elm rebuilds the whole tree on every message and lets `elm/virtual-dom` diff
it. We don't need that, because **the board never changes shape.**

Once the player count is fixed, the board is a fixed set of slots: N zones
times the same `configLocations`, plus the bullseye. `Polygon` places them once.
Rotating the board doesn't move a slot. It changes which zone color each slot
is drawn in. Every render of the board is therefore one map:

    slot -> { shape, fill, stroke, piece color (or none), piece radius, what a click sends (or nothing) }

This is what `drawLocationAtCoords` already computes. It is the real content of
View.elm, and it can be in Roc from the first version.

The rest of the screen is small and changes wholesale:

- **the hand**: up to 5 cards, each with its colors and its action (activate, discard, cover or none)
- **a line of instructions**
- **the credits line**
- **the cheat sheet**: a few lines
- **up to two buttons**: oops and done

So our "virtual DOM" is two mechanisms, neither of them general:

1. **The board is a keyed patch.** JS builds the SVG once, one element per slot.
   On each update it sets the attributes that changed, by slot id. Nothing is
   created or destroyed.
2. **The panel is replaced.** A handful of text and buttons, rebuilt from
   scratch each time. It is cheap, and no user can notice.

A click never carries a JS closure. Each clickable slot or card carries the
message Roc gave it, and JS hands that message straight back to `update`.

## Layers, in order

1. **The rules, pure Roc, with the tests.** Port the twelve rules modules and
   port `tests/Example.elm` into Roc `expect`s. Also write the ordered
   Dict/Set and the faithful `elm/random`. The layer is done when the tests
   pass and, if we take up the oracle, when a scripted game matches Elm move
   for move.
2. **The platform.** This is a small wasm platform in the canvas-apps mold
   (`host.zig` + `main.roc`), but driven by events instead of a clock:
   `init : U64 -> Box(model)`, `update : Box(model), Msg -> Box(model)`,
   `view : Box(model) -> View`. `roc glue` generates the JS reader, as
   `JsGlue.roc` does for canvas apps.
3. **Version 1, the fat JS.** Roc returns the slot map and the panel as data.
   JS owns layout, the SVG skeleton, the patching and the text. The game is
   playable in a browser.
4. **Roc takes the panel.** The panel becomes a small tree of nodes in Roc
   (div, span, b, button, text, and a style list), and JS renders it by
   replacement. JS is left with the board skeleton, the patcher and the event
   plumbing.
5. **Roc takes the skeleton.** The polygon layout moves into Roc: `view` also
   reports slot positions, JS draws whatever it is told, and nothing about
   Fast Track is left in JS.

A checker runs at every step. The canvas apps are gated through `page_check`
plus a shot rendered with `mini_canvas`, with no browser. Here the equivalent
drives a scripted game through the wasm and asserts on the slot map, then
renders the board to a PNG so I can look at it.

## The one gap in the wire

**`JsGlue` doesn't read `Str`**, which is on the canvas-apps open list. Fast
Track needs text: card names, instructions and hints.

- The colors can be closed tags in Roc (the six zone colors, plus the few
  highlight colors View uses), so they need no strings.
- The text can't avoid them.

So `JsGlue` gains `RocStr` decoding: the small-string case and the heap case,
about twenty lines of JS emitted by the script. That makes Fast Track its
second user, which is when that code earns its place.

## Questions for Steve

1. **Where does it live?** One option is a new repo (`roc-fasttrack`), which
   would copy the platform and `JsGlue`. The other is a directory in roc-apps
   beside `canvas_apps/`, which shares `glue/`, `docs/roc-notes.md` and the
   deploy to roc.lynrummy.com. **I'd pick roc-apps**, because the platform and
   the glue are shared the day we start. Your phrase "brand new project" could
   mean either.
2. **Elm as an oracle?** It would mean installing the `elm` 0.19.1 binary (one
   file, about 25 MB, no npm) and building `ft.html` to replay seeded games.
   Without it, the ported tests are the only judge of the rules.
3. **Player count.** The Elm code is written for N sides (`Polygon`,
   `zoneColors`), but the todo says the UI to pick it was never built. Should
   the port stay at Elm's hard-coded 4 (`Game.beginGame`), or should picking 2–6 be in scope?
4. **WhatIf / the AI.** `WhatIf.elm` (358 lines, with `Debug` in it) is the
   start of the computer player. Should it be ported with the rest, or left
   until the game plays?
