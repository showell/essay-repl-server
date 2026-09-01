# What we own outright

*2026-09-01*

Two things happened today and they were not the same kind of thing, which is
why it is worth writing them down together.

In the morning `web/blitter.js` was still deciding what the screensaver looks
like. Not painting it — *deciding* it. A shading recipe, four visibility
thresholds, numbers chosen by eye, sitting in the one file in the whole project
that nothing could run. Everything else the game does is inside a checksum
somewhere; those were inside nothing at all. By evening they were Codex,
graded, and the browser was handed two colours and a span and told to fill a
polygon.

In the morning there was no Rust interpreter. By evening it ran twenty-five of
the twenty-seven safari units and printed, byte for byte, what the zig arm
prints.

## The interpreter, in numbers

Six of the smaller checks, measured tonight:

| unit    | steps      | seconds | steps/sec |
|---------|-----------:|--------:|----------:|
| pond    |      3,824 |   0.001 | 7,178,147 |
| num     |     21,236 |   0.002 | 9,109,823 |
| camera  |     97,845 |   0.009 | 11,264,378 |
| blit    |    149,984 |   0.023 | 6,621,598 |
| critter |  5,364,771 |   0.746 | 7,191,197 |
| world   | 10,425,320 |   1.610 | 6,474,627 |

The interesting column is the last one. It barely moves. Across programs
spanning four orders of magnitude of work — 3,824 steps to 10.4 million — the
machine holds somewhere around seven million steps a second. Nothing degrades.
There is no quadratic hiding in there; if a list append were copying its left
side on every iteration, `world` would not be running at the same rate as
`pond`.

That is worth knowing because it says what tomorrow's problem is *not*. The two
slow checks — `render` and `ride`, 2.54 and 1.29 seconds through Debug-built
zig, minutes through this — are not slow because the interpreter falls over on
big programs. They are slow because a step costs about 140 nanoseconds and they
take an enormous number of steps.

Which leaves exactly one measurement I do not have and should have taken first:
how many. `world` is 10.4 million steps for zig's 0.07 seconds. `render`'s zig
side is thirty-six times heavier than `world`'s, so a naive scaling puts it near
375 million steps and just under a minute — and it took longer than that. Either
the ratio is worse than linear in the zig time, or the rate does drop somewhere
in there. One `codexrun bench render-unit.codex` settles it, and the answer
picks the fix: fewer steps, or cheaper steps. Those are different projects.

My honest guess is cheaper steps, and the suspect is unglamorous. A variable
reference walks a chain of scopes doing a linear scan of each. There is a
`scope.rs` in the repo already; resolving names to slot indices ahead of time is
the oldest trick in the book and it is exactly the trick this shape of
interpreter is built to receive.

## Why this arm is worth more than its speed

Before today the Rust front end had five green oracles and every one of them
compared a *structure* we built to a *structure* Cobblestone built. Lex, parse,
desugar, scope, the IR chapter preamble. All green. And `and` did not
short-circuit, and nothing noticed, because none of those oracles can see what a
program *does*.

The interpreter is the first thing here that sees meaning. And it shares nothing
with the other arms below the raw text — no types, no IR, no zig, no guest — so
when it disagrees, the disagreement is attributable to something.

It disagreed once today, on purpose. `literal_main` is the repro for a finding
we already sent: Cobblestone accumulates a Real literal's digits into a wrapping
i64, so nineteen digits arrive as a different and usually negative number,
silently. We read it as an f64 and get it right. The two arms print different
things and the script *fails if they ever agree*, because a second independent
front end declining to reproduce a bug is not an inconvenience — it is the
evidence.

That is a template, and I think it has been under-used. `codexrun sweep` sits at
551 of 979 corpus programs printing exactly the right thing. That list of 428
disagreements has only ever been read as our to-do list. Some of it is. Some of
it is not, and the only way to find out is to ask, for each one, *which side is
wrong* — instead of assuming.

## Directions I do not think we have talked about

**Make `codexrun` safari's inner loop, not just its fourth arm.** The judge
sweep costs about ninety seconds cold through zig and a compile per module. The
interpreter runs the light checks in single-digit milliseconds with no compile
at all. If writing a new Codex check went from "bundle, transpile, build, run"
to "run", the cost of *writing Codex* drops by an order of magnitude — and the
cost of writing Codex is the actual bottleneck on "mostly Codex-based". The zig
path stays the graded answer. The interpreter becomes the thing you hit while
you are still thinking.

**A speed target for the interpreter, stated so it can be falsified.** The
compiler has one: 1,705 programs in under sixty seconds. The interpreter has
none. I would propose *all twenty-seven safari units in under ten seconds*.
Today that is minutes. It is a good target because it is a real workload rather
than a microbenchmark, and because failing it is informative.

**A second show that actually exists.** `harness/second_show.js` builds a night
walk through a city and proves the renderer does not know it is drawing a
motorcycle. It is a test fixture. Making it a real page would be the first thing
this project ships that angry-gopher does not have — and here is the part I find
genuinely interesting: its guest does not have to be a port. safari-codex's
Codex is a translation of somebody's zig, and it inherited that zig's shape. A
show written natively in Codex, with the interpreter as its inner loop, would
tell us something a port cannot: what this language is like to *write in*, on a
problem where nobody has already decided the structure. It would also exercise
our front end on a distribution of Codex that was not written by Cobblestone's
own authors, which is a corner of the language the checkout does not cover.

**Send a suite, not just findings.** We have been throwing bugs over the wall,
and that is the right thing to do with bugs. But we now hold twenty-seven
programs with expected outputs that four independent implementations agree on —
zig native, bare metal, wasm, and now a Rust interpreter. That is a conformance
suite. There are something like fifty plugs in Damian's tree, and a plug author
today has no way to check their work beyond the compiler's own tests. A suite
scales with the size of their fleet; a bug report scales with the size of our
attention. I do not know whether they would want it. I think it is worth asking.

**And a question about the rungs.** The plan has been the ladder's six: lex,
parse, desugar, scope, check, lower. That is a plan for building a compiler, and
it is a good one. But today we accidentally shipped a second product. An
interpreter does not need the type checker — it proved that by running safari —
and its critical path through the remaining work is much shorter than the
compiler's. We should decide *which product we are finishing first* rather than
treating the rungs as a single ladder where the only direction is up. They are
not the same climb.

## The divergence

The safari app started diverging from angry-gopher today, in its internals, and
that is fine. The wire carries a tag angry-gopher has never heard of. The
browser half has lost a section it used to own. The two programs still paint the
same picture, and there is a harness that runs both and insists on it, but the
insides are ours now in a way they were not this morning.

I suspect that matters more than it looks. Every other thing on this box is
someone else's: the language is Damian's, the plugs are Damian's, the game was
angry-gopher's. We are careful with all of it for good reasons. The safari app
is the one artifact where the answer to "can we change this?" is just yes — and
it turns out that when the answer is yes, you find out things about the design
that being careful never shows you. The blitter was holding decisions for two
years and nobody could tell, because nobody was allowed to move them.
