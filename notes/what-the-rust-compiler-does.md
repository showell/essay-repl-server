# What the Rust compiler actually does, layer by layer — and what it doesn't

A concrete look at the Rust compiler as it stands, so we can see the good
structure we already have, and name the one place we are improvising where we
could be designing. The prompt behind it: I keep invoking Hindley-Milner — are
we actually expressing it, or stumbling toward its known answers one failing
test at a time? The honest answer is the second, and it is worth being precise
about why, and about what the principled version would be.

## The spine: what each layer earns and hands on

The pipeline is `lex -> parse -> desugar -> check -> lower -> lift -> prune ->
emit`, with the interpreter as a separate tree walker. The thing that ties it
together — the currency of the whole system — is the **span**.

**Lexer.** Produces tokens, each carrying a span: a byte offset and length. Not
glamorous, but every later layer's ability to attribute a fact to a node rests
on it.

**Parser.** A CST whose nodes keep their spans. Still shape, no meaning.

**Desugar.** The AST, and the first interesting hand-off. Seven forms are
rewritten — `(a, b)` becomes `MkTup2 a b`, `for x in xs -> b` becomes `map-list
(\x -> b) xs`, and so on — which means the desugarer INVENTS nodes that were in
no source. An invented node has no position, but it still needs an **identity**,
because the checker will want to file a type for it and lowering will want to
find that type. So `synth()` mints a span with line 0 and a monotonic offset:
not a position, an identity. The concrete pay-off is exactly the bugs we fixed:
a comprehension's `map-list` name is given the loop variable's real span so the
checker records one expression type for it; a lambda that had NO span (COMPILER-
30) could not have its solved parameter types found by lowering until it got
one. The span is how the upper layer's knowledge survives to the lower one.

**Check.** Earns types and files them in two places. The **substitution** is a
slot array indexed by variable id — slot `i` holds what variable `i` resolved
to, or itself if unresolved. The **span-keyed tables** (`expr_types`,
`pat_types`) hold the type a node was checked against: `record_expr_type(sp, t)`
files it, `expr_type_at(sp)` reads it back by binary search after one sort at
the check/lower boundary. Polymorphism enters here not by inference but by
reading the DECLARED signature: `parameterize` walks a written type, turns each
lowercase name (`List a`) into a `ForAll`, and `instantiate` mints fresh
variables for it at each use. The empty-list fix files the element type by span;
the binary-operator fix writes operand agreement into the substitution — both
are "earn it, then file it so downstream reads an answer, not a hole."

**Lower.** Re-reads the checker's answers and re-derives nothing: `expr_type_at`
by span, `deep_resolve` to follow the substitution, `type_defs` for a field's
declared type and slot. `empty_list` reads what the checker recorded at the
span, then resolves it. This is the part that is genuinely right — lowering is a
READER, not a second type-inferencer, which is only possible because the checker
filed everything under a key lowering can look up.

**Interpreter.** 3,430 lines that barely mention a type; it runs on shape.
Which is the whole reason a green interpreter run tells you a program computes
the right value and nothing about whether a single type was resolved.

## What kind of type system this actually is

It has Hindley-Milner's MACHINERY — fresh variables, unification, a
substitution, `instantiate`, `ForAll` — but it is not Algorithm W. There is **no
generalization**: `build_undeclared_fun_type` mints fresh variables for an
undeclared definition and stops; it never closes over the free variables of an
inferred type to make it polymorphic. All polymorphism comes from the WRITTEN
signature. That is a legitimate and common choice — a language with explicit
signatures does not need to infer principal types — and it puts us closer to
**bidirectional type checking** than to full HM inference.

And the inference is **unify-as-you-go**: a single walk of the AST that unifies
as it meets each node, not a constraint-collect-then-solve. That is exactly why
ORDER mattered in the `map-list` bug — a variable was unified late, and a node
read earlier kept the stale answer.

## Are we doing HM explicitly, or rediscovering it?

Rediscovering it. We have the machinery, but not the explicit phases, and we
have been building the checker TEST-DRIVEN and BYTE-MATCHED to codexir. Every
recent fix — unify the operands, default the orphan, file the type under a span
— is a LOCAL rediscovery of a standard practice, applied to make one failing
program match the reference, not derived from an algorithm we wrote down. It
works because the known solution is small and we have a reference to match. But
it is stumbling, and two of the things we keep stumbling into are exactly the
phases worth designing on purpose:

1. **A zonk-and-default pass.** "Carry every type forward" should be a
   GUARANTEE, enforced by a final walk of each definition that resolves every
   variable and defaults any that inference left genuinely ambiguous — the
   monomorphic orphan the empty list produced. Today that defaulting is one
   special case I added at the end of the per-definition loop. As a PHASE, it
   turns "no unresolved type reaches lowering" from a thing we hope is true into
   an invariant the compiler enforces, and it is the single change that most
   directly delivers the essay's thesis.

2. **An explicit bidirectional structure.** Several cases are expected-type-
   flows-down: the empty list taking its element from context, a lambda taking
   its parameter type from its callee. We thread an ad-hoc `want`/`expected`
   argument for these. Bidirectional typing — a `check(e, expected)` mode beside
   `infer(e)` — is the named algorithm for precisely this, it fits a signature-
   directed language better than Algorithm W, and making it explicit would
   systematize what we now do by hand and remove some of the order-dependence.

The algorithm we are NOT overlooking but also not committing to is full HM
generalization / constraint-based solving (Elm's solver, GHC's OutsideIn). We
likely do not NEED generalization — signatures give us the polymorphism. But a
collect-constraints-then-solve core would eliminate the order-dependence that
bit `map-list`, at the cost of a bigger rewrite. That is a decision to make
deliberately, not a thing to assume either way.

## The tension, and how it resolves

All of this is held in place today by the byte-match to codexir: the self-host
is 3,222 of 3,222 identical, and that gold is what makes the Rust arm
trustworthy. A principled zonk/default/bidirectional core would produce MORE
resolved IR that DIVERGES from codexir wherever codexir is incomplete — as
`alias-empty` already does. That is not a regression to fear; it is the
inversion. To carry every type forward, the Rust checker has to stop being a
faithful copy of codexir and become the principled thing codexir should match.
The Roc corpus, which aims at the type corners, is the instrument to drive that,
and the zig plug, which refuses a hole, is the judge.

## Reflection

The good news is that the SPINE is right. Spans as the carry-forward key, the
substitution as the store, span-keyed answers filed by the checker and merely
read by lowering, no re-derivation downstream — that is a clean design and it is
why our lowering is small. The gap is not in the spine. It is that the type
ENGINE at the center is a faithful reimplementation grown patch by patch, when
it could be a small, explicit, principled core: infer, then zonk-and-default,
with a bidirectional check mode for the cases where a type flows down. The
research to do is not exotic — it is writing down the two or three phases we are
currently improvising, and deciding, once, to be the reference rather than the
copy.
