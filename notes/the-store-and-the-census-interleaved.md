# The Store and the census, interleaved

*2026-10-06. Follows [three long tasks for CC](three-long-tasks-for-cc.md):
lines 1 (the Store) and 2 (every refusal named) as one long assignment, and
the tactics that keep CC moving without piling up debt.*

## First, where TCP sits

TCP is not in the Store; my earlier essay blurred the two by calling both
"the floor".

The **floor** is everything under the application's `handle(request) ->
response`: boot, devices, TCP, HTTP, the disk, the clock. The application
reaches the floor through a few narrow **doors**: requests in and responses
out, the Store, the clock, random bytes, the log. TCP is behind the first
door. The application never sees a socket, which is why it doesn't care
whether Linux is under it. The **Store** is the second door: the data, as
named files.

So line 1 builds one door, and line 2 maps the whole floor, TCP included. The
synergy is that part of the floor is directly under the Store: `fat16`,
`page_cache`, `io.durable`, the block driver's flush, `kept_log`. Naming the
refusals there *is* part of specifying the Store, because every error the
Store can answer comes from one of those refusals. Mapping them first means
the Store's error list is written from evidence, not guessed.

## The interleaving

Five phases, alternating between design work and methodical work. When a
design question has to wait for Steve, there's always mechanical work next to
it, so CC never sits idle.

| phase | line | what | done when |
|---|---|---|---|
| **A. The ground under the Store** | 2 | properties in `fat16` (its gaps), `page_cache`, `io.durable`, the block driver's `flush`, `kept_log`, `log_ring`, `gpt`; each reached from a simulator or host test | each module has a row in `COVERAGE.md`'s table; the floor is raised |
| **B. The door** | 1 | the Store interface; the model; the FAT store on the in-memory disk; its error list taken from phase A's refusals | the FAT store passes a host test against the model for every operation, including after a power cut |
| **C. The other side of the floor** | 2 | `proto`, `arp`, `stream` and `Spill`, `request_heap`, TCP's invariants as `always` in a `-Dcoverage` kernel (B15) | rows in the table; the floor raised |
| **D. The twin and the judge** | 1 | the strict Linux store; `store_sim` driving the model, FAT and Linux with the same seeded operations and crashes | `store_sim` runs 1,000 seeds clean in the properties step, and its properties are on the floor |
| **E. The rest, and the census** | 2 + 1 | `scsi`, `virtio`'s rings, `pvh`, `civil`, `wallclock`, `restart`; then angry-gopher's disk calls mapped onto the Store, as a doc | every module has a row, even "nothing to name, because..."; every disk call has a row in the census |

Phase A comes first, ahead of the Store design, because it's safe, it starts
CC in the code the Store will sit on, and it produces the Store's error list.
Phase C is the deliberate rest between two design phases. Phase E ends with
the census, which needs both lines done: it asks of each angry-gopher call
"which Store operation is this, and which refusals can reach it?"

**Out of scope, said explicitly:** DHCP (the box's, B18); any change to
angry-gopher's code; any change to what the kernel does. A property may
observe; it may not steer.

## Tactics: keeping CC moving

**Every item ends in a command and a number.** "Raise coverage in `proto`" is
a direction; "`zig build properties` reaches 11 of `proto`'s 12 properties,
and the 12th is under Questions" is a finish line. Each item in `QUEUE.md`
says which command proves it, and the commit message says what it printed.

**A timebox, stated in the item.** If an item has taken about three attempts
without a passing test, CC writes down what it knows (what it tried, what
failed, the shortest reproduction), marks the item **parked**, and takes the
next one. Parked is not failed, and parked work is often what the box can
settle in a minute with KVM. The thing to avoid is the opposite pair: grinding
for hours on one item, or dropping it silently.

**Refusals are reported, never routed around.** Item 65 showed CC's own
checks can stop work. The rule CC already follows is the right one: say what
stopped it under Questions and move on. The box picks it up. The essay's
scope above is written plainly so nothing in it reads like what tripped
item 65.

**A clear line between what CC decides and what it asks.** CC decides:
names, file layout, test structure, which simulator reaches which property,
the order of modules within a phase, and fixes to its own earlier work. CC
asks, in Questions, and keeps going: adding a seventh Store operation,
anything that changes kernel behavior, anything in angry-gopher, and any
finding that looks like a prod bug.

**A found bug is a test first.** If a property shows a real defect, CC
writes the failing case as a regression test. If the fix is in a pure layer
and small, CC fixes it in the same commit. Otherwise CC files it as a
B-item, with the test committed but excluded from the default run *and named
in the item*, so it's visible rather than silently skipped. Then CC moves on.
Hunting the bug is the box's job, with KVM and prod's logs.

**Push after every item, green.** Each commit leaves `zig build test` and
`zig build properties` passing. CC merges `interrupts` and `antithesis-sdk`
into its branches at each phase boundary, not mid-phase, so the box's merges
stay easy.

**A phase report, five lines.** At the end of each phase CC adds a short
entry to `QUEUE.md`: what was reached, what's parked, what was asked, what
surprised it. That's what lets Steve or the box catch a drift in an hour
rather than after a week.

## Tactics: calibrating debt

You said debt isn't the worry, and I agree; the risk is miscalibration. If CC
is too tidy it slows to a crawl; too loose and the box inherits cleanup it
can't tell from design. The calibration I'd hand CC:

**Fine to leave, and say so in one line:**
- duplicated helpers across simulators (a frame builder in two sims);
- a crude generator that reaches the property, even if a smarter one would
  reach more;
- a property worded awkwardly;
- a module's table row saying "reached by a host test only, no simulator yet".

**Never, whatever the time saved:**
- a test weakened, or an oracle loosened, until it passes;
- a property that can't fire, written to make the count look good (a
  `reachable` behind a condition that's never true);
- a skip without a name;
- kernel behavior changed as a side effect of adding a property;
- a seventh Store operation slipped in without asking.

**The debt ledger.** One section in `QUEUE.md`, one line per shortcut: what
it is, where, and what fixing it would take. The box reads it at merge time.
This turns "debt" from a feeling into a list someone can triage, and it frees
CC to take the shortcut, because writing it down is the whole cost.

## What success looks like when you're back

- `COVERAGE.md`'s table has a row for every module in gopher-metal, with how
  many properties each has and what reaches them.
- The floor is substantially higher than today's, and every MISS left on it
  is either parked with a reason or under Questions.
- The Store exists in gopher-metal with three implementations and a
  simulator that judges them against each other, with power cuts.
- The census tells you which of angry-gopher's disk calls fit the six
  operations and which don't. The misfits are the agenda for the next
  design conversation, and line 3, the seed explorer, has something rich to
  steer.

If that's the direction, I'll write phases A–E into `QUEUE.md` as items, with
the tactics above in `CLOUD_WORK.md`, where they'll outlast this assignment.
