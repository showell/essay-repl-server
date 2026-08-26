# Instruments, and Their Blind Spots

*2026-08-26. The codexzig fixed point is the milestone. What makes it a
milestone is not that it is the strongest check we have — it isn't — but
that it is a different KIND of check from the ones around it, and the
toolchain is finally a set rather than a ladder.*

## The fixed point, and what kind of fact it is

`native/codexzig` is one program. Codex source goes in on stdin, Zig comes
out on stderr. It is the whole compiler front end plus the Zig emitter plus
an IR text parser, translated into Zig and compiled to a native Linux
binary — 60,497 lines of Codex, 2,886,824 bytes of bundled source, no
emulator anywhere in its execution.

`codexzig_build.sh` ends by feeding the program its own bundle and comparing
the result, byte for byte, against what the seed-plus-ring-plug path emitted.
When those agree, the build has proved a small, strange, load-bearing thing:

> The compiler, translated to Zig, translates itself to Zig and gets the
> same answer as the compiler that did the translating.

That is a *closure*, not a correctness proof, and the distinction is the
whole point of this note. A closure says the machinery is consistent with
itself. It says nothing whatever about whether the answer is right.

## The `let` in the middle

The nicest structural fact about codexzig is one that looks, at first, like
an inefficiency.

The bundle has two halves. The front half is the compiler's own chapter set
— everything from tokenising to lowering, ending at an IR chapter in memory.
The back half is the Zig emitter. You would expect the harness to hand the
IR from one to the other directly, and that is exactly what the first
version did. It does not work. The emitted Zig will not compile.

So the two halves are joined like this instead:

```
  in let ir-text = emit-ir-chapter (ir-prune-unreachable-roots ir czg-emit-roots) meta (ch.type-defs)
  in let parsed  = parse-ir-chapter ir-text
  in print-text (emit-zig-chapter (parsed.chapter) (parsed.type-defs))
```

It serialises the IR to text and parses the text straight back, in memory,
microseconds later. A round trip to nowhere.

The reason is finding 44: **the wire format derives information the AST does
not carry.** Implicit record type parameters exist in the serialiser's
output because the serialiser computes them; they were never on the tree.
Hand the tree over directly and the emitter is missing facts it needs, and
emits Zig that a Zig compiler rejects.

I find this genuinely beautiful. We tend to think of serialisation as
plumbing — a lossy, tedious step you would remove if you could. Here it is
the opposite: the round trip is where information is *created*, and the
in-memory shortcut is the lossy path. The `let` is not a workaround. It is
an admission, in one line, about where the compiler's knowledge actually
lives.

## What the fixed point cannot see

Now the limitation, because it is what organises everything else.

Everything codexzig checks is the Zig arm against **itself**. The fixed
point compares codexzig's output to the pipeline's output. The corpus run
compares codexzig's output to the depot's expected answers — but the sample
is defined as *programs the pipeline already got right*, and codexzig's
bytes are identical to the pipeline's, so on that sample the result is
entailed rather than discovered. An earlier version of that docstring
claimed this leg could catch a defect the two share. It cannot, by
construction, and a cold read caught the claim.

Finding 42 is what that limitation looks like when it bites. The Zig plug's
self-tail loop read a **top-level definition where the source reads its own
parameter** — a loop that silently consumed a global instead of its own
argument. Both arms of every self-comparison would have been wrong together,
identically, and every fixed point would still have closed.

What caught it was the thing the fixed point is not: a rung, comparing the
Zig arm against **bare metal** — the seed compiler running as a tiny
operating system in an emulator, which shares no code with the Zig path at
all. The oracle was outside both.

So: codexzig says transpilation still works. The rungs say the answer is
right. Those are different sentences and no amount of the first adds up to
the second.

## The set, and what each instrument is blind to

Written out, the toolchain is not a ladder to one summit. It is a set of
instruments with deliberately non-overlapping blind spots.

- **The rungs** — twelve units, two arms, bare metal versus Zig. The only
  oracle that is outside both arms. Expensive: QEMU, about an hour.
- **The tier set** — small targeted unit tests with a gold ledger. Cheap,
  and historically our best yield per minute.
- **The corpus census** — 593 programs from the depot, each with an expected
  output written by people who never heard of our plug. The only oracle
  outside the entire project.
- **codexzig** — the whole compiler transpiles faithfully, in a quarter hour
  instead of fifty-one minutes. Breadth and speed; no independent oracle.
- **The truth bank and its provenance sidecars** — what makes a number still
  mean something a week later.
- **The sandbox system** — what makes a number mean anything *at all*, by
  guaranteeing no run reads yesterday's artifact under today's name.

Each one has a hole, and the holes are the design. The corpus has the best
oracle and the least resolution: it tells you a program's output is wrong
without telling you which stage did it. The rungs have the best resolution
and cost an hour. codexzig has the best breadth-per-minute and no
independent oracle whatsoever. Ask any one of them alone and you get a
confident answer to a question you did not ask.

## Today, which is testimony

Two pieces of work today were the same lesson from opposite directions.

**First.** We turned on the compiler driver's error gate — a check the real
driver performs and our harness had simply never copied. It asks, after
parsing and type checking, whether any errors were reported, and refuses to
generate code if so.

Forty-one of 593 corpus programs immediately stopped emitting. Three of them
were programs we had classified as *well-behaved*: they transpiled cleanly,
built, ran, and matched the depot's expected output byte for byte — while
the compiler was reporting errors about them the whole time. The front end
said `Undefined name: map-list`, and the back end, never asked whether the
error bag was empty, went on and got the right answer anyway.

Twenty-eight of the 41 turned out to be ours: our unit assembler was missing
two chapters that upstream's assembler pulls into every unit unconditionally,
because they hold the functions the *desugarer* writes calls to — names no
author ever types and so no author ever cites.

The number that mattered was not the 41. It was this: the corpus census
keeps a histogram of "emitter gaps", ranked by how many programs hit them,
and that histogram is what tells us which emitter arm to write next. It went
from 135 distinct gaps to 133. The two that vanished were `no emitter for
MkTup2` (18 programs) and `no emitter for map-list` (2). **Twenty entries in
the ranking that decides our work were our own bug wearing an emitter's
costume.**

Our resolver's own docstring had warned about exactly this: "the plug's
fallback fires — which looks exactly like an emitter gap and is not one."
The file written to prevent the failure contained it.

**Second.** Update 50 landed. Before compiling anything, the ceremony
requires reading the diff against the four constants we hard-code on our
side — the guest RAM cell, the serial ring's address and size, and its two
cursor cells — because a moved contract "shows up as a diff in every truth
at once, indistinguishable from a compiler change." All four held. Then the
seed identity check said *no release note names this seed*, which would have
banked a genuine release under a hash instead of a number and left it out of
the pruner forever. Update 50 simply used a note form the matcher had never
seen.

Neither of those is a compiler defect. Both are the instrument drifting away
from the thing it measures, quietly, in the direction of everything being
fine.

## The same law, from both ends

Update 50 also contains this, in Damian's own hardware bed, about a NIC
register model:

> *an instrument that cannot fail is not evidence; ask what the suite cannot
> express before reading its silence as agreement.*

He is writing about a registered defect that had no falsifier — every arm of
his suite passed whether or not the bug was present, so the suite's silence
meant nothing. He gives the law a name and files it.

We arrived at the identical sentence from the other side of the fence on the
same day, twice. A gate that was never switched on cannot fail. A histogram
that counts our own missing chapters as the compiler's gaps cannot fail. A
`.expected` comparison run only on programs already known to pass cannot
fail.

The convergence is not a coincidence and it is not profound. It is what
happens whenever two people build measuring equipment carefully enough to
start distrusting it. The interesting part is the ordering: **you find these
by building the instrument that would have caught them, and then noticing
what it says about the ones you already had.** The error gate found the
missing chapters. The missing chapters found the phantom histogram entries.
The phantom entries are the reason the next emitter arm we write will be the
right one.

The fixed point is the milestone because it is fast and broad and closes on
itself. It earns its place in the set precisely by being unable to see what
the rungs see — and the day's work was mostly about knowing, for each
instrument, exactly which sentence it is entitled to say.

*Ladder: `8830e7b`, `46e8f6a`. Update 50 pin `u50-rebank` at `8cc80685`,
seed `C45E5825`, banking to `truth/u50`.*
