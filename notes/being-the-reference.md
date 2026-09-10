# Being the reference: two oracles, a whetstone, and what we give up

We just decided to be the reference and not the copy. That is the right call,
but it is worth being clear-eyed that it is a TRADE, not a pure win, and that
the Roc tack you are considering is the right driver only if we pair it with the
design work we keep deferring. This is a riff, not a plan.

## What "reference, not copy" frees, and what still binds

Dropping the obligation to reproduce codexir's internals frees exactly one
thing, and it is the thing we want: the **type content of the IR**. We can
resolve a variable codexir leaves open, default an ambiguous monomorphic type,
file a type under a span codexir never recorded — and where that makes our IR
differ, the difference is us being more correct, not a bug.

Three things still bind us, and they are enough:

- **The same source language.** We parse the same `.codex`. Lex/parse/desugar
  stay faithful; that is the shared front we already proved.
- **The same output from the same program.** This is the golden invariant, and
  it is what makes internal boldness SAFE. We can rewrite the type engine
  however we like, as long as every program still produces the same value
  through the interpreter, the wasm plug, and the zig plug. Output-equivalence is
  the refactoring net under a redesign.
- **The plug's contract.** The zig and wasm plugs read a specific IR shape. We
  do not control them; they are the fixed downstream. So we may change the TYPES
  we put in the IR, never the IR's protocol. The plug is the contract, and it is
  a good discipline — it keeps "be the reference" from drifting into "invent our
  own language."

So the freedom is real but bounded: same source, same answers, same wire — and
inside that box, types as good as we can make them.

## What we give up, and what has to replace it

The byte-match to codexir was not just a grading rule; it was a **cheap, total
regression detector**. Self-host at 3,222 of 3,222 means any change that broke
any definition showed instantly, for free. Deciding to diverge means we lose
that for exactly the definitions we improve — and we cannot tell a good
divergence from a regression by the diff any more.

So the safety net has to change shape, from a byte-diff to **behavioral
oracles**:

- **zig answers the type question:** does our IR compile? A hole refuses.
- **Roc's `.expected` (and upstream's) answer the value question:** does it run
  to the right answer?
- **the backends cross-check each other:** interpreter, wasm, and zig should
  agree on output; a disagreement is a bug wherever it is.

There is even a behavioral replacement for the self-host: not "does our IR match
codexir byte for byte" but "does our IR of the compiler, through the plug, build
and run a working compiler." Stronger, because it is end to end — and heavier,
because it is a build, not a diff. That is the price of being the reference: the
regression net gets more expensive and more real at the same time. Worth paying,
worth naming.

And a burden comes with it: **every divergence must be justifiable.** We differ
from codexir only where we can show we are right — our IR compiles through zig,
or runs to the oracle's answer, where codexir's does not. A divergence we cannot
justify is not a reference improvement; it is a bug wearing the same clothes.

## The Roc tack — where it is right, and where it lies to us

Porting Roc's tests, Codex as the source and Roc's answers as the oracle, is a
genuinely good driver, for reasons that are easy to undersell: the oracle is
EXTERNAL and CORRECT (a mature compiler for a nearly identical language), the
tests are DESIGNED to stress the type corners (closures, aliasing, folds,
recursion) rather than the common paths our huge self-host corpus already
covers, and it is cheap and incremental. Every port that fails through the zig
plug hands us a specific, reproducible type gap with a known-right answer.

Here is where it lies to us if we are not careful: **porting more tests is
DISCOVERY, and discovery is the stumbling we just diagnosed.** We could port a
hundred Roc programs, fix a hundred local gaps, and end up with a hundred more
patches and still no zonk-and-default phase, still no explicit bidirectional
check. A bigger whetstone does not sharpen a knife you never decide to grind.

The synthesis is the whole point: use the Roc corpus as the **whetstone**, but
let each lesson land as a **phase**, not a special case. When a port reveals an
unresolved orphan, the fix is not "default this case" — it is "the zonk pass now
defaults every ambiguous monomorphic variable, and here is the port that proves
it." When a port reveals an expected type that should flow down, the fix is not
another `want` argument — it is "the bidirectional `check` mode handles this
shape." The corpus tells us WHAT the engine must do; the engine is where the
answer goes. And competing with Roc means reading Roc — its compiler is open,
its constraint solver and defaulting and monomorphization are exactly the
research you asked whether we were skipping. The antidote to stumbling is to
study the compiler we are using as the bar.

## The two phases this implies

- **Phase one, Roc, codex set aside.** Build the principled type engine —
  infer, then zonk-and-default, with a bidirectional check mode — against two
  external oracles: Roc for values, zig for types. Grow the type-stress corpus.
  The output is that our compiler becomes the REFERENCE for well-typed Codex IR.
- **Phase two, back to codex.** Spend the reference. Grade upstream's front end
  against our IR, program by program, and turn each divergence into a front-end
  PR. This is the inversion, cashed in — and it only works because phase one
  made "our IR" mean "the correct IR," not "our copy of theirs."

## Two oracles, and the discipline they demand

Zig refuses a hole, which is what makes it a type oracle — but zig runs
upstream's plug, which has its own codegen bugs (the discard we fixed today was
one). So a zig failure is ambiguous until attributed: is it OUR type gap (fix
the checker) or the PLUG's codegen (PR upstream)? The Roc corpus already taught
us that triage — three frontend findings, one checker, two plug — and it is the
discipline that keeps "zig as oracle" honest. Two oracles, and the standing
question at every red: which layer moved.

## Reflection

The quiet upgrade here is epistemic. We are trading one internal oracle that is
sometimes wrong — codexir, whose bugs we spent the day finding — for two
external ones that are not: Roc for meaning, zig for types. That changes the
question we ask ourselves from "do we match upstream" to "are we correct," and
only the second question lets you be a reference at all. The Roc tack is the
right way to keep asking it, provided we answer each instance by improving the
algorithm and not by adding a patch. Go deep on the corpus, yes — but grind the
knife each time, and read the compiler that already got there.
