# The third tenant

*2026-10-16. Brainstorming the unikernel's third application. Steve's
brief: break new ground without being too much of a rabbit hole; fun or
useful; above all, push the unikernel in a way that creates a feedback
mechanism.*

## What the first two have in common

Chat and Dog Park look different, but they share one shape. Each is a
server that **answers**:
- requests arrive through prod's Caddy;
- the kernel replies;
- between requests, nothing happens unless something asks.

Dog Park pushed this furthest: its server is a referee that never plays,
re-running what the page reports. Even the background Shale runs are
slices fitted into the gaps *between* answers.

So the cheapest way to break new ground is to break that shape. There are
four directions I can see:
- **the kernel as a client,** reaching out instead of waiting;
- **the kernel acting on its own clock,** not on someone's request;
- **the kernel facing the internet directly,** with no Caddy in front;
- **the kernel doing heavy work inside a request.**

Each idea below takes one or two of these. Each also has to answer Steve's
key question: what feeds back?

## 1. The Observatory: a droplet that watches the other two

**What it is.** A small droplet on the same private network that:
- polls lynrummy.com and Dog Park on a schedule (`/version`,
  `/admin/host`, the home page) and records the answers and their times;
- receives prod's Caddy access logs, posted to it in batches by a small
  script on prod;
- keeps the history and serves one status page;
- answers Shale scripts over all of it.

**The new ground:**
- **The kernel as a client.** Today the kernel's TCP code only accepts
  connections. The Observatory opens them: a connect, one HTTP request, a
  timeout, and a peer that might not answer.
- **Work on its own clock.** It polls every minute whether or not anyone
  is looking. This is exactly what Dog Park sidestepped by becoming
  client-driven. The kernel's timers, its idle loop and its "between"
  hook would carry a scheduled job for the first time.
- **Writes that only append, onto data that keeps growing.** Chat writes
  in bursts when people talk. The Observatory writes steadily, forever.
  The FAT layer, the cache and log rotation all get a workload that
  never stops.

**The feedback mechanism is the product.**
- It would replace things we do by hand today: the watchdog Steve runs
  over SSH, and `knocks` run on demand.
- Its data grows on its own, so it is its own slow stress test. In a
  month it holds a month of logs and finds out what that does to the
  disk.
- Every anomaly it shows is in our own stack. Either a sibling droplet
  misbehaved, or the Observatory did, and either one is a finding.

**The rabbit-hole check:**
- **No TLS and no DNS:** the private network and fixed addresses
  (10.100.0.3, .4) avoid both.
- **The client code is small:** a TCP connect plus one HTTP/1.1 request
  with `Connection: close`.
- **The real danger is scope creep** into a monitoring product, with
  alerting, charts and retention policies. Cap it: one page, a handful
  of Shale scripts in a cookbook, and no alerting at first.
- **"Who watches the watcher"** has a cheap answer: the Observatory's own
  `/version` goes on the list `knocks` checks, so the box notices when it
  stops.

**Is it fun?** Not obviously. But a status page with a month of the
site's heartbeat on it, and scanners visible as weather, is the kind of
thing that becomes a pleasure to glance at.

## 2. A shared toy where the server owns the clock

**What it is.** Something several people see at once, that moves on the
server's clock rather than any player's:
- **a pond:** fish drift, visitors drop food, and the fish remember who
  fed them;
- **or a Dog Park "commons":** one shared park where the herds keep
  moving after you let go.

**The new ground:**
- **The world advances on the server's clock.** Chat waits for messages;
  Dog Park waits for drags. This one doesn't wait.
- **Fan-out:** one tick goes out as a live stream to every viewer.
  Chat's streams exist, but nobody has ever pushed many of them at once.
- **Timer accuracy under load,** in a form you can see.

**The feedback mechanism.** People. Damian and Apoorva played Dog Park
within an hour of it going live. A shared toy turns every timing bug into
something a person notices: a stutter, a fish that jumps. That's a very
honest instrument.

**The rabbit-hole check.** Networking for real-time games is one of the
deepest holes in software. Stay out of it by being slow: a few ticks a
second, things that drift rather than dart, and nothing a player must
react to in under a second. And no prediction on the client side; that
is the hole.

**Is it fun?** Yes, and it's also the cheapest way to get people other
than us into the loop.

## 3. A tiny public DNS server

**What it is.** Authoritative DNS for a subdomain such as
`*.lab.lynrummy.com`: a handful of records, served over UDP, with no
recursion.

**The new ground:**
- **UDP as a server.** The kernel speaks UDP today only to get its own
  address by DHCP.
- **No Caddy in front.** The kernel faces the internet on its public
  card. Every scanner, amplification probe and malformed packet lands on
  our code directly.

**The feedback mechanism.** The internet itself:
- resolvers will query it constantly, and scanners will probe it
  constantly;
- that's a free, endless, hostile input stream, exactly what the kernel's
  README admits production never gives it today ("one polite client");
- today's scanner-visibility work would become this target's main act.

**The rabbit-hole check:**
- **Authoritative-only is genuinely small:** a fixed zone, a parser for
  one message format, and a refusal for everything else.
- **The traps** are recursion, DNSSEC and zone transfers. Refuse all
  three.
- **The one real risk is reflection attacks:** a DNS server can be
  abused to amplify traffic at a victim. Rate-limiting answers by source
  is a small, necessary piece.

**Is it fun?** Not really. It is the most adversarial of the four, which
fits the kernel's zero-bugs goal, and the least delightful.

## 4. A photo shelf

**What it is.** Upload a photo; the shelf stores it, makes thumbnails and
serves an album. lynrummy.com's chat already holds uploads of several MB
each (the `big_files` script found one of 5 MB, and many of 2 MB), so
there's a real collection to start from.

**The new ground:**
- **Heavy CPU work inside a request:** decoding and resizing an image
  takes real milliseconds. Today the kernel's turns are short.
- **Large files end to end:** through the upload path, the cache and the
  disk.

**The feedback mechanism.** Usefulness: Steve's own photos, browsed on a
phone. Every slow thumbnail is felt.

**The rabbit-hole check.** Image formats. PNG decoding is a weekend;
JPEG is a project, and phone photos are JPEG. Accepting only PNG makes it
small and makes it less useful. That tension is the honest problem with
this one.

## Comparing them

| | new ground | feedback | fun | rabbit-hole risk |
|---|---|---|---|---|
| Observatory | a client; its own clock; growing data | watches our own stack, daily | modest | low, if scoped |
| shared toy | the server's clock; fan-out | people noticing stutters | high | medium (stay slow) |
| DNS | UDP; facing the internet | the internet's hostility | low | low-medium |
| photo shelf | CPU in a request; big files | Steve's daily use | medium | JPEG |

## The recommendation: the Observatory

It breaks the most new ground for the least risk:
- **It is a client, it runs on its own clock, and its data grows.** None
  of the three has ever been asked of the kernel.
- **It is useful on its first day,** replacing two things done by hand.
- **It is a feedback mechanism in the most literal sense.** It watches
  the other tenants, so the bugs it surfaces are ours, in a place we
  already care about.

And one more reason, which may be the deepest. It would be **the third
application built through `addAppKernel` and `app_image.py`.** Today's
essay ("The second tenant") argued that the second application turned
the kernel into a platform. The third tells us whether that platform is
real. If the Observatory takes as little plumbing as Dog Park did, or
less, the platform has earned its name. If it takes more, we learn
exactly where the platform still bends around its first tenant.

**If fun matters more than usefulness this time,** idea 2 is the pick. It
pushes on the same question as the Observatory, a server that acts on its
own clock, and it brings people in.

**A combination worth naming.** Build the Observatory first, then give it
a small fun face: a "pulse" page where each site is a creature that
breathes with its response times, and scanners drift past as weather.
That keeps the useful core and lets the toy grow on top of something
real.

## Open questions for Steve

- Is the Observatory's first job **polling** (the client, the clock) or
  **logs** (ingest, growing data)? Polling is smaller and breaks more new
  ground; I'd start there.
- **Should it face the internet at all?** Private-only keeps it simple.
  Behind Caddy like the others, it would get a status page anyone can
  see.
- **One disk, like Dog Park, or a volume, like lynrummy.com?** Its whole
  value is history, so this is the first target where persistence across
  releases is plainly earned from day one.
