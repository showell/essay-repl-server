# Why three guests, and whether it should be two

You said your naive view was: bundle all the Codex source that maps to
codexzig, run it right through the seed, done.

That is very nearly right, and the whole answer is one sentence wide.

## The seed does not emit zig

`seed/Codex.cdx` is a 2.9 MB bootable x86-64 kernel. It is a Codex compiler,
and it has exactly two output modes, selected by the mode line at the top of
the blob you feed it:

```
CDX map             -> an x86-64 CDX binary, plus a symbol table
IR-CCE decks=172    -> the same compile, but it hands back IR text instead
```

Neither of those is zig. Zig comes from exactly one place in the entire
system: `codex/plugs/zig/ZigEmitter.codex`. And that is *source*. It cannot
emit anything until something is running it.

That is the entire bootstrap problem, and everything below is consequence.

## What you actually get if you do the naive thing

Here is the part worth saying clearly, because your instinct is not wrong:
**bundle the codexzig source, run it through the seed, and you get a working
transpiler.** It really does work. The seed compiles the whole thing —
parser, type checker, lowering, IR text emitter, IR text parser, ZigEmitter,
the harness — into one bootable kernel.

What you get is a transpiler shaped wrong for the job:

- It runs under QEMU, not on Linux. It is a kernel. You boot it.
- It cannot read your file. Our harness says
  `read-file-uni "/dev/stdin"`, and `/dev/stdin` is a hosted path. Grep the
  whole Cobblestone checkout for it and you get nothing — that string is
  ours, and it only means something to a program running on an OS.

So you have a transpiler you cannot hand to anyone, and to turn it into one
you can, you need zig text, and to get zig text you need ZigEmitter to
actually run somewhere. Which is where we came in.

## The three guests, and what each is for

```
1  ringplug-source.codex  304 KB  -->  ringplug.cdx    408 KB    27 s
2  codexzig-subject.codex 2.9 MB  -->  codexzig.ir     9.9 MB   233 s
3  codexzig.ir            9.9 MB  -->  codexzig.qemu.zig 2.3 MB  96 s
```

**Guest 1 makes the emitter runnable at all.** At the bottom of the
bootstrap the only executor in the world is a Codex kernel, so the emitter
becomes one. This bundle carries no compiler — just the declarations,
`IRTextParser`, `ZigEmitter`, and a body. 304 KB against the subject's 2.9.

**Guest 2 gets the transpiler's own IR.** Same seed, same source you would
have fed it anyway, different mode line. This is the step that is *exactly*
your naive plan; it just asks for IR instead of a binary.

**Guest 3 runs the emitter over that IR.** Boot the kernel from guest 1,
feed it the file from guest 2, and 2.3 MB of zig comes back.

Then `zig build-exe` — two seconds — and there is a Linux executable.

## The thing I did not expect: guest 1 is about the intake

I assumed for a while that `ZigPlugRing.codex` existed because the emitter
needed some special packaging. It does not. It is thirty-nine lines and it
is almost entirely a *front door*:

```
opening = read a mode line, then read-serial-cce, parse, emit, print
```

The shipped zig plug takes its input over TCP. The ring one reads the
compiler's own serial ring. Same parser, same emitter, different intake —
and the reason is heap, measured: the TCP receive path costs about **130
bytes of guest heap per byte of IR** before the parser sees anything (four
payload materialisations per frame plus a per-character text conversion,
none of it restored, against a bump allocator that never frees).
`read-serial-cce` is a machine-code loop at one byte per byte. Our IR is
9.9 MB. TCP cannot admit that; the ring can.

So guest 1 is not "the emitter, specially prepared". It is "the emitter,
given a door that a bare-metal program can actually open".

## The strongest version of your question — and I think it lands

Take your instinct seriously and push it one step further than I did.

Bundle the compiler **and** the emitter **and** a ring intake into one
subject. Compile that with the seed: one kernel that is the whole
transpiler, reading from the serial ring. Then boot it and feed it the
*hosted* codexzig source. It emits zig. Build that.

```
1  [compiler + emitter + ring intake]  -->  codexzig-ring.cdx     GUEST
2  codexzig-ring.cdx  <  codexzig-subject.codex  -->  zig         GUEST
3  zig build-exe                                                   host
```

**Two guests.** And the shape of it is lovely: *compile codexzig to a
kernel, then use it to transpile codexzig.* That is your sentence, with one
extra hop, and it drops guest 1 and guest 3 into a single step.

I have not tried it. I want to be exact about that, because I have written
three confident mechanisms in the last two days and measurement refuted all
three. So here is what I have, labelled:

**MEASURED.** Everything in the tables above. Also: the seed is
deterministic — I rebuilt `ringplug.cdx` from scratch and it came back
byte-identical to the one already committed, and `codexzig.qemu.zig` has
been identical across every build. (`zig build-exe` is *not* deterministic:
three builds from one unchanged .zig gave two alternating sizes and three
different hashes. The emulated bare-metal compiler reproduces; the native
toolchain on top of it does not. I did not see that coming either.)

**LEAD, untested.** The two-guest shape. What I would want to know before
believing it:

- *Does it fit?* Today the front end runs in guest 2 and the emitter runs in
  guest 3, in separate 3 GB address spaces. Merging them means one guest
  holds the source, the AST, the IR *and* the emitted text at once, in a
  bump allocator that never frees. The seed already dies silently above
  3072 MB on this box. This is a measurement, not an argument, and it is the
  only real question.
- *What is lost?* `codexzig.ir` stops existing as a file. That is 9.9 MB I
  currently find genuinely interesting, and it is the artifact the ladder
  asks nearly all of its questions about — though this repo is not the
  ladder, so that may be worth nothing here.

## The honest answer to "why is it three"

Because it was inherited, not because it was designed.

The ladder builds `codexir` and `zigemit` as two separate tools, joined by a
pipe, because the ladder *wants the IR text file* — it is the comparison
point for a dozen rungs. `codexzig` was built inside that world and adopted
its shape: bundle, seed to IR, plug to zig. When I lifted the build into this
repository I carried the shape across without asking whether the reason came
with it.

It did not. This repo has one property to defend and no rungs. So the right
version of your question is not "why three" but "why not two", and I do not
have a measured answer — only a suspicion about heap that is worth one guest
to settle.

Cheap to test, incidentally: bundle it, run the seed, see whether a kernel
comes out and whether it survives its own source. Two guests, about six
minutes, and a `--force` I should remember to run in the background.
