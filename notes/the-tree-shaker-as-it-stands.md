# The tree shaker, as it stands

The zig plug ships a fixed runtime library with every program it emits. That
library — the *prelude* — is 37,461 bytes and 96 top-level zig declarations,
and it goes out whole whether the program touches one declaration or ninety.
`lex.zig` uses about half of it. The shaker's job is to emit only what a
program reaches.

This is where that project is now, what has been proven, and what is left.

## How it works

**One algorithm, in a chapter that has never heard of zig.**
`codex/foreword/core/Shake.codex` is reachability over named parts. It knows
about a `ShakePart` (a name and a list of fragments) and nothing else: no
target, no syntax, no file format. A consumer hands it parts and roots and
gets back what survives, *in the order the input gave them*.

That order rule is load-bearing rather than incidental. Because `shake-kept`
never sorts, shaking with every name as a root reproduces the unshaken whole
byte for byte — which is what separates "the parts table is mis-cut" from
"the closure is wrong", two faults that otherwise share one symptom.

**A part records its dependencies by writing them.** The obvious design keeps
a text and a list of edges side by side, and they drift. Instead a part is a
list of fragments: `ShakeLit` is inert text, `ShakeUse` is text that is *also*
an edge. `shake-frag-text` and `shake-frag-uses` are two projections of one
list, so writing another part's name and depending on it are the same act.
Nothing to keep in step.

**Two consumers, one chapter.** `findings/probe-shake.codex` cites the same
chapter the emitter cites. What the fixtures test is what runs — not a second
copy that agrees today. And because the probe is a tier, the closure itself
gets the double-compiling treatment: bare metal under QEMU and the zig arm
must produce identical output.

**The table is generated, never typed.** `shake_parts.py` reads the emitter's
123 `& "..."` chunks, groups them into parts, splits each part's text into
`ShakeLit`/`ShakeUse` fragments, and splices a new `ZigEmitter.codex`.
Hand-editing 123 string literals byte-exactly is where a week would go, and a
dropped `\n` is indistinguishable from a wrong closure once both are
downstream.

**Roots come from a crude substring scan** of the emitted program text: a part
is a root when its name appears anywhere before the prelude. That is imprecise
in the safe direction — an extra root keeps a part nobody needed; a missing
root breaks the build. In practice it has no imprecision at all, and the
reason is structural: a Codex text literal is emitted as CCE hex escapes
(`"\x30\x0d\x18..."`), so a program's own strings cannot contain a prelude name
in a form the scan can see, and emitted zig carries almost no comments. Crude
roots and code-position roots agree exactly on every program tried.

That last fact settled an open design question. The *upward channel* — letting
emission report what it learned back to its caller — is **not needed for
shaking**. It remains worth building for its own reasons; it is not on this
critical path.

## Four gates, and what each cannot see

The gates matter more than the algorithm here, because the algorithm is
twenty lines and the ways to get the *data* wrong are numerous and quiet.

| Gate | Question | Cost |
|---|---|---|
| **Declaration** | Is every top-level declaration in the prelude a part name? | free |
| **Identity** | Do the parts, concatenated, equal a prelude the plug really emitted? Does each part's fragment list rebuild its own text byte for byte? | free |
| **Corpus edge** | Shake with the *real* roots, then ask zig's own question of the result: is anything referenced here not declared here? | 3.7s / 15 programs |
| **Table** | Is the table in the shipped emitter exactly what the generator produces? | free |

The important line in that table is the third. The identity gate runs the
whole closure with every part name as a root — which sounds strong and is
blind to every edge error, because reachability completes before any edge
matters. It proves the cut and the concatenation and stops there. The corpus
edge gate is the only one that exercises an edge, and it does so without a
compiler: shake the program, then scan the finished text for prelude names in
code position and require each to be declared in what survived.

There is a fifth thing, which is a gate on a gate. `--prove-gate` suppresses
one declaration and requires the corpus gate to name it, so its power is
checked rather than assumed. The victim is derived rather than written down:
the most-depended-on part that is *never* a root in any program, so it survives
only through the closure. Today that is `cx_gpa` with 20 incoming edges — and
deliberately not `std`, which has 27 but is named directly by every program, so
suppressing it would prove the scanner works and leave reachability untested.

## What has been validated

**The cut is complete.** 96 parts for 96 declarations. Three chunks carried a
comment block *and* a declaration in one string, so they had no part of their
own and could only survive by coincidence — whichever part swallowed them
happening to be kept. `cx_heap_base` was the dangerous one: five callers, none
of them reaching the part it was buried in.

    old cut   93 parts, 96 declarations    4 clean, 10 broken over the rungs
    new cut   96 parts, 96 declarations   14 clean,  0 broken

**The restructure moves no byte.** Natives built from the 96-part emitter with
the shake off, then compared against the pre-restructure baseline:

    ast/codexir.zig   1,979,036 bytes   md5 b77431b7   BYTE-IDENTICAL

That is the whole closure running with an all-roots root set and reproducing
the hand-written chunk list exactly. It is the strongest available statement
that the data is right, and it is deliberately separate from the statement
that the *selection* is right.

**The closure agrees across arms.** `probe-shake` is 19 fixtures, green on
bare metal and through the plug, byte-identical. Fixture 8 — the ordering one —
now distinguishes the table-order implementation from the discovery-order one
that somebody would plausibly write instead: table `[C, A, B]` with A → B → C
rooted at A gives `C A B` where discovery gives `A B C`. Both implementations
were simulated over all ten graph fixtures first; it is the only one that
separates them.

**The cost of computing roots is measured, not guessed.** `probe-scancost` is
now in the tier set with a banked gold. Eight runs, boot subtracted:

    scan   2.29s for 20,643,840 chars   →   9.0M chars/s
    largest program we emit: 186M chars →   21s  (15–33 bounded by extremes)

**The reduction, on the 96-part cut, over the 14 rung programs:**

    lex.zig            52/96 parts   52% of prelude bytes   48% smaller
    lower.zig          69/96         68%                    32%
    passes_to_x86.zig  80/96         79%                    21%
    codexir.zig        79/96         86%                    14%

## The link to corpus and tiers

Both, and in different roles.

**Tiers own the algorithm.** `probe-shake` and `probe-scancost` are ordinary
members of the tier set, run by `tiers_run.py`, banked under
`findings/gold/u52/`, keyed on program text plus seed so a fixture edit forces
a re-bank rather than silently reusing a stale answer. The closure is
double-compiled like everything else.

**The corpus owns the data.** The 589 programs in `codex/test/` are the only
population large enough to exercise which parts get dropped together.
`corpus_run.py --transpile` emits all of them through the natives — minutes,
no QEMU — and `shake_parts.py --check-corpus` shakes each one and checks it.
That is the scale at which the orphan bug would have shown as 468 broken
builds, and 14 rungs is a smoke test by comparison.

There is a third link, and it is the actual argument for the project. Of the
96 parts, **42 are kept by every rung program, 8 by none, and 46 by some and
not others.** Today an edit to any of those 46 moves the emitted bytes of every
program identically, because every program carries the whole prelude. With
shaking on, it moves a strict subset — and *which* subset is a signal the corpus
byte-identity oracle currently cannot see at all. Shaking does not just make
output smaller; it un-blinds an instrument we already rely on.

Worth being plain about what it does **not** buy: compile time. Zig already
dead-strips the unreached declarations. Same binary size, no measurable
compile-time signal. The payoff is legibility and that oracle.

## What remains

**1. Turn the shake on and run the corpus gate at scale.** The shake is off in
the committed emitter, and turning it on is a flag on the generator rather
than a hand edit. Then rebuild natives, transpile the corpus, and run
`--check-corpus` over all 589. The corpus `.zig` files currently on disk
predate the prelude-last change and every one of them skips, so this needs a
fresh emit. **This is the item that decides whether the shaker ships.**

**2. `check-zig-prelude-surface.ps1` breaks by design when the shake is on.**
It requires every subject's prelude to be identical; shaking makes them differ
on purpose. The replacement is a stronger property, not a weaker one: each
emitted prelude must be a sub-selection of one known whole, in table order,
verified by a greedy walk that has to land exactly at the end. The surface is
then derived from the whole rather than from any one program, which keeps the
reserved list a union — as the emitter's own prose already insists it must be.

**3. A hole that has nothing to do with shaking.** `zig-prelude-decls` is
documented as "the UNION over the whole prelude" and names 23 of the 96
declarations. Every `fn` is missing, including `cx_print` and `cx_new`.
`zig-sanitize` renames a program's name only when it appears in that list, so a
Codex program defining `cx-print` should emit a second `fn cx_print` into a
file that already has one. The cause is in the deriving script: it reads
`const NAME`, `var NAME`, `|capture|` and function *parameters*, and never a
function's own name — so it has been printing OK over a surface missing three
quarters of the declarations. A probe is written and **not yet run**; nothing
above should be treated as established until it is.

---

*Ladder `master` @ `3ebcd32`. Emitter branch `zig-tree-shaking` @ `e74cd110`
in `~/showell_repos/cobblestone-treeshake`, shake still off. Run
`20260828T190620Z-shake-96parts`.*
