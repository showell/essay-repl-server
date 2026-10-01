# Chat on a droplet with no Linux: where we stopped

*2026-10-01, end of the day. gopher-metal `5e8b88b`.*

## The milestone

Gopher Chat, the real server (angry-gopher's own code, every route), ran on a
DigitalOcean droplet with **no operating system under it**. You logged in from
your browser, created an account, and opened Lyn Rummy and Seattle Delivery
too. From this box I logged in, posted a message, and read it back. It booted
from a disk image uploaded the ordinary way, found its hardware itself, got its
address from DigitalOcean, and answered over the real internet.

## What the day built, in order

1. **A droplet, imitated here.** QEMU set up with the same devices in the same
   slots as a real droplet, checked slot by slot against this box (which is a
   droplet).
2. **Our own boot loader.** About 300 lines: the BIOS runs it, it loads
   gopher-metal and starts it the way gopher-metal expects.
3. **Finding devices on the PCI bus,** the way a PC lists them.
4. **DHCP that asks again** when an answer is lost.
5. **Writing on the screen,** because DigitalOcean's console shows only the
   screen.
6. **The first real droplet,** and a detour: DigitalOcean's import wrapped our
   disk inside a new one, because our partition 1 was empty. We found that by
   looking at the droplet's disk from its rescue mode. Fixed by putting the
   kernel in partition 1.
7. **Chat's files in partition 2,** and the real server on the droplet.
8. **The private card:** chat can be told to listen only on the droplet's
   private network, where prod's Caddy will reach it.
9. **The chat judge, on the droplet machine.** The same judge that compares
   every answer with the Linux build now also runs on the droplet-shaped
   machine, and passes everything.
10. **A slow screen, fixed.** You spotted about 60 ms per request. It was our
    own logging: every log line scrolled the screen by copying all 2,000
    characters of screen memory, one slow trip to the hypervisor each. Now the
    screen scrolls by telling the display "start one row lower", which is how
    PCs have always been able to do it. Here that took a request from about 250
    ms to 13.5 ms.

## Things you noticed, and what they were

- **Scanners** (`/mcp`, `/sse` and so on) hit any public address within a
  minute. They're answered 404 in microseconds. Chat on the private card ends
  that.
- **"waited" ~70 ms** for scanners is one network round trip to wherever they
  are. Mine from this box was 1.4 ms.
- **No pictures:** the home page's pictures live in a `gallery/` folder that
  prod's deploy copies and the test site didn't have. Fixed in the next image
  (`gopher-metal-chat-v2`), checked here: they're served.
- **"apoorva" and "Steve":** the droplet's data is the judge's test site, with
  two accounts named after prod's. Plus one rule in angry-gopher itself
  (`docs.zig`, "post to chat": Steve talks to Apoorva, everyone else talks to
  Steve).

## What's next, when you pick it up

- **Upload `gopher-metal-chat-v2`** (with the pictures and the private card)
  and point a test address on prod's Caddy at `10.100.0.4`.
- **Deploys and data:** rebuilding a droplet replaces its whole disk, chat's
  files included. Chat's files belong on a separate DigitalOcean volume (which
  needs a driver for the controller volumes attach to) or in some other place a
  deploy doesn't touch. You said to leave this until much more testing has
  been done.
- **One unexplained stall:** one boot here printed its first line and then
  nothing for a minute. 26 boots since all came up in a second. Unexplained,
  noted, being watched.
- The test site's accounts, if you want different ones for testing.
