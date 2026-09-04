# Two things the ladder built, and what is worth carrying

*2026-09-04, written while deciding what `codex-qemu` should inherit.*

The exercise is cutting fat. Two candidates: `ir_to_x86_on_cce`, the rung Steve
remembers as the ten-to-fifteen-minute one, and `f3_run.zig`, which I carried
over this afternoon without asking whether it should exist and then spent four
rounds repairing. Neither is worthless. Both are the wrong shape.

## `ir_to_x86_on_cce`: it is a capacity test, and it says so

The rung has no harness of its own. It rides as a second subject inside the unit
`gen_ir_to_x86_harness.py` builds, so the 2.4 MB of compiler underneath both
subjects is compiled once instead of twice. What the rung owns is the subject:
`codex/foreword/core/CCE.codex`, 526 lines, with a dull integers-in-integers-out
driver appended.

Its own docstring is unusually clear about why:

> No new emitter surface is expected: **the point is capacity**, which is the one
> thing a tiny subject cannot test. Accumulators, deck sizing, the WCET walk and
> the code buffer all scale with the subject, and every cap in that path was set
> by subjects small enough never to reach it.

That is a real and separate question from the one `ir_to_x86_on_fib` asks.
Eighteen lines cannot fill a buffer. And the subject choice is careful: CCE
because it cites nothing, so a compiler with no bundler in the loop can compile
it; dull driver because a rung that also exercised new print paths "would stop
being a capacity test and start being two experiments at once."

## What it has actually caught

One documented thing, and it is exactly the thing it was built for.

`JUSTIFICATIONS.md` records the heap-reservation sizing:

    rung              defs  reservation   bare metal   zig arm    zig/bare
    ir_to_x86_on_fib     3   25,362,432   23,654,536   27,014,528   1.142x   OVER by 6.5%
    ir_to_x86_on_cce    61   29,163,520   23,708,712   27,064,232   1.142x   fits, 2.1 MB free

The pair is the finding. **The ratio is flat across 3 definitions and 61** —
1.142x both times — which says the zig arm's overhead is a per-object
representation cost and not a per-definition one. The reservation formula's
`defs*65536` term "barely matters": bare metal spends 54 KB more on 61
definitions than on 3, and the flat term does all the work.

You cannot learn that from one subject. Two points at different sizes is the
minimum for a slope, and the whole conclusion is about the slope being flat.

So: load-bearing, once, for precisely its stated purpose. That is a thin record
for a rung, and it is also not nothing — a wrongly-sized reservation is the
failure that kills a run with no diagnostic.

## Where the eggs could move, and where they cannot

Steve's instinct is that `codex-zig-transpiler` should carry more of this. It is
right about the axis and wrong about the backend, and the distinction is the
whole answer.

`codex-zig-transpiler` compiles **2.9 MB** — the compiler itself — and demands a
fixed point. That is a capacity test an order of magnitude beyond CCE's 526
lines, running continuously, against a subject nobody had to invent. If the
question is *"do the accumulators and buffers hold at scale"*, that repo asks it
harder and more often than the cce rung ever did.

But it asks it of the **zig emitter**. `ir_to_x86_on_cce` asks it of the
**x86-64 back end** — a different code generator, different buffers, a different
WCET walk, and the only one whose output is machine code. Nothing in the four
modern repos exercises that path at any scale at all.

So the honest split:

- **the sizing question** — how the two arms' memory scales with subject size —
  is better served by the transpiler's 2.9 MB fixed point, and by measuring, not
  by a rung.
- **the x86 back end at scale** has no other home. If it is worth testing, it is
  worth testing here.

And the second one deserves a harder question than I can answer from the record:
**who compiles something large to x86?** The seed is prebuilt; running it does
not exercise the emitter. The answer is the depot's own self-host, which is not
something we run. If nobody in our loop compiles 500+ lines to bare-metal
machine code, then the cce rung is testing a capacity nobody consumes — and the
right move is to drop it and let the transpiler's fixed point carry the sizing
work.

I do not think that question has been asked. It should be, before the rung is
carried or dropped, because it is cheaper to answer than the rung is to keep.

## `f3_run`: F1 to F4, a progression nobody wrote down

The `f` numbers are milestones of the fib ladder, and the old README explains
them in one paragraph that nothing else references:

| | what it was |
|---|---|
| F1 | fib through the front end |
| F2 | fib through the x86 back end — this is the `ir_to_x86_on_fib` rung |
| F3 | **run** the emitted code |
| F4 | **boot** the emitted binary |

The names are the problem. F1 and F2 dissolved into rungs and stopped being
called F-anything; F3 and F4 survive as `f3_run.zig` and `f4_boot.py`, two files
whose names encode a position in a sequence that no longer exists. Nobody
reading `f3_run.zig` can tell what F3 *was* without finding a README paragraph
1,800 lines in.

What they ask is genuinely different from the rungs, and the same README says it
in one line: **"The rungs prove the plug emits the same bytes. These ask whether
the bytes mean anything."** Two emitters can agree on a wrong answer. Everything
else in the toolchain compares text; these are the only things that execute.

## F4 is the stronger check, and I carried F3

`f3_run.zig` carves `fib` out of the content buffer, drops it in RWX memory and
calls it. It proves the instructions are real. Its sibling's docstring says
exactly what it does not prove:

> which proves the instructions are real but **says nothing about the binary
> around them** — the header, the entry point, `__start`, the runtime init, the
> serial path.

`f4_boot.py` reassembles the dump into a real CDX the way `emit-binary-tail`
does — header, content, tail — boots it, and checks it prints what its program
says. The README calls it **"the one check that does not depend on the two arms
sharing a mistake."**

So of the two, F4 is the one with the unique property, and I carried F3. Not
because I compared them; because it was a `.zig` file next to a rung I was
copying.

## What the repair bill says

`f3_run.zig` needed four fixes to run once in its new home:

1. `std.process.argsAlloc` is gone in this zig — my own change, backed out
2. the harness prints a subject banner the parser does not expect
3. the harness grew an `emit-diags` line and a `.` since the parser was written
4. a failed build left a partial binary, and "skip if it exists" reused it

Items 2 and 3 are the diagnosis. **The dump format moved and the parser never
noticed**, because in the ladder it was fed by `split_truth.py` and only ever saw
one rung's output. 230 lines of Zig hand-parsing a text format that drifts, to
call one function in one shape.

The capability is worth keeping. That implementation is a liability.

## Thinking outside the repo

The strongest observation is that **something already asks F4's question at
scale, and it is not F4.** `corpus_run.py` runs the depot's 1,239 programs
natively and compares against hand-verified `.expected` files. That is "do the
bytes mean anything" at a thousand programs, against the one oracle in the whole
system that is neither an implementation nor a fixed point — it is what a human
said the answer should be.

F4 boots six binaries. The corpus checks 1,239 programs. What F4 has that the
corpus does not is the **bare-metal x86 path specifically**: the corpus runs the
hosted zig binaries. So F3 and F4's real scope is narrower than "do emitted
bytes work" — it is "do emitted *x86* bytes work", which is the same narrow
column as the cce rung.

That is a tidy result: **both candidates reduce to the same question, and it is
the only question left that nothing else covers.** Does the x86-64 back end
produce machine code that is correct at more than toy size? If the answer
matters, one thing should ask it, not a rung and two f-numbered scripts. If it
does not matter, all three go.

## What I would carry, concretely

**Rename by the question, not the position.** `codex-qemu/fib_checkers` already
names by route — `verify_fib_with_qemu.py`, `verify_fib_with_zig.py`,
`verify_fib_with_x86.py`. F3 is already inside the third of those. F4 becomes
`verify_fib_by_booting.py`, and the f-numbers die with the ladder, which is the
right place for a brainstorming artifact to end up.

**Carry F4's property, not F3's implementation.** Booting the reassembled binary
subsumes calling a function out of it, and it is the check that does not depend
on the two arms sharing a mistake. If only one survives, it is that one.

**Do not carry 230 lines of drifting text parser.** The dump is the compiler's
own format; a parser for it belongs next to something that already reads that
format, or the emitter should be asked for a binary rather than a text dump it
then has to be reassembled from. That is the "outside the repo" move — not
finding a better home for the parser, but not needing one.

**Answer the consumer question before carrying the cce rung.** If nothing in our
loop compiles 500 lines to x86, its capacity is untested because it is unused,
and the transpiler's 2.9 MB fixed point is where the sizing work belongs.
