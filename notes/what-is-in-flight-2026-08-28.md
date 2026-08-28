# What's in flight — the prelude, the shaker, and the tuples on deck

Three pieces of work, all touching the same 37,461 bytes of zig that the plug
staples onto every program it emits. They arrived in a particular order, and
the order was mostly luck: one of them is a defect that has been there since
long before any of this started, and it surfaced only because the other one
made me go looking at the same list.

## 1. The tree shaker — done, unsent

The prelude ships whole to every program. `lex.zig` uses about half of it,
`arith.zig` less than half. The shaker emits only what a program reaches.

**How it works, briefly.** One target-agnostic chapter,
`Foreword chapter Shake`, does reachability over named parts and preserves
input order. A part records its dependencies by *writing* them: it is a list
of fragments where `ShakeLit` is inert text and `ShakeUse` is text that is
also an edge, so a part's text and its edges are two projections of one list
and cannot drift apart. The zig plug supplies 96 such parts, generated from
the emitter's own prelude by `shake_parts.py` — never typed by hand. Roots come
from a substring scan of the emitted program.

**Where it stands.** The shake is on, natives build from it, and the full
corpus agrees:

```
607 programs transpiled, 578 emitted

EMITTED GATE     578 clean, 0 broken     nothing referenced is undeclared
SUB-SELECTION    578 ok,    0 not        each prelude is the whole, in order, minus parts
```

Reduction over those 578: median **57% smaller**, best 75%, worst 35%; the
smallest quartile of programs sheds 61%.

**What it is actually for**, since the size number is the least interesting
part: 46 of the 96 parts are kept by some programs and not others. Today an
edit to any of those moves the emitted bytes of every program identically,
because every program carries everything. With shaking it moves a strict
subset — and *which* subset is a signal the corpus byte-identity oracle
cannot see at all right now. It does not buy compile time; zig already
dead-strips. It buys legibility, and it un-blinds an instrument we already
rely on.

## 2. Finding 67 — the reserved list, fixed in the same PR

A zig file *is* a struct, so its top-level declarations are its members and
two with one name is a hard error. The plug's only defence is `zig-sanitize`,
which appends an underscore to a program's name if that name appears in
`zig-prelude-decls`.

That list covered **22 of the prelude's 96 declarations, and none of its 74
functions.**

```
probe-prelude-collide.codex — a top-level named cx-print
  bare metal   runs, 7 correct lines
  zig          error: duplicate struct member name 'cx_print'
                                                   'cx_new'
                                                   'cx_concat'
```

The cause is not a judgement call, it is a regex. `check-zig-prelude-surface.ps1`
derives the reserved surface from emitted output, and to harvest a function's
*parameters* it matches:

```
'\bfn\s+[A-Za-z_][A-Za-z0-9_]*\s*\(([^)]*)\)'
```

It reads straight past the function's own name to reach the parameter list and
drops it on the way. So the script has been printing `OK: every derived name
is reserved` over a surface missing three quarters of the declarations, while
the emitter's prose asserts the list "is the UNION over the whole prelude and
stays that way." That was never true.

**Severity is higher than the `cx_` prefix suggests.** 69 of the 74 sit in
what is effectively the plug's namespace, which is why zero of 578 corpus
programs collide. The other five are `CxList` and `CxFn1..CxFn4` — the
comptime type constructors. Codex type names are CamelCase. `CxList` is a name
a program can pick with no sense of trespassing, and a second probe confirms it
fails the same way.

**Why it is in the shaker's PR rather than its own.** It is not caused by
shaking — both probes fail identically on a tree with no shaker in it. But the
fix touches `check-zig-prelude-surface.ps1`, and so does the shaker, for an
unrelated reason: that script requires every subject's emitted prelude to be
*identical*, which shaking breaks by design. One file, two repairs, one PR.

The replacement for the identity test is stronger than what it replaces: each
emitted prelude must be a **sub-selection of one known whole, in table order** —
walk the parts, consume what matches at the cursor, skip the rest, require the
cursor to land exactly at the end. A prelude that reordered, duplicated,
truncated or invented anything fails that walk. "They are all identical" tested
none of it.

## 3. Tup2..Tup5 — on deck, and not what you'd guess

`Foreword Tuple` rides into every unit unconditionally, so every emitted
program carries 24 lines of tuple constructors. In `arith.zig` each of the
four appears **exactly once — its own declaration, zero uses.**

The thing worth stating plainly: **tree-shaking does not remove them and never
will.** They are emitted into the *program* region by the type-def emitter,
not into the prelude, so the prelude shake cannot reach them. All four are
still present in shaken corpus output. `ir-prune-unreachable-roots` already
does exactly this shape for defs; type-defs never got it.

Before that, the transpiler exercise: point `codex-zig-transpiler` at the
tree-shaking branch. Simulated, `arith.zig` goes from 907 lines to about 460 —
a 54% cut. The fixed point itself will barely move, because `codexzig` is a
2.9 MB program that reaches most of the prelude.

## Reflection, and two ideas

**The gates were harder than the algorithm, by a lot.** `Shake` is twenty
lines and was right early. What took the day was the data: is the cut
complete, do the edges hold, is the shipped table what the generator produced.
Three of those five gates exist because an earlier gate turned out to prove
less than it appeared to. The sharpest example: shaking with *every* part name
as a root reproduces the unshaken prelude byte for byte, which sounds like a
strong check and is blind to every edge error — with all names rooted,
reachability completes before any edge matters. Both edge bugs walked straight
through it while it reported green.

The lesson I'd keep is narrower than "write more gates". It is: **for each
gate, write down what it cannot see, next to it.** Doing that for the corpus
edge gate is what turned up its one real blind spot — it catches "referenced
but not declared" and cannot catch "required but neither referenced nor
declared", i.e. anything zig resolves by *name*. That is currently harmless,
but only because no prelude part is called `main` or `panic` or `std_options`,
and that is a fact worth checking rather than a fact worth assuming.

**Two ideas the work suggested.**

*The accumulator, and the ratchet that makes it honest.* Roots come from a
substring scan because there is no upward channel — `emit-zig-expr` returns
`Text` and `ZigCtx` threads only downward. The structurally right answer is to
accumulate roots at the codegen sites. My first objection was that this
requires every site to remember, and I was wrong about the size of that
problem: the hand-written surface is **21 sites, 14 names**, not the 246 I
first counted, which had swept in the prelude's own text and the reserved
list. So Steve's construction works — make a helper the only way to spell a
builtin, and forgetting stops being possible. `check_builtin_sites.py` is the
ratchet that makes "the only way" a fact rather than an intention; it refuses
a 22nd hand-written site today. Worth noting the scan should survive
afterwards, as a gate asserting the accumulator's roots are a superset of the
scan's — that converts a completeness argument into a check.

*Shaking as an oracle, not a feature.* The un-blinding effect might be the more
useful half. Right now, if I edit one prelude function, the corpus tells me
"all 578 files changed" — which is true and useless. Shaken, it tells me
"these 41 changed and these 537 did not", and the 41 are exactly the programs
that reach the thing I touched. That is a dependency map falling out of a
size optimisation, and it is checkable: the set of programs whose output moves
should equal the set whose root closure contains the edited part. If those
ever disagree, something is wrong with the closure — a self-checking property
that costs nothing to run and that we do not have today in any form.

---

*Ladder `master`. Emitter branch `zig-tree-shaking` in
`~/showell_repos/cobblestone-treeshake`, shake ON, unsent. Runs
`20260828T192913Z-shake-on-corpus` and `20260828T200552Z-f67-byteneutral`.*
