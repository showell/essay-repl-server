# Roc interludes

The idea: a few very short chapters that each stop the ride for one Roc idea. Each one is a short opening line, one real snippet from Safari Ride, a table that takes the syntax apart, and a line that hands back to the ride ("Back to the ride. More annotations are coming."). They also give the table of contents some Roc words.

## Which ideas get one

The test for an interlude: the idea is spread across several chapters, so no single chapter owns it. An idea that one chapter already owns stays there, such as tag unions and `match` in Billboard Critters, `map` in A far tree, `Try` in Refused, and `where` in Asking a kind. That test gives four:

| Interlude | Goes after | Its snippet | Its table takes apart | Why it's spread out today |
|---|---|---|---|---|
| **Annotations** | Platforms, packages and modules | `Distance.metres : F64 -> Distance`, then `frame_view_at` | the name, `:`, the arguments and their commas, `->`, what comes back, a type variable in lower case | One page reads one annotation as a first pass. The pieces as types, Things and Refused each add a piece. Records in annotations and annotations over several lines are never explained. |
| **Three ways to name a type** | The pieces as types | one of each from the ride: `Sprite.Setting : {…}`, `Distance ::`, `Conifer :=` | `:`, `::`, `:=`: what each one makes, who can build or open a value, and whether it can hold methods | The pieces as types introduces all three, Billboard Critters returns to `:=`, and Nature types finally owns it. The inventory found `:=` explained three times. |
| **Records** | Billboard Critters, just before Shapes | `Shapes.rectangle`, which takes a record apart | building `{ a, b }`, punning, reading a field, taking a record apart in the arguments, updating with `{ ..r, x }`, a record type in an annotation | These pieces show up in Things, Billboard Critters, Shapes and the flip book, a few at a time. |
| **Methods** | Refused, just before Nature types | `spot.foot().forward()` | the `.{ }` braces, `value.method()` as `Module.method(value)`, `<` and `==` as `is_lt` and `is_eq`, getter methods | Method calls are everywhere from Things on. `spot.lift()` and its kin are never explained, and Asking a kind needs methods before `where`. |

That brings the published book from 14 chapters to 18. None of the existing chapters moves.

## What changes around them

- **The chapter before each interlude** ends as it does now. The interlude's first line says it's a pause ("Before the next piece of the ride, a closer look at annotations.").
- **The chapter after each interlude** opens as it does now, because each chapter's opening already stands alone (MISSION C4).
- **The places that explain the idea in passing get shorter.** One page keeps its first pass at an annotation. The pieces as types, Billboard Critters and Nature types keep a line on `:=` and point back to the interlude. That's where the trim comes from.

## Shape of one interlude

The Annotations interlude, sketched:

> **Annotations**
>
> Every function in Safari Ride carries a type annotation, and the book shows many of them alone, before their bodies. Here's a small one:
>
> `{{signatures Distance.metres}}`
>
> | Piece | Means |
> |---|---|
> | `metres` | the function's name |
> | `:` | "has the type" |
> | `F64` | what it takes: one 64-bit float |
> | `->` | then |
> | `Distance` | what it gives back |
>
> *(a second, longer annotation, `frame_view_at`, with two arguments, and two rows on the comma and on a type defined in another module)*
>
> Back to the ride. Every chapter from here on reads annotations like these.

About 150 words and one table.

## Revised after Steve's reply: Functions, not Annotations

Steve: "annotations should mostly be covered under functions." So the first interlude is **Functions**. It still goes after Platforms, packages and modules, before The pieces as types, which defines its first functions (`metres = |metres| Distance.(metres)`).

Its snippet is a small, whole function: annotation and body together. Its table takes both apart:

| Piece | Means |
|---|---|
| `metres :` | the annotation: the function's name, then its type |
| `F64 -> Distance` | it takes one `F64` and gives back a `Distance` |
| `metres =` | the definition |
| `\|metres\|` | the function itself starts here: what it's given goes between the bars |
| `Distance.(metres)` | the body, whose value is what the function gives back |

A second, longer annotation, `frame_view_at`, adds two arguments and a type from another module. A body made of a block of named values, and a call with `.`, wait for Things, which uses them first.

The order then reads: Platforms → **Functions** → The pieces as types → **Three ways to name a type** → Things. There's a full chapter between the two interludes, so they never run back to back.

## Recommendation

Pilot **Functions** first (it was Annotations before the revision above). Write it and run it through the review rounds, then read it in place, between Platforms and The pieces as types. If the interlude format earns its place there, the other three follow the same pattern. If it reads as a detour, we've spent one short chapter finding that out.

The open question for you is whether the four listed are the right four, or whether some should be cut or swapped.
