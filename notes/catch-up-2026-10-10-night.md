# Catch-up, late night 2026-10-10

*Where everything stands, and four yes/no questions at the end (each
defaults to yes). Nothing is running on the box now.*

## Since you stepped away: idle time, the smallest first version

**Built, tested, pushed** (gopher-metal `28649cd`, `48a167f`; design in
[idle time on metal](idle-time-on-metal.md)):

- **The queue** (`src/idle.zig`): when the kernel's loop has nothing to
  serve and nothing has arrived for 200 ms, the next idle task gets one
  step, after the console's turn. A step over its 200 ms budget breaks a
  property and is counted.
- **The first task** (`src/idle_check.zig`): each volume's check, asked
  again while the machine serves. Step one walks the tree through the FAT
  and folders held in memory; each later step compares 8 runs of the FAT
  copies on the disk (~100 ms of production's disk). A write mid-check
  starts it over, so findings never come from a half-changed volume. Then
  an hour's rest.
- **One implementation:** the boot's check now runs the same code to the
  end that the idle task runs in slices.
- **`/admin/host`** will show idle steps, overruns, and each volume's last
  check: when, files, folders, damage, leaks, restarts, the longest step.
- **Tests:** the sliced check finds exactly what the whole check finds
  (damage included) and stops when a write lands; the queue waits for quiet,
  takes turns, counts overruns; the task slices, restarts, rests.

**On a booted kernel** (metal-vmm, 30 seeds): idle steps ran, the longest
~9 ms against the 200 ms budget, and a sliced check finished. The clean
kernel passed.

**Two things worth knowing:**

1. **My first commit didn't build as a kernel.** `zig build check` had
   skipped the kernel because my own angry-gopher commits left the port
   stale. It printed "NOT type-checked" and still exited 0, and I'd
   filtered its output for errors. Fixed in one line, but the trap is
   structural: that's question 2.
2. **A plant miss that turned out not to be mine.** In those 30 seeds the
   TCP plant fired 4 times and was never caught. The same 30 seeds on
   master *before* idle time give exactly the same result, so it's the
   small sample (across 300 seeds it's caught in 15).

**The gap:** idle steps ran in only 3 of 41 runs, because a sweep's kernel
stops right after its last request. Sweeps need idle windows on purpose:
that's question 1.

## Earlier tonight, for the record

- **Plants and tests pass on master** with batched frees and CC's 150-152;
  the judge holds fsck's orphaned names to the kernel's count of them.
- **`/admin/search?key=…`**, the dumb baseline (angry-gopher `017b6801`):
  reads every transcript *you* can see (`chat_store.visibleConvs`), blocks
  everyone while it runs, and only runs on a GET from this site. A cold
  review found no blocker; its fixes are in.
- **Search decisions** (recorded in the KV essay's "Decisions" section):
  the index lives in memory, derived from the transcripts, built at boot;
  the client is dumb (the server tokenizes); no self-DMs or stranger DMs;
  the KV store waits for a real source-of-truth user.
- **CC's queue, revised** after a cold review, with your answers: 153 (send
  cuts 1, 2, 3, 7; 4 deferred; last-seen dropped), 154 (review follow-ups,
  scoped down), 155 (search's server side, UI later). **Waiting on your
  go to CC.**

## Four questions (default: yes)

1. **Should the kernel linger ~500 ms of virtual time after its last
   request in sweeps, so every run ends with idle work, followed by a full
   plants run (~15 min) before anything builds on it?**
   *Yes* means every seed exercises idle time and no seed changes which
   shape it runs. The cost: every run ends differently, and an idle step
   may meet a fault aimed at a request (which is also a test).
   *No* means I add a separate shape instead, which remaps which shape
   every seed runs.

2. **Should `zig build check` fail, not warn, when it can't type-check the
   kernel (a stale port)?** *Yes* closes the trap that bit me tonight, for
   CC too. The cost: a stale port stops `check` until `./port.sh` is run.

3. **Is the revised queue (153-155) ready for your go to CC?** Nothing in
   it changed since the cold review's edits and your five answers.

4. **Cut v23 from master once question 1's plants run is clean, without
   waiting for CC's 153-155?** Master already has what you held v23 for
   (batched frees, 152), plus `/admin/search` (which would give us the
   real corpus size for search) and idle time (production would start
   reporting its own volume checks). *No* waits for CC's batch, likely
   another day.
