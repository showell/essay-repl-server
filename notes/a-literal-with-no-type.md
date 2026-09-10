# A literal with no type

The arms had been consolidated for an hour when `ir-diff` ran over safari's
fifty-four exported specs for the first time and reported thirty-one of them
differing from upstream's frozen IR. Twenty-seven curated programs and
twenty-nine Roc ports had shown four differences between them, every one a
place we were ahead. Thirty-one on safari was a different kind of number.

## Reading the diff

Every differing token was the same token. Our wire said `(name "across"
error)` where upstream said `(name "across" real)`: a hundred and four name
reads, in twenty-four programs, all `error`, all on names bound by a `let`. Ten
more were `mul-int` where upstream said `mul-num`, and those followed from the
first: an operand of unknown type sends the multiply down the integer arm.

The `let` nodes themselves said `real` on both sides. Lowering types a `let`
from the value it just lowered, and the value was fine. Only the *reads* were
wrong, and a read gets its type from what the checker recorded at that span
when it inferred the name — which is whatever the binder held in the checker's
environment at the time.

So the question was what the checker thought `across` was, and the answer was
in the shapes. `let along = bull-dist + col * spacing + ...` read back `real`.
`let across = 0.0 - (lane-width / 2.0 + ...)` read back `error`. `let corner-a
= if d <= 0.000001 then 0.0 else ...` read back `error`. `let sgn = if
seg.exit-right then 1.0 else 0.0 - 1.0` read back `error`. Each bad one *starts
with a real literal*: as the then-branch of an `if`, or the left operand of a
subtraction. An `if` answers its then-branch's type; a binary answers its left
operand's. And the checker's inference arm for a literal read:

    E::Lit(_, IntLit, _)  => Integer
    E::Lit(_, TextLit, _) => Text
    E::Lit(_, BoolLit, _) => Boolean
    E::Lit(..)            => Ty::Error

A real literal had no type. `2.0` in `x * 2.0` never mattered, because the
multiply unifies its operands and answers the left, and the left was `x`. The
moment the literal came first, `error` was the answer, the `let` bound it, and
every read carried it out.

## Why nothing had caught it

The self-host is the compiler compiling itself, 2,869 definitions, byte-exact
against upstream, and it stayed byte-exact through this fix. The compiler's own
source has almost no real literals, and none heading a `let`. The curated 28
and the Roc 29 are integer and list programs. Safari is a driving game: every
chapter is geometry, and a `let` that opens with `0.0 -` or `if .. then 0.0` is
its most ordinary sentence. It found in one run what three corpora could not
have found in a hundred, which is the argument for corpora chosen by what they
are *about* rather than by what we happened to be working on.

The fix is two lines, NumLit to `real`, CharLit to `char`, as upstream's
`infer-literal` has always said. Re-freezing our IR moved exactly the hundred
and fourteen tokens the diff had named and nothing else. Eight units still
differ, and all eight are a real literal one ULP apart, where the hosted
upstream still double-rounds and we do not. Those wait for Update 58.
