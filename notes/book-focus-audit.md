# The book's focus audit: what goes, what merges

You asked for every chapter after the first five to have a sharp focus. Later chapters should teach or reinforce key Roc ideas, and app-only chapters stay only if they pay off earlier ones. A cold reader audited the 39 chapters from Functions onward, and these are my calls on its verdicts. I'm going ahead with them now. Say so if you want any of them back.

## Cuts and merges I'm making (44 chapters become 37)

| Change | Why |
|---|---|
| **Stepping** goes into **The ride instant** | It has a diagram and three bullets, and no code. The ride instant already makes its point. |
| **Grass** goes into **The sky** | It has no Roc idea of its own: one rectangle and a constant. Together they make one backdrop chapter. |
| **Types for places** goes into **The pipeline** | It's mostly setup for the pipeline, and it shows `Distance` for the third time. |
| **Nature types** goes into **Asking a kind** | It teaches nominal types for the third time. Its real job, why methods sit inside the braces, is what Asking a kind needs. |
| **Stills** is cut. Its one Roc point, a still as plain data in units of its own height, moves into **Billboard Critters** | The rest is production history (how the stills got made), not Roc. |
| **The bike** goes into **The rider** | The two chapters show record update and `with_lean` twice over. |
| **The truck's lights** goes into **The truck** | It re-shows the truck's sprite. Its new content is two short `match`es. The truck chapters are due a rewrite anyway, after the truck refactor. |

## Verdicts I'm declining

- **The beacons stays its own chapter, rather than merging into The setting sun.** It's the simplest thing derived from the clock alone, and the one home of `Steps` wrapping. A merged chapter would carry four widgets.
- **What a cat does to the rider stays separate from The cat.** It's short and sharp: the world changing the rider. The cat chapter is already the longest in the book.
- **Rails stays separate from The road.** It's where depth order meets individual quads. Its record-update teaching moves to its proper home (below).

## Roc ideas that get one home each

- **Record update** `{ ..r, f: x }`: in A flip book's `step_back`. Other chapters point there and stop re-explaining it.
- **Match guards** (`if` on a branch, in The rider's gaze): explained where they first appear. Today nothing explains them.
- **`??`**: explained once, in The bird. The math layer just uses it.

## Defects found along the way

- The "what catches you out" appendix cites chapters that don't exist.
- The glossary defines "card", which no chapter uses.
- The glossary says a polygon has "five or more corners". The code says any other number of corners.
