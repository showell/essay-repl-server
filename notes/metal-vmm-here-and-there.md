# "Here" and "under QEMU": why the disk tests run slower on our machine

*2026-10-01, metal-vmm, the first thing after unparking it*

## The cast

There are three programs in this story.

- **The guest.** A tiny program from gopher-metal that believes it owns a whole
  computer. It has no operating system under it. It talks straight to a disk, a
  network card, a clock and a serial port (the line it prints text on). The
  `vfat` guest, for example, writes five files to a disk and reads them back.
- **metal-vmm.** Our program. Its job is to *be* that computer: when the guest
  reads the disk, metal-vmm answers; when it asks the time, metal-vmm answers.
  **When `check.sh` says "here", it means "the guest running on metal-vmm".**
- **QEMU.** A widely used program that does the same job as metal-vmm, built by
  many people over many years. We run every guest on it too and require the
  same printed words, which is how we know metal-vmm answers correctly. It's the
  reference.

So `4192 ms here, 2071 ms under QEMU` means: the same guest, doing the same
work, took 4.2 seconds on our computer-imitation and 2.1 on QEMU's.

## How a guest runs on metal-vmm

Imitating a computer instruction by instruction would be slow, so metal-vmm
doesn't. It uses a feature of the processor itself, reached through Linux's
**KVM**: the guest's instructions run *directly on the real processor*, at full
speed.

The exception is anything that touches a device. When the guest reads the disk
or asks the time, the processor stops it and hands control to metal-vmm. That
stop is called an **exit**. metal-vmm works out the answer, puts it where the
guest expects it, and lets the guest continue.

Think of a worker at a desk who does their own work quickly, but has to walk
down the hall to a manager's office for every supply. Work is fast and supplies
are slow.

## How a guest ran on QEMU in `check.sh`

This was the surprise. `check.sh` starts QEMU **without** telling it to use KVM,
so QEMU uses its fallback: a **software processor**. It reads each of the
guest's instructions and imitates it. No real processor runs the guest's code.

In the worker picture, the worker and the manager are now the same slow,
careful person. Every piece of work takes longer, but fetching a supply is just
reaching into a drawer, with no walk down the hall.

So the two timings were never measuring the same thing:

| | ordinary work | each device access |
|---|---|---|
| metal-vmm ("here") | real processor speed | an exit: slow |
| QEMU in `check.sh` | imitated in software: slow | a function call: fast |

That explains the whole pattern:

- **`clock`** is mostly ordinary work. 1.2 s here, 8.3 s under QEMU.
- **`vfat`** is almost entirely device access. 4.2 s here, about 2 s under QEMU.

## Why `vfat` is nearly all device access

I traced its disk requests. The guest asks for one 512-byte piece of the disk (a
**sector**) at a time:

- **44,193 requests**, but only **34 different sectors** among them.
- About twenty of those sectors were each read **about 2,300 times**. They hold
  the disk's table of contents (the FAT: which parts of the disk belong to which
  file).

The guest keeps no copy of what it has already read, so it goes back to the disk
for the table of contents again and again. That costs about 221,000 exits in
total. QEMU, with its software processor, pays the same requests at
fetching-from-a-drawer prices.

There's one more twist. **This box is itself a virtual machine**: DigitalOcean
runs it on their own hypervisor. So each exit is a trip through two layers of
hypervisor, not one, which makes the walk down the hall longer than it would be
on a real computer. Here it averages about 19 microseconds per exit, everything
included.

## The fair comparison

Once I knew the cause, I ran QEMU the other way too, with KVM, the way
metal-vmm works. Two rounds, interleaved:

| | `vfat` | `clock` |
|---|---|---|
| QEMU, software processor (what `check.sh` does) | 1.7 – 2.0 s | 8.2 – 8.3 s |
| QEMU, with KVM | 3.3 – 3.4 s | 4.6 s |
| metal-vmm | 4.15 s | 1.23 s |

With both on KVM, metal-vmm's `vfat` is about 25% slower, not 2× slower. I have
a likely reason for that gap but haven't measured it directly. Of metal-vmm's
221,000 exits, **88,000 are the guest asking the time**. metal-vmm makes every
clock read an exit on purpose: that's how it owns time, so a run repeats exactly.
QEMU with KVM lets the guest read the real processor's clock without stopping.
88,000 walks down the hall at roughly 19 µs each come to about 1.7 seconds,
more than the whole gap.

(`clock` is slower under QEMU-with-KVM for a different reason: that guest waits
for real seconds to tick by, and only metal-vmm's seconds are its own.)

## A note on noise

You mentioned this box usually shows about 15% randomness in timings. metal-vmm's
`vfat` runs came in at 4151, 4156 and 4192 ms, within 1%. That's
because the guest does *exactly* the same thing every time on metal-vmm, down to
the number of exits, which is the point of the project. QEMU's runs of the same
guest ranged from 1.7 to 2.1 seconds.

## What I changed

- `check.sh` now says `under QEMU, software CPU`, with a comment explaining what
  that means for the timings.
- The README had a wrong explanation: it said QEMU "has spent years not doing"
  exits, as though the same kind of machine were simply better tuned. It now
  gives the reason above, with these measurements.
- My first edit to `check.sh` put an apostrophe inside a quoted string and broke
  the script, and I pushed it before running it. It was fixed in the next commit,
  and `check.sh` is green again (9 of 9).

## What this does *not* say

Nothing here is a bug in metal-vmm. All nine guests still give the same answers
as QEMU and repeat themselves exactly. The slowness is the price of two things
we chose: owning every clock read, and running on a rented virtual machine.

One thing about the *guest* stands out: re-reading the same twenty sectors
2,300 times each. That lives in gopher-metal's disk code, not here. A real disk
would make it very slow, and it would be cheap to fix. It's worth knowing about,
not urgent.
