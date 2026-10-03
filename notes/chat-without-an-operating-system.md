# Chat without an operating system

*2026-10-03. An open-ended look at gopher-metal: what it is, what it has
taught us, and what it might be for.*

## What it is

Lyn Rummy's chat server, angry-gopher, is about fourteen thousand lines of
zig. On lynrummy.com it runs the way almost every server in the world runs:
as a program on Linux, which handles the network card, the disk, the
clock, memory, and everything else between the program and the machine.

gopher-metal runs the same program with no Linux at all. The droplet boots
our own loader, which starts our own small kernel. The kernel finds the
network cards and disks on the PCI bus, speaks TCP, keeps a FAT file system,
reads the clock, and hands requests to the unchanged chat code. That's the
whole machine: one program, nothing under it but what we wrote.

It began on 2026-09-16 as a side branch of a Roc experiment. It was parked
two days later with everything green, because there was no machine to run
it on. It was unparked on 2026-10-01, when a DigitalOcean droplet turned
out to be such a machine. By that evening, chat ran on a real droplet. Two
days later it has been rehearsed against a copy of prod's real data, on
FAT32, with every one of 1,084 compared pages identical to Linux's.

## Why anyone would do this

It's a fair question, and the honest answer has several layers.

**The one we said first was speed.** It's real, but it turned out to be
the least interesting. Metal is within about a tenth of a millisecond of
Linux on pages that need no file, and about a millisecond behind on pages
read from disk. Through Caddy, over the internet, nobody can feel either.

**The one that turned out to matter is understanding.** When you own
every layer, nothing is someone else's problem. We know exactly what
happens when a disk write is cut off halfway, because we made it happen
on purpose and looked at the bytes. We know exactly what a request costs,
because nothing is hidden in a kernel we didn't write. That kind of
knowledge is rare, and it compounds.

**The one nobody planned is that it made the Linux application better.**
Every time metal disagreed with Linux, someone had to find out which was
wrong, and Linux was not always the right one. The list of bugs found in
angry-gopher itself is long, and some were serious:
- a request that deleted any member's game history;
- a guest account anyone could take over;
- game sessions that dropped lines under concurrent writes;
- a disk that a stranger could fill in fifteen seconds.

None of them had anything to do with bare metal. They were found because
the metal project forced the application to be read carefully, by someone
looking for trouble.

**The last is the far one:** a web server in a box. If an application only
ever talks to the world through a narrow seam (requests, a file store, a
message bus), then the floor under it is replaceable, and Linux is one
floor among others. The essay about that is
`notes/a-web-server-in-a-box.md`. It's still mostly an idea, but the Store
was a real step toward it.

## The judge is the whole method

If one thing explains how the project moved this fast without falling
over, it's the judge. Every change runs the same requests against the same
data on Linux and on metal, and requires the same answers. There's no
specification to argue about; Linux is the specification, in practice.

That turns a vague question ("is metal correct?") into thousands of small,
mechanical ones ("did this page come back byte for byte the same?"). It
also cuts both ways. When the answers differ, sometimes metal is wrong,
and sometimes Linux is doing something nobody meant.

The judge's quiet strength is that it has more than one opinion to
consult:
- the Python FAT reader, written from the specification and not from our
  code;
- mtools;
- Linux's own vfat driver;
- fsck.

None of them is better than our code. Each is wrong in different ways, and
when three of them agree against ours, ours is almost always the one at
fault. This was the project's best habit: never let anything grade its
own homework.

## What it costs

It would be dishonest to skip this.

**Everything Linux does for free, we do by hand.** A slow disk, a
flaky clock chip, a directory with more than 256 entries, a connection
that never finishes: each was a stop-the-machine bug at some point, and
each was found by looking, not by luck. CC's audit of "fixed sizes against
data that grows" exists because the 256-entry one was found in production
code, not in a test.

**Some things we haven't done, and may never.** Metal has no HTTPS, so
Caddy on prod still handles that, and so a Linux machine still sits in
front. It has no shell, so administration is web routes: a backup to
download, a secret to rotate, a status page. It serves one request at a
time, which is fine for chat's traffic and would not be for many other
sites.

**And the gates take real time.** A full check of a change is now 18
minutes, down from 30. That's the price of comparing two machines on
every story.

## How it was built

The last two days were also an experiment in how work gets done.

A cloud Claude worked unattended, writing code, tests and adversarial
reviews from a queue in a file. A Claude on the box ran the slow and
privileged checks, merged what passed, and kept the queue full. Steve made
the decisions, almost always in a single sentence:
- case doesn't tell names apart;
- FAT32 before the cutover;
- build the restart, deploy it later;
- re-identify old cookies once;
- strict game limits;
- root is fine.

Each sentence unblocked hours of work.

What worked was not speed but division. The writer was never the judge
of its own work, and the judge was never asked to write. The weak point
was the box's discipline under pace: pushes ahead of their gates, merges
that launched the gates even when they conflicted. Those were fixed by
writing rules down, not by trying harder. That seems to be a general
lesson.

## Where it stands

- **Live:** metal.lynrummy.com, with test data, through prod's Caddy.
- **Rehearsed:** the move of prod's real data, on FAT16 and FAT32, with
  the same answers as Linux, read-only and after writes.
- **Ready:** a runbook with go/no-go lines, a way back, a backup, a secret
  rotation, a watchdog.
- **Waiting on a real droplet:** whether a reset restarts the machine or
  powers it off. Until that's known, a crash halts with its log on the
  screen, and someone has to turn the machine back on.
- **Not decided:** when.

## Open questions

**Is the cutover worth doing, or is the rehearsal the real result?** The
project has already paid for itself in bugs found and understanding
gained. Moving prod adds risk for a speed nobody can feel. On the other
hand, a system that is only ever rehearsed is never quite real, and
running chat on metal is the only way to learn what months of real use
teach.

**What is the second application?** A floor with one tenant is a port. A
floor with two is a platform. Lyn Rummy already runs there, but it was
born in the same codebase. Something written fresh against the seam, in
zig or Roc, would be the real test of the "web server in a box" idea.

**How much of Linux do we actually want back?** HTTPS, more than one
request at a time, a way in when the web routes are down. Each would make
metal more capable and less small. The project's character so far has
come from being small enough to understand completely. That is worth
protecting, even at some cost in features.

**What does it mean that an operating system's worth of work took about
three weeks?** Not that operating systems are easy. Rather, a server
needs very little of one, and a careful judge plus independent oracles can
carry a small team a long way, most of it unattended. That may be the most
transferable thing here.
