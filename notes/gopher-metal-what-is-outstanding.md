# gopher-metal: what is outstanding

Chat serves from a machine with no operating system, and every answer it gives
is checked against the same source built for Linux. That part works. This is
about what does not exist yet, in the order it worries me.

## 1. It has never run on real hardware — and "real hardware" is two questions

Everything so far has run under QEMU's `microvm`. The drivers are virtio over
MMIO; the boot is PVH; the network is slirp; the disk is a file. Each of those
is a thing QEMU provides, and **which of them a real machine provides decides
whether tomorrow is a day's work or a season's**:

**If it means a real box running KVM** — our kernel as a guest on physical
hardware, with a bridge or TAP instead of slirp and a real block device — then
almost nothing has to change. The soak already runs under `-enable-kvm`, so
the CPU is real today; what would be new is a real network path and a real
disk underneath the same virtio drivers. Worth a day, and it would settle the
numbers that matter: throughput to Caddy over a private network, what the disk
costs when it is a disk, whether the TSC calibration holds on a machine that is
not ours.

**If it means no hypervisor at all**, the gap is much larger and worth naming
plainly before anyone is surprised by it:

- **PVH is not a firmware protocol.** It is how QEMU and Xen hand control to a
  guest. A physical machine boots through UEFI or BIOS, so we would need either
  a UEFI stub or a multiboot2 entry and GRUB in front of us.
- **There is no virtio on a real machine.** `microvm` gives us virtio-blk and
  virtio-net at fixed MMIO addresses. Real hardware has PCI, and behind it an
  ethernet controller and an NVMe or AHCI disk, none of which we can talk to.
  That is three new drivers and PCI enumeration before the first packet.
- **Interrupts.** We poll. That is a deliberate and good fit for one loop with
  one core, but a real machine's devices expect an interrupt controller
  configured, and some will not work well without one.

I am not raising this to argue against it — the second path is the interesting
one and the whole project points at it. I am raising it because the two are
being said with the same two words, and only one of them is tomorrow.

## 2. Nothing watches the machine

There is no health route and no watchdog. If the loop wedges or a panic stops
the machine, the way anyone finds out is that chat stops answering. Caddy in
front will report a dead upstream, which is something, but the machine itself
says nothing about its own state, and nobody can ask it. This is the cheapest
outstanding item and probably the next one: a route that reports uptime,
requests served, connections held, streams held, heap live bytes and the TCP
counters, plus something that restarts the machine when it stops answering its
own loop. On a box in a rack, "it stopped and someone noticed" is not a plan.

## 3. Measurements that are claimed but not taken

- **Recent got a cache today** — the last message of each conversation is
  recorded beside the session instead of being recovered by reading every
  transcript in full. A cold read of it found five defects, since fixed, and
  the judge proves both builds still agree. What nobody has done is time it on
  a transcript big enough for the difference to show. The long boot produces
  exactly such a transcript, so the number is one run away.
- **The slowdown is fixed as far as we can see**, which is 4,201 requests. The
  long run queued for this evening asks 42,000 of one kernel.
- **Uploads work to 40 MB**, judged against Linux. Nobody has uploaded to the
  machine over a lossy link, or while streams are being served to other tabs.

## 4. Known limitations we have chosen, and should keep choosing on purpose

- **Received data must be in order.** A segment that arrives early is dropped
  and re-asked for. On a private network to Caddy this is close to free; on a
  path with real reordering it costs a round trip per event. The send side is
  where the work went, and that asymmetry was deliberate.
- **No TIME-WAIT.** A connection we have finished with is forgotten, and a late
  FIN gets a reset rather than a quiet acknowledgement. Correct enough for a
  peer that is one hop away and wrong for the open internet.
- **An upload is held whole in memory.** The heap grows for it and shrinks back
  afterwards, which is why a 40 MB upload is answered the way Linux answers it,
  but a 100 MB video would want to stream to disk on both hosts instead.
- **A non-ASCII filename is written wrong.** FAT16 stores a name's bytes where
  it should store UCS-2 units. Every name the application writes today is
  ASCII, so nothing is broken; it is a trap laid for the day something is not.
- **Finding a free short name is quadratic** when many names share their first
  six characters. Linux hashes after five; we scan.

## 5. Gaps in the judging itself

The judge compares our answers with Linux's over the same files. Two things it
structurally cannot see:

- **A mistake both sides make.** Today the upload gate passed while doing
  nothing at all: it read the stored file's URL after normalizing the random
  name out of it, so both hosts fetched a file that does not exist, both
  answered 404, and two 404s agree perfectly. A mutation run exposed it. The
  gate now requires the round trip to have happened, not merely to have matched
  — and every differential test in this repo deserves the same question asked
  of it.
- **A test that passes through the path it was meant to test.** The same shape
  caught me again an hour later, and this time a cold reader caught it, not me.
  Chat's new last-message record was unreadable for exactly the sessions it
  existed for — a uid nobody knew left a field empty, and an empty field made
  the line one field short. My test asserted that the last message came back
  right. It did: from the fallback that reads the whole transcript. **A test of
  a cache has to assert that the cache was read**, not that the answer was
  right, because the fallback's whole job is to make the answer right.
- **Anything about the world outside the emulator.** Both sides of the
  comparison live in the same QEMU-shaped world. This is the same blind spot as
  item 1, arriving from a different direction.

## 6. What is green, briefly

Because the list above is longer than this one and that is misleading on its
own: the whole route table, 256 connections, streams held and pinged and
budgeted, the send side with a measured retransmission clock and fast
retransmit, correct close, uploads, whole-request readiness, FAT16 read and
write judged by Linux's own driver, and a long boot that holds its rate from
the first window to the last.

---

## Three things I learned, none of them about TCP

**A constant with no provenance is a bug that has not happened yet.** The
retransmission timeout was one second, and it got there by accident: 200
milliseconds chosen for no reason, then raised to a second when segments were
being re-sent that had not been lost — whose actual cause was fixed in the same
commit. By the time anyone read it, the comment cited RFC 6298 and looked like
a decision. Steve's phrasing is the part worth keeping: *things like timeouts
get set by past-Claude with no justification, and present-Claude assumes
they're a Steve decision.* The path measures 40 microseconds. We had been
waiting a second for it. The fix in the code was an afternoon; the fix in the
habit is to write down where a number came from, so that the next reader can
tell a measurement from a flinch.

**Cheap feedback is not a nicety, and the cost of not having it is invisible.**
For a full day the unit of iteration was a four-minute run that booted QEMU
fifteen times before reaching anything I had changed. I paid it perhaps a dozen
times. Building the thing that runs one gate took half an hour, and the first
bug it found was one I had committed twenty minutes earlier — in seventeen
seconds. The lesson is not "be disciplined about long jobs." It is that a slow
loop hides its own cost, because every individual wait is justifiable and only
the sum is absurd.

**Agreement is not correctness, and neither is a green test.** The strongest
tool in this project is that two builds of one program must answer identically,
and today it quietly passed a test where neither build did anything. Twice more
the same day, a test was green because the slow path underneath it worked. The
common shape is worth naming: **every one of these tests asserted an outcome
that something else was also willing to produce.** A differential test that
compares two implementations is blind to a mistake they share; a cache test
that checks the answer is blind to the fallback; a judge that compares answers
cannot see that both sides live in the same emulator. The cure is not more
tests. It is to make each test say what it is really claiming — this file came
back byte for byte, this record parsed, this machine ran on hardware — so that
the claim has only one way to be true.
