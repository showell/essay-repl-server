# roc2rust performs on par with roc: where we stand, 2026-09-25

This morning, Fast Track's Rust translation already matched `roc` line for
line, but it cheated on memory. It made nine times as many allocations as
`roc`. glibc's fast malloc hid the cost; on musl, the allocator roc's own
runtime uses, the translation ran two to three times slower than `roc`.

Tonight the same Roc program, translated by rocflight's `roc2rust`, **runs
25–35% faster than `roc build --opt=speed` on musl, in about the same memory.**

## The headline

Ten games of each Fast Track experiment (ten seeds for `exp_duplicate`, 20
rollouts for `exp_rollout`). Every Rust output is identical to roc's.

| 10 games | roc | Rust, musl | Rust, glibc |
|---|---|---|---|
| exp_duplicate | 6.57 s, 9.2 MB | **4.51 s, 9.1 MB** | 2.13 s, 9.7 MB |
| exp_rollout | 1.62 s, 2.1 MB | **1.11 s, 2.1 MB** | 0.68 s, 3.8 MB |
| exp_table | 0.55 s, 2.6 MB | **0.32 s, 2.4 MB** | 0.18 s, 4.1 MB |
| exp_cards | 0.50 s, 2.4 MB | **0.37 s, 2.7 MB** | 0.17 s, 4.1 MB |
| exp_search_size | 0.31 s, 3.6 MB | **0.20 s, 4.3 MB** | 0.10 s, 5.5 MB |

**The fair comparison is the musl column**, because roc links musl's malloc.
On glibc, Rust is about three times faster than `roc` but uses 1.5–2 MB more:
that is glibc's fixed cost, and it matters less as a program grows.

Fast Track is small but not a toy: ten modules, a branching search, records of
lists of records, and strings throughout.

The corpus gate held all day: roc2rust still translates and passes 506 of
the 521 ported programs.

## How the allocations came down

`exp_duplicate`, one seed, counted by a build of the runtime that tallies
every allocation:

| stage | allocations | bytes allocated | glibc time |
|---|---|---|---|
| this morning: `.clone()` at every read | 11.1 M | 511 MB | 0.52 s |
| read-only uses borrow; empty lists free; list writes in place when unshared; a first cut at moves | 5.5 M | 409 MB | 0.41 s |
| moves at the **true** last use | 5.2 M | 167 MB | 0.33 s |
| a record update takes over its base | 5.2 M | 166 MB | 0.28 s |
| **strings laid out as roc's** | **2.2 M** | 170 MB | 0.20 s |
| read-only builtins borrow their list | 2.2 M | 171 MB | 0.20 s |
| `roc` | 1.2 M | 192 MB | 0.63 s |

Three changes did most of the work.

**Move at the last use.** Roc's own trick: a list that is unshared is written in
place, and a value is unshared when nothing reads it later. roc2rust now walks
each function backwards to find each variable's last read, and hands the value
over there instead of cloning it. A list write goes through `Rc::make_mut`: in
place when this is the only reference, a copy otherwise.

This is where Rust earned its place. The analysis is easy to get subtly wrong:
Roc's evaluation order, lambdas, loops, a borrow that outlives an argument. A
wrong move in the generated code is not a crash or a wrong answer. **rustc
rejects it, every time.** It happened three times today, and each was a
compile error pointing at the exact line. A Zig target would have given us
more control over layout, but it would not have caught those bugs.

**Strings as roc lays them out.** Fast Track's players carry their colour and
their cards as short strings, and the search copies players constantly. A Rust
`String` allocates on every copy. The runtime's `Str` now holds up to 23 bytes
in place, as roc's does, points at a literal instead of copying it, and puts
only longer built strings behind a reference count. That one change cut
allocations by more than half, in every experiment.

**Lend, don't clone.** A builtin that only reads a list (`len`, `get`, `any`,
`map`, …) now borrows it. That saves no allocation, since cloning an `Rc` only
bumps a count, but the counting sat inside tight loops.

## What we tried and put down: a list in one allocation

A Rust list here is `Rc<Vec<T>>`, which is two allocations: the count, then
the elements. roc's is one. The remaining 1.8× gap in allocation count is
mostly that. We tried three single-allocation lists:

- **Hand-written, with `unsafe`.** Allocations fell below roc's (1.11 M), with
  no time gained on glibc. It was about 150 lines of code that rustc can no
  longer check.
- **typst's `ecow` crate.** It is vetted (Miri runs in its CI), but its
  reference count is atomic. That made it *slower* than today's list. It also
  added a dependency.
- **A safe hybrid:** `Rc<[T]>` for a list built all at once (one allocation),
  `Rc<Vec<T>>` once its length changes. It made a third fewer allocations, but
  was 10–15% slower and used more bytes, because switching between the two
  forms copies elements.

**None of them paid.** Allocation count was never the goal. The goal was time
and memory, and those are already on par. The runtime stays safe Rust with no
dependencies. The branches are deleted; the measurements are in the commit
messages and in memory.

## What is left

- **exp_search_size uses 21% more memory than roc.** It is the one experiment
  where memory is not even. Nobody has looked at it yet.
- **A closure is copied to call it.** `(*wins.clone())(j)` bumps a count just
  to call `wins`. It is cheap, but free to remove, and it is in the generated
  code everywhere.
- **Closures passed to the program's own functions are `Rc`s.** Closures passed
  to builtins are already borrowed.
- **Full-size runs.** Ten games agree with one game; the full experiments take
  minutes each and have not been rerun since the morning.
- **An `expect` mode for roc2rust**, so a translated program can run its own
  tests.

## rocflight upstream

Brian has not answered anything, and his main has not moved since 09-22. Our
open work, regrouped today so that it merges cleanly:

- **PR #1**: loading the modules a module imports (with the old #3 folded in).
- **PR #22**: the fixes that let rocflight's *interpreter* run Fast Track. All
  five experiments now match roc there too, about six times slower than
  compiled code.
- **PR #23**: five smaller fixes.
- **PR #25**: opt-in recording of every node's type, which our translators read.
- **Issues** #4, #6, #9, #11, #13, #14, #16, #17 (with a proposal that rocflight
  be stricter than roc about shadowing), and #24.

Our `all-prs` branch is Brian's main plus every open PR as sent, so we test
exactly what he would merge. It picked up #25 this evening. `codex-emit` is
`all-prs` plus a short, listed stack of changes we keep for ourselves: the
translators themselves, and two partial fixes we hold back as too risky to
send.
