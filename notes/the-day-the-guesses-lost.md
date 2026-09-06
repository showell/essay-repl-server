# The day the guesses lost

A day that started with four items I was sure about and ended zero for four.
This is the account, because the pattern turned out to be more useful than any
of the individual findings.

## What actually got built

Three things, none of which were on the plan at breakfast.

**`codexir`** — the compiler, stopping at the IR wire, built in
codex-zig-transpiler in ninety-seven seconds with no QEMU guest at all. The
ladder built its codexir through the seed because the seed emits x86 and there
was no other way to a first zig; `codexzig` exists now and is a verified fixed
point, so the chain is swap-one-chapter, transpile, `zig build-exe`. It settled
seven unattributed corpus diffs the day it was born.

**A Rust interpreter that runs Cobblestone's own front end**, byte-identical to
bare metal on 63 of the first 80 corpus programs, and byte-identical to
`codexir` on 35 of 35 at the same pin with nothing normalised away.

**Instruments.** A counting allocator, a step-and-memory reporter, a sampling
profiler bucketed by chapter, a ramp that survives its own out-of-memory
failures. By the end these were doing all the actual work.

## The four things I was wrong about

**One: the cache.** Memory grew as *n*<sup>1.6</sup> in subject size and I was
confident it was the nullary cache I had narrowed that morning — the compiler
contains writers, so the whole-program gate turns off caching for every
list-valued constant, and `builtins` is two hundred records rebuilt on every
mention. Clean story. The measurement: **1107.8 MB with the cache narrowed and
1107.8 MB with it wide open.** Identical to the tenth of a megabyte. The cache
costs *steps* — 28 million against 204 million — and not one byte.

**Two: the flat memory.** Next suspect: the paged byte store backing the type
checker's memo tables, growing without bound because nothing reclaims. The
measurement: **`Parser` peaks at 2.3 GB with zero pages mapped.** Not a page.

**Three: `text-contains`.** Cite resolution was the hot spot, and its inner
loop compared characters one interpreter call at a time. A `text-contains`
guard would reject the common case in a single native call. I checked the
builtin table — `bs-alloc = "none"` — and shipped it. The subject *defines its
own* `text-contains`, a substring search written in Codex, so the call site got
an O(*n*×*m*) scan instead. A self-compile went from cite resolution at 20% of
the run to `str-index-loop` holding 77% of every sample.

The compiler had warned me, in output I had read that afternoon: *"a shadow
that computes the same result more slowly is the failure mode that has actually
cost time here."* I never saw it because I had filtered CDX3005 out of my own
build script as boilerplate. **I suppressed the diagnostic that predicted my
exact mistake.**

**Four: builtin dispatch.** Every builtin call walks a string match over two
hundred arms; replacing it with an index looked obvious. `perf` says
`Interp::builtin` is **3.8% of the run, including every builtin's actual
work**. There is nothing there.

## What was actually wrong

`address-of`.

The compiler asks two ordering questions of it, constantly:

```
copy-sx-text (b) (t) = if address-of t < b then t else substring t 0 (text-length t)
mcopy-name / mcopy-type / mcopy-row:  if a < mc.mc-floor then t
```

Both mean *was this allocated before that base, and therefore durable*. Our
`address-of` returned a raw host pointer — about 1.2×10<sup>14</sup> — and every
floor it was compared against is an allocator offset around
1.6×10<sup>9</sup>. Five orders of magnitude apart. **The comparison was not
occasionally wrong; it was false for every value, always.**

So nothing was ever recognised as already durable, the source text was rebuilt
at every keep boundary, and the memo side lists held all of it. The instrument
that found it counted full-length `substring` calls — the compiler's idiom for
rematerialising a text — and the answer was exact:

| subject | peak | floor | excess | rematerialised |
|---|---|---|---|---|
| 4 KB | 126.7 MB | 126 | 0.7 | 4.8 MB |
| 52 KB | 607.7 MB | 126 | 481.7 | **487.4 MB** |
| 112 KB | 2303.7 MB | 126 | 2177.7 | **2176.5 MB** |

To within 0.05%. Not a distribution of small inefficiencies — one thing:
24,350 copies averaging 89 KB, which is the source text, rebuilt over and over.

Giving texts an address drawn from the same cursor `__heap-save` reads made
memory flat in subject size, made three subjects that died at 4 GB peak at 145,
and made `Parser` three times faster. The copies were work as well as bytes.

## And the same bug, in someone else's arm

`codexir` reads the IR wire, which no existing arm does — `codexzig` consumes
it, safari consumes the program. On its first day it disagreed with the Rust
interpreter on one field, and the disagreement was systematic: every effect
label in every compiled program collapsed to the same one. A six-line program
using only `print-line-uni` reported its row as `Task`, a name from the builtin
table it never mentions.

The zig plug's `cx_address_of` is heap-relative, and `.rodata` is below the
heap base, so every string literal answered **0** — the same value the
empty-slice case uses to mean "no pointer". `mcopy-name-fresh` keys a `Name` on
that address and nothing else, so every literal-named name collided on one key
and the first one copied was adopted by all the rest.

The comment above that function describes the same failure as Finding 31:
*"answering a constant 0 made every object identical to every other one AND to
null, and the compiler reads that as an answer."* Fixed once; this was the
residue. It's PR 131 now, with three bootstrap rounds byte-identical and 35 of
35 corpus programs matching after.

**Two arms, the same conceptual error, found within hours of each other.** One
answered in the wrong coordinate system, the other reused the sentinel. Both
because `address-of` looks like a debugging aid and is actually something the
compiler computes with.

## What the profile says about ambition

Once there was a real profiler, the self-compile stopped being mysterious:

| phase | share |
|---|---|
| LEX | 0.9% |
| PARSE | 1.3% |
| DESUGAR | 0.1% |
| SCOPE | 20.4% |
| **CHECK** | **73.5%** |

Eighteen minutes, forty-five billion steps, and it never reached LOWER. And
`perf` says half the time is `eval` + `apply_spine` + `eval_tail` — the
tree-walker floor. Removing *every* allocation would be about 1.15×. There is
no tuning that makes this fast; there is only a different execution model.

Which is worth saying plainly: **the self-compile is a stress rig, not a
capability.** Nothing depends on it. What it produced was findings elsewhere —
the durability bug, the page-per-byte lookup, the shadowed builtin, the
quadratic in cite resolution. It breaks in informative places, which is the
whole job of a stress rig.

It also sharpens the case for the road not taken today. Everything we fought is
the cost of *interpreting somebody else's compiler*. A native `check` and
`lower` pays none of it, and produces IR independently rather than reproducing
Cobblestone's by construction — which the interpreter arm can never do, however
fast it gets.

## The pattern

Every one of my four confident hypotheses was refuted by a measurement, usually
within minutes of the measurement existing. Every one of those measurements
came from an instrument built that day, and each instrument was built because
the previous guess had already failed.

The order that worked, in retrospect:

1. Build the instrument.
2. Let it kill the hypothesis.
3. Build the next instrument out of what the corpse showed you.

The `text-contains` mistake is the one I'd keep. It wasn't a slip — I checked
the thing that was easy to check (does a builtin with this name exist) instead
of the thing that mattered (what does this call site resolve to in this
bundle). And the system had already told me the answer, in a diagnostic I had
configured myself not to see.

Instruments beat intuitions. Diagnostics you've silenced beat both.
