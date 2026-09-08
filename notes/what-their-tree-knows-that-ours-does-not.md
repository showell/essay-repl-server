# What their tree knows that ours does not

Ten pull requests went to Damian's compiler between 117 and 133. All ten
landed. Nine went in as written or nearly so. That is a good result and it is
not the interesting part.

The interesting part is the four places where their agents had to change
something on the way in — because in every one of those, the thing we got wrong
was invisible from where we were standing. Not "we were careless". Not "we
didn't test enough". **Invisible.** We could have read our copy of their source
all day and not seen it.

That is worth understanding, because it is the difference between friction we
can remove and friction we cannot.

---

## The shape of the problem

We have a clone of their repository. It looks like their tree. It is not their
tree.

Their actual working copy lives in Perforce, behind a client configuration,
inside a build system with rules that are enforced by people and by convention
rather than by the compiler. What we see on GitHub is a periodic export — the
bytes, without the rules that produced them.

So when we send a patch, we are guessing at a set of constraints we have never
been shown. Most of the time the guess is fine. Four times out of ten it was
not, and each of the four is a different *kind* of thing we could not see.

---

## Gap one: a citation is a whitelist, not a door

Codex chapters cite each other. We had read

```
cites Codex chapter Phase Allocator (deck-short-of)
```

as *"this chapter uses the Phase Allocator"*, with the parenthesis as a note
about which bit. It is not a note. It is the **complete list of names this
chapter is allowed to use from that chapter.** Reach for a second name and the
program does not compile.

Our patch for PR 117 used `hosted-kind` inside `TypeChecker.codex`, which cites
Phase Allocator selectively and does not list it. That should have failed. It
didn't — but only because `hosted-kind` turns out to be a *builtin*, and
builtins need no citation at all. We were right by accident.

Their agent flagged it as *"worth checking when a change reaches for a name the
chapter has never used"*, which is a generous way of saying: you got away with
that one.

**Why it is invisible:** nothing in the file says the parenthesis is exhaustive.
You learn it by breaking it, or by being told. We have now been told.

**What it costs:** one review round-trip per occurrence, forever, until we
check it ourselves. The check is mechanical — cross the identifiers a diff
introduces against the citing chapter's cite list — so this one is fixable and
we will fix it.

---

## Gap two: the tree does not want our prose

We write a lot of explanation into code. It is deliberate: a comment that says
*why* a line is the way it is survives a refactor that a comment saying *what*
it does will not.

Their tree has a standing rule against narrative in source. When PR 127 landed,
our two lines of code went in exactly as written and the paragraph above them
was cut down to the rule:

- **Kept:** `peek-qword a 0` is a bare-metal-only contract, and `variant-tag`
  costs the same load there.
- **Cut:** that this was the root of issue 126, how it was found, what the
  wrong version did.

Both of those are true and useful. One belongs in the source and one belongs in
the changelist, and the boundary is theirs to draw, not ours.

**Why it is invisible:** you cannot see a rule against something by looking at a
tree that follows it. The absence of narrative reads as "nobody bothered", not
as "this is forbidden".

**What it costs:** their reviewer's time, once per patch, trimming prose we
should not have written. We have asked where exactly the line falls. Notably,
they have twice called our *pull request bodies* reviewable and useful — so
this is a rule about source files, not about explanation in general. The
explanation is welcome; it just goes somewhere else.

---

## Gap three: their tree cannot take our tools

We built a validator for WGSL shaders. It runs `naga` — the validator Firefox
itself uses — and it caught something real: 24 shaders that Chrome accepted and
Firefox would refuse. The PR fixing them landed and their agents verified it
beautifully, regenerating all 42 shaders through their own independently built
compiler and finding ours byte-identical.

The validator itself did not land. Their tree has a rule against depending on
anything outside its own Windows-plus-Codex environment, and ours drives a Rust
binary from node.

That is a coherent rule. A project that compiles itself from its own seed loses
something real the first time it needs a toolchain it did not build.

**Why it is invisible:** it is a rule about what a self-hosting project is
*for*, not a rule about code. It does not appear anywhere in the source because
it is a rule about what does not appear.

**What it costs:** nothing, once understood — but it reshapes what we should
send. Most of what we can offer them is *measurement against implementations
they do not own*: Firefox's shader validator, the zig compiler, a browser. The
right artifact for that is usually **the number, in a pull request**, not the
tool that produced it. We keep the tool. They get the answer.

---

## Gap four: the bytes we see are not the bytes they have

This is the one that would have been hardest to guess.

We found fifteen files in their foreword that use Windows line endings, where a
stray carriage return lands *inside a chapter's name* — so the chapter is
present, a citation to it still cannot match, and the compiler reports a missing
chapter, which is not what is wrong. That diagnosis was right and they said so.

Our fix was to convert those fifteen files from CRLF to LF. On their side that
would have rewritten every line of fifteen files — 143 lines in one of them —
because **Perforce already normalises line endings on that tree.** What actually
survives over there is twenty stray carriage return bytes, one per file. The
real fix is one changed line per file.

Our patch was twenty bytes of defect and several thousand lines of collateral.

They also found that the problem is not fifteen files but nineteen, because we
censused the directory where the failure surfaced instead of the whole tree.
That part is entirely ours and has nothing to do with Perforce.

**Why it is invisible:** a version control system's storage layer is not in the
files. We were looking at an export and reasoning about an original.

---

## The fifth gap, which is ours alone

One patch would have miscompiled, and it is the one worth ending on because
nothing about their tree explains it.

We changed a function so its fifth parameter meant something different: it had
held one entry per definition — 6,431 of them — and now held one per citation,
106. **Both are lists of text.** The types are identical. We updated the
function and left four callers passing the old list into a parameter that is now
indexed a completely different way.

It compiles. It produces wrong answers in three phases of the compiler, silently.

Their agent found it by reading. Our arms could not have: the affected code only
does anything when two chapters define the same name, and the compiler's own
source — the subject we test everything against — apparently has no such case.
Our differential said the output was byte-identical across 6,890 definitions,
and it was, and the patch was still broken. **A green comparison over a path
your subject never walks is not evidence of anything.**

And we own the tool that would have caught it. It answers in about a second:

```
$ xref who apply-cite-overrides codex/
apply-cite-overrides: defined in Chapter Scoper
  read by 3 chapters:
    Lowering, Name Resolution, Type Checker
```

That is their list. We wrote that tool. We did not run it, because we run it out
of curiosity while reading rather than out of a rule — and since the *type* did
not change, nothing failed and the question never came up.

The rule we did not have, and now do:

> **When a parameter's meaning changes and its type does not, the compiler is
> not a check and no test is a check. List the callers and read every one.**

---

## What the four gaps have in common

Three of them are facts about a system we cannot see: which names a chapter may
use, what prose the tree accepts, what a file is made of in the depot. Those are
cheap to fix once written down, which is why they are now written down.

The fourth is a habit: we asked our tooling a question when we were curious and
not when it mattered.

There is a fifth thing, and it is the most encouraging. Read their responses and
what comes through is not tolerance. They ran the census our change invited
before accepting it. They rebuilt 42 artifacts from source rather than copying
ours, and kept seven untouched ones as a control. They compiled the verifier
with the *previous* seed so the thing under test did not build its own judge.
They measured our speed claim, could not reproduce it, and said so in the
changelist rather than letting a nice title stand.

That is a high standard being applied to work from outside, at some cost, over
and over. The friction is real and most of it is ours to remove.

---

*Written by Claude (Anthropic), working with Steve Howell.*
