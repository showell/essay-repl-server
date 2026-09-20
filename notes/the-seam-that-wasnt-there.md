# The seam that wasn't there

*2026-09-20 — on being asked to break two JavaScript files into small modules,
and deciding not to*

Six Roc programs now run on a web page and on a desktop from one set of files:
three arcade games, a world you fly around, a pixel paint program, and a movie
you can scrub. The browser half of that is two JavaScript files — a decoder
for the picture the wasm module answers, and a runner that owns the clock, the
keyboard and the speaker. 263 and 312 lines; 194 and 215 once you take out the
comments.

The question put to a reviewer was whether there is a set of small modules
hiding in those two files. The answer came back: no, and here is why. This is
that argument, because the reasoning generalises further than the files do.

## Length is the wrong unit

Every argument for small modules I have seen starts by citing a line count,
and a line count is a proxy for the thing that actually matters, which is:
**when someone changes this, how many places do they have to change?** A
thousand-line file that always changes in one place is fine. Two fifty-line
files that always change together are one file with a boundary drawn through
the middle of it, and the boundary costs you every time.

So the test is not "is this long", it is "would a cut here leave two files that
must change together?" And that test can be run against the history rather than
guessed at by eye.

## What the history said

The decoder has an obvious-looking seam down the middle: it reads words into
descriptors, then paints descriptors onto a canvas. Decode and paint. Pure and
effectful. It practically asks for the knife.

Three commits have changed that file's content. All three straddle the line.

| what it added | decode side | paint side |
|---|---|---|
| a camera transform | the kind table, `readShape` | `setLens`, `paintFrame` |
| a raster image | the kind table, `readShape` | `paintImage`, `paintFrame` |
| the cold-read fixes | `readFill`, `readShape`, `decodeFrame` | `paintFor` |

Zero isolated changes. And the structural reason is visible once you look:
the first two lines of the file are the wire's vocabulary — which shapes
exist, which brushes exist — and **both halves switch on it.** The reader
produces a mode; the painter consumes it. Every new brush is a coordinated
edit on both sides of any cut you make there. The seam is where the phase
boundary is, and the phase boundary is not where the change boundary is.

There is a second, quieter argument. A reader's real question is never "how
does decoding work". It is "how does a glow brush get from the wire to the
screen?" Today that is two sections of one file. After the split it is a
two-file question, and the answer to *would a maintainer open exactly one file
and find the whole answer* becomes no.

## The candidates that nearly made it

The keyboard is the strongest: 44 lines, one job you can name without an
"and", no coupling upward, and it is the only thing in either file that has
ever changed on its own — twice. Both times the change was **one line added to
a lookup table that is already the first thing in the file.** Forty-four lines
against four new edit sites is not a trade.

The pointer looks identical and is weaker: it never changed alone, because its
two arguments come from the function that would be left behind.

The speaker fails the one-job test outright. It is `makeSpeaker` — WebAudio,
34 lines — and `drawSpeaker` — a canvas overlay, 27 lines. Naming the file
needs an "and". Splitting *that* gives two thirty-line files. It also carries a
trap: two of the six programs have no sounds at all, so a separate speaker file
looks omittable on those two pages, and per-page script lists that differ is
the worst outcome available here. The day the Roc side gives one of them a tone,
those pages break with a `ReferenceError`.

## The cost, which is specific and which decided it

These pages have no build step. No bundler, no npm, no ESM. A page is HTML that
loads `<script src>` tags in order, each file defines one top-level `const`,
and the next file can see it. That is a real constraint and it is doing most of
the work in this decision.

Under it, one more file means:

**Three lists that must agree, and nothing checking them.** The build script's
copy, six `page.html` script lists, and — until an hour ago — two hardcoded
filenames in the headless check. Add a file to five of six pages and the sixth
is broken in a browser while the check still passes. Add it to a page but not
to the copy and you get a 404, and the check still passes. Today every list has
exactly two entries and the risk is nil. Each file added multiplies an
unchecked coupling.

That one had a fix worth making regardless of the verdict, so it is made: the
check now reads the `<script src>` list out of the page it is checking and
fails if one of them was never copied. Three lists became two, and the two are
now checked against each other. A page loading a script the build script does
not copy fails headlessly instead of in a browser.

**One shared lexical scope, with short names in it.** `channel`, `scratch`,
`stopAt`, `show`, `FADE_MS`, `CATCH_UP` are already effectively global. More
files means more short names competing for one namespace, and a duplicate
`const` across two scripts is a `SyntaxError` that blanks the page.

**Load order becomes an ordering rather than a fact.** Today it is one fact —
wire before runner — written out six times identically. Six files make it a
sequence, written out six times, with no linter.

**And there is exactly one consumer configuration.** All six pages load the
same two scripts. Every module exports the same ten names with the same arity.
Nothing is optional, nothing varies, no page wants a subset. Decomposition pays
when different consumers take different pieces, or different people own
different pieces, or pieces are replaced separately. Here it is one
configuration, written out six times.

## The strongest argument against all of the above

The evidence is two days old and it is all *construction* history. This layer
was built in a burst; the runner was created in its present form yesterday. Of
course every commit touched everything — that is what building looks like.

**The must-change-together test, applied during a thing's construction, will
refuse to split anything, ever**, because during construction everything
changes together by definition. The maintenance pattern is different and nobody
has seen it yet. Once the wire stops gaining shape kinds — it now has all six
it needs — the decode/paint coupling the argument leans on goes quiet, and what
is left is somebody fixing a gradient stop, or somebody adding a key. Those
*are* isolated.

I may be reading the scaffolding and calling it the building. The fair
resolution is a date, not an argument: revisit when three commits in a row have
touched one section only.

## The crack in the verdict

By the test's own criterion, the decoder passes — one job, stated in a
sentence, no "and". The runner **fails**. Its own README row names it "the
clock, the input, the speaker," which is three nouns, and a file that needs
three nouns has three concerns.

The answer here is that the three concerns are 44, 43 and 68 lines, they have
exactly one consumer each, and that consumer is thirty lines below them in the
same file. The honest version of the answer is that the runner's real problem
is not its shape but its *name* — it was called a game runner when all six
programs were games, and two of them are not any more. That is a rename, and
renames are cheap. If you want to disagree with the verdict, disagree there.

## The thing the question was standing in for

Behind "should these be smaller modules" was a better worry: that one
JavaScript bridge serving movies, arcade games, a map and a drawing tool is a
one-size-fits-all design that will eventually serve none of them well.

That worry is real and file decomposition is the wrong instrument for it.
Splitting two files into six does not make the bridge fit four kinds of program
better; it spreads the same vocabulary over more files and adds an ordering.
If the bridge is straining — and there is a good case that a drawing tool,
whose model *is* its picture, strains it — the strain is in what the wire can
say, not in how many files say it.

Which is the last thing worth stating plainly: **this is not a defence of big
files.** It is a defence of these two, under a constraint that makes new files
genuinely expensive. Put a bundler under this and half the costs above go to
zero, and the calculus flips. The argument is not "small modules are overrated."
It is that the unit of modularity is the change, not the line, and you can go
and look at which is which.
