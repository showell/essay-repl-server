# One copy of each chapter, 530 tests

*2026-09-22. The ported Codex tests rest on a claim that stopped being true when
the corpus grew from 137 programs to 791: that a chapter emits the same Roc
wherever it appears. Two of the three reasons were our own bugs. The third is
real, and it turns out to cost almost nothing.*

## The short version

- The package is one shared copy of each Codex chapter plus a small app per
  test. That only works if a chapter's emitted Roc is **identical in every
  program that carries it**.
- At 137 programs it was. At 791 it was not: **44 chapter names had two or more
  texts.**
- Two causes were the bundle leaking into a chapter through generated names —
  our emitter's fault, now fixed, 44 down to 28.
- The 28 that remain are a **real property of the language**, not a bug, and
  they are all in the big machine and disk tests.
- **At the size cap we ship, the cost is zero tests.** The decision only starts
  to bite if we want the whole corpus, and even then it is 59 of 780.

## What the package is

`rocemit` writes one Roc module per Codex chapter. A Codex program carries every
chapter it cites, so 791 programs carried 791 copies of `ListUtils`. Roc shares
code with a package, so `tests/package.py` puts the chapters in `codex/` once and
makes each test a short app over them:

    app [main!] { cdx: "./codex/main.roc" }
    import cdx.ListUtils

That deduplication is sound only if every program's copy of a chapter is byte
for byte the same. Each app is still RUN against Cobblestone's recorded output
before it is kept, so a wrong share cannot ship silently — it shows up as a test
that prints the wrong thing.

## The two bugs

**A binding that only carried a type.** An IR literal has no slot to hold a
type, so when a value must carry a unit type (Celsius, Kelvin) Codex's lowering
binds it to a name and answers the name — the name is where the type lives. The
name is `__unit-<offset>`, and the offset is the value's position **in the
bundled program**. Behind one set of chapters that is `unit_7046`; behind
another, `unit_57933`. Identical code, different text.

That rule is upstream's own (`Lowering.codex:615`) and our IR has to reproduce
it exactly or we lose wire equality with Cobblestone, so it cannot be fixed
there. But Roc spells a unit as its own integer and needs no such name. We were
emitting a binding nothing reads:

    celsius_to_Kelvin = |c| ({
    	unit_7046 = (c + 273)
    	unit_7046
    })

The emitter now recognises `let x = e in x` for what it is and emits `e`:

    celsius_to_Kelvin = |c| (c + 273)

My first attempt renumbered those names per definition, which would have made
the text stable while keeping the pointless binding. Steve pushed back on it —
"are we papering over something?" — and he was right: the fix is to stop
emitting the artifact, not to launder its name.

**A counter that ran across the whole program.** Hoisted temporaries were
numbered from one counter for the entire emit, so a chapter's `mem__47` became
`mem__1` in a program with fewer chapters ahead of it. The number only has to be
unique inside a definition, which is how the device names already worked. It now
resets per definition.

Both are the same rule, stated once: **a chapter's emitted text must depend only
on the chapter.**

## The 28 that are not bugs

| what varies | chapters | example |
|---|---|---|
| the threaded state | 20 | `Sha256` over `Mem.Mem` vs over `Machine.Machine` |
| a name that collided | 7 | `gpio_set!` vs `foreword__board_gpio_set!` |
| not a chapter at all | 1 | `MachineMedia`, which the ladder generates per test |

The first is the interesting one. A Codex program that reaches a device threads
a state through every definition that touches it, and rocemit picks that state
from what the *whole program* reaches. So the same `Sha256` chapter is a
different Roc module in a program that reaches the machine than in one that only
reaches memory:

    sha256_buf! : Mem.Mem, I64, I64, I64 => (Mem.Mem, List(I64))
    sha256_buf! : Machine.Machine, I64, I64, I64 => (Machine.Machine, List(I64))

Both are correct. Neither is the chapter's alone. The second cause is the same
shape: when two chapters in one program define the same name, one gets a prefix,
and which one is a property of the pair, not of either chapter.

## What it costs, measured

Greedy packing at each size cap, over the 791 passing programs, counting the
tests that would have to be dropped because a chapter they need is already in
the package in a different form:

| cap | tests picked | shareable | dropped on a clash | chapters | package |
|---|---|---|---|---|---|
| **16 KB** | 530 | **530** | **0** | 122 | 590 KB |
| 24 KB | 594 | 590 | 4 | 182 | 1.1 MB |
| 32 KB | 608 | 602 | 6 | 203 | 1.3 MB |
| 64 KB | 617 | 610 | 7 | 220 | 1.6 MB |
| none | 780 | 721 | 59 | 323 | 3.1 MB |

**At the cap we ship, nothing clashes.** Every chapter with two forms is in a
machine, GOP or FAT16 test, and those carry 20 to 90 KB of chapter text each —
far past the cap for entirely separate reasons.

A note on that cap, because it bit us: a test is charged for the chapters no
earlier test needed, so **the first test to need `Text` pays for all of it.**
`Text.roc` grew past 8 KB when rocemit learned real equality and printing, and
the old 8 KB cap then silently excluded every test that prints anything — the
first regeneration produced 17 encoders and reported it as "774 over the cap".
The cap must clear the biggest shared chapter; 16 KB does.

## The recommendation

**Ship at 16 KB and drop on a clash.** It costs nothing today, the packager
already detects a clash and already runs every app before keeping it, and the
README can say plainly which tests are left out and why.

If we ever want the machine tests in there, the answer is not to rename modules
inside one package — `Sha256` and `Sha256Machine` would be a lie about what the
chapters are. It is **two packages**, `codex/` and `codex-machine/`, because a
program threads exactly one state and each app imports the package matching its
own. That is a real day of work for 59 tests, and those 59 are the ones whose
value here is lowest: they exercise our machine model as much as they exercise
Roc.

## Where this leaves the ported tests

The old package on disk is still the 124-test one from 2026-09-12; I reverted
the half-regenerated copy rather than commit it. What remains is mechanical:
regenerate at 16 KB, then rewrite the README template, which still says "eleven
slow programs" and "137 units" from the old era and needs its slow list
re-derived (two new ones are over the quarter-second line, `interval-exhaustive`
at 1.1 s and `lib@hkdf-test` at 372 ms).

---

Written by Claude (Anthropic's model) with Steve Howell.
