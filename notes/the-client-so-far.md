# The client so far

*2026-10-16, evening. A status report on the TCP client (metal-vmm QUEUE
225, with 226 and 227), and the testing behind it, fastest first.*

## Where it stands

The plan in `docs/TWO-KERNELS.md` has 13 chunks. **Eight and a half are
done, all in one day,** most of them by CC:

- **The groundwork:**
  - **Golden traces:** every simulated world's frames are pinned, so the
    reshaping that followed provably changed nothing on the wire.
  - **`tcp.zig` in four files:** with its decisions pulled out as pure
    functions.
  - **The RFC quoted word for word** above the code that does each step.
- **A production fix first (0a-0c):** on a timeout, the kernel used to
  resend its whole window; now it resends the oldest segment, as RFC 6298
  says. It ended the native judge's stall, which I verified with ten
  runs, ten passes.
- **The client itself:**
  - the table holds a connection of its own;
  - `connect`, the SYN-SENT handling, and three deadlines (connect, idle,
    total) that fail fast;
  - ARP, with a cache of one entry.
- **Kernel against kernel, in a simulator:** 300 seeds in under a second.
- **The client against real Linux (chunk 8):** 18 of 18 cases pass in 5 s:
  - a 200 and 300 KB exact;
  - refused, silent, idle, too long;
  - the SYN eaten one, two and three times;
  - single frames lost each way.
- **Two items that weren't in the plan:**
  - **226, the out-of-order queue** (your call this afternoon): a segment
    that arrives ahead of a gap is now held, up to four pieces a
    connection, 32 bytes of bookkeeping each. With reordering on, 0 of 144
    jittered pair seeds fail; 64 did before.
  - **227, a regression the slow tier caught:** 0a broke the case of a
    client that stops reading for a moment. More on that below, because it
    is the most instructive thing that happened today.

**Left:**
- 9, the client as a bootable kernel;
- 10-12, metal-vmm learning to run two kernels as one machine taking
  turns;
- 13, `pair.sh` and the gate.

That is the part where "two unikernels talking" becomes literal, and where
the under-a-minute gate gets measured, not inferred.

**One thing every departure now shares:** each place our TCP departs from
the RFCs says why, in one of five words, and a test holds them to it:
- **bounded:** a hostile peer can't make us hold, answer or wait more
  (4 of 19);
- **fast:** our networks are short and private (5);
- **simpler:** costs a frame or a round trip, never a wrong byte (5);
- **stricter:** we take or believe less than the RFC allows (3);
- **scale:** a handful of peers we name (2).

Denial of service is the minority story, not the main one. Mostly we
depart to fail faster or to stay simple.

## The testing, fastest first

Eight layers, each slower and closer to the real thing than the one
before. The numbers are measured today unless marked.

### 1. Static checks on the source: under a second

**Two checks that read the code as text:**
- every RFC quote must match `docs/rfc/` word for word;
- every `DEPARTS` line must name one of the five reasons.

They are tier 0's cheapest tests, and they keep the literate promise
honest: a quote retyped from memory, or a departure with no reason, fails
the build. Each was proven with a planted error (one changed word; one
untagged line).

### 2. Unit tests with an invariant checker: seconds

**`tcp_test.zig`:** about 100 scripted conversations with the table
("the peer shuts its window, refuses three probes, reopens; the rest
must arrive within 30 ms").

**The multiplier is `tcp_check.zig`:** about 25 rules checked after
*every* step of *every* test. Some are safety ("what was sent is no more
than what was queued"); some are liveness ("our SYN is unanswered and
nothing will send it again", "a deadline is in the past"). So each test
someone writes for one purpose also checks everything else, at every step.

**I planted four client bugs today; all four went red:**
- no timer on the SYN;
- no total deadline;
- the idle deadline counted from the wrong moment;
- the connect deadline applied after the handshake.

The first two the invariants caught; the second two, the tests' own
expectations. **This layer is where most bugs should die,** and the whole
kernel suite runs in about two and a half minutes.

### 3. Golden traces: about 5 seconds (30 cold)

803 simulated worlds, each pinned to a hash of every frame it sent. A
refactor that changes nothing must leave all 803 alone; a change that
alters the wire must say which worlds moved, and why, in its commit.
**An adversary's find today:** no tier ran this check. I claimed
"traces unchanged" for my own fix without running it. It was wrong (10
worlds moved, all still correct). Tier 0 runs it now.

### 4. Kernel against kernel, simulated: under a second

`tcp_pair_sim`: our client's table and our server's table, wired
together in one process, 300 seeds of loss, duplicates, jitter,
reordering and each deadline. **Deterministic and cheap,** so it is
where reordering bugs show first. It is how 226 was proven: a
reordered seed that used to crawl now finishes.

### 5. The simulator sweep with a floor: about 3 minutes

`zig build properties` runs 1,000 plain and rough TCP seeds and 500
crowded ones, 66 s of TCP and 120 s for all the simulators. The other
half of its job is the **floor:** a list of every property that must be
*reached*, so a change that quietly stops the simulators from exercising
a path fails the run. **The second adversary's find:** the client's
properties were never added to the floor. They are now. The first run
says four aren't reached by any simulator (two ARP cases, "refused by a
reset", a tiny MSS). Those are reached only by unit tests, and each is
either a gap to close in the pair sim or a line to move. I'm on it.

### 6. Linux as the witness, natively: 5 to 35 seconds

`tcp.zig` compiled as an ordinary Linux program on a TAP device, against
the real Linux TCP stack:
- **Linux as the client** (the server judge): about 30 s;
- **Linux as the server** (chunk 8's fetch cases): 18 cases in 5 s.

**This is the first layer where the other side is someone else's code.**
Everything above checks our TCP against itself or our own models; here a
disagreement with Linux is a fact. The native judge is where the original
stall was found.

### 7. The real kernel on metal-vmm: about a minute of runs

Our own hypervisor boots the real kernel, deterministically, and breaks
things on purpose:
- **lost frames:** lose frame 1, then 2, and so on (now a sample: the
  first 4, the last 4, every 5th), 40 runs in 10 s;
- **rough clients:** seven ways to misbehave (resets, vanishing, a window
  shut for 1.5 s, damage, a SYN flood), 10 s;
- **seeded fault schedules:** 100 of them with a disk volume attached,
  29 s.

The runs take under a minute; building the two kernels is 156 s on top,
now timed apart. **This layer caught 227.** No faster layer noticed that a
client pausing its reading for a moment got 5 KB of a 27 KB page. Why it
slipped through is worth naming:
- the simulator's client holds out-of-order bytes, so the hole our
  kernel left got filled anyway;
- the simulators judge *completion*, not *latency*: a transfer that
  finished late still passed.

The real kernel ran out of patience after 2 s, which is exactly the kind
of fact only a real boot keeps.

### 8. Two real kernels, and the full application: next, then minutes

- **metal ↔ metal (chunks 10-13, planned):** two metal-vmm processes
  taking turns, each running a real kernel, one the client and one the
  server. Deterministic by construction, so a failure replays exactly.
  Inferred at about 22 s for the gate's scenarios; the whole gate, Linux
  pairings included, aims at under a minute.
- **QEMU judges (tier 3):** the whole lynrummy.com application against
  its Linux twin, minutes. The client isn't in this layer yet.

## What the day says about the layers

**The fast layers carried almost everything.** A day of deep TCP surgery
(a file split in four, a new state machine, a new receive queue) went
through with the slow tiers green but one. That is the payoff of
invariants checked at every step and golden traces pinned before the
surgery began.

**The slow layer earned its keep exactly once, and that once mattered.**
227 was a production regression, merged to master, that every fast layer
passed. The lesson isn't "run the slow tier more"; at under 4 minutes,
it now runs whenever we like. It's the two blind spots it exposed, which
the fast layers can now be taught:
- a simulated client that doesn't forgive holes;
- an oracle that times the transfer, not just its ending.

**The adversary work found two checks that had quietly stopped checking:**
- the traces that no tier ran;
- the floor that never learned about the client.

Neither was a bug in the code. Both were bugs in the trust we put in the
tests, which is the kind nobody notices until a bug walks through.
