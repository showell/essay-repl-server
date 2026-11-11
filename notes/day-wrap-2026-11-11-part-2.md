# The day, part two: 2026-11-11

The second half of the day turned "Asking a kind" from a chapter that tried to do two jobs into three chapters that each do one. The code moved with the book: four type and naming fixes landed because a reader looked at a page.

## The book

| # | Chapter | Where it stands |
|---|---|---|
| 1–8 | Introduction … A far tree | Passed. Swept today for "draw" and for chapter links. |
| **9** | **Types for places** | **New**, drafted at the end of the day: `RoadPoint` and `Spot`, almost all code, no picture. Unreviewed. |
| **10** | **The pipeline** | **New.** Three cold readers, three nitpick rounds and a long-read editor. Its diagram is the chapter's map ("outstanding"). Ready for your review. |
| 11 | Nature types | Passed earlier. Its opening now points back at the pipeline. |
| 12 | Asking a kind | Rewritten from a new spine: it opens on `rendering_of`, `where` is a constraint, and it has a concept table. Waiting for your full read. |

**A deploy is in progress.** The publish tier for 11 chapters is running. "Types for places" makes it 12, so the tier runs once more before you get the commands.

## What changed in the book's machinery

- **Chapter links.** `{{chapter A far tree}}` renders as a quiet, dotted link to that page. A title that isn't a chapter stops the build. A chapter outside the published range shows as plain text, so the live book never links to a missing page. The book's nine quoted references became links in the form "in the … chapter".
- **The draw sweep.** Chapters 1–12 hold no imprecise "draw" now. Functions produce or give back sprites, the platform paints, and chapters explain.
- **Diagrams** are held to the text column's width, with type big enough to read.
- **New widgets:** `pipeline`, which shows only what the pipeline renders, cropped to where it stands. `kinds` and `conifers` came earlier in the day.

## What changed in the code

Each of these started from a reader's question:

- **`Point`** is lib's own type: callers write `Point`, not `Point.Point`. That was 176 uses (Anton's nit).
- **`EmojiStill`** is the type, and the traced animals are its values, as in `EmojiStill.cow` (notramo).
- **`RaisedPoint` is `PointAtHeight`.** Its height runs either way, so "raised" said only half of it (your question about "Lowered").
- **The truck is an ordinary kind.** `Truck.scenery_sprite` replaces `truck_sprite`, and the repacked `SightedTruck` is gone. A cold agent found that the truck needs nothing a `Sprite.Setting` lacks.
- **`TreeSighting.tree_renderings` is inlined.** "The name saves too few tokens for what it obscures."
- **The style guide** gained one rule: a module that holds one type is that type.

All 60 apps check clean. Every gate passed before each merge, including the long expects gate (999).

## MISSION, as amended today

- **C15:** the opening says what's ahead. Name a chapter's Roc concepts only when the chapter is about one.
- **D7:** pronouns, calibrated. Use the name when in doubt, without stripping every pronoun.
- **D10:** precise, never casual. Casual writing reads as sloppy.
- **D11:** precise verbs. A clause constrains, a function gives back, a chapter explains, the platform paints. When the official tutorial phrases a concept, say it in our own words with its core terms.
- **C9:** chapter references are links, written "in the … chapter".
- **H5:** diagrams are no wider than the text, with readable type, and can run vertically.
- **H9:** every chapter gets a picture of its own. A shared picture is a smell.

## Reflection

1. **Your best edits were structural.** "The pipeline deserves its own chapter" did more for "Asking a kind" than three rounds of sentence fixes. The same goes for the warm-up chapter: a breather before the long one is a decision about pace that no reader agent would have suggested.
2. **I still reach for vague verbs.** "The pipeline drew", "a chapter drew", "a clause asks": each sounds fine until someone asks what actually happens. D11 is now the rule I most need to read before writing.
3. **I overcorrected once.** You asked for a Roc-concept preview in one chapter, and I put it in six. Your note to extrapolate on code fixes but take more care with prose rules matched what happened today: the `Point` sweep was welcome, and the preview sweep had to be pulled back.
4. **The flow check is a step, not a habit yet.** I orphaned the `where` preview by inserting the `Rendered` block without re-reading the hand-offs. MISSION already says to; I skipped it.
5. **Cold agents earned their keep on facts, not voice.** The truck agent and the long-read editor each found something real. The nitpick rounds found real friction too. Every sentence still came from one hand.
6. **Zulip is useful in small doses.** Two of the four code fixes came from there. Turning a remark into a gated root-cause fix, and saying so in the thread, is a good loop.

## Loose ends

- **The deploy:** finish the 12-chapter tier, then your commands.
- **Compiler PR 12925:** linux-core failed at a runner step, and linux-strategy failed in the differential test. Its log is readable only when the run ends, so I haven't judged it yet. Don't point Anton at it until I have.
- **Labels inside widgets** (Anton's exploded view): parked as an idea for kind and enum chapters.
- **Your reviews:** "Types for places" and "The pipeline" (new), then "Asking a kind" (rewritten).
