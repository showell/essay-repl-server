# What the ladder is for, and whether it still needs to be a repo

*2026-09-04. Written after a day that started on safari specs and ended with
`git clean -xdf` taking the ladder from 347 MB to 4 MB.*

## Four repos that can be described in a phrase

Steve described the modern repos in four phrases, and the phrases are the
interesting part:

- **rust-codex-compiler** — a completely independent oracle
- **codex-zig-transpiler** — a fixed point against a large subject
- **codex-wasm-transpiler** — a fixed point against a large subject
- **safari-codex** — an actual Steve application

Each is one sentence. Each says what would be lost if the repo vanished. Try it
for **codex-zig-ladder** and the sentence does not arrive. It is a rung
harness, a QEMU driver, a sandbox system, a findings register, an outbound PR
queue, a corpus census, a branch-topology ledger, three linters and a
priorities file that itself says it is the plan of record.

The file counts say the same thing more bluntly. Of 557 tracked files, **323
are `findings/`** and 100 are `src/`. The largest component of the ladder is a
written record, and the second largest is the machinery. Those are two
different kinds of thing wearing one name.

## The property the ladder cannot have

Here is the sharper problem, and I did not see it until today.

The ladder compares two arms: bare metal under QEMU, and the zig plug. Both are
Damian's code. They share the entire front end — the same lexer, the same
parser, the same desugarer, the same type checker, the same lowering, all of it
Codex source from the same commit. They diverge only at the emitter.

So the ladder can find emitter disagreements, and it does; the uniform-boxing
fix that took it from 6/14 to 11/14 is exactly that shape. But **anything wrong
above the IR is invisible to it by construction**, because both arms inherit it
identically. Fourteen rungs, hours of QEMU, and a whole class of defect it
cannot see on any subject.

This is not hypothetical. Today the safari spec suite found that Codex converts
a decimal Real literal incorrectly — 10 of 120 ordinary doubles land one ULP
away, in the front end, so every backend gets the same wrong bits. The ladder
has never seen it and never could. It took an independent front end fifteen
minutes.

I made the same mistake in miniature earlier in the day. I argued that all four
arms should share one bundler, for one source of truth. That is exactly
backwards: a shared component is unfalsifiable by the comparison it participates
in. Four arms agreeing tells you nothing about the thing all four inherited. The
ladder is that argument at full scale, and it has been running for weeks.

## What the ladder uniquely has

One thing, and it is genuinely precious: **bare metal**. Real x86, no host
runtime, under QEMU. It is the only arm that can answer questions about memory,
the deck, `address-of`, boxing, and what the machine actually does. Findings 70
and the boxing gap both came from there, and neither could have come from
anywhere else.

Everything else in the repo is scaffolding around that one capability, and the
scaffolding has grown larger than the thing it holds up. 1,862 lines across
seven files exist to cut sandboxes, name measurements, save them, restore them
and check that a checkout has not moved. Today all seven turned out to be
solving problems created by the other six.

## Three things I had stopped questioning

Steve asked me to open three assumptions. Opening them is easier now that the
above is on the table.

### The fourteen rungs

They are twelve units over five subjects, and they are a **history of the
project rather than a design**. Each rung was the frontier when it was built:
lex when the lexer was the question, then parse, then desugar, up to
`passes_to_x86`. Nothing has ever asked which are load-bearing now. Two of the
fourteen are subject variants of one unit. One — `ir_to_codex_roundtrip` —
takes its own previous output as its subject, which is a real fixed-point
property and also means it can pass while the thing it round-trips is wrong,
because both sides come from the same arm.

What a person actually wants is not fourteen rungs. It is: **run stage X on
subject Y under arm Z, and show me what came out.** The rungs are a frozen
enumeration of a few dozen points in that space.

### The subjects

I said everything hangs off `fib` and that was wrong, so it is worth writing
down correctly:

| rung | subject |
|---|---|
| lex, parse | `Syntax/Lexer.codex`, 659 lines |
| desugar | `Ast/AstNodes.codex`, 640 lines |
| scope | `Semantics/NameResolver.codex`, 503 lines |
| check, lower, ir_to_codex, ir_to_wire, lir_to_x86, ir_to_x86 | `fib`, 7 lines |
| ir_to_x86_on_cce | the CCE chapter, chosen because it cites nothing |
| passes_to_x86 | `Chapter: Mid`, and `plug-oracle-arith.codex` |

The front half is measured against real 500–660 line compiler chapters. The back
half narrows to seven lines. That is not arbitrary — a whole x86 instruction
stream has to be diffable by eye — but it leaves **a hole exactly where types
live**. `check`, `lower` and `ir_to_wire` are the rungs that carry inferred
types, and `fib` has one type, one comparison and one recursion.

The defect we are chasing right now is the plug typing `n <= 1` as `error`
instead of `boolean`. It is visible on `fib` by luck: there is exactly one
comparison in the subject. A subject with three types would have told us whether
the plug gets every comparison wrong or only this one, which is the first
question anybody would ask, and the ladder cannot answer it.

### Bare metal as the only oracle

It is not, any more, and that is new since the Rust front end reached LOWER.

Rust is byte-identical to upstream through lex, parse and desugar across the
whole corpus, and its IR chapter preamble matches on 1,011 of 1,012 programs. So
for the front half of the ladder — the half with the big subjects — **there is
now an independent oracle that answers in milliseconds instead of minutes**, and
independence is the property the ladder's two arms structurally lack.

What Rust cannot answer: anything below the type checker, where 1,001 of 1,011
programs come back "not yet typable" and 479 of those refusals are effect rows.
And nothing at all about hardware.

That is a clean division of labour, and it is roughly the opposite of how the
work is currently distributed.

## What a decomposition might look like

Not a proposal yet — a shape to argue with.

**A bare-metal runner.** One job: given a Codex commit and a subject, run it on
real x86 under QEMU and print what came out. No rungs, no banks, no sandbox
taxonomy, no naming scheme. The comparison belongs to whoever asked the
question, and the answer is a file. This is the ladder's irreplaceable
capability with everything else stripped off.

**The front half moves to rust-codex-compiler.** It already has the oracle
property and already runs the whole corpus. "Does upstream's lexer agree with an
independent lexer on 1,012 programs" is a question that repo is built to answer
and the ladder answers slowly, on one subject, with a shared front end.

**The fixed points stay where they are.** codex-zig-transpiler and
codex-wasm-transpiler already do the thing the back half of the ladder gestures
at — compile the compiler with itself and demand the same artifact — against a
subject vastly larger than `fib`.

**The records are not machinery and should not be deleted with it.** 323
findings files, the outbound queue, `CARRY_FORWARD.md`, the branch topology, the
corpus of 1,239 programs with `.expected` files. These are the accumulated
result of two months and none of them need a rung harness to exist. Whatever
happens to the machinery, this wants a home where it is not entangled with
scripts that write 343 MB beside themselves.

## What I am unsure about

**Whether the middle survives the split.** `check`, `lower` and `ir_to_wire` are
the rungs with no good home: too deep for the Rust arm until the type checker
lands, too fine-grained for a fixed point, and running on a seven-line subject
because the alternative is unreadable. The honest answer might be that they wait
for Rust's checker rather than being rehoused.

**Whether the corpus belongs to any of the four.** It is 1,239 programs with
hand-verified expected output, and it is the only oracle in the system that is
neither an implementation nor a fixed point — it is what a human said the answer
should be. That may deserve its own small repo rather than being a directory
inside a harness.

**Whether "one sandbox, one commit" survives contact with the plug loop.** The
plug lives in the Codex checkout, so every plug edit is a new commit and, read
literally, a new sandbox and another 1,800 seconds of QEMU. The reconciliation is
that a sandbox is pinned to the *oracle-relevant* commit — everything outside
`docs/` and `codex/plugs/` — which is a rule I only found today, by accident,
while fixing a naming scheme. It deserves to be a designed rule rather than a
lucky one.

**And whether any of this should be a repo at all**, versus a directory in
rust-codex-compiler with a QEMU script in it. The ladder became a repo when the
ladder was the project. It is not obvious that it still is.
