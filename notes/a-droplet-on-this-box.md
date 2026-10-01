# A droplet, imitated on this box

*2026-10-01, gopher-metal `b932763`. Step one of putting Gopher Chat on its own
droplet.*

## Why imitate one

Every time we try gopher-metal on a real droplet, it costs a few cents and a
slow loop: build a disk, upload it to DigitalOcean, create a droplet, look at
its screen through a web page, delete it. When it fails to start, the droplet
tells us very little.

So the first step is a machine on this box that looks to gopher-metal exactly
like a droplet does. Then all the early mistakes happen here, in seconds, where
we can see the serial port and stop the machine whenever we like. The real
droplet only gets involved once things already work.

## Copying the droplet

This box *is* a droplet, so I asked it what hardware it has. A PC lists its
devices on the **PCI bus**: each device sits in a numbered slot and announces
two numbers, who made it and what it is. This box's list now lives in the repo
as `droplet/lspci.txt`:

| slot | what it is |
|---|---|
| 00.0, 01.0–01.3 | the chipset: Intel's 440FX from 1996, its disk, USB and power-management parts |
| 02.0 | the screen (a virtio graphics card) |
| 03.0 | the network card for the public internet |
| 04.0 | the network card for the private network (where prod's Caddy would reach us) |
| 05.0 | a virtio-SCSI controller: **where extra disks ("volumes") attach** |
| 06.0 | the main disk, which a custom image becomes |
| 07.0 | a tiny disk DigitalOcean uses for setup data (cloud-init's) |
| 08.0 | the memory balloon (lets the hypervisor ask for memory back; we can ignore it) |

`droplet/droplet.sh` starts QEMU with the same chipset, the same BIOS-style
start-up, and the same devices in the same slots, at prod's size: one
processor and 2 GB.

## Checking the copy

A copy can be wrong, so `droplet/shape.sh` checks it two ways:

1. **The slot list.** It asks QEMU for its PCI list and compares it with the
   real droplet's, slot by slot. All 12 match.
2. **Starting from a disk.** A droplet's start-up is old-fashioned: the BIOS
   reads the first 512 bytes of the disk into memory and runs them. So I wrote
   the smallest possible program, those 512 bytes, which prints one line and
   stops:

   ```
   gopher-metal droplet: booted from the disk's first sector
   ```

   It printed that line.

Then I broke each check on purpose, to make sure it can fail. With the USB part
taken out of the copy, the slot check said exactly which slot was missing. With
the disk's "this is bootable" mark removed, the start-up check failed. A check
that can't fail tells you nothing.

## Where the copy differs, on purpose

- **An "exit door."** A test program can end the run by writing to a special
  port. A real droplet has no such door; a write there just goes nowhere.
- **The networks are QEMU's.** Its built-in DHCP server hands out made-up
  addresses. On a real droplet, DigitalOcean's DHCP server hands out the real
  ones.
- **The processor is this box's,** which is itself a droplet's, so that's as
  close as it gets.

## One thing I learned

On a droplet, extra disks ("volumes") don't attach the way the main disk does.
They hang off the SCSI controller in slot 05. That matters for an idea from
earlier: keeping chat's data on a separate volume, so that replacing the main
disk for a deploy doesn't wipe the chat history. gopher-metal can't talk to that
controller yet. It's not needed now, just one more piece if we take that route.

## Next

The 512-byte program proves the start-up path. gopher-metal itself is far bigger
than 512 bytes, so the next step is a **boot loader**: the standard little
program (GRUB) that fits in those first bytes, finds the real kernel on the disk
and starts it. After that, gopher-metal has to find its devices by reading the
PCI list itself, which is what QEMU's simpler test machine always did for it.
