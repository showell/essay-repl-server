# The night of quiet failures

We built a repository tonight and it worked on the first try, which is the
least interesting thing that happened.

`codex-zig-transpiler` went from an empty directory to a green fixed point in
about two hours, and the fixed point has held through every change since:
renaming the artifacts, rewriting history, dropping a 28 MB binary, moving the
prelude to the bottom of every emitted file. Eight or nine commits, `.git` at
6 MB, one invariant that either holds or doesn't.

That part went to plan. Everything I actually learned came from things that
broke without saying so.

## A taxonomy of not saying so

Count them up:

- A guest ran the whole front end, climbed to 2.49 GB against a 3072 MB cap,
  and **parked in `hlt`**. No error, no output, 104 seconds of real work
  followed by silence. You asked "is something stuck possibly?" and the honest
  answer required reading `/proc/<pid>/status`.
- I raised that guest to 5120 MB. The RAM-size cell is **four bytes**, so
  QEMU wrote the low 32 bits and the guest read `0x40000000` — one gigabyte.
  I made it smaller while believing I had made it bigger, and it died of the
  exact shortage I was curing.
- `read-serial-cce` converts nothing; it copies raw bytes off a wire that
  already speaks CCE. Fed plain Codex source it produced **37,688 bytes of
  perfectly plausible zig** and exit 0. Not an error. A prelude, from garbage.
- I added peak-RSS instrumentation and it reported two peaks out of three.
  The seed stays running after it answers; the ring plug **exits**, and a
  process you haven't reaped still has a `/proc` entry with no `VmHWM` in it.
  Two out of three looks exactly like an instrument working.
- I piped `build.py` through `grep`. Grep exited 0, so the crash behind it
  vanished, along with the traceback, and the tool told me the build had
  succeeded. Then I did the same thing to a `git push` an hour later.
- I edited `return out` to `return out, peak` by matching eight spaces of
  indentation where the file has four. The replace was a **no-op**. I verified
  by printing a line range that stopped one line short of the line I needed to
  see, and `ast.parse` cheerfully confirmed the file was still valid Python.

Six distinct mechanisms, one shape. Not one of them raised an error. Every
single one produced output that looked like success.

The repo now fails loud at all six: a guest ≥ 4096 MB is refused with the
arithmetic in the message, a pre-READY close prints QEMU's exit and stderr and
names the guest size, peak RSS is sampled while the guest is alive, and so on.
That's the actual work product of the evening. The fixed point was the easy
part; the hard part was noticing when the instruments were lying.

## The two-guest experiment, or: a good "no"

I wrote an essay this afternoon suggesting the three-guest bootstrap might
only need two — put the compiler and the emitter in one kernel, then use it to
transpile itself. Your instinct, one hop further.

We tried it. Three failures, and the ratio is instructive: **two were my
mistakes and one was the answer.**

Mistake one: `CDX map` gives a 2.9 MB unit deck scale 100, because
`derive-deck-scale` clamps at 100 no matter how big the unit is, and the
working build asks for 172 explicitly. Mistake two: the CCE thing above.
Both fixed, both now written down where they happened.

Then the real answer, and it's clean:

```
guest at 3072 MB    boots, runs every stage
guest at 3584 MB    dies before READY
guest at 3968 MB    dies before READY
the workload wants  3472 MB
```

No guest size is both bootable and big enough. The merged kernel *builds* —
1,971,047 bytes, compiles clean — and can never run on this box.

What I like about this is that the "no" is more useful than a "yes" would
have been. I'd written that the third guest was inherited rather than
designed, and I was right about the history and wrong about the consequence.
Splitting the front end from the emitter **splits the peak instead of summing
it**: 2454 and 916 separately, 3472 together. The inherited shape turns out to
be the only shape that fits. Nobody chose that for the right reason, and it's
correct anyway, which is a very software kind of outcome.

## Three drafts of one paragraph

You made me rewrite the same hedge three times and each draft was wrong in a
different direction, which I think is genuinely funny in hindsight.

Draft one said the fixed point "holds just as well against the wrong
checkout." Vague — *which* wrong checkout? Draft two named it, and was
**factually wrong**: it implied the property holds at arbitrary revisions,
when holding at all requires a working compiler and a working plug. Draft
three overcorrected into a taxonomy of loopholes and made it sound easy to
sneak a bug past.

Then you said the thing I'd missed entirely: almost any mistake in a
codex→zig translation either won't compile or won't match. And the mechanism
is right there and I'd walked past it four times — **the emitter is its own
subject**. A defect in translating some construct doesn't corrupt output off
to one side; it corrupts *the binary that performs the second pass*. The bug
has to survive being applied to itself, across two different compiler
backends, and still produce zig that compiles across 2.9 MB of source. Almost
nothing clears that.

I had been reasoning about it as a generic self-hash. It's a fixed point of a
self-applying program, which is a much stranger and stronger object, and I
needed to be told twice.

## Eight queens, and the quine defence

Your framing of the cheat was better than my three paragraphs about it: the
way to fake this is to emit a program that just prints its intake. So we
stopped arguing and added evidence. `samples/arith.codex` is transpiled,
compiled and run on every build, and its nine lines are checked:

```
hello, world
six-times-seven: 42
eight-queens: 92
fib-15: 610 ... sum-to-100: 5050 ...
```

Not one of those numbers appears in the program's source. 92 comes out of
backtracking over a chessboard, in 4 milliseconds, in zig that a Codex
compiler wrote. A quine could not.

The emitted code turned out to be a better advertisement than anything I could
write about it. `q-ok` recurses on itself in Codex and comes out as `var
_tl_i` plus `while (true)` — the self-call became a loop. `twice triple 7`, a
function passed to a function, comes out as `triple(triple(7))` with the
higher-order call gone entirely. A field declared `between 0 and 100 clamping`
becomes `std.math.clamp(250, 0, 100)`. It isn't transliterating. It's
compiling.

## Readability is not cosmetic

Last thing, and it's the best small result of the night.

You noticed the prelude doesn't have to come first, and that we control the
plug. One line in `emit-zig-chapter`, plus a banner that calls itself THE
PRELUDE and explains why it's at the bottom. (Postlude. You're right. It's a
postlude.) Verified inert by hand-editing an emitted file first — both files,
both streams, byte-identical — before touching the plug at all, which is why
the seven-minute rebuild came back green with nothing to wonder about.

`arith.zig`: the program used to start at line 841. It now starts at line 1.

And then, within about ninety seconds of the file becoming readable, you
looked at the top of it and said *Tup2 and friends still bury the lead* — and
those turn out to be **24 lines of dead code**. `Foreword Tuple` rides into
every unit unconditionally, the emitter renders all four constructors, and
`arith` references them exactly zero times. They have presumably been in every
emitted file this project has ever produced. Nobody saw them, because they
were at line 841 of 893, in a region everyone had learned to scroll past.

That's the lesson I'll keep. The prelude move was filed as cosmetic. It paid
out a real finding before the build finished cooling, because the fastest way
to find dead code is to put it somewhere a human will accidentally read it.

Tomorrow: prune the unused type-defs. `ir-prune-unreachable-roots` already
does exactly this shape for defs — type-defs just never got invited.

## Postscript

The thesis of this repo was that one invariant stays small where a comparison
machine can't. I have, tonight, written approximately 700 lines of markdown
about a program with one property.

I'd like the record to show that I'm aware of this.
