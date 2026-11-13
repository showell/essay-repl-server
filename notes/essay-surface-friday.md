# The essay surface, Friday: it shipped

The week's project is done. The server you're reading this on was put in place by `scripts/release.shale` a few minutes ago, the first release that wasn't done by hand. It carries the fix for Thursday's unescaped name.

## The release, as it printed

```text
release: /home/steve/essay-dogfood on 127.0.0.1:9301
running: pid 2484343, unknown (built before release.shale)
   == fast: PASS, 3558 ms, cpu 3457 ms
   == race: PASS, 2740 ms, cpu 1677 ms
   == anchoring: PASS, 12281 ms, cpu 11753 ms
   == audit: PASS, 1350 ms, cpu 602 ms
   == dates: PASS, 1698 ms, cpu 351 ms
   == bench: PASS, 4925 ms, cpu 1636 ms
full check: SAFE TO SHIP, 26562 ms
built bin/essay-surface.new: 92fb48b ..., 926 ms
comments kept: 3 files, 7 comments, in essay-dogfood/releases/2026-11-13T175107Z/comments, each compared
stopped the old server; its log kept
ok: the index, 508 notes, the same as before
ok: all 7 comments from before on their pages and in their files
RELEASED: running 92fb48b on 127.0.0.1:9301; to roll back to unknown: ... rollback=1
```

The release took 27.5 seconds in all. The full check is 26.5 of those. The swap and its checks took under a second.

## What the script does

1. It refuses to touch anything unless exactly one server is running as expected and the checkout is committed.
2. The full check must say SAFE TO SHIP.
3. It builds the new server beside the old one.
4. It copies your comments into `releases/<when>/` and compares the copy file by file, before anything stops.
5. It swaps the servers and keeps the old binary.
6. It checks that the index lists the same notes, that a note renders, and that every comment is on the same block it was on before, both on the page and in its file.
7. If any check fails, it puts the old server back and checks that one the same way.

## A failure it caught that the full check couldn't

On dev, the agent planted a fault in a throwaway copy: a server that looked for comments in the wrong folder. The full check said SAFE TO SHIP, because every check passes the comments folder explicitly. The release caught it ("comment f31eaaa22556 ... missing now") and rolled back. All seven comments came through byte for byte, and the whole failure, rollback and recheck took under a second. That's the case for a release check beyond the full check: it tests the thing as it will really run.

## Two traps it hit

- **A real bug, found on the way:** the server said "listening" before it held its port, so a check could talk to whatever else was on that port. It's fixed.
- **The job trap, again.** In the first trial, a budget stop left the new, unchecked server running and nothing rolled back. That's the fourth time this week. It's the reason a cold agent is changing Shale right now so a stopped run stops the jobs it started. The release script will need one word for it: `keep_on_stop` on the server it restores.

## Calls you may want to unmake

1. A comment must land on the same block, so a release that changes anchoring will roll back and need a look by hand.
2. Each release adds a small `releases/<when>/` folder, and nothing prunes them.
3. Today's rollback target shows as "unknown", because the old binary predates version stamps. Every release from now on records its commit.

## The week, in numbers

| | |
|---|---|
| Go | about 2,500 lines of server and tests, standard library only |
| Shale scripts kept | fast, full, release, bench, audit, dates, the comments smoke test, and a shared prelude |
| A note / the index | 0.13 ms / 0.10 ms median |
| Faults planted | 12 or so, each once; 3 found real problems |
| Releases by hand | 5. By script: 1 so far |

Next comes draft 2 of the book, written from the five journals.
