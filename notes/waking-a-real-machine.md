# Waking a real machine

Thinking out loud about bare metal for gopher-metal: what actually has to be
written, what hardware to aim it at, and the one genuinely hard question, which
is not a driver at all — it is how Caddy on a DigitalOcean droplet reaches a
machine sitting on a private network somewhere else.

## Why KVM on a real box is not worth the trip

Worth saying first, because it clears the ground. Under KVM the processor is
real, but **the devices are still QEMU's**: virtio-blk, virtio-net, the same
MMIO transport we already drive. Everything we would run there is code we
already have, and the one thing it adds — real CPU timing — we already get,
because the soak runs with `-enable-kvm` today.

So the rung is nearly empty. Every unknown worth paying for is in the devices,
and you only meet those by removing the hypervisor.

## The three things, and the two nobody counts

You said CPU, disk, network card, and that is the right list of *devices*. Two
more things sit around them, and in practice they are what the first week is
spent on.

### 0. Firmware has to hand us the machine

PVH is not a firmware protocol — it is how QEMU and Xen start a guest. A real
machine starts through UEFI (or legacy BIOS, on anything old enough not to
want). So we need a new front door:

- **A UEFI application.** Zig targets `x86_64-uefi` directly and produces the
  PE binary firmware expects. We get called with boot services live, ask for
  the memory map, call `ExitBootServices`, and the machine is ours. UEFI also
  hands us two things we would otherwise have to hunt for: the **ACPI RSDP**
  (the root of every table that says where things are) and a **linear
  framebuffer** through GOP.
- **Multiboot2 and GRUB** is the other classic route. Less to write than PE,
  but it puts GRUB in the chain and gives us less than UEFI does.

**I would write the UEFI stub, and keep the PVH entry.** Two entry points over
one kernel: PVH for QEMU, UEFI for hardware. That is not sentiment — it is what
keeps the whole existing judge running at QEMU speed while the metal port is
half-finished. The day we can only test on hardware is the day iteration goes
from seconds to minutes.

Secure Boot has to be off, since nothing we build is signed.

### 0.5. We have to be able to see something

This is the one that bites first and gets left off lists. Today every probe
prints to a 16550 serial port that QEMU always provides. A real machine may
have no serial port at all.

Options, roughly in order of how pleasant they are:

- **A COM header on the board.** Most business small-form-factor desktops
  (OptiPlex, EliteDesk, ThinkCentre) still have one, plus a $6 bracket and a
  USB-to-serial cable at the other end. Our existing `serial.zig` works
  unchanged.
- **A BMC with serial-over-LAN**, on a server board or a rented machine. This
  is the nicest: the console arrives over the network, so the box can live
  anywhere.
- **A PCIe serial card**, if the board has no header. Still a 16550.
- **The framebuffer.** UEFI hands us a linear framebuffer; we already have
  framebuffer code in the family (roc-apps/floor), and a font blitter is an
  afternoon. This is the fallback when there is no serial anywhere, and it is
  also just nice to have — a machine that can say something on a monitor is a
  machine you can debug at the desk.

**Whatever we choose, it is the first milestone.** Everything after it is
debugged through it.

### 1. The processor

We already do most of this: long mode, paging, an identity map of the low 4 GB,
TSC calibration, the CMOS clock. What changes on real hardware:

- **An IDT that actually handles faults.** On QEMU a fault is a mystery; on a
  real machine it is a silent reboot loop. A minimal IDT whose handlers print
  the vector, the error code and RIP to the console is worth more than any
  other 200 lines in this port.
- **Finding the TSC's rate without the PIT.** The PIT is disappearing from
  newer platforms. Modern Intel publishes the ratio in CPUID leaves `0x15` and
  `0x16`; failing that, ACPI's power-management timer or the HPET is a fine
  reference. Our calibration already has the shape — it just needs a second and
  third source.
- **The other cores stay asleep.** UEFI leaves the application processors
  halted, and one core is the machine's design. Nothing to do, which is the
  best kind of item.

### 2. The disk: NVMe, not AHCI

Both are possible; NVMe is the better target and, counter-intuitively, the
smaller one to write.

An NVMe controller is a PCIe device with a handful of registers (capabilities,
configuration, admin queue base addresses, doorbells). You allocate a
submission queue and a completion queue in memory, tell the controller where
they are, issue `Identify`, create one I/O queue pair, and then reads and writes
are 64-byte commands with physical-region pointers. Polled, single-queue, that
is on the order of five hundred lines — and the shape is *the shape we already
have*: a ring you put requests into and poll for completions, exactly like
virtio-blk.

AHCI is not much worse, but SATA is the legacy path on anything new, and its
command layer (FIS types, a command list, a PRDT, port state machines) has more
pieces.

One real trap: **sector size.** FAT16 here assumes 512-byte sectors. Most
consumer NVMe reports a 512-byte logical block (512e) but some are 4Kn. The LBA
format is in `Identify Namespace`, so we read it and refuse loudly rather than
compute the wrong sector.

### 3. The network card: choose the hardware to fit the driver

This is the one place where the right move is to let the software pick the
hardware. There is no generic Ethernet driver — every family is its own
descriptor format and its own bring-up dance. So we pick one, buy it, and
target exactly it.

**Intel's e1000 family is the one to pick**: the 82574L, or the newer i210 /
i211. Reasons: Intel publishes the datasheets, the descriptor model is the
textbook one (a receive ring and a transmit ring, head and tail registers you
poke), polled operation is natural, and a card costs about the price of lunch.
The driver is a few hundred lines and reads like our virtio-net driver with
different structure layouts.

Realtek 8168/8169 is the other common one and is well understood, but the
documentation situation is worse.

**So the shopping list decides the driver, not the other way round**, and I
would rather buy a $30 Intel card than write a driver for whatever happened to
be on the motherboard.

### The piece that is not a device: PCI

Before any of that, we have to find the devices. That means PCI configuration
space: walk buses, read vendor and device IDs and class codes, read the BARs to
learn where each device's registers live, and set the bus-master bit so the
device may do DMA at all.

The legacy port-I/O path (`0xCF8`/`0xCFC`) is about eighty lines and works
everywhere. ECAM through ACPI's MCFG table is the modern way and we can add it
later if something needs extended config space. Since we poll, we need no MSI
or MSI-X, which removes the main reason to want ECAM early.

Two traps worth writing down before they cost a day:

- **BARs above 4 GB.** We identity-map the low 4 GB. A 64-bit BAR can be placed
  higher, and then our map does not cover the registers we just found. Either
  extend the map or reprogram the BAR into low space.
- **The IOMMU.** If firmware leaves DMA remapping enabled, our drivers' DMA
  gets blocked with no explanation. Usually it is left to the OS to turn on,
  but it is the kind of thing that eats an evening.

## The real problem: Caddy is on a droplet and the machine is not

Everything above is work we know how to do. This one is a decision, and it is
the one that decides whether bare metal serves real users or stays a demo.

Today: Caddy on the DigitalOcean droplet terminates TLS and reverse-proxies to
`localhost:9001`. The plan has always been that our machine speaks plain
HTTP/1.1 on a private network with no public address — that is what keeps TLS,
certificates and HTTP/2 out of the project entirely. A bare-metal box in your
house is not on the droplet's private network, and there is no such thing as a
LAN that spans the two.

Five ways out, with what each one costs *our machine*:

**A. The machine learns to tunnel.** WireGuard is the obvious protocol, and
zig's standard library has the primitives (X25519, ChaCha20-Poly1305, BLAKE2s).
But it puts a key exchange, a cipher state machine and a second protocol inside
the thing whose whole virtue is being small enough to judge. **I would not do
this**, at least not first.

**B. A helper on the same LAN owns the tunnel.** A Raspberry Pi, an old box, or
your router if it runs OpenWRT: it holds the WireGuard link to the droplet, and
Caddy proxies to an address that the helper forwards onto the LAN. Our machine
sees an ordinary Ethernet segment and needs nothing new at all. Cheap, boring,
standard — and it keeps every line of crypto out of the kernel we are judging.

**C. Move Caddy to the LAN.** Then the topology is exactly the one the plan
describes — Caddy and gopher on one private network — and the droplet leaves
the path. The cost is that the public front door becomes your house: a static
address or dynamic DNS, ports open, and residential uptime underneath chat.

**D. Rent bare metal in a datacenter.** Providers sell real machines with real
private networking, so "Caddy on one host, gopher on another, private network
between them" becomes literally true with no tunnel anywhere. This is the
grown-up answer and the one that could carry real traffic.

The catch is that **we no longer choose the NIC**, which undoes the neat trick
of picking hardware to fit the driver. Before buying anything we would have to
know exactly which controller is in the machine, and take a plan where it is an
Intel part we have a driver for. Some providers also give an out-of-band serial
console over the network, which would solve the "how do we see anything"
problem beautifully — worth confirming per provider rather than assuming.

**E. Do not connect it to production at all, yet.** Boot the box on your LAN,
point a browser at it, and run the judge from a laptop on the same network. The
judge speaks HTTP over a socket; it needs an address instead of a QEMU port and
nothing else.

**And that last one is the sequencing insight I did not expect when I started
writing this.** The topology problem does not block the first bare-metal
milestone — it only blocks putting real users behind it. "Chat, served from a
machine with no operating system, to a browser on the LAN" needs no tunnel, no
Caddy, no DNS and no decision about any of the above. We can have that, and
then argue about topology with a working machine in the room.

## Keeping the loop fast, which is the thing I would get wrong

Today's whole way of working depends on a rebuild-and-boot cycle measured in
seconds. Real hardware POSTs for thirty seconds before it even reaches our
code. If the metal path becomes the way we test, iteration dies.

So:

- **QEMU stays the correctness loop.** Every existing gate keeps running there,
  against the PVH entry, at the speed it runs today.
- **Metal answers only what metal can answer**: does the NIC link up, does DMA
  work, what does a real disk cost, does the clock hold.
- **Netboot rather than a USB stick.** Firmware that can HTTP-boot, or iPXE
  chainloading our EFI binary, turns "flash a stick, walk to the machine" into
  "copy a file and power-cycle". Worth setting up on day one; it is the
  difference between a five-minute cycle and a forty-second one.
- **The probe pattern carries over.** This repo already grows one kernel per
  driver — `block`, `net`, `rng`, `clock`. Metal gets the same ladder, and each
  rung is a real milestone: print something; read the memory map; list the PCI
  devices (which also tells us what we bought); identify the NVMe and read
  sector zero's boot signature; bring the link up and answer one ARP; DHCP;
  then the whole server.

## What I would buy

For a machine at home, aimed squarely at the drivers we want to write:

- **A fanless mini-PC with Intel i210/i211 NICs and a COM header** — the sort
  of box sold for OPNsense firewalls. Known NIC, real serial console, low power,
  and it can live next to the router where the LAN story is simplest.
- Or **a used business SFF desktop** ($50-100) plus an **Intel i210-T1 or
  82574L PCIe card** ($25-40) plus a serial bracket and a USB-to-serial cable.
- An NVMe SSD, any size. The volume we need is measured in megabytes.

Either way the rule is the same: **buy the NIC we intend to write a driver
for**, and check for a serial console before checking anything else.

## The questions I would want answered before writing code

1. **Where does this box live** — your desk, next to the router, or a
   datacenter? It decides the console story and the topology story together.
2. **Is the first milestone "a browser on the LAN"?** I think it should be, and
   it lets every topology question wait.
3. **How much do we care about it carrying real chat traffic**, versus being
   the thing that proves the machine is real? If the answer is "eventually,
   seriously", option D starts looking better than B, and the NIC question
   needs settling before any hardware is bought.
4. **Serial or framebuffer first?** Serial is less work and remote-friendly;
   the framebuffer is more work and more satisfying, and we have prior art.


---

# Iteration 2: "why doesn't someone just rent me the hardware?"

They do — that is a real product category, not a gap. But the market is
smaller and stranger than you would expect, and looking at it properly changed
what I would recommend.

## The flagship just died

**Equinix Metal — the best-known bare-metal cloud, and the one I was going to
recommend — is gone.** Announced as sunsetting, stopped selling, switched off
on 30 June 2026, support retired at the end of September, console access
lingering to the end of the year. Anything still provisioned after the sunset
was deleted.

That is worth more than a correction to my shopping list. The company that owns
the datacenters, whose whole business is floor space and interconnection,
could not make renting bare machines pay. Which is most of the answer to your
question.

## Why it is a thin market

Every property that makes a VM cheap to sell is a property bare metal lacks:

- **Utilization.** One physical box can carry many tenants as VMs. Rented
  whole, it earns one rent, and it earns nothing at all while it sits between
  customers.
- **Provisioning time.** A VM appears in seconds. A real machine has to be
  wiped, re-imaged and POSTed — minutes, sometimes tens of minutes — and that
  is dead time the provider eats.
- **Firmware persistence.** This is the deep one. A tenant with real hardware
  can write to the BIOS, the BMC, the NIC's option ROM, the drive's firmware —
  and those survive a reinstall. To rent the same box to someone else safely, a
  provider must re-flash everything it cannot verify, which is slow, risky, and
  occasionally bricks a machine. AWS's Nitro cards exist in large part to move
  the trust boundary off the motherboard for exactly this reason.
- **None of the cloud's operational tricks work.** No live migration, no
  snapshot, no resize, no moving you off failing hardware. A dead disk is a
  support ticket, not an automatic reschedule.

So bare metal is a specialty product with worse margins, sold mostly to people
who need it for licensing, latency or compliance — and one of the biggest
sellers just concluded it was not worth doing.

## What is actually awkward for us, which is not what I expected

I assumed the hard part would be getting permission to boot our own code. It is
not; several providers support custom netboot or a rescue environment you can
write an image from. **The hard part is the network card.**

A datacenter machine has a datacenter NIC: dual 10 or 25 gigabit, Mellanox or
Intel's X710/E810 family. Those are serious devices — descriptor formats built
for offload, queues built for many cores — and writing one from scratch is not
the few-hundred-line afternoon that an Intel i210 is. Renting hardware means
taking the NIC that comes with it, which throws away the one move that made
this tractable: *choose the hardware to fit the driver.*

The other two are fine. Storage is standard NVMe nearly everywhere, which is
the driver I would write by choice. Consoles vary from excellent
(serial-over-SSH, IPMI) to awkward (a KVM-over-IP unit a technician physically
attaches on request).

## The one that looks right anyway

**Hetzner's dedicated line** comes out well, for an unglamorous reason: their
cheaper machines are built from consumer parts, so the onboard NIC is an Intel
PCH part — the interface name in their own documentation is the giveaway — and
that is the **e1000e family**, the same lineage as the i210 I wanted to buy. A
driver written for it is the driver we were going to write anyway.

The rest of the picture:

- **Getting our code on it:** their rescue system is a PXE-booted Linux that
  runs in RAM without touching the disks. From inside it we can write our EFI
  binary to the machine's boot partition and reboot. Not as slick as handing a
  provider an iPXE URL, but it is a two-minute loop and it cannot brick us —
  rescue always comes back.
- **Seeing what happens:** no permanent serial console on the cheap lines. A
  KVM-over-IP unit can be requested, and because it captures video rather than
  serial, **our UEFI framebuffer console would be visible through it**. That
  moves the framebuffer from "nice to have" to "the thing that makes a rented
  machine debuggable."
- **The private network:** their vSwitch is a real layer-2 VLAN between your
  own machines. Which leads to the part I like.

## The topology that falls out

If the box is in a datacenter that also sells ordinary VMs, the architecture we
designed becomes *physically true*:

```
the internet → Caddy (a small VM) ──private VLAN── gopher-metal (a real machine)
```

Both in the same facility, connected by a layer-2 network that is actually
private, with no tunnel, no crypto in our kernel, and no residential uplink
under chat. The DigitalOcean droplet stops being in the path for chat at all —
DNS points at the new front door.

The cost to us is one small thing: a vSwitch is **802.1Q tagged**, so frames
carry a four-byte VLAN tag between the MAC addresses and the ethertype. That is
perhaps twenty lines in the frame parser and the frame writer, and it is a fact
about a private network we would meet in any datacenter.

## So the three options, honestly ranked

1. **A box at home, first.** Still where I would start, and nothing above
   changes that: we choose the NIC, we have a serial cable, the machine is on
   the desk when it does not boot, and the first milestone — chat served from
   bare metal to a browser on the LAN — needs no provider at all.
2. **A rented dedicated machine, once it works.** Consumer-grade hardware on
   purpose, for the NIC. This is what carries real traffic, with Caddy moved
   onto a VM beside it and the droplet out of the path.
3. **Bare metal from a hyperscaler.** Hourly billing makes an experiment cheap
   and the consoles are good, but the network device is theirs — Amazon's is
   ENA, which is documented but is a second driver we do not need to write.

I would do 1 and 2, and in that order, because the whole cost of 2 is a NIC
driver that 1 lets us write against hardware we picked and can power-cycle by
hand.
