# The overnight sweeps: what a hundred thousand seeds said

*Written 2026-10-09, mid-morning, about the first nights of `nightly.sh`,
from 2026-10-08 22:13 to now. The numbers are from `~/nightly/`.*

## The short version

Over about twelve hours the box ran a little over 150,000 seeds against
the real kernel on metal-vmm. They found **two real bugs in the kernel**,
both in how the disk code heals itself at boot, and both are fixed.

Everything else they found was wrong with **us**: with metal-vmm, with the
judge, or with what we were asking the kernel to do.

The most important finding was the quietest. For most of the night, the
sweep was **not looking at the two things it most needed to see**. It
judged no coverage properties at all, and it never sent a request that
wrote to the disk. A clean night meant less than it looked.

That isn't a reason for gloom. It is what a first set of nights is for.
But it changes what "86,600 seeds, 0 failed" should be taken to mean, and
this essay is mostly about that.

## The nights, in order

| night | what each seed asked | seeds | failures | what they were |
|---|---|---|---|---|
| 10-08 22:13 | `GET /`, release kernel | 35,000 | 21 | 2 kernel bugs, 19 a gap in the judge |
| 10-09 00:28 | `GET /`, fixed kernel | 86,600 | 0 | — |
| 10-09 06:31 | `POST /play`, coverage kernel | 31,400 | 39 | 36 a lying disk, 3 a metal-vmm bug |
| 10-09 10:19 | ten request shapes, coverage kernel | running | — | — |

Each night stopped early, by hand, because the one before had taught us
something we wanted the next to use. You allowed that last night ("we
still have plenty of time to re-start"), and it turned out to be the rhythm
of the whole stretch.

## Night one: two real bugs, and nineteen of ours

The first night ran the release kernel, with each seed asking for the home
page while the faults played out: lost frames, rude clients, a refused or
rotten disk sector, a volume that loses its power.

**Seed 16341** rotted a byte in the first of the two copies of the FAT, the
table that says which clusters belong to which file. At boot, the kernel
compares the two copies and, where they differ, keeps the one that checks
out healthier. Here both checked out *equally* healthy, so the kernel kept
the first copy, the rotten one, and wrote it over the good one. The fix:
when nothing says which copy is right, write neither.

**Seed 18771** refused one write while boot was repairing the two copies,
and the whole boot stopped with "the FAT could not be held in memory". But
the FAT *was* held; only the repair failed. The fix: a refused repair is
said, and boot goes on.

Both are the kind of bug the deterministic path is for. They need a
particular byte to rot, or a particular write to fail, at a particular
moment of boot. On a real droplet that might happen once in years, and
then it couldn't be repeated. Here each is a seed number, repeatable
forever, and each now has a test that fails on the old code.

The other nineteen were **our judge being wrong**. A client that reset the
connection before its request was whole left the guest waiting for a
request that would never come. metal-vmm then ended the run as idle, and
the sweep called that a crash. It isn't: a client that left is owed
nothing. Now it's an excuse, "an idle end after the client left", allowed
only when the client really did leave.

## Night two: clean, and blind

With both fixes in, the second night ran 86,600 seeds in about six hours
with no failures at all. That felt good. Then a test sweep the next
morning printed a line I had seen a hundred times without reading:

```
201 runs, 0 properties
```

**The release kernel never reports its coverage properties.** It records
them, but never writes them out. The sweep's rule "a run must break no
property" had been checking an empty list all night. A kernel that broke
one of its own invariants, without also changing the page or crashing,
would have passed.

We ran the release kernel because the coverage build used to cost too much
to compare fairly: printing its catalog at boot took about nine seconds of
the guest's own time, enough to change what a run did. The reason it cost
that much turned out to be worth knowing. **KVM handles the `rep outsb`
instruction one byte at a time, with one exit per byte.** The serial
port's "16-byte bursts" were sixteen exits, not one. The 300 catalog lines
were 111,448 exits.

The fix was **the coverage door**, a private port where the kernel hands
metal-vmm a whole line by address, in one exit, costing the guest no time.
A coverage boot is now 6,660 exits against the release kernel's 6,256,
with the same page. The difference is a disk check that only coverage
builds run.

The second blind spot was in the request. **`GET /` never writes to the
disk.** The unhurt run did 99 reads and 0 writes on the volume. So every
volume fault in the schedule was hurting nothing:
- the power cut mid-write had no write to cut;
- the write cache had nothing to lose;
- the failed sync had nothing to sync.

Night two was clean partly because it never asked the question.

## Night three: writes, and what they showed

The third night sent `POST /play`, which creates a player: 29 sector
writes, on the coverage kernel. The first trial of it failed **every
seed**. That was not the kernel either. fsck complained about something
the kernel does on purpose: after a change, it marks the volume's
free-cluster count as "unknown", which the FAT spec allows. The judge
didn't know that yet.

With that fixed, two more lessons came from the night's 39 failures.

**36 were a disk that lies.** Each had a volume that said it writes
straight through but really held writes in a cache, drained them in its
own order, and then lost its power. What came back was scrambled:
- folders with no `.` entry;
- files whose cluster chains run into free space.

No driver can defend against a disk that lies about its cache, since it
never knows to flush. This morning you decided to excuse it, the way the
durability judge already excuses a write the disk lost. The excuse covers
the disk only, never a wrong page.

**3 were a request that never got an answer.** Each client sent its POST
one or two bytes per packet, and the guest never replied. With no faults
at all, a request in 64 packets was answered and one in 65 was not. It
looked like a hard limit in the kernel. A cold agent traced it, and **it
was metal-vmm's**:
- the simulated client put its whole request onto a 64-frame wire at once;
- its own first packets were pushed off the end;
- with no fault knob turned, the client never resends, so the guest never
  saw the request begin.

The kernel has no such limit. The client now keeps to the wire's room, and
a packet lost that way is reported at the end of the run.

## What the night of shapes is for

The night running now gives each seed one of ten requests:
- reads: the home page, a 26 KB PDF, the game page;
- writes: a player, an account, a game session, a move, a puzzle move
  (339 sectors);
- a refused login;
- two clients at once.

A setup step makes a player first, so the requests that need a login carry
its cookie. Each kind is judged against its own unhurt run.

Its first hundred seeds reached 51 of the kernel's 245 properties, against
42 with `GET /` alone. That's progress, and it is also a modest number.
Most of the 194 still unreached are the disk code's handling of corruption
it never meets, and TCP edge cases no request shape provokes. More seeds of
the same shapes won't reach them. That needs either the explorer steering
the real kernel (the convergence work) or faults aimed at them.

## What I take from it

**The judge matters more than the seed count.** Of the 60 failures across
these nights, two were the kernel's. The rest were the judge, the harness
or the request being wrong. That will shrink as the harness matures, but
for now each night's main product is a better judge, and the bugs come
second. A judge that's too loose hides bugs (night two). One that's too
strict cries wolf (night one's nineteen). Both kinds got fixed this week.

**"Clean" needs a denominator.** "0 failures" is only worth what was
checked: which properties were judged, and which code the requests could
reach. The report line that said "0 properties" was there all along.
Reading the boring lines is part of the job.

**The harness bugs were found the way kernel bugs should be.** Each one
was a repeatable seed, reduced to a minimal case: 64 packets fine, 65 not.
Each was traced to a line and fixed with a test that fails first. That
machinery works, and it doesn't care whose bug it is.

**Being honest about the count:** two kernel bugs in a night and a half is
a modest yield, and both needed a failing disk. Nothing found this week
needs an expedited release. My read is that the kernel is in decent shape
for the requests we've sent it. The kernel is also not where our
uncertainty now lies. It is in what we haven't sent, and in what we
haven't yet checked.

## Next

- **Tonight's shapes night** reports in the morning. It is the first with
  writes, properties and variety all at once.
- **CC's item 122** attacks the excuses added this week, since each one
  widens what passes.
- **The durability judge** still needs its cookie request. The setup step
  now makes one possible.
- **The snapshot work** (`docs/SNAPSHOT.md`): boot once and branch many
  runs from that point. It makes runs about four times cheaper, and it is
  the ground the explorer needs to steer the real kernel toward the
  properties no shape reaches.
