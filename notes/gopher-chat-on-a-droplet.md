# Renting something closer to the metal: what DigitalOcean actually offers

*2026-10-01: gopher-metal and metal-vmm, unparked. The question: what can we rent
from DigitalOcean that runs Gopher Chat closer to the metal, at least as fast as
lynrummy.com?*

## The short answer

**DigitalOcean doesn't rent ordinary bare-metal servers.** Its only bare-metal
product is eight-GPU AI machines, sold by contract through its sales team. Every
other machine it sells is a **droplet**, which is a virtual machine.

But there's a way to get much closer to the metal than we are today, at the same
price as prod: **make gopher-metal the droplet's operating system.** No Linux,
no hypervisor of ours, nothing between chat and DigitalOcean's own virtual
hardware. DigitalOcean calls this a **custom image**: you upload a disk, and a
droplet boots from it.

## Where things stand today, in layers

Today chat runs on prod as an ordinary Linux program:

```
lynrummy.com today:     DigitalOcean's hypervisor → Linux → chat
gopher-metal so far:    DigitalOcean's hypervisor → Linux (this box) → QEMU → gopher-metal → chat
the proposal:           DigitalOcean's hypervisor → gopher-metal → chat
```

The middle line is how we tested gopher-metal: on this box, inside QEMU. The
bottom line has *fewer* layers than prod does today.

**What it still isn't:** a machine with nothing under it. DigitalOcean's
hypervisor is still there, and the devices gopher-metal talks to are still
virtual ones. When you parked this in September, you said plain KVM on a rented
box wasn't worth it, because the devices would still be QEMU's and nothing new
would be exercised. That objection partly applies here, so here's what this
would and wouldn't test:

| | new? |
|---|---|
| how the virtual disk and network card behave | **no**: almost certainly the same QEMU code we test against |
| how the machine starts (an old-style PC BIOS reading a disk) | **yes** |
| how gopher-metal *finds* its devices (the PCI bus) | **yes** |
| a real network: DigitalOcean's DHCP server, real latency, real clients | **yes** |
| real users, through Caddy, on hardware we pay for | **yes** |

## What a droplet looks like from the inside

This box is a droplet, so I looked. It presents itself as an ordinary PC:

- **A BIOS**, made by "DigitalOcean", version 20171212. Custom images must boot
  that way; the newer UEFI start-up isn't supported.
- **A PCI bus**, the standard way a PC lists its devices, with two virtio
  network cards (public and private) and virtio disks. Virtio is the same
  family of virtual devices gopher-metal already drives. They're the modern
  (version 1.0) kind, which is the kind gopher-metal speaks.
- **A serial port.** (DigitalOcean's web console shows the screen, not the
  serial port, which matters below.)

DigitalOcean's documentation says custom images must contain Linux tooling
(`cloud-init`, `sshd`, an ext4 filesystem). Those are what *its* conveniences
need: setting passwords, adding SSH keys, resizing the disk. DigitalOcean can't
check what's inside the disk you hand it. The Unikraft project, which builds tiny
single-purpose kernels like gopher-metal, publishes a tool that deploys them to
DigitalOcean this way. Two things the docs say do matter:

- **Droplets from custom images get their address by DHCP.** gopher-metal already
  does DHCP; it's how it gets an address from QEMU today.
- **No IPv6** for custom-image droplets. Chat sits behind Caddy, so it doesn't
  need it.

## What gopher-metal is missing

Each of these is small, and each can be built and tested **on this box, for
free**: QEMU can be set up to look exactly like a droplet (the same PC chipset,
the same BIOS, devices on PCI).

1. **Starting from a disk through the BIOS.** Today QEMU loads gopher-metal
   straight into memory. A droplet reads the first sector of the disk and runs
   whatever is there. That needs a boot loader (GRUB is the standard one) and a
   matching entry point in gopher-metal.
2. **Finding devices on the PCI bus.** Today QEMU tells gopher-metal where its
   devices are. On a PC it asks the bus. This changes *where* each device's
   controls are, not how the devices work, so the disk, network, TCP and FAT16
   code above it doesn't change.
3. **DHCP that asks again.** metal-vmm found in September that gopher-metal asks
   for an address once and waits forever if the answer is lost. On a real
   network that has to be fixed.
4. **Something on the screen.** DigitalOcean's recovery console shows the
   screen, not the serial port gopher-metal prints to. It needs to write its
   messages to the screen as well, or a droplet that fails to start shows
   nothing at all.

Then a first real boot on the cheapest droplet ($4–6 a month, billed by the
hour, deleted afterwards): does it start, get an address, and answer a request?

## Performance compared with prod

**Is it faster?** Probably, since one whole layer (Linux) is gone. But we've only
measured gopher-metal inside QEMU on this box, so we don't know.

**"At least comparable to lynrummy.com"** comes down to buying the same size of
droplet as prod, or a bigger one. Your options at DigitalOcean (prices from its
pricing page today):

| kind | example | price/month | processor |
|---|---|---|---|
| Basic | 1 vCPU, 1 GB | $6 | shared with other customers |
| Basic | 1 vCPU, 2 GB | $12 | shared |
| CPU-Optimized | 2 vCPU, 4 GB | $42 | **dedicated** |
| General Purpose | 2 vCPU, 8 GB | $63 | **dedicated** |

"Dedicated" means the processor cores are yours alone, so no other customer's
work slows yours. That's the step closest to the metal that DigitalOcean sells.
I couldn't look up which plan prod is on (I'm not allowed to read prod), so
that's the first question for you.

One more thing in our favour: a droplet also gets a **private network address**
(this box has one), and a gopher-metal droplet in the same region as prod could
take requests from prod's Caddy over that private network. That's the setup the
gopher-metal plan always assumed: Caddy keeps the certificates and the encryption,
and chat speaks plain HTTP behind it.

## What I'd suggest

Build the four missing pieces against a droplet-shaped QEMU here, for free. Then
spend a few cents on one real boot. Only after it starts, gets an address and
answers a request do we pick a droplet size and point Caddy at it.
