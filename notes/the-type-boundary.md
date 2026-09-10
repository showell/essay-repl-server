# The type boundary is where the quality lives

Stepping back from a day of specific fixes to the shape of the system they were
fixing. The claim: the Codex system's quality frontier is its **type system's
completeness**, that completeness is measured almost nowhere except at the
**zig boundary**, and the lever on all of it is the **Rust compiler** we
control outright. Everything we did today was a special case of one principle —
carry earned knowledge forward — and it is worth saying why that principle,
and not a dozen others, is the one that keeps mattering.

## Two kinds of consumer

An AST, and the IR it lowers to, gets consumed by two kinds of backend, and
they ask opposite things of the types.

**Type-erasing consumers.** The Rust interpreter is a tree walker; the wasm
plug boxes. Neither needs a type to be concrete at the point of use — a value
carries its own tag at runtime, or the walk simply does the arithmetic the node
names. An empty list of unknown element type runs fine; a generic function runs
fine unspecialized. These backends are correct as long as the **shape** is
correct, which is to say as long as lex, parse, and desugar produced the right
tree. And they have been battle-tested on an enormous corpus — the Codex
compiler compiling itself, the safari application — precisely because that is a
large test of *shape* and only a shallow test of *types*.

**The type-demanding consumer.** Zig is statically typed with no runtime type
information and no default boxing: in a zig program the type *is* the
representation. So the zig plug cannot emit a list without a concrete element
type, cannot emit a value whose type is still a free variable, cannot leave a
generic unresolved unless it is a real, bound generic it can hand to zig's
comptime. Every place the frontend left a type under-specified, zig refuses.

This is the whole reason the six Roc findings surfaced as *build* failures and
never as wrong answers. The interpreter and the wasm plug ran all six correctly.
The programs were not wrong; the types were merely incomplete, and only the
strict backend could tell.

## Why this is the frontier, and not something else

Codex is a conventional language. Records, sums, lambdas, a Hindley-Milner-shaped
type system with variables and unification and generics, and an effect row on
top. It breaks no new ground against Roc, Elm, or Rust. That is a gift twice
over. First, it means the front half — lex, parse, desugar — is solved work;
get it right once and a straightforward tree walker consumes it, which we have
proven. Second, it means we already know what *correct* looks like at every
hard step, because those languages' compilers show it: how an ambiguous
monomorphic type is defaulted, how an empty literal gets its element, how a
generic is either kept as a real parameter or specialized away. There is no
research here, only carry-through.

So the depth is not spread evenly across the compiler. The front is shallow and
done. The depth is concentrated in **the checker and the lowering it feeds** —
the layers whose job is to *earn* type knowledge by inference and then *file*
it so every downstream layer gets a concrete answer. That is the frontier, and
the zig plug is the instrument that measures how far along it we are.

## Carry earned knowledge forward, precisely

Steve's standing note — is a deep layer re-deriving what an earlier one knew? —
is the same statement seen from the other side. The checker EARNS a type: by
unifying an operator's operands, by solving an empty list's element from its
context, by instantiating a call. The only question that ever matters is whether
it FILES what it earned — records it under a span, resolves the variable, writes
the concrete type into the node — so that lowering and the plug read an answer
rather than a hole.

Today's three fixes were the same defect three times:

- The binary operators answered a result type but never unified their operands,
  so a type the checker could have known stayed a variable.
- An empty list's element was solved-but-unfiled, or unconstrained-but-not-
  defaulted, so it reached a plug as a hole.
- A comprehension's lambda had a type the checker held but had not filed under
  the lambda's span, so lowering could not find it.

In each case the honest fix was at the layer that owned the knowledge — the
checker — and in each case that fix was also the *simpler* one, because it did
the work once instead of leaving every downstream consumer to cope with its
absence. A patch in lowering, or a special case in the plug, is the shape of
re-deriving what an earlier layer should have carried; it is more code and it is
wrong at the edges.

## The Rust compiler is the lever, and the oracle can invert

We control the Rust compiler completely, and it is independent of upstream's
front end — which is exactly what the ladder's two arms were not, and exactly
why the ladder could not see a defect above the IR. Independence is what lets it
disagree, and a conventional language is what makes an independent front end
tractable to build in the first place.

That independence buys something we only started using today. For *values*, the
oracle is external and fixed: the expected output, Roc's own answers. For
*types* — the IR — the oracle has been codexir, upstream's front end. But the
moment our checker resolves something upstream leaves open, the relationship
inverts: **our IR becomes the reference for correct typing, and upstream's is
the thing that is behind.** `alias-empty` is the first case — our IR now spells
a concrete element where codexir still spells a hole. Fed to the zig plug, our
type-complete IR compiles where upstream's does not.

That is the whole strategy in one sentence: make the Rust checker carry every
type forward, and it becomes the gold standard for fully-typed Codex IR — the
thing that grades upstream's front end, program by program, and turns each
divergence into a front-end fix to send. The zig plug is the total check that
keeps us honest about "fully typed," because it is the one client that will not
let a hole pass.

## Reflection

The interpreter's tolerance got us far and hid the frontier at the same time. It
let us prove the compiler and the app over a huge corpus without a complete type
system — real coverage, but of shape, not of types — and a green interpreter
run says nothing about whether a single type was actually resolved. The zig plug
and the interpreter measure orthogonal things, and you need both: one asks *does
it compute the right value*, the other asks *is it fully typed*. The Roc corpus
mattered not because it was large but because it aimed at the type system's
corners — aliasing, closures, folds, empty containers — the places the big
corpus never pressed.

The pleasing part is how little of this is exotic. There is no clever trick
waiting to be discovered, only a discipline to be applied at one layer: earn the
type, file the type, and let a strict backend tell you when you didn't. The work
ahead is in the checker, the test is the zig plug, and the reference is a Rust
compiler that finishes what the front end started.
