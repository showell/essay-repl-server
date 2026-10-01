# Our own boot loader

*2026-10-01, gopher-metal `8e44e9b`. Step two of putting Gopher Chat on its own
droplet.*

## What a boot loader is for

When a droplet powers on, its BIOS (the small built-in program every PC
starts with) does one thing to find an operating system: it reads the **first
512 bytes** of the disk into memory and runs them. That's all. Whatever is in
those 512 bytes has to do the rest.

gopher-metal is about 17 MB, so it can't be those 512 bytes. A **boot loader**
is the little program that is: it fits in the first sector, finds the real
kernel elsewhere on the disk, and starts it.

## Why not GRUB after all

In the last essay I said we'd use GRUB, the standard boot loader. Once I looked
closely, writing our own was the better fit, for three reasons:

- **gopher-metal expects to be started a particular way.** It was written for
  QEMU's direct start-up, which hands the kernel a short note: "here's where the
  memory is." GRUB starts kernels a different way, so we'd have had to teach
  gopher-metal a second way to start.
- **We already knew exactly what that start-up does,** because metal-vmm does
  it too. The loader repeats it, from a BIOS instead of from a hypervisor.
- **GRUB is a big dependency,** and installing it onto a disk image needs root
  access on this box. Ours is about 300 lines.

## What the loader does

In plain steps:

1. **The first 512 bytes** print `gopher-metal loader` and read the rest of the
   loader from a little further along the disk. (One sector isn't enough room
   for all of it.)
2. **Read the kernel** from its own section of the disk (a **partition**),
   32 KB at a time. The BIOS can only put what it reads into the first
   megabyte of memory, and the kernel lives above that, so each piece is read
   low and then copied up.
3. **Ask the BIOS where the memory is.** A PC's memory has holes in it (for the
   screen, for the firmware, for devices), and the kernel needs the map.
4. **Write the note** gopher-metal expects, with the map in it, switch the
   processor into the mode the kernel expects, and jump to its first
   instruction.

Every message goes to the serial port *and* the screen, because DigitalOcean's
web console shows only the screen. If something goes wrong on a real droplet,
that's where we'll read about it.

## The disk, laid out

A second small program, `gm-image`, builds the disk:

```
sector 0         the loader's first 512 bytes (plus the partition table's signpost)
sectors 1-33     the partition table: the disk's table of contents
sectors 34-...   the rest of the loader
sector 2048-     partition 2: the kernel
the end          a backup copy of the partition table
```

Partition 1 is deliberately left empty. That's where chat's data will go,
because gopher-metal's disk code mounts the *first* partition it finds, and that
needs to be the data, not the kernel.

## How it was checked

- **Linux's own partition tool** (`sgdisk -v`) reads every disk we build and
  reports "No problems found." That's an outside judge of the table of contents.
- **gopher-metal's memory test** booted through the loader on the droplet-shaped
  machine at three sizes:

  | memory given | memory the kernel found |
  |---|---|
  | 512 MB | 536,312,832 bytes |
  | 2 GB (prod's size) | 2,146,925,568 bytes |
  | 4 GB | 4,294,409,216 bytes |

  Each is the full amount minus about half a megabyte the firmware keeps for
  itself. The 4 GB case matters because that's where the map has a hole in the
  middle and memory beyond it, and the kernel found all of it.
- **gopher-metal's clock test** passed too. It uses the PC's timer chips, which
  a droplet has and our simpler test machine was set up to mimic.

Then I broke the loader on purpose, three ways:

| break | result |
|---|---|
| look for the kernel in the wrong place | fails, and says why on screen |
| skip copying the kernel into memory | fails: the machine never comes back |
| skip clearing the kernel's scratch memory to zero | **still passes** |

The third one is worth being honest about. A brand-new machine's memory is
already all zeros, and gopher-metal is written not to count on that memory being
zero anyway. So nothing can tell whether the loader cleared it. I wrote that down
in the loader itself rather than pretend it's tested.

## What doesn't work yet, as expected

The disk test fails, loudly:

```
FAIL: no virtio-blk device in any mmio slot
```

On our simpler test machine, QEMU puts devices at fixed, known addresses. On a
droplet (and so on our droplet-shaped copy), devices sit on the **PCI bus**, and
the kernel has to ask the bus what's there. That's the next step. It changes
how gopher-metal *finds* its disk and network card, not how it talks to them.
