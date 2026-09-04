# The Rust Codex compiler: where it stands, and what it is actually for

2026-09-04, written at the end of a long night.

## The facts first

`fib` is byte-identical through six layers — lex, parse, desugar, scope, check,
lower — against upstream's own rung truths for its own rung subject. One
command says so:

    ./slice.sh slice/Fib.codex .../lower.truth
    SLICE GREEN: Fib.codex is byte-identical through lower

The interpreter runs safari's committed units at **17.2 million steps per
second** — 160 million steps in 9.3 seconds, the largest single unit
(`drive_main`) 115 million steps in 6.7.

The IR text emitter reaches 8 of 1,012 golds byte-identical and is parked
deliberately.

Everything below is opinion built on those three numbers.

## What this thing is for, in the order I would defend

Steve named five uses: linting, quick arms, code exploration, refactoring, and
the interpreter. I would rank them by how much of the value is already banked
versus still speculative.

**Code exploration is already the biggest win and nobody planned it that way.**
`cohesion`, `xref`, `seams` and the collapse exist because the parser reads the
whole checkout at 25 MB/s with zero errors. That capability paid for itself
within days: the four-way ZigEmitter split was cut by `cohesion --blocks`
against the parser's own tree, not by splitting on blank lines, and the plan
files are now committed so the next Update re-cuts in one loop. `xref arity`
found that `check-chapter` had drifted from five parameters to nine at Update 54
and that nobody had noticed for two Updates. That is not a compiler feature. It
is a *reading* feature, and it is worth more per hour invested than anything
else in the repository.

**Refactoring is the one where the parser is not a convenience but a safety
property**, and I had underrated it until tonight. In a literate language,
*prose belongs to a definition*. A blank-line splitter or a regex does not know
that, so it silently reattaches a paragraph to the wrong function — and the
result compiles, which is the worst possible failure mode for a refactor.
`cohesion --blocks` hands out byte ranges from the parser's own tree, so a
definition leaves with the paragraph written above it and a `Section:` header is
never dragged along behind the definition that precedes it.

The evidence is concrete. `ZigEmitter.codex` was ~4,500 lines and one chapter;
it is now four pages of that same chapter, 421 definitions in and 421 out, zero
names defined twice. It was re-cut against Update 55 rather than rebased,
because U55 edited the very section that moves — and re-cutting takes their text
as given and never merges. Four definitions nothing reads were removed the same
way, by block range, after being re-verified dead against the new Update rather
than on faith.

Two things make this more than a one-off. `extract_chapter.py` **refuses**
unless every planned name exists exactly once in the source, so an upstream
rename announces itself instead of silently dropping a definition. And the plan
files are committed, so the next Update is one loop and a pagination rather than
an hour of reconstruction — which is what it cost this time, because the first
split's plans were never saved.

The next target is `opening.codex`: 31 definitions, zero outbound edges, four
entry points. The collapse algorithm — absorb every single-caller definition
into its caller to a fixed point, and rank survivors by LINES rather than by
count — is what finds those, and it finds them in a way reading cannot. I would
put refactoring second only to exploration in banked value, and I would say the
two are really one capability: *the parser lets you see the shape, and then it
lets you change it without breaking the prose.*

**Linting is the same capability wearing a hat, and it compounds.** Three
checks now run in seconds before any guest: arity, bundle completeness, page
consistency. Each exists because the expensive version happened first — a rung
died an hour in, a bundle went to a guest missing three chapters, a wall of
CDX3002. The economics here are brutal in our favour: a QEMU guest costs
minutes, a parse costs milliseconds, and *most* of what kills a run is visible
in the text. I would keep pushing here even at the expense of the compiler
proper.

**Quick arms are the least proven and I am least sure about them.** The idea is
that a fast native front end lets us answer questions the ladder currently
answers with a guest. It is plausible and partly demonstrated, but every
concrete instance so far turned out to need something only bare metal has.
I would let this one emerge rather than aim at it.

**The interpreter is the one with a real ceiling, and it is worth talking about
properly.**

## The interpreter: 17 million steps a second, and why that is not enough

The insight that mattered a few days ago was that the *earlier layers are
enough to run Codex*. You do not need types, you do not need IR, you do not
need a backend. Lex, parse, desugar and a tree-walk get you a working Codex,
and that is why safari's units run at all. That remains the highest-leverage
observation in this project, because it decouples "run Codex" from "compile
Codex" — two goals that look like one and are not.

But 17M steps/sec is a tree-walker's number, and the honest read is that we are
leaving a factor of several on the floor. Steve asked whether type information
could speed it up. My answer is: **a little, and much less than the thing we
already have and are not using.**

Here is the hot path today:

```rust
fn get(&self, n: &str) -> Option<Value> {
    // ... walk a linked chain of scopes ...
    if let Some(i) = names.iter().rposition(|k| k == n) { ... }
    // ... else recurse into parent ...
}
```

Every variable reference is a **string comparison scan** up a chain of frames.
In a loop that touches `n` a hundred million times, that is a hundred million
string compares and pointer chases, and it is almost certainly where the time
goes. Types do not fix this. **Scope resolution does** — and scope is rung four,
it is already green, and its whole job is knowing which binding a name refers
to. Turning a `NameRef` into a `(depth, index)` pair at load time converts the
hot path from a search into two dereferences.

That is my strongest opinion in this essay: *the interpreter's speed problem is
a name-lookup problem, not a type problem, and the fix is a layer we already
built and are not consuming.*

Types would help second-order things. `add-int` versus `add-num` is currently
decided by inspecting the runtime value on every execution; with checked types
it is decided once. Allocation is the other half — an earlier round found 40% of
runtime in malloc and a 1.93x win from fixing it, which suggests value
representation still matters more than arithmetic dispatch. My guess at the
ordering, stated so it can be proven wrong: **scope indices first, value
representation second, type-directed dispatch third.** I would be unsurprised
if scope indices alone were worth 2x and types were worth 15%.

There is also a design question hiding here that I do not think we have faced.
A tree-walker that consumes resolved scope and checked types is no longer
really a tree-walker; it is a compiler to closures, and at that point the
question "should this emit bytecode" becomes live. I do not think we should do
that yet. But I think we should stop calling it "the interpreter" as though its
shape were settled.

## The IR line is a different project with different economics

Everything IR-shaped — `ir.rs`, the gold comparison, the pipeline, the emitter
— is in service of **zig**, and it should be judged that way. It is not needed
to interpret Codex and it is not needed to lint or explore it.

That matters because the IR line has a much worse cost curve. Two ceilings are
already visible and neither is a matter of effort:

- **The golds are post-pipeline.** `type-checker-test` differs from its gold
  because the gold inlined `apply-twice` away — `fold-constants`,
  `inline-leaf-calls`, `inline-single-caller`. Matching golds in general means
  implementing three optimisation passes whose only purpose is to reproduce
  someone else's optimiser.
- **Effect rows carry unification row ids.** 420 of 1,012 corpus units want one,
  and the gold spelling — `(row (labels (label "Console.Write" "")) "" 6)` —
  contains a number that no amount of syntax will produce.

Neither is a reason to stop. Both are reasons to be honest that "byte-identical
IR for the corpus" is a much larger project than "a Rust Codex front end", and
to stop treating gold count as the project's scoreboard. Eight is not a
disappointing number; it is a number measuring the wrong thing.

## What I would do about the checker, having just built some of it

The checker was worth building for a reason I did not expect. Matching
`next-id 8` sounded like conformance theatre — Steve pushed back on exactly
that, and he was right to. But chasing it surfaced four structural facts that a
reasonable implementation gets wrong and that no amount of "the types look
right" would have caught:

- `empty-unification-state` is not empty: it starts at `next-id = 2` with two
  substitution slots.
- `substitutions` is a slot array indexed by variable id, not a list of pairs.
- A definition's parameters come from its declared arrow and mint nothing;
  `bind-lambda-params` mints, but it is for lambdas.
- `expr-types` counts name references, not nodes.

My own attempt had two of these wrong in a way that *cancelled* — I started the
counter at 0 and minted two extra, so the total matched while every variable id
was shifted by two. Those ids are printed into the IR as `(tvar 41)`. A number
that is right for the wrong reason is worse than a number that is wrong, and
the only thing that caught it was insisting the number be right for the right
reason.

So: type variable ids are observable, allocation order is load-bearing, and the
counters are worth matching. But `substitutions` and `expr-types` were never
targets — they fell out of doing the right thing, which is what a good invariant
does.

## The finish line, and what I actually think the path is

I do not think "a Rust compiler that matches Codex byte for byte on the whole
corpus" is the right finish line. It is a finish line for the *IR* work, and
that work is in service of zig, and zig already has a working path.

Here is what I would aim at instead, in order:

**1. Make the interpreter fast enough to be the default way we run Codex.**
Scope indices, then value representation. If safari's units drop from 9.3
seconds to 3, the interpreter stops being a curiosity and becomes the thing you
reach for. That changes what is cheap, and changing what is cheap is how this
project has made every one of its real gains.

**1b. Keep refactoring on the parser, and keep the plans.** The ZigEmitter
split re-cut cleanly against a new Update because the tooling reads the tree
rather than the text. `opening.codex` is next. This is cheap, it is safe in a
way hand-editing is not, and every split makes the next Update's diff smaller.

**2. Keep the linter ahead of the Updates.** Every Update so far has needed
harness changes, and five of the last seven moved a signature we call. The
linters cost seconds and have already caught a two-Update-old drift. This is
pure compounding return.

**3. Take the checker as far as safari needs and no further.** Safari is the
second program that matters, and it is a far better target than the corpus
because it is *real* and *ours*. The corpus rewards breadth; safari rewards
depth, and depth is what the compiler and safari both need.

**4. Let the IR work be opportunistic.** Emit what the checker makes free.
Do not implement the pipeline to chase gold counts. Revisit if and when the
zig path actually needs a second implementation.

The thing I would most like to be talked out of is (1) — it is the item I am
most confident about and least able to prove, because I have measured *where*
the time goes only by reading the code, not by profiling it. That is the first
experiment I would run tomorrow, and it costs about ten minutes.

## One honest note about method

The most useful thing that happened tonight was being told to stop. I built
`lower` before `check`, got eight golds, and generated a refusal histogram whose
top three entries were all the missing layer's output — 480 effect rows, 155
names with no type, 21 empty list literals. It looked like progress and was
mostly scaffolding around a hole. The corpus histogram was a bad compass
precisely because it was quantitative: it rewarded whichever bucket was biggest,
and the biggest buckets were proxies for one thing.

The slice replaced it. One program, every layer, one diff that says which layer
breaks first. It is a smaller measurement and a much better one. I suspect that
generalises further than this project.
