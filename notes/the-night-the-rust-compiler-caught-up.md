# The night the Rust compiler caught up

*Written 2026-09-07, for Steve, who fell asleep somewhere around the middle of
it. No compiler background assumed.*

---

## The short version

We started the evening with 19 of 28 test programs compiling correctly. We
ended it with **28 of 28, byte for byte identical to upstream's own compiler.**

Then this morning we pointed the same machinery at a much harder target — the
Cobblestone compiler's *own source code*, 3.4 megabytes of it — and found two
real bugs that the 28 programs could never have shown us. One of them was the
kind of bug that makes you sit back in your chair: for months, in a handful of
places, our compiler had been silently rewriting `+` into `&`.

Below is the whole story, in order, with the interesting parts explained
rather than named.

---

## Part 1: What we are actually building, in one paragraph

Damian's Codex language has a compiler written in Codex itself. We are writing
a **second, completely independent compiler for the same language, in Rust.**
Not to replace his — to disagree with it. Two independent implementations that
must produce identical output are an enormously powerful bug-finding device,
because when they disagree, exactly one of them is wrong and neither can hide.

"Identical output" needs a definition, and ours is strict: our compiler and
his must produce the same **IR** — the intermediate document a compiler
produces after it has understood a program but before it emits machine code —
down to the byte.

---

## Part 2: The wall at 24

The 28 test programs are small, frozen, real Codex programs with upstream's own
expected output beside them. Getting from 19 to 28 was mostly ordinary bug
work, and I'll spare you the individual fixes. But partway up we hit something
that *wasn't* ordinary, and it's the most architecturally interesting thing
that happened all night.

Our compiler was producing its IR as **text**. It walked the program and
printed the answer directly, the way you might write out a translation
sentence by sentence.

Upstream doesn't do that. Upstream builds the IR as a **tree** — a data
structure in memory — and then runs a series of *rewriting passes* over that
tree before printing anything. Three of them, in order:

- **fold constants**: `2 + 3` becomes `5`.
- **inline leaf calls**: a tiny function that calls nothing else gets its body
  pasted into its caller.
- **inline single-caller**: a function called from exactly one place gets
  absorbed into that place.

Here's the thing: **the answers we are being graded against are what comes out
the far side of those passes.** So a text-first compiler cannot win. It isn't
that it's harder — it's that the target is a document describing a program
that has already been rearranged, and you cannot rearrange text you have
already printed. I measured the ceiling honestly before touching anything:
text-only emission could have reached 24 of 28 and never 28.

So we rebuilt it the way upstream has it, which is also just the way it should
be built:

```
check ──▶ lower ──▶ lift lambdas ──▶ pipeline ──▶ prune ──▶ text
```

Six stages, each one a separate file, each handing a real data structure to
the next. The refactor was done in two commits: first *build the tree and
print it*, verified byte-for-byte unchanged — proving the new architecture was
a pure restructuring and not a behaviour change — and only *then* add the
passes. That ordering matters. If you change the shape and the behaviour in
one step and something breaks, you have no idea which half did it.

With the passes in, all 28 went green.

**The lesson, which is your standing question:** we were doing hard work at a
deep layer because an earlier layer wasn't carrying its knowledge forward. The
fix was never to be cleverer at the bottom. It was to build the thing the
bottom needed.

---

## Part 3: The literal that was decoded three times

A smaller version of the same lesson, worth telling because of how it ended.

When Codex source says `"hello\tworld"`, something has to decide what `\t`
means. We were deciding it in **three different places** — and for character
literals like `'\t'`, in two more. Five decode sites for one question. Upstream
has one, in a stage called the *desugarer*.

So I moved ours to one place. And in doing that, two things came out that I
would never have found by reading:

1. **The two decoders are legitimately different.** In a text literal `\t` is
   *two spaces*; in a character literal it is *one*. Had I "unified" them
   without checking against the oracle, I would have picked one rule and been
   wrong half the time. Consolidation without an oracle is a coin flip
   wearing a lab coat.

2. **Both escapes are errors upstream anyway.** Codex refuses `\t` and `\r`
   inside a text literal outright. We were quietly accepting them. That is an
   *acceptance gap* — our compiler said yes to a program upstream says no to —
   and it only surfaced because the fix was graded against the real thing
   rather than against my own idea of what the escape meant.

---

## Part 4: A better subject — the compiler's own source

Twenty-eight small programs is a good fast gate. It is not a good *hard* test.
You suggested the frontend Codex files, and you were right; they are a far
crueller subject.

There are two of them, and both are just Codex source:

| subject | size | what it is |
|---|---|---|
| `codexcheck-subject.codex` | 3.44 MB, 92 chapters | the entire Cobblestone compiler as one unit |
| `ringplug-source.codex` | 388 KB, 14 chapters | a smaller, self-contained piece |

We can't compare IR on these — they're too big to have a frozen expected
answer. But we can compare something almost as good: **four counters** that
both compilers print.

Think of them as odometers. As a type checker works through a program, it
invents temporary placeholder types ("I don't know what this is yet — call it
*thing #4,197*"). The counters say how many it invented, how many it recorded,
how many it merged. If two independent compilers walk the same 3.4 MB of
source and their odometers agree exactly, they did the same work in the same
order.

This is a *stern* test. Getting a hundred and eighteen thousand of anything to
land on the same number by accident is not a thing that happens.

Where we stood at 2:44am:

```
                oracle       ours    delta
next-row-id    311,802    311,802        0     ← exact
next-id        118,066    118,071       +5
expr-types     145,772    145,776       +4
check-errors         0          0        0
```

Three hundred and eleven thousand of one counter, exact. Five out of a hundred
and eighteen thousand on another. Close enough to be tantalising and far
enough to be real.

### The instrument problem

Five in 118,000 cannot be found by counting. You need something that says
*where*.

Upstream prints one line per definition saying what kind of type it settled
on — `tb <name> <kind>`. Compare our list against theirs and any disagreement
names a definition. That is a localiser, and it's exactly what a delta of five
needs.

It reported two disagreements on the small subject. **They were ours, and they
were not the checker's** — they were the *printer's*. When a definition
declares no type, it gets a placeholder, and unification fills it in later. We
were printing the placeholder instead of the filled-in answer, so a definition
that is a list printed as "unknown". One-line fix.

With that fixed: **zero disagreements on the small subject, and zero across all
7,207 definitions of the whole compiler.** Which is a genuine result about the
type system, and a reassuring one: *no definition anywhere in the Cobblestone
compiler gets the wrong type from us.* Whatever the remaining counter gap is,
it is about the *order* things are invented in, not about being wrong.

### Three ways to waste an hour

I tried to narrow the gap by cutting the subject down. All three obvious cuts
are invalid, and each one fails in a way that looks like a compiler bug until
you work out that it isn't:

- **One chapter alone isn't a subject.** Names are visible across a whole
  compilation unit without being explicitly imported, so a lone chapter is
  missing things it never had to ask for.
- **The first N chapters aren't either.** The bundle isn't dependency-ordered
  — chapter 46 cites a chapter that appears later in the file.
- **Half a chapter isn't either.** The Zig emitter's definitions are mutually
  recursive, so any truncation leaves a dangling reference.

That's written down now so nobody pays for it twice.

What *does* work: chapters 1–12 of the small subject stand alone and match
exactly. Chapter 13 is where the deltas live. I went to sleep with that.

---

## Part 5: This morning — into the haystack

Chapter 13 is 4,561 lines. But the third trap above says you can't truncate
inside it... and that turned out to be *almost* true rather than true. Some
truncation points do produce a valid program; most don't. So the bisection is
noisy but workable: cut, run both compilers, keep the cuts where both accept
the file, and watch where the delta appears.

Eleven cuts later, four lines:

```codex
is-zig-primitive (s) =
 is-zig-keyword-loop zig-primitive-names s 0 (list-length zig-primitive-names)
 | is-zig-int-primitive s
```

I rewrote it on one line. The delta vanished. Put the line break back, and it
returned.

### Bug one: a newline is not an operator

Here is what was happening, and it is worth understanding because it is a
beautiful example of a bug that hides behind a *correct* answer.

When the compiler reads source, the first stage (the lexer) turns bytes into
tokens: names, numbers, operators — and also **layout** tokens marking where
lines and blocks begin. Later, when the desugarer sees `a + b`, it looks
through the tokens for the operator.

It looked for "the first token that isn't *trivia*". And `is_trivia` means
something very specific in our codebase: *"a token we invented that upstream
doesn't have"* — spaces, skipped prose, unmappable bytes. It exists so we can
prove our lexer matches upstream's, token for token.

A newline is not one of those. A newline is upstream's too. So a newline is
not trivia — and when the operator begins a continuation line, **the newline
comes first, and the newline was taken as the operator.**

Then the second half. The function that turns an operator token into an
operator ended with:

```rust
_ => BinaryOp::OpAnd,
```

A silent fallback. Anything unrecognised became `&`.

So: nine definitions in that file had their `+` and `|` **silently rewritten to
`&` by our compiler.**

And nothing failed. Not one test, not one program, not one byte of IR. Because
in Codex, `&` is overloaded — it's boolean AND, text append, *and* bitwise —
so the language decides what it means by looking at its left operand's type.
Which is exactly what `+` does. The types agreed, the programs ran, the output
was right.

The *only* observable difference in the entire system: `&` is the one operator
that records an entry in the expression-type table, because it's the one
operator whose meaning has to be written down for later stages. So the odometer
read one high. That single digit, in a hundred and forty-five thousand, was
the whole visible surface of the bug.

Two fixes. The desugarer now asks the question it actually meant — a new
`is_layout()` for "newline, indent, dedent" — and `binary_op` no longer
guesses. I checked first: across the four big frontend units, the 28 curated
programs and all 177 of safari's Codex files, **zero** tokens reach the
fallback. So refusing costs nothing, and the next unrecognised operator will
be a named error instead of a counter nobody can explain.

That closed `expr-types` on **both** subjects — 145,772 and 12,378, exact — and
took the curated counters from 25 to 26 of 28.

### Bug two: the definition that declares nothing

One gap left: the small subject was two *under* on invented placeholders. Same
bisection, now much quieter with the noise gone, landed on two definitions —
and the four-line repro is about as small as these get:

```codex
Chapter: P
Section: S
  a = 7
```

A definition with no declared type. Upstream invents **two** placeholders for
it; we invented one.

Reading upstream's source for why is the good part. When a definition has no
signature, upstream doesn't reuse the placeholder it made when it first
registered the name. It calls `build-undeclared-fun-type`, which mints a
*fresh* one for the result plus an arrow for each parameter — and then **ties
the two together** by unifying them. Two names for one thing, joined.

That looks redundant and isn't. The registration placeholder is what everyone
*else* sees when they call this definition; the new one is what the
definition's own body is checked against. Building them separately and then
equating them is how the checker keeps "what I promise" and "what I compute"
from being accidentally the same object.

Forty lines. And with it:

```
ringplug-source.codex, 388 KB, 14 chapters, all four counters:

                oracle       ours
substitutions    9,173      9,173
next-id          9,173      9,173
next-row-id     22,636     22,636
expr-types      12,378     12,378
check-errors         0          0
```

**An exact match on all four, on 388 KB of the compiler's own source.** Two
independent type checkers, written in different languages by different people,
inventing 9,173 placeholders and 22,636 effect rows in the same order.

The big subject moved to +7 — which is arithmetic, not a regression: it has
undeclared definitions too, so closing this gap moved it *up* by two and
revealed a third, separate cause underneath. That one's next.

---

## Where things stand

| gate | result |
|---|---|
| unit tests | 167 pass |
| curated interpreter (`run.sh`) | 28 / 28 |
| curated Rust-compiles-Codex (`native.sh`) | 28 agree, 0 differ, 0 refused |
| curated two-host IR (`ir.sh`) | 28 identical |
| safari spec suite | 54 specs, 2,351 values |
| curated checker counters | 26 / 28 |
| **ringplug (388 KB)** | **all four counters exact** |
| self-host (3.44 MB) | rows and expression types exact; +7 placeholders |

The two curated stragglers are both *induction* proofs and want a checker
stage we haven't built. The self-host +7 is the open thread.

---

## The thing I'd want you to take away

Both of this morning's bugs had been in the compiler for a long time. Every
test we had was green. Every program produced the right answer. The `+`-to-`&`
rewrite in particular had **no user-visible symptom at all** — you could have
run that compiler for a year and never seen it.

They were findable because of one decision: grading against a *counter* the
oracle also publishes, rather than only against final output. Final output is
where you find the bugs that matter today. Counters are where you find the
bugs that will matter later, while they're still cheap — a compiler that gets
the right answer by a slightly different route is a compiler that will
eventually get a different answer.

And the subject mattered as much as the instrument. The 28 curated programs
are 4–16 KB each and *nobody writes a binary operator on a continuation line
in a 200-line test program*. It took 3.4 megabytes of somebody's real,
idiosyncratic, hand-written source to shake that loose.

Which was your suggestion.
