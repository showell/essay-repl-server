# Autonomous run, 2026-11-12: the log

This is a running log of the long book run you handed me. Each entry says what landed, and any decision I made without you is marked **Call**, with its reason. Everything listed here is on master, and the dev book is http://143.244.172.148:9210/tutorial.fresh/

## The book now

The book publishes 18 chapters. These are new or reworked since you left:

| # | Chapter | What happened |
|---|---|---|
| 5 | Types | Renamed from "The pieces as types". It keeps its `##` and annotation rows, which it needs before Functions. |
| 6 | Functions | The Roc interlude, now with a **Methods** section at its end. |
| 7 | Things | Stopped re-teaching what Functions covers, and four density cuts. |
| 8 | Billboard Critters | The same: arguments, blocks and method calls are no longer taught as new. |
| 14 | Refused | All three nitpick rounds done. |
| 17 | Grass | New. A clean draft, with its readers' fixes. |
| 18 | The sky | New. A clean draft, with its readers' fixes. |
| 19 | Mountains | New. A clean draft; its readers are reading it now. |

## Calls I made

- **Methods went into Functions, not its own chapter.** A Methods interlude would have pre-empted Nature types (methods inside a type's braces) and Asking a kind (dispatch). The one idea no chapter owned is that a method is a function associated with a type, and that `x.f(y)` is the type's `f(x, y)`. That fits a short last section of Functions, right before Things first uses it. So the interlude lane is done: Functions is the one interlude.
- **The sun moved to the motion half.** At step 1,529 the sun is out of view, behind the rider, so a still-frame sun chapter would have had nothing in its picture. The sun is really about motion, since it sinks step by step, and "The setting sun" already lives in the motion half. The still frame's world now runs Grass → The sky → Mountains → The road … The frame widget's layer order still lists the sun between grass and sky, which is harmless, because that layer is empty at this step.
- **The Bearing/Turn lesson moved to Mountains.** The `turn_as_bearing` failing program used to sit in the old sun chapter. Mountains is where bearings are first needed, so it moved there. The old sun chapter still has its copy until it gets its own pass.
- **The sky admits its picture is one color.** At step 1,529 the sky is near its day color and the horizon hasn't warmed yet, so the two colors match. The chapter says so, and hands the change to the second half. The old draft's table of sky colors at five steps was pinned by no test, so it's gone.
- **Code fix: `Scene.truck_renderings`.** The truck's `match` moved out of `scene_in_view` into a small function of its own. Three nitpick rounds had tripped on a `# ...` that cut the match off mid-way, and the book now quotes it whole. Every safari gate passed.

## Roc PR 12925

The second fix for the hang is green where it matters on the fork's CI: linux-eval passed, which runs the dispatch-chain test that used to hang, and static-checks passed, which runs the lint. Two jobs failed on runner trouble: linux-core timed out installing valgrind from snap, and the macOS build failed early with no log. linux-strategy and the harness job are still running; the harness runs the PR's regression test for the original segfault. Once those two are green, I'll push to the PR branch and post the short comment you approved.

## Update: the first half is complete

The book now publishes **23 chapters**, and the first half, one frame held still, runs to its end:

Things → … → Asking a kind → **Grass → The sky → Mountains → The road → Rails → Radio towers → Stills → Herds**.

Every new chapter got a clean draft, plus cold readers for truth and order and an animation think-aloud. Their fixes are in. The nitpick rounds are done for Grass, The sky, Mountains and The road. Stills and Herds are with their readers now.

### More calls

- **The old Elephant and "corner critters" chapters are gone.** Billboard Critters already teaches their code (`BendAnimal.bend_billboards`, `species_of`, `Billboard`).
- **The table of contents follows the new structure.** Its parts were left over from the old draft: "Man-made" sat above The road with no "Nature" before it. Now the order is "The big picture" → "One frame" (before Things), with the categories "Nature" (before Grass), "Man-made" (before The road) and "Critters that stand still" (before Stills). "Motion" now starts at A flip book.
- **Numbers no test pins came out.** Gone are the sky's five-step color table, the stills' polygon and point counts, the road's tan(22.5°) arithmetic, and the rail's "49 quads at 45°".
- **One more code fix:** `book_names.txt` now allows `U32.until` beside `U64.until`, since the prose names both.
- **A flow pass on the middle chapters** (Shapes, A far tree, Asking a kind) cut what Functions now teaches, and A far tree no longer opens with Shapes' first line.

### What's between the halves

The file still holds several old-draft chapters between Herds and A flip book: The modules, The world, A simple tree, A conifer, Roadside trees, and the old sun chapter. None is published. MISSION marks The modules and The world as open, and says the trees get only the far-tree chapter. When the motion half starts, my plan is to cut the three tree chapters and keep the old sun chapter's material for "The setting sun". That leaves The modules and The world as your call: they could become an interlude about the program's shape, or be cut.

## Update: the motion half has begun

The book now publishes **26 chapters**. The second half opens with three new chapters:
- **A flip book**, written fresh as the opening. It drops the parts One page and Functions now cover, and describes the step widget as it really is: three figures, and a play button that also stops the ride.
- **The clock**, which keeps a moment and a length apart, with the `clock_plus_seven` failure.
- **The ride instant**, which reads `RideInstant.next` whole, in its order. It also has the table of carried and derived parts, and model_at_next_step's input snapshot. The step widget and `step_back` now live only in A flip book.

Each got a truth and think-aloud reader, and their fixes are in. One code fix came out of it: `Steps.roc`'s doc comment said two clocks subtract, but `steps_since` is the only way to get the steps between them.

**Housekeeping:** the old draft's chapters are parked, unpublished, just before the appendices: The modules, The world, A simple tree, A conifer, Roadside trees, and the old sun. `book_negatives` used to stop reading at "The modules". It now stops at the first chapter the new book hasn't reached, and that boundary moves with each new chapter.

## Roc PR 12925

On fork PR #3, linux-eval and static-checks passed, so the hang and the lint are fixed. linux-core failed, and the macOS build was cancelled; both were runner trouble. linux-strategy and the harness job have run more than three hours, against 58 minutes upstream, so another case may hang in the strategy runner. I'll read their logs when they finish or time out. The upstream PR stays untouched until they're green.

## Update: 33 chapters, through the rider

The beacons → The setting sun → Stepping → The rider → The bike → The throttle → The rider's gaze.

- **The setting sun** takes in the parked old sun chapter's material: the sun's `Sighting` tags, its glow and disc, and why step 1,529 shows no sun.
- **Stepping** is the old "Stepping through the ride", rewritten short: the stepping modules, the step function, and what stepping costs.
- **The rider** and **The bike** are clean drafts.
- **The throttle** and **The rider's gaze** got a lighter pass. Their old drafts were sound and their numbers are pinned by expects, so I cut the "New in this chapter" lists, fixed stale chapter names, rewrote the negatives, and fixed the reader's findings. One of those: the gaze chapter quoted `Gawking.is_gawking`, which only the widget calls, so it now quotes `Gaze.noticed_pig`, which the brake really asks.
- **The beacons have no reader pass yet.** Their cold reader was stopped by a safeguards flag, which looks like a false positive.

**Memory:** at your request, `MEMORY.md` now tells cold agents to stop at a marked STOP line, right after the Roc and book entries.

**Roc PR:** linux-strategy passed on the fork. The harness jobs and the Windows jobs are still running.

## Next

The truck, The truck's motion, The truck's lights, then the cat, the bird, Rehearsal.

## Update, 2026-11-13: the whole book is drafted (44 chapters)

**Your new rule** ("a major code smell means a rewrite from scratch") is in MISSION G1.

**Refactors, each followed by a chapter rewritten from a new spine:**
- **Beacon:** `blink_phase` brings the phase inside one blink, and the key argument has a clearer name. The Beacons chapter is rewritten, and two readers have been through it.
- **Encounter timing:** `EncounterPlan.Timing` is gone. One function, `stage_at`, takes a plan, the clock and a length to a stage. Bird and cat errors are renamed with `map_err` and `?`. Timelines take a frame only. The Cat and The bird are rewritten.
- **Coast and LeanSearch:** no widget-only flag in the hot loop, no impossible `?? crash`, and one midpoint function. The ride got a little faster. Rehearsal is rewritten.
- **RoadAhead:** the private helper that shared its name with `RiderView.rider_point_ahead` is now `rider_point_round_bends`.

**New chapters:** The math layer (one point's trip from the road to the screen), Proving it (the gate's proofs), The platform (where the effects live), and Zooming back out. The old drafts' unpinned numbers and history are gone.

**A near-miss the gates caught:** I tidied the beacon's angle to `2π·(p/T)`. The page gate failed, because regrouping floats changes the last bits. It's reverted, and Proving it now uses it as its example.

**OUCH:** two cold readers read a stale copy of the built book, in the roc-apps checkout. Readers now always get the lane's build path. It's in memory.

**Open for you (no rush):** the old chapters still parked before the appendices (The modules, The world, three tree chapters, the old sun). They're unpublished. Do we cut them, or mine them for an appendix?

**Roc PR 12925:** linux-harness passed. linux-core failed on a CI-side valgrind install timeout. Windows is still running. I push only on green.
