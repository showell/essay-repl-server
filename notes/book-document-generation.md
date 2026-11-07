# How the book gets made

*2026-11-07. The state of document generation through Roc and Shale, including the syntax coloring.*

The short version: Shale does everything that touches the outside world, Roc does the one pure transformation in the middle, and the Markdown renderer knows nothing about Roc code. That split wasn't planned as a whole, but it has held up, and today's churn was a good test of it.

## The stages

| Stage | Done by | What happens |
|---|---|---|
| Expand | `build.shale`, 950 lines | `tutorial.md` holds prose and lines like `{{code Cat.instant_at}}`. Each becomes a fenced block with the real source in it |
| Split and draw | `book.shale` | The result is split at chapter headings, and Graphviz draws each ```` ```dot ```` fence, twice if it's wider than a phone |
| Render | `make_book.roc`, `Book.roc`, `BookFence.roc`, roc-markdown | Every page is turned into HTML in one pure Roc run, with navigation and contents |
| Color | `color_roc.shale`, 602 lines | Spans go around Roc code in the rendered HTML |
| Check | `book_check.mjs` | A real browser drives every page and widget |
| Publish | `book.shale` | The channel's book is replaced only by one that passed |

`tutorial.md` is about 2,700 lines, and it holds 225 includes. The last build made 43 pages and reached 2,122 links.

## Expansion: the book can't lie about the code

This is the part I'd keep if everything else went. The book doesn't contain code. It contains names, and the names are resolved at build time.

The include forms have grown to fit what chapters needed:

| Form | Gives |
|---|---|
| `{{code X}}` | One definition, with its doc comment and annotation |
| `{{code X from "a" to "b"}}` | Part of one, with `# ...` where lines were cut |
| `{{module X}}` | A whole file |
| `{{signatures A.b C.d}}` | Just the annotations |
| `{{types row X words}}` | A table row with the type from the source |
| `{{fails name}}` | A program, and what the pinned compiler says about it |
| `{{proof row N words}}` | A row of the held proof values |

Each of these fails loudly. An anchor that no longer occurs exactly once stops the build. A `{{fails}}` program that compiles stops the build, because the book's claim would then be false. Today that paid off many times over: more than 240 renames went through the book, and a name that had gone couldn't quietly survive in a listing.

There's a limit worth stating. Includes keep the listings true, and they do nothing for the prose around them. "`Beats`" stayed in the cat chapter's sentences long after `Beats` was deleted, and nothing complained. The prose is only checked by cold readers.

## Rendering: Roc, pure

`make_book.roc` runs on Roc's echo platform, which gives it arguments and a way to print, and nothing else. Shale reads the files and hands over the text, and the program prints pages. A comment line names each page's file, and the renderer's escaping means manuscript text can't forge one.

Because the hook is pure, a diagram has to be drawn before the render, and a widget's folder has to be looked for before it. That's why `Manuscript.Contents` exists: it's everything the render is allowed to know, as a value. It's a small but honest example of the book's own subject.

roc-markdown has one extension point, the fence hook, and `BookFence` uses it for four things: a live widget frame, a drawn diagram, a titled listing, and everything else as plain code. The same renderer also serves this essay surface.

## Coloring: outside the renderer

You asked for this to be Shale over Roc's AST, with no Roc knowledge in the Markdown processor, and to be told if the AST was too lossy. That's how it came out, and the AST was a little lossy, in a way we could live with.

The renderer leaves a ```` ```roc ```` fence as `<pre><code class="language-roc">` with escaped text. `color_roc.shale` runs afterward, on the rendered pages. It adds spans, and `book.css` decides how they look.

Two things make it more interesting than it sounds:

1. **A listing usually can't be parsed.** Most blocks are part of a definition. But every block came from a file, so the script parses the file whole and finds the block in it. The caption names the file, and the block's lines are the file's lines with a common indent removed.
2. **The tree doesn't hold everything.** It places strings, numbers, type names, tags and top-level names exactly. It has no comments and no keywords, so those are read from the text the tree doesn't claim, where a `#` can only start a comment. That's the lossy part, and it's handled by elimination rather than a second parser.

The guard I like most: a page's text must stay byte for byte the same once the spans are removed, or the build stops. Coloring can't change what the book says. A block that can't be placed comes out plain, and the run says so. The last count I saw was 198 blocks colored and none plain. That count is from before today's last few merges, though the build has passed since.

## Checking

`book_check.mjs` is what caught the two failures today that the merge gate couldn't. A rename sweep turned a fence into `widget route_segments`, and the build stopped because no such folder exists. Then a longer name made an inline call too wide for a phone, and the check failed the page at 490 pixels in 390. Neither is visible from Roc.

It also holds each widget to behavior: a click has to change the picture, unless the widget is marked as still.

## What's weak

- **The merge gate doesn't build the book.** It expands the includes but doesn't render or check, so an agent's green gate says nothing about fences or phone widths. That's what cost two failed rebuilds today. A cheap fix is to have the gate check fence words against folders.
- **It's slow for what it is.** A full build takes four to six minutes. Most of that is `book_check` at about three minutes, and release builds of 13 widgets at up to two. `looks=1` skips driving widgets, but I keep running the whole thing out of habit.
- **It hits Shale's limits.** A run gets 64 programs, and the main run sits near that, which is why widget builds moved to a child run. `name_hunt.shale` is now 327 bytes from Shale's 64 KiB script cap, which is the same kind of limit in the lints.
- **`build.shale` is large.** At 950 lines, it's the biggest piece, and it has grown a form at a time. It hasn't had the review the Roc has.
- **Book-specific code lives in three languages.** Shale, Roc and JavaScript each hold part of what a fence means. A widget fence is parsed in Roc, checked in Shale, and driven in JS with its own `STILL` list.
- **It isn't published.** The book is on the dev channel, on this box. `site/publish.sh` doesn't take it yet.

## Open questions

Could the same machinery serve other documents? Almost none of it knows about Safari. The includes need a source tree, and the fences need a folder convention. If roc-chat or Shale's own docs wanted listings that can't lie, I think it'd take a small amount of separation, mainly pulling the include forms out of `build.shale` into a cookbook recipe.

Should the prose be checked by anything besides readers? A lint could at least flag a backticked name in the prose that no longer exists in the code. That would have caught `Beats`, and most of what the rename sweeps had to list by hand. It's the obvious next gate, and I'm a little surprised we don't have it.

And coloring has a question I can't settle from here. It runs after rendering because the renderer mustn't know Roc, which was the right call. But it means the script reparses every source file on each build to find blocks that `build.shale` extracted from those same files a few minutes earlier. The expansion step already knows exactly where each block came from. If it left a note behind, the placing logic, which is the hardest part of `color_roc.shale`, might mostly go away.
