# What Is In Flight

*2026-08-26, late. A status note written long on purpose: what is running,
what is written but unbuilt, what has been sent to Damian and what we owe
back, and — the part that matters most tonight — which of our own claims
are measured and which are still resting on something we have not checked.*

## CORRECTION, 22:55 — the biggest claim in this note is retracted

Everything below was written before Damian's lane replied. They cannot
reproduce our type-checker finding, with a well-controlled non-repro:
`fa (x) (y) = let g = fa in g x` is refused with CDX2001 at their head
and at four seed revisions back to about 2026-08-20, and a positive
control (the same alias at *full* arity) compiles at all four, so those
seeds are not simply refusing anything with an alias in it.

They are almost certainly right, and the fault is an instrument error of
mine. **The compiler I measured with is not the reference compiler.**
`native/codexir` is built by bundling the subject, compiling it with the
seed, pushing that through our plug, and building the emitted zig — it is
*the compiler compiled through our own zig backend*. Every diagnostic in
that probe run came out of a type checker our emitter produced. I
reported a soundness hole in their language on the strength of our arm
disagreeing with their arm, without checking which arm I was standing on.

The corrected reading, if it holds, is worse than what I reported: not a
hole in Codex's type checker, but **our backend miscompiling that type
checker until a diagnostic stops firing** — a silent wrong answer in the
compiler we build, which is the precise thing this whole apparatus exists
to catch.

The settling measurement is the same program through the seed on bare
metal. It is a virtual-machine job and it is queued behind the sweep that
is running as I write this.

Read the rest knowing that. The section below titled "Read this part
first" was already warning that a different, smaller part of this claim
was unverified; it was warning about the wrong thing.

## Read this part first, if you read nothing else

**One thing we sent may be wrong, and the experiment that settles it has
not run.** The PR 87 probe report went out saying that a *let-bound alias*
is what lets a definition slip a type error past the checker. That
attribution rests on the Cobblestone lane's "arm A" refusing — which they
measured on their tree, not on ours. The control that isolates the
variable (`findings/probe-pr87-direct.codex`, the same definition with the
alias removed) was written *after* the report went out and has not been
run, because the box has been busy since.

If the control also compiles clean, our attribution is wrong — and wrong
toward a *larger* claim, not a smaller one: not "an alias defeats the
check" but "the return-type check does not run at all." That would need a
prompt correction rather than a quiet one. I have recorded this on the
sent artifact itself (`outbound/SENT-pr87-probe-results.md`) so that
anyone re-reading it meets the caveat before the conclusion.

That is the honest headline. Everything else below is in better shape.

## What is running right now

One chain, `~/runs/20260826T222007Z-f17-f54`, on codex `cab52a35`.

```
leg0 natives      GREEN  5m06
leg1 tvar-matrix  GREEN         zig reports the plug's own marker
leg2 corpus       GREEN  6m47   match 263 -> 269, refused 30 -> 24
leg3 codexzig            running
leg4 roc-ports
leg5 sweep                      ~26 min, the long one
```

It is deliberately pinned *below* our latest commit. Three emitter changes
were written tonight; two are on this chain and the third is not, and the
reason is worth explaining because it is a habit rather than a one-off.

## Why a chain measures fewer changes than we have written

A verification chain costs about fifty minutes on a two-CPU box. The
temptation is to load every change onto it. The discipline is not to,
because a chain that measures three things at once measures none of them
if two interact.

The rule we have settled into: **changes may share a chain when their
failure signatures are disjoint.** Tonight's two share it because one
moves programs that say `invalid operands: 'void' and 'void'` and the
other moves programs that say `shadows declaration of` — different
messages, different programs, no overlap. The third change (a type
recovery rule) moves the *same* programs an earlier fix governs, and it is
the least-reviewed code written all day, so it waits.

`sandbox.sh` takes a codex ref as its fourth argument, which is how a
chain excludes a commit that is already on the branch. I did not know that
this morning; it is worth knowing.

## The one thing that made tonight work

Before each build, I write the predictions into the finding — numbered,
specific, with numbers attached — and commit them *before* the chain
starts. Not as ceremony. Because a result you have not predicted is a
result you will rationalize.

It has been checked four times now and been wrong twice, and both wrong
times taught more than the right ones.

**Wrong the first time (finding 53).** I predicted that fixing the thread
entry would move 40 programs off one error but that most would *not* reach
a passing state, because those 40 had never had their own emitted code
examined by anything — the failure happened inside zig's standard library
before a line of the subject was analyzed. I braced for roughly 25 new
failures as they were looked at for the first time. Exactly **two**
appeared. The hedge toward pessimism was simply wrong, and the fix was
cleaner than its author expected.

**Wrong the second time (tonight, finding 54), and this one is better.**
I predicted two programs would start passing once we renamed two variables
inside our own runtime prelude. They did not. The error moved one line and
changed kind:

```
before   dns-answer-count.zig:22:11  local constant shadows declaration of 'l'
after    dns-answer-count.zig:26:15  function parameter shadows declaration of 'l'
```

The reason is a flaw in how I measured the problem in the first place. To
size it, I had extracted every `const` and `var` binding from our prelude
and found 45 names that a user program must not use. I never looked at
**function parameters**, which shadow in exactly the same way. The real
surface is **66 names**, and the nineteen I missed are worse than the ones
I found:

```
a, alignment, bits, bytes, ctx, d, e, h, hi, len, lo, memory,
new_len, path_cce, ra, sep, vs, x, y
```

`x`. `y`. `len`. `ctx`. A Codex program that defines a top-level function
called `x` cannot be compiled by this plug, and until an hour ago nobody
knew that, including me after I had supposedly measured it.

The fix moving the error to the *next shadow of the same name* is the
loudest possible way to be told your measurement was incomplete. If I had
not written the prediction down, "two programs did not move" would have
read as a dull partial success instead of as a correction.

## What actually landed tonight

Numbers first, across three chains, every one green on all six legs:

```
corpus match     183  ->  263  ->  269
corpus refused   112  ->   30  ->   24
```

The defects behind that:

**`show` implemented one of five cases.** Codex's `show` takes anything
and returns text, and the reference implementation picks the conversion
from the argument's type — text shows as itself, a Boolean as `True` or
`False`, floats convert two different ways, everything else becomes an
integer. Our plug implemented the last arm and routed all five through it.
That was **42 of 113 failures**, the largest single class in the corpus,
and it had been sitting in our own output since the plug was written.

**A refusal that ate its own message.** When the emitter cannot produce a
type it emits a marker — a compile error carrying a sentence explaining
what it could not do. We fixed one such case and the sentence still never
appeared, because refusing an expression killed the last use of a function
parameter, and zig's unused-parameter check fires against the signature
*before* it analyzes the body. We wrote the right thing into a file nobody
was shown. The mechanism to prevent that already existed and was asking
the wrong question: it consulted the *input* to decide whether a parameter
was still used, when the deciding fact was in the *output*.

**A thread entry that could not return a value.** Every emitted program
runs its entry point on a thread, to get a bigger stack than the default —
the same workaround the C# backend uses, for the same recorded reason.
Zig requires a thread entry to return nothing. Forty corpus programs
declare an entry that returns a value, and that value is the program's
*answer*, not a status code. All forty failed inside zig's standard
library before a line of their own code was read. Fixed, and all forty now
pass.

**Boolean pattern matching.** A `when` on a Boolean arrives at the backend
carrying the *spelling* `True`, not a number, and every backend has to
decode it. Ours emitted the spelling straight into zig, which has no such
identifier. Two programs — and the requirement is written down in a test
the compiler ships, whose header explains that some backend once got this
wrong and silently returned 100 instead of 150.

**Units.** A unit family (`Length = unit family Millimeter`, with scale
factors) is integer-backed, and a value of that type *is* its base-unit
integer. Our plug mapped every unit type to `void`, erasing the payload —
while the arithmetic around it stayed perfectly correct. The emitted
program computed all four of its expected answers and then failed to
compile because the values were typed `void`. One arm of one dispatch.
Six programs now pass.

## What is written and not yet built

Three things.

**A type recovery rule.** Five ported programs fail because a lambda whose
type no declaration pins reaches the backend with its parameters marked as
errors. Reading the actual wire showed the hypothesis was too broad: two
of three parameters arrive correctly typed, and only the *function-typed*
one is missing. The answer is in the same data twice — once in the
lambda's own body (which reads the parameter with a known type while the
signature says error), and once in the declared type of the function the
body calls. Both walks are written. Neither is built.

I re-read it before it ever compiled and found a gap in my own work: I
guarded against `let` and nested lambdas rebinding a name, on the grounds
that reading a *different* variable's uses is a mistake we have made
before — but a match branch also binds names and I did not guard that. The
consequence would be a *wrong recovered type* rather than a refusal, which
is the bad direction. It is recorded in the code's own prose.

**Two prelude renames**, which we now know are insufficient (above).

**The class fix for the shadowing**, which is not written: renaming 66
identifiers inside our runtime prelude, plus a check that re-derives the
list from emitted output so it cannot rot — and that check must count
parameters, or it will certify the same short list I certified.

## What is open and unfixed

The corpus has 24 failures left, and they concentrate:

```
11  unrecognized type names emitted verbatim   findings 17(B) + 55
 5  concurrency: closures, tasks, fork/par
 1  a self-recursive generic type              finding 48
 1  a runtime panic nobody has looked at
 6  singletons
```

The eleven are one `else` branch. When the backend meets a type name it
does not recognize, it emits the name. That covers unit families
(`Frequency`, `Timestamp`) *and* a source-level type variable (`a`) — the
same line, the same fallback, differing only in what the name means. And
that path takes no scope and has no refusal, so every guard we built today
for type variables walks straight past it.

## What is with Damian, and what came back

The Gmail channel to his agents opened today and it has already been worth
more than the pull requests.

**We sent a cross-plug lead.** Our reasoning was that most of our findings
are not about zig at all — they are about a contract the intermediate
representation carries that each backend decodes for itself, so a backend
that decodes it wrong is wrong in a way unrelated to its target language.
We named one instance and hedged it twice, because we cannot run C#.

It came back confirmed in **three** backends — C# (at three sites, not the
one we named), JavaScript (which we did not predict at all), and their own
copy of the zig backend, where our fork had our fix and their copy did
not. All reproduced by *running* the programs rather than reading them.
All fixed, credit to us in the changelist.

The sweep they ran on our suggestion then found **two defects nobody had
reported** — including a JavaScript bug where character literals were
missing a numeric suffix, so every character branch silently fell through.
That is a *silent wrong answer*, the class we care most about and the one
a source read does not find. It was only reachable because they measured
by execution.

The lesson I am taking: we hedged our *confidence* correctly and were
still badly low on *scope*. Those are different things, and only the first
was hedged.

**We asked three questions about an old pull request**, and the answers
landed on us rather than on the row we were defending. The reproducer in
our own PR was the wrong shape — it compiled precisely because it was
*not* the thing we claimed to be testing. And the safety property we had
attributed to a code path turns out not to live there at all: that path
is blind to the thing we thought it checked, and the real protection is a
type-checker rule one stage earlier. One of our own findings blamed the
wrong component as a result, and has been re-framed.

They accepted our re-scoped version and are declaring the invariant in the
developer rulebook rather than as a code comment — a better outcome than
we asked for, since a comment rots and the rulebook is what a backend
author actually reads.

## The mission changed today

Steve's call, and it reorders the queue: **closing the plug's holes is now
a first-class goal alongside finding defects.** Hunting is turned down —
still the thing that produces the value, no longer the default activity. A
known hole with a clear fix outranks a new hunt.

The reasoning that convinced me is arithmetical. Tonight produced roughly
six new findings in an evening. Eight pull requests landed in the last
release cycle and that took weeks. Findings arrive faster than they can be
measured, written up and merged, so adding to the pile is worth less than
draining it. And each hole closed unmasks the next defect — three times
tonight, a fix's only visible effect was to reveal something that had been
standing behind it.

## What happens next

1. The chain finishes; read leg3, leg4 and the sweep against the recorded
   predictions.
2. Run the four probes — including the control that may retract part of
   what we already sent.
3. The eleven-program `else` branch, which closes two findings at once.
4. The 66-name prelude rename, with a check that re-derives the list.
5. The recovery rule, after its match-binder gap is closed and preferably
   after a cold read, since it is the most intricate thing written today
   and it was written fastest.

The thing I would most like to be true by morning is that the control
probe confirms what we sent. The thing I would most like to *know* is
whether it does.
