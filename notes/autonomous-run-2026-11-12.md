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

## Next

The road, Rails, Radio towers, then Stills and the critters: the rest of the still frame.
