# Four layers down, and the two that are left

A day in, the Rust front end reads Codex. Not "parses most of it" — reads it.
Four of the compiler's six front-end layers now reproduce Cobblestone's own
rung truths byte for byte, and the chapter header of every IR file we have a
gold for comes out identical: 1,012 corpus programs, all 27 safari units, and
the compiler itself.

That last one is worth pausing on. `codexzig-subject.codex` is the Codex
compiler plus the zig emitter plus a harness, bundled into one 2.98 MB file,
and the transpiler repo ships its IR beside it. We hand our Rust front end that
file and get its 310-line chapter header back byte-identical in 0.9 seconds.
The whole checkout parses at about 40 MB/s, against roughly 150 KB/s for
`codexir`.

So the front end is fast and it is faithful. What I want to write down is what
that does **not** yet mean, and what I think we should do about it — because
the honest version of "four layers down" is closer to "one and a half".

## What is actually checked

The chapter header is everything in an IR file above the definitions:
sections, constructors, type definitions, effect operations. It is fixed by
syntax alone, which is exactly why we can check it now. It is also **7.7% of
the corpus IR by bytes, and 0.5% of safari's**.

The other 99.5% is the definitions, and each node in there carries a type the
compiler inferred. To reach it you need the type checker. So today, *every
expression body in every program we have* is validated by nothing except 65
unit tests I wrote by reading Cobblestone's source. That is a real number and
it is small.

The rung truths do not help here either. They are one subject each, at the
declaration layer. `desugar.truth` would pass a desugarer that answered
"error" to every expression it met — which is exactly why I built a
whole-corpus counter beside it, and why that counter immediately found a bug
worth 1,410 unresolved names.

That pairing is the pattern that has been working all day, and I would make it
the standing rule: **the rung truth proves the pass runs; a corpus sweep proves
it does not misfire.** Neither alone is worth much. Together they have caught
every real defect this project has had.

## The shape of what's left, and the risk in it

Your instinct that the last couple of layers carry most of the complexity is
right. The remaining two are the type checker and the lowering to IR, and the
checker is the single largest thing in the project — Hindley-Milner-style
unification, with the numbering of type variables visible in the output.

The risk is not that they are hard. It is that **the oracle only switches on at
the end of both.** Today's rhythm has been: build a piece, measure it against
1,012 programs, fix what the measurement says. If I start the checker now, that
rhythm stops for as long as it takes to finish the checker *and* the lowering,
because nothing in between produces anything a gold can be compared to. That is
the longest dark stretch this project would have had, at the point where the
work is hardest.

I would rather not walk into it. So: what else do we have?

## Four assets we have not spent

**1. Safari has expected output.** It is a program that runs and prints things,
with `.expected` files beside it, and four independent arms that already
disagree usefully. Nothing about that requires our type checker. If our front
end can *evaluate* the AST — a plain tree-walking interpreter, no types at all
— we can run safari's samples and diff the output. That is a semantic oracle,
and it tests the thing that actually matters: does this program mean the same
thing? An interpreter over the AST is a fraction of the work of check plus
lower, and it validates desugaring far more sharply than any structural
comparison, because a wrong precedence or a swapped `|>` shows up as a wrong
number on the screen.

**2. The refusals are a checker oracle that costs nothing.** The gold bank has
222 programs the compiler *declines*, with the diagnostic each one produced. A
type checker that accepts them is wrong, and we learn that without reproducing
a single type. That grades the checker's judgement directly, separately from
its bookkeeping.

**3. The IR's shape survives type erasure.** Every definition in a gold IR is a
tree with a type stapled to each node. Strip the types and what remains is the
*shape* the desugarer and lowerer produced — application nesting, match arms,
let chains. We already have a canonicaliser for the IR (it exists to renumber
type variables), so a type-erasing variant is a small extension. If a
shape-only lowering can emit that, we would validate expression structure
across 1,012 programs **before** writing the checker, and the checker would
then have one job instead of two. I want to spike this rather than promise it:
lowering may make decisions that need types, and I do not yet know how many.

**4. The compiler is its own hardest test.** 2.98 MB, every construct in the
language, and we already have its IR. Anything we build can be pointed at it on
day one. It has caught two defects today that the corpus did not.

## Not being constrained by their decisions

You have already ruled that byte-identical IR is a ratchet and not the gate.
I think we should push that further and be explicit about what "works like
Codex in the ways that matter" means, because it is a much smaller target than
"reproduces Codex":

- **Accepts and rejects the same programs.** This we can check cheaply and
  completely.
- **Gives the same types.** Checkable from the golds, with the variable
  numbering canonicalised away.
- **Produces programs that behave the same.** Checkable by running safari.

And a list of things we do **not** owe them: their type-variable numbering,
their error message wording, their reachability pruning of the definition list,
their internal data structures, or their allocation strategy. Several of those
are compromises made for a compiler that has no garbage collector and runs on
bare metal. We have neither constraint. Copying them costs us speed and buys
nothing.

There is a bigger version of this. If the goal is compile speed and linting,
the valuable artifact is a front end that *understands* Codex — parses, checks,
and can answer questions about a program. Emitting Cobblestone's exact IR text
is a separate deliverable, and possibly an optional one. Worth deciding
deliberately rather than by momentum, because it changes what "done" means.

## What I would do next

Today, in order:

1. **Close the last 56 unresolved names** and finish the desugarer's synthesis
   passes. Small, and it makes everything after it trustworthy.
2. **Spike the type-erased IR comparison** — an afternoon, not a day. If it
   works, expression shape gets an oracle over 1,012 programs and the checker's
   job halves. If it does not, we learn exactly which decisions need types,
   which is worth knowing before writing the checker anyway.
3. **Then the AST interpreter, aimed at safari.** Not because we need an
   interpreter, but because it is the cheapest path to "this program still
   prints the right thing", and safari is the program we most want that
   guarantee for.

The checker comes after those, with its judgement already gradeable against the
222 refusals and its bookkeeping the only genuinely new work.

For the long term, three things that would keep this maintainable:

- **One command that runs every gate.** There are now six and I run them by
  hand. That is exactly how a gate goes quietly red — and one of mine did today
  for a full commit before I noticed, which is why the pass criteria are now
  narrowed to things that must be true *now*, with everything else reported as
  inventory beside them.
- **Keep the derived tables derived.** The character alphabet and the 263
  built-in names are both read out of the compiler by a ladder script and
  committed as generated tables. Anything else that is really the compiler's
  data should arrive the same way, never typed in.
- **Keep the two-part discipline.** Rung truth for presence, corpus sweep for
  correctness, and never let a number that cannot be zero yet sit inside the
  pass criteria.

## The short version

The front end reads the whole language and does it fast. What it cannot yet do
is tell you whether it *understood* any expression, and the cheapest ways to
find that out are not the next layer of the compiler — they are safari's
expected output, the 222 refusals, and the shape hiding under the IR's types.
Three oracles we already own and have not spent.
