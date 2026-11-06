# The tutorial: what's next

*2026-11-06, updated at the end of the day's long session.*

## Where it stands

The book is live on the dev channel at http://143.244.172.148:9210/tutorial/, with 36 pages, 29 diagrams and 14 embedded widgets. Safari's code list is closed, so the book is the main work now.

The order follows [the chapter order note](book-chapter-order.md), with two rules: progressive difficulty, tempered by categories. The first half holds one frame still, and it's fine to tease concepts there that get explained later.

- **The big picture:** Introduction, The problem, One whole module, The modules.
- **One frame:** The world; nature (Trees, Grass, The sky, Mountains); man-made things (The road, Rails, Radio towers); billboard critters (Stills, The elephant, the corner critters, A pig, Herds).
- **Motion:** The ride instant, The beacons, The cat, The bird, The stepped things, The rider, The bike, The throttle, What a cat does to the rider, The rider's gaze, The truck.
- **Under the hood:** The math layer, Proving it, The platform, Zooming back out, then the appendices and credits.

The sky comes before Mountains because `Mountains` imports `Sky`.

The voice follows the Roc tutorial to a degree: "we" and "you", a rare "hooray", short plain sentences, Hemingway over Faulkner. Prose work stays with me, with no delegating.

## Next

1. **Settle the new order.** Fix what a cold read finds, and show the parts on the contents page, which is still one flat list.
2. **The later chapters** to the same proofreading standard. The cat and the math layer are the longest, at 42 KB each.
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
