# The Two Chapters Nobody Cites

*2026-08-26. Our compiler test units had been missing two files for as
long as we have been building them, and the only reason nobody noticed is
that the compiler reported the error and then produced the right answer
anyway.*

## What a "unit" is, and why we assemble one

Codex programs are written in chapters. A small test program is usually a
driver — a dozen lines that say "I use the sorting chapter" and then call
into it:

```
Chapter: BoardTypes
  cites Foreword chapter Board
```

The compiler does not go looking for `Board` on disk. Something upstream
of it must paste the cited chapters and the driver into one long file — a
*unit* — and hand that to the compiler. In the depot that job is done by
a PowerShell function called `Resolve-CiteOrder`. On our side it is done
by a 90-line Python file called `cite_resolve.py`, written to do the same
walk so that our tools compile the same program the depot's tools do.

That last clause is the whole point. Our project exists to compare two
compilers against each other. If the two are not fed the same bytes, every
disagreement is noise.

## The bug

`Resolve-CiteOrder` has a loop at the bottom of it that ours did not:

```powershell
foreach ($impl in @(@('Foreword','ListUtils'), @('Foreword','Tuple'))) {
    & $walk $impl[0] $impl[1]
}
```

Two chapters get pulled into *every* unit, whether or not anything cites
them. Not a special case, not a fallback — unconditional, before the
program's own cites are walked at all.

The reason is worth stating plainly, because it is a nice piece of
language design and it is exactly why nobody would guess it. Codex has
syntactic sugar. Write

```
  for x in xs -> f x
```

and the *desugarer* — a stage inside the compiler — rewrites it into a
call to a function named `map-list`. Write a pair like `(a, b)` and it
becomes a constructor named `MkTup2`. Those names are never typed by the
author. They are written by the compiler, into your program, on your
behalf.

So `map-list` lives in `Foreword/ListUtils.codex` and `MkTup2` lives in
`Foreword/Tuple.codex`, and if you had to *cite* those chapters to use
`for` loops and tuples, then the language's own syntax would be
conditional on a line nobody could know to write. Upstream's comment on
that loop says so in as many words: without it, `for` fails with
`CDX3002: Undefined name: map-list`.

Our resolver walked only what the source cites. So it never included
them. Every unit we have ever built was missing both.

## Why this was invisible for so long

Here is the part I find genuinely interesting.

Yesterday we turned on something we had been skipping: the compiler's
**error gate**. The real compiler driver checks, after parsing and type
checking, whether any errors were reported — and if so it refuses to
generate code. Our stripped-down harness had never done that check. It
collected the errors into a bag and then generated code regardless.

The moment the gate went on, 41 of 593 corpus programs stopped emitting
anything, and three of them were programs we had classified as
*well-behaved*: they had transpiled cleanly, built, run, and matched the
depot's own expected output, byte for byte.

Read that again, because it is the strange bit. The compiler front end
said `Undefined name: map-list`. And then the back end went ahead and
generated code that produced exactly the right answer.

That is what a missing chapter looks like when nothing downstream depends
on the error being fatal. The name was undefined, an error was filed, and
the code generator — which was never asked whether the error bag was
empty — carried on and got lucky. Turning the gate on did not create 41
new problems. It made 41 existing ones visible, and this note is about the
28 of them that were ours.

## The fix, and what it moved

Three lines of intent: walk the two implicit chapters first, then the
source's own cites, then the source. Same order upstream uses, which
matters because the compiler numbers its diagnostics against the assembled
unit — a different order is a different set of line numbers.

Measured across the whole corpus with nothing else changed:

| | before | after |
|---|---|---|
| programs the gate halts | 41 | 13 |
| correct against the depot's expected output | 178 | 179 |
| emitted Zig identical to the two-tool pipeline | 536/536 | 564/564 |
| the tier set (our unit tests) | 15 green, 7 noted | unchanged |

The residue is pleasant: on a program that uses neither tuples nor `for`
loops, the emitted Zig grows by 586 bytes of unused type declarations and
nothing else. The functions from `ListUtils` are pruned away as
unreachable; type definitions are not pruned, so the four `TupN` types
ride along harmlessly.

## The hypothesis this was supposed to prove, which it didn't

There was a second, larger pile: 112 programs the census calls *clean* —
our translator refused no construct — whose emitted Zig nonetheless will
not compile. Many of them failed on `use of undeclared identifier`, with
names like `Tup2` and `Timestamp`. That is exactly what a missing chapter
looks like from downstream, so the working theory was that both piles were
one bug and this fix would move roughly 150 programs at once.

It moved zero of them. I re-ran all 112 through the compiler and the Zig
build, before and after, one variable changed: 111 refused before, 111
refused after, and once you normalise for line numbers shifting, only four
messages differed at all.

A refuted hypothesis is still a day's work well spent, because the pile is
now characterised instead of assumed. And characterising it turned up
something better than the theory it killed.

## What was actually in the pile

Sorting the 112 by the first error Zig reports:

- **39 programs — one bug.** Our generated `main` always launches the
  program's entry point on a thread:

  ```zig
  const t = std.Thread.spawn(.{ .stack_size = stack_bytes }, opening, .{});
  ```

  Zig requires a thread's entry function to return `void`, `u8`, or
  `noreturn`. When the Codex program's entry point returns a *value* — an
  integer, a float, a string — the emitted Zig is rejected before it ever
  runs. Thirty-two return integers, six return text, one returns a float.
  That is 35% of the pile, and it is a single defect in our translator.

- **47 programs** — type mismatches inside the generated code, which need
  reading one at a time.

- **The rest** — a long tail: five want a `Frequency` type, five a
  `Timestamp`, two a 16-element tuple, and singletons after that.

- **13 programs still halt at the gate**, and they are not this bug.
  Nine are *negative tests* — programs whose entire purpose is to be
  rejected, so a compiler that rejects them is working. Four are the
  quoted-works family, and those are a harness gap of exactly the same
  shape as the error gate: the real driver splits a signed-code blob off
  the end of the source *before* tokenising it, and the shared helper our
  harness is built from starts at tokenising. Same lesson, third time:
  reuse the whole driver, not half of it.

## The lesson, which is not about chapters

Our resolver's docstring opens by claiming it does "the same walk the
depot's own bundler does". It was written carefully, by someone reading
the upstream code, and it was still wrong — because the thing it missed
was not in the part of the file that looked like the walk. It was in a
loop underneath, doing something the walk's own description would never
lead you to expect: adding dependencies nobody declared.

The instrument was lying, quietly, in the direction of "everything is
fine". It took switching on an unrelated check — the error gate — before
anything asked the question. Two of yesterday's three discoveries and both
of today's have the same root: a piece of the real driver we did not copy,
and no test that could tell.

*Ladder: `cite_resolve` implicit chapters, commit `8830e7b`.*
