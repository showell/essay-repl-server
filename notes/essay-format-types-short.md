# Session 8's types, the short read

The agent's full proposal is at http://localhost:9301/notes/essay-format-types.md. It runs about 240 lines, and you don't need to read all of it. Here's what matters, with a recommendation for each of its three questions.

## What it proposes

- **A note is a title, an optional subtitle, and a list of blocks.** There are eleven kinds of block: paragraph, heading, bullets, numbered list, quote, code, table, image, diagram, widget and divider.
- **Inline text is flat.** A span is plain, bold, italic or a link, and styles never nest.
- **Your two habits get types of their own:** the italic subtitle under a title (in 296 of your 522 notes), and the bold lead on a paragraph or bullet (in about 375 each).
- **A diagram is its dot source, as written, and a widget is a name plus a description** of what it shows. That's how the book drafts already write a widget, and there's room inside the type to grow.
- **Files are `<name>.note`,** beside the `.md` notes.
- **What it drops is small:** a second paragraph inside a list point is the largest loss, in 47 notes. Everything else touches 27 notes or fewer.

## Your watch-list, answered by this session

- **Sketch, or compiling Roc?** It compiled, without being asked. That's ten type-only modules, checked with no errors and no warnings. The agent planted two faults to prove the check was reading the nested types.
- **Bogged down in types?** No. By its own timestamps, the types took about 2 minutes, reading and counting your notes took about 12, and the report took longest. The counting is where the value is: every "we don't need that" comes with a number.
- **Bogging you down?** This is the risk the session shows. The proposal is thorough, and too long to reply to quickly. The fix is this kind of note: the orchestrator boils a report down to what needs you, with recommendations. I'd make that the pattern for Part Two, and the book can show it.

## The three questions, with my recommendations

1. **Note and Block: nominal or opaque?** Nominal means anyone can build and read them, at the cost that the types allow an empty list. **My recommendation is nominal for now.** It's the minimum viable product's choice, and opaque can come later when a reader actually needs a guarantee.
2. **More than one paragraph in a list point?** It's 47 notes. **My recommendation is no.** Your agents write those notes, and they'll adapt: one paragraph per point reads better anyway.
3. **Keep the divider?** **My recommendation is to keep it.** It's cheap, and 80 notes use it.

## Next, if you agree

Session 9 is the minimum viable product: one `.note` file, parsed and rendered end to end on dev, with a real diagram drawn. That forces the first real decision about where Roc runs (MISSION PC). The types get revised only where that end-to-end path pushes back.
