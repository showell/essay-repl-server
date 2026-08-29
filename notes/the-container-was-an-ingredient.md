# The container was an ingredient

*2026-08-29, written after PR 103 went out and both sandboxes were pruned.
Forty-one ladder commits today, ten in Cobblestone across all branches, one
new PR. The essay is about why a measurement needs three coordinates and what
happens when a fourth one leaks in unannounced.*

## Four repos, and what each one is allowed to say

It is worth naming the boundaries before describing what crossed them, because
almost every confusion today was a fact that was true in one repo being read
as though it were true in another.

| repo | authority | moves when |
|---|---|---|
| `damiant3/Cobblestone` | the language, the compiler, the plugs | Damian ships an Update |
| `showell/NewRepository` | our unlanded deltas, one branch per PR | we propose something |
| `codex-zig-ladder` | the apparatus that measures the above | we learn how to measure better |
| `codex-zig-transpiler` | one artifact and its fixed point | either of the first two moves under it |

The important asymmetry is that the ladder is not downstream of Cobblestone in
the way a test suite is downstream of the code it tests. It is a *separate
instrument with its own release history*, and it can be wrong on its own
schedule. Today's largest finding was entirely a ladder defect. Cobblestone
was innocent, and no amount of staring at Cobblestone would have surfaced it.

That asymmetry has a practical consequence that took a while to internalise:
**a ladder measurement is never identified by one ref.** It is identified by a
pair — which codex ref was measured, and which ladder ref did the measuring —
and either one moving invalidates the result. Neither repo's `git log` can
tell you the pair. That is what `U53.log` is for, and it is why every sandbox
writes a `MANIFEST` naming both.

## An Update is a coordinate, not an event

The word "Update" does a lot of work here, and it is worth being precise about
what kind of thing it is. Update 53 is not a moment in time; it is a *pin*. It
names a tree — `58b08c38` — and a seed, `B066CEB5FE8FC9E8`. Everything the
ladder says is said relative to such a pin.

This is why the checkout model is "pin a branch per Update, no local master."
A local master would drift, and a drifting baseline is worse than no baseline,
because it still produces rows and the rows still look like findings. The
branch `u53-rebank` exists to hold `58b08c38` still while everything else
moves.

Today's fix branch was cut from exactly that ref, and this turned out to
matter more than it usually does. `zig-plug-drop-shadowed-arms` contains one
commit on top of plain Update 53 — no other unlanded work underneath it. So
when the corpus was swept twice, once at `58b08c38` and once at `88daa0a8`,
the *only* difference between the two populations was the thirty-seven lines
in `ZigEmitter.codex`. One variable. Every row in the diff had exactly one
possible cause.

Compare the shape we have hit before: a branch stacked on two other unlanded
branches, measured against a release. Every row then has three possible
causes, and the rows cannot tell you which. The standing rule — measure
against our fork's stack and *name* it in the PR — exists because a stack is a
branch, not a pile of working-tree patches, and only a branch can be named.

## The sandbox was supposed to be furniture

Here is where the day turned.

The third coordinate is the sandbox. A ladder run does not happen in the
checkout; it happens in a freshly cut pair of detached worktrees under
`~/runs/<timestamp>-<label>/`, with an `env` file pointing `CODEX_ROOT` at the
codex half. The reason is stated plainly in `sandbox.sh` and it is a good
reason: every ladder output is gitignored, so a shared checkout accumulates a
full set of plausible, real, stale files under exactly the names the next run
looks for. A fresh tree carries none. A run that wants natives must build them
or be handed them on purpose.

The design intent is that the sandbox is *neutral*. It is a container. It
holds the measurement; it is not part of the measurement. Two sandboxes cut
from the same two refs should be interchangeable, and if they are not, the
whole apparatus is measuring its own scaffolding.

They are not interchangeable. Zig bakes the build directory into the binary it
produces — for stack traces, entirely reasonably — so `native/zigemit` built
in `20260829T205145Z-u53-dup-arms` contains that string, and the one built in
`20260829T220422Z-u53-dup-baseline` contains the other. A plain `grep -a` on
either binary reads it straight out.

The container leaked into the artifact. And then two separate mechanisms
hashed the artifact and called the result an identity.

## The same leak, wearing two opposite disguises

This is the part I find genuinely instructive, because the two consequences
look like opposites and are the same bug.

**`natives_stamp()` is a sha over the two binaries.** `dup.sh` opened by
announcing "plain-U53 natives were `ec0d7989cbe3`; a match here means the fix
never reached the build." The intent is exactly right — it is a falsifier, and
having one is better than not having one. But because the two builds live in
different sandboxes, the stamps could never match *whatever the source did*.
The guard could only ever pass. It reads as the check that proves the change
took, which is worse than no check, because its presence is why nobody writes
the real one. I copied the idea into my own baseline script before noticing,
which is its own small lesson about inherited scaffolding.

**`bank_describes_this_tree()` compares the same shas** under the name
`meta.tools`, and prints `*** THE BANK IS NOT ABOUT THIS TREE ***` when they
differ. Same leak, and now the gate can only ever *fail*. A bank taken today
is "not about this tree" tomorrow, because tomorrow is a different sandbox.
Four mutually distinct tool identities for what is substantially one
toolchain:

| | codexir | zigemit |
|---|---|---|
| the bank, 08-27 | `6c1711aa` | `6eb2621b` |
| the main checkout | `10850a2d` | `9fdf7112` |
| dup-arms | `dfed25e4` | `8e5b843f` |
| dup-baseline | `c27ca4e2` | `f715286e` |

The main checkout's binaries carry `20260826T160728Z-u50-harness-lift` — they
were built in a sandbox on the 26th and copied in, path and all. The container
outlived the container.

One guard that cannot fail, one that cannot succeed, both descended from a
build directory ending up inside a binary. Both look like rigour.

## What this did to a queued item

`U53.log` carried an open item: *re-bank the corpus census at U53, so there is
finally a comparand that records its own base.* Reasonable, and I nearly did
it. It would not have worked. The new bank goes stale the instant the next
sandbox is cut, because staleness is defined by a field that always moves.

The distinction worth keeping is between the two halves of the bank's
metadata. `meta.base` records *refs* — which trees produced this run. That
half works, because a ref is a name in a repo and survives relocation.
`meta.tools` records *binary shas* — which artifacts produced this run. That
half cannot work, because an artifact is a thing in a directory and does not.

So the general form: **identify a measurement by its source coordinates, not
by its materialised artifacts.** Repo plus ref survives being moved,
rebuilt, copied, and pruned. A binary does not. The two candidate fixes both
follow from that — derive the tool identity from the bundle fingerprint of
plug plus harness plus seed plus zig version, which `zigc_verify.sh` already
computes for its build cache; or keep the path out of the binaries and make
them reproducible. The first is cheap and works today. The second is the
root-cause fix and trades against the panic traces the corpus reads when a
program crashes. Neither is built, because both are infra.

## The corpus is shared across Updates, which is why a defect can hide in it

The other interplay worth writing down is between the corpus and the Update
sequence, and it produced the most interesting single fact of the day.

The corpus is 614 programs from Cobblestone's own `codex/test/`. It travels
across Updates. Our verdicts about it are ours, but the population is theirs,
and it accumulates.

The two-arm run said: zero verdicts moved across 326 built programs, and 581
of 582 emitted `.zig` files byte-identical. The one that moved was
`circbuf-test` — not the new test, which lives in `test/ops/` and is in
neither arm's population. At plain Update 53 it emitted two `.None` prongs in
a single switch, which is a real instance of the very defect the PR fixes,
sitting in their corpus, arriving from an or-pattern exactly as row 2.02
describes.

And it had been invisible. `circbuf-test` is refused for an *unrelated*
reason — `switch must handle all possibilities`, a different plug gap — and
zig stops at the first error. Neither arm's log contains the string `duplicate
switch value` anywhere. The defect was masked behind another defect, in a file
that never compiled, for however many Updates.

The methodological point is sharp enough to keep: **a verdict is a lossy
projection of an emission.** Verdicts moved: zero. Bytes moved: one file. If
the comparison had been verdict-only — which is what a bank diff is — the
change would have been declared inert, and the declaration would have been
true and useless at the same time. It really did move nothing observable; it
also really did fix a live instance. Both.

I had predicted zero movement, in writing, in the script, before the run. The
reasoning was that the gate's precondition is a shape zig already refuses, so
nothing that built before could be affected. That reasoning was correct and
the conclusion was still incomplete, because it never occurred to me that a
program could carry the defect while being refused for something else. Writing
the prediction down is what made the gap visible; a prediction that stays in
your head gets quietly revised into whatever happened.

## Where the row numbers live

A smaller but recurring interplay: the backlog rows are a shared namespace
across the repo boundary, and we do not own the numbering.

PR 103 closes `plugs-backlog` row **2.02**, and 2.02 is Damian's row — he
wrote it, describing the zig plug refusing legal Codex. So the PR cites it and
adds nothing. Contrast the prelude work, where we drafted a row as 1.100 and
it landed renumbered to 2.01 at absorption, the register having reached 2.00
in the meantime. Our numbering of our own contributions is provisional until
it lands. The row *text* is the contribution; the number is upstream's to
assign.

This is the same lesson as the sandbox, one level up. A number assigned in our
tree is a local artifact. The stable identity is the description.

## The recommendation

Do not re-bank the corpus census. The item should stay struck until the tool
identity is source-derived, because until then the bank cannot answer the
question it exists for, and a fresh bank would only make the banner quiet for
one run — which is strictly worse than a banner that is loudly wrong, since a
quiet wrong answer is the failure mode this whole box is built to prevent.

The cheap fix is the bundle fingerprint, and it is maybe an hour. It would
retire the banner, make `--changed` meaningful again, and let a single-arm
corpus run mean something — which is the difference between an eight-minute
question and a thirty-minute one, on every zig-plug PR from here on. That is
the item I would put next, ahead of re-banking anything.

And in the meantime the rule is simply: **two arms, or nothing.** A bank diff
is not evidence today. It was not evidence yesterday either; we just could not
see that yet.
