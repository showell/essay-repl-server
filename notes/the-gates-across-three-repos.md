# The gates across three repos

*Steve's Claude on the dev box, 2026-10-06. A map of how angry-gopher,
gopher-metal and metal-vmm are tested today, what each check costs, and
where it could be better. Times are measured this morning unless marked
otherwise.*

## The one principle

A check earns its place by **what the change could break** and **what the
commit is for**. A commit that will never ship on its own (a refactor, a
chat tweak tested live, a simulator) needs the checks for what it touched. A
commit that becomes an image on lynrummy.com needs everything, on exactly
that code. Most of what follows asks whether each repo's tiers line up with
that.

## The map

- **angry-gopher** is the program: every route and app, written and tested
  on Linux. It no longer deploys itself; `ops/deploy` only refreshes the
  watchdog on prod, because metal serves.
- **gopher-metal** is the machine: kernel, drivers, FAT, TCP. `port.sh`
  copies angry-gopher's `zig-server/src` in and swaps `std.Io` for
  `metal.io`. A **release is a boot image** built by `droplet/chat.py`
  from both repos.
- **metal-vmm** is test-only: our deterministic hypervisor, run by
  gopher-metal's gates and by its own scripts.
- **Cloud Claude** works on metal-vmm and gopher-metal's simulators. It has no
  KVM, so it runs unit tests only; every guest boots on this box.

The path a line of code takes to the site:

    angry-gopher commit → port.sh → gopher-metal gates.sh + long.sh → chat.py image → droplet rebuilt

## Each repo's tiers, and what they cost

### angry-gopher

The gates follow the subsystems (from its ops memory, not re-measured today):

| Just edited | Gate | Warm |
|---|---|---|
| chat | `ops/check_chat` | ~3 s |
| Lyn Rummy (Elm or TS) | `ops/check_lynrummy` | ~30 s |
| the zig server only | `ops/check_zig` | ~1 s |
| cross-subsystem, or "about to commit" | `ops/check` (all of the above, plus safari, chess, solver, docs, CSS) | ~40 s |
| engine hot path, milestones | `ops/check_full` | ~2 min |

A pre-commit hook (`ops/git-hooks/pre-commit`) runs the whole `ops/check`
on every commit. **It is not installed on this box** (`core.hooksPath` is
unset), so in practice the over-testing comes from habit: my memory says
"`ops/check` before committing", whatever the commit touched.

### metal-vmm

| Check | What it asks | Time |
|---|---|---|
| `zig build test` | 221 tests of the models, no guest | ~3 s |
| `check.sh` | nine probe kernels, same words here as under QEMU | ~22 s |
| `same.sh` | the same guest twice, identical runs | ~5 s |
| `site.sh all` | the real server, every route, here and under QEMU | ~100 s |
| `rest.sh all` | the PC-shaped machine: halts and interrupts, every route | ~50 s |
| `lossy`, `flaky`, `sound`, `sweep` | by hand, for hunting | varies |

Since yesterday the box runs the unit tests plus `check.sh` and `same.sh`
(half a minute) at every merge of Cloud Claude's work. That rule exists
because a two-line special case in `check.sh` failed a merge two hours late.

### gopher-metal

`gates.sh` has two tiers. **`quick`** (about two minutes: host tests, the
kernels, the probes, one chat-judge story) is for a single commit. **Full**
is for a batch or a release. Its stages this morning, on v17's code:

| Stage | Time |
|---|---|
| `zig build test` (830 tests) | 76 s |
| the kernels and gopher.elf | 91 s |
| the probes | 52 s |
| **the chat judge, FAT32, on microvm and the droplet machine side by side** | **616 s** |
| **the chat judge, FAT16, microvm** (only when FAT or io code changed) | **520 s** |
| droplet boot, droplet hello, screen | 80 s |
| metal-vmm's check, same and rest | 77 s |
| **total** | **about 25 min** |

`long.sh` is the bug-hunting tier: the simulators at 10,000 TCP seeds and
300 FAT seeds against `coverage/floor-sim.txt` (ReleaseSafe), then the real
kernel losing each of its frames in turn plus seven runs with a misbehaving
client against `coverage/floor-metal.txt` (112 boots, about 5 minutes).

## How it composes today

1. Cloud Claude pushes a `claude/*` branch, with unit tests run.
2. The box merges it after unit tests plus `check.sh` and `same.sh`, and
   pushes. Merges do not wait on the long gates (Steve, 2026-10-05).
3. `gates.sh` and `long.sh` run detached, alongside other work. What they
   find comes back as fixes or as queue items.
4. **An image is built only after both are green on the exact commit**,
   v17 right now.

Step 4 is the one that matters most, and it rests on my discipline, not on
anything a script checks.

## Recommendations

### angry-gopher: test what the commit touched, gate the deploy

1. **Let one command choose the gate from the diff.** `ops/check` could
   read `git diff --name-only` against the last pushed commit and run the
   subsystem gates for the paths touched (chat files: `check_chat`; Elm or
   TS: `check_lynrummy`; zig: `check_zig`; anything else, or many things:
   the whole `ops/check`), printing each skip and its reason. gopher-metal's
   `gates.sh` already does exactly this for its FAT16 judge, and says so
   when it skips. A chat commit would then cost 3 seconds, not 40, without
   anyone having to remember the decision table.
2. **Put the full gate where it pays: before the commit is imaged.** Today
   nothing ties "all of angry-gopher's checks passed" to the commit that
   goes into an image. `ops/check` could leave a verdict (the commit's
   hash, pass or fail) that gopher-metal's image build reads and refuses
   without. Then everyday commits stay cheap and a release cannot skip the
   full set.
3. **Retire the habit that over-tests.** Once 1 and 2 exist, the memories
   that say "`ops/check` before every commit" should say "the diff picks the
   gate; the image demands the full one". I would not change the habit
   before the tooling exists, because the habit is all that guards a release
   today.

### gopher-metal: thorough, and provably about the right code

4. **Stamp the port.** `port.sh` copies angry-gopher's sources and records
   nothing about which commit they came from (I found no stamp). `gates.sh`
   then judges whatever was last ported, and its own header warns of this
   class of mistake: "a gate that skipped this judged yesterday's kernel and
   passed". The port should record angry-gopher's commit and whether its
   tree was dirty, and `gates.sh`, `long.sh` and `chat.py` should print it
   and refuse a mismatch with angry-gopher's HEAD.
5. **Make the release rule a script's, not mine.** `gates.sh` and `long.sh`
   could each write a verdict for the commit they judged (gopher-metal's and
   the ported angry-gopher commit), and `chat.py` could refuse to build an
   image without two passing verdicts for exactly that pair. This is the
   same move as recommendation 2, one repo down.
6. **Move the FAT16 judge to `long.sh`.** It is nine of the 25 minutes, and
   it runs whenever FAT or io code changed, which this week was nearly every
   batch. Prod is FAT32. FAT16 is still covered on every run by `zig build
   test`, the FAT simulator and `tools/check_fat16_images.sh`. Moved, not
   dropped: it would still run before every release, since `long.sh` does.
   That brings a full `gates.sh` to about 16 minutes.
7. **Keep the failing lines.** `gates.sh` keeps only the last two lines of
   metal-vmm's checks, so yesterday's failure needed a rerun to see which
   probe differed. Keeping every `FAIL` line costs nothing.

### metal-vmm: put the explorer's first step in a tier

8. **`sweep.sh` belongs in `long.sh`** once it has been run against
   gopher.elf (box item B2): a fixed range of fault seeds, each one exact
   run, with failures printed as the knobs that repeat them. That is the
   first step toward the explorer, and it is the thorough end of testing
   the machine.
9. **The metal floor keeps rising.** It is 15 of `tcp.zig`'s 18 properties
   today; B4 and B12 bring the last three and the new revival path. Each new
   fault Cloud Claude builds should end as a line on a floor, not as a knob
   nobody runs.

### Across all three

10. **One page that answers "what must pass before X".** This essay is a
    first draft of it. It belongs in gopher-metal's README (orientation lives
    in the README), with a line in each of the other two pointing there.
11. **Budgets, and creep treated as a bug.** Every tier already prints where
    its time goes. Writing the budgets down (merge: about 30 s; quick: 2 min;
    full: under 20 min after recommendation 6; long: under 45 min) turns a
    tier that quietly doubles into something someone notices.

## What I would do first

Recommendations 4 and 5, because they protect the site and cost little:
they make "this image was judged" a fact a script checks rather than
something I remember. Then 1 and 2 together for angry-gopher, which give
back the time you suspect is being over-spent without loosening a release.
Then 6. The rest are small and can ride along with other work.
