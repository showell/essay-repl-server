# Where the Ladder Stands

*2026-08-26. A long note on the state of the project: a compiler that now
reproduces itself byte-for-byte on our arm, an Update that took eight of
our patches and handed back new work, a habit of stealing test programs
from another language, and the growing suspicion that our real bottleneck
is no longer finding defects.*

## What the project is, briefly

Damian is building Codex: a language, a compiler for it, and an operating
system, all written in itself. The compiler emits machine code directly
for bare metal, and it also has *plugs* — backends that translate Codex
into other languages. There are plugs for zig, C#, python, rust, swift,
haskell, riscv, arm64, wasm, and about forty others.

Our job is not to finish the zig plug. Our job is to find defects. The zig
plug is the instrument, not the product.

The method is an oracle: take a Codex program, run it on bare metal, run
it through the zig plug, and compare. Where the answers differ, one of
them is wrong. Bare metal is the reference, so a difference is usually a
defect in the plug — but not always, and the interesting days are the ones
where it is not.

That comparison runs across three scales. A handful of hand-built *rungs*
that check specific compiler stages against recorded truth. A *corpus* of
606 programs from the compiler's own test directory. And a *tier set* of
unit tests that has consistently been the best yield of the three.

## The fixed point

The most significant thing built in the last two days is `codexzig`. It is
one program. You give it Codex source on standard input and it gives you
zig on standard error. Underneath, it is the compiler's own chapters —
parser, type checker, IR lowering — bundled together with the zig emitter
and an IR text parser, compiled through the zig plug into a single 2.36 MB
binary.

The build ends with a test that has a specific name: the **fixed point**.
`codexzig` is handed its own source and asked to emit zig for it. The
output must be byte-for-byte identical to the bundle that produced it.

It held again tonight, on a build that included three days of emitter
changes:

```
############ fixed point: codexzig re-emitting its own bundle
    IDENTICAL to ast/codexzig.zig (2355953 bytes) -- fixed point holds
```

This matters for a reason that is easy to state and easy to
underestimate. A compiler that can compile itself and get the same answer
is not proof of correctness — a compiler can be consistently wrong. But it
is a very strong consistency check across an enormous surface. The bundle
exercises the parser, the type checker, the lowering, the emitter, and the
runtime, on a program of 2.36 megabytes, in one shot. If any of those
drifts, the bytes move.

There is a wrinkle inside `codexzig` worth mentioning because it is a
defect we already found, sitting in plain sight. The two halves of the
program are joined by writing IR out as *text* and parsing it straight
back in memory. That looks absurd — why serialize and immediately
deserialize? Because the AST does not carry everything the wire carries.
A record's implicit type parameters are derived by the text emitter and by
nothing else, so handing the AST directly to the next stage produces zig
that will not compile. The round trip is not ceremony. It is a workaround
for finding 44, made load-bearing.

I want to be clear about what the fixed point does *not* do. It checks the
zig arm against itself. It cannot see a mistake that both halves share.
The rungs check against bare metal, and that is a different question. The
proof that this distinction matters is finding 42, where a silent wrong
answer would have been shared by both arms of a self-consistency check and
sailed through.

## Update 50 came over the wall

Damian ships Updates. Each one is a new snapshot of the whole tree, and
absorbing it is a defined ceremony: re-pin, rebuild the natives, re-bank
the recorded truths, sweep, and see what moved.

Update 50 arrived with **all eight of our outstanding pull requests
merged** — PRs 84 through 91. That is the entire outbound queue, empty for
the first time in weeks. It is a good feeling and also a slightly
disorienting one, because our standing discipline is to measure against
our fork's stack rather than bare upstream, and right now there is no
stack. The pin measures the depot with nothing of ours underneath it.

Update 50 also brought new work from Damian's side, and one piece of it
caught us immediately. He turned lambda lifting on for the source-emitting
path — one `lift-lambdas` call became two. Our two harnesses,
`CodexZigHarness` and `CodexIrHarness`, have zero. So the codexzig fixed
point failed on its first contact with the new Update: 300 lifted lambda
definitions on the driver's arm, zero on ours.

This is a shape we had already seen once that same day. A list of IR
emit-roots had been *copied* from upstream into both harnesses, and
upstream had since grown two entries. Ours had four, theirs had six, and
no oracle could see the difference because both harnesses were wrong in
the same way.

The lesson generalizes and it keeps arriving: **do not copy a list, reuse
a pipeline.** Every time we have duplicated a sequence of steps instead of
calling the thing that performs them, it has drifted, and it has drifted
silently, because the copy is what we test against.

There is a companion lesson from the same day, which cost an hour and
looked for a while like an emitter regression: reuse the *whole* runner,
not half of it. Feeding `codexir` a raw `.codex` file where the real
runner feeds it a cite-resolved unit produces failures that look exactly
like a bug in the code you just changed.

## The Roc initiative

A few days ago we started porting small programs from Roc — another
functional language — into Codex, and running them through the plug.

The idea is simple. Our corpus was written by the people who wrote the
compiler. It exercises what they thought to write. It shares their blind
spots by construction. Roc's snippets were written by people who have
never heard of Codex, and — this is the part that matters most — they come
with *expected values* those people wrote down. When a ported program
prints something else, the disagreement is with an authority that has no
stake in our compiler being right.

Eleven ports exist now. Two match. Nine do not.

A 2-of-11 pass rate sounds like failure. It has been the most productive
thing we did all day. Those nine failures produced:

- **Finding 50**, on the very first run of the very first port that used a
  Boolean. `show` in Codex has the type `forall a. a -> Text` — one name
  over five different jobs. Bare metal picks the job from the argument's
  type: a Text shows as itself, a Boolean as `True` or `False`, a 32-bit
  real widens before conversion, any other real converts directly, and
  everything else becomes an integer. The zig plug implemented the last
  arm and sent all five to it.

- **Finding 51**, tonight, from three iterator ports that all failed the
  same way.

- **Hypothesis H2**, on lambdas whose type no declaration fixes, which
  arrive at the plug with an error type for their parameters and their
  return and are diagnosed by nothing.

Here is the uncomfortable part, and I think it is the real lesson of the
Roc work. Finding 50 was not hiding. It accounted for **42 of the corpus's
113 refusals — 37 percent, the largest single class.** The evidence had
been sitting in our own corpus output for as long as we have been running
it. We had never read it.

Eleven programs is a list. A hundred and thirteen is a pile. When a
suite is small enough that every failure demands an explanation, you
explain every failure. When it is large enough to summarize, you summarize
it, and a summary is where a 37-percent class goes to hide behind a number.

So the value of Roc turns out not to be that it reaches shapes the corpus
cannot. It is that it is *small*, and it comes with an outside authority,
and those two properties together force per-item accounting.

## Should we attack the corpus directly instead?

Steve raised this, and I think the answer is: yes, but not by porting more
things into it, and not instead of Roc.

The corpus already ranks our work for us. Every run prints a histogram of
emitter gaps sorted by how many programs hit them:

```
123  no emitter for poke-32
119  no emitter for peek-32
 95  no emitter for poke-byte
 57  no emitter for poke-16
 53  no emitter for alloc-bytes
```

That top block is hardware and OS intrinsics — memory-mapped I/O, port
access, block devices. Implementing them would move a lot of programs from
red to green. It would also find approximately nothing, because a missing
emitter is a *known* gap. The histogram already tells us it is missing. We
would be doing coverage work, and coverage work is not what the ladder is
for.

The interesting corpus work is the other pile: the 112 programs that emit
zig and then fail to *compile* it. Those are not missing emitters. Those
are the emitter being wrong. Finding 50 lived there. Finding 48 lived
there — a self-recursive type that is also generic, emitted with no
indirection, so zig says the type contains itself. Thirty-nine of the 112
are one single defect: emitted `main` spawns `opening` on a thread and zig
refuses any entry function that returns a value.

So my read is that the corpus deserves a **reading** pass, not a porting
pass. Classify all 112 refusals by cause, the way we classified the 42.
That is keyboard work, it needs no compute, and I would expect it to
produce several findings from evidence we already have on disk.

And Roc should continue in parallel, at a low rate — a few ports at a
time — precisely because it is small and keeps forcing us to explain
individual failures. Roughly eight snippets remain in the closure and
recursion cluster.

## The box, and the rhythm of the day

This machine has two CPUs. One compute job at a time is a hard rule; more
than one and they fight, and the measurements stop meaning anything.

A verification chain — build the native tools, run the type-variable
probe, run the corpus, build codexzig, run the Roc ports, sweep the rungs
— takes about forty-five minutes. The sweep alone is twenty-eight.

Steve observed that we keep the CPU busy nearly constantly, and that this
limits productivity somewhat. Both halves are true, and I would add that
the limit is softer than it looks, because there is nearly always keyboard
work that does not need the box.

Tonight is a fair sample. The chain ran for forty-five minutes. During it I
wrote a fix for finding 51, wrote the fix for finding 50, split a new
queue item out of it once measurement showed the two halves cost wildly
different things, filed a finding, promoted a hypothesis, fixed a defect
in the verification script itself, and updated the queue. Nine commits.

The trick that makes this work is that the sandbox is a *pinned copy*. Each
run cuts its own git worktrees at a fixed commit, so edits to the main tree
during a run cannot reach the measurement. Without that, keyboard work
during a compute job would be reckless.

The thing that goes wrong is a subtler version of the same problem. Today's
first chain measured a tree two commits behind the one under test, because
it was assembled by hand and assembled before those commits landed. The
fix was to stop assembling it by hand: the chain is now a script that
stamps both live HEADs into its status file before it starts. Its very
first run caught something the hand assembly would have missed — three
emitter commits that had **never been through a compiler at all**, dead on
leg zero in eleven seconds.

That is the argument for scripts over commands, made concretely. The
script did not just save typing. It made a specific class of wrong
measurement impossible.

## What the numbers say tonight

The chain finished while I was writing this. All six legs:

```
leg0 natives      GREEN  5m13   the guard compiles at all
leg1 tvar-matrix         case (g) diagnosed -- and see finding 51
leg2 corpus       GREEN  2m54   type-variable markers 40 -> 8 -> 0
leg3 codexzig     GREEN  5m54   fixed point holds
leg4 roc-ports    RED    2 of 11
leg5 sweep        GREEN 26m35   14 of 14 rungs
```

The sweep is the one that checks against bare metal rather than against
ourselves, and it is unmoved. That matters more than it sounds: this build
reordered when the emitter builds its type context, which is a real
behaviour change beyond the guard, and fourteen rungs of recorded truth
say it changed nothing they can see.

Zero type-variable markers across 606 programs, down from forty before any
fix. Match count 183 to 185, and nothing that matched stopped matching.

I want to state the reach honestly, because it is much smaller than that
headline sounds. Three hundred and twenty-five of 329 verdicts *carried*
from the previous run, because the emitted zig was byte-identical. Of the
twelve that moved, ten are programs added today. Exactly two pre-existing
programs changed verdict.

Both changed in the right direction. One went from a raw zig error to an
honest plug refusal. The other went the other way — from a refusal marker
to a compile failure — and that is also good, because the marker had been
standing in front of finding 48. Removing one defect's mask is how the
next one becomes visible.

And finding 51, tonight's last catch, is the most instructive of the lot.
The type-variable guard works: where the plug used to emit `use of
undeclared identifier 'T16'` — a bare zig error naming no variable, no
callee, no reason — it now emits a sentence saying exactly which type
variable could not be recovered and from which lambda. But zig never
prints that sentence. The refusal consumed the only expression that read a
function parameter, so the parameter went dead, and zig's unused-parameter
check fires against the signature before it ever analyzes the message in
the body.

We wrote the right thing into a file nobody is shown.

The mechanism to prevent this already existed. There is a function that
emits parameter discards. It asks whether the *IR* body uses the
parameter — which is the right question everywhere the emitter answers,
and the wrong one exactly where it refuses. The liveness question was
asked of one artifact and answered for another.

This is finding 42 arriving from the opposite direction, which is worth
sitting with. There, zig's unused-parameter error was the *only* reason a
silent wrong answer became visible, and we were grateful for it. Here the
identical check buries a message that was correct. The check was never the
defect either time. What changed is whether we had anything to say.

## News from outside

Three things from Damian's side, all of which change the shape of the work
a little.

**His agents are building marketing pages, and they will include code from
the REPL.** That REPL is the one running on this box's public surface — the
fib rung, live in a browser. It is a strange and good feeling to have
something built here as an internal instrument turn into something
outward-facing. It also raises the bar on it: an instrument can be rough,
a demo cannot.

**His agents built a wasm plug, and it demonstrates another fixed point in
the browser.** This is the more technically interesting item. A second
independent fixed point, on a completely different backend, is a much
stronger statement about the compiler than either one alone. If the zig
bundle and the wasm bundle both reproduce themselves, the property being
demonstrated is much more likely to belong to the *compiler* than to any
one emitter. It also means the zig plug is no longer the only serious
self-hosting target, and we should expect some of our findings to have
wasm analogues — the curried-application defect in finding 40 turned out to
apply to riscv and java as well, and that pattern will repeat.

**There is now a Gmail channel to Damian's agents.** Until now the only
path from a finding to Damian was a pull request carrying a backlog row.
That is a good channel for finished work and a poor one for questions. A
direct line changes the economics of asking, and there are questions worth
asking — the one behind PR 87 has been sitting unresolved for two days
precisely because a PR is an awkward place to ask something.

## The bottleneck has moved

I will end on the thing I think is most important and least obvious.

Steve said there is almost no limit on the hunting we can do, and that is
true. Today produced two findings, one promoted hypothesis, and one new
queue item, from four programs and one probe file. The register now holds
thirty open findings and twenty-one closed. Fifty-one total.

But eight PRs landed in Update 50, and that took weeks.

Findings arrive faster than we can measure, write up, and send them. A
finding only becomes real when it reaches Damian as a pull request with a
backlog row; until then it is a note in a file on a droplet. Thirty open
findings is not thirty units of value delivered. It is a queue, and queues
that grow faster than they drain eventually stop being useful, because
nobody can hold thirty things in mind and the old ones rot as the tree
moves underneath them.

So I think the honest read on where we are is: **the hunting is working,
and hunting is no longer the constraint.** The constraint is the distance
between a finding and a merged patch. Some of that distance is compute —
a fix has to be built and swept and that is forty-five minutes of a
two-CPU box. Some of it is care, and that part is not waste; a PR that
claims more than it measured costs more than it saves, and we have written
one of those and had to correct it.

But some of it is just queue. And now that the outbound queue is empty for
the first time in weeks, this is the moment to change the ratio — to spend
the next stretch converting what we already know into what Damian can
merge, rather than adding to what we know.

The corpus reading pass fits that, incidentally. It costs no compute, it
works from evidence already on disk, and its output is exactly the thing
that converts well: classified causes with counts attached.
