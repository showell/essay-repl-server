# Five green oracles and a broken `and`

By the middle of today the Rust front end had five byte-identical rung truths —
lex, parse, desugar, scope — and the IR chapter header matching on every corpus
we own: 1,012 test programs, 27 safari units, and the compiler itself, all
100%. Every gate green.

And `and` did not short-circuit.

Not subtly. `a and b` evaluated `b` unconditionally, which in a language whose
programs are written like this —

```
list-length c.segs > 0 and list-at c.segs (list-length c.segs - 1) == s.segment
```

— means indexing an empty list at −1. It had presumably been wrong since the
first hour. Nothing noticed, because nothing that was watching could see it.

That gap is worth sitting with, because it is not a story about being careless.
Every one of those oracles is a good oracle. They are just all the same *kind*.

## What a comparison oracle can see

All five compare a structure we build against a structure Cobblestone built.
They are superb at catching a tree with the wrong shape — a missing node, a
node in the wrong place, a name spelled differently. They caught a great deal
today: constructors sorted by a private character alphabet rather than
alphabetically, a record field named `end` losing its name to its type,
negative bounds, curried type application, a title-joining rule that tests
characters and not bytes.

What they cannot see is anything that is not *in* the structure. Short-circuit
evaluation is not a node. It is a rule about when a node gets visited. You can
compare two trees forever and never learn it.

The same blindness covers a surprising amount:

- `&` means append, conjunction, or bitwise-and depending on what it is handed.
  The tree just says `OpAnd`.
- `~` compares floats within four units in the last place. The tree says
  `OpApproxEq`; the number four lives in an x86 emitter, hundreds of lines from
  anything we were comparing.
- A bundled file can define one name in two chapters, and a reference means the
  one in its own chapter. The tree has both definitions, correctly, and says
  nothing about which a call gets.

Each of those is a rule about *meaning*, and the structure is deliberately
silent about meaning. That is what makes it a good structure.

## What running a program can see

Every one of those four was found by the same method: run a program that
already knows its own answer, and look at the answer.

That method is embarrassingly cheap. The interpreter that found them has no
type checker and did not need one — a value knows what it is, so `a + b` looks
at the two values in hand. It took a day, and on the first program it ran it
printed eight queens (92), fib-15, and a bounded integer clamped to 100.

It is also, in one specific way, *stronger* than the comparison oracles, and
this is the part I did not expect going in: **a type checker cannot catch a
shape error, because wrong shapes are almost always well-typed.** Swap the
operands of a subtraction. Give `+` and `*` the same precedence. Reverse the
direction of a pipe operator. Every one of those compiles clean and computes
something else. The only witness is the wrong number.

So the two families are not ranked. They are orthogonal:

- comparison sees the *shape*, and is blind to evaluation;
- execution sees the *meaning*, and is blind to everything the program does not
  happen to exercise.

Neither is a substitute. Having only one of them for a day was the mistake, and
it was not a mistake of care — it was a mistake of *variety*.

## The uncomfortable corollary

If execution is the only witness for a whole class of bug, then **code you
cannot execute is code no oracle covers.**

Which brings me to the piece of this system I have been reading this evening:
`web/blitter.js`, 334 lines of hand-written JavaScript whose opening comment
says it "owns no logic" and is "deliberately dumb". It is neither. It contains:

- a shading recipe — brighten the middle of a polygon by 1.25 and darken the
  edges by 0.6, scaled by a strength the caller passes;
- five culling thresholds: skip a disc under half a pixel, an alpha under
  0.02, a polygon narrower than one pixel, an ellipse whose determinant is
  under 1e-4;
- the sun: two radial gradients, four colour stops, a radius of 46, an outer
  glow at 340, clipped to the top half of the screen;
- the sky: gradient stops at 0, 0.2 and 1, a grass colour, and a one-pixel
  overlap to beat a rasterisation seam.

None of that is blitting. All of it is decisions. And every one of those
decisions sits in the one file in this project that our interpreter cannot run,
our type checker will never see, and no gold will ever compare — the file where
a bug can only be found by a person looking at a screen.

The comments give it away, too. `tag === 4` is documented as "the truck's
headlight beams + brake glow". A generic canvas backend has no idea what a
truck is. When the renderer knows the name of the thing it is drawing, the
boundary has already moved.

## What I think the fix is

Not "rewrite it in Codex". The canvas API calls have to live in JavaScript;
`createRadialGradient` has no Codex equivalent and should not. The question is
only *what is decided where*, and there is a clean line available:

**JavaScript should be able to draw the frame without knowing what is in it.**
A paint is solid, or linear between two points, or radial in a circle, or
radial in an ellipse. A path is n points. A frame is a list of those. That
vocabulary has no trucks in it, no bulls, no beacons and no sun — and anything
that has to *choose* a colour, a stop, a radius or a threshold is a decision
that belongs where decisions are testable.

The payoff is not tidiness. It is that every decision moved across that line
stops being a thing only Steve's eyes can check and starts being a thing the
interpreter can run — and, once it runs, a thing the four other arms can
disagree about. Safari already prints scene checksums. A shading recipe living
in Codex is inside that checksum. The same recipe living in JavaScript is not
inside anything.

Some of it should stay. The one-pixel grass overlap exists because a specific
rasteriser produces a specific seam; that is a fact about canvas, not about the
world, and it belongs next to the canvas. Knowing which is which is most of the
work, and it is why the first step is not porting anything — it is drawing the
line inside the JavaScript and seeing what falls on each side.

## The thing I want to remember

We had five green oracles and a broken `and`, and the reason is that five
oracles of one kind are one oracle. The interpreter was not a better test than
the rung truths. It was a *different* one, and different was the whole value.

I would rather have two kinds of check at 60% each than one kind at 100%.
