# The tutorial: what's next

*2026-11-06, written at the end of the night, for tomorrow morning.*

## Where it stands

The book is live on the dev channel at http://143.244.172.148:9210/tutorial/, with 18 pages, a table of contents, 19 diagrams and 5 widgets. It names 67 of the 72 modules. Eight widgets are built and running on the dev channel, and four of those are new to the book.

The renames are still landing on their branch, and nearly everything below waits on them, because it edits the same text.

## First thing tomorrow

**Code comes first, as you said, so we can close the book on it:** land the renames, then `Pixels`, the bare-F64 lint, the throttle's gates rename, and the 12 `if`-under-a-lambda sites. The tutorial work below follows.

1. **Embed the new widgets.** `route`, `bends`, `step` and `rehearsal` go into their chapters.
2. **Move the existing widgets up.** A chapter with a widget opens with a very brief intro, then the widget, which frames the rest of the chapter.

## Then, in the same pass

The chapter agent has all of this queued, and most of it comes from your comments tonight.

- **An opening chapter, "Introduction",** with a little prose before the ride, since the demo takes a moment to load. The book's title stays.
- **A new chapter, "The road":** `Joint`, `GroundSighting` and `RailSighting`, opening with the `bends` widget.
- **Two short sections:** `SafariCritter` in "The world", and `CanvasRoll` in "The stepped things", quoted whole.
- **A builder check** that every module is named in the book.
- **The 61 reader fixes** from [the forward-references list](book-forward-references.md), including chapter openings that restate their premise. The list also defines "the gate", which most of "Proving it" depends on.
- **The throttle's "gates" get a new name,** so they stop colliding with the merge gate.
- **"The workhorses" section** stops using that word. The modules become "core utility modules", if they need a name at all.
- **A table for the proof,** generated from `gates/proof.expected`, where the slider was.
- **A widget or diagram near the top of each section,** following [the openers plan](book-chapter-openers.md), which also suggests other framing for chapters with no widget.

## After that

- **"Zooming back out":** the closing chapter is still a stub.
- **The later chapters** to the shape of Sky and Cat, adding 🌳 and 🍃 as each is reworked.
- **The fact-check pass,** which clears the 9 remaining `[check:]` notes.
- **Publishing to roc.lynrummy.com.** `site/publish.sh` needs a small change to know about the book.
- **Trying the stylesheet on the essay surface,** after comparing roc-markdown with Python-Markdown across the notes.

## Parked or waiting

- **Odin:** parked until tomorrow, as you said. The next step there is your call.
- **The Rocco rerun and PR** come in a couple of days: `foreign.shale` is ready, and the `Dropdown` fix is written up in [the first contribution note](rocco-first-contribution.md).
- **Shale's time budgets and shared parse** come after the code work.
