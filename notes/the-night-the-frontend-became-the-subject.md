# The night the frontend became the subject

You fell asleep somewhere around the point where the Rust compiler was
getting nineteen of twenty-eight programs right. This is what happened after
that, written for someone who does not want to be told what a monomorphic
type variable is.

## The thing being built, in one paragraph

`rust-codex-compiler` is our own front end for Codex, written from scratch in
Rust. It reads a `.codex` file and produces **IR** — a plain-text intermediate
form, the compiler's halfway house between the program you wrote and the
machine code that eventually runs. Damian's own compiler does the same job.
The whole game is: given identical input, do we produce **byte-for-byte
identical** IR? Not "equivalent". Identical. That is a brutal standard and it
is the right one, because "equivalent" is a judgement call and "identical" is
a `diff`.

The scoreboard is twenty-eight small programs in `cobblestone-curated-tests`,
frozen, with upstream's own answers beside them.

**We finished the night at twenty-eight of twenty-eight.** Zero differences,
zero refusals.

## Why nineteen was a ceiling and not a milestone

Here is the interesting part, and it is the part that made the night worth
staying up for.

Our compiler was building its IR the way you'd write a report by typing
directly into the final document: read the program, and print IR text as you
go. That works, and it got us to nineteen, and with a lot of grinding it might
have got us to twenty-four. It could not have got us to twenty-eight, and the
reason is structural.

Damian's compiler does not print IR and stop. It prints IR into an internal
**tree**, then makes several passes over that tree to tidy it up — folding
`2 + 3` into `5`, inlining small functions into their callers, deleting code
nothing reaches. The answers we were being graded against are the output
*after* all that tidying. You cannot match the tidied answer by typing the
untidied one very carefully. You have to build the tree and do the tidying.

So that is what got built: lowering produces an actual IR tree; a separate
layer renders that tree to text; and between them sit the clean-up passes and
a final sweep that drops unreachable code. Five stages where there was one.

The lovely part is that the refactor was proved *byte-neutral* before the
passes were switched on — same twenty-eight files in, same bytes out, just
routed through a tree. Then the passes went in and the score moved.

## Your standing question, and the answer it got

You always ask whether we're doing too much work deep in the system because an
earlier stage failed to pass along something it already knew. Twice last night
that question paid for itself.

**Once in the type-checker.** A piece of the code was about to grow sixty
lines of machinery to work out the type of a field pulled out of a data
structure. Damian's compiler does exactly that, so copying it looked
responsible. But he needs it for a reason we don't share: his layers are
separated by a wall, and the answer is on the other side of the wall.
**Ours has no wall.** Chasing it back found two genuine holes in our own
type-checker, and fixing *those* moved the score and made the deep code
*shorter*. That is the ideal shape of this: the deep layer stops guessing
because the shallow layer starts telling.

**Once in string handling.** A quoted string was being decoded in three
different places, and a character literal in two. Consolidating them to one
place turned up something neither of us would have guessed: the two decoders
are *legitimately different* — `\t` means two spaces inside a string and one
space inside a character — and upstream actually rejects both of them at the
lexer as errors. If we had "cleaned that up" by picking one rule, we'd have
been wrong twice and had no way to notice.

## Then we changed subjects, and everything got better

Twenty-eight small programs is a fine regression gate and a poor microscope.
Your suggestion — *"the frontend codex files are good things to match"* — was
the right one and it changed the character of the work.

The Codex compiler is itself written in Codex. Bundled up, that is **3.44 MB
of source in ninety-two chapters**, and both our compiler and Damian's will
happily eat it. It runs in 2.5 seconds our side, 19 seconds his. Suddenly the
test subject is a hundred times the size and written by someone who was not
thinking about us.

The graded numbers are four counters — think of them as odometers. As the
type-checker works it hands out numbered slots for the types it hasn't figured
out yet, and it keeps a note of what it decided about each expression. The
counters are: how many slots got handed out, how many notes got written. If
our compiler and his agree on those numbers over three million lines of work,
they are doing the same thing. If they disagree by even one, something in
there is different.

Overnight, on the whole compiler:

| counter | Damian's | ours | gap |
|---|---|---|---|
| effect rows | 311,802 | 311,802 | **exact** |
| type slots | 118,066 | 118,071 | 5 |
| expression notes | 145,772 | 145,776 | 4 |
| errors | 0 | 0 | **exact** |

Three hundred thousand of one thing, exact. And a gap of *five* in a hundred
and eighteen thousand of another.

## Finding five in a hundred and eighteen thousand

You cannot bisect a number. What made it findable was noticing that the oracle
prints one line per definition saying what kind of thing it is — a function, a
list, a number. That is a per-definition localiser rather than a total, and
comparing those lists says *which definition* rather than *how many*.

It immediately reported two disagreements, and they were ours — but not the
type-checker's. **We were printing the wrong thing.** A definition that
declares no type gets a blank slot to start with, filled in later; we were
printing the blank slot instead of what got filled in. Print the filled-in
answer and: **zero disagreements on all 7,207 definitions in the compiler.**

That is a real result, and it's worth stating plainly: **no definition
anywhere in the Codex compiler gets a wrong type from us.** Whatever the
remaining gap was, it was about the *order* things were allocated, not about
being wrong.

I also burned an hour on three false starts, which are now written down so
nobody repeats them: a single chapter isn't a valid test subject (names are
visible across the whole file without being imported), a *prefix* of chapters
isn't either (they aren't in dependency order), and truncating a chapter fails
because its definitions call each other in a loop. What *does* work: the
small subject, `ringplug`, splits cleanly at chapter 12, and chapter 13 — the
Zig emitter, 4,500 lines — is where its gaps lived. That's where I left it.

## This morning: chapter 13

Two bugs, both small, both in places I would not have looked.

**A newline was being read as an operator.** Codex lets you break a long
expression across lines with the operator starting the new line:

```
  is-zig-primitive (s) =
   is-zig-keyword-loop zig-primitive-names s 0 (list-length zig-primitive-names)
   | is-zig-int-primitive s
```

Our desugarer picks the operator out of that by asking each token "are you
skippable whitespace?" and taking the first one that says no. But the function
it was asking answers a subtly different question — it means "is this token
*ours* rather than Cobblestone's", a bookkeeping distinction from a completely
different part of the system — and a newline answers *no* to it. So the
newline got taken as the operator. And the code that turns an operator token
into an operator had a fallback: *anything I don't recognise is `&`*.

So nine definitions in that file had their `+` and `|` **silently rewritten to
`&`**. Nothing broke — `&` in Codex happens to produce the same type as `+`
does — and the programs still ran correctly. The only trace it left anywhere
in the universe was that `&` is the single operator that writes an extra note,
so one counter ran one over.

That is a nice illustration of why the byte-identical standard is worth its
cost. A defect that changes nothing observable except a counter is a defect
that lives forever in a system graded on "does it work".

Two changes: the desugarer now asks the question it actually meant (*is this a
layout token?*), and the operator table no longer guesses — it refuses. I
checked that nothing legitimate was riding on that fallback: zero tokens reach
it across the four big frontend files, the twenty-eight, and safari's 177
Codex files. So refusing costs nothing and the next unrecognised operator
becomes a named error instead of a counter nobody can explain.

**And a definition with no declared type was one slot short.** Bisecting the
last gap landed on a genuinely odd bit of upstream source where a type
signature has got separated from the definition it belongs to, so two
definitions sit there with no declared type at all. We were giving each of
them one blank slot. Damian's compiler gives them *two* — one when it first
registers the name, a second when it actually checks the body — and then ties
the two together. Reading his `build-undeclared-fun-type` and doing the same
closed it exactly, including the effect row it also mints when the definition
takes arguments.

## Where it stands

**`ringplug-source.codex` — 388 KB, fourteen chapters — is now exact on all
four counters.** Every type slot, every effect row, every expression note:
identical to upstream's, in a file we did not write and were not tuning
against.

The whole 3.44 MB compiler is exact on effect rows (311,802), exact on
expression notes (145,772), exact on errors, and **seven** type slots apart
out of a hundred and eighteen thousand — a different, smaller cause that the
same method should reach.

The curated set went from 25 to 26 of 28 on counters, and the two that remain
both want a feature of upstream's checker we haven't built yet, so they're a
known hole rather than a mystery. Everything else stayed green: 168 tests, all
28 programs interpreting correctly, all 28 compiling byte-identically, safari's
54 spec files and 2,351 graded values.

The pattern worth keeping from all of it: **every one of these bugs was found
by an instrument, not by reading code.** The tree refactor was proved neutral
before it was trusted. The counter gap was localised by a per-definition
printout, not by staring. And the two bugs this morning were found by cutting
a 388 KB file in half over and over until a four-line function fell out. None
of them were visible from the code. All of them were visible from a number
that was one too big.
