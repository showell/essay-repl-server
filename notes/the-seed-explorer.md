# The seed explorer

*2026-10-07. A design for steering our simulators the way Antithesis steers
a system, driven by what we actually want found. For Steve; once you've
weighed in, the build goes to CC.*

## What we have, and what's missing

Every simulator in gopher-metal (`tcp_sim`, `fat_sim`, `page_sim`,
`ready_sim`, `store_sim`, `durable_sim`, `pure_sim`, `floor_sim`) has the
same shape: `runSeed(seed)` makes a PRNG from the seed and plays out one
whole story, every decision drawn from it. `zig build properties` runs seeds
1 to N and reports which of the 248 properties on the floor were reached.

That's **blind**: seed 7,341 knows nothing of what seeds 1 to 7,340 found.
What Antithesis adds on top of determinism and properties, which we already
have, is **steering**: it notices when a run did something new, and spends
its next runs near that moment instead of rolling fresh dice from the start.

The evidence that we need it is already on the floor:

- **Two properties are reached only at `long.sh`'s 300 FAT seeds, never at
  the default 20** ("a FAT32 entry's first cluster is past 65535", "a run of
  sectors fails to read"). Blind search pays 15× for them.
- **Some refusals need a coincidence**, like the FAT writer's re-checks that
  need "a disk that lies between two reads." CC wrote last night that a
  case could reach them "but finding that number by search is fiddly." That
  is exactly an explorer's job.
- **The bugs blind seeds did find came late**: 15 failures in 50,000 seeds
  last week, with the flood eviction found by volume rather than by aim.

## How Antithesis does it, as far as its public docs say

I'll stick to what Antithesis has said publicly, and say where I'm
inferring.

1. **It owns every source of nondeterminism.** Time, thread scheduling,
   network faults and randomness all come from the platform. Its SDK even
   offers `get_random` and `random_choice`, so a program's own choices are
   handed to the platform rather than made privately. metal-vmm already
   does this for the kernel: its clock and its entropy are ours.
2. **It explores a tree of timelines.** From a moment it found interesting,
   it goes back to that moment and lets the future play out differently.
   The past is kept and the future is re-rolled. It does this with
   whole-machine snapshots. (I'm inferring the details; the "multiverse"
   framing is theirs.)
3. **It decides what's interesting** from coverage and from the SDK's
   assertions. A `sometimes` that hasn't held yet is a target. Numeric
   assertions report how close a run came to a limit, and the platform
   steers toward the edge. Our SDK already emits both: since items 61 and
   73, every comparison reports its edge and its reach.
4. **It doesn't shrink.** A failure comes back as a reproducible timeline
   with its history, not as a minimised input. (This is the difference from
   Hypothesis and from AFL-style fuzzers, which mutate and shrink inputs.)

The first, third and fourth we can copy almost as-is. The second we copy
with one substitution, which turns out to be cheap.

## The design

### 1. A recorded run is a tape of draws

Every simulator takes its randomness through zig's `std.Random`, which is an
interface: a pointer and a `fill` function. So the explorer's source of
choices **is a `std.Random`**, and no simulator's logic changes:

- **Recording:** draws come from a PRNG, as now, and each `fill` call's
  bytes are appended to a tape.
- **Branching:** the first *k* fills are replayed from an old tape, and
  every fill after that comes fresh from a new seed.

A run's **position** is the number of fills so far. A seed's run, recorded,
is byte for byte the run it is today. The one change to each simulator is a
second entry point beside `runSeed(seed)`: `runWith(random)`.

**This is how we copy Antithesis's snapshots.** A simulator run takes
milliseconds, so going back to a moment means replaying the tape's prefix
up to it, not restoring memory. The past is identical because the
simulators are deterministic, and the future differs because the draws
after position *k* do. That's exactly "keep the past, re-roll the future,"
without a snapshot.

### 2. Moments: where a run did something new

The SDK gains one hook: when a property is **first reached in a run**, or a
comparison sets a **new edge or reach**, it records the run's current
position. A run's result is then a tape plus a list of moments: *at
position 4,812, "tcp: a shut window is probed" fired; at 6,003, slots in
use reached 61.*

A moment is **new to the explorer** if no run before it reached that
property, or got that close to that edge.

### 3. The loop

```
corpus = []
repeat until the budget is spent:
    with probability p (say 0.2): a fresh seed          ← blind, as today
    otherwise: pick a moment from the corpus, weighted
               replay its tape up to that position
               (or a little before), re-roll the rest
    run it; record its moments
    if any moment is new to the explorer: add the run to the corpus
    if an oracle failed: save the tape; that file is the reproduction
```

**Which moment to pick** is the one real policy. The first version,
deliberately simple:

- **Rarity first.** A moment for a property few corpus runs reached weighs
  more than a common one.
- **Edges second.** For a comparison whose limit is still unreached (slots
  in use never hit the table's size), favour the run that got closest:
  Antithesis's numeric guidance.
- **Unreached `sometimes` and `reachable` sites get no moment yet.** The
  explorer can't aim at what nothing has touched. That's what the blind
  fraction `p` is for, and why it's never zero.

### 4. The explorer is deterministic too

The explorer's own choices (which moment, which new seed) come from one
seed of its own. So `zig build explore -Dsim=fat -Dbudget=2000 -Dseed=1` is
the same exploration every time. That makes it something `long.sh` can run
as a gate, and its floor something a regression can break, like any other
tier.

### 5. What it's measured against

At equal budget, blind seeds against the explorer, per simulator:

- the floor's MISSes left at the end;
- runs to first reach, per property;
- **the benchmarks above**: does the explorer reach the two long-tier FAT
  properties within the default 20-run budget that blind seeds need 300
  for? Does it find the FAT writer's "disk lies between two reads" case
  that CC couldn't hand-place?

If it doesn't beat blind seeds there, we've learned that cheaply, and the
code is small enough to delete.

## Our use cases, in the order I'd serve them

1. **The simulators** (everything above). In-process, fast, and CC can
   build and prove all of it without KVM.
2. **The Store judge.** `store_sim` is the slowest simulator (most of
   `properties`' five minutes) and the one whose bugs would cost data, so
   aimed runs matter most there. Power cuts at the exact write of a
   `replace` are moments worth branching from.
3. **metal-vmm, later.** The real kernel's runs already draw every fault
   from `FAULT_SEED`. The same tape can sit under metal-vmm's own decisions
   (which frame to eat, when the peer resets, which write the power fails
   after). Branching there costs seconds per replay, because a kernel run
   takes seconds, not milliseconds. metal-vmm's device snapshots (built,
   device side only) could make it cheaper; that's a later question, and
   the closest we'd come to Antithesis literally.

## Where I'd differ from Antithesis, and why

- **Replay instead of snapshots, for the simulators.** It's cheaper to build
  and equivalent for deterministic in-process code. Snapshots matter only
  when a run is expensive, which is the metal-vmm phase.
- **No mutation of single choices, at first.** Changing one draw in the
  middle of a tape (Hypothesis's and AFL's move) shifts the meaning of
  every draw after it. Branching keeps the past exact, which is
  Antithesis's choice and the easier one to reason about. Mutation is a
  good experiment *after* the baseline is measured.
- **No shrinking, at first.** Antithesis doesn't, and a saved tape is
  already a reproduction. If a failing tape turns out to be too long to
  read, "truncate the tape and re-roll" is a cheap shrinker to add later.

## Questions for you

1. **Gate or tool?** Should a fixed-budget, fixed-seed exploration join
   `long.sh` with a floor of its own, or stay a tool we run when hunting?
   I'd say tool first, gate once it has beaten blind seeds once.
2. **The blind fraction.** Starting at 20% is a guess. Fine as a knob?
3. **Who builds it.** All of section 1 to 5 is CC-shaped: SDK work plus a
   `runWith` beside each `runSeed`. I'd queue it as a long assignment like
   last night's, ending in the benchmark table. The metal-vmm phase stays
   with the box, after we've seen the numbers.
4. **One determinism check first.** Replaying a full tape must give the
   identical run, the same properties and the same digest. CC found
   uninitialised bytes leaking into a simulator once. I'd make "replay
   equals record" the first test of every `runWith`, before any
   exploring.
