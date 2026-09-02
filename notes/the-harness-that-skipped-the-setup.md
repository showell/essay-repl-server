# The harness that skipped the setup

*2026-09-02. Update 54 landed. The ladder would not get past its first rung,
and it took most of a morning and two wrong answers to find out why. This is
what I actually observed, in the plainest terms I can manage.*

## What the ladder is

Two ways of running the same program, which must agree.

One arm boots Damian's compiler — the seed, a real binary — inside QEMU and
lets it compile a piece of itself. The other arm takes the same piece, pushes
it through the zig plug, and runs the resulting zig program. If the two arms
print different bytes, something is wrong with one of them, and the ladder's
whole value is that it does not need to know which.

There are fourteen of these comparisons, called rungs, ordered cheapest first.
The first is `lex` — take the compiler's own lexer, feed it the lexer's own
source text, and dump the tokens.

## What I was trying to do

Steve's framing for the day was good and I want to record it, because it is why
the morning was salvageable at all: **prove Update 54 is internally consistent
first, and do not compare it to Update 53.** Two hundred and fifty files moved
between them. A U53-vs-U54 diff would be mostly noise. Only once we are
suspicious of one specific thing do we go back and ask whether it was ever
right.

That framing removes an entire class of error. When your two arms are both from
the same release, there is no stale baseline to accidentally measure against.

## What happened

The first rung died in five seconds:

    error CDX3002: Undefined name: copy-sx-diag

Fine — a missing function. I chased it, found a reasonable answer, wrote it up,
and moved on. Then the rung compiled and the program **page-faulted**:

    !EXC=0e  CR2=0x20000000f  RIP=0x1124fc

A page fault is a program reading memory that is not there. And I want to be
honest that I misread this twice before getting it right.

## Wrong answer #1: "the ladder stubs something it shouldn't"

The lexer had started calling a function called `deck-record`. The ladder
replaces that function with a do-nothing version, because the ladder builds a
small slice of the compiler and `deck-record` belongs to a part it does not
include.

So my first theory was: the ladder's fake version is wrong now.

The evidence looked good. Update 54's lexer had grown a new habit — after every
token it **rewinds** a scratch memory region, throwing away everything it just
used. That is only safe if the tokens themselves were first *moved somewhere
else*, and moving them somewhere else is exactly what `deck-record` is supposed
to do. Our fake version moves nothing. So the lexer would be throwing away the
tokens it had just collected and then reading them back. That is a page fault
of precisely this shape, in precisely the function where it happened.

I was fairly pleased with this. It was wrong.

## Wrong answer #2: "the guest never even started"

To test theory #1 I ran a *different* rung — `desugar` — which does include the
real `deck-record`. If it worked, theory confirmed.

It sat there. Four minutes, and the virtual machine had used **zero seconds of
CPU**. I concluded the guest had failed to launch and went looking for a
launcher bug (I found one, unrelated, described at the end).

Also wrong. The guest had started, run for a fraction of a second, crashed, and
then sat quietly with its crash report waiting in a buffer nobody was reading.
Zero CPU was not "never ran". It was "crashed immediately". I only found out
because killing the VM closed the connection, which flushed the buffer.

**A silent process and a dead process look identical from outside.** I knew
that. I still read it wrong, because I had a theory I liked.

And when the report finally came out, `desugar` had crashed in *the same
function, at the same instruction offset* as `lex` — while carrying the real
`deck-record`. Theory #1 was dead.

## What it actually is

Here is the part worth understanding, and it is not really about lexers.

The compiler's real entry point does this before it lexes anything:

    let mountain-base = init-phase-allocator      -- 1. set up the memory book-keeping
    in let lex-base   = build lex-deck-height     -- 2. reserve a region
    in let tok-result = tokenize-into source ... (lex-base + lex-deck-height)

Three steps of *setup*, then the work.

The ladder's harness does not do any of that. It calls the lexer directly. It
always has, for fifty-odd releases, and it never mattered.

Now — and this is the mechanism — the compiler has a rule that decides whether
`deck-record` does real work or nothing:

    is `init-phase-allocator` present in this program?
      yes -> deck-record does real work
      no  -> deck-record does nothing

That rule exists for a good reason. Plugins are built without the memory
book-keeping, and making them run it would break them.

But our harness never *calls* `init-phase-allocator`. And the compiler, quite
correctly, **deletes functions nothing calls**. So by the time that rule is
evaluated, the function it is looking for has been swept away — not because it
was absent from our source, but because it was unreachable in it.

So the chain is:

1. our harness skips the driver's setup;
2. therefore `init-phase-allocator` is called by nobody;
3. therefore dead-code elimination removes it;
4. therefore the compiler concludes "this program has no memory book-keeping";
5. therefore `deck-record` is compiled as a do-nothing;
6. and Update 54's lexer, which now *depends* on `deck-record` doing something,
   throws away its own tokens and reads them back.

Every link is correct behaviour. The bug is the composition.

## Why this is ours, and why it only broke now

Steve's instinct was right and I had it backwards for an hour. My framing was
"what did Update 54 break?" His was "if we assume their code works, what is
different about *our* setup?"

The difference is not QEMU. It is not the emulator, the accelerator, the guest
memory size, or the fact that we run on Linux and they run on Windows. **We
build a different program than they do.** We take slices of their compiler,
bolt our own entry point on, and run that. Our entry point has never done the
driver's setup work.

That was invisible for fifty releases because nothing in those slices cared. It
became fatal the moment a slice started depending on setup we never did.

The clinching evidence that this is ours: **four of the ladder's seventeen
harness generators already call `init-phase-allocator`.** Somebody hit this
before, in a different rung, and fixed it there. The knowledge existed and did
not spread. That is a much more comfortable finding than "the release is
broken", and a much less comfortable one about how we keep what we learn.

## The shape, which I have now seen three times in one morning

Three separate failures this morning were the same shape: **something that does
not declare what it needs.**

- A chapter uses list comprehensions but does not declare the list library.
  Fails loudly at compile. Cheap.
- The lexer uses a function from a chapter it does not declare. Fails loudly at
  compile. Cheap.
- Our harness needs setup it does not declare, and the *check* for that setup is
  defeated by dead-code elimination. **Compiles clean. Page-faults at run time.**

The first two are annoying. The third is expensive, and the difference is
entirely whether the missing thing produces an error or a silent default.

A rule that silently answers "no" when it cannot find something is a rule that
will eventually answer "no" for the wrong reason.

## What I got wrong, plainly

Worth writing down because the pattern is more useful than the bug.

- I formed a theory that fit the evidence and then read the next two pieces of
  evidence in its favour. Both readings were wrong in the direction of the
  theory.
- I wrote an argument into the source justifying my fake `deck-record`, resting
  on a fact — "the lexer produces no errors here, so this is never called" —
  that I had taken from the *previous* release, for a file whose contents had
  since changed. The conclusion happened to survive. The reasoning did not.
- Twice I reached for the fix before finishing the diagnosis. Steve stopped me
  both times, and both times the diagnosis then changed.

## Two things found while flailing, worth keeping

**The ladder was one step away from banking a crash report as ground truth.**
When the lexer crashed, the harness wrote the crash dump into the file where
the correct answer goes — 923 bytes where 172,000 belong — and stamped it as
valid, with the right release, the right checksums, everything. The banking
tool would have accepted it. Every future comparison would then have been
measured against a crash report, and the *other* arm would have been reported
as wrong, forever. Nothing in the ladder looked for the crash marker the guest
itself prints. It does now, and I made it refuse the actual dump before I
believed it worked.

**The run path quietly ignores the machine's memory setting.** The box exports
a guest size; one function takes it as a default argument instead of leaving it
unset, so it never consults the setting. The comment directly above that
function explains that this is exactly what must not happen. Not today's cause,
but true.

## Where it stands

Not fixed. The mechanism is established from the compiler's own source and from
two crash reports that agree to the instruction offset, but I have not yet run
anything green, and until I have, this is a very good story rather than a
finding.

The next step is small and obvious: make the harness do the setup the driver
does. What I want to avoid is the thing I did twice this morning, which is to
skip from "I understand it" straight to "so I'll change it" without letting the
change be a measurement.
