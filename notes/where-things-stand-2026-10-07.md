# Where things stand, 2026-10-07 evening

*One page for the morning: the four repos, what's open and whose it is, and
tomorrow's release.*

## The short version

- **Production:** v18 serves. The slow afternoon was DigitalOcean's storage,
  and it's gone.
- **Everything is on `master`** (`main` for the SDK), pushed and green. The
  one side branch is angry-gopher's `request-door`, held until v20 is
  ported.
- **The cloud session is paused** until the box says otherwise.
- **v20 ships tomorrow** after one morning of gates.

## The four repos

| repo | `master` | what it holds now |
|---|---|---|
| **angry-gopher** (the app) | `e4d68654` | `store.has` answers "no" only for what isn't there; case-folding fixed; one handler at a time on Linux; **`limits.zig`**, every bound on a request in one file; a check holding the Caddyfile to it |
| **gopher-metal** (the kernel) | `6ad8ea8` | folders held in memory; B21, B22; a path through a file answers like Linux; the head buffer from `limits.zig`; **`STORE.md`, `HOST.md`, `MUTATION.md`**; the Store judge |
| **zig-coverage-sdk** | `8444388` | the seed explorer (tape, named choices, aimed flips), its review fixes, a thinner guidance stream |
| **metal-vmm** | `9194808` | the queue, now **127 lines of what's open**, with everything else in `QUEUE-ARCHIVE.md` |

## What the day settled

- **The Store is one seam.** angry-gopher's own `store.zig` is the
  interface. `zig build store-judge` runs it over Linux and over metal's real
  stack against a model: all eleven operations, 200 seeds, ten seconds.
  Getting it green found and fixed four places where Linux and metal
  answered differently, and one leftover temporary file both left behind.
- **The host is a contract** (`HOST.md`): one handler at a time on both
  hosts, durability as the host's promise, one source of truth for limits.
- **Limits live in one file.** Writing it down found Caddy refusing documents
  between 1.0 and 1.05 MB that the app allows.
- **The request door** is built and green on its branch: every handler takes
  a narrow `Request`, and a lint keeps it that way.
- **Tests that notice:** CC planted 85 bugs; the tests catch 63. `fat16`
  catches the fewest (8 of 16), and every survivor is diagnosed.
- **Gates are surgical** (your rule today): quick checks while developing,
  gates on a release morning.

## Tomorrow: v20

1. **The gates, first thing:** port, `gates.sh`, `long.sh`, about an hour,
   on `master`'s pair.
2. **The image**, and your go.
3. **Your steps**, as before, plus one: install angry-gopher's
   `deploy/Caddyfile` on prod and reload Caddy (`deploy/README.md` has the
   commands), for the `1MiB` cap.

What v20 changes on the site: chat sends about five times fewer disk
requests (a slow storage day hurts a fifth as much); a disk error no longer
reads as "absent" anywhere (legacy cookies refuse, retirement sweeps
nothing); an unreadable config halts rather than serving misconfigured;
documents up to 1 MiB get through Caddy. What it doesn't change: nothing
you'd see on a normal day.

## Open, and whose

**The box:**
- the request door to `master` once v20 is ported, then its stage 2;
- the app's locks deleted (one handler at a time made them idle);
- durability on Linux, and the Bus contract and its simulator (`HOST.md`'s
  owed list);
- B16 (the SDK in the release verdict) and B23 (a 16 KB-plus head gets no
  answer on metal-vmm);
- the older list in the queue.

**The cloud session (paused):** 98 (the benchmark's fair denominator,
possibly landing as it stops), 99 (attack today's merged work), 102 (the
rough peers reaching their four TCP properties by design, so they can go
back on the metal floor), 101 (proposals).

**You:** backups (the `doctl` snapshot cron needs your API token); whether
and when CC resumes; the Caddy reload with v20.

## The rhythm from here

A release a day for a few days, each one's note separating what changes the
served code from tests and docs, and a cold review of each release's diff
drafting the next one's list. Gates on release mornings; quick checks
otherwise.
