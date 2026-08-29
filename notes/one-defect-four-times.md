# One defect, four times: where the findings stand

*2026-08-29 evening, written while the second compiler PR measures. Plain
terms, because the interesting thing here is a pattern rather than a
mechanism.*

## The thing to understand first

Codex compiles in stages. A **type checker** works out what type everything
is, and then a **lowering** stage writes that down into an intermediate form
called the IR — the wire that every backend reads. Our zig plug reads the
wire. Bare metal reads the wire. Everyone downstream reads the wire.

So the wire is a report. And the defect family we keep finding is always the
same sentence:

> **The checker worked out the answer. Nothing wrote it down.**

The type is not missing. It was computed, correctly, and then the lowering
stage failed to carry it across. Downstream sees a hole where an answer
should be, and does something plausible with it — which is the dangerous
part, because a hole that gets filled in plausibly does not look like a bug.

That is the whole family. Once you see it, the individual findings stop being
separate puzzles.

## The first one, and why it set the pattern

**H2 / PR 93** was a lambda — an inline anonymous function. The checker had
solved what its parameters were. The IR carried none of it, so the plug saw
`error` where a type belonged.

The root cause was almost silly: the lambda node in the syntax tree had **no
source position**. Every other kind of expression carried one. The checker
files its answers under "the thing at this position", so with no position
there was no way to ask for the answer — it had been filed under an address
that nothing could look up.

That landed upstream, and the fix was named `lambda-expected-ty`: *when the
context tells you nothing, go ask the checker what it recorded here.*

Then it happened again. And again.

## The same shape, three more times

**Finding 57 — a branch join forgets what both branches knew.**

An `if` has two arms. Both arms come back with a concrete answer. The `if`
itself comes back with a variable — an unknown. Straight from the wire:

    then-branch   Step(Integer)     concrete
    else-branch   Step(Integer)     concrete
    the `if`      Step(tvar 16)     a variable

Both branches agree, and the join throws it away. This blocks three of the
Roc ports we vendored, all failing with "unresolved type variable".

The uncomfortable detail: the machinery to prevent this **already exists** in
the compiler and was not wired to this site.

**Finding 58 — an empty list has nothing to look at.**

Write `[]` and there is no element to read a type from, so the type must come
from context: the function you pass it to declares one. The checker does that
unification correctly. But the empty-list case never *records* its answer, so
the wire carries `list of error`.

    __lam_0  xs   (list error)

The declaration is one line further down the same file. Nothing was hard here
either; the answer just was not written down.

**Finding 59 — the context is trusted when the context is nonsense.**

A non-empty list `[a, b, c]` takes its element type from context. Fine — until
the context is a *variable belonging to somebody else's scope*. At a
polymorphic call, the "context" is the callee's declared type with its own
type variables still in it, and those variables mean nothing where you are
standing. The literal's own elements were correctly typed the whole time and
were ignored.

This is the biggest of the three by reach: it blocks `hamt-test`,
`kvstore-test` and `list-test` outright, and is half of what blocks two more.

And it is, precisely, **the lambda defect one node over**. The compiler's own
prose under `lower-lambda` explains that a lambda "used to record the EXPECTED
type it was handed, which at a polymorphic call is the callee's declared
parameter with its type variables still in it." They found that, fixed it for
lambdas, and wrote down why. A list literal does the identical thing and has
no equivalent guard.

## The fourth thing they asked for, which we are not sending

Update 53's release note asks for **four** fixes and reserves them for us in
its register, with the instruction `DO NOT TAKE THESE UP` — they have
suspended their own work waiting.

We are sending three. The fourth was an instance-method span site, on the
theory that it was another instance of the same family. **We built it and
measured it, and it does nothing.** No type moved. Both target programs stayed
broken. And it was not even free: it shuffled internal variable numbering, so
it would add noise to every future diff while buying nothing.

We reverted it, on a standard they themselves set: *a fix that nothing
measures waits for an instrument.* This one had an instrument and failed it.

Telling them that is probably worth more than the three fixes, because a
reservation is sitting on it and nobody is working on it.

## The one we found today, which is a different animal

**Finding 68** came out of running the whole 580-program corpus against
Update 53 — the first time anything had, since the release.

    let total = (\xs base step -> fold-loop xs base step 0) [1,2,3,4] 0 (\acc x -> acc + x)

`total` is a number. The IR says two different things about it in one line: the
binding calls it a **three-argument function**, and the use site five words
later calls it an **integer**. One name, two types, in the same statement.

Same family — a type that should have been carried — but with a twist that
matters:

**Both arms agree on the wrong answer.** I checked, because the first version
of the IR I read came from *our* compiler, which is the compiler as rendered
by our own plug. Reporting from that has cost a wrong report to Damian before.
So I ran the same program on bare metal through the seed, and the seed's own
wire carries the identical contradiction.

That has a consequence worth stating plainly. **The fourteen rungs — the whole
double-compiling ladder — cannot see this, by construction.** The rungs
compare our arm against bare metal and demand byte-identity. A defect both
arms share is invisible to a comparison between them. It showed up only
because the corpus *builds* the emitted output, and the zig compiler rejected
it: `expected 'i64', found a function`.

That is the clearest case I have seen for why we run both instruments. The
rungs answer "do the two arms agree." The corpus answers "does the answer
work." Today those were different questions and only one of them was being
asked.

## Where everything actually stands

Two PRs are open with Damian:

- **PR 99** — a comment in the zig plug's prelude table that says "do not
  hand-edit, regenerate instead", naming a generator that is in *our*
  repository and a source file that no longer exists. It is unfollowable in
  both halves, and it is our error: it shipped with our own PR 98. It cost us
  a wrong turn adding the real conversions.
- **PR 100** — the f64 real conversions themselves, which safari-codex needs.
  Measured: 328 corpus programs clean against 326, zero regressions, and both
  arms agreeing line-for-line on a new test whose answer was read off bare
  metal with a control alongside it.

In flight right now: the **second compiler PR**, findings 57/58/59, rebased
onto Update 53 and measuring. The prediction is specific — the five programs
these are supposed to unblock all sit outside the baseline's clean set, and if
the fixes work they should appear, with nothing else moving.

Still owed: writing up finding 68, and settling whether Update 53 introduced
it or whether it has been there longer.

## The part I would keep

Four instances of one sentence, found separately, over six weeks, by different
routes — a lambda, a branch join, an empty list, a list literal — and each was
diagnosed from scratch as if it were new. The register now says "same family
as COMPILER-30" on two of them, which is the beginning of the right instinct
but arrived late.

The general defect is not any of the four. It is that **the compiler has no
rule requiring a lowering site to carry what the checker solved**, so every
site is a fresh opportunity to forget, and forgetting is silent. The fifth
instance is out there. What would find it is not more diagnosis but a
property: for every expression the checker resolved, does the wire carry the
answer? That is checkable in one pass over the IR, and PRIORITIES has it
written down as a standing item nobody has built yet.

---

## Postscript, an hour later

Three things resolved after this was written, and one of them changes the
argument rather than just updating it.

**The second compiler PR is sent** — [#101][], with the measurement it was
waiting on: clean 326 to 330 on the corpus, zero regressions, `hamt-test` and
`kvstore-test` both matching, and `list-test` staying blocked exactly as
finding 59's "PARTIAL" said it would.

**`roc-fold-empty` is the interesting result**, and it is the one that changes
the argument above. The empty-list fix works — the program leaves `markers` —
and it lands immediately on finding 68. So finding 68 is not just a fifth
instance of the family, it is now the thing standing between a working fix and
a clean program. The register's claim that this program goes "markers to match"
was measured on the old base and no longer holds; the difference between those
two trees is Update 53.

**Finding 68 is filed** as [#102][], with the mechanism traced to the line: the
call-site name reference carries the lambda's own function type nested inside
its own return position, because `build-curried-fun-ty` prepended three
parameters to a type that already had them. Compiler, not plug — the seed
produces the same wire, so there is nothing plug-side to fix and a plug
"repair" would mean choosing between two types the compiler asserted in one
statement.

**And two of the findings I was going to work on next turned out to need
nothing.** Finding 61 is already fixed in Update 53, from our own issue-94
report — confirmed by output rather than source, since the emitted zig calls
`hamt_empty(i64)` against `fn hamt_empty(comptime T58: type)`. Finding 60's
code was dropped on purpose weeks ago, on the grounds that its rule had been
wrong twice and the second wrong version shipped a wrong answer into a build.
Its register entry had not said so in the header, so it was reading as
unfinished work. It says so now.

That last one is the small lesson of the evening: **a finding whose header does
not carry its disposition will be picked up again.** Three entries were in that
state today, and each one cost a few minutes of re-deriving something already
decided.

[#101]: https://github.com/damiant3/Cobblestone/pull/101
[#102]: https://github.com/damiant3/Cobblestone/issues/102
