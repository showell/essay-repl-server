# Asking again, and writing on the screen

*2026-10-01, gopher-metal. The last two pieces before a real droplet.*

## Part 1: DHCP that asks again

### What DHCP is

When a machine starts on a network, it doesn't know its own address. It
shouts "does anyone have an address for me?" (**DHCP**), a server answers with
an offer, the machine says "yes, I'll take that one", and the server confirms.
Two messages out, two back.

### What was wrong

gopher-metal sent each message **once**, then watched for the answer for a
fixed number of loop turns. If either message, or either answer, was lost on
the way, it never asked again: it gave up and stopped. A machine that loses
one packet at start-up would never get an address, so it would never serve
anything. On QEMU's private test network
packets are never lost, so nobody noticed. metal-vmm, which can lose a chosen
packet on purpose, found it in September.

### The fix

The standard rule (from the DHCP specification): wait about **4 seconds** for an
answer; if none comes, ask again and wait **8**, then 16, 32, and 64 seconds.
Each wait is nudged by up to a second either way at random, so that many
machines that lost the same packet don't all ask again at the same instant.
After six tries (a little over three minutes) it gives up and says so loudly.

The waits are real measured time now, using the machine's clock, not "some
number of loop turns", which takes a different amount of time on every
processor.

### Checked by losing packets on purpose

metal-vmm can throw away the machine's *n*th outgoing packet. Here's each case,
before and after. The times are the machine's own clock:

| packet lost | before | after |
|---|---|---|
| none | gets an address | gets an address |
| the first "address, please?" | **gives up, no address** | asks again, gets one (3.2 s) |
| the "yes, I'll take it" | **gives up, no address** | asks again, gets one (3.5 s) |
| both of those | (not run: losing the first is already fatal) | asks again twice, gets one (10.6 s) |
| every packet, forever | (not run: losing the first alone gave up after 0.03 s) | tries six times over 184 s, then gives up with a clear message |

## Part 2: writing on the screen

On a real droplet nobody can read the serial port, where gopher-metal has
always printed everything. DigitalOcean's web console shows the **screen**.
So now everything gopher-metal prints goes to both.

A PC's screen, at start-up, is a grid of 80 columns by 25 rows of text, and
the grid lives at a fixed place in memory: write a letter there and it
appears. gopher-metal carries on from where the BIOS and our boot loader left
the cursor, and scrolls when it reaches the bottom.

One safety rule: on machines that have no screen (QEMU's small test machine,
metal-vmm), that same place in memory might be ordinary memory in use for
something else. So gopher-metal only writes there when the PCI bus lists a
display, which a droplet's does.

### How it was checked

A new script boots a test on the droplet-shaped machine with no "exit door",
just as on a real droplet, so the machine stops with its screen intact. Then
it copies the screen's memory out and checks that every line gopher-metal
printed to the serial port is on the screen, in order. Here's the screen, as
the web console would show it:

```
iPXE (https://ipxe.org) 00:04.0 CB00 PCI2.10 PnP PMM 7EFCACF0 7EF0ACF0 CB00
Booting from Hard Disk...
gopher-metal loader
  reading the kernel
  kernel in memory
  starting it
gopher-metal memory probe
  memmap entries 7
  total ram 2146925568
  ...
  the heap is empty again, and std's allocator finds no leak
PASS
```

(The first two lines are the BIOS's own.) With the screen-writing line taken
out of gopher-metal on purpose, the check fails. Scrolling is tested
separately, by printing 30 lines into a 25-line screen.

## Part 3: ready for a real droplet

### What your new droplet told us

The droplet you rented (`107.170.90.53`, Ubuntu, nyc2) has exactly the same
devices in exactly the same slots as the one I copied, and its BIOS gives away
its machine type: `pc-i440fx-6.1`, which is QEMU's name for this kind of PC. So
DigitalOcean runs droplets on QEMU too.

I also asked DigitalOcean's network for an address the way gopher-metal would
(with a tool that asks but changes nothing). **No answer, on either card.** An
ordinary droplet like yours doesn't use DHCP. Its addresses are written into
its settings when it's created. DigitalOcean's documentation says DHCP is
served only to droplets made from a **custom image**. So gopher-metal has to go
up as a custom image, not be copied onto your Ubuntu droplet. Your Ubuntu droplet
then has a better job: it's a machine in the same region and on the same
private network, so it can test the gopher-metal droplet the way prod's Caddy
eventually will.

### The kernel that goes up first

A small one, `hello`: it gets an address on both network cards, puts them on
the screen, and answers every web request forever:

```
hello from no Linux, on the private card, request 4
```

On the droplet-shaped machine here, all six test requests (three per card) got
exactly the right answer, and the screen logged each one:

```
gopher-metal, on a droplet, with no Linux
  public card: 10.0.2.15 (mask 255.255.255.0, router 10.0.2.2)
  private card: 10.116.2.15 (mask 255.255.240.0, router 10.116.2.2)
  listening on port 80
  request 1 on the public card: GET /round1 HTTP/1.1
  request 2 on the private card: GET /round1 HTTP/1.1
  ...
```

The whole disk is 3 MB (37 KB compressed). Once it's a droplet, two checks
from outside: `curl` from this box to its public address, and from your Ubuntu
droplet to its private one.
