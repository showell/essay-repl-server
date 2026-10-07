# The other doors

*2026-10-07. A web server in a box, past the Store: the interfaces an
application needs besides its data, grounded in what angry-gopher actually
uses today. Follows [a web server in a box](a-web-server-in-a-box.md) and
[where the metal stack stands](where-the-metal-stack-stands.md).*

## The pattern, again

The Store turned out to exist already: angry-gopher had built its own
`store.zig`, with FAT's rules on every host, before we went looking. The same
is true of the rest. The top of angry-gopher's `router.zig` declares **the
host contract**: seven things any host must do before it calls `route`, and
"a kernel that boots this table has no other contact with the application".
`bus.zig` declares a streaming door with a clean rule: **the application
describes a stream; the host keeps it.**

So this isn't a design from scratch. It's what the Store work was: find the
doors the application already uses, count how wide each is, write the
contract down, narrow it where it's machine-shaped, and put a judge on it.

## The census, beyond the Store

Every place angry-gopher's 77 server files reach something other than their
own logic or their data:

| door | used | what for |
|---|---|---|
| **the request**: zig's `std.http.Server.Request` | 60 calls, 39 files | every handler takes one |
| **live streams**: `Bus`, publish and subscribe | 27 calls, 8 files | chat, notifications, Recent |
| **writing a response out in parts** | 31 calls, 9 files | streams, large pages |
| **locks** | 45 calls, 12 files | Linux runs requests at once; metal doesn't |
| **password hashing** (bcrypt) | 41 calls, 7 files | login, API keys |
| **the clock** | 26 calls, 16 files | timestamps, sessions, throttles |
| **signing** (HMAC) | 20 calls, 2 files | session cookies |
| **config** | 15 calls, 7 files | the few settings a deploy names |
| **the host's log and facts** | 13 calls, 3 files | /admin/host |
| **random bytes** | 7 calls, 3 files | session ids, salts, upload names |
| **the network itself** | 2 calls, 2 files | |

Two things stand out. **The request is the widest door by far**, and it's
zig's own type, which is machine-shaped by definition. And **the locks**
are a door nobody named: they exist because the two hosts run requests
differently.

## Each door

### The request: the one to narrow first

Today every handler takes `*std.http.Server.Request`: zig's whole HTTP
server object, with its reader, its header iterator and its
connection-level behaviour. That works on metal only because gopher-metal
runs zig's own HTTP server, unmodified, over its own TCP. It's the reason
the port is one line per file. It's also why no other language can be a
tenant: a Roc or Cobblestone application can't take a zig server object.

**The proposal:** a small Request the host fills in, and a Response the
application returns.

- **Request:** method, path, query, a header lookup, the cookies, the
  client's address (as Caddy's trusted proxy says), and the body, already
  read up to the route's cap.
- **Response:** status, headers, and a body that's either bytes or **a kept
  stream** (the Bus's door, below).

**The strictness rule applies here too.** The Linux twin enforces metal's
limits (the largest header, the largest body, a slow client's patience)
before the application sees anything, so a request that would fail on the
droplet fails on a laptop. Today those limits live in three places: Caddy,
zig's server, and metal's TCP.

**The judge comes free.** A recorded session, meaning requests in and the
responses plus the Store's tree out, replayed against the Linux host and
the metal host. That's the chat judge we already run, written as a contract
any application gets.

This is the biggest single change: 39 files' handlers move off zig's type.
It's mechanical once the Request type exists, but it's broad.

### Live streams: already the best door

`bus.zig` is the design the first essay hoped for, and it already runs both
ways. A handler writes a stream's headers and backlog, records what it
*keeps* (a subscriber, and how to render an event for this viewer), and
returns. Linux serves a kept stream by blocking on that connection; metal's
single loop asks for the next frame when it has room to send it. One source,
two hosts.

What it lacks is what the Store lacked: **a written contract and a judge.**

- **The contract:** events are live-only. A slow reader's full queue drops
  the event, and reload re-derives it. That rule is in a comment, and it
  deserves to be the contract. Ordering per key, and what a stream owes at
  its end, should be written down too.
- **The judge:** a simulator that drives the Hub with publishers, readers
  that stall, and readers that vanish, under both hosting styles (blocking
  and next-frame), and checks the same frames reach the same readers. It's
  pure logic. It's also where CC's proposed `Wait` seam under `stream.zig`
  fits.

### Durability: a door the platform owns entirely

v18 added a promise the application never sees: **no response leaves before
the writes ahead of it are on the disk.** The application never calls
flush; the host does, at the one moment that matters. That belongs in the
contract as the platform's promise, because it's what lets an application
say "saved" honestly. It's also where yesterday's "hold metadata writes
until the durability point" idea would live.

### Concurrency: the door nobody named

Linux runs requests on many threads at once; metal runs one loop. Today
angry-gopher bridges that with locks: `chat_mu` and 44 other lock calls,
correct for Linux and no-ops in effect on metal. The first essay's rule
says the twin must not hide a race the droplet never hits, *or the
reverse*. Right now the two hosts are different machines here, and the
judge can't see it, because it replays requests one at a time.

**The proposal: the platform runs one handler at a time, on both hosts.**
A handler runs to completion with no other handler interleaved. A kept
stream is served between handlers, never during one. Applications lose
their locks entirely, metal is already this, and at lynrummy.com's scale
Linux loses nothing that matters. The alternative is to keep concurrency on
Linux and teach the judge to interleave; that's a much bigger tool for a
benefit we don't need. **This is a decision for you**, because it's a real
constraint on any future tenant.

### Clock and random: doors the explorer needs

Both are nondeterminism, which makes them exactly what "steering by design"
says the platform should own.

- **Clock:** "now" as wall time (for timestamps people read) and as
  monotonic time (for timeouts and throttles). On metal it's set from the
  hardware clock at boot and never corrected. Under metal-vmm it's a
  decision.
- **Random:** bytes, cryptographic on every real host: virtio-rng and
  RDRAND on metal, the OS on Linux.

**In tests, both come from the tape.** Then the explorer can steer a
session's expiry or an id collision the way it steers a disk fault. Today
angry-gopher reads the clock in 16 files through zig's `Io`, so on metal
it's already injectable. Making it explicit is mostly a matter of not
reaching around it.

### Crypto: a service, for tenants that aren't zig

Password hashing (bcrypt) and cookie signing (HMAC) are 61 calls, all
through zig's standard crypto. For zig tenants that's fine, and it should
stay. For a Roc or Cobblestone tenant, writing your own bcrypt is how
security bugs are born, so the platform should offer four functions: hash a
password, verify one, sign bytes, verify a signature. That's narrow,
security-critical, and identical on every host.

### Config, log, host facts: small and nearly done

- **Config:** a value by name, typed when read; refused if malformed. B21
  just made "unreadable" stop the boot rather than quietly use defaults.
- **Log:** a line, with secrets taken out as it's written (metal already
  does this for /admin/host).
- **Host facts:** what /admin/host shows. `host_status.provide` is already
  this door.

## The shape of it

| door | exists today | the gap |
|---|---|---|
| Store | angry-gopher `store.zig`, judged by `store-judge` | `has()`, the cut rows, the model's limits |
| **Request / Response** | zig's own server type | **the door itself**, the biggest change |
| Streams (Bus) | `bus.zig`, both hosts | a written contract, a simulator |
| Durability | v18's flush | written into the contract |
| **Concurrency** | locks on Linux, one loop on metal | **a decision**, then deleting the locks |
| Clock, random | through `Io` | owned by the tape in tests |
| Crypto | zig std | a four-function service, for other languages |
| Config, log, facts | `config.zig`, the log ring, `host_status` | written down |

## What I'd do, in order

1. **Write the host contract down** (`HOST.md`, beside `STORE.md`): the
   seven steps `router.zig` already lists, plus durability and the
   concurrency rule once you've decided it.
2. **The concurrency decision**, since it changes how every other door is
   written.
3. **The Bus contract and its simulator**: pure logic, the best door made
   provable, and a natural item for CC as builder again, or as adversary.
4. **The Request door**, last of the big ones and the widest. It's what
   makes a non-zig tenant possible, and it deserves its own essay once the
   others are settled.

Clock and random ride along with the explorer work; crypto and the small
doors take an afternoon each when a second tenant actually arrives.
("Abstraction earns its keep on the second user.")

## Questions for you

1. **One handler at a time, on both hosts?** My recommendation is yes.
2. **Is a second tenant in view?** Lyn Rummy as its own app, a Roc app, or
   a Cobblestone one. The Request door and the crypto service are only
   worth their cost if one is coming; the contract and the judges are worth
   it regardless.
3. **Body caps and limits in one place?** Caddy, zig's server and metal's
   TCP each hold some today. The contract would name one source of truth.
