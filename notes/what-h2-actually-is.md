# What H2 actually is, and what we think fixes it

*2026-08-27, written while the verification chain runs on the wrapper fix.*

## The one-sentence version

When Codex hands our zig plug a lambda, some of that lambda's parameters
arrive with **no type at all** — the wire literally says `error` where a
type should be. Four other plugs paper over this with a guess. Zig will not
let us guess. So the fix is to **go find the type**, which is possible more
often than it looks, because the answer is almost always sitting one node
away in the very same IR.

## Where the `error` comes from

Nothing is broken upstream. The compiler is doing something reasonable that
happens to lose information a statically typed target needs.

When the compiler lowers `let f = \i -> ...`, it lowers the bound value
with "no expectation" — and its way of spelling *no expectation* is the
type `ErrorTy`. A lambda then peels its parameter types off that
expectation. Peel a parameter off "no expectation" and you get "no
expectation" back. So the parameter's type cell comes out `error`.

The type checker **did** solve for that parameter. It knows what `i` is.
Nobody asks it before the IR is written, and by the time the IR reaches a
plug the answer is gone.

For a plug targeting a dynamically typed language, who cares — Python
doesn't need the annotation. For C# you write `object`; for Rust,
`Box<dyn Any>`. Zig has neither. Zig needs a real type in the signature or
it will not compile the function.

## Why this is ours and not theirs

This is the part that reversed direction this morning, and it's worth
stating plainly because we spent time going the wrong way.

`ErrorTy` on the IR wire is not an anomaly. It's a **contract the fleet
answers**. Four sibling plugs have an explicit arm for it:

- C# → `object`
- Rust → `Box<dyn std::any::Any>`
- Ada → `Long_Long_Integer`
- Fortran → `integer(8)`

Our `emit-zig-type` and C#'s `cs-type` are arm-for-arm parallel — same
cases, same order — and ours is the only one missing this arm. So the plug
that is behaving oddly is *ours*. Bare metal runs all twelve Roc test
programs fine. Nothing upstream needs changing for them to work.

## Why we can't copy the sibling answer

Ada and Fortran answer `i64`. That looks tempting and it is wrong, and we
have a test that proves it's wrong.

The H2 matrix has seven cases. Six of them have `Integer` as the true
answer — which is also the language's default — so a plug that just
defaulted every unknown parameter to `Integer` would pass six of seven and
look great. Case f is deliberately `Text`. A guesser fails there visibly.

C# and Rust answer with a universal dynamic type. Zig has none; our own
source already records that `anyopaque` is not accepted as a parameter type
at all.

So the only honest answer for zig is **the actual type**, recovered.

## The recovery, in plain terms

Two places to look, and both are inside the IR we already have.

**Source one: the lambda's own body.** The parameter cell says `error`, but
three lines down the body reads `(name "acc" int-default)` — the *use* of
the parameter carries the type the parameter's declaration lost. So: walk
the body, find a use of this name, take its type. This is not a trick; it's
the same technique the compiler's own lambda-lifting pass uses to type the
values a closure captures.

**Source two: the callee.** Sometimes the parameter is never used inside the
body — it's only passed onward as an argument. `\xs base step -> fold-loop
xs base step` never *uses* `step`, it hands it to `fold-loop`. But
`fold-loop` has a declared type, and that declaration rides along on the
name node in the same expression. Count how deep in the apply spine the
argument sits, take that numbered parameter off the callee's declared type,
and that's your answer.

Between them these two cover most of what we're missing.

## The rule that keeps recovery honest

A walk that goes looking for "a use of the name `i`" can easily find the
*wrong* `i`. If the body contains `let i = "hello" in ...`, that inner `i`
is a different variable and its type says nothing about our parameter.

This matters more than it sounds, because getting it wrong doesn't produce a
refusal — it produces a **confidently wrong type**, which is exactly the
failure mode we're trying to eliminate. A guess that zig immediately
contradicts is a hypothesis; a guess that produces a plausible wrong type is
a bug in waiting.

So both walks stop at every rebinding: a `let` of the same name, a nested
lambda that takes it as a parameter, a match branch whose pattern binds it,
and an `act` block binding it partway through. Three of those four were
already handled; two were found and closed today, one of them by going and
looking for the sibling mechanism after fixing the first.

## What the first real build taught us

The recovery works. From the first build, straight off the wire:

```
fn __lam_2(i: i64) i64                            recovered from its own body
fn __lam_3(base: i64, step: CxFn1(i64, i64)) i64  recovered from the callee
fn __lam_6(s: []const u8) []const u8              case f — Text, not a lucky i64
```

That third line is the one that matters most. It is the cell that separates
recovery from guessing, and it came out `Text`.

**And the matrix still didn't build.** Because a lambda in this plug gets
typed **twice**, in two different places, from two different sources:

1. the lifted `fn __lam_N(...)` definition, which now recovers, and
2. the **closure struct** built when that lambda is used as a *value* —
   which reads the function type riding on the name node, and that type
   still said `error`.

So the definition came out right and its wrapper came out refused, and since
one refusal marker anywhere takes the whole zig file down, the definition
being right bought us exactly nothing.

That's the wrapper fix, and it's what's on the box right now: the wrapper
patches its unanswered slots from the definition's recovered parameters.
The two readings of one lambda now agree.

## The subtle one a cold reader caught

Worth recording because I wrote it and didn't see it.

The wrapper isn't always built for a *whole* function. It's often built for
a **partially applied** one — `fold-loop xs base` with the last argument
still to come. In that case the type being patched covers only the
*remaining* parameters. Slot 0 of that type is not parameter 0 of the
definition; it's parameter *N* where N is how many arguments were already
supplied.

Patching from 0 hands the trampoline the type of a parameter that was
already consumed — for one of our test cases, a list type where an integer
belongs. **A wrong answer, not a refusal.** Sometimes zig catches it at the
generated call; sometimes the two types both happen to be `i64` and it slips
through silently.

The function's own arithmetic said so two lines apart the whole time. The
fix is one offset. The reason it's worth a paragraph is that it is precisely
the class of bug the rebinding rule above exists to prevent, reintroduced by
me in a different place ninety minutes later.

Same read also caught: an `error` **buried inside** a type — `(fn error
error)` — was passing through untouched, because the check only looked at
the outermost node. That renders a refusal marker *inside* `CxFn1(...)`,
where our own "is this type unmapped" test structurally cannot see it. The
question asked of a slot is now "does it contain an error anywhere", and a
recovered answer is only taken if it's clean.

## What still refuses, and why that's correct

Two of the seven matrix cases keep their refusal, and both should:

- **Case g** binds a lambda and never applies it. Nothing anywhere
  constrains its parameter. `error` is the honest answer here, and a plug
  that invented a type would be lying.
- **Case a** has an unused parameter — `\i -> xs`. Its own body says
  nothing about `i`, and it is never passed as an argument, so neither
  source can see it. The type *is* knowable, but only from how the
  **binding** is applied out in the enclosing function (`f 0`), which is a
  third source neither walk has. That's the next piece of work, and it's a
  real one, not a footnote — it's the shape of `roc-closure-captures-list`.

## What we don't know yet

Honestly: whether this moves the eight refusing Roc ports. The build before
the wrapper fix moved **nothing** — corpus identical to the pinned census
cell for cell (318/268/24/23/2/1), Roc ports still 3 match / 8 refuse — and
that was the expected result once the wrapper was identified as the gate.
The run on the box now is the first one that can move them.

The other thing worth knowing is that the fixed point held: `codexzig`
rebuilt from this branch and re-emitted its own 2.36 MB bundle
byte-identically. Whatever we've done, we haven't made the compiler a
different compiler.
