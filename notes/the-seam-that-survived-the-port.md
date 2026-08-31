# The seam that survived the port

*2026-08-31, written the same afternoon the wasm plug learned to let a chapter
say what it exports — and immediately revealed that the optimiser eats
exported functions.*

Steve, thinking out loud: the safari driving game ran as zig compiled to wasm
with a hand-written JS blitter, long before Cobblestone. The same game also
compiles to a Windows screensaver and a Linux executable. And **the JS seam
mapped almost verbatim to the seams the two native ports needed.** So a hybrid
is not a compromise — it is two tools doing what each is best at, wasm for the
heavy lifting, JS for the skeleton and the mostly generic display layer. There
is a JS plug sitting there untested if we ever wanted the whole thing in
Codex.

I want to take the middle observation seriously, because I think it is doing
more work than it is being given credit for.

---

## A seam that survives three ports is not a seam, it is a boundary

The blitter interface *looks* like a web accommodation. It exists because wasm
cannot touch the DOM: you compute pixels in linear memory and something else
puts them on a canvas. That is a constraint, and constraints produce
accommodations, and accommodations are usually ugly and local.

Except this one wasn't local. The same line — *here is what the program
computed, now paint it* — is what Windows wanted and what Linux wanted. Three
platforms, three completely different things on the far side (a canvas, a
screensaver host, a framebuffer), and the near side did not move.

That is the signature of a real architectural boundary rather than a
workaround. And it was **discovered by a constraint rather than designed**,
which is worth noticing on its own, because that is one of the more reliable
ways architecture actually gets found. Nobody sat down and decided the game
should separate simulation from presentation at exactly that line. wasm's
inability to draw forced a line, and the line turned out to be the one that
was always there.

The generalisation I would offer: **a restriction that survives being lifted
was never a restriction.** When you port to a platform without the limitation
and keep the shape anyway, the shape was load-bearing.

## What that implies about "100% Codex"

The JS plug is available, untested, and would let the whole thing be Codex.
I think that would make the demo purer and slightly worse, and it is worth
being precise about why, because "purity is bad" is a lazy answer.

**The JS layer is where platform variance lives.** Canvas versus screensaver
host versus framebuffer; device pixel ratio; when you get a frame callback and
what happens when the tab is backgrounded. That is exactly the material a
language selling determinism and portability should *not* be absorbing. A
Codex chapter that has to know about `requestAnimationFrame` has taken on a
liability in exchange for a bullet point.

**And generated JS is worse than written JS at the one job that layer has**,
which is being read and adjusted by whoever is debugging the page. The blitter
is thirty lines that somebody will step through in devtools at some point.
Generated code is not where you want to be standing when that happens.

But I do not think that means the JS plug is pointless, and I would resist
framing it as "the thing we would use if we wanted to be pure." That framing
makes it a purity tool, and purity tools get built and then not used. **A more
interesting use is as a readable target** — the same role the Codex emitter
plays. JS you can paste into a page, a REPL, a sandbox, a notebook, a CDN
snippet, an environment that takes a script tag and not a wasm fetch. That is
a distribution story rather than a purity story, and distribution is the thing
the project actually lacks.

Those are different products and I would not let the second one justify itself
by being the first.

## The part I think is undersold

Here is what struck me, connecting this to today's work.

Every single thing that was painful this afternoon was the seam.

The wasm plug decided a module's exports by testing each definition name
against a hardcoded 484-name list drawn from unrelated applications. A program
that wanted to export `my-entry` could not say so. That is not a wasm defect;
it is what happens when a toolchain has no vocabulary for *the program has an
outside*.

I fixed it — a chapter can now declare `wasm-exports = ["greet"]` — and
immediately found the next layer of the same thing. A declared export gets
deleted by the pruner, because a function called only from JavaScript has no
callers inside the chapter, and "no callers" is precisely what dead-code
elimination removes. Root it, and you hit the layer below *that*: a function
with exactly one internal caller gets folded into that caller by the
single-caller inline pass, before pruning ever runs, and no root can reach
back past it.

**The compiler's model of a program is a closed one.** There is an entry
point, and everything live is reachable from it. That model is correct for a
kernel and correct for a command-line tool, and it is *wrong* for a hybrid —
where the defining property is that the program has functions whose only
callers are outside the compilation unit entirely.

So "hybrid" is not a deployment style. It is a statement about the boundary of
the compilation unit, and the toolchain currently has one blunt way to express
it: a list of root names, hardcoded in whichever driver happens to be running.
That is the 484-name allowlist's actual sin, and it is the same sin as the
roots list in `opening.codex`. Both are "which names does the outside world
know about", written down somewhere that is not the program.

And the Windows/Linux observation is what makes this more than a wasm
complaint. **If the seam is the same on three targets, the vocabulary for it
belongs in the language, not in a plug.** A native build needs to know which
functions are exported from the shared object. A screensaver host needs to
know the entry symbols. The wasm module needs an export section. Three
targets, one concept, currently expressed three ways and none of them in
Codex.

`wasm-exports` as a magic definition name that one emitter reads is a
perfectly good afternoon's fix and I would not pretend it is more than that.
The thing it is standing in for is a language-level notion of *external
surface* — and the argument for that notion is not the browser. It is that the
same list is needed by every target that is not a closed kernel.

## Where I would push back on the framing

"Two tools each doing what they're best at" is comfortable and mostly right,
and it hides one real cost: **the seam is where the type system stops.**
Everything crossing it is untyped, unchecked and versioned by hand. Get the
argument order wrong in the blitter call and you find out by looking at a
wrong picture.

The honest counter is that this is true on native too — the C ABI is not
typed either, and the Windows and Linux ports pay exactly the same price. Which
is, I think, an argument *for* Steve's position rather than against it: the
seam is not a web tax. It is the price of having an outside at all, and you
pay it once per boundary regardless of what is on the far side. It is only a
web problem if you imagined native was getting it for free.

The place where I would want more caution is versioning. A hand-written JS
blitter and a hand-written Codex chapter drift, and today's export mechanism
makes that drift *silent in the worst direction*: the module simply does not
have the function, and the page fails at a property access. That is why the
first thing I did after making exports declarable was make a declared name
that matches no surviving definition emit a comment into the module. It is not
a fix. It is the difference between "you spelled it wrong", "the optimiser ate
it", and "you never wrote it", which are three different afternoons.

## What I actually think, in one paragraph

The hybrid is right and the reason it is right is stronger than versatility.
The seam between compute and presentation is a real boundary — proven by the
fact that it survived two ports to platforms with none of the constraints that
produced it. What is missing is not a way to avoid the seam; it is a way to
*declare* it, in the language, once, for every target. Today that concept
exists as a 484-name list in an emitter, a roots list in a driver, and now a
magic definition name in a chapter. Those are three encodings of "here is what
the outside can call," and the fact that a hybrid feels slightly unnatural is
not because hybrids are unnatural — it is because the toolchain has no word
for the thing every hybrid needs to say.

## Loose thread

The one that nags: if the compiler's model is closed, then dead-code
elimination and inlining are *correct* under that model and the bug is the
model, not the passes. Which means the fix is not "teach the inliner about
exports" — it is that the export declaration should be part of the input to
the pipeline, the way the entry point is. I do not know whether that is a
half-day or a month in this codebase, and I notice that the cheap version
(root them in the driver) fixes the common case completely and leaves exactly
one shape broken: a function called once internally *and* exported. That is a
narrow enough gap to live with for a while, and narrow gaps you can name are
much better than wide ones you cannot.
