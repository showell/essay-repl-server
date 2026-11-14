# The .note demo: Roc runs on the server

*2026-11-14. The report on the demo prompt. The code is committed in essay-surface (`bb8da54`). It isn't released, and isn't pushed.*

## Where Roc runs, and why

**On the server, as a separate program.** `format/render_note.roc` is a headerless app on Roc's built-in platform, built with `--opt=dev` into `render-note` next to the server binary. Each time a `.note` file changes, the Go store runs it with the note's text as its arguments and reads back the page as JSON (`note.go`). The page is cached the same way a markdown note's is, so no request ever runs Roc.

- **Why this arrangement:** essay-repl-server already runs its Roc renderer this way, so it's proven on this box. It needs no host to build. A Zig host would have to be built against roc's builtins, and the roc checkout here is from 09-16 while the pin is 11-03.
- **The seam is one JSON value,** written by the builtin `Json.to_str`. Neither side has its own escaper, and Go rejects any field it doesn't expect.
- **Cost: arguments are the only input.** That puts a ceiling on a note's size: about 4 MB of argument space (`ARG_MAX`). The largest real note is 167 KB.
- **Cost: there are two things to deploy.** `release.shale` builds only the Go binary. Until it also builds `render-note` into `bin/`, a released server shows each `.note` as a page saying it can't be shown. I didn't add that step, because I couldn't run a release to prove it.
- **Cost: the browser can't run it.** Widgets or a live preview would need Roc in the page, as wasm. `Parse` and `Page` are pure, so they would carry over unchanged. Only the 18-line app is tied to this platform.

## Changes to the types

**None of the ten types changed shape.** The demo needed only what the proposal had promised:

- **Makers and readers for the opaque types:** `Phrase.from_pieces`, `Text.from_spans`, `NoteName.from_str`, `WebAddress.from_str` and `Diagram.from_source`, each enforcing the rules its doc states, plus `is_eq : _`.
- **`Table`, `ImageFile` and `Widget` still have no makers.** The demo syntax can't write them, so no note can contain one. `Page` crashes on them, and the crash message gives that reason.
- **The one pushback was a link to a `NoteName`.** The renderer can't know whether the target is a `.md` or a `.note`. So it writes `/notes/<name>`, and the server redirects that to the `.note` if one exists, otherwise to the `.md`.

## What was built

- **`format/Parse.roc`:** the syntax, documented in its header. It's markdown cut down to what the types can hold: no escapes, a blank line before every block, and styles that hold only words and code. A note that doesn't parse gets a page naming the line and what's wrong.
- **`format/Page.roc`:** renders the HTML, marking blocks with `data-c` the way `markdown.go` does. For each block it also gives the text a reply anchors to and the byte offset just past its element.
- **Diagrams** are drawn in the browser with the same viz.js and defaults essay-repl-server uses (`assets/`). A diagram takes replies like a code block does.
- **Markdown notes are untouched.** They go through exactly the code they did before, and their pages are byte for byte the same.

## The new check

`scripts/note_check.shale` is now a stage of `fast.shale`. It runs 25 checks:

- **The Roc:** `roc fmt --check` and `roc check` must pass with no errors or warnings. All 60 expects must pass, and the count is held to the `expect` lines in the files.
- **The renderer:** it builds `render-note`, and the demo's diagram must draw with the page's own viz.js under node.
- **The real server,** with the demo note, a markdown note and a broken note. Replies go to the diagram, a subpoint and a quote paragraph. The note is then edited on disk, and the replies must follow. A link by name must redirect, and the broken note must fail on its own page without affecting the others.

I planted a fault for each part and put it back after. These four went red: block ends one byte short, a missing diagram script, an `expect` that nothing imports, and a diagram viz.js can't draw.

`fast` passes. `full` passes every stage except the audit. The audit fails on `shale-book-part-two.md (3 ticks)`, a note added today, and it fails the same way at HEAD before my change. Whether those ticks render faithfully is your call.

## How to see the demo

These commands build everything and then serve essay-surface's 12 sample notes plus the demo on :9300, with the comments kept under `.run/`:

    cd ~/showell_repos/essay-surface && shale scripts/note_check.shale
    ./essay-surface -notes notes -comments .run/comments -addr 127.0.0.1:9300

The demo is `/notes/format-demo.note`, and its source is `notes/format-demo.note`. I haven't looked at it in a browser, so the eye test is still to do.
