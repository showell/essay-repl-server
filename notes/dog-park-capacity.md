# Dog Park's capacity: how many players, and what fills up first

*2026-10-15. A cold agent measured the numbers on this box; I edited the
results and folded in a log-retention policy. It covers dog-park `main`
`9e5eb75`, the small world: 6 × 6 tiles, 64 dogs, 8 cows. Numbers marked
measured were measured; the rest are estimates built on them.*

## The answer

On the smallest DigitalOcean droplet (1 vCPU, 1 GiB), the game could
serve about this many:

| | 1 vCPU / 1 GiB | 2 vCPU / 2 GiB |
|---|---|---|
| dragging at the same moment, at your real hand speed | **~25** | ~30–35 |
| dragging at the same moment, worst case (a full 100 + 100 px drag every tick) | ~3 | ~4 |
| **playing** (dragging a quarter of the time) | **~80** | ~100 |
| accounts, if about 10% play at the busiest time | ~800 | ~1,000 |
| games kept in memory for an hour | ~3,000–4,000 | ~10,000 |

**The CPU limits play, and the disk fills first.** The log has no limit
today. It grows by about 30 MB for every hour a player plays, so 80
players would fill a 25 GB droplet in under a day of busy play. Memory is
nowhere near a limit.

**A second core doesn't double anything.** The server checks one report
at a time (webbox's "turn"), so checking is capped at one core. A second
core only takes Caddy, TCP, the kernel and waiting for disk syncs.

## Where the time goes

The server re-runs every tick the page reports. The cost model is
roughly **half a millisecond per report, plus about 50 µs per pixel of
drag.** It grows in a straight line, because the walk is capped at 48
critters: even a crowded spot costs only about 10% more.

| | measured |
|---|---|
| one tick, a full drag at the busiest spot (200 one-pixel steps) | 9.3 ms |
| the same, among 421 poops / in a packed herd | 10.2 / 10.8 ms |
| a 16-tick report through `POST /report`, gentle drag | 12.5 ms (31 KB) |
| the same, a full drag every tick | 149 ms (37 KB) |
| the same, leashed but not dragging | ~0.5 ms (335 B) |
| a log append plus a sync of the whole filesystem | 0.3–0.8 ms (worst 6 ms) |
| one small report's round trip through the real server (TCP + HTTP) | 1.2 ms |

**How you actually drag,** from your own logs (the old park, 4 reports a
second):
- **Distance:** a tick with a drag moves the dog a median of 11–14 px, a
  mean of about 19, with 90% under 42 and 99% under 110.
- **How often:** about 41% of the ticks that ran carried a drag.

**A player costs the server, per second of play:**
- dragging at your average speed: ~18 ms (2% of a core); ~26 ms on a slower droplet core;
- dragging briskly (50 px a tick): ~45 ms;
- the worst case: ~150 ms (15% of a core);
- leashed but not dragging (the 20 s before the leash comes off): ~2 ms;
- resting: nothing.

The 1 vCPU numbers assume a basic droplet core is about 1.5× slower than
this box's. That factor is a guess.

**The arithmetic for the table:**
- **At your average speed:** 700 ms of a core per second (a 70% target),
  divided by 26 ms per dragging player, is about 27 players dragging at
  once.
- **Worst case:** about 3 players.
- **Typical play:** with a quarter of the time dragging and the rest
  leashed, each player costs about 8.5 ms a second, which allows about
  80 playing.

One worst-case report holds everyone else up for at most 150 ms. That's
well inside the page's 2 s window, so nobody's game freezes from it.

**On the page:**
- **A laptop:** spends about 2% of a tick on your average drag, and 30% on
  the worst.
- **A phone** (estimated 3–5× slower): fine on ordinary drags. On a
  maximal drag it falls behind, at 56–94 ms for a 62.5 ms tick:
  correct, but sluggish.

## Memory: ~150 KiB a game

**Measured:**
- **A game's server state:** 151,928 bytes. Most of that is two 64 KiB
  answer buffers; the board itself is about 20 KB.
- **Each request in flight:** about 300 KiB, briefly.
- **The running :9103 server:** uses 12 MB.

Leaving about 300 MB for the OS and Caddy:

| memory | games |
|---|---|
| 512 MiB | ~1,300 |
| 1 GiB | ~4,000 |
| 2 GiB | ~10,000 |

One hidden cost: **starting a game reads its whole log into memory**,
inside the turn, before applying the part after the snapshot. With
today's multi-MB logs, that's a spike and a pause. Trimming the log
(below) fixes this too.

## Your policy: try to keep a game for an hour, promise nothing

That works out cleanly:
- **In memory:** keep the games used most recently, evicting the least
  recently used past a cap (about 1,000 games on 1 GiB, 3,000 on 2 GiB).
  An evicted game restarts quickly from its snapshot when its player
  comes back.
- **Only evict games idle for a few minutes.** A game restarted from disk
  starts a new epoch, and a page still open on it gets "the server
  restarted" and stops. That's within "promise nothing", but it shouldn't
  happen to someone mid-game.
- **On disk:** see log retention, next.

## Log retention: a debugging record that stays bounded

The log is the right record for debugging: every kept report, exactly as
the page wrote it. It's how I rebuild your boards when you report "dog
185 can't move". But it only ever grows. **The snapshot plus the log
after it is all a restart needs,** so the rest is only for debugging, and
can be bounded on purpose.

The proposal:
1. **Rotate each game's log at a snapshot.** A snapshot is written every
   64 kept ticks, which is 4 s of play. Rotate on a size or time
   boundary rather than at every snapshot: start a new log file every
   10 minutes of play, with the snapshot it starts from.
2. **Keep each game's logs for its last hour of play, while the game is
   kept.** That's up to about 30 MB for a game played the whole hour, and
   far less for most. This matches "try to keep it for an hour", and
   covers any bug you report within the hour.
3. **A total cap for every game on disk,** say 2 GB on a 25 GB droplet,
   deleting the oldest rotated files first. If the cap bites, a busy
   hour loses its oldest debugging history first, never a game's current
   snapshot.
4. **An evicted game keeps its folder** (snapshot plus recent logs) under
   the same cap. It's deleted after an hour idle, or sooner if the cap
   needs the room.
5. **A game kept for an hour without its logs** costs only 20–50 KB on
   disk (snapshot plus tail). Disk stops being a limit, and CPU is
   the real ceiling.

Steve, you said persistence would be wise "even if it's only for
debugging". This keeps it, sized deliberately, and makes restarts
cheaper as a side effect.

## What changes in the code (not written yet)

- **Retire "one player at a time"; admit up to N.** Keep the turn's
  `503 busy N` as admission control. At most about **20 accounts** hold a
  20-second play turn at once on 1 vCPU (25 on 2 vCPU). That bounds the
  worst case: 20 players at your average speed is about half a core.
  - The 5-account cap becomes a memory and disk cap, of hundreds of
    accounts.
  - In `players.zig`: `most_players`, `claimed: u8`, and `slotOf`, which
    reads one-digit ids, all grow. `Turn` becomes a small set of
    holders.
- **Games become a map, not five slots.** In `app.zig`, the fixed
  `games` and `reset_next` arrays become a map with a least-recently-used
  list, and eviction that frees a game's server state.
- **Log rotation and the retention cap,** as above.
- **The big lever, later:** games don't interact. Judging each game under
  its own lock instead of the global turn would let 2 vCPUs really mean
  twice the players. That's a webbox design question, not something for
  tomorrow.

## Not measured, and worth measuring on the real droplet

- **The droplet's core speed:** run `physics-server-bench` there to
  replace the 1.5× guess, and the fsync bench on its disk.
- **A load test:** N synthetic pages replaying one of your logs at a
  report a second, through Caddy. Measure CPU, the wait for the turn
  (p99), and sync time.
- **Memory with 1,000 games started.**
- **Starting a game whose log is several MB.**
- **A tick with all 2,048 poops in view.**
- **A real phone.**

The rest:
- **Keep-alive (QUEUE 213):** barely matters for capacity, since TCP plus
  HTTP is about 1 ms of a 26 ms report. It's for development's
  connection churn.
- **Caddy:** opens a fresh connection to the server for each request.
  That costs a little CPU on the same core; not measured.
- **The drag statistics are yours alone,** from the old park.

**Two benches are stale for the small world.** `physics-server-bench`
doesn't compile (it leashes dog 137 of 64), and `bench_page.mjs`'s
packed herd crashes. The agent fixed both in a scratch copy only. I'll
fix them properly.
