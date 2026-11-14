# The types for a note format of our own

*2026-11-14. A proposal, for argument before anything is built on it. The types are in essay-surface's `format/` and compile at the box's pin. There are no functions and no Go yet.*

## The short version

- **A note is a title, an optional subtitle, and a list of blocks.** The title is a field, not a heading, because every note has exactly one.
- **Eleven kinds of block:** paragraph, heading, bulleted list, numbered list, quote, code, table, image, diagram, widget, and divider.
- **Inline text is flat.** A run of text is plain, bold, italic or a link, and what it holds is words and inline code with no style of its own. So styles never nest.
- **Two things from your notes become types of their own:** the italic line under the title (in 296 of your 522 notes) and the bold lead on a paragraph or bullet (in about 375 notes each).
- **What it drops is small.** The largest loss is a second paragraph inside a list item, in 47 notes. Next come code blocks inside list items, lists nested two deep, and bold or italics in headings, at under 10 notes each.
- **The files are `<name>.note`**, beside the `.md` notes, which keep rendering as they do now.

## Where the counts come from

I read the 12 notes in essay-surface's `notes/` and then counted every feature over all 522 notes in essay-repl-server's `notes/`, since 12 is too few to count by. The counter is `scripts/features.shale` in essay-surface. It reads the markdown line by line as `markdown.go` does, so code inside a fence counts only as code. Each count below is the number of notes that use the feature at least once. Where a count is a ceiling rather than exact, I say so.

## How to read the Roc

Four Roc forms carry this proposal.

- **`[A, B(x)]` is a tag union**, a sum type like Rust's `enum`: a value is exactly one of the tags, and `B` carries an `x`.
- **`X :: T.{ }` is an opaque type.** Only module `X` can build one or look inside, so a check in its maker is the only way in. Here the makers don't exist yet: they come with the parser.
- **`X := T.{ }` is a nominal type.** It's a named type whose insides anyone can build and read.
- **`.{ }` after a type holds its members**, here only nested type aliases, which other modules name as `Block.Prose`.

## Note

```roc
Note := {
	title : Phrase,
	subtitle : Note.Subtitle,
	blocks : List(Block),
}.{
	Subtitle : [NoSubtitle, Subtitle(Text)]
}
```

**For:** a whole note. The subtitle is the line under the title that says when, for whom, or what for: "*2026-11-05. Five flight drawings for safari's Roc bird...*". Today that's an italic paragraph, and 296 notes open with one. As a field, it's drawn as a subtitle and written as plain text, so its links and bold just work. (All five places where your notes put a link inside italics are subtitles.)

**Leaves out:** a second title (7 notes paste two drafts into one note), anything above the title (4 notes start without one), and front matter such as a date or an author. Dates already come from git, and the subtitle carries the rest as words.

**Nominal, not opaque:** a note built from valid parts is a valid note, so there's nothing for a maker to check. Its readers are the page, the index and the comments, and they read its fields directly. That's the call I'm least sure of; see the questions at the end.

## Block

```roc
Block := [
	Paragraph(Block.Prose),
	Heading({ level : Block.HeadingLevel, title : Phrase }),
	Bullets(List(Block.Point)),
	Numbered({ first_number : U64, points : List(Block.Point) }),
	Quote(List(Block.Prose)),
	Code({ language : Block.Language, body : Str }),
	Table(Table),
	Image({ file : ImageFile, description : Str }),
	Diagram(Diagram),
	Widget(Widget),
	Divider,
].{
	Prose : { lead : Block.Lead, text : Text }
	Lead : [NoLead, Lead(Phrase)]
	HeadingLevel : [Section, Subsection]
	Point : { prose : Block.Prose, subpoints : List(Block.Prose) }
	Language : [NoLanguage, Language(Str)]
}
```

**For:** one piece of the page, in reading order, and the thing a reply attaches to. A list's points and a quote's paragraphs would each take replies, as list items do today.

**Leaves out:** raw HTML of every kind. Only `gopher-roc-demo.md` uses it (its `raw` fence), and no note has an HTML block or comment. A widget is the way to put something live on the page.

## Paragraphs and their leads

**For:** `Prose` is a paragraph's words, with an optional bold lead: "**The short version.** Each tick is a pure function...". The lead is a part of its own because it's what your notes do with bold. Of the 8,737 lines with bold in them, about 6,900 open with it: 378 notes lead paragraphs this way and 373 lead bullets. A lead names its paragraph, so a reply or a table of contents could quote it.

**Leaves out:** a line break inside a paragraph. Your notes have no hard breaks (no two trailing spaces, no backslash), and 275 notes wrap their prose by hand, so a line break in a paragraph's source is a space.

## Headings

**For:** a `Section` (today's `##`) or a `Subsection` (today's `###`, in 86 notes) under the title.

**Leaves out:** deeper levels (no note uses `####`) and styles in a heading. A heading's words are a `Phrase`, so it can hold code but not bold or a link. That drops styling from headings in 7 notes. No title holds a style or a link.

## Lists

**For:** `Bullets` and `Numbered` lists. A numbered list keeps the number it starts at, because 19 notes continue a count past a heading or a code block ("5. The world..."), and starting them over at 1 would put a wrong number on the page. Each `Point` is one paragraph, with a lead if it has one, and a list of subpoints under it.

**Leaves out:**

- **A second paragraph in a point** (47 notes), and a code block (7 notes) or an image (1 note) inside one.
- **Lists nested two deep** (at most 9 notes; my count also caught a diff inside a code block), since subpoints have no subpoints.
- **Numbered subpoints** (4 notes), since subpoints are always bullets.
- **Loose and tight lists.** 27 notes put blank lines between points, and that would no longer change how the list is drawn.

The depth limit is in the types: a `Point`'s subpoints are `Prose`, which has no list to hold.

## Quotes

**For:** a quoted passage of one or more paragraphs, each of which may have a lead. 45 notes quote, mostly a before and after ("**Before:** ...") or a recommendation set apart.

**Leaves out:** a list inside a quote (3 notes, all in the book's edit notes) and a quote inside a quote (none).

## Code

**For:** text shown exactly as written, with the language it names, if any. 85 notes have Roc, 17 Zig, and 68 have code with no language.

**Leaves out:** syntax highlighting. Nothing draws a language differently today, and the type doesn't promise to. It also has no second way to write code: the 48 notes with four-space indented commands would fence them. (Today's `markdown.go` draws those as paragraphs anyway.)

## Text and Phrase

```roc
Text :: List(Text.Span).{
	Span : [
		Unstyled(Phrase),
		Strong(Phrase),
		Emphasis(Phrase),
		Link({ label : Phrase, target : Text.Target }),
	]
	Target : [Note(NoteName), Web(WebAddress)]
}

Phrase :: List(Phrase.Piece).{
	Piece : [Plain(Str), Code(Str)]
}
```

**For:** `Text` is a paragraph's, a cell's or a subtitle's words, as a list of spans. Each span is unstyled, bold, italic or a link. `Phrase` is words and inline code with no style. It's what a span holds, and what titles, headings and leads are made of. Code inside bold is common (215 notes) and code inside italics less so (56), and both are kept.

**Leaves out:** a style inside a style or a link. That drops italics inside bold (6 notes), a link inside bold (1), and strikethrough (3, which today's renderer shows as `~~` anyway). There are no footnotes, entities, escapes, inline HTML or reference-style links, and no note uses any of them.

**Opaque, because the maker keeps rules:** neither is ever empty, two unstyled spans never stand side by side, and no piece holds a line break. Two texts that read the same are then the same value.

## Link targets

```roc
NoteName :: Str.{}
WebAddress :: Str.{}
```

**For:** `NoteName` is another note, by its name without the extension (`basic-machine-design`). The maker checks it's lowercase letters, digits and hyphens. A link never holds a path or a server URL, so `/notes/x.md` (3 notes) and `x.md` (33 notes) become one form. `WebAddress` is an `http://` or `https://` address with a host and no space, `<`, `>` or `"`, so no `javascript:` or `file:` link can be written.

**Leaves out:** links to a place inside a note (none use them), link titles (none), and links to any other file. That last one is a `.patch` beside a note, in 1 note. Bare URLs (56 notes) and `<https://...>` (3 notes) still become links. That's a question for the syntax, not the types.

## Table

```roc
Table :: { column_headings : List(Text), rows : List(List(Text)) }.{}
```

**For:** a heading for each column, then rows of cells. 223 notes have tables, and 30 of them are more than four columns wide. The maker checks for at least one column and that every row is exactly as wide as the headings. A reader can then take a row's cells by column without checking the row, which is why it's opaque.

**Leaves out:** column alignment (4 notes use `:--:`), cells that span columns, tables without headings, and anything but text in a cell.

## Image

```roc
Image({ file : ImageFile, description : Str })
ImageFile :: Str.{}
```

**For:** a picture file kept beside the note, such as `sunset-before-5700.png`, with the words a reader sees if it doesn't load. 7 notes have images, 22 in all, and every one is on a line of its own. The maker checks the name: lowercase, digits and hyphens, then `.png`, `.jpg` or `.svg`, with no folder.

**Leaves out:** an image inside a sentence (none outside code), an image from the web or from elsewhere on the box, and sizes.

## Diagram

```roc
Diagram :: Str.{}
```

**For:** a diagram drawn from its dot source, as written. 63 notes have 183 diagrams between them, 3,649 lines of dot. The format never reads inside the source. Drawing it is Graphviz's job, in the browser as essay-repl-server's `dot.js` does or on the server, and the type doesn't decide which. The maker checks only that the source isn't empty and starts as a dot graph does (`digraph`, `graph` or `strict`).

**Leaves out:** other diagram languages, a caption, and per-note style. The defaults stay where essay-repl-server keeps them, in one place for every note. It's opaque so a caption or a layout choice can be added inside it later without touching any reader of a block.

## Widget

```roc
Widget :: { name : Str, description : Text }.{}
```

**For:** a place where a small live program will run, given as which widget it is and what it shows. The shape comes from your notes: 12 of them (the book drafts) already hold a `widget` fence with just such a description: "Press play and watch the two towers blink out of step." The description is what a reader sees where the widget can't run, and what an author writes before it exists.

**Leaves out:** everything a widget will need to run: its inputs, its size, its state, its code. That's the room. Because the type is opaque, those go inside it without any reader of a block changing.

## Divider

**For:** a break with no heading, today's `---`, in 80 notes. Mostly it sets a note's opening apart from its body, or its body from its sources.

**Leaves out:** the three spellings (`***`, `___`), which become one.

## What the format drops, by notes

Of the 522 notes:

| dropped | notes |
|---|---|
| a second paragraph inside a list point | 47 |
| blank lines between list points changing how the list is drawn | 27 |
| lists nested two deep | 9 at most |
| a code block inside a list point | 7 |
| a second title in one note | 7 |
| bold or italics in a heading | 7 |
| italics inside bold | 6 |
| a note with no title on its first line | 4 |
| numbered subpoints (they become bullets) | 4 |
| column alignment in a table | 4 |
| a list inside a quote | 3 |
| strikethrough | 3 |
| raw HTML (the `raw` fence) | 1 |
| a link inside bold | 1 |
| a link to a file that's neither a note nor a web page | 1 |
| an image inside a list point | 1 |

No note uses `####` or deeper, footnotes, task lists, hard line breaks, backslash escapes, entities, HTML blocks or comments, reference links, links to a heading, or link titles.

## Kept, though they'd be written one way

These are questions for the syntax, not the types, and no note loses anything by them:

- **Indented code** (48 notes) becomes a fenced block.
- **`_italics_` and `__bold__`** (5 notes) become `*` and `**`.
- **`/notes/x.md` and `x.md` links** become one link form, to a note's name.
- **`<https://...>` links** (3 notes) are written as bare URLs.

## The file name

**`<name>.note`**, as in `basic-machine-design.note`, beside the `.md` notes in the same folder. The extension picks the renderer, so an old note is never read as a new one, and a name with no extension (a `NoteName`) refers to either. I passed on `.essay`, because "essay" is the server's name and not the file's, and on anything with "md" in it, because the format shares none of markdown's rules.

## Where the types live, and how I know they compile

Ten modules in essay-surface's `format/`, one type each, with `format/roc-version` naming the pin (`nightly-2026-11-03-34bd006`). They sit apart from the Go at the root, which goes on rendering the old notes, and the new format's parser and renderer would join them there. `roc check format/Note.roc` reaches all ten and finds no errors and no warnings, and `roc fmt --check` passes. To make sure the check was really reading the nested types, I planted a misspelled type in `Block` and an undeclared nested type in `Text`, and each went red by name before I put it back. Shale's name, layout and error hunts are clean over the ten files, after three renames they asked for (`Point`, `first_number`, `column_headings`).

## Questions for you

1. **Note and Block are nominal, so the renderer and the comments read and match them directly.** The cost is that the types allow an empty list or quote, which only the parser would never make. Making them opaque closes that gap and makes every reader ask the module for each part. Nominal, or opaque?
2. **One paragraph per list point, and subpoints one level deep.** That's the largest loss: 47 notes have a second paragraph in a point, and 7 have code in one. Do you want points that hold more than one paragraph?
3. **The divider.** It's cheap, and 80 notes use it, but a heading or the subtitle does most of its job. Keep it, or drop it?
