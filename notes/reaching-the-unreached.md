# Reaching the unreached

*2026-10-07. For Steve: what to do about a `sometimes` that no test ever
reaches, with or without an Antithesis, and where static analysis fits.
Plainer than [the seed explorer](the-seed-explorer.md); it assumes no
Antithesis background.*

## The problem in one sentence

A `sometimes` (or a `reachable`) that no run has ever reached is a
question: **what has to be true for the program to get here?** Every
strategy below is a different way of answering that question, or of getting
a computer to answer it for you.

Our floor has a short list of these right now. From this morning's sweep,
for example:

- "fat: a FAT32 entry's first cluster is past 65535"
- "fat: a file of 4 GiB or more is refused"
- "rtc: no chip answers"
- "fat: a write finds a file's chain ends before its size"

They look alike in the report, as four MISS lines. They aren't alike at all,
and treating them alike is the main mistake to avoid.

## What Antithesis does, in plain terms

Antithesis runs your whole system inside a machine it controls completely:
the clock, the network, the disk, the thread scheduling, and every random
number your code asks for. Because it controls all of that, any run can be
replayed exactly.

Then it plays a very long game of "what if". It runs the system, watching
which of your assertions fire. When a run does something it hasn't seen
before (a new `sometimes` holds for the first time, or a number gets closer
to a limit than ever), it treats that moment as promising. It goes back to
that moment and tries different futures from there, many times.

That's why it finds weak coverage quickly. Plain random testing spends every
run starting from scratch, so a rare state stays rare. Antithesis spends its
time **near the edge of what it has already reached**, so each new
foothold makes the next one cheaper. It's a search, not a lottery.

What it doesn't do is *understand* your code. It never reads the `if` in
front of your `sometimes`. It finds that state by trying and noticing. So it
works beautifully on states that are rare but reachable, and it's helpless
against a state that nothing in its environment can ever produce.

## First, sort the unreached into four kinds

Before choosing a strategy, ask which kind of unreached it is. Each kind has
a different cure, and three of the four aren't cured by smarter search.

**1. Dead: no path leads there at all.** A function nothing calls, or a
condition that can never be true given the code around it. *Cure:* delete
it, or turn the `sometimes` into an `unreachable` assertion that documents
the impossibility. *No amount of testing helps.*

**2. Only the environment can get there.** "rtc: no chip answers" happens
when the real-time clock chip is missing or broken. No simulator of ours has
a clock chip; only metal-vmm's model does, and today it always answers.
*Cure:* teach the environment to misbehave, which is a knob in metal-vmm
(CC's proposal N1 is exactly this, five knobs for these). *Smarter search
inside the simulator can't help; the state isn't in its world.*

**3. Reachable, but rare under our generator.** "A FAT32 entry's first
cluster is past 65535" needs a FAT32 volume big enough to have more than
65,535 clusters, with a file stored past that point. `fat_sim` makes FAT32
volumes sometimes and big ones sometimes, so it happens, but rarely enough
that the default 20 seeds miss it and `long.sh`'s 300 find it. *Cure:* any of the strategies below. This is where search
shines.

**4. Reachable in principle, unaffordable in this harness.** "A file of
4 GiB or more is refused" needs a 4 GiB buffer in memory. A simulator could
in principle make one, but no test suite should. *Cure:* a design change
that makes the check reachable cheaply (for example, a check on a *length*
that a test can pass without the bytes), or accept it as proved by reading:
the check compares a number against `0xFFFF_FFFF`, and that's evident.

The overnight work already did much of this sorting without naming it. CC's
"For the box" list in `COVERAGE.md` is kind 2. Its `floor_sim` cases (a
damaged partition table, a memory map with one wrong field) cured kinds 3
and 4 by building the state directly. I'd make the four kinds a column in
`COVERAGE.md`, so every MISS says which it is.

## The toolbox for kind 3, from oldest to newest

### Read backward, then build the state directly

The old-school way, and still the most reliable. Start at the `sometimes`,
walk upward, and write down every condition that has to hold on the way:
the `if` around it, the function that calls this one, the state that
function needs. For the FAT32 cluster:

1. `entryFrom` must see `kind == .fat32` and an entry whose high half is
   nonzero.
2. So a directory entry must point at a cluster above 65,535.
3. So a file must have been allocated there.
4. So the volume must have that many clusters, and the allocator must have
   handed out a high one, which it does only after the low ones are used.

Step 4 suggests the shortcut: make a FAT32 volume, mark the first 65,536
clusters as used, write one file. A ten-line test reaches it every time.
That's a **directed test**, and it's what CC's `floor_sim` mostly is.

Its strength is certainty. Its weakness is that it only proves the one state
you thought of, and the thinking is manual.

### Widen the generator ("swarm testing")

A random test generator usually turns every feature on at once with some
probability, which makes rare *combinations* very rare. **Swarm testing**
(Groce and others, 2012) flips that: each run first picks a random
*configuration* (which features exist at all, how big things are), then
generates within it. A run that's only big FAT32 volumes and many small
files reaches the high-cluster case constantly.

Our simulators already lean this way. `fat_sim` and `tcp_sim` each start a
run by choosing a scenario: lossiness, sizes, what goes wrong. Making those
choices more extreme, and more independent of each other, is cheap and
helps every rare state at once.

### Give the target a slope

A boolean target gives search nothing to climb: a run either reached
"cluster past 65535" or it didn't. A **numeric** property gives it a hill.
"The highest cluster any file has been given" can be recorded on every run,
and a run that reached 60,000 is visibly closer than one that reached
2,000. Antithesis calls this numeric guidance, and our SDK already has it:
items 61 and 73 made each comparison report its closest approach.

So a cheap move for any stubborn kind-3 MISS is to add a comparison beside
it that measures *how close* a run came. That costs nothing for blind seeds,
and it's what makes the explorer able to aim.

### Coverage-guided fuzzing (AFL, libFuzzer, and zig's own)

A fuzzer feeds a function random bytes, watches which branches of the code
each input runs, and keeps inputs that reached a branch nothing else had.
Then it mutates those. It's Antithesis's idea applied to one function's
input instead of a whole system.

It's best for **parsers**: the IP and TCP header parsers, the HTTP request
reader, the partition table. zig 0.16 has a fuzzer built in
(`std.testing.fuzz`, run with `zig build test --fuzz`), which instruments
the code's branches itself. I haven't tried it here, and it's marked
experimental, so it's an experiment worth an afternoon rather than a plan.

### Symbolic execution (KLEE, SAGE)

This is the computer doing "read backward" for you. A symbolic executor
runs the code with *unknown* inputs, collects the conditions along each path
(`kind == fat32`, `high_half != 0`, ...), and hands them to a constraint
solver, which answers "here is an input that makes all of them true."
Microsoft ran this (SAGE) across Windows file parsers and found many bugs.

It's the most powerful tool here, and the heaviest. KLEE works on LLVM code,
which zig can emit, but our code isn't C, and a solver drowns in loops over
a whole disk image. For us it's research, not a next step.

### Steering (the explorer)

The seed explorer CC is about to build is Antithesis's move, on our
simulators: remember the moment a run first did something new, and try new
futures from there. It's strongest exactly where blind seeds are weakest:
kind 3, especially with slopes added.

## Are we doing any static analysis?

**A little, and only of one kind.**

What we have:

- **The SDK's scanner** reads the source and finds every property call,
  even in code that's never compiled. Zig only compiles what something
  refers to, so a `sometimes` inside an unused function would otherwise be
  invisible, which is precisely the property the report most needs to show.
  That's static analysis, but of *where the properties are*, not *how to
  reach them*.
- **The zig compiler** itself catches a lot (types, unused variables,
  integer overflow in debug builds). That's correctness, not reachability.

What we don't have: anything that reasons about **paths**, meaning which
conditions lead to a property, or whether any input can satisfy them.

Cheap static analysis we could add:

1. **Dead-in-this-build.** The scanner knows every property. Each build
   (the kernel, the simulators) knows which ones it compiled. The
   difference is code that build never refers to. A property that's in the
   source but compiled by no build is likely kind 1: dead, or waiting on a
   caller. That's a few lines in `report.py`, comparing two lists we
   already produce.
2. **A "why unreached" sheet.** For each MISS, print the enclosing
   function, the `if` and `else` conditions around the property, and every
   place that function is called from. The scanner already parses the
   syntax tree, so the conditions are a short walk up it; callers are a
   search. That's the raw material for reading backward, gathered
   automatically.

And the honest part: **the best path analyzer available to us is a model
reading backward with that sheet in hand.** That's what CC did overnight,
for dozens of properties, writing directed tests in `floor_sim`. It worked.
It wasn't a tool, though. It was judgment, applied one property at a time,
with no record of why each was hard. Making the sheet automatic, and the
four kinds a column, turns that into a routine anyone can audit.

## What I'd do

1. **Sort every MISS into the four kinds**, as a column in `COVERAGE.md`.
   That alone says where effort is useless: smarter search on a kind-2
   property is wasted.
2. **Add slopes** beside the stubborn kind-3 properties: a numeric
   comparison for "how close." It helps the explorer and costs nothing
   otherwise.
3. **Build the "why unreached" sheet and the dead-in-this-build check** into
   `report.py` and the scanner. Both are small and both are SDK work CC can
   do.
4. **Let the explorer run**, then measure it on the kind-3 list.
5. **Try zig's fuzzer on one parser** as an afternoon experiment.
6. **Leave symbolic execution** as a someday.

Items 1–3 are small and fit well right before the explorer in CC's queue,
since they sharpen exactly what it measures. Want me to queue them?
