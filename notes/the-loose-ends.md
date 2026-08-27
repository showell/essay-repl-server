# The loose ends, and which ones to cut

*For Steve. 2026-08-27, late. Written while the compiler-only sweep runs.*

---

## Why this is worth writing down tonight

We opened nine things today and closed four. That is a fine ratio for a day of
exploration, but the residue is not one pile — it is four piles that want four
different dispositions, and I think we have been treating them as one. The
useful move before sending anything over the wall is to say, for each loose end,
what it *is*: a shippable fix, an argument, a lead, or something to drop.

I will also say plainly where I think we should **cut bait**, because two of
these have already cost more than they will return.

## Pile one: three fixes that are done and want a PR

Findings 57, 58 and 59. Built, measured, corpus-checked, and Damian has already
said "send all four as the second PR; that is the word" — four, because at the
time I believed finding 64 was one of them and it was not.

These are not loose ends. They are finished work waiting on two things: the
mirror push (so they measure against seed `4341370C` rather than one he has
replaced), and the sweep now running, which is the first one taken on the
**release emitter** rather than with our four ZigEmitter commits in the tree.
That distinction is the cold agent's, and it was right: `README.md` says sweep
the release's emitter verbatim because the alternative measures a compiler
nobody ships, and every sweep we ran before this one had our plug fixes in it.

**Disposition: PR, as soon as the sweep is green.** Nothing here is a lead.

## Pile two: one architectural argument with four independent legs

This is the pile I think is worth an Issue, and it is stronger than any of its
parts.

**The pattern: a CST node too weak to carry what the source plainly says.**

1. **`LambdaExpr` had no span.** Every lambda in the language filed under
   file-id 0, so the checker's answer could never be looked up. That is
   COMPILER-30 and it has landed.
2. **`InstanceDef.type-name` is a `Token`.** `instance Showable (List Integer)`
   arrives as the bare token `List` — `parse-instance-type-head` returns the
   token after the paren and calls `skip-to-close-paren` on the rest. The
   argument is discarded at parse time and the node could not have held it
   anyway. The head type reaches the dictionary's NAME and never its TYPE.
3. **`ErrorTy` is two facts in one spelling** — the type-failure atom and
   `lower-let`'s no-expectation sentinel. Already in his rulings queue,
   deliberately unpatched on both sides.
4. **The IR carries instantiated types at call sites but not at definitions**,
   which is why `hamt_empty()` was emitted without its comptime argument while
   `hamt_set(i64, ...)` was fine.

Each of those on its own is a bug report. Together they are a claim about where
this compiler loses information, and the claim is testable: *the CST is the
narrowest part of the pipe, and facts the programmer wrote down die there.*
Damian's own IR-fidelity instrument — built from our essay's argument, before
our PR arrived — is evidence he already finds this framing useful.

**Disposition: one Issue, properly hedged, tonight.** Not a PR. Three of the
four have no patch attached and two of them shouldn't have one yet.

## Pile three: leads that are honest but unfinished

- **Finding 65a.** The instance-head fix works on plain classes and *adds a
  marker* on a superclass chain. Measured, reproducible, not understood.
- **The unconstrained-type defaulting question.** Two programs, and the right
  answer is upstream: the compiler knows whether a variable is free after
  solving and the wire should say so. We should not default in the plug, and I
  argued why at length.
- **Monomorphisation.** Three `iter-*` ports. The design question is settled by
  a measured fact — Codex permits polymorphic recursion, so the instantiation
  set is infinite in general and emitter-side specialisation cannot terminate.
  The emitter already emits `comptime T: type`. This is execution, not research.

**Disposition: the first two go in the Issue as leads, clearly labelled as
leads.** The third is ours and stays on our queue.

## Pile four: cut bait

I want to be direct about two.

**Finding 60 — the unused-`let` discard. Cut it.** It took three builds, its
rule was wrong twice, and the second wrong version shipped a *wrong answer*
into a build (`deck-bracket-contract` went `match → differ`). What it buys is
one Roc port. The third rule is correct as far as we know, but "as far as we
know" is doing a lot of work in a thing that has been wrong twice, and the
honest expected value of further work on it is negative. It is already reverted
from nothing — it is still on the branch. **I would drop it from the plug PR
entirely and keep the register entry as a record of the zig rule we measured.**

**Finding 63 — the discard's scope. Already parked, keep it parked.** One
program in 595, and that program is one we wrote. The fix needs the enclosing
definition's body threaded through `ZigCtx`. You said we are too timid about
expanding `ZigCtx` and I agree in general — but this is the wrong first
customer for that expansion, because the payoff is a single self-authored test.

**What I would NOT cut:** finding 65's simple half, even though it is not
shippable tonight. Unlike 60, it is one build old, its failure mode is
specific and named, and it sits on a structural argument we are about to make
in the Issue. That is worth one more sitting; the discard was not.

## The thing I keep getting wrong, since it bears on how much to trust the above

Three times today I wrote a confident mechanism into a document and had to
withdraw it: finding 64's diagnosis, finding 63's diagnosis, and finding 65's
falsifier. In every case a five-minute measurement settled what an hour of
reading had not, and in two of the three the wrong version had already been
sent or committed.

The pattern is specific enough to name: **I infer a mechanism from one error
message, write it down as fact, and only then test it.** The correction is not
"be more careful" — it is the canary discipline we already have and I keep not
reaching for: when a diagnosis matters, make the suspect path answer a value it
could not produce any other way, before writing the prose.

For the Issue this means: every mechanism claim gets a citation to a
measurement, and anything I have not measured gets labelled a lead in the text,
not in a footnote. Damian's agents will be reading this overnight without us in
the loop to qualify it.

## What I propose for tonight

1. **Sweep finishes** → the three-finding PR is sendable the moment the mirror
   push lands.
2. **One Issue**, tonight, carrying: the four-legged structural argument, the
   unconstrained-type question with its recommendation, finding 65 with its
   superclass failure stated as a failure, and monomorphisation noted as ours.
   Every claim marked measured or lead.
3. **Drop finding 60 from the plug PR.** Keep 61, which is one line, measured,
   and unblocked two programs nobody predicted.
4. **Stop opening new threads.** We have enough.
