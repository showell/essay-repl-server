# Does the Safari Ride book cover the Roc tutorial?

*2026-11-06. The book at roc-apps master 48922e6, against roc-lang.org/tutorial as of today.*

The tutorial has 76 idioms, by my split. The book covers 34 and shows 8 more without naming them. Another 11 are gaps that Safari's code could fill, and 10 are gaps it can't, because Safari has no example. The other 13 are left out for a reason, each given below.

The tutorial is current. Every idiom I could test compiles on the pinned Roc (nightly-2026-11-03-34bd006), with one small difference in how an inline `expect` fails. I couldn't test `read_str!` or the two dependency headers, because they need a platform or a package this box's test programs don't have. So the differences further down are choices made in this codebase, not stale tutorial text.

## Fix these first

1. `?`. The tutorial gives it a whole section. The book says only that the game has none, and never says what it does. One sidebar quoting `Users.from_files` from roc-chat would also close the gaps on merged error tags and on `Try(ok, err)`.
2. `??`. The book leans on `?? crash` and never says what `??` is. The tutorial doesn't teach it either, so a reader who did the tutorial has never seen it.
3. `where`. The book quotes three `where` clauses and doesn't mention them. They're the reason `Timeline` works for both a cat and a bird.
4. Numbers and `Dec`. The tutorial says plain numbers default to `Dec`. Safari uses `F64` throughout, and no line of code says `Dec`. The book never explains why.
5. `dbg` and inline `expect`. No code in Safari, roc-chat or roc-markdown uses either, so the book can't quote one. A single sidebar can cover both, and it has a good point to make about `Fraction.of`.

## Every idiom, in the tutorial's order

Covered means the book explains it, or shows it and names it. Shown means it's in quoted code and nothing says what it is.

| Tutorial section | Idiom | The book |
|---|---|---|
| Hello, World | The `main!` entry point, taking `_args` and answering `Ok({})` | Omitted |
| Hello, World | `echo!` | Omitted |
| Hello, World | `roc main.roc`, and `main.roc` as the default | Omitted |
| The REPL | `roc repl`, with expressions and definitions | Omitted |
| The REPL | Piped input, `--no-color`, `NO_COLOR` | Omitted |
| Pure and effectful functions | An anonymous function | Covered: The road, The bird |
| Pure and effectful functions | Functions as ordinary values | Covered: Mountains, The math layer, The platform |
| Pure and effectful functions | A `!` ending marks an effect | Covered: The ride instant, The platform |
| Constants | `name = value` | Covered: The bird, The beacons |
| Constants | No reassigning or shadowing, a warning with exit code 2 | Gap, Safari has an example |
| String interpolation | `"${...}"` | Gap, Safari has an example |
| String interpolation | Each part must be a `Str`, so `.to_str()` | Gap, Safari has an example |
| String interpolation | Advice: name a long expression | Omitted |
| Expect | Top-level `expect` | Covered: One whole module, Proving it |
| Expect | `roc test` | Covered: One whole module, Proving it |
| Expect | `roc fmt`, with no options | Gap, no Safari example |
| `for` style | `for x in list` | Covered: The cat, The platform |
| `for` style | `var $name` and reassigning it | Covered: The cat, The platform |
| `for` style | A `var` can't be reassigned from an inner function | Gap, no Safari example |
| `for` style | `for_each!` | Omitted |
| `fold` style | `.fold(start, step)` | Covered: The math layer |
| Blocks | A function's body is one expression, which can be a block | Covered: The stepped things |
| Blocks | A block as a plain value | Shown: The math layer |
| Statements and expressions | The difference, and blocks as the bridge | Gap, Safari has an example |
| Statements and expressions | `1..=10` | Gap, no Safari example |
| `return` statements | `return` | Covered: The cat |
| `return` statements | A warning for code after `return` or `crash` | Omitted |
| `crash` statements | `crash "..."` | Covered: The world, Proving it |
| `crash` statements | `crash` isn't error handling | Covered: The world, Proving it |
| `crash` statements | The platform decides what follows a crash | Gap, no Safari example |
| `expect` statements | `expect` inside a block, skipped under `--opt=speed` | Gap, no Safari example |
| `dbg` statements | `dbg` | Gap, no Safari example |
| `if` expressions | `if` as an expression | Shown: The ride instant, and many others |
| `if` expressions | The one-line `if` with no braces | Omitted |
| `if` expressions | `if` with no `else`, as a statement | Shown: The cat |
| Records | A record literal | Covered: The ride instant, and throughout |
| Records | `Bool.True` and `Bool.False` | Shown: The platform, The rider's gaze |
| Records | Record update | Covered: The bird, The rider, The bike |
| Records | `{ a, b } = record` | Shown: The elephant |
| Lists | A list literal | Covered: throughout |
| Method Calling | `x.len()` is `List.len(x)`, found by type | Covered: One whole module |
| Pattern Matching | List patterns, with `..` | Covered: The truck, but see the corrections below |
| Pattern Matching | Patterns nest | Covered: The bird |
| Pattern Matching | The `_` default branch | Covered: A pig |
| Tags | A list's items must have compatible types | Gap, Safari has an example |
| Tags | A tag with a payload | Covered: The beacons, The cat |
| Pattern matching on tags | Matching tags | Covered: The world, and throughout |
| `Try` | No `null`, with `Ok` and `Err` instead | Covered: The sky, The bird |
| `Try` | `match` on `Ok` and `Err` | Covered: The bird |
| `Try` | A tag with no payload | Covered: throughout |
| `Try` | Error tags from two sources merge | Gap, no Safari example |
| `Try` | The number types, and `Dec` as the default | Gap, Safari has an example |
| Exhaustiveness | A missing case is an error | Covered: The world |
| Exhaustiveness | A needless `_` warns, so avoid `_ =>` | Gap, Safari has an example |
| `Try` methods | `.ok_or`, which is `??` here | Gap, Safari has an example |
| Underscore patterns | `_` inside a pattern | Covered: The rider |
| The `?` postfix operator | `?`, and what it stands for | Gap, no Safari example |
| Types | Inference, and annotations being optional | Shown: throughout |
| Types | Soundness and immutable values | Covered: The rider, Rehearsal |
| Types | `roc` runs despite errors, so `roc check && roc` | Gap, no Safari example |
| Parameterized types | `List(Str)` | Covered: The cat, The bird |
| Function types | `->` and `=>` | Covered: The sky, The platform |
| Function types | `A, B -> C` | Shown: throughout |
| Function types | `Try(ok, err)` | Gap, Safari has an example |
| Type variables | A lowercase type variable | Covered: The cat, The bird, The bike |
| Type variables | `where` | Shown: The cat, The bird |
| Structural types | Tag union types | Covered: The world, The bird |
| Nominal types | `Color := [...]` | Covered: The ride instant, The cat |
| Upgrading from alpha-4 | The old syntax | Omitted |
| Dependencies | Headerless apps and the Echo platform | Omitted |
| Dependencies | `app [...] { pf: platform ... }` | Gap, Safari has an example |
| Dependencies | A package and `import pkg.Module` | Gap, Safari has an example |
| Platforms | One platform per app, which supplies the I/O | Covered: The platform |
| Platforms | The standard library has no effects | Gap, no Safari example |
| Platforms | The popular platforms | Omitted |
| Additional Resources | Links | Omitted |

## Shown but not named

These need a sentence each, beside code the book already quotes.

| Idiom | Where it's quoted | Suggestion |
|---|---|---|
| A block as a plain value | `Lens.focal`, in The math layer. Also `Mountains.snow_peak_height`, `TreeDraw.ring_angles` and `Animation.alternating_timeline` | The text calls it "a value computed from other values". Say that the braces are a block, whose value is its last line. |
| `if` as an expression | `SafariApp.step`, in The ride instant: `paused = if ...` | Say that `if` answers with a value, as the bird chapter does for `match`. |
| `if` with no `else` | `Animation.playing_at`, in The cat | One clause: this `if` is a statement, so it needs no `else`. |
| `Bool.True`, `Bool.False` | `SafariApp.canvas_app` writes `Bool.False`, and `Gaze` writes a bare `False` | Say that a `Bool` is two tags, and that both spellings compile. |
| `{ a, b } = record` | `Wildlife.bend_critters`, in The elephant | The book names this in parameter lists but not here. It's the one such line in the game. |
| Annotations | Throughout. Safari has 1,481 annotations. | Say in One whole module that Roc would infer every one of them, and that we write them anyway. |
| `A, B -> C` | Throughout | One clause, in The sky, where `->` is named. |
| `where` | `Timeline.at_beat` and `Timeline.instant` in The cat, `Animation.path_spot` in The bird | See below. |

`where [lift.plus : lift, lift -> lift]` says that `lift` can be any type with a `plus`. That's why a cat can measure its lift in `CatHeights`, and a bird in something else, with one `path_spot`. The Cat chapter already says "a cat fills the first with its own poses", so the sentence fits right after that.

## Gaps Safari's code can fill

| Idiom | The example | Chapter |
|---|---|---|
| No shadowing | `Throttle.acceleration`, the names `a1` to `a4`. They're numbered because a name can't be reused. | The throttle |
| `"${...}"`, and `.to_str()` | `VehicleLimits.turn_speed`, a crash message: `"... no speed for a turn of ${degrees.to_str()} degrees"`. It's the only one in the game modules, and the book's code has no `${` at all. | The truck, or Crashes that help |
| Statements and expressions | `Animation.playing_at` has `for` as a statement. `World.built_segment` has `match` as an expression. | The cat, where `for` first appears |
| A list's items must match | `SafariApp.frame`: every shape in the list is a tag of one union. That's the tutorial's `Bird`, `Number` fix at scale. | A frame is a list |
| The number types and `Dec` | `Distance` and the table in Numbers with units. `canvas_apps/safari/bare_floats.txt` lists what may hold a bare `F64`. | Numbers with units |
| Avoid `_ =>` | `EmojiStills.emoji_polys_for` needs its default, because numbers have no end. `Trees.accent` has none, so a new tag fails to compile. | A pig, which can contrast them |
| `??` | `World.SegmentIndex`, already quoted, for `?? crash`. For a plain default, `Shapes` and `Brush` in `lib/`: `List.get(xs, i) ?? 0.0`. | The world |
| `Try(ok, err)` | `Fraction.from_ratio : F64 -> Try(Fraction, [OutOfRange])`. It's the only `Try` type in the game. | Crashes that help, beside `Fraction.of` |
| The `app` header | `web.roc`, line 3 | The platform |
| A package and `import pkg.Module` | `web.roc`: `lib: "../lib/main.roc"`, then `import lib.WasmApp` | The platform |

Every `??` in the game modules is a `?? crash`, 23 of them. The plain defaults are all in `lib/` and the gates.

`web.roc`, `lib/` and `gates/` are out of reach of the book's includes, as the book's own check note says. The last two rows, and the `lib/` example for `??`, need that fixed, or need quoting by hand.

## Gaps with no example in Safari

Each of these is something a reader should still hear, in a line or two.

| Idiom | Why Safari has none | Suggestion |
|---|---|---|
| `?` | Nothing in the game can fail in a way a caller must handle. Safari has 0, roc-chat 151, roc-markdown 26. | A sidebar in The ride instant, where the book says the game has no `?`. Quote `Users.from_files` from roc-chat. |
| Error tags merge | The same reason. | The same sidebar. `Users.from_files` declares five error tags, and its two `?`s pass along the tags of the calls they wrap. |
| `dbg` | Safari's proof is hashes and `expect`s. All three repos have 0. | A sidebar in Proving it. `dbg` works in a pure function, so it's the one way to look inside `Bike.advance` without changing its type. |
| Inline `expect` | All three repos have 0. | The same sidebar, as a contrast. `Fraction.of` crashes in every build, and an inline `expect` is skipped under `--opt=speed`, so it couldn't do that job. |
| `1..=10` | Safari writes `U32.until(0, n)` and `U32.to(0, n)`. All three repos have 0 ranges. | A note in Herds. `for` takes a range, and `List.from_iter` doesn't. |
| A `var` stays in its function | A program that breaks the rule doesn't compile. | A `{{fails}}` program in The cat, next to "nothing outside can see it". The compiler's message is good. |
| `roc fmt` | It's a tool, so it isn't in the code. | A clause in The page itself. It explains why the book's code has tabs and the tutorial's has spaces. |
| `roc check && roc` | It's a tool. | A row in "Getting it to compile". `roc` still runs a program with a type error, reports it, and exits 1. My test printed its first line before the error, because it never reached the bad code. |
| What follows a crash | It's up to the platform. | A sentence in Crashes that help, saying what the page does. I didn't check what that is. |
| The standard library has no effects | Effects are absent from the game altogether. | A sentence in Where the effects went. |

## Left out on purpose

| Idiom | Why |
|---|---|
| `main!` and `echo!` | Hello world. The book assumes the tutorial, and Safari's entry point is an app record, which The platform covers. The gate programs do use both, and The platform says so. |
| `roc main.roc` | Installing and running a first program isn't the book's job. The ride is already running in the page. |
| `roc repl` | The same. It's a tool for trying Roc, and it has nothing to do with this program. |
| Piped REPL and `NO_COLOR` | Details of that tool. |
| Naming a long expression | General advice. The book practices it on every page. |
| `for_each!` | It's effectful, and the game has no effects. Neither roc-chat nor roc-markdown uses it. The `var` rule it illustrates has a row of its own above. |
| The warning after `return` | Safari has one `return`. The compiler's message explains itself. |
| The one-line `if` | `docs/roc-style.md` rules it out, and Safari holds that at zero, so the book can't quote one. |
| Upgrading from alpha-4 | Anyone reading the book is on current Roc. |
| Headerless apps, Echo | Safari's apps all have headers. It's part of hello world. |
| The popular platforms | The book names roc-ray, the one it uses. A list of the others would date. |
| Additional resources | The book already points to the tutorial. |

## Where this code differs from the tutorial

All of these forms are current, unless the line says otherwise.

| The tutorial | This code | Which is current |
|---|---|---|
| Teaches `.ok_or(0)` for a fallback | Writes `??`, and `docs/roc-style.md` calls a silent default a mistake: "never a silent `?? default`" | Both compile, and `x ?? y` is the shorter form. Safari's rule is a house rule. |
| Has no opaque types, `.{ }` blocks or `Type.(x)` | 102 opaque types, 125 type blocks, 118 wraps and 161 unwraps | Both. The book teaches these itself, which is right, since the tutorial's section on nominal types is very short. |
| Doesn't cover modules | One type per file, with a block of definitions | The type module is what the pin wants. A `module [...]` header gets a deprecation warning. |
| Leaves most code unannotated | Annotates nearly everything | Both. |
| Uses `?` for errors | Uses `crash` for bugs and has almost no `Try` | Both. Safari has so little that can fail. |
| `1..=10` | `U32.until(0, n)` | Both, and they aren't interchangeable. `..=` gives a `Range`, and `List.from_iter` wants an `Iter`. |
| Plain numbers, so `Dec` | `F64` inside unit types | Both. |
| The braceless `if` | Always braces | Both compile. Braces are a house rule. |
| Four spaces | Tabs | Tabs. `roc fmt` at the pin turned four spaces into a tab when I tried it. |
| An inline `expect` works "essentially like a `crash`" | Not used | At the pin, a failed one in a plain `roc` run prints `Expect failed`, carries on to the end, and exits 1. The tutorial's wording is a little strong. |

## Two corrections to the book

"Only `Truck` and `Paint` use a list pattern", in The truck, isn't so. `SceneDraw.second_shape_points`, `EmojiStills.still_facts` and `TreeDraw.trim_hull` use one too, and so do `expect`s in `BirdDraw`, `Ground` and `TreeDraw`. `trim_hull` is worth a look: `[.., a, b]` takes the last two items, a form neither the book nor the tutorial shows. Perhaps the sentence meant only the patterns that walk a list.

"`List.from_iter` over a range", in Herds, is loose. `I64.until(0, n)` is an `Iter`, and a real `0..<n` range is refused there.

## How this was checked

I read the whole book, and the tutorial's code, section headings and a report of its prose. On the pin I compiled the tutorial's forms and ran 11 `expect`s over them. That covered `?`, `where`, nominal types, list and tag patterns, and `Dec`. The shadowing warning, the interpolation error, the `var` rule, both exhaustiveness messages and `--opt=speed` were each tried on their own.

Two Shale tools came out of this, on the `idioms` branch of roc-apps, in `canvas_apps/safari/tutorial/`.

`roc_examples.shale` finds a feature by reading Roc's syntax tree. It knows 90 features and reads 262 files in about two seconds. Run it with no setting for the list, `feature=guard` for one, or `feature=all` for a table of counts.

Its counts match a separate `git grep` on `var`, `for`, `while`, `return`, `?? crash`, `expect` and others, and I read all five `match` guards by hand. Safari's counts include `lib/`, `gates/` and the book's builder, so they run higher than the game alone. roc-ast is on the 10-30 nightly, not the 11-03 pin, though it parsed every file.

`roc_tutorial_code.shale` prints the tutorial's 46 code blocks by section, from a saved copy of the page.
