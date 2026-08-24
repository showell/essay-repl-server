# Tail Calls and the Shape of a Loop

*2026-08-24. Finding 33: why the zig plug ran out of stack where bare
metal used none, and what changing it actually required.*

## The symptom

`native/zigemit` — the plug's own emitter, compiled to a native Linux
binary — was handed the 13.2 MB IR of the compiler's back-end unit and
died. Not with a wrong answer, not with a diagnostic: it exhausted its
thread's stack inside `tokenize-collect`, the lexer's main loop. The
measurements from the night it was found: 512 MB of stack dies, 2 GiB
dies, 3.5 GiB gets through tokenizing and then hits a different wall
(finding 34, the arena). The IR holds 3,282,147 tokens and
`tokenize-collect` advances exactly one token per call.

Bare metal compiles the same thing with no stack growth at all.

## Why the two arms differ

`tokenize-collect` calls itself, and the call is the last thing it does
— its result is the caller's result, unmodified. That is a *tail call*,
and a tail call needs no frame: the caller has nothing left to do, so
the callee can reuse the caller's frame. The compiler's own x86 back end
knows this. It threads a flag called `st-set-tail-pos` through emission,
and where that flag is set a self-call becomes a jump. Depth zero,
however long the input.

The zig plug knew nothing about tail position. Every call was a call. In
a Debug build a frame of that function is a few hundred bytes, so three
million tokens is roughly a gigabyte of stack that exists only to be
unwound at the end.

This is a faithfulness gap rather than a performance nicety. Both arms
compute the same answer for any input small enough to finish; they
disagree about which inputs finish at all. The ladder's whole premise is
that the two arms should be indistinguishable, and "works up to about
two million tokens" is a distinction.

## What the fix has to do

The transformation itself is old and well understood: a self tail call
becomes a loop. Parameters become mutable locals, the tail call assigns
the next values and jumps back to the top.

```
fn f(n: i64, acc: i64) i64 {          fn f(n: i64, acc: i64) i64 {
    if (n == 0) return acc;               var _tl_n = n;
    return f(n - 1, acc + 1);   ==>       var _tl_acc = acc;
}                                         while (true) {
                                              if (_tl_n == 0) return _tl_acc;
                                              const t0 = _tl_n - 1;
                                              const t1 = _tl_acc + 1;
                                              _tl_n = t0; _tl_acc = t1;
                                              continue;
                                          }
                                      }
```

Three details in that sketch are the whole difficulty.

**The vars cannot be the parameters.** Zig's function parameters are
immutable, and zig forbids shadowing them, so the loop's state needs
different names and every mention of a parameter in the body has to be
rewritten to the new name. The emitter already has a rename table for
exactly this problem — lambdas and shadowed parameters use it — so the
loop borrows it rather than inventing a second one.

**The arguments must be evaluated before any assignment.** Consider
`loop next (acc & [x]) i`: the new accumulator is built *from* the old
one. Assign left to right and the second argument reads a variable the
first argument already overwrote. So each argument goes into a
temporary first, and only then do the variables take their new values.
This is the kind of bug that produces a plausible wrong answer rather
than a crash, which is the worse kind.

**The tail position has to be found, not assumed.** And this is where
the real work was.

## The spine

The emitter builds every definition as a single expression. A `let` is
an expression — a labeled block that breaks with a value. An `if` is an
expression. A `when` is a switch expression. The whole body of a
function is one `return <expr>;`.

But a loop needs *statements*. You cannot `continue` out of the middle
of an expression; `continue` is a statement, and the construct it jumps
out of has to be a statement too. So the tail positions of a definition
— and only those — need a second, statement-shaped emission path
alongside the expression one.

Which tail positions? The obvious answer is "the ones after `if`", and
the obvious answer would have failed. Here is the loop the finding is
actually about, cleaned up:

```
  tokenize-collect (st) (acc) (ceiling) =
   if <deck is nearly full>
    then LexCollected { ...refusal... }
   else when scan-token st
    is LexToken (tok) (next) ->
     if tok.kind == EndOfFile then LexCollected { ...done... }
      else tokenize-collect next (push acc tok) ceiling
    is LexEnd ->
     LexCollected { ...done... }
```

The tail call is four levels down: **if → when → if → self-call**. An
if-only spine walk would have transformed nothing here and reported
success. So the walk descends `if` branches, `let` bodies, and the arms
of an unguarded `when` — and the arms are why a switch prong now has to
be able to hold statements as well as a value.

Of the compiler's 114 `*-loop` definitions, 101 open with `if` and 9
with `let`; the rest are shaped like the one above. All of them are on
the spine the walk now covers.

## The refusal that isn't one

The emitter has a standing rule, learned expensively: never map an
unhandled construct onto a valid-but-different one. A vector pattern the
emitter didn't implement was once rendered as `else =>`, silently
turning it into a catch-all, and the obvious fix would have silently
dropped a real arm. Unhandled constructs now emit `@compileError` naming
the gap.

This change is the one place where that rule correctly does *not*
apply, and it is worth being precise about why. A tail position the walk
doesn't descend into simply emits `return <expr>;` — exactly what the
emitter did yesterday for every definition. The recursion inside it stays
recursion. The program is correct either way; what varies is only whether
it also gets the loop.

That is the difference between a *translation* and an *optimization*. A
translation that meets a construct it doesn't understand must refuse,
because guessing produces a wrong program. An optimization that meets one
must decline quietly, because its fallback is the correct program it was
trying to improve on. Refusing here would turn every unhandled shape into
a build failure for no gain in correctness.

So the feature's reach is a property of how deep the spine walk goes,
and that is a thing you can measure and extend, rather than a thing that
breaks.

## The probe

The measurement harness came before the measurement:
`findings/probe-tail-loop.codex`, four definitions.

- `count-if` — tail call under an `if`
- `count-let` — a `let` binding between the `if` and the call
- `count-match` — the call in a `when` arm: tokenize-collect's own shape
- `sum-nontail` — `n + sum-to (n - 1)`, where the call is *not* in tail
  position because its result feeds an addition

The last one is the control, and it is the one I care most about. An
emitter that turns it into a loop is wrong — it would be discarding the
pending addition — and it would be wrong in a way that produces a
plausible number rather than a crash. `sum-nontail 1000` must stay
500500.

Bare metal has answered: 200000, 200000, 200000, 500500. The zig arm
answers once the natives finish rebuilding.

## Where it stands

The emitter change compiles, the plug builds, and the three warmup
oracles pass — which proves no regression and nothing else, since none
of those three programs contains a tail call. The evidence that matters
is the probe's zig column and then `zigemit` getting past tokenizing on
the 13 MB IR with the stock 512 MB stack, which is the finding's own
test.

One thing found in passing, unrelated to tail calls: last night's rung
rename left two bundlers — the ones for `codexir` and `zigc` — still
delegating to a script that no longer exists under that name. Neither is
part of the fourteen-rung sweep, so the rename's own verification pass,
which was green on all fourteen, could not have caught them. They failed
the moment the native build next ran, loudly, naming the missing file.
The rename proposal had worried about the opposite failure: a stale name
quietly selecting a real-but-wrong artifact and reading as green. Getting
the loud one is the good outcome, and it is worth noticing which of the
two you got.
