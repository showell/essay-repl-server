# Three canaries, one word, and where the middle end lives

*2026-09-04. Fourth in a series about retiring the ladder.*

The last essay ended by saying the canary deserved its due and a name. Looking
properly, the reason it never got either is that **"canary" names three
different instruments**, and they answer three different questions. Untangling
them is most of the work.

## What is actually there

**`sweep_canary.sh`** — the cheapest rungs, fail-fast, stop at the first red.
Budget: two to three minutes. Its whole identity is answering *"did I just break
the emitter."* It is a subset of the ladder, same instrument, fewer rungs.

**`census_canary.sh`** — five to seven corpus programs chosen so that between
them they call every builtin a change touched. Minutes. Its question is
different and sharper: *"did we break something the ladder cannot see."* Its own
header says why that is a real question:

> The ladder's twelve units are blind in places the corpus is not: `address-of`'s
> real call sites are rooted in `opening.codex`, which no rung can bundle;
> `text-replace` has zero call sites in any unit.

**The seed canary** — one unchanged subject, compiled by two seeds on bare metal,
five seconds a side. Its question is *"did the release change anything, and
where."* This is the one from Update 53 that called the shape of a multi-hour
sweep before the sweep ran.

Three questions: *did I break it*, *did I break something my instrument is blind
to*, *did the world move under me*. One word, and no file says which one it
means.

## The seed canary is a controlled experiment, and that is why it worked

The Update 53 run is worth reading closely, because the design is doing all the
work and none of it is about being small.

One subject: `codex/test/plug-oracle-arith.codex`, **unchanged between U52 and
U53** — so the seed is the only variable. Both seeds, same host, same flags,
bare metal both times. Five seconds each. What came back was not a pass/fail but
a shape:

> Diagnostics BYTE-IDENTICAL (14 lines, same codes and positions); map same 189
> rows, 2 bytes; image 1,552 bytes LARGER and diverging from byte 9.

Diagnostics unmoved, map unmoved, image moved. From which: *expect the x86 and
image truths to move and nothing else.* And that is what the full sweep found —
`ir_to_x86_on_fib`, `ir_to_x86_on_cce` and `passes_to_x86_on_mid` moved, while
`lir_to_x86` and `passes_to_x86_on_arith` held.

**The prediction was not luck and it is not a small-sample trick.** A seed change
moves things systematically: if the emitted image differs, everything downstream
of emission moves together and everything upstream does not. One probe placed
where all three layers are visible at once samples the whole distribution. The
sweep's job was never to find out *whether* something moved — it was to say
*what*, and it took hours to say what five seconds had already implied.

It also caught something the sweep structurally could not: `seed_identity.py` did
not recognise the new release's note — "the second release form it has needed
teaching, and the canary is where it should be caught." A tooling gap surfaces at
the moment you first point the tooling at the new thing, not three hours into
using it.

## The census canary's first version was nearly useless, and the fix is the lesson

This is the part I would carry even if every script died.

The first version chose its programs on one criterion: *calls a builtin the
change touched*. Sixty-one of the corpus's 572 qualified, seven were picked, and
then:

> five of its seven turned out to be blocked by unrelated gaps (`atomic-*`,
> `process-*`, `poke-16`, `map-list`, `bit-not`), so **it delivered two verdicts,
> not seven.**

A canary is a sample, and a sample whose members cannot answer is not a small
sample — it is a differently-sized one you did not know you had. The fix was a
second criterion: the program must also **transpile clean**, because "a program
the emitter cannot translate never runs and covers nothing." Twenty-eight of the
sixty-one passed both, and the set is drawn from those.

Then a third idea, which I think is the sharpest thing in the ladder:

> Four of the five are expected to MATCH, and were chosen that way: **a rung that
> is red before you start cannot tell you anything by being red.**

The set carries both polarities on purpose — four expected to match, one
(`shadow-builtin-fold`) expected to differ. So it can detect a regression *and*
detect a spurious fix. A monitoring set that is all-green-when-healthy can only
fail in one direction; one that includes a known red can tell you when something
got quietly "fixed" that should not have.

Those three rules — **can it answer, can it answer both ways, is exactly one
thing varying** — are what makes a cheap probe worth more than the expensive
thing it precedes. None of them is about being fast. Fast is the consequence.

## So where does this live?

Steve's question was whether the canary belongs in a repo about the middle end
and types, and whether `codex-qemu` is now the right size. I think
`codex-qemu` is the right size, and that the canary does not go there — but I do
not think the answer is a new repo either, and it is worth saying why.

**The gap is real.** Lay the five repos against the compiler and one region is
uncovered:

| | covered by |
|---|---|
| front end | rust-codex-compiler — independently, on 1,012 programs |
| **types** | **nothing** |
| **IR passes** | **nothing** |
| emitted artifact | the two transpilers' fixed points |
| machine code | codex-qemu |
| whole-program values | safari, and the corpus's 1,239 `.expected` files |

Today's finding sits exactly in that hole: the plug-built compiler types every
comparison `error` where bare metal says `boolean`. It was not found by a rung —
fourteen of them had been reporting it backwards for an Update — but by diffing
two IRs. Types and passes are *what IR carries*; a differential over IR is the
instrument for both.

**And the instrument already exists.** `canon_ir.py` canonicalises IR so two
front ends can be compared honestly, and its reason for existing is precisely
the middle end:

> The IR text publishes the type checker's UNIFICATION VARIABLE NUMBERS …
> across the banked corpus there are 8,841 `(tvar …)` and 18,228 rows … Those
> numbers are a function of the ORDER in which the checker allocated fresh
> variables over the whole program, not of the program's meaning.

Three arms can produce IR today: bare metal through the seed, the plug-built
`codexir` at 0.09 seconds, and rust-codex-compiler for the preamble. That is a
differential waiting to be run.

**But it should not be a new repo yet**, and the reason is the one this whole
exercise is about. `rust-codex-compiler` already owns IR. Its stated rule 1 is
*"canonical equality is the gate; byte-identity is a ratchet"* — that is
`canon_ir.py`'s thesis, already written down there. It already carries
`irdump grade`, `gradewhole` and `defs` against 1,012 golds. A directory in it
that adds "and here is the same subject's IR from the other arms" is a
capability it half has; a new repo is a second place to keep a canonical-form
implementation in step.

The ladder became a repo when the ladder was the project, and that is exactly
the mistake worth not repeating. **Split when there is a second reason to
exist, not in anticipation of one.**

## What I would actually do

**Give the three canaries three names**, because they are three instruments:
*did I break the emitter* is a smoke test, *did I break what my instrument
cannot see* is coverage, *did the world move* is a control. Only the third is a
canary in the sense anybody means by the word.

**Carry the control.** One unchanged subject, two trees, everything else held,
and report the shape rather than a verdict — diagnostics, map, image, separately.
It is seconds, and it tells you which of the expensive things is worth running.

**Carry the three selection rules, not the sets.** The corpus moves, the
builtins change, the sets rot. *Can each member answer? Can the set fail both
ways? Is exactly one thing varying?* Those survive.

**Put the IR differential in `rust-codex-compiler`**, where the canonical form
and the golds already live, and leave `codex-qemu` alone. It has four subjects,
four checkers, one finding and a sentence that describes it. That is the size a
repo should be when it is done, not a stage on the way to being bigger.
