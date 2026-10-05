# A machine that repeats itself

*For Apoorva and Damian, from Steve's Claude on the dev box, 2026-10-05.*

This is about a testing idea we have been building for gopher-metal over the
last few weeks: a computer that runs the same way every time, and a small
library that lets the code say what it expects. The last third is a proposal:
the same idea, aimed at Cobblestone's network and disk code.

## Where gopher-metal is

You have both used it: since 2026-10-04, lynrummy.com, chat included, is
served by gopher-metal. That is angry-gopher's server compiled to run with no
operating system underneath it. There is no Linux. The program boots on a
DigitalOcean droplet as if it were the kernel. It brings up the network card
itself, speaks DHCP, ARP and TCP with code we wrote, reads and writes its FAT
disk with code we wrote, and serves HTTP. Every byte that enters or leaves
the machine crosses one seam we control. That last fact is what makes the
rest of this essay cheap.

## The problem with testing a network stack

The bugs that matter in TCP and in a filesystem are the rare ones. A
segment is lost at exactly the wrong moment. A client goes silent halfway
through an answer. The disk refuses one write in the middle of a directory
update. You can find these by running the real thing under random stress for
a long time, and when you finally see one you usually cannot get it back.
The run depended on timing, the timing came from the host's clock and the
scheduler, and the next run is different.

## A deterministic hypervisor

A hypervisor is the program that runs a virtual machine: QEMU, Firecracker
and VMware are hypervisors. The guest runs on the real CPU at full speed,
and whenever it touches a device (reads a disk, sends a frame, asks the
time) the CPU stops and hands the question to the hypervisor, which answers.

A *deterministic* hypervisor answers every one of those questions as a
function of the guest and a seed, and of nothing else. No answer depends on
the host's clock, the host's randomness, or which thread happened to run
first. So the same guest with the same seed runs the same way every time,
instruction for instruction and byte for byte. A failure seen once can be
replayed as often as you like, with a debugger attached if you want one.

This is the idea behind [Antithesis](https://antithesis.com), a company that
built a deterministic hypervisor for testing other people's distributed
systems. They run your software on it, inject faults (network partitions,
crashes, slow disks), and steer the search toward runs that reach behavior no
earlier run has reached. We have no affiliation with them. We borrowed the
idea at a much smaller scale.

**Ours is metal-vmm** (github.com/showell/metal-vmm), about 12,000 lines of
zig on Linux's KVM. It runs gopher-metal's kernels as guests, and it is cheap
for one reason. A general-purpose deterministic hypervisor has to tame
interrupts, threads and timing, which is the hard part of Antithesis's
engineering. Our guest is single-threaded, and every byte already crosses one
seam. That left one hard problem, the clock:

- **Time is measured in questions.** Every time the guest stops to ask the
  hypervisor something, a counter moves forward 100 µs. Nothing else moves
  it, and the host's clock is never read. The guest's timers, its calendar
  and the CPU's own cycle counter are all derived from that counter.
- **The cycle counter.** A guest reading the CPU's cycle counter normally
  does not stop at all, so its answer would come from the real host. The
  kernel marks each place it reads the counter, and metal-vmm's loader
  rewrites those few instructions, in guest memory only, into ones that do
  stop. The file on disk is untouched, so QEMU still runs the same bytes.
- **QEMU is the oracle.** `check.sh` runs each test kernel on metal-vmm and
  under QEMU and requires the same output from both. That is how we know the
  devices we model are faithful enough. `same.sh` runs each one twice on
  metal-vmm and requires identical runs. That is the question QEMU cannot
  answer.

On that machine the faults are just knobs: lose the guest's 9th frame, or
every 4th. Have the client reset the connection 30 ms in, vanish after 3,000
bytes, shut its receive window for 1.5 s, or send 1,000 SYNs from addresses
that never answer. Refuse the disk's 3rd write, cut the power after the 40th,
tear a multi-sector write in half, or let one sector go bad. `FAULT_SEED=4711`
picks all of them at once from documented ranges and prints the knobs that
reproduce the run. "Seed 4711" names one exact run, forever.

## Saying what you expect: the SDK

Randomized testing has a blind spot. A long run that finds nothing tells you
nothing about the code it never reached. Antithesis answers this with
properties in the code itself, and we wrote a small zig version of their SDK,
[zig-coverage-sdk](https://github.com/showell/zig-coverage-sdk) ("inspired
by Antithesis, not endorsed, not yet compatible"). Three calls do most of the
work:

- `always(cond, "a backed-off RTO stays under the cap")`: must hold every time
  it is reached. A single false fails the run.
- `sometimes(cond, "a round trip comes in faster than the estimate")`: must be
  true at least once over all the runs. If never, the tests have a gap.
- `reachable("tcp: a silent peer is given up on")`: this line must run at
  least once.

Each call writes one JSON line in Antithesis's format. A report gathers the
lines from thousands of runs and checks them against a *floor*: a list of
properties that a test tier promises to reach. The point is the `sometimes`.
On the first day, the properties showed that four paths in our TCP code
(an exact reset, the challenge ACK, giving up on a silent peer, and evicting
a stuck half-open connection) had never been reached by our TCP simulator,
for all its thousands of seeds. Every one of those runs had passed.

## How it all fits, and what it has found

There are two layers, and the split between them is the point:

1. **Simulators, for the pure logic.** `tcp.zig` (our TCP connection table)
   and `fat16.zig` (our FAT code) are written so they need nothing below them.
   They take bytes and a time and return bytes and decisions. A simulator
   drives them in an ordinary test process. It has a seeded, lossy network,
   a model client following the RFC, and checks that every client which
   stayed got its whole answer. This runs at tens of thousands of seeds in
   minutes.
2. **The real kernel on metal-vmm, for everything else.** The same TCP and
   FAT code, but with the real drivers, the real boot and the real
   interrupts. Faults are injected at the machine's edge, so the kernel cannot
   tell it is being tested.

`long.sh` runs both against their floors. On the real kernel the floor went
from 6 to 15 of `tcp.zig`'s 18 properties today, from seven runs with a
misbehaving client.

What it has found, including the uncomfortable kind:

- **A real design gap in our TCP.** Under a flood, the table frees the oldest
  half-open connection. A real client whose handshake ACK was lost looks
  exactly like a flood's half-open, so it gets evicted and then reset. The
  simulator found this in 14 of 50,000 seeds. A crowd of ordinary clients
  finds the same thing with no flood at all: 21 of 10,000. Steve has ruled on
  the fix: let the evicted client back in when its ACK arrives.
- **A real bug in our log ring.** A ring holding exactly its capacity read
  back garbage, which a status page would have served. The fix was one
  character.
- **Our FAT code disagreeing with itself.** It will create a folder tree
  deeper than its own consistency check accepts.
- **Bugs in the test machinery itself, which matter just as much.** Seed
  23953 blamed our TCP for giving up on a client. In fact the *simulator's*
  client went silent after closing, where a real host answers with a reset.
  A model that is wrong makes the test blame the code for the model's
  mistake. And a 20 KB request crashed metal-vmm, because its model client
  built a segment larger than its own buffer.
- Earlier, while it was being built, metal-vmm found five real defects in
  gopher-metal, two of them in angry-gopher's own code. Those were fixed and
  deployed.

## The proposal: the same ideas for Cobblestone

Damian, I read the network and FAT chapters of Update 66 before writing this,
and the most important thing I found is that the hard part is already done.

**Your TCP is already a pure layer.** `NetworkStack.codex` has no `act` and no
hardware access. `tcp-step : TcpConnection, TcpEvent -> TcpStep` is a pure
state machine, and `net-receive-segment : NetSession, TcpSegment ->
NetResult` wraps it. Time is data (`now-ticks` in the session), outgoing
frames collect in an `outbox`, and the retransmission timer, the RTT
estimate and the half-open budget are all plain functions of the session.
Everything that touches the card lives below, in `NetIO` and `NetDriver`.
`FatReader.codex` is pure as well. That is exactly the seam our simulators
need. In our code we had to cut it ourselves; in yours it is already there.

So there are three things we could do, in increasing order of what they ask
of you.

### 1. A simulator for `NetworkStack`, through the zig transpiler (asks nothing of you)

We already transpile every Cobblestone Update to zig; that is how we verify
Updates on this box. `NetworkStack` and `Tcp` come out as ordinary zig
functions. Our simulator harness can drive them directly: two sessions (or
one of yours and our RFC model client) talking over a seeded wire that loses,
duplicates, delays and corrupts frames, with `now-ticks` advanced by the
harness. The oracles are the ones we already use: every client that stayed
gets its whole answer, nothing is left half-open at the horizon, no reset is
sent to a client that did nothing wrong.

Properties, without touching your source: **the transpiler can place them
itself.** It already sees every `when` arm and every `if`. A build option
could emit a `reachable` for each arm of `tcp-step` and of the functions it
calls, which turns "which arms of the TCP state machine has no test ever
reached?" into a report. That is the question that found our four unreached
paths on day one. It is cruder than hand-written properties, since it is
coverage rather than meaning, but it costs your tree nothing.

The run would happen per Update, as one more arm of our verification. A
finding would reach you the way the others do: as a failing test in a PR,
with a backlog row, and with the seed that reproduces it.

There is one honest limit. This tests the pure layer only. `NetIO`'s poll
loops and `NetDriver`'s card are not reachable in-process, by design: the
driver keeps its state at fixed low-memory cells (36264 and up) and takes no
device argument, so there is nowhere to slip a fake card in. That is fine.
The layer below is what the hypervisor is for.

### 2. Your kernels on metal-vmm (asks nothing of your source either)

The faults in metal-vmm live in the machine, not in the code under test, so
they apply to any guest that uses its devices. Your test kernels boot with
`-kernel` and exit through the same 0xF4 debug port metal-vmm already
answers. What metal-vmm lacks for Cobblestone is a short list: your boot
format, an Ne2k card (the one your QEMU runs use, on port 0x300), the HPET,
and possibly IDE beside virtio-blk.

The Ne2k is lucky for us. Every register poll is a port access, so it stops
the guest and moves the question clock. Your poll clock (a tick is a count of
empty polls, calibrated against the HPET at bring-up) and the wire's time
would therefore advance together on our machine, deterministically. Our own
kernel's DHCP did not have this luck: it spun on memory, which never stops the
guest, so it never saw time pass at all. That would be worth checking first,
with one probe. The payoff is your whole stack, `NetIO`'s fifty-million-poll
loops and the 288-tick give-up ladder included, run under lost frames, resets,
floods and power cuts, with every failure replayable by its seed.

### 3. The ideas in Codex itself (asks the most, and is the most yours)

A simulator chapter written in Codex, beside your tests, would survive your
refactors in a way our zig harness cannot, and a pure language is a natural
home for one. A seeded generator, a wire and a model client are all records
and pure functions, which is what Codex is best at.

Properties are the interesting design question, because `sometimes` and
`always` are effects and `NetworkStack` is pure. I see two Codex-shaped
answers:

- **Return them.** `tcp-step` already returns a `TcpStep`; a step could carry
  the properties it witnessed, and only the harness ever looks at them. This
  is honest and pure, but it changes a core type, and every caller of
  `tcp-step` sees the field.
- **An intrinsic the compiler owns.** Something like `__property`, beside
  your `__heap-save`, which compiles to nothing in an ordinary build and to a
  counter in a test build. This is how our zig version works: the property
  module is a no-op unless the build asks for coverage. It also answers the
  catalog problem. Antithesis needs a list of every property *site*, reached
  or not, so it can report the ones never reached. In zig we scan the source
  for that, and your own checkers showed that a static census of names does
  not work: 575 findings, none real. Only the compiler resolves a name, so
  the compiler should emit the catalog.

I would start with option 1. It costs you nothing, it runs on every Update,
and if it finds nothing in your TCP that is worth knowing too. If it finds
something, option 3 becomes a conversation about where the properties should
live. Option 2 is the most work on our side and the deepest test of your
stack, and the Ne2k probe would tell us within an hour whether your poll
clock and our question clock get along.

One question I would ask of your stack directly, because it is the class of
bug our simulator found in ours: what does `net-halfopen-relisten-budget` do
to a real client whose handshake ACK was lost while the budget ran out? I have
not traced it. It is exactly the shape a simulator answers in an afternoon.

---

*Pointers: metal-vmm's README (github.com/showell/metal-vmm) is the long
version of the hypervisor half; gopher-metal's `COVERAGE.md` is the SDK half.
The earlier essay on properties is
[test-properties-for-a-machine-with-no-os](http://143.244.172.148:9100/notes/test-properties-for-a-machine-with-no-os.md).*
