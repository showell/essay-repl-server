# `gen-eq-def`: the one-line change that zeroed our counter gate

*2026-09-09*

## First, the correction

This is **not** something we send to Damian. There is no PR here and no issue.

`gen-eq-def` is upstream's feature, upstream implemented it correctly, and it
works. The gap is entirely on our side: our Rust front end does not do the same
thing, so it produces different numbers. Nothing goes on the `u58-candidate`
branch, because that branch is for changes to *Cobblestone*, and Cobblestone
does not need changing.

The work is in `rust-codex-compiler`, in our desugarer, and it is a porting job.

## What the feature is

Codex lets you write `x == y` on your own types. Somebody has to supply the
comparison. The compiler generates it: for a type `T`, it synthesises a
definition called `__eq_T` that takes two `T`s and returns a `Boolean`, and
whose body walks the structure — match on the left value, match on the right,
compare the payloads.

You never see it. It has no source location, because there is no source. Every
span inside it is a `synthetic-span`.

That much has been true for a while.

## What changed, and it is one line

Here is the whole thing, in `codex/compiler/Ast/Desugarer.codex` line 664:

```
U55:  if deriving-has (td.deriving) "Eq" | td-self-recursive td
U56:  if deriving-has (td.deriving) "Eq" | td-eq-safe   td
```

The generator did not change. The **guard** did — the test deciding which types
get one.

At U55 you got a generated equality if you asked for it (`deriving Eq`) or if
your type was **self-recursive** — a linked list, a tree, something that
contains itself. A narrow set.

At U56 the second condition became `td-eq-safe`, which is:

```
td-eq-safe (td) =
   when td.body
    is VariantBody (ctors) -> ctors-eq-safe ctors 0 (list-length ctors)
    is otherwise -> False

ctors-eq-safe (ctors) (i) (len) =
   if i >= len then True
   else if fields-name-type (...) "Real" ... then False
   else ctors-eq-safe ctors (i + 1) len
```

Read plainly: **it is a sum type, and no constructor carries a `Real`.** That is
the entire test. `Real` is excluded because floating-point equality is a trap —
`NaN` is not equal to itself, so a generated structural comparison would be
quietly wrong.

Everything else qualifies. Which is very nearly every sum type anyone writes.

## Why that zeroed our counter gate

The counter gate compares five numbers between our front end and upstream's on
the same program: type-variable substitutions, next-id, next-row-id,
expr-types, check-errors. Exact agreement on all five, or the unit diverges.

Generating a definition costs type variables. Two parameters, a declared type
`T -> T -> Boolean`, a body full of matches — every one of those needs a fresh
variable minted during checking. Upstream mints them. We do not, because we
never generate the definition.

So on essentially every unit we come out **about 64 short**:

```
int-pow          ours[323 323 586 233]   oracle[387 387 586 233]
handler-smoke    ours[303 303 500 227]   oracle[367 367 500 227]
induction-list   ours[284 284 472 199]   oracle[346 346 472 198]
```

Look at what moves and what does not. Substitutions and next-id are up 64.
`next-row-id` is **identical**. `expr-types` is identical.

That shape is the fingerprint, and it says precisely what happened. Row ids come
from record and variant *rows*, and a generated equality declares no new type,
so no rows. `expr-types` records the type of each expression **keyed by span** —
and every span in a generated definition is synthetic, so nothing gets recorded.

A definition minted with no rows and no spans is exactly a definition we do not
synthesise. The counters told us the shape before we found the line.

Why *64* and roughly constant regardless of the program? Because it is not the
program's own types doing it. Every resolved corpus unit carries the same
foreword chapters — `ListUtils`, `Tuple`, `Console` — and those bring a fixed
set of sum types with them. The unit's own types add a little on top, which is
why `induction-list` shows 62 rather than 64.

**1,001 units agreed before U56. Zero agree now.** Not a thousand defects: one
missing feature, counted a thousand times.

## Why the emitted IR barely moved

Here is the part that is genuinely interesting.

While the counters collapsed from 1,001 to 0, the IR wire went the *other* way:
`identical` rose from 864 to 865. The bytes we emit agree with upstream's on
more programs than before, not fewer.

Both readings are correct. Generated equalities are minted at **registration**
and then **pruned before emission** — nothing calls `__eq_ListUtils_Foo` in a
program that never compares two of them, and unreachable definitions are removed
before the IR is written. So they cost 64 type variables in every unit and reach
the wire in almost none.

This is worth holding on to, because it cuts both ways. We had already recorded
that the counters are blind to what a later pass prunes — that was learned when
several units came out byte-identical while four definitions were named `"    "`.
This is the same blindness seen from the other side: a **total** counter
divergence sitting on top of an IR ratchet that went **up**.

Neither instrument is sufficient. The counters found the cause in ninety seconds
by shape. The wire says how much of it actually matters. If we only had the
counters we would think the sky had fallen; if we only had the wire we would not
know anything had changed at all.

The one place it does reach the wire is the compiler compiling *itself*, where
something genuinely does compare two `TokenKind`s. On that subject, `__eq_TokenKind`
is the single definition the oracle emits and we emit nothing for.

## A prediction that was registered in advance, and held

Before Update 56 landed, an essay here argued that the richest vein for new
compiler work was synthesised definitions — deriving, classes, instances — and
that any new feature of that shape would land there first and would show up in
our counters before anywhere else.

It did, exactly. That is worth saying not because the guess was clever but
because it was written **down, beforehand**, which is the only thing that makes a
prediction worth anything. A pattern noticed after the fact is a story.

## What we do about it

Implement `gen-eq-def` in our desugarer. Concretely, our port needs to:

1. run the same guard — a sum type, no `Real` in any constructor field, or an
   explicit `deriving Eq`
2. synthesise the same definition, with the same name `__eq_<T>`, the same two
   parameters, the same declared type, and the same match-on-both-sides body
3. give every node a synthetic span, so that `expr-types` does **not** move —
   that is the check that we did it the same way rather than merely did
   something similar
4. register it at the same point in the pipeline, so the type variables are
   minted in the same order

Step 4 is the one that will be fiddly, and step 3 is the one that will tell us
whether we got it right. If our `expr-types` moves, we have generated the
definition but recorded spans for it, and that is a different bug wearing the
same clothes.

The success condition is unusually crisp: **the counter gate goes from 0 agree
to something in the high hundreds in one change.** Nothing else we could do to
that gate moves it at all until this lands, because every unit is failing for
this one reason. It is the single highest-leverage item on the board.

## What it does not fix

It will not move the IR ratchet much, for the pruning reason above. The 164
units whose emitted bytes differ are a separate work queue with separate causes,
and they will still be there afterwards.

That is fine. They are different questions and they deserve different answers.
What matters is that until `gen-eq-def` lands, the counter gate cannot be read
*at all* — every unit is red for a reason that tells us nothing about that unit.
Afterwards, whatever is still red is news.
