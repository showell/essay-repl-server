# Roc in the contents

You asked for a table of contents that shows the book is half about Roc. A cold reader went through every chapter after the first five, named the Roc idea each one really teaches, and checked it against the code the chapter quotes. These are my picks from its inventory.

## Renames

A chapter whose main point is a Roc idea gets a title that leads with it, using the official tutorial's terms. The app name stays after a colon, where the app is what the chapter's picture shows. Refused loses its old name outright, because "Refused" tells a reader nothing. The slugs stay the same, so no links break.

| Now | New title | What the chapter teaches |
|---|---|---|
| Billboard Critters | Tag unions: billboard critters | tags, tags that carry values, `match`, the exhaustiveness error |
| A far tree | Lists and map: a far tree | `map`, `map_with_index`, a lambda in place, `concat`, the first `expect` |
| Asking a kind | Where clauses: asking a kind | methods, static dispatch, `where` |
| Refused | Errors as tag unions | `Try`, `?`, `? \|BehindCamera\| OutOfSight`, `keep_oks` |
| A flip book | Immutable values: a flip book | a new value each step, record update |
| The clock | Opaque types: the clock | `Clock :: U32`, a moment against a length, `crash` |
| Rehearsal | Variables and loops: rehearsal | `var`, `$`, `while`, `for`, inside a pure function |

The other app chapters keep their titles: they're rightly about the app. Proving it stays as it is, because its main story is the hash gate, not `expect`.

## Two new interludes

Each is short, like Functions, with a Code | Term | What it says table.

1. **Records**, right after A far tree. The book teaches records a piece at a time, across six chapters: destructuring an argument, the `fill` shorthand, the open record `..`, record update, nested update, `..` in a pattern, and renaming a field. The interlude gathers them, one quoted line each. The six chapters then drop their explanations.
2. **Pure functions and effects**, right after A flip book. `!`, the thick arrow `=>` against the thin `->`, and the input as a plain value. Today this is one paragraph in The ride instant. Asking a kind, Rehearsal and The platform all lean on it, and Asking a kind points forward to it for `main!`. The paragraph in The ride instant becomes a pointer.

With those, 12 of the 39 titles name a Roc idea, counting Types, Functions and Platforms.

## Smaller fixes I'm making anyway

- `??` is defined twice, in The bird and The math layer. It gets defined once, in The bird.
- When to `crash` and when to return a `Try` is first stated in Proving it, chapter 35. A paragraph at the end of Errors as tag unions states the rule where `Try` is taught.
- The list functions (`map`, `fold`, `keep_oks`, `join_map`, `find_first` and seven more) each get a gloss in passing across about twelve chapters. They go in one table in the patterns appendix.
- `Book.slugs` still had Rehearsal after "What a cat does to the rider", so the page-to-page links sent readers the wrong way. Fixed.

## Not doing

- **A "Functions as values" interlude.** The idea is spread over five chapters, but each use reads plainly where it comes. One more sentence in Functions covers it.
- **Gathering the extra pattern forms** (`|` alternatives, `..`, guards, tuples). Each one comes up once and explains itself in place.
