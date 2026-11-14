# Session 9's demo, the short read

*2026-11-14. The agent's full report is at http://localhost:9301/notes/essay-format-demo.md. This is what needs you, with a recommendation.*

## See it

**The demo is live on your surface:** http://localhost:9301/notes/format-demo.note

It's one note in the new format, with paragraphs, lists, a quote, code and a dot diagram. Every block takes replies, the diagram included. Nobody has looked at it in a browser yet, so yours is the first eye test.

## What the session settled

- **Roc runs on the server, as its own program.** The Go server runs `render-note` whenever a `.note` file changes, and reads the page back as JSON. No request ever waits on Roc. The agent chose this because the old essay surface already runs its Roc renderer this way.
- **The types held.** None of the ten changed shape. The one pushback was a link to another note: the renderer can't know whether it's a `.md` or a `.note`, so the server redirects.
- **The costs are honest ones.** There are now two programs to ship, and the browser can't run Roc yet. The parsing and rendering code is pure, so it would carry over to the browser unchanged if a widget needs it.
- **Your markdown notes are untouched,** byte for byte.

## What I did before releasing

- **The release script now builds the renderer,** checks that it renders the demo, and moves it with its server through every swap. I proved a release, a rollback and a roll-forward on dev before touching yours.
- **The full check was red because of me.** My Part Two note had a bare code fence in a sentence. I reworded the sentence instead of excusing it.
- **Released as 8deea74,** with your 17 comments where they were.

One limit worth knowing: rolling back past this release while a `.note` exists fails safe. The older server doesn't list `.note` files, so the index check refuses and puts the new one back.

## Next: my recommendation

**Session 10: I write my own notes to you as `.note` for a while.** You and I are the real requirements, and real use is what pushes back on the types. That's cheaper and more honest than designing the next feature in the abstract. Widgets come after. They're the feature that forces the decision about Roc in the browser, and they'll be a better session once the format has been used for real.
