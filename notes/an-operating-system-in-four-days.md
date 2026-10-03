# An operating system in four days

*2026-10-03. A reflection, as promised in "Chat without an operating
system": what it means that a unikernel took about four days of actual
work, spread over three weeks by a park.*

## The numbers, first

gopher-metal's history fits in one line of `git log`:

| day | commits |
|---|---|
| 2026-09-16 | 18 |
| 2026-09-17 | 28 |
| 2026-09-18 | 1, and then parked |
| 2026-10-01 | 35 |
| 2026-10-02 | 252 |
| 2026-10-03 | 32, so far |

In those days:
- **a kernel:** 16,900 lines of zig in 43 files;
- **its tools:** about the same again in probes, judges, droplet scripts
  and checkers;
- **its documentation:** 7,600 lines.

It boots a real DigitalOcean droplet with our own loader, finds its devices
on the PCI bus, speaks TCP, keeps FAT16 and FAT32, restarts itself after a
crash, and serves Lyn Rummy's chat. This morning it read a copy of prod's
real data from a real 16 GiB volume, and agreed with Linux on every page
that wasn't expected to differ.

That's a unikernel: one application and just enough operating system to
run it, built as a single image. Four days is fast for that by any
standard I know of. The interesting question is why, because the obvious
answer, "the models are fast", is only a small part of it.

## Why it was possible at all

**The target was narrow, and that is most of the story.** A general
operating system has to run any program on any hardware for any number of
users. This one runs one program, on one kind of virtual machine, for one
purpose:
- no processes;
- no users;
- no permissions;
- one processor;
- one request at a time;
- three kinds of device.

Each "no" deletes a large part of what makes operating systems hard. It
wasn't cutting corners. The work was shaped to the problem, and the
problem was small.

**The application had already drawn the seam.** angry-gopher threads zig's
I/O interface through everything it does. So moving it onto metal meant
providing one implementation of that interface, not rewriting fourteen
thousand lines: `port.sh` changes one line per file. Zig's standard
library supplied the HTTP server, the cryptography and the allocators
unchanged. A large share of "an operating system" turned out to be "the
parts of Linux that this program actually touches", and that list is
short.

**The development machine was the production machine.** A DigitalOcean
droplet is itself a virtual machine running under KVM, with the same
virtio devices QEMU provides. So QEMU on the box wasn't an approximation of
the target; for practical purposes it was the target. Bugs reproduced on
the box, ran in seconds, and could be repeated thousands of times. The one
thing QEMU couldn't settle (does a reset restart a droplet or power it
off?) took Steve fifteen minutes at a console this morning.

**Earlier work carried forward.** The Roc "floor" experiment, Codex's
bare-metal harness and the deterministic hypervisor had each worked out a
piece: how to boot, how to talk to a serial port, how virtio queues behave.
None of that had to be rediscovered.

## Why it was fast

**There was always an answer key.** Linux running the same application is
a specification nobody had to write. Every change was checked by asking
both machines the same questions and requiring the same answers. This
converts the hardest kind of work, "is this correct?", into the easiest
kind, "are these bytes equal?". A team without an answer key spends most
of its time deciding what correct means. This one almost never did.

**Several opinions, none of them ours.** Our FAT code was checked by a
Python reader written from the specification, by mtools, by Linux's own
driver and by fsck. Each is wrong in its own ways, so when three agree and
ours doesn't, ours is wrong. Speed without this would have meant fast
mistakes.

**The writer and the judge were different Claudes.** CC wrote code, tests
and adversarial reviews from a queue, unattended. The box Claude ran the
slow, privileged checks and merged only what passed. Neither had to trust
the other's claims. Every claim arrived as a commit, and every commit met
the gates. That division was the main reason the volume of work, about
fifty items in one day, didn't turn into a volume of bugs. Today CC
deliberately stopped the machine after every single disk write and found
three real defects. One of them would have left a crashed droplet
refusing to boot forever.

**Verification became the bottleneck, and that is the right bottleneck.**
By the second day CC finished items faster than they could be checked. The
response was to make checking cheaper (thirty minutes down to fifteen),
not to check less. When writing is cheap, the scarce thing is knowing
whether what was written is right, and that's where the attention went.

## On Steve as "mostly a yes-man"

Steve describes his part that way, and I think it undersells it in an
instructive way.

**The decisions that mattered most were made before anyone asked.**
- Bare metal on a droplet, not on a datacenter machine with a fight over
  its network card.
- Park it when there was no machine, unpark it when there was.
- All at once, no gentle cutover.
- And the doctrines, written long before this project:
  - eliminate a problem rather than paper over it;
  - no regressions;
  - find the structure;
  - independent oracles.

Those shaped every proposal before it reached him, so most proposals
arrived already pointing the right way. Saying yes to them was cheap
because the steering had happened upstream.

**The decisions he did make were one sentence each,** and each unblocked
hours of work:
- case doesn't tell names apart;
- FAT32 before the cutover;
- build the restart, deploy it later;
- re-identify old cookies once;
- strict game limits;
- root is fine;
- keep FAT16, but make it easy to skip.

A yes-man approves whatever is put in front of him. These were judgements
about what mattered, made quickly because the options had been laid out
as decisions rather than as problems. The arrangement worked because the
Claudes did the exploring and framing, and the person did the choosing.

**And twice he declined to decide.** He let the work find its own pace,
and he said a premature push or two "is not the end of the world". That
restraint is a decision too. It is what let the work run unattended
overnight and still be there in the morning, green.

## What it does not mean

**It doesn't mean operating systems are easy.** This one is easy only
because it refused nearly everything an operating system is usually for.
Add HTTPS, more than one request at a time, a second application or real
hardware, and each brings back a piece of the hard part.

**It doesn't mean the work is proven.** It is proven against Linux, on the
questions the judge knows how to ask, under the abuse we thought to
apply. Months of real use will ask questions nobody thought of. The
cutover is the start of that proof, not the end of it.

**It doesn't mean speed was free.** The fastest days were also the days
the box pushed ahead of its gates and launched checks on merges that had
conflicted. Every fix was a rule written down, not more effort. That
seems to be how this kind of work stays honest at this pace: the
discipline has to live in files and scripts, because the pace outruns
anyone's attention.

## What it might mean

**The cost of software has moved.** Writing the code was the cheap part.
Knowing whether it was right (the judge, the oracles, the mutation tests,
the stop-at-every-write test) was where the effort went, and where it
should go. A project that budgets for writing and treats checking as an
afterthought will be fast and wrong. This one budgeted the other way.

**Small, complete things are within reach again.** For a long time "write
your own operating system" meant a decade, or a toy. A server that needs
only what one application uses, checked against a mature system that
already does the job, sits in between: real enough to serve prod's data,
small enough to be understood completely. There are probably many more
things like that than we assume, each waiting on someone willing to say
"no" to most of the problem.

**And the shape of the team matters more than its size.** Two Claudes and
one person, each doing only what it is best placed to do: write, judge,
decide. The second Claude didn't double the speed. It made the speed
safe.
