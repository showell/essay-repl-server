# The corpus that argues back

*2026-09-12, late. Cobblestone's own test suite as a ladder for our Codex to
Roc emitter: 597 programs, each beside the output it must print. What it
found in one evening, and the one thing it says we cannot have.*

## The ladder

`codex/test/` holds 641 Codex programs. 597 sit beside an `.expected` file
holding exactly what the program prints; 24 more are diagnostic tests, which
expect a compiler error rather than output. That is the same shape as
safari's 54 frozen verdicts, and thirty times the size, so `tests/ladder.sh`
emits each one to Roc, runs it on the Echo platform, and diffs. Thirty-eight
seconds for the lot, two at a time.

Every outcome is counted apart, because they mean different things:

| | at the start | now |
|---|---|---|
| pass | 38 | 125 |
| fail | 35 | 0 |
| refused by the emitter, by reason | 500 | 445 |
| diagnostic tests, skipped | 24 | 24 |
| diverges, by name and reason | 0 | 2 |
| crash | 0 | 1 |

A refusal is the emitter saying, by name, that it has not built a form. A
failure is the emitter being wrong. The first is a queue; the second is a
bug, and there are none left.

Two things had to be right before any of that meant anything. Eighty-six of
the verdict files begin with a stray `0x01` byte and forty-six carry
carriage returns, both the console capture's rather than the program's, so
the ladder compares them as text. And `roc check` reports only the file it
was handed: a broken import compiles to a crash at its own site and says
nothing, which is how two real defects in our emitted `List` module sat
under a green games gate. Every gate now checks every emitted module.

## What it found in the emitter

Eight rules, none of them about tests.

- **An effectful function's arrow is `=>`.** Codex marks the effect on the
  row and Roc on the type; a `[Console] Nothing` annotated `->` is a type
  error at every call site.
- **A recursive type is nominal.** Roc's `:` is a transparent synonym and
  may not be recursive, directly or mutually; `:=` may, and its
  constructors are still written bare everywhere. The emitter now finds the
  declared types that reach themselves, over a closure of who mentions
  whom.
- **A nominal type has no structural `==`.** So the equality Codex derived
  is attached to the declaration as the `is_eq` method Roc's `==`
  dispatches to, and a list of the type then compares.
- **A declared type named like one of Roc's own** (`Box`, `List`,
  `Result`, …) takes a trailing underscore, or Roc reads it as the builtin
  and asks it for a type argument.
- **`targets` is a reserved word** — and so are `requires`, `provides`,
  `exposes`, `packages`, `platform` and `app`. The platform header's
  vocabulary is reserved in the middle of an ordinary module too, so a
  parameter named `targets` is a parse error.
- **A Codex list is matched with `Cons` and `Nil`, a Roc list with
  brackets**: `[]` and `[h, .. as t]`, and a tail nothing reads is `..`
  alone, because `.. as _` is not a pattern.
- **A boolean pattern keeps its case.** The IR writes `True` and `False`;
  a lowercase test in the emitter made every boolean pattern `False`, and
  the two arms of every boolean match became the same arm.
- **An opening may be a value, or sit inside lets.** A program whose
  `opening : Integer` is an expression prints it, which is what the driver
  does and what the verdict records.

Two builtins were worth more than the rest put together: `__narrow`, the
checker's marker for a value proved to fit a bound, which is the value
itself at runtime and was blocking sixty programs; and `text-length`, which
is a byte count because a Codex Text is one unit per character over an
alphabet of 1 to 127.

## What it says we cannot have

Here is the finding, and it is not a bug we can fix.

**A Codex list is written in place. A Roc list is a value.** The two agree
everywhere a program uses the answer the write hands back, which is almost
everywhere, and they part company wherever a program writes a list through
one name and reads it through another. The corpus contains programs that
do exactly that, deliberately, and one of them is in the foreword:

    cb-shl1 : List Integer, Integer, Integer, Integer -> Integer
    cb-dbl-mod (x) (m) (n) = cb-dbl-fix x m n (cb-shl1 x n 0 0)

`cb-shl1` takes a limb array and answers an *Integer*: it doubles the
bignum in place and hands back the carry, and the next line reads the
doubled array through the name it passed in. That is the bignum the RSA
chapter verifies signatures with. In Roc the doubling is a new list that
nobody keeps, and `cryptobig` quietly printed 11 where the verdict says 8.

Quietly is the part that matters, so the emitter now refuses it: a
definition that writes one of its own list parameters and answers something
that is not a list is a mutation the caller reads back, and it is declined
by name instead of emitted as a wrong number. Six definitions in the corpus
match.

That rule does not catch every case, and the corpus proves it. `list-push`
writes through a shared list too, so a walk that hands the same accumulator
to two siblings sees the first one's push in the second — `ui-event-test`
counts three where we count two. Detecting *that* needs to know what two
call sites share, which is a different kind of analysis. It is named in the
ladder as a divergence, with its reason, and a verdict is what caught it.

So the honest boundary is: **a Codex chapter that mutates a list for its
effect cannot be ported to Roc, and the foreword contains one.** Anything
citing `CryptoBig` inherits it. Everything we have actually shipped —
safari's 54 units, the 46 GPU kernels, the three games against Damian's own
graders — stays green, because none of them does this.

## What is still refused, and what it is worth

| family | programs | worth it? |
|---|---|---|
| memory and hardware builtins (`peek-32`, `poke-byte`, `port-out-32`, `alloc-bytes`, `process-get-pid`) | ~120 | no: these drive a machine |
| the `Char` type and `char-at` | ~110 | yes, and it is the big one |
| `=~=`, approximate equality on reals | 41 | yes, small |
| an act outside the opening | 32 | yes: the Console effect, threaded the way Device already is |
| a chapter whose name is not a Roc module name | 14 | yes, trivial |
| everything else | ~130 | case by case |

The char family is the next real rung, and it is not a one-liner: a Codex
character is a CCE code unit over a private frequency alphabet, where
`char-code 'A'` is 41 rather than 65. Porting it means carrying that
alphabet into Roc in both directions. Everything downstream of text
handling waits behind it, which is most of what a compiler does.

The hardware family is the opposite: those programs poke a network card and
read a port. They are not a gap in the emitter. A ladder that counted them
as failures would be lying about how far there is to go, which is why the
ladder names every refusal by its reason and lets you add them up yourself.
