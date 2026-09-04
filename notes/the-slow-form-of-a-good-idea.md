# The slow form of a good idea

2026-09-04. A day spent making a tree-walking interpreter and a desugarer
faster, and being wrong twice in the same shape.

## The numbers first

|  | start of day | end |
|---|---|---|
| interpreter | 17,487,495 steps/s | **36,925,278** (2.11x) |
| desugarer | 10.0 MB/s | **29.0 MB/s** (2.9x) |
| `Expr` node | 104 bytes | **56** |
| `Value` | 24 bytes | **16** |
| safari's meaning-oracle | 22 units, 5 held back | **all 27, none held back** (104 s) |

Six commits. The gates did not move once: 70 unit tests, safari at 26 agree and
one disagreeing on purpose, the IR grade byte-identical at 923 of 1012, and a
corpus sweep verified verdict-identical across 982 programs.

Everything below is what those numbers cost to learn.

## The shape of the thing

An interpreter that walks a tree has two kinds of cost. There is the work the
program asked for, and there is the work the interpreter does to find out what
the program asked for. The second kind is invisible in the source and enormous
in the profile.

The first change of the day was the whole day in miniature. `perf` said the
walker spent 10.7% of its life in `lookup` and about 8% inside SipHash. That is
name resolution: every time the program mentioned `x`, the interpreter walked a
chain of scopes comparing `String`s, and on a miss fell into five `HashMap`s.
Every time. For a name whose meaning was fixed before the program started.

So: compile the tree once into a form where a local is `(hops, slot)`, a global
is an index, a literal is already a value, and an application spine is already
flat. **1.84x**, and the step counts came out byte-identical before and after,
which is the only reason the rate is comparable at all.

That is the good version of the day's lesson. The interpreter was re-deriving,
on every step, what could not change.

## The cheapest win was dead work, not clever work

Later, profiling the *front end* on one 2.7 MB file, one symbol stood out at
about a sixth of the run: `Node::descendants`, with a `sort_by_key` inside it.

It collected every node in the subtree into a vector, sorted the whole vector by
each node's first-token offset, and *then* kept the ones matching the kind the
caller asked for. The desugarer calls it once per chapter over the whole tree to
find definitions. The sort key was not free either — finding a node's first token
walks a stack, so the comparison allocated.

Filter first, sort only the matches. **Desugar went 10.0 to 26.2 MB/s.**

Nothing about that was insight. It was reading a profile and looking at what the
hot symbol actually did. The largest single speedup of the day was a three-line
reordering of an existing function, and it had been sitting there the whole time
because nobody had profiled the front end — we had profiled the interpreter,
because the interpreter was the thing we were thinking about.

## Twice, the obvious form of a good idea was the slow one

Here is the part worth writing down.

**Round one.** Counting allocation sites showed that building a record copied
every field *name* — 1,585,699 `String` allocations in a single safari unit, for
a handful of distinct names, about two fifths of everything the run allocated.
The fix is interning: share the names. The obvious way to share an immutable
string in Rust is `Rc<str>`.

`Rc<str>` measured **16% slower**.

`Rc<str>` is a fat pointer: pointer plus length, sixteen bytes. It took
`Value`'s largest variant from 16 bytes to 24, and `Value` itself from 24 to 32.
Every step of the interpreter moves `Value`s. Removing 1.59 million allocations
did not come close to paying for making the universal currency a third bigger.
`Rc<String>` — thin pointer, one more indirection on a dereference that almost
never happens — won 6.3% instead.

**Round two**, hours later, on the same day, having supposedly learned. Replacing
`Name = String` with an interned four-byte symbol removes 6,185,699 allocations
from desugaring the corpus. First measurement: desugar **regressed 14%**.

Interning does not remove work, it *substitutes* work. Every one of those 6.19
million allocations became a hash-table lookup, and the default hasher in Rust is
SipHash — designed to survive an adversary who gets to choose your keys. These
keys are identifiers out of a source file. There is no adversary. Twenty lines of
FNV took it back to parity.

Both times the idea was right and the first implementation of it was slower than
doing nothing. Both times the only thing that caught it was measuring after, not
reasoning before.

## Allocation count was never the currency

Put the four changes side by side and the pattern is not subtle.

| change | what it removed | what it paid |
|---|---|---|
| resolve once | name lookups, per step | **1.84x** |
| `descendants` | a sort of the whole tree | **desugar 2.62x** |
| intern field names | 43% of all allocations | 6.3% |
| symbols everywhere | 6.19M allocations | +7.9% interp, desugar parity |

The two that paid best removed *work that did not need doing*. The two that
ground removed *allocations*, and allocation count turned out to be a poor proxy
for time. Freeing 43% of a run's allocations bought 6%, because the ones I freed
were the cheap ones — short, uniform, hitting the allocator's fast path — while
the expensive ones (a `Vec` and an `Rc` per scope frame) I left alone.

What did correlate with time was **size**. `Value` 24 to 16 bytes and `Expr` 104
to 56 are probably most of why the interpreter moved at all: fewer cache misses,
and in the desugarer, less of the 22.8% of runtime that was the kernel handing
the process pages to hold the tree.

If I had to compress the day into one sentence for the next person: *do not
count allocations, measure sizes, and delete work rather than relocating it.*

## Three times I said a measurement and meant an inference

I told Steve, confidently, that half the corpus sweep was front-end cost. I had
two numbers — the interpreter got 1.84x, the sweep got 1.28x — and I solved for
the residual. It is arithmetic and it is worthless: it assumes the corpus speeds
up at the same rate as safari, and it assumes per-program setup was unchanged,
and both assumptions were false. The front end is **12%** of the sweep. I had to
walk that back an hour later.

I also said the gold banks were unusable because their pins do not match the
checkout. True for *grading* — you cannot claim correctness against a stale
bank. Completely wrong for *refactoring*, where what you need is not a green
number but an **unchanged** one. The IR grade sits at 923 of 1012 for reasons
that have nothing to do with today's work, and that made it a perfect baseline:
a nine-module change to the type of every name in the AST, and the output file
came back byte-identical to the one captured before. That single diff is worth
more than any argument I could make about the change being safe.

The method that keeps working: **capture the baseline before you touch
anything, then diff.** It caught the interpreter rewrite (982 corpus verdicts,
one differing line, and it was the elapsed time). It would have caught the
mistake I nearly shipped in the IR emitter, where names are written with `{:?}`
because that is how the IR gets its quotes — with a symbol type that would have
silently emitted `Sym(4)` into every gold.

## A note on build commands

`cargo check` is 1.3 seconds. `cargo build --release` is 66. In a refactor with
170 compile errors, using the second one as your feedback loop is the difference
between twenty minutes and an afternoon, and Steve is the one waiting through it.

Steve's note, when I told him: past Claudes made the same mistake with zig.

But the corollary matters as much. Release *is* load-bearing for anything that
runs: the same 169 million interpreter steps take 4.7 s built release and 20.3 s
built debug, a 4.34x. So the rule is not "avoid release", it is **match the build
to the question** — `check` when the question is "does it compile", release when
the question is "how fast" or "is it still right".

## What is left

`eval`'s own dispatch is ~32% of the interpreter profile and nothing today
touched it. Getting at it means a flatter representation than a tree walk — a
bytecode, or a closure tree — which is a project rather than an afternoon.

Below that, the frame per binding: every `let`, every `act` bind and every match
arm still heap-allocates a `Vec` *and* an `Rc`, 710,584 times in a ten-million-
step unit, and 296,196 of those frames hold exactly one value.

On today's evidence, expect single digits from it.
