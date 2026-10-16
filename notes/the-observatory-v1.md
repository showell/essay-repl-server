# The Observatory, version one

*2026-10-16, late. Where the TCP client stands, and a plan for the
smallest Observatory that is still real: one target, Dog Park, polled on a
sleep interval. Steve's brief: very minimal, Dog Park first, another Dog
Park release if the server side needs anything, and at least some sort of
sleep-interval capability.*

## The client, in one paragraph

**The kernel can now be a client, and it ships.** v32, serving
lynrummy.com since this evening, carries a TCP client. It can:
- connect, with three deadlines (connect, idle, total) that fail fast;
- ask ARP for its peer;
- fetch one HTTP page.

No route calls it yet. On the way, the server's own TCP got sounder:
- after a loss it resends the oldest segment first, as RFC 6298 says;
- it holds segments that arrive ahead of a gap;
- every place it departs from the RFCs says why, in one of five words.

**The client has three judges:**
- **real Linux,** as server (18 cases, 5 s);
- **QEMU,** booting the client kernel to fetch a page;
- **our own server kernel,** two machines on metal-vmm taking turns, 50
  runs in 22 s, every page byte-identical to an independent copy, the
  whole run deterministic.

The Observatory is the first application that uses the client for
something. It is also the first one whose job is to *wait*.

## What v1 is

**A kernel that wakes up every N seconds, fetches one page from Dog Park,
writes one line about it, and goes back to sleep.** It serves one page of
its own showing the last lines. That is all.

- **One target:** Dog Park at its private address, `10.100.0.3:80`,
  `GET /`. Today that is the landing page, 1,185 bytes, answered in about
  40 ms.
- **One interval:** `interval_s` in its config, say 60. Each poll has the
  client's three deadlines, so a poll that hangs ends on time and says
  which deadline.
- **One line per poll,** appended to a file on its own disk:

      2026-10-17T09:14:00Z ok 200 1185 bytes 4 ms
      2026-10-17T09:15:00Z connect_deadline 150 ms

  The outcome word is the client's exit word (`ok`, `connect_deadline`,
  `idle_deadline`, `no_arp`, `reset`, `short` …), so the log speaks the
  same language as the judges.
- **One page,** `/`: the last 100 lines, newest first, plus a count of
  each outcome since boot. Behind prod's Caddy, private or public (a
  question for Steve below).
- **One disk, no volume,** as Dog Park: a release starts the history over.
  For v1 that is a feature. The history is what we look at today, not an
  archive.

**Not in v1, on purpose:** more than one target, lynrummy.com, Caddy's
logs, alerts, charts, retention, a pulse creature. Each is a v2 question.
Most of them are only worth asking once v1 has run for a week.

## The sleep interval: the one real piece of kernel work

**Every application so far only answers.** Chat waits for messages; Dog
Park waits for drags. The Observatory acts on its own clock, which the
kernel has never been asked to do. There are two ways to give it that:

**A. The application keeps its own clock, in `between`.** Zero kernel
changes. The kernel already calls the site's `between` after each request
and on idle turns (it is what steps background Shale runs). The
Observatory's `between` asks "is the next poll due?" and, if so, starts one
fetch, then advances it a step at a time on later calls.
- **What it costs:** the kernel idles by waking on a short timer. That is
  how gopher.elf showed up today in metal-vmm, waking every 0.8 ms,
  about 1,250 times a second, with nothing to do. On a droplet that is
  harmless. In metal-vmm it is the 3 million exits a 600 s idle costs.

**B. The application tells the kernel when it next needs to wake:
`between` returns a due time,** and the kernel rests until then or until a
frame arrives.
- **What it costs:** a small change in `probe/gopher.zig`'s main loop and
  its idle rest. Its payoff is large: an idle Observatory costs nothing
  between polls, and under metal-vmm a day of polling would take seconds,
  because time jumps over rests.
- **Every application benefits.** Dog Park's and chat's idle checks
  would sleep longer too.

**My recommendation: ship A in v1 and queue B right behind it.** A is a
morning's work in the application alone, and it proves the feature end to
end. B is then a kernel optimization with a working application to
measure it against, which is the right order (doctrine: build layers in
order, and earn the abstraction on its second user). If A's tick costs
show up as a problem, which they would first in metal-vmm's test runs, B
comes sooner.

## What Dog Park might need: one small release, maybe

v1 can poll Dog Park's landing page as it is. But a landing page is a
page for people, and the Observatory would be reading tea leaves in its
byte count. **The honest target is a `/version` on Dog Park**, like
lynrummy.com's:
- its commit;
- `started_ms`, so a restart is visible;
- the turns held, and the accounts handed out.

Small JSON, no secret in it.

That is a Dog Park release: a few lines in `src/play/`, its QEMU gate,
an image, and **one consequence to weigh**: a Dog Park release starts
every game over. So: v1 polls `/` first, and `/version` rides the next Dog
Park release that has another reason to happen.

## How we test it: the pair harness was built for this

Here is the happy accident of today's work. **metal-vmm's pair mode is
exactly the Observatory's test bench:**
- the Observatory kernel as one side;
- dogpark.elf as the other;
- the wire between them under our control.

Because metal-vmm skips time across a guest's rests, a sleep interval
costs no wall time. With B in place, a hundred polls 60 s apart is a
hundred minutes of guest time and, measured the way today's pair runs
were, a few seconds of ours. With A, the idle ticks make it slower; that
is the first number v1's tests will report, and the case for B.

**The scenarios, almost all of which `pair.sh` already knows how to
make:**
- **Dog Park answers every time:** N lines, all `ok`, the page
  byte-identical each time.
- **Dog Park is silent for a stretch** (every frame from its side lost
  between poll 10 and poll 20): those lines say `connect_deadline`, the
  rest `ok`, and the Observatory never stops polling.
- **Dog Park restarts mid-run:** the line after says `ok` again.
- **A poll that would run past the next one's time:** the next waits
  (one fetch at a time, never two), and the line says it was late.

And against real Linux, as the client's native judge does: the
Observatory's poll loop on Linux, against a Python server that answers,
stalls and refuses on a schedule.

## The plan, as chunks

1. **The Observatory app** (a new repo, or a folder in dog-park; a
   question below), built with `addAppKernel` like Dog Park:
   - a `Site` whose `between` keeps the schedule (option A) and runs
     `fetch.Client`;
   - its log;
   - its one page.
2. **Its tests:**
   - unit tests of the scheduler: due, late and one-at-a-time, purely, by
     a clock we pass in;
   - the poll loop on Linux against a stalling Python server;
   - a `pair.sh`-style gate against dogpark.elf.
3. **Its droplet:** the cheapest one, nyc2, on the private network; a
   Caddy block; deployed by the steps in `DEPLOY.md`.
4. **Then, when earned:** B in the kernel, `/version` on Dog Park,
   lynrummy.com as a second target.

## Open questions for Steve

- **Where does it live?**
  - **Its own repo** (`observatory`) is cleanest, the third tenant proving
    the platform.
  - **A folder in dog-park** is quicker, and wrong in the long run.
- **Private or public page?** Public behind Caddy is a status page anyone
  can see, Dog Park's uptime included. Private (reached through prod, or by
  a Shale script) keeps v1 smaller. I lean private for v1.
- **The interval:** 60 s is gentle and makes a day's page fit in 1,440
  lines. Any reason to want faster?
- **B now or later?** My recommendation is later. But if a Dog Park
  release happens anyway, its kernel could carry B at no extra release
  cost.
