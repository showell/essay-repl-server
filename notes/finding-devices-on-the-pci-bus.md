# Finding the disk and the network card on a droplet

*2026-10-01, gopher-metal `88d14b9`. Step three of putting Gopher Chat on its own
droplet.*

## The problem

gopher-metal talks to two devices that matter: a disk and a network card. Both
are **virtio** devices, a family of simple virtual hardware that hypervisors
offer. gopher-metal already knew how to talk to them. What it didn't know was
how to *find* them on a droplet.

On QEMU's small test machine (`microvm`), finding a device is easy: each one
sits at a fixed, published memory address. gopher-metal just looked at a list
of known addresses.

A droplet is a PC, and a PC does it the old way: devices sit in numbered
**slots on the PCI bus**, and the operating system has to *ask*. Here we are the
operating system, so gopher-metal has to ask.

## How asking works

Two steps, both simple once written down:

1. **Who's in each slot?** You write a slot number to one I/O port and read the
   answer from another. Each device answers with who made it and what it is.
   The virtio devices all say "made by Red Hat" (the company that defined
   virtio) and then which kind: disk, network card, and so on.
2. **Where are its controls?** A virtio device on PCI hands over a short list
   of notes ("capabilities"): *my settings are here*, *my doorbell is here*,
   *my status flag is here*, *my device-specific details (disk size, network
   address) are here*. Each note points into a block of memory the BIOS set
   aside for that device when the machine started.

After that, everything is the same as before. Setting up the queues the disk
and network card use, sending requests, reading replies: none of that
changed. Only the "where are your controls" part differs, so gopher-metal now
has one idea of a device that is either kind, and each low-level operation
("set status", "ring the doorbell") is written once for each.

## Did it work?

On the droplet-shaped machine, through our boot loader:

| test | result |
|---|---|
| disk | found on the bus; read its size and its first sector; wrote a sector and read it back |
| network | found the public card; asked for an address by DHCP and got one |
| random numbers | found no virtio random-number device (a droplet has none), so used the processor's own instruction |
| memory, clock | still pass, with every boot starting on garbage-filled memory (below) |

Both device tests passed on the first try.

## Nothing that worked before broke

The same code still has to work on the old test machine and under metal-vmm,
our hypervisor. The rule is that a machine with a PCI bus is asked through it,
and only a machine without one gets the old fixed-address search. All of these
passed:

- gopher-metal's full probe suite on QEMU's test machine (23 checks);
- the real chat server, judged request by request against the Linux build of
  the same code: every request answered the same;
- metal-vmm's two checks: same output as QEMU, and the same output twice.

One trap was caught before it bit. metal-vmm answers questions about devices it
doesn't have with zeros, while a real PC with an empty slot answers with all
ones. Zeros would have looked like "there is a PCI bus here", and every device
would have gone missing under metal-vmm. Neither all-zeros nor all-ones is a
real maker's number, so both now mean "nobody there".

## Two side discoveries

**Testing with garbage in memory.** You asked whether QEMU can start a machine
without zeroed memory. It can: give it a file to use as memory, filled with a
pattern, and opened so the machine's writes never reach the file. That made the
boot loader's "clear the kernel's scratch memory" step testable at last. Without
that step, the clock test now fails ("the clock claims a rate before anyone
measured one"); with it, the test passes. Every boot in `droplet/boot.sh` now
starts on garbage.

**A test that hadn't been built for two weeks.** One of gopher-metal's
web-server tests (`stdhttp`) stopped compiling on 17 September, when a function
it calls gained a new argument. Nobody noticed, because the test scripts kept
running the copy built before that change. It compiles and passes again.

## What's next

- **DHCP that asks again.** On a real network a lost reply happens. Today
  gopher-metal asks once and waits forever.
- **Text on the screen.** gopher-metal's own messages still go only to the
  serial port. The loader already writes to the screen; the kernel should too,
  or a failure on a real droplet is invisible.
- **Chat's data disk.** On a droplet, extra disks hang off a different
  controller (SCSI), which gopher-metal can't talk to yet. Or chat's data goes
  in a partition of the main disk. That's a decision for later.

After the first two, a real droplet can be tried.
