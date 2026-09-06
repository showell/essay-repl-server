# Twenty-eight programs, four hosts

There is a version of this week that reads as a retreat. We had seventeen
hundred corpus programs and a sweep that took most of a day and tied up the
box while it ran. Now we have twenty-eight programs and four scripts that
finish in under a minute. By the count of programs under test we gave up
ninety-eight percent of the corpus.

By the count of *questions we can answer today* we gained everything, and the
reason is worth writing down, because the instinct that produced the seventeen
hundred is a good instinct and it was still wrong.

## What the big corpus was actually buying

A corpus of seventeen hundred programs somebody else wrote is a wonderful
thing to own. It is not chosen by what we happened to be working on, which
means it can surprise us, and the whole value of an oracle is that it can
surprise you. That argument is correct and I would make it again.

The trouble is that the argument is about *coverage*, and coverage is only
half of what a test suite is for. The other half is **turnaround**. A gate
that takes six hours tells you the truth about your compiler six hours after
you ask, which means you ask about three times a day, which means you spend
the day guessing in between. And guessing is where the bad hours go. The
week's most expensive mistakes were not wrong code; they were a bisection run
against a contaminated set of rungs, a claim that the native arm was flat when
it was under its own noise floor, and a cost measured on the wrong workload.
Every one of those is a guess that a faster gate would have killed in
seconds.

So the twenty-eight are not a smaller version of the seventeen hundred. They
are a different instrument. The seventeen hundred answer *is our compiler
right about programs nobody chose for us*. The twenty-eight answer *did the
edit I just made break anything*, and they answer it before I have finished
reading the diff. You need both. You can only afford to run one of them
constantly.

## Four hosts, and why the fourth one matters most

The same twenty-eight programs now run four ways, and the design principle is
that each script holds a different thing fixed:

| script | held fixed | varies |
|---|---|---|
| `run.sh` | nothing | the whole Rust stack, end to end |
| `ir.sh` | the compiler's source | the host that interprets it |
| `wasm.sh` | the frontend | the wasm plug |
| `native.sh` | nothing upstream | Rust compiling Codex itself |

`ir.sh` is the purest of the four and the least likely to fail. It takes
upstream's frontend, has our Rust interpreter *interpret* that frontend to
compile a program, and has `codexir` — the very same frontend, compiled to a
native binary — compile the same program. Two hosts, one compiler, one source.
Any difference is the interpreter's and there is no third explanation. That is
a beautiful gate and it has been green for a while now, which is exactly what
you want from a gate that pins down your foundations.

`wasm.sh` went green on the first run this week: twenty-eight of twenty-eight
emit a module, assemble under `wat2wasm`, and produce the expected output.
Zero refusals, zero traps. That is worth a moment of pleasure and then a moment
of suspicion, and the suspicion is the honest part: **the twenty-eight were
curated by running them, so of course they run.** They were selected for being
programs an interpreter could get output from quickly. Programs that name
hardware — `port-out-32`, `read-mmio-32`, the gpu and uefi builtins — never
made it through that filter, and those are precisely the programs where the
wasm plug declines. A clean sweep over a population selected for cleanliness
is a weaker result than a clean sweep over a population selected by somebody
else. It is still a real result. It is not the result it looks like.

I did tamper it before believing it — one text literal in one IR document,
`ok` to `NOPE`, and the run stage reported `DIFFER`. A green gate that has
never been shown to go red is not evidence, it is decoration.

## The fourth host is where the honesty gets interesting

`native.sh` is the one with no Codex compiler anywhere in the loop. Rust reads
a `.codex` unit and produces IR itself, and we ask whether it lands on the
document upstream's own frontend produces from the same bytes. This is the
arm that could not exist a month ago, and it is the arm the whole
independent-oracle project is for.

Seventeen of twenty-eight agree byte for byte. I expected far worse — I said so
before running it. Eight refuse, and a refusal names its own hole: three
`FieldAssign`, two `literal kind NumLit`, two if-branch unifications, one
`Lambda`. Those are honest gaps in a front end that is still being built, and
each one is a morning of work rather than a mystery.

Three *differ*, and the three have three entirely different causes, which is
the most encouraging thing in this whole note.

**One is off by a single character.** `foreword-concurrent` produces a document
of exactly the same length as upstream's, differing in one place: an effect row
carries id `848` where upstream says `847`. Somewhere we mint one row that
upstream doesn't, or upstream mints one first that we mint later. The counters
are graded, so a single extra mint shifts everything downstream by one and the
document stays the same size. This is the kind of defect that would be
invisible in any test that compared behaviour instead of bytes.

**One is six bytes and is a real inference gap.** `secrets-name-sort` has a
record literal with an empty-list field. Upstream writes `(list-expr (elems)
text)`; we write `(list-expr (elems) (tvar 352))`. The record's declared field
type is `List Text`, and upstream lets that flow inward to resolve the empty
list's element type. We leave it as a type variable, because we type the
literal before we look at where it's going. Six bytes of diff, one missing
edge in the inference graph.

**And one is not a bug at all.** `negation-abutment` differs by fifteen hundred
bytes and emits eight definitions where upstream emits three. For a while I
read that as a lowering disaster. It is the opposite: upstream's `opening`
body never mentions `one`, because upstream *inlined* it.

```
show (two 1 -2)   →  (binary add-int (int-lit 1) (int-lit -2))
show (one -5)     →  (int-lit -5)
show (neg-var 3)  →  (apply (apply (name "two" …) (int-lit 1) …) …)
```

Upstream inlines a definition at a call site whose arguments are all literals,
one level deep, and then prunes the definitions that leaves unreferenced.
`neg-var 3` inlined to `two 1 -3` and stopped, which is why `two` survives.
Notice it inlines but does *not* fold: `1 + -2` stays a binary add rather than
becoming `-1`. That is a specific, discoverable design decision, and we found
it by diffing rather than by reading, which is the whole argument for having an
independent implementation in the first place. We did not know upstream had an
inliner. Nobody told us. The diff told us.

Three differences, three causes, none of them the same shape. That is a
compiler with distinct remaining problems, not a compiler that is broadly
wrong. A single systematic error — every effect row off, every empty list
unresolved — would be one bug wearing many costumes. Three unrelated causes in
three programs means we are down to the tail.

## The control that lied

The first time I ran the native arm I got something very different: twenty of
twenty-eight came back `no-diagnosis`, meaning **the oracle refused the
program**. Twenty of our carefully curated, known-good programs, rejected by
upstream's own compiler.

That is not a result. That is a broken control, and the tell was that `ir.sh`
had `codexir` emitting clean IR for all twenty-eight the day before. Two gates
cannot disagree about whether the oracle works.

The cause: the compiler's own `ladder/native.py` runs `cite_resolve` on its
input, which is exactly right for a raw corpus program — that is how a program
gets its cited chapters. Our units are *already* resolved and frozen. Running
the resolver again duplicated every cited chapter; `normalize-eq` went from
4256 bytes to 7965. The oracle halted on the duplicate definitions, correctly,
and reported six errors. `native.sh` skips resolution and gets seventeen
agreements.

I want to dwell on this, because the failure mode is more instructive than the
fix. **A broken control produces a plausible number.** Twenty of twenty-eight
failing is not an absurd result for a front end this young — it is roughly what
I had predicted out loud. If it had come back as twenty-eight of twenty-eight
failing, or as a crash, I would have investigated immediately. It came back as
a believable disappointment, and a believable disappointment is the hardest
kind of wrong answer to catch, because it agrees with you.

The thing that caught it was not cleverness. It was having a *second gate*
whose result contradicted the first. `ir.sh` said the oracle works on these
bytes; `native.py` said it doesn't. Those cannot both be true, and the
contradiction is what forced the look. This is the actual argument for having
four scripts instead of one good one: not that each covers different ground,
though it does, but that they **check each other**. An instrument you cannot
cross-check is an instrument you have to trust, and trust is not a property you
want in a measuring device.

## What the twenty-eight can't do

They cover the node kinds thinly in places we know about — one `char`, two
`ty:sum`, two `ty:con`, three `lambda` across the whole set. They were selected
for running fast and producing output, which biases them away from exactly the
programs that stress a compiler: the big ones, the slow ones, the ones that
name hardware, the negative tests that are supposed to fail. `wasm.sh` going
green says less than it appears to for precisely this reason.

The honest framing is that the twenty-eight are a **regression suite**, not a
conformance suite. They tell us we haven't broken what worked. They cannot tell
us we're right. The seventeen hundred can tell us we're right, and they will
still be there when we want that answer badly enough to spend a day on it.

What we gave up was the ability to be surprised. What we bought was the ability
to iterate — and iteration is what turns a known gap into a closed one. The
eight refusals in `native.sh` are each an afternoon. With a six-hour gate they
would each have been a week.

## Where this leaves the two threads

Thread A — Rust interpreting upstream's frontend — is green on all four gates
over the curated set and has been for long enough that it is now infrastructure
rather than a project. It is what `ir.sh` and `wasm.sh` stand on.

Thread B — Rust compiling Codex natively — is at seventeen of twenty-eight with
eleven named obstacles, three of which are single-cause diffs and eight of
which are unimplemented forms. That is a much better position than "a front end
that mostly doesn't work," and I would not have described it accurately without
running the thing.

The inliner is the interesting discovery and I don't think we should chase it
yet. It is an optimisation, we can reach byte-identical output without it on
twenty-seven of twenty-eight programs, and implementing an inliner to match
somebody else's inliner exactly is a large amount of work for one program's
worth of agreement. It goes in the notebook. The row-id off-by-one and the
empty-list element type go on the bench.
