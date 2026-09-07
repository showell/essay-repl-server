# What the counters count

*Written 2026-09-07. Steve asked what these four numbers actually are, and how
today's hunt worked. No compiler background assumed.*

---

## The problem the counters solve

We have two compilers for the same language: Damian's, written in Codex, and
ours, written in Rust. The strict test is that they produce **byte-identical
IR** — the intermediate document a compiler emits after it understands a
program. On the twenty-eight curated test programs we can run that test
directly: compile with both, `diff`, done.

On 3.4 megabytes of the compiler's own source we can't. Nobody has a frozen
expected answer for a file that size, and producing one would just move the
question.

So we grade something else. Both compilers, at the end of type checking, print
four numbers. If two independently written type checkers walk the same 3.4 MB
and all four numbers land on the same values, they did the same work in the
same order.

Here's what each one is.

---

## 1. `next-id` — how many placeholders the checker invented

This is the important one, so it gets the most space.

A type checker's job is to work out what type everything is. Sometimes it's
written down:

```codex
is-zig-keyword : Text -> Boolean
```

That says: takes a Text, returns a Boolean. No mystery.

But plenty of things aren't written down. A definition might have no signature
at all. A function might be generic — `list-at` works on a list of *anything*,
and what "anything" is depends on the call site. And even inside a fully
annotated function, intermediate values have types nobody stated.

When the checker meets something whose type it doesn't yet know, it does the
only sensible thing: it **invents a placeholder**. Not a guess — a named
unknown. "I don't know what this is. Call it *thing #4,197*." Then it keeps
going, and as it sees how the value gets used, it works out what #4,197 must
have been and writes that down.

This is the standard machinery of type inference, and the useful thing about
it here is that the placeholders are *numbered*, from a counter that only ever
goes up. `next-id` is that counter's final value: **the total number of
placeholders invented while checking the program.**

On the whole compiler, that is 118,066.

### Why this isn't an internal detail

You might reasonably think the numbering is private bookkeeping. It isn't.
Those numbers get **printed into the IR**:

```
(tvar 41)
```

That's a placeholder appearing in the compiler's actual output. So if our
checker invents its placeholders in a different order, or invents one more
than upstream does, every number after that point shifts — and the IR we
produce stops matching, byte for byte, for reasons that have nothing to do
with being *wrong*.

That is what makes this counter a real test rather than a proxy. We are not
measuring something correlated with correctness. We are measuring a thing that
is literally in the deliverable.

## 2. `substitutions` — where the answers get written

Every placeholder gets a slot, and when the checker figures out what #4,197
actually was, the answer goes in slot 4,197.

Upstream allocates the slot and the number together, so this counter moves in
lockstep with `next-id` — they're the same number in both arms, always. It's
worth printing anyway: if they ever *disagreed*, that would mean one of the
two compilers has a bookkeeping bug independent of anything else, and I'd want
to know immediately.

## 3. `next-row-id` — the same idea, for effects

Codex types say more than most languages': they say what a function *does*,
not only what it returns.

```codex
opening : [Console, FileSystem] Nothing
```

That reads: performs Console and FileSystem effects, returns nothing. The
`[Console, FileSystem]` part is called an **effect row**.

Rows need placeholders for exactly the same reason types do — "this function
performs some set of effects I haven't worked out yet" — and they get their
own counter. And they too reach the output. A builtin's wire type looks like:

```
(fn text nothing (row (labels (label "Console.Write" "")) "" 460))
```

The `460` is this counter. So an effect-row placeholder minted one step early
or late shows up in the IR the same way a type placeholder does.

On the whole compiler: 311,802. **Ours matched that exactly before today
started**, which was the first real sign that the checker was in good shape —
getting three hundred thousand of anything to agree by accident is not a thing
that happens.

## 4. `expr-types` — what the checker tells the next stage

The checker works out types; later stages need to *use* them. So the checker
keeps a table: for each expression, at its position in the source file, the
type decided for it.

Not every expression — only the ones later stages actually look up. Upstream
records at seven specific places, and being faithful to *which* seven is part
of matching the count. One of those places matters a lot today: **`&` is the
one operator that records an entry**, because `&` is overloaded (boolean AND,
text append, bitwise) and the recorded type is the only thing that tells later
stages which job it was doing.

On the whole compiler: 145,772.

## 5. `check-errors` — type errors found

Zero on both arms. This is the control. Without it, "our numbers match" could
mean "we both gave up in the same place." Both compilers fully accept 3.4 MB
of source, and *then* the other four numbers mean something.

---

## Why this is a good instrument

Final output tells you whether you got the right **answer**. Counters tell you
whether you got there by the same **route**.

That distinction earned its keep this morning. Our desugarer had been silently
rewriting `+` into `&` — nine definitions in one file, wherever the operator
started a continuation line. Every program still compiled. Every test stayed
green. Every byte of output was right, because Codex's `&` takes its meaning
from its left operand's type and so does `+`.

The *only* thing in the entire system that noticed was `expr-types` reading
145,776 where the oracle said 145,772. Four, out of a hundred and forty-five
thousand. That's what a route-checker buys you: a bug with no symptom becomes
a bug with a number.

The flip side is that these counters are **unbelievably blunt about
location.** "You are seven over" tells you nothing about where. Which is the
rest of this essay.

---

## Bisecting a subject that won't be cut

The idea is the obvious one: if the whole thing is +7, cut it in half and see
which half carries it. Repeat. Twenty questions.

The obstacle is that this file doesn't cut. It's a *resolved unit* — 92
chapters bundled into one compilation unit — and it isn't a pile of
independent files. Four rules bite, and I hit all four:

**One chapter alone isn't a subject.** In Codex, names are visible across a
whole compilation unit *without being imported*. So a chapter lifted out on
its own is missing names it never had to ask for, and the oracle refuses it:
`CDX3002 Undefined name: i64-min`.

**The first N chapters aren't a subject either.** The bundle isn't
dependency-ordered — chapter 46 cites a chapter that appears later in the
file. Cut anywhere and you've orphaned something.

**Some of a chapter's pages aren't a subject.** A chapter split across several
files declares how many: `of 14`. Include two of the fourteen and you get
`CDX3004 spans 2 files but this page declares 'of 14'`. This one cost me two
false starts, because it reads exactly like a compiler bug until you notice
the page count is a *declared invariant* the file is asserting about itself.

**And satisfying any one of these can violate another.** Pulling in a cited
chapter drags in its pages, which reference more names, which pull in more
chapters. So the set has to be grown to a **fixed point** — keep applying all
four rules until nothing changes — rather than computed in one pass.

So the tool for today wasn't a bisection script. It was a thing that answers:
*given a chapter, what is the smallest valid subject containing it?*

### The shortcut that didn't work

I first tried computing the name rule statically: tokenize each chapter, work
out which names it uses, subtract the ones it binds locally (`let x =`,
parameters, lambda arguments), and pull in whoever defines the rest. No oracle
in the loop, so it'd be fast.

It collapses. **Every single target came out as the same 64 chapters and
51,600 lines** — the whole middle of the compiler, every time. Subtracting
local bindings didn't rescue it. The approximation is too loose: enough
incidental name collisions and everything reaches everything.

Asking the oracle for one undefined name at a time is slower per step and
gives genuinely minimal subjects. Chapter 49 needs **7 chapters and 765
lines**, not 64 and 51,600. An over-approximation isn't a bisection; it's a
tautology with a runtime.

---

## The actual hunt

**Pass one.** For each of the 92 chapters, build its smallest valid subject,
run both compilers, compare. 56 chapters measured, **every one clean.** The
other 35 tripped a size cap I'd set too tight — they're the back half of the
compiler, where the subjects run to tens of thousands of lines.

**Pass two, and the good moment.** The first result back was chapter 22,
`Builtins`. Its minimal valid subject is **50,869 of the unit's 71,967 lines**
— and it's clean on all three counters.

That single measurement exonerated about 70% of the compiler at once,
including all fourteen X86-64 code generator pages and most of the chapters
still queued for individual testing. Which is the nice property of a fixed
point: it doesn't give you the chapter you asked for, it gives you a large
self-consistent region, and a clean region is worth far more than a clean
chapter.

Eleven candidates left. Ten came back clean — Name Resolution, both Lowering
pages, Resolve Types, IR Text Emitter, IRCheck, Passes, Codex Emitter, Zig
Emitter, and CheckHarness's own dependencies.

**Chapter 88, `Opening`, came back +7.** The whole gap, in one chapter, with
expression types and rows still exact. Opening is the compiler's driver — the
top-level program that runs all the phases.

## The correction

Obvious next move: bisect inside Opening's 2,387 lines the way we did in
ringplug this morning. Cut it at line 1,200, see which half carries the +7.

So I ran the endpoints first, to check the bisection was well-posed. Truncate
Opening to its **first line** — essentially delete it — and the subject still
reads **+7**.

Which means Opening isn't guilty. Opening's *closure* is. Opening is the
driver, so it references nearly everything, so building the smallest valid
subject containing Opening drags in 87 of 92 chapters — including a handful
that nothing else pulled in. The delta is in one of *those*, and Opening was
just the chapter whose gravity happened to collect it.

That's a real methodological point and I nearly walked past it: **a dirty
closure does not mean a dirty chapter.** Every clean result in this sweep is
sound — a clean closure genuinely exonerates everything in it. But a dirty
result only tells you the *set* is dirty, and the set can be much bigger than
the thing you were asking about. The asymmetry is easy to miss because the
clean case is so well-behaved.

Running the endpoints before the bisection is what caught it, and that was
luck as much as discipline — I did it to check the instrument, not because I
suspected anything.

## The answer was already on my screen

The set difference gave eighteen candidates, and one of them stopped me cold.

Chapter 85, `Fat16`: **+7, in a six-chapter, 3,919-line subject.** That result
was in the *first* sweep. It had been sitting in the output file for an hour.

I'd missed it because of how I summarised. I counted "56 clean, 35 skipped",
noticed that's 91 of 92, and moved on to the second pass. The one chapter I
didn't account for was the one carrying the whole bug. A tally that doesn't
balance is a question, and I treated it as a rounding error.

Opening was never the culprit — it just has enough gravity to pull Fat16 into
its closure, which is exactly what the endpoint check had already told me.

## Seven field accesses

Fat16 is a chapter built almost entirely of records — disk volumes, directory
entries — so the obvious suspect was field access. I instrumented our checker
to log every field lookup that *failed* and fell back to inventing a
placeholder.

Seven. Exactly seven, on the nose:

```
3  FIELD-MISS obj=None field=li-entries
2  FIELD-MISS obj=None field=li-lfn
2  FIELD-MISS obj=None field=gd-partitions
```

`obj=None` means the thing we were taking a field *of* hadn't resolved to a
record at all. We didn't know what it was, so we couldn't look the field up,
so we invented a placeholder. Upstream knew, looked it up, and invented
nothing.

Every one of the seven had the same shape:

```codex
here <- fat16-cluster-entry-sectors vol (fat16-cluster-sector vol cluster) ...
...
else fat16-cluster-entries-walk vol next (here.li-entries) saved power ...
```

That `<-` is Codex's effectful bind: *run this thing that touches the disk,
call the result `here`.* Then a few lines later, `here.li-entries`.

And our checker's code for that statement was:

```rust
crate::ast::ActStmt::Exec(x, _) | crate::ast::ActStmt::Bind(_, x, _) => {
```

Look at the `Bind` arm. `Bind(_, x, _)` — the first field is **the name being
bound**, and it's matched with `_`. We inferred the statement, we unioned its
effects, and then we threw the name away. So `here` was never in scope, and
`here.li-entries` was a field access on something the checker had no
information about.

Upstream's rule, three lines of Codex:

```codex
is AActBindStmt (name) (e) (s) ->
  let er = infer-expr-at st env e (depth + 1)
  ...
  in let env2 = env-bind-local env (name.value) (deep-resolve acc-st (er.inferred-type))
```

Bind the name, to the fully-resolved type. Exactly what `let` already did in
our checker two arms further down — we'd got it right for `let` and never
written it for `<-`.

Reproduced in eleven lines, fixed in about fifteen, and:

```
codexcheck-subject.codex — 3.44 MB, 92 chapters, 7,207 definitions

                    oracle      ours
substitutions      118,066   118,066
next-id            118,066   118,066
next-row-id        311,802   311,802
expr-types         145,772   145,772
check-errors             0         0
```

**Every counter, exact, on the entire Cobblestone compiler.** Two type
checkers written independently in two languages, walking 3.4 megabytes of
source, inventing a hundred and eighteen thousand placeholders and three
hundred and eleven thousand effect rows — in the same order, to the last one.

Gates all green: 172 unit tests, the curated 28 passing on the interpreter, 28
agreeing byte-for-byte on native compilation, 28 identical through the two-host
IR check, safari's 54 specs and 2,351 values.

## What I'd keep from this

**The counters were the only thing that could have found this.** A discarded
`<-` binding sounds catastrophic and wasn't: the programs still compiled, the
IR was still right, every test stayed green. The checker just did slightly
more work than it needed to, in a way that showed up as seven numbers out of
a hundred and eighteen thousand.

**Two of today's three bugs were invisible to output.** The `+`→`&` rewrite
and this one both produced correct programs. Only the route was wrong. If we
were grading on output alone, both would still be in there, quietly waiting
for the day some other change made them matter.

**The instrument cost more than the fix.** Fifteen lines of Rust, versus an
afternoon of building something that can cut a file that isn't supposed to be
cut. That's the usual ratio, and it's worth remembering when the instrument
feels like a detour — the next counter gap will cost a fraction of this one,
because the subset builder is written now.

**And read your own output.** The answer was on screen an hour before I saw
it, because I summarised 92 into "56 and 35" and didn't ask about the one left
over.

---

## The short version, if you skipped the middle

- The four counters measure **how the checker got there**, not just where it
  ended up — and because the numbers reach the IR, "how" is part of the
  deliverable.
- Two independent compilers now agree exactly on 311,802 effect rows and
  145,772 expression types across the whole Cobblestone compiler, and on all
  four counters for the smaller 388 KB subject.
- The gap is **closed**: all five counters agree exactly on the whole 3.44 MB
  compiler, and on the 388 KB subject too. It was a `<-` bind whose name the
  checker discarded.
- Most of today's work was building an instrument that can cut a file that
  isn't supposed to be cut. That part is reusable; the next counter gap will
  cost a fraction of this one.
