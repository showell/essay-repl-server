# Could the notes use our Roc markdown?

Yes, for about a day of work, but not as roc-markdown stands. Today's `Md.render_document` would visibly hurt 83 of the 359 notes, mostly by losing code blocks and rules. It would also repair 114 notes that Python-Markdown is mangling right now. Five small additions to the document mode remove nearly all the losses, and three notes need an edit. The one trap is that 29 of the 66 stored comments would land on the wrong paragraph unless a script moves them first.

## What the server does now

`essays.render_markdown` strips front matter (no note has any) and calls Python-Markdown 3.5.2 with `fenced_code`, `tables` and `sane_lists`. Nothing post-processes the HTML. `view_body` adds the dot scripts when the page holds `class="language-dot"`. In the browser, `dot.js` draws each fence, and the comment widget anchors a comment on the Nth `p` or `li`.

## The comparison

I rendered every note through the server's own function and through `render_document` at 7e516eb, on roc-markdown's pinned Roc, passing every fence through as code. All 359 rendered. After whitespace and the noise below, 151 notes are identical.

| Roc loses | Notes | Example |
|---|---|---|
| Indented code | 49 | 105 blocks collapse into paragraphs (`camera-splits-in-three`) |
| Rules | 47 | `---` shows as three hyphens, 124 times |
| Images | 3 | 7 images become links (`odin-webgl-spike`) |
| Angle-bracket URLs | 3 | `<http://...>` shows as text |
| Raw HTML | 2 | `gopher-roc-demo`'s styled page; `<sup>` in `the-day-the-guesses-lost` |
| Email autolinks | 1 | `red@red.R0` becomes a `mailto:` link, 110 times |
| Reference links | 1 | `[#101][]` shows as written |

| Roc wins | Notes | Example |
|---|---|---|
| List right after a paragraph | 104 | Python prints "...for a rule: - roc-chat's read rule...; - ..." |
| Nested lists | 58 | Python flattens a two-space nested item |
| Bare URLs | 8 | Python leaves them unlinked |
| Bold inside italics | 7 | `*...**source**...*` loses its bold |
| Fence in a list item | 5 | Python shows inline code |
| Angle-bracket placeholders | 4 | `<inviter's name>` vanishes as an unknown tag |
| Strikethrough | 3 | Python leaves `~~` literal |
| Lost text | 1 | Python drops the last 40 lines of `roc-chat-leaves-the-nest` at a `<script` in backticks |
| Issue number | 1 | `#12641` at a line's start becomes an h1 |

Two differences could go either way. In 41 notes a continuation paragraph stays inside its list item, where Python ends the list and restarts it. In 3 notes, quotes separated by a blank line stay separate.

The rest is noise or nearly so. Heading ids appear in every note, invisibly, and they are a gain. Roc writes `&#39;` and `&quot;` where Python writes the character, which no reader sees. Roc keeps tabs in code, so 45 notes need `tab-size: 4`. Roc writes `align=` on table cells, which the server's `th, td` rule overrides, so 72 cells in 4 notes need a line of CSS.

Three things don't differ. The 343 tables in 162 notes have the same cells. The 156 dot fences in 48 notes come out the same, so `dot.js` and `view_body` work unchanged. Neither side does smart quotes or footnotes.

## What a switch takes

roc-markdown needs about 120 lines and their tests, all gated to the document mode so the chat's frozen answers don't move: rules (25), indented code (50, the only one needing care, because of list items), images as a new document option (20), angle-bracket URLs (15), and email autolinks off (5).

The server needs about 60 lines: a small Roc app with a build step in `ops/install.sh`, and `render_markdown` calling it and failing loudly if it is missing. That app's fence hook gives a `raw` fence its body unescaped, and the CSS above goes in. A one-time script of about 40 lines moves each comment's `para_index` by matching its paragraph's text.

Roc's echo platform has no stdin, and one argument stops at 128 KiB, which two notes exceed. My harness passes such a note in parts, and that worked. Speed is no issue: a process for the largest note took 86 ms on a dev build, where Python took 207 ms.

Three notes need edits: `gopher-roc-demo` goes in a `raw` fence, `the-day-the-guesses-lost` rewrites three `<sup>`s, and `one-defect-four-times` makes two reference links inline. The 5 essays in claude-collab use the same function, and I didn't compare them.

## The book's typesetting

This doesn't depend on the switch, because `book.css` styles plain tags. It could go on the Python output today, in about half a day. One rule has to go: `p:has(+ pre)` turns the paragraph above a code block into a small caption, and the notes have 700 such paragraphs. The `article >` selectors become `.wiki-md >`, and the comment widget's fixed colors need dark-mode values. The switch adds only the heading ids, which allow section links and a table of contents.
