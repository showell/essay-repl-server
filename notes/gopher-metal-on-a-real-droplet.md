# gopher-metal, on a real droplet

*2026-10-01. The first time gopher-metal has run anywhere but an emulator on
this box.*

```
$ curl http://162.243.30.235/from-the-ladder-box-1
hello from no Linux, on the public card, request 1
```

That answer came from a DigitalOcean droplet in nyc2 with **no operating
system**: no Linux, no hypervisor of ours, just gopher-metal, booted by our own
boot loader from the droplet's disk, finding its network cards on the PCI bus,
getting its address from DigitalOcean by DHCP, and answering over TCP. Twenty
more requests, all answered correctly, averaging 13.5 ms each from this box.

## Getting there took one detour

### The symptom

The first droplet made from our image showed the BIOS's banner, then
`Booting from Hard Disk...`, and then nothing. Not even the first line our boot
loader prints.

### Ruling things out

- **Is it the BIOS?** The droplet's screen named its BIOS (SeaBIOS 1.15.0-1,
  which is exactly Ubuntu 22.04's build) and its machine type (QEMU's
  `pc-i440fx-6.1`). I fetched that very BIOS, booted our image on that very
  machine type here, and it ran perfectly, all the way to answering requests.
  So not the BIOS.
- **Is it the serial port hanging?** Our loader waited, with no limit, for the
  serial port to be ready before printing anything, and on a droplet nobody
  reads the serial port. I measured this box's own serial port (it's a droplet
  too) and it was always ready. Even so, the loader now writes to the screen
  first and gives up on a stuck serial port. And the loader now puts a green
  letter in the screen's top-right corner as its very first act, with nothing
  in between that could hang.
- **Is it the compression?** You suspected the `.gz`. We tried the
  uncompressed image too. Same result.

The green letter never appeared. So our first instruction never ran.

### What was actually on the disk

DigitalOcean can boot a droplet into a rescue system with its disk attached, and
SSH in. Comparing the disk with our image, piece by piece:

- The disk's first sector, the one the BIOS runs, was **not ours**. It was
  DigitalOcean's: a partition table, a valid "bootable" mark, and **446 bytes
  of zeros** where the boot code goes.
- **Our whole image was there, intact, starting one megabyte in**, inside a
  partition DigitalOcean had created to hold it.

DigitalOcean's import had decided our image wasn't a whole disk but a single
filesystem, made a fresh disk, and put our image *inside* it. The BIOS jumped
into zeros, and the processor ran nothing useful forever.

My best guess at why: our disk's table of contents deliberately leaves
**partition 1 empty** (reserved for chat's data) and puts the kernel in
partition 2. A tool that looks for "partition 1", finds nothing, and concludes
"this is a bare filesystem, not a disk" would do exactly this. That's an
inference about their code, not something I've seen in it.

### Getting past it

From the rescue system, I copied our image straight onto the droplet's disk,
checked that the four key pieces now matched ours exactly, and you switched the
droplet back to booting from its disk. It came up, printed both network
addresses on the screen, and answered.

## What this proves, and what it doesn't

**Proven on real DigitalOcean hardware:**
- our boot loader starts from DigitalOcean's BIOS;
- gopher-metal finds the disk and network cards on the PCI bus;
- DigitalOcean's DHCP gives it its real public address;
- its TCP talks to the real internet.

**Not yet:**
- **the private network** (where prod's Caddy would reach it): it got an
  address there too, but nothing has asked it anything over it yet;
- **DigitalOcean's import**: for now our image only works when copied onto the
  disk by hand. The fix is to put the kernel in partition 1 and have gopher-metal
  find chat's data partition by its *type* rather than its position, which is
  the better design anyway, then re-import to see it accepted as it is;
- **chat itself**: this is `hello`, a 150-line kernel. The real server needs a
  data partition, which is next after the import fix;
- **speed**: 3 to 25 ms per request from this box. The spread is probably our
  own logging: once the screen fills up, every logged request moves all 25 rows
  of screen memory, which is slow on a virtual machine. Not measured yet.
