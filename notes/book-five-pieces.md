# Does the book's spine solve the five pieces?

Mostly yes. Every chapter after the opening five solves one of the pieces, or is a Roc interlude, or is one of the closing chapters. The spine has three soft spots, though, and The problem's preview has to be honest about them.

## The map

| Piece | Chapters that solve it |
|---|---|
| Things | Things, Tag unions: billboard critters, Shapes, Lists and map: a far tree |
| The rider's view | The pipeline, Where clauses: asking a kind, Errors as tag unions, and later The math layer |
| The world | The sky and the grass, Mountains, The road, Rails, Radio towers, Herds |
| Motion | Immutable values: a flip book, Records, Pure functions and effects, Opaque types: the clock, The ride instant, The beacons, The setting sun, The rider, The throttle, Variables and loops: rehearsal, The rider's gaze, The truck, The truck's motion, The cat, The bird, What a cat does to the rider |
| The person watching | "Pausing and stepping", a section in Pure functions and effects, and The platform |

Functions, Proving it and Zooming back out sit outside the pieces. That's fine: one is a Roc interlude, and the other two close the book.

## The soft spots

1. **The rider's view comes before the world.** The diagram reads things, then the world, then the view. The book goes things, then the view (the pipeline: how a thing reaches the frame), then the world. The book's order is the better one, because the pipeline is what every world chapter uses. The preview should follow the book, and the diagram can stay as it is: it shows how the pieces depend on each other, not the order the chapters take them in.
2. **The rider's view is split.** The pipeline chapters solve it in practice, and the perspective math waits for The math layer, near the end. A Far tree already says so. The preview can say it in one clause.
3. **The person watching has no chapter of its own.** It's one section of an interlude, plus The platform. The problem promises controls "they can find, and answer each one straight away", and the book pays that in two places, neither of which is named for the piece. One fix is to let The platform own the piece: it's where the input arrives and the frame goes out. It would need one short paragraph on the controls, taken from the interlude's section, which then just points to it.

Motion is half the book. That's honest: motion is where the ride's real difficulty lives.

## What I'd do to The problem

Keep it a problem statement. After the table, add one short paragraph that previews the book piece by piece in the book's own order: things, then the rider's view, then the world, all in one still frame, then motion, then the person watching, at the platform. Then the existing line about Platforms. No other changes to its framing.

Before that, decide soft spot 3: does The platform take over the person watching?
