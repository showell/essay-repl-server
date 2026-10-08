# The strange path

*Written at 02:15 UTC on 2026-10-08, while the first overnight soak is still
running and has told us nothing yet. So this is about the path, not the
results.*

## What we are actually doing

Strip the vocabulary away and the last two days look like this: to serve a
chat site for a few friends, we are building a small Antithesis. A
deterministic hypervisor (metal-vmm), an assertions SDK (zig-coverage-sdk),
simulators for each pure layer, and now a seed explorer: a program whose job
is to steer the other programs into corners nobody wrote a test for.

That is a strange thing to be doing, and I think it's worth saying out loud
which parts of it have already paid, which parts haven't yet, and what would
tell us to stop.

## What has already paid

Most of the payoff so far came from **agreement**, not exploration:

- **The Store judge.** It ran angry-gopher's own `store.zig` over Linux and
  over metal's real FAT stack against one model. That found and fixed four
  places where the two hosts gave different answers, plus a temporary file
  both left behind. Those were real bugs in served code, and they were cheap
  to find.
- **`limits.zig`.** Writing every request bound down in one file found Caddy
  refusing documents the app accepts (1 MB vs 1 MiB).
- **The small-body pre-read**, the Bus fix, `has()` no longer swallowing
  errors. Each came from asking "do the two hosts mean the same thing here?"
- **CC's mutation run.** It planted 85 bugs and the tests caught 63. FAT
  caught the fewest, 8 of 16. That told us where our tests are weak with no
  exploration at all.

The common thread is **making the code say what it means, in one place, on
both hosts**. That is your "design for testability" instinct, and it has the
best record of anything we've tried.

## What hasn't paid yet

The explorer has found **no bugs**. Every number I've given you about it is a
count of *properties reached*, and a property reached is not a bug found.
A `sometimes` that fires means a corner was visited. It doesn't mean the
code was wrong there.

The lab results are real but carry two caveats:

1. **The lab is mine.** I wrote the synthetic stories, then tuned the
   explorer against them. "Moments about double depth" is true on a story
   built to have depth. It's a fair test of the mechanism, and a weak test of
   whether gopher-metal has corners like that.
2. **Blind seeds are a strong baseline.** On fat_sim, at small budgets, blind
   beat every clever variant: the scenario choices at the top of a run matter
   more than anything after them. Real simulators may be mostly that shape:
   wide and shallow. If so, a smarter explorer buys little.

The soak is the first honest test, because its simulators are the real ones
and its control is blind runs on the same budget.

## What the soak can tell us

There are three possible outcomes:

- **A failure.** Any run that breaks an oracle is a real bug or a broken
  oracle, either worth the whole effort. The soak prints how to reproduce
  each one: the simulator, the approach, the explorer seed and the run
  number.
- **Properties only the explorer reaches**, round after round. That is a
  smaller win. It says our simulators *have* depth, and that the explorer is
  the cheaper way to reach it than more seeds.
- **Nothing**: all three approaches reach the same things. Then the
  simulators are wide and shallow. Blind seeds were already doing the job,
  and the explorer is a tool waiting for a deeper subject.

My guess is mostly the third, with a few TCP properties in the second: the
rough-peer and crowd corners that were already "reached by timing luck" on
the metal floor. I'd rather be wrong.

## Where the path converges, if it does

The simulators are the cheap stand-in. The real Antithesis move is to run
**the actual kernel** under a deterministic hypervisor while a tape decides
every fault: which frame is lost, when the disk fails, what the peer lies
about. We already own both halves:

- metal-vmm makes a kernel run a pure function of its knobs;
- the explorer steers anything whose randomness comes from a tape.

Joining them means metal-vmm takes its fault decisions from a tape (a file
of bytes, replayed then extended) instead of from its own seeds. Then
moments, flips and the allocator steer *the production kernel*, not a
simulation of its layers. Each run costs seconds instead of milliseconds, so
budgets are hundreds, not thousands. That's exactly where steering beats
blind sampling, because you can't afford to be blind.

That is the version of this path I'd find hardest to call strange: a
deterministic box that searches for the ways our real server breaks. It's
also a week's work, not an evening's, and it shouldn't start until the soak
says the explorer is worth pointing at anything.

## The zig annoyances, named

These are worth working out on purpose rather than tripping over:

- **A test under `zig build` prints nothing until it exits,** and a test
  that writes to stderr counts as failed. The soak's log sat empty for seven
  hours. Fixed by running the binary directly; now in memory.
- **The simulators are tests, not programs.** They reach for
  `std.testing.allocator` and `std.testing.io` inside, so anything that
  drives them (the bench, the soak) must itself be a test. Simulators that
  take an allocator and an `Io` as arguments would make the soak an ordinary
  program, with the zig test runner out of the picture.
- **Configuration is build options.** Every knob is a `-D` flag on
  `zig build`, which you dislike, and reading the environment needs libc.
  A soak that reads a small config file (or just has good defaults and no
  knobs) would be cleaner.
- **0.16's `std.Io` churn** touches everything that measures time or
  writes a file, so small tools cost more than they should.

None of these is a reason to leave zig. All of them are a reason to give the
simulators a proper library shape, which is also what designing for
testability asks for anyway.

## What I'd do next

1. **Read the soak, then let it decide.** A failure or a steady
   explorer-only property earns the explorer a default (likely the
   allocator), a second night, and then the metal-vmm tape. Nothing earns it
   a freeze: the options stay in the SDK, off by default, and we stop
   spending evenings on it.
2. **Ship v20 regardless.** None of this touches served code.
3. **Put the next effort where the record is best:** agreement between the
   hosts, and the mutation survivors. FAT's eight uncaught bugs are a
   concrete list. Each one is a test that should exist, and writing them needs
   no explorer.
4. **Give the simulators a library shape** when we next touch them, for
   the zig reasons above and because it's the testable design.

The strange path isn't wrong. It's a research bet sitting next to a
production server. The discipline is to keep it from consuming the days that
make the server better, and to let one honest measurement decide how far it
goes.
