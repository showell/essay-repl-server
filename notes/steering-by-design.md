# Steering by design

*2026-10-07. Third in a row, after [the seed explorer](the-seed-explorer.md)
and [reaching the unreached](reaching-the-unreached.md). It folds in three
things Steve said: SAGE feels like the cleanest idea; we own all of our code,
so it should be built to be steered; and today the box drives while CC turns
adversary.*

## Why SAGE feels clean

SAGE (Godefroid, Levin and Molnar at Microsoft, 2008) is "read the code
backward" done by a machine, one run at a time:

1. **Run the program on one real input**, and as it runs, write down every
   branch it took that depended on the input: "byte 4 was not 0x7F," "the
   length was under 512," and so on. That list is the run's **path**.
2. **Take one condition on that path and flip it**: "what if byte 4 *had*
   been 0x7F?"
3. **Ask a solver for an input** that keeps every earlier condition and
   flips that one. Run it. That run goes somewhere new, by construction.
4. **Do that for every condition on the path**, keep the inputs that
   reached new code, and repeat from them.

It's clean because it never guesses. Random testing hopes; Antithesis
notices and returns; SAGE *reasons* about exactly which decision stood
between a run and the code it missed. The price is the solver: SAGE has to
work out, from machine code, how each branch depends on the input, and that
analysis is the hard, heavy part.

## The move we can make that Microsoft couldn't

SAGE was pointed at other people's binaries, so it had to *discover* the
decisions by watching machine code. **We own every line, so we can simply
have the code tell us.**

Look at how `fat_sim` starts a run today:

```zig
const fat32 = rng.uintLessThan(u8, 4) == 0;      // FAT32 one run in four
const mode  = rng.uintLessThan(u8, 4);           // 1 = filling, 2 = crowded
```

To the explorer in the earlier essay, those are just bytes on a tape. If it
flips a byte, it has no idea it just turned FAT16 into FAT32, and the bytes
after it may now mean something different.

Now suppose the code says what it's deciding:

```zig
const fat32 = choices.pick(@src(), "fat: the volume is FAT32", .{ .no = 3, .yes = 1 });
const mode  = choices.pick(@src(), "fat: the run's mode", .{ .plain = 2, .filling = 1, .crowded = 1 });
```

A **named choice point** says where it is, what it's choosing, and what all
the alternatives are, with their usual weights. That changes everything
SAGE needed a solver for:

- **The path is free.** A run's path is just the list of choices it made,
  by name, in order. No instruction tracing.
- **Flipping is free.** "What if this run had been FAT32?" is: replay up to
  that choice, force the other alternative, and let the rest play out
  fresh. No solver, because the alternatives are listed right there.
- **The future stays meaningful.** Every later draw still comes with its
  own name, so a flip early in the run doesn't scramble what the later
  bytes mean.

So we get SAGE's core loop: take a run's path, flip each decision in turn,
keep what reaches something new. We get it without SAGE's hardest part,
because we built the program to describe its own decisions. **That's what
"testable by design" means here: the code carries hooks so a tool can steer
it, not just observe it.** It's also exactly what Antithesis's SDK asks of
you when it offers `random_choice`: hand your decisions to the platform.

## The hooks, all of them

If we take "built to be steered" seriously, it's a short list, and some of
it already exists:

1. **Every decision is a named choice.** The simulators already route all
   randomness through one `std.Random`. Named choices are a thin layer on
   top: `pick` for a list of alternatives, and `range` for a number with a
   name and bounds.
2. **Every target has a slope.** Beside a stubborn `sometimes`, a numeric
   comparison that measures how close a run came ("the highest cluster
   given out" next to "a cluster past 65535"). The SDK has these since
   items 61 and 73.
3. **Every decision worth simulating is pure.** The seams pulled out so far
   (`durable`, `ready`, and CC's proposed `Wait` under `stream.zig`) exist
   so a simulator can reach the decision without a device. Each new seam is
   a new place to steer.
4. **Every run can prove it's repeatable.** Replaying a run's choices gives
   the identical run, checked by a digest. Without that, flipping one
   choice tells you nothing.

The same four hooks work beyond the simulators. metal-vmm's fault knobs are
choices too ("eat this frame?", "cut the power after this write?"), so the
real kernel can be steered the same way later.

## What the explorer becomes

The design from the first essay stays, with one change in what it varies:

- **Antithesis's move:** from a run that did something new, go back to a
  moment and re-roll the future.
- **SAGE's move:** from a run, flip one named choice, keep everything before
  it, and re-roll what follows.

Both are cheap here, both use the same replay machinery, and the benchmark
decides how to split the budget between them. The two FAT properties that
blind seeds reach only at 300 seeds are a good first test, because both sit
behind a named decision (FAT32, filling) plus a slope (how high the
clusters go).

## zig's fuzzer, in its place

zig 0.16's built-in fuzzer (`std.testing.fuzz`, run with `zig build test
--fuzz`) is classic coverage-guided fuzzing: it feeds a function bytes and
keeps those that run new branches. It's the right tool for **parsers**,
where the input really is bytes and there are no named decisions to steer:
the IP header, the TCP segment, the HTTP request, the partition table.
It's worth an afternoon on one parser, alongside everything above. It
complements the explorer; it doesn't replace it.

## Today: the box drives, CC attacks

**The box builds** the explorer itself, in this order, committing at each
step:

1. **The tape** in zig-coverage-sdk: a `std.Random` that records and
   replays, with the replay-equals-record test.
2. **Named choices** (`pick`, `range`) on top of the tape.
3. **`fat_sim` first**: its decisions named, `runWith` beside `runSeed`,
   and replay equals record over 100 seeds.
4. **The loop**: Antithesis's re-roll and SAGE's flip, a corpus,
   moments from the SDK.
5. **The benchmark** on the two FAT targets, against blind seeds at equal
   budget. Then the other simulators, if it earns it.

**CC becomes the adversary.** Coverage says code *ran*; it never says a test
would have *noticed* if that code were wrong. The classic way to measure
that is **mutation testing**: plant a small, deliberate bug (flip a `<` to
`<=`, drop a flush, return early), run the tests, and see whether anything
fails. A planted bug nothing catches marks a weak oracle, and no amount of
coverage reveals it.

So CC's role today:

- **Plant mutants** in gopher-metal's pure layers (`tcp`, `fat16`,
  `page_cache`, the Store, `durable`), one at a time, on its own branch,
  never merged. Run the simulators against each one. Report which mutants
  survived and why: no test reached the line, or one reached it and
  didn't check.
- **Review the box's explorer commits** as they land, adversarially:
  determinism holes, a tape that drifts, a benchmark that flatters.
- **Hand the explorer targets.** Every surviving mutant is a bug the
  explorer should be able to find once it's planted again. "Does steering
  catch what blind seeds miss?" then gets a second benchmark, made by
  someone other than the builder.

This splits the work cleanly. The box builds the steering; CC measures
whether the tests behind it actually check anything. CC needs only zig and
the simulators for all of it.

## What happens to CC's queue

Items 82–86 (device knobs, a full-volume Store simulator, `readAt`, the
stream seam) are builder work, and they're good. I'd **park them** behind
the adversary role rather than drop them. Items 87–92 (the explorer) move to
the box. If you agree, I'll rewrite the queue that way, give CC a mutation
item with the rules above, and start on the tape.
