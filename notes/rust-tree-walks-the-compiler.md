# Rust tree-walks the compiler

Initial reactions to: bundle Cobblestone's own front end, interpret it with
`codexrun`, and have it compile `fib` to IR.

I spent about fifteen minutes measuring before writing this, because the idea's
merit turns almost entirely on whether the interpreter can get near it at all.
It can get nearer than I expected.

## What I measured

**The Rust front end already chews the whole compiler, and it is not close.**

    desugardump cover codexzig-subject.codex
    1 files, 6431 definitions desugared
    332811 AST expression nodes, 0 of them the error node (0.000%)
    desugar: 3440947 bytes in 0.143s, 22.9 MB/s
    0 name(s) the scope pass could not resolve

3.4 MB, 92 chapters, zero error nodes, zero unresolved names, a seventh of a
second. Reading, desugaring and scoping the compiler is a solved problem.

**The interpreter gets INTO the driver.** I took the existing transpiler subject,
dropped its trailing zig harness, appended a four-line one that calls
`compile-frontend-cdx` on an inline `fib` and prints `emit-ir-chapter`, and ran
it. It did not fall over at the door. It ran until:

    builtin `__heap-save` has no rule for ()

**And that first blocker is a bug we have already diagnosed once.** `__heap-save`
is implemented. What it lacks is a NULLARY rule — the same shape as the
`uefi-read-key-ex` incident, where a builtin's arity came out of the probe as a
default rather than as a fact and the interpreter guessed one argument for a
function that takes none. The error names the victim, not the culprit.

So the honest status is: not "can the interpreter run the compiler", but "which
of about a dozen builtins does it still owe".

## The reaction I want to lead with

**This is a test of the interpreter, not of the IR.** Worth saying plainly,
because the framing is easy to slide on. If Rust interprets Cobblestone's own
front end, the IR that comes out is Cobblestone's IR by construction — the same
algorithm, the same allocation order, the same `(tvar N)` numbering. Agreement
with bare metal would not be four independent compilers agreeing. It would be
one compiler, run on a fourth host, agreeing with itself.

That is not a criticism. It is the most demanding interpreter test available
anywhere in this ecosystem, and the oracle is free and exact. But it is worth
being clear that the thing under test is `interp.rs`, and the compiler is the
subject.

The native Rust `check` and `lower` remain the independent road. This does not
replace them and should not be described as doing so.

## What makes it a good idea anyway

**The subject is enormous and real.** The corpus sweep is 982 programs of
mostly modest size. This is one program of 6,431 definitions that uses records,
variants, effects, higher-order functions, text handling and deep recursion, all
at once, with an exact expected answer. Nothing else we could feed the
interpreter is this demanding.

**It is the same move that unstuck both transpilers.** "Use their
`opening.codex` directly" was the change that got codex-zig-transpiler and
codex-wasm-transpiler to a fixed point at U55. Emulating the driver's phases by
hand is what kept breaking. This is that lesson applied one level further out:
do not reimplement the front end, RUN it.

**It defers the type checker honestly.** Not "skip the hard part" but "let the
hard part be somebody else's code for now". The Rust checker still has 479
effect-row refusals of 1,001; interpreting Cobblestone's unifier sidesteps every
one of them while still producing typed IR.

**And the ladder rungs are already the staircase.** `lex`, `parse`, `desugar`,
`scope`, `check`, `lower` each have a truth file cut against `Fib`, and the
truths NEST. So this is not one big-bang experiment. It is six entry points into
the same bundle, each with a gold already banked, each of which fails
independently and says which layer the interpreter could not carry. Start at
`lex` — if the interpreter can run Cobblestone's lexer over `fib` and reproduce
`lex.truth`, that alone is a real result.

## The part I find genuinely interesting

**A tree walker does not need the allocator ceremony, and that is a
simplification the other arms cannot have.**

The zig harness opens with four lines of it — `init-phase-allocator`,
`__heap-save`, `__deck-set`, `__heap-advance` — and the subject reaches for
`deck-record` 1,555 times, `__heap-save` 114, `__deck-pos` 59, `__heap-restore`
47. That machinery exists because the compiled arms manage their own memory. A
tree walker's host does that job for it.

So for this arm most of that family is a no-op: `deck-record` is the identity,
`phase-compact` is nothing, the heap positions are bookkeeping integers nobody
reads back. The entire memory campaign — the thing that has eaten the most time
upstream this year — is invisible from here.

That cuts both ways, and the second way is the more interesting one. **This arm
cannot see memory defects at all.** Every bug the deck bracket has produced,
every `mcopy-type` misread, every lifetime error — none of it can appear. So
agreement between this arm and bare metal is evidence about the SEMANTICS and
silence about the memory discipline. Which is fine, as long as nobody later
reads a green line here as covering both.

## What I do not know, and would want to find out cheaply

**The step count.** This is the one real risk. `render` is 605 million steps and
`ride` is 1.35 billion; at 37M steps/sec those are 16 and 36 seconds. Compiling
even a twelve-line program through a 6,431-definition front end could plausibly
be anywhere from 10⁷ to 10¹⁰ steps. The bottom of that range is instant; the top
is twenty minutes and breaks the ten-minute rule for this repo. I would measure
it before building anything, and `codexrun bench` already reports step counts.

**Memory.** The compiler builds large intermediate structures and our `Value` is
three words with persistent lists underneath. A front end that allocates
comfortably inside a 512 MB deck may not sit comfortably inside a tree walker's
heap. Also worth a number before a commitment.

**Effects.** The sweep's short tail includes five effect-handler failures. The
compiler uses `[Console]` and `[FileSystem]`; the pure entry point avoids the
second, which is why I inlined the source as a Text literal rather than reading
`/dev/stdin`.

## What I would do first

Three things, in order, none of them longer than an afternoon:

1. **Fix the nullary-arity family and see how much further it gets.** The
   failure mode is already understood and the fix is in the builtin table, not
   in the interpreter. Each fix buys another few hundred lines of progress and
   the next error names the next gap. That loop is cheap and the errors are
   informative.

2. **Measure the step count on the smallest possible subject** — the lexer alone
   over `fib`, against `lex.truth`. If that is a hundred million steps, the whole
   idea is affordable. If it is a hundred billion, we learn that for the price of
   one run and stop.

3. **Only then decide whether to climb.** `lex` → `parse` → `desugar` → `scope`
   → `check` → `lower`, each against its banked truth. The first rung that
   refuses tells us something specific about the interpreter, and the last one
   would be `fib`'s IR — the thing the native road is also aiming at, arriving by
   a completely different route.

My overall reaction: **worth doing, and cheaper than it looks.** The front end is
already there, the interpreter is already in the door, the golds are already
banked, and the failures so far are a builtin table rather than anything
structural. What I would resist is describing the result as a fourth independent
compiler. It is a fourth host for the same compiler, which is a different and
still valuable thing.
