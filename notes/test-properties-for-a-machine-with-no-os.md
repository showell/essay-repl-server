# Test properties for a machine with no OS

*2026-10-05. Where the Antithesis-style SDK stands after its first day, and
how it serves your four goals: a sturdier TCP table, tests at two speeds, a
Zig SDK Antithesis could take, and our own deterministic hypervisor.*

Code: gopher-metal, branch
[`antithesis-sdk`](https://github.com/showell/gopher-metal/tree/antithesis-sdk)
(`45d8db7`), with `ANTITHESIS.md` at its root.

## What exists now

The TCP code that serves lynrummy.com can now state facts about itself as it
runs, and a test run can say which of them held. There are two kinds:

- **"This must always be true."** For example: a retransmission timer never
  goes past its cap. Seeing it false even once means a bug.
- **"This should happen at least once."** For example: three duplicate
  ACKs trigger an early resend. If it never happens, that's not a bug in the
  code. It means our tests never reached that code at all.

The second kind is the one ordinary tests can't express, and it's the reason
to want the SDK at all. A unit test checks a case someone thought of. A
"sometimes" checks whether a randomized test ever got near a case.

The same 18 statements in `tcp.zig` are read in two places:

- **On Linux**, against the TCP simulator: `zig build properties` runs 500
  random network scenarios in about a second once it's compiled, then prints
  a verdict for each statement.
- **On metal**, in the real kernel booted under QEMU: a kernel built with
  `-Dantithesis` prints the statements to its serial port, in the exact
  format Antithesis reads. The judge collects them and a small tool gives
  the verdicts. That flag is off by default, so the image we ship is
  unaffected. The quick gates pass with the SDK compiled in.

## What it has already told us

**No invariant broke.** Nothing was wrong in 500 simulated runs or in a run
of the real server on metal.

**Four paths in the TCP table were never reached by the simulator:**

1. a connection reset by the peer with the exact sequence number;
2. a reset with the wrong number, which must be challenged instead of
   obeyed (the defence against forged resets);
3. giving up on a peer that has gone silent;
4. a stalled half-open connection making room for a new one, which is the
   SYN-flood defence.

Each has a hand-written unit test in `tcp_test.zig`. What none of them has
is a test under loss, reordering, duplication and stalls all at once, which
is where TCP bugs tend to live. The simulator, the one tool that could test
them that way, never goes there. Its client resets only when it gives up
itself, which no passing run does, and its table has one client and two
slots, so nothing ever competes for a slot.

That's a small finding, but it's a real one. Two of the four are security
paths, the forged-reset defence and the flood defence, and the randomized
testing has been blind to them. Nothing announced that before today.

On metal the picture is starker: one judge gate reached 3 of the 18. QEMU's
network never loses a packet, so nothing on the real kernel exercises any of
the recovery code. All of that code has been tested only in the simulator.

## Goal 1: a sturdier TCP table

The next step, which I'm starting after this essay, is simulator scenarios
for the four missing paths: a client that resets (sometimes with a wrong
number), a client that goes silent with data still owed, and more clients
than slots. The test of success is mechanical: the four "never reached"
lines turn into "reached", while every "always" still holds and every seed
still passes the simulator's oracles.

Two things make this more than coverage bookkeeping.

**The properties find holes in the tests; they don't find bugs.** A bug is
found when a new scenario reaches a path and something breaks there: an
oracle, or one of tcp_check's invariants. So the properties direct the
search and the existing oracles judge what it finds. That's the right
division of labour, and it means the simulator's oracles stay the authority.

**There is a mutation tool already** (`tools/mutate_tcp.py`). It breaks
`tcp.zig` on purpose and checks that some test notices. Combined with the
properties it gives a sharper question: for each path we now reach, does
breaking it get caught? A path that's reached but whose mutation survives
is covered in name only. I'd run that once the four scenarios exist.

## Goal 2: tests at two speeds

What makes the hybrid work is this: **the statements are written once, in
the code, and every tier reads the same ones with a different budget.**

| tier | runs | what fails it |
|---|---|---|
| quick gates (today) | `zig build test`: seeds 1–8 plus the regressions, the unit tests | any broken "always" |
| properties sweep | 500 seeds, a second | any broken "always" |
| long run, pre-deploy or nightly | tens of thousands of seeds; the real kernel under a lossy network; later, Antithesis | a broken "always", **or a "sometimes" on the floor list never reached** |

The rule I'd propose: **a broken "always" fails every tier; a "never
reached" fails only the long tier, and only for statements on a short
list.** You could call that list a coverage floor. It holds the paths we've
decided must be exercised before a deploy, with the four above as the
first entries once they're reachable. A quick gate can't promise to reach
rare paths, and shouldn't be blamed when it doesn't. A pre-deploy run can,
and should be.

The weak spot is the metal half of the long tier. The real kernel only
meets a clean network. QEMU can be made to drop and delay packets, and
metal-vmm already can on command, with `WIRE_EAT` and `WIRE_LOSS`. Until
one of them runs in the long tier, the recovery code is tested only on
Linux, against a simulated table. The table is the same code, but the
kernel loop around it isn't, and v4's interrupts and idle halt live in that
loop.

## Goal 3: giving Antithesis a Zig SDK

Their SDKs (Go, Rust, C++, Java, Python, .NET) have no Zig version. What we
have would be a credible start, and one part of it is a real contribution:
the catalog.

Every SDK has to know about every assertion before the program runs.
Otherwise a "sometimes" that never runs is never reported, and it's
exactly the one you need to hear about. Rust uses a linker trick (a crate
called linkme). Go runs a separate tool over the source. Zig has neither.
Ours puts each assertion in a named linker section, and getting that to
hold up took three fixes, each found by a test failing:

- Zig's own linker leaves gaps between entries, so each one is padded and
  tagged.
- Release builds deleted assertions inside code the optimizer proved
  unreachable. That's the worst possible place to lose one, so each is
  exported to keep it.
- An assertion exists only if its function is compiled at all. Zig skips
  functions nothing calls, so assertions in those functions don't exist.
  That limit is documented, not fixed.

Someone writing a Zig SDK would hit all three. That's worth upstreaming.

What upstream would want that we don't have:

- **The rest of the API.** Antithesis's randomness calls (how their
  hypervisor steers a run), `setup_complete`, and the "rich" assertions
  like `always_greater_than`, which give their explorer something to climb.
- **Their real output path.** On Linux that's a library their hypervisor
  provides (`libvoidstar.so`), which their SDKs load at startup when it's
  there; we only write the file fallback. Zig can load a library like that
  (`std.DynLib`), but I haven't tried.
- **Threads.** Ours assumes one, as metal does. A general SDK needs atomic
  counters.
- **Its own package.** It sits in gopher-metal's `src/` today. It already
  depends only on `std`, so moving it out is cheap.

My recommendation: don't build any of that yet. Keep using the SDK here
until it has earned its keep on TCP and one more layer (FAT is next). Then
extract it as its own package with the missing API, and open the
conversation with Antithesis. Their SDKs are open source, so a PR is a
natural channel, but a short note first asking whether they want Zig at all
would cost little. The freestanding serial-port sink stays ours. Nobody
else runs their server without an OS.

## Goal 4: our own deterministic hypervisor

We already have one, parked: **metal-vmm**, built 2026-09-18. The same
kernel with the same seed gives the same run, every byte. It can eat the
nth network frame or refuse the nth disk write on command, and it found
five real defects before you parked it.

Antithesis is, roughly, three parts:

1. a deterministic hypervisor, so any run can be replayed exactly;
2. properties, so a run can tell what happened in it;
3. an explorer, which keeps choosing faults and random values, steered
   toward runs that do something new, meaning properties not yet reached.

We now have small versions of the first two, built separately. **The third
is the gap, and the first two make it cheap.** metal-vmm's "eat the nth
frame, for every n" is already a crude explorer. It's a sweep rather than
a search, but it's systematic and replayable. The properties give it what
it lacked: a way to score a run. A run that reaches a "sometimes" no
earlier run reached is worth keeping and mutating; one that reaches nothing
new is worth dropping. A fault-sweep loop scored by "which statements did
this run reach?" is a small program, and it would make metal-vmm a bug
hunter rather than a fault-replayer.

There's also a structural advantage. Under metal-vmm, the serial port is
the hypervisor's own code. So the assertion lines don't need a log file and
a script: the hypervisor can read them during the run and react, for
instance by forking the run at the moment a rare path is reached. That's
what Antithesis does, and our setup reaches it by a short route.

**Something to check before resuming it.** metal-vmm was built on the fact
that the guest took no interrupts. Since v4 (2026-10-01) it takes them, for
the idle halt. The design looks deterministic-friendly: interrupts are
taken only at the one instruction where the kernel halts, so a hypervisor
can deliver them at an exact, repeatable point. But metal-vmm predates it,
and I haven't confirmed that it still runs today's real server
deterministically. The gates run metal-vmm's checks on the probe kernels;
I haven't looked at whether they cover `gopher.elf` with interrupts on.
That check comes first, before any explorer.

## The order I'd go in

1. **Now:** simulator scenarios for the four never-reached paths; fix
   whatever they find; commit as I go.
2. A long-tier script that runs thousands of seeds and checks a floor list,
   plus a lossy run of the real kernel (QEMU or metal-vmm).
3. Properties in FAT (the cached and on-disk FATs agree; no write outside
   `data/` and `auth/`), where the stakes are a bricked volume, not a slow
   connection.
4. Check metal-vmm against today's kernel, then the scored fault-sweep.
5. Extract the SDK, fill out the API, and write to Antithesis.

Steps 2 and 3 could swap; FAT has the worse failures. I've put TCP first
only because the tooling is already standing there.

## What I'm unsure of

- Whether 500 seeds is the right sweep for the middle tier, or whether the
  middle tier should be a fixed seed list chosen for coverage, which is
  cheaper and repeatable. I lean toward the fixed list once the four
  scenarios exist.
- How much of goal 3 Antithesis would actually want. Their customers
  mostly run containers on Linux, and Zig is a small audience. The catalog
  technique stands either way.
- Whether metal-vmm's determinism survived v4. Unknown until checked, and
  it's the foundation of goal 4.
