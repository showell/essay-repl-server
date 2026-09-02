# The ask is smaller than it looks

*2026-09-02. Steve asked whether we should file an issue upstream about the
intermediate values. I went to check the assumption and it turned out to be
wrong, in a way that makes the ask much better.*

---

## The claim I made, and why it was wrong

This morning I wrote that our harness exists "because we need the intermediate
values that the real driver throws away."

Steve's instinct was that this had better be load-bearing, since we pay for it
every Update. So I went and checked. It isn't load-bearing, because it isn't
true.

The driver's phase functions return the intermediates. All of them:

    CompileChecked = record {
     scoped : AChapter,              <- the desugared, scoped chapter
     all-bindings : List TypeBinding,
     ust : UnificationState,         <- the type state
     ctor-names, renames, colliding, assignments, ...
    }

    LexResult   = record { tokens : List Token, ... }
    ParseResult = record { doc : Document, ... }

Every single value our twelve rungs dump — the token list, the parse tree, the
scoped chapter, the type bindings, the IR — is already a field on a record
their own code hands back. Nothing is thrown away. I asserted otherwise from
memory rather than from reading, which is the same mistake in miniature that
cost the morning.

## So what is actually stopping us

One line at the top of the file:

    Chapter: Opening

`opening.codex` holds **185 definitions**. Among them are `compile-lex`,
`compile-parse`, `compile-desugar-and-scope`, `compile-type-check`,
`compile-frontend-cdx`, `scaled-floor`, `derive-deck-scale`,
`resolve-all-expr-types` and `lift-ir-for-emit` — every phase function and
every piece of the memory arithmetic we spent today getting wrong.

They are all in the same chapter as `opening`, which is the program's entry
point.

A harness has to define its own `opening` — that's what makes it a program. So
it can never bundle that chapter, because the two definitions would collide.
Our own bundler says so in as many words: *"opening.codex is the one chapter
that cannot come along — it defines `opening`, and so does the harness."*

The phase functions aren't hidden. They aren't private. They're **welded to
the entry point by chapter membership**, and that is the whole of it.

## What that costs us, in numbers

We can't call them, so we retype them. `ast/emit_harness.py` is 812 lines, and
twelve of its blocks exist for no reason except to restate what
`opening.codex` does, feeding seventeen generated harnesses.

Here is the part that settles the argument. Of the **last fourteen commits** to
that file, **eight** are corrections of the form "the driver does X and we
didn't":

- the RESOLVE and LIFT reservations were missing
- one of the two copies of the phase calls was still on the old argument list
- `check-chapter` was called without the wrapper the driver gives it
- the lower ceiling was passed as 0
- `lower-chapter` gained a ninth argument
- `check-chapter` went from five arguments to nine
- the diagnostic bags the driver builds itself were never merged
- the hosted harnesses didn't lift after the driver started to

Six of those eight are from today. None of them is a bug in our logic. Every
one is a divergence in a hand copy.

## The ask, sharpened

Steve's framing was "make them stop throwing away intermediate values, or at
least structure their code so it's easier for us to maintain our harnesses."
The first half is aimed at a problem that doesn't exist. The second half is
right, and it can be made very specific and very small:

> **Split `Chapter: Opening` in two.** Move the phase functions and the deck
> arithmetic into a `Compile Driver` chapter. Leave `opening` — the entry
> point, the argument parsing, the modes — in `opening.codex`, citing the new
> chapter.

That's a file split. No behaviour changes, no algorithm moves, nothing they
have to design. Codex already supports citing named functions out of a
chapter, so nothing is forced on anyone who doesn't want it.

And it converts our entire failure class from *transcription* to *calling*:

- an argument list can't drift, because we pass arguments to the real function
- a reservation can't be forgotten, because it's inside the function
- a `deck-record` wrapper can't be missed, for the same reason
- `scaled-floor` and `derive-deck-scale` become reachable, so our decks would
  scale the way theirs do instead of using raw constants — which is one of the
  two things still open tonight

It's also a good ask *for them*, which matters when you're asking someone to
move their code around. A 185-definition chapter that mixes the entry point
with the compilation pipeline is already the kind of thing that gets split
eventually. We're just the ones who noticed the seam.

## The honest counter-cases

**It doesn't fix everything, and I'd rather say so than oversell.** Two of
today's six defects survive it. `lir_to_x86` broke because a chapter we bundle
grew a dependency on a chapter we don't — that's about *subsetting the
compiler*, which the split doesn't touch. And tonight's deck-guard fault would
still need diagnosing.

**A rung is a slice, and the driver assumes the whole compiler.** Being able to
call `compile-type-check` doesn't help if the chapter carrying it drags in the
back end. This is the real objection, and the honest answer is that it makes
the split *partial* rather than useless: the small back-half rungs would keep
hand-built harnesses, and the front-end rungs — which is where every one of
today's defects landed — would not.

**We'd be depending on their internal structure.** True, but we already do; we
just do it implicitly, by copying it. Depending on a function signature is
strictly better than depending on our memory of a function signature, because
the compiler checks the first one.

**The risk I'd flag to them explicitly**, because we just spent a day inside
it: moving a definition between chapters is not always behaviour-preserving in
this compiler. The deck intrinsic is gated on `init-phase-allocator` and
`deck-record` resolving to the *same defining chapter*. Anything that moves
code across a chapter boundary can flip that gate, silently, and we have the
scar tissue to prove it. That's a thing for them to check, not a reason not to
do it — but it should be in the issue, because it's the kind of detail that
turns a cheap change into a bad afternoon.

## Recommendation

File it, as its own issue, separate from 115.

Lead with the measurement, not the request: eight of our last fourteen
harness-generator commits are corrections of a hand copy of their driver, six
of them in one day. Then the one-sentence ask. Then what it does not fix, and
the chapter-gate risk.

We should also say plainly that we'll do the work on our side — we're not
asking them to maintain our harnesses, we're asking for a seam we can hold
onto. That's a much easier thing to say yes to, and it happens to be true.

One caution on timing. We are one day into Update 54 and I have been wrong
twice today about things I asserted confidently. This particular claim I have
checked — the record fields are quoted above, the chapter count is real, the
commit list is real. But the *reason* it's worth filing is that it's a
structural observation rather than a defect report, and structural
observations get better when they've survived a night.
