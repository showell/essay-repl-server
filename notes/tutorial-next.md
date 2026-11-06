# The tutorial: what's next

*2026-11-06, updated at the end of the day's long session.*

## Where it stands

The book is live on the dev channel at http://143.244.172.148:9210/tutorial/, with 25 pages, 29 diagrams and 11 embedded widgets. Safari's code list is closed, so the book is the main work now.

The chapter order is: Introduction, The problem, One whole module, The modules, The ride instant, The world, The road, The sky, Birds and cats: drawing the stills, The cat, The bird, The elephant, Rhinos, giraffes and the other corner critters, A pig, Herds: cows and pigs, The beacons and the headlights, The stepped things, The math layer, Proving it, The platform, Zooming back out, then the appendices and credits.

The voice follows the Roc tutorial to a degree: "we" and "you", a rare "hooray", short plain sentences, Hemingway over Faulkner. Prose work stays with me, with no delegating.

## Next

1. **A stretch of chapters about the rider.** The stepped things is now the longest chapter, at 56 KB, and it should become several chapters. The rider is always deciding whether to accelerate, brake or hold steady, and that's the likely spine. It takes in the bike, the throttle's limits, "What a cat does to the rider", and a new section on the rider's gaze, which the pig chapter foreshadows through `Distracting` (`Gaze.roc`). The truck may want its own chapter too.
2. **The later chapters** to the same proofreading standard, once the split is done. The math layer is the next longest.
3. **"Zooming back out"** still ends in a placeholder.
4. **The fact-check pass,** after the dust settles: the `[check:]` notes, "about eighty modules", "the JS keeps the clock", the cat's timing depending on speed as well as position, and the hand-pasted tables of real values, which nothing keeps from drifting.
5. **Publishing to roc.lynrummy.com.** `site/publish.sh` needs a small change to know about the book.

## Small open calls for Steve

- Is the sun's `scale` as a `Fraction` right? The lens only widens, so it can't pass 1, and it crashes loudly if that ever changes.
- `lift.mapped(...)` would let the bird's arc read as a formula, but it's an escape hatch on `Distance`. I'd leave it.
- The comment "note" button shows on every paragraph. Should it show only on hover?
- `gates/FrameBench.roc` compiles only at publish. It checks clean in 0.16 s, so it could join the merge gate.

## Parked or waiting

- **Odin:** the next step is Steve's call.
- **The Rocco rerun and PR** come around 2026-11-08: `foreign.shale` is ready, and the `Dropdown` fix is written up in [the first contribution note](rocco-first-contribution.md).
- **The flaky widget check** in `book_check` hasn't come back since the two-frame wait went in. Its failure message now says whether the canvas felt the press.
