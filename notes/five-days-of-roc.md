# Five days of Roc

*2026-09-11 to 2026-09-15. Open-ended: what we pointed Roc at, where it fit,
where it pushed back, and what the pushing taught. What is still in flight
lives in the project notes, not here.*

## What there is

On the morning of September 11, Safari was a Codex program and roc-apps did
not exist. On the evening of the 15th, https://roc.lynrummy.com serves six
things built with Roc:

| project | what the Roc is | how it is judged |
|---|---|---|
| Safari | Codex emitted as Roc, plus one hand-written bird | 54 specs, byte for byte |
| BASIC | hand-written | NBS: 195 pass; 55 of 99 games match exactly |
| the GPU gallery | 46 WGSL kernels emitted, run on the CPU | every kernel checks; two frames match Python |
| games | 2048, Minesweeper and Klondike emitted | Damian's own graders, 82 arms |
| the machine | emitted Codex on a Roc model of codex-vm's devices | the tests' x86 verdicts |
| the framebuffer | emitted Codex drawing through a zig host | image hashes, native and wasm alike |

Under them are two instruments. **rocemit** is about 4,000 lines of Rust that
re-spell our compiler's typed IR as Roc modules. **The ladder** runs every
program in Cobblestone's `codex/test` through Roc against its x86 verdict. The
ladder passed 125 of 597 on the night of the 12th. The next day it learned to
read the whole directory and passed 483 of 1,017. Today it passes 787 of
1,032. roc-apps has 224 commits.

## Two kinds of program

The work split along a line nobody planned: programs Roc received from Codex,
and programs written in Roc.

**The emitted programs cost the least, because the hard part was already
done.** Every node in our compiler's IR carries its type, so rocemit never
infers anything; it re-spells. A Codex chapter becomes a Roc type module
(`Slug :: [].{ ... }`), which is also exactly what an app imports. That is why
Safari moved in an afternoon. The Roc that comes out is Roc nobody would write
by hand: 9,436 lines for Safari alone, every definition annotated, every name
qualified. It is still trustworthy, because another implementation holds the
answers.

**The hand-written programs are where Roc's cost model was felt directly.**
BASIC is about 5,000 lines and the machine's device modules about 4,800. Nobody
else's verdict stood behind a design choice there. What stood behind it was a
count of allocations.

## Where it fit

**Pure computation fit with almost no friction.** Safari's frame, the GPU
kernels and the three games are functions from a state to a state or a
picture. The one real fight was building lists. Codex conses onto a recursion,
and in Roc each level of that copies everything below it. Once the emitter
wrote an accumulator loop instead, Safari's first frame went from 110 ms to
15 ms. After that, the emitted code was simply Roc.

**The platform line fit better than expected.** Roc keeps the program pure and
hands the world to a host. Our hosts are about 3,500 lines of zig, and "zig for
infrastructure" became the rule: memory, devices, the GPU. The same emitted
scene draws in 1.4 s a frame on the Roc-modelled machine and in about 100 ms
with memory in the host. The GPU widget tests take 18 to 32 ms against 1.4 to
2.3 s. Both draw the same pixels, down to the hash. Moving infrastructure out
of Roc changed the price and not the answer, which is what a boundary is for.

**The dev backend made iteration possible, and its price is visible.**
BASIC builds in 6 seconds on it. The LLVM build takes 1,420 seconds and peaks
at 2.2 GB. It prints the same 307 transcripts, and runs the slowest
conformance program 2.7 times faster. Everything we publish is a dev build. In
the raytracer's hot function, 86% of the instructions are stack moves, which
is the other side of those 6 seconds.

**The nightlies helped more than they get credit for.** A release build of the
compiler every day meant the Safari sweep took 27 seconds instead of five and a
half minutes. The difference between a gate you run on every change and one you
schedule is the difference between checking and guessing.

## Where it pushed back

### A Codex list is a place; a Roc list is a value

Codex writes a list in place. The two languages agree wherever a program uses
the answer. They part wherever it writes through one name and reads through
another. The foreword's bignum doubles its limbs in place and answers the
carry, so nothing that cites it can be ported as written. rocemit refuses those
definitions by name, and 65 of the ladder's refusals are this family, the
largest single one. That is not a defect in either language. It is the
boundary between two meanings of "list", and a large share of what does not
yet run sits on it.

### Copies nobody can see

In Roc a write happens in place only when nothing else refers to what is
written. The language has no way to require it and no warning when it does not
happen. Two spellings that look equally innocent can differ by a copy per
execution. `List.set(l, i, v) ?? l` names `l` in its fallback, so every store
copies: 137.8 s of CPU against 3.5 s. Other shapes copy too:
- a value threaded down a recursion and handed back;
- a helper given a record together with something read from it;
- a run loop that passes its record without a fresh update.

None of these rules came from reading. They came from counting.

**The counting instrument was an accident, and so was one of our issues.** The
default platform gives every heap value its own `mmap`, so `strace -c` counts
allocations exactly, and a ladder of tiny BASIC programs could be held to zero
allocations per statement. The same property costs one machine program 22.4 s
against 3.1 s on a C allocator. We filed the cost as
[#11335](https://github.com/roc-lang/roc/issues/11335) and kept using the
instrument.

The data structures that answered it are ordinary: persistent 32-way vectors,
stacks as a list and a depth, a read-only evaluator, and devices behind one
reference. They bound the damage without making it predictable. The comments
in BASIC say which copy each odd-looking shape avoids, because the next reader
cannot see it either.

### Compiling by running

Roc evaluates a call whose arguments are known at compile time, with no step
limit ([#11334](https://github.com/roc-lang/roc/issues/11334)). A seven-line
program that loops forever never finishes `roc check`. An emitted tic-tac-toe
search checked in 2.7 s and then ran in 3 ms. The same power returns later in
this essay, hiding a bug.

### The small ones

No shadowing. Nominal types have no structural `==`. A type error compiles
into a crash at run time while the rest of the program runs, and `roc check`
exits non-zero for a warning, so every gate judges on the ✗ mark rather than
the exit code. Only self tail calls are removed, so the globe's two mutually
recursive functions needed a forwarder. There is no `exp`, `log`, `floor` or
`round` on F64. And one nightly dies with an illegal instruction on this CPU.
Each of these cost a sweep; none cost a design.

## The same bug, twice

On September 14, `Machine.flags` failed to link for the browser:
`relocations not in offset order`. It parsed codex-vm's command line into a
record holding two device records. The reduction got as far as "a function
that copies a record of nested records in each of seven branches". Its notes
say plainly that the last step between linking and failing was not isolated.
The workaround carried the two devices beside the record, and the batch page
built.

On September 15, text became units: a Codex Text is now a `List(U8)` rather
than a `Str`. A short `Str` lives inline, while a list is always a pointer. Two
widget programs stopped linking with the same message.

This time we read the object file instead of reducing the source. A Python
reader of about 150 lines listed the data relocations wasm-ld refuses. There
were nine, and all were pairs inside constant records 152 bytes wide. Decoded
as CCE units, the pairs were a widget's id and label: "set-theme" and
"Theme: Terminal". From there the cause was a short read of Roc's source:
- the constant builder appends a record's relocations in field-name order;
- the layout places an 8-byte-aligned tag union before a 4-byte list;
- the wasm writer passes the order through unsorted.

Renaming one field so the two orders agree made the program link.

Reproducing it cost three tries. The first two programs were folded away
entirely by the compile-time evaluator. The third got its index from the host,
and it failed. The fix is one sort. A patched compiler links:
- the reproduction;
- the widget program;
- the September 14 finding.

So the second encounter was almost certainly the same bug as the first.

The first workaround was honest. It said what was not understood, and it
unblocked the page. It did not have the cause, though, so the next change that
added pointers found the bug again. The difference the second time was the
layer we looked at. Reducing source chased shapes; the object file held the
answer in four entries. The first finding sat unreported. The second went out
with a reproducer and a tested fix, as
[#11419](https://github.com/roc-lang/roc/issues/11419).

## What the second implementation found in the first

Several of this week's findings are not about Roc at all. Running Cobblestone's
programs through a second compiler and a second runtime made them disagree
with x86 in places that turned out to be Cobblestone's. Five pull requests
went to Damian:
- the fat16 fixtures' second FAT;
- the Raytracer's shading units;
- GuiOS's sidebar click;
- Fireworks' random number generator;
- a nearest-hit search the Roc profile pointed at.

The Fireworks case is the pleasing one. Its `rnd` multiplies past 64 bits, and
Roc crashed where x86 traps. Roc's crash was the faithful behaviour, and the
fix belonged in Codex.

Our own interpreter was corrected too. `text-to-integer` and an empty-pattern
`text-replace` now read as x86 does, and so does a right shift. Roc was the
second machine that disagreed, and disagreement between machines is an
instrument.

## Was it the right target?

For pure programs it was a good one: the fit was close enough that the emitted
code needed no apology. For a machine made of small writes, it worked, but only
with a discipline the language does not check and a ladder to enforce it. For
infrastructure it was the wrong tool, and the platform model made that cheap
to admit, because zig could take that part without the Roc changing.

The workarounds come in two kinds, and they should age differently. Some
changed our shape:
- accumulator loops;
- a read-only evaluator;
- devices behind one reference;
- forwarders for mutual recursion.

Those are knowledge about writing Roc, and they will outlast any compiler
version. Others route around a defect: the split `flags` record, and two
framebuffer rows marked blocked. Those should disappear. Each now has an issue
behind it, with a program that shows the problem and, in one case, a fix
tested on a patched build. None of the three has a reply yet.

## Open questions

- **Are the copying rules Roc's, or its dev backend's?** A later dig found
  earlier findings flipping both ways between backends. If so, the rules
  describe one compiler's analysis, not the language, and the ladder is the
  only thing that would notice them change.
- **Would a "this write copied" diagnostic change how Roc gets written?** The
  allocation ladder was that diagnostic, built by hand for one program.
- **Of the 245 tests that do not pass, how many sit on the list boundary, how
  many need emitter work, and how many need devices?** The refusal counts
  suggest an answer, but a refusal names only the first obstacle.
- **Does the emitted Roc stay downstream of Codex for good?** The bird on
  Safari's fifth tree was the first deliberate divergence. BASIC and the
  device models were never Codex at all.
- **For a public demo, which cost is right: the dev backend's stack moves, or
  LLVM's build time?** Everything published so far chose the first.

| repo | revision | role |
|---|---|---|
| roc-lang/nightlies | nightly-2026-09-11-793f9d8 | the compiler |
| roc-apps | 3e25e94 | the apps, platforms, ladder and site |
| rust-codex-compiler | aae2c78 | rocemit |
| cobblestone | u61-candidate 7b9235e7 | the Codex source and the verdicts |
