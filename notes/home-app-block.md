# The App block: one row of the home page, read from a file

*angry-gopher's `zig-server/src/home.zig`, 2026-10-18. A refactor in three steps, the third not yet judged.*

## What an App block is

The home page of lynrummy.com is a launch pad: a headline, then one row per
app, each with a thumbnail, a linked title, a paragraph, a button, and a
small line of tech facts. *Which* apps, and in *what order*, lives in one
file, `pages/home.txt`, read from disk at request time. The file is a
little markdown-ish language:

```
# Apps by Steve and Claude

## Lyn Rummy -> /game
cta: Play
lang: Elm
tech: a solver
code: https://github.com/...
A two-deck rummy, its board solved by search,
for two players or against the bot.
essay: /essays/lyn
image: /img/lyn.png
```

A `##` line starts a block and names its title and link (`->`). Then
`name: value` lines fill its fields, and every other line is description,
joined with spaces. Blank lines only separate blocks. Seven field names:
four required (`cta`, `lang`, `tech`, `code`), three optional (`essay` for a
"Read more" link, `image` for the thumbnail, `install` for an "Install
locally" link). A description is required too.

Each block becomes an `App`:

```zig
pub const App = struct { title, href, cta, lang, tech, code, essay, image, install, desc };
```

The parse is shared. The home page renders the `App`s as rows, and
`/gallery` renders the same list as cards. The gallery once kept its own
hand-copied list "in the same order as pages/home.txt", which went stale
the first time a row moved. One parse, two renderers.

## What the smell recipe saw

`cookbook/zig/smells.shale` flagged `pushApp` as the longest parameter list
in angry-gopher: **12 parameters**. The parser held the block being read as
ten separate locals, `c_title` through `c_desc`, plus a `have` flag. At
both of `pushApp`'s call sites, all ten went through by position:

```zig
if (have) try pushApp(alloc, &apps, c_title, c_href, c_cta, c_lang, c_tech,
                      c_code, c_essay, c_image, c_install, &c_desc);
```

Ten strings of one type, in one order, at two call sites. Swap `c_tech` and
`c_code` in one of them and it still compiles; the page just shows the
wrong line in the wrong place.

The same body had a second shape: seven branches alike but for a name and
a length.

```zig
} else if (std.mem.startsWith(u8, line, "cta:")) {
    if (!have) return error.MalformedHome;
    c_cta = std.mem.trim(u8, line[4..], " ");
} else if (std.mem.startsWith(u8, line, "lang:")) {
    if (!have) return error.MalformedHome;
    c_lang = std.mem.trim(u8, line[5..], " ");
} ...   // tech:, code:, essay:, image:, install:
```

Each branch carries its prefix's length (`4`, `5`, `6`, `8`) by hand, and
a new field needs a new branch, a new local, a new reset on `##`, a new
parameter and a new argument at two call sites: six edits to stay in step.

## The three steps

**First, the parse apart from the read.** `parseHome(io, alloc)` read the
file and parsed it in one function. Now it is a line:

```zig
pub fn parseHome(io: Io, alloc: Alloc) !Parsed {
    return parseHomeText(alloc, try store.read(io, alloc, "pages/home.txt", .unlimited));
}
```

and `parseHomeText(alloc, src)` is the grammar, pure, testable on a string.

**Second, tests of the grammar, on the old code.** It had none: the only
test near it checks that a missing `home.txt` is a 500. So before changing
the parser, two tests went in and passed against the body as it was:

- a full block, the optional fields there and absent, a description
  joined across lines;
- `MalformedHome` for each required field left out, one at a time, and
  for prose before any block, a field before any block, a title with no
  `->`, no headline, and no app.

Then a plant, to see the tests bite: the `cta` check taken out of
`pushApp`. The missing-field test failed, and the check went back. That
commit stands on its own, with the parser unchanged and the grammar now
held to its comment.

**Third, the block as a value.** The ten locals and `have` become one
optional value, the block being read:

```zig
const Draft = struct {
    title: []const u8,
    href: []const u8,
    cta: []const u8 = "",
    lang: []const u8 = "",
    tech: []const u8 = "",
    code: []const u8 = "",
    essay: []const u8 = "",
    image: []const u8 = "",
    install: []const u8 = "",
    desc: std.ArrayList(u8) = .empty,
};

var block: ?Draft = null;   // none until the first `##`
```

`have` is gone because it was always the same fact as "is there a block":
`block != null` now says it. A `##` line pushes the old block and starts
a new one in one expression, and the defaults do the reset that ten
assignments used to:

```zig
if (block) |*d| try pushApp(alloc, &apps, d);
block = .{ .title = ..., .href = ... };
```

The seven field branches become one loop over the names, unrolled at
compile time:

```zig
const field_lines = [_][]const u8{ "cta", "lang", "tech", "code", "essay", "image", "install" };

} else field: {
    const d = if (block) |*d| d else return error.MalformedHome;
    inline for (field_lines) |name| {
        if (std.mem.startsWith(u8, line, name ++ ":")) {
            @field(d, name) = std.mem.trim(u8, line[name.len + 1 ..], " ");
            break :field;
        }
    }
    // prose: the description
    if (d.desc.items.len != 0) try d.desc.append(alloc, ' ');
    try d.desc.appendSlice(alloc, line);
}
```

`name ++ ":"` and `@field(d, name)` are resolved at compile time, so the
generated code is the same seven comparisons. But the name now appears
once, and the prefix length comes from the name instead of a hand-counted
`4` or `8`. A field name in the list with no field of that name in
`Draft` does not compile. "Stray outside a block" is checked once,
before the field lines and the prose alike, instead of eight times.

`pushApp` takes the block:

```zig
fn pushApp(alloc: Alloc, apps: *std.ArrayList(App), d: *Draft) !void
```

Three parameters, down from twelve, and nothing positional to swap.

## What stays as it was

- **The grammar.** The prefixes do not overlap, so the order of the field
  list cannot change a result. A `## ` line is still checked before a
  `# ` line, so a title is never taken for the headline.
- **`App` itself.** `Draft` and `App` have the same fields, apart from
  `desc`, a growing buffer in one and a finished slice in the other.
  `pushApp` is where one becomes the other, and where the required fields
  are checked.
- **Both renderers.** They see the same `App`s.

## Where it stands

Steps one and two are committed, but not pushed. Step three is written and
not yet judged. Its judge is the two grammar tests and angry-gopher's
gate, which run after the kernel's tier 3 and its properties sweep finish,
so that two builds are never run at once. If the tests pass, it is
committed and goes out with the gate.

## A question it leaves

`Draft` and `App` could be one type: `App` with defaults, and `desc` built
apart, then set at the push. I kept them separate because they mean
different things: a `Draft` may be incomplete, and an `App` never is, as
`pushApp` is its only door. That's the distinction "make state honest"
asks for. It costs nine field names written twice. If a tenth field
arrives, it is added in three places: `App`, `Draft`, `field_lines`. Two
of those are the compiler's to keep consistent, the copy into `App` in
`pushApp`, and the parse test's expectations.
