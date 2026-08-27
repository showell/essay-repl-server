# The unconstrained-type question

*For Steve. 2026-08-27 evening, after findings 59, 60, 61, 62 and 63.*

---

## The question, stated as narrowly as I can make it

Some programs contain a type that nothing determines. Not a type we failed to
carry — a type that genuinely has no answer, because no line of the program
ever depends on what it is.

    case-g       let h = \k -> 1 in n              nothing ever applies h
    list-test    cl-is-empty (cl-nil)              is-empty never looks at an element
    roc-alias-empty   x = [] ; y = x ; length y    only the length is ever asked

Bare metal runs all three without blinking, because a machine word is a machine
word and nobody asked what it meant. Zig cannot: it wants a type for the slot,
and there isn't one to give.

So: **what should our backend emit for a type the program does not constrain?**

Three answers are available. Refuse. Pick something. Or get the compiler to
say which case we are in. I think the third is the only one that is right for
the long term, and I want to lay out why the other two are more dangerous than
they look — particularly the second, which is the tempting one.

## Why any answer is safe, if the premise holds

There is a real theorem underneath the tempting answer, and it is worth stating
properly rather than gesturing at.

If a type variable is genuinely free after solving, then by parametricity no
observable behaviour of the program can depend on which type is chosen for it.
A function polymorphic in `a` cannot inspect an `a`; all it can do is move one
around. `cl-is-empty` looks at a constructor tag, never at a payload. `length`
counts cells. `case-g` never enters `h` at all. Substituting `Integer` for `a`,
or `Bool`, or an empty struct, cannot change what any of these print.

So if we KNOW the variable is free, defaulting is not a hack. It is the
correct compilation of a program whose meaning does not mention the type. That
is a genuinely strong argument and I do not want to undersell it, because the
case against defaulting is not "it might be wrong in principle."

The case against it is that we cannot currently tell when the premise holds.

## The premise is exactly the thing we keep getting wrong

Today we found four separate places where the compiler had solved a type and
the IR did not carry it:

- **57** — a branch join kept a variable both of its branches had resolved.
- **58** — an empty list literal's solved element type was never recorded.
- **59** — a list literal took a variable that is bound nowhere over its own
  correctly-typed elements.
- **PR 93 / COMPILER-30** — every lambda in the language was filed under a
  synthetic span, so the checker's answer could never be looked up.

In every one of those, the wire showed a type variable or an `ErrorTy`, and the
honest reading of that wire — the one the plug is able to make — was
"unconstrained". In every one of those, the honest reading was **wrong**. The
answer existed. Something dropped it.

That is the whole difficulty. **On the wire, "genuinely free" and "we lost it"
are spelled identically.** A bare `tvar 618` looks exactly like a bare `tvar
25` looked before finding 59, and exactly like the `error` cells looked before
PR 93. The plug has no way to distinguish a type that has no answer from a type
whose answer was mislaid, because the distinction lives in a unification state
the plug never sees.

A defaulting rule in the plug is therefore not a decision about unconstrained
types. It is a decision to stop being able to detect a whole class of compiler
defects — the class we have found four of in one day. Every future instance
would compile, run, and produce a plausible answer.

## The failure mode we would be reproducing, in our own words

We sent PR 93 this afternoon. Its central evidence is a table:

| plug | answer | what that is |
|---|---|---|
| C# | `object` | erase |
| Rust | `Box<dyn Any>` | erase |
| Ada | `Long_Long_Integer` | **guess** |
| Fortran | `integer(8)` | **guess** |

and the sentence that carries it: *"This is not four plugs honouring a
contract. It is four workarounds for one missing fact, two of which silently
miscompile."* Case f of the matrix — a lambda parameter whose true type is
`Text` — is what refutes the guess.

If we answer the unconstrained-type question with "default to `i64`", **we
become the fifth row of that table**, and the argument we just made upstream
becomes an argument against us. Not rhetorically: mechanically. Ada guesses a
64-bit integer for a type it does not know, and is wrong whenever the type was
`Text` and something dropped it. We would guess a 64-bit integer for a type we
do not know, and be wrong in exactly the same circumstances, for exactly the
same reason.

That is not an argument from consistency or embarrassment. It is that Ada's
authors presumably reasoned the way I would be reasoning: *this only fires when
the type is unknowable, and when it is unknowable any answer works.* They were
right about the theorem and wrong about the premise, and their plug now
miscompiles `Text` parameters in silence. The theorem does not protect you when
the premise is unverified.

## What I think we should do

**The long-term answer is that the compiler must distinguish the two cases on
the wire, because it is the only place where the distinction exists.**

After unification finishes, the compiler knows perfectly well whether a
variable was solved or is still free. That is not an inference; it is a lookup
in the state it already holds. A variable that is free after solving is a fact
about the program. A variable that was solved but not recorded is a compiler
defect. Today they arrive spelled the same, and that is what should change.

Concretely, the wire wants a form that says *free*, distinct from a type
variable in scope and distinct from `ErrorTy`. Then:

- A plug seeing the free form may default with confidence, and the choice is
  provably invisible.
- A plug seeing a bare in-scope variable knows it is inside a generic and can
  thread a comptime parameter.
- A plug seeing `ErrorTy` knows something is wrong, which is what that atom
  should have meant all along.

This is the same argument as PR 93 and the same argument as the `ErrorTy`
sentinel collision, one layer along: **one spelling for two facts is what makes
a backend guess, and the fix is to spell them differently.** It is also work
Damian said he was open to, in the terms he used — *"a thing we never needed
till now. You found the gap, and we can fill it."* This is another such gap,
and it is smaller than the last one: the information is already computed, and
`is-synthetic-span`-style plumbing is not even required, because the free-ness
is a property of the type rather than of a span.

**Until that exists, refusing by name is the correct behaviour and we should
keep it.** It is what the emitter does today — `no element type for this empty
list`, `unresolved type variable T16 of __lam_0` — and every one of those
refusals is a true statement. Eight corpus programs sit behind them. Eight
programs is a real cost and it is the right cost: those refusals are what
surfaced findings 57 through 62, and a defaulting rule would have converted all
six of those findings into silence.

**And when we do default — after the wire can tell us — the choice should be a
zero-sized type, not an integer.** This is the part I feel most strongly about
and it is the cheapest insurance available.

If the premise holds, a zero-sized type is as correct as any other, by the
theorem above. If the premise is violated — if the type was actually determined
and something dropped it — then:

- an `i64` default **compiles and runs and gives a wrong answer**, because
  almost anything you might do with a mislaid type also typechecks against a
  64-bit integer;
- a zero-sized default **fails to compile**, loudly, at the first line that
  actually uses the value as anything.

That asymmetry is worth more than any elegance. It makes the default
self-checking: it is correct exactly when it is safe and it breaks visibly when
it is not. It is the difference between the Ada row of that table and a plug
that cannot silently miscompile. `doctrine_eliminate_dont_paper_over` says
fail-loud is the floor, and this is the one place where the floor is available
for free.

## One correction to the question itself

Some of what I have been filing under "unconstrained type" is not that, and it
is worth separating before any of the above gets built.

**Matrix case g is an UNUSED VALUE, not an unconstrained type.** `let h = \k ->
1 in n` — `h` is never read. There is no need to invent a type for `h`, because
there is no need to emit `h` at all. The right answer there is to not
materialise the binding, which is finding 60 and 63's territory, and the type
question never arises.

`list-test` and `roc-alias-empty` are different: their values ARE used, just
never in a way that inspects an element. `cl-nil` is passed to `cl-is-empty`;
the empty list's length is taken. Those genuinely need a type for a slot, and
they are the real instances.

So before designing anything, the eight programs behind these markers should be
split into *unused value* and *used value with a free type*. I would expect the
first group to be closed by finishing the discard work and the second to be
smaller than eight. Designing a defaulting rule for programs that turn out not
to need one is the kind of work that looks like progress and is not.

## Summary

1. **Do not default in the plug today.** The plug cannot distinguish a free
   type from a mislaid one, and four findings in one day say mislaid is
   common. Defaulting would trade a class of detectable compiler defects for
   silence.
2. **Refusing by name is correct in the meantime** and should stay. The eight
   blocked programs are paying for a detector that has already earned its keep
   six times today.
3. **The real fix is upstream and is the same shape as PR 93:** the compiler
   knows whether a variable is free after solving, and the wire should say so.
   That makes defaulting safe rather than merely convenient.
4. **When we default, use a zero-sized type.** It is correct when the premise
   holds and fails loudly when it does not. An integer default is the Ada row
   of the table we just sent upstream, and it fails silently in exactly the
   circumstances we cannot currently detect.
5. **First, separate the unused values from the free types.** Some of this
   question dissolves rather than being answered.
