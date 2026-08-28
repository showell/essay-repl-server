# Shaking without zig

*Design thinking, 2026-08-28. Nothing built. The question is whether the core
of tree-shaking can be a chapter that never says "zig", and whether that
chapter can be tested before ZigEmitter is touched at all.*

---

## The problem, stripped

Three inputs, and only one of them is interesting.

1. **Roots.** Names the consumer requires. For the zig plug these come from
   scanning emitted program text for `cx_foo(`. For anything else they come
   from somewhere else. **The chapter should not care.**
2. **Parts.** An ordered list of `{name, needs, text}`. The prelude, cut at a
   seam that already exists: every `& "..."` chunk in `zig-prelude` is exactly
   one top-level declaration or one comment block. 122 chunks, 93 named decls.
3. **The closure.** Roots reach parts; parts reach other parts. `cx_ll_of`
   calls `cx_ll_empty`, which calls `cx_gpa.create(CxList(T))`. Three levels
   from one root, and nothing in the emitted program mentions `CxList`
   directly.

The third is the whole algorithm and it is not novel. It is reachability in a
directed graph, plus "keep the input order".

    shake : List Part, List Text -> ShakeResult

    Part        = record { name : Text, needs : List Text, text : Text }
    ShakeResult = record { kept : List Part, unmatched : List Text }

That signature mentions no target, no syntax, no file format. It is the entire
public surface.

## The split, and what is deliberately NOT in the chapter

**In the chapter:** the closure, the ordering rule, cycle handling, and the
honest reporting of roots that matched nothing.

**Stays in ZigEmitter:** extracting roots from emitted text (`name & "("` for
functions, bare name for vars — `cx_print` is a prefix of `cx_print_line`,
`cx_print(` is not), and concatenating `kept` back into a string.

**Generated, never typed:** the parts table itself. Hand-editing 122 string
literals byte-exactly is where a week would go. A ~40-line script reads
today's `zig-prelude` and writes the table.

The chapter is maybe sixty lines. Everything expensive is on the other side of
its interface, which is the point.

## The twist: where do the edges come from

Steve's framing — indirect calls are opaque, embedded in the text — is exactly
the question of who computes `needs`. Four answers:

**(a) Scan at shake time, inside the chapter.** Cheapest to write, and wrong:
it makes the chapter text-aware and target-aware, which is the thing we are
trying to avoid.

**(b) Declare `needs` by hand in the table.** Clean chapter, silent drift. Edit
a prelude chunk to call something new, forget the edge, and a live declaration
is dropped — discovered at `zig build` time, for whichever programs happen to
exercise it. **This is the one failure mode that must never happen**, so a
mechanism whose failure mode IS that mechanism is disqualified.

**(c) Generate the edges mechanically into the table, and regenerate to
verify.** Precise, and drift becomes a diff rather than a silent drop.

**(d) The caller supplies the edges; the chapter takes them as data.**

**(d) is the answer, and it subsumes (c).** The chapter's contract is
graph-only. ZigEmitter can start by scanning the parts' own text at shake time
— always correct by construction, no table to drift — and later move to a
generated table for speed, with the chapter unchanged and untouched. The
decision about where edges come from stops being an architectural commitment
and becomes an implementation detail on one side of a line.

## Invariants, in the order that matters

**1. Never drop a reachable part.** Keeping too much costs bytes. Dropping too
little costs a broken build, late, for a subset of programs. Every ambiguous
call — is this a reference or a word in a comment? — resolves toward keeping.
The failure mode is chosen, not discovered.

**2. Determinism.** Same inputs, same output bytes, always. The corpus
byte-identity oracle is the safety net for the whole project; a shaker that
reorders under set iteration would poison it.

**3. Preserve the parts table's order.** Not topological. Zig does not need
declaration order — container-level declarations are order-independent, which
is exactly what PR 95 proved by moving the entire prelude below the program.
Topological sort would be gratuitous churn and would break byte-identity
against today's output for no gain.

That third one buys something free and large:

> **Shaking with every part name as a root must produce output byte-identical
> to the unshaken prelude.**

That is the identity gate, it needs no zig build to check, and it can be run
over the real 122-chunk prelude before any filtering is trusted. If it fails,
the parts table is wrong — a dropped `\n`, a mis-split chunk — and you learn
that separately from whether the closure is right. **Those two bugs have the
same symptom and this separates them.**

## Three decisions worth arguing about

**A comment block belongs to the declaration below it.** The prelude's
comments are load-bearing prose — "The capacity is load-bearing, not a hint",
"Mirrors bare metal's `__text_to_double`, not a correctly-rounded parse". If a
part is only the decl, shaking orphans them into a header of explanations for
code that is no longer there. So a part is *(leading comments + one decl)*,
kept or dropped together.

**Unmatched roots are reported, not swallowed.** A root naming no part means
either the program references something the prelude does not provide (a real
bug) or the extractor over-matched (a name inside a string literal, expected
and harmless). The chapter cannot tell these apart and should not guess. It
returns them and lets the caller rule.

**`zig-prelude-decls` must NOT be narrowed to the kept set.** It is the
shadowing-reservation list, and it stays the union over the whole prelude. The
cost of over-reserving is one spurious underscore; the cost of narrowing is
that the same Codex source emits a *different spelling* depending on which
builtins it happened to touch. This is already written into the emitter prose
and it is the trap shaking sets for its own author.

## The part that justifies doing it this way

**The algorithm can be tested to exhaustion before ZigEmitter is opened.**

Because the chapter is graph-only, its fixtures are graphs. No zig, no QEMU,
no plug build, no corpus:

    linear     A->B->C, root A            all three, in table order
    diamond    A->{B,C}, B->D, C->D       four parts, D once
    cycle      A->B->A, root A            both, terminates
    island     A->B, plus unreached C,D   two
    no roots   any table, roots []        empty, and no crash
    unknown    root "nope"                kept unchanged, unmatched ["nope"]
    identity   roots = every part name    every part, original order

Seven fixtures, each a handful of lines, each with an exact expected answer.
That is a tier-style probe or a one-off script, seconds to run, and it settles
the algorithm completely. **Only then does the expensive half start**, and
when the emitted zig is wrong afterwards you already know the closure is not
why.

## The second user already exists

The doctrine says an abstraction earns its keep on the second user, and the
honest thing is that the second user is not hypothetical — it predates the
first.

`cite_resolve.py` in the ladder resolves a chapter's `cites` transitively:
`_walk` carries a `seen` set, accumulates `parts` in order, and returns a
`missing` list beside them. That is this algorithm, on a different graph,
already written, and it independently arrived at **the same two-output shape**
— what you resolved, and what you could not. A design that converges with
working code written for another purpose is more likely to be the right shape
than one argued from first principles.

Other consumers that would fit without modification: any emitter with a fixed
runtime library (the C# plug's helper set, a future C or wasm plug), and
dead-definition elimination over IR, which is the same closure over a
different node type.

## What could still go wrong

**The parts table is the fragile artifact, not the algorithm.** 122 chunks
generated by a script that has to get every newline right. The identity gate
above is the whole defence, and it should run first and always.

**A false root keeps too much and nobody notices.** That is by design, but it
means the measured 60% reduction could quietly become 20% without failing
anything. Worth reporting the ratio, not just the correctness.

**The payoff is still not compile time.** Measured: zig already dead-strips
this — same binary size to the byte, no compile-time signal. What it buys is
legibility (a defect in an 800-byte program instead of a 38 KB one) and
un-blinding the corpus byte-identity oracle, which today goes dark on every
prelude edit because all 589 emitted files move at once. Do not re-argue this
one; it has been measured.

---

*The next concrete step is the seven fixtures, not the emitter.*
