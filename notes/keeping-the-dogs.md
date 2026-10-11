# Keeping the dogs

*2026-10-11. How Dog Park's server should keep the world on disk, now that
every move rewrites one 250-dog file. A thinking piece: options, trade-offs,
and a recommendation.*

## The premise: memory is the truth

The server holds the world in memory, and that is the truth. The disk exists
for one reason: **so a server upgrade, or a crash, doesn't wipe the world.**
Two things follow from that:

- **The disk can lag.** Losing the last second of a dog's motion in a crash
  is fine. Losing a dog is not.
- **Reads never come from disk while serving.** The world is loaded once, at
  start. After that the disk is write-only.

So the question isn't really "what database". It's three smaller ones: what
the unit of writing is, when to write it, and what makes a half-written state
safe.

## The unit of writing

**A. One file for the world** (today: `dogs.json`, about 15 KB). Simple, and
every move rewrites everything. On metal a write like that costs tens of
milliseconds of disk, on every move. That's the thing to fix.

**B. One file per dog** (`dogs/<id>`, a few bytes).
- A move dirties exactly one record.
- There's no cross-file consistency to worry about, because a dog is only
  ever in one file.
- 250 small files is nothing for FAT.
- Startup reads 250 files. That's fine at this size, slow at 100,000.

**C. One file per tile** (your idea: `tiles/<col>_<row>`, holding the dogs
standing in that tile).
- It matches the shape the game already has: tiles are what pages
  subscribe to, and what a broadcast will be addressed to.
- Later, a huge world could load a tile's dogs from disk only when someone
  subscribes to it, so memory need not hold the whole world.
- **The catch: a dog crossing from tile A to tile B dirties two files.**
  Write B, then crash before A is rewritten, and on restart the dog is in
  both. It needs a rule: each dog record carries a version (a move counter),
  and on load the higher version wins and the stale copy is dropped. That's
  cheap, but it's a real rule with a real test, not a nicety.

**D. A generic key-value store** (any key to any bytes, persisted lazily).
- It's tempting, and the shape is right: an in-memory map, a set of dirty
  keys, a flush.
- But under the "abstraction earns its keep on the second user" doctrine,
  Dog Park is the first user. Chat already has its own stores, shaped by
  what chat needs.
- I'd build the mechanism inside Dog Park with a generic-looking seam: keys
  and bytes in, dirty-tracking inside. Promote it to webbox the day a second
  application wants it.

## When to write: lazy, on purpose

All of B, C and D want the same mechanism, so it's the part to get right:

- **Mark dirty, don't write.** A move updates memory and puts the key in a
  dirty set.
- **Flush a dirty key** when it hasn't been flushed for a second, and always
  when a leash is released (that's when a human thinks "I put it there").
  A drag of 10 seconds then costs about 10 writes, not hundreds.
- **What calls the flush?** There's no timer in webbox yet (the `App.tick`
  question from the last essay). Until there is, each request can flush
  whatever is due on its way out. That works because nothing moves without
  a request today. **The day a wandering dog exists, `App.tick` does the
  flushing too.** This is the second reason for `App.tick`, which is a good
  sign it's the right concept.
- **Upgrades:** on Linux, a stop can flush everything first (a shutdown
  hook). On metal, an upgrade today is a droplet rebuild, effectively a
  power-off, so we lose at most the debounce window: a second of motion.
  That's acceptable by the premise.

## What makes a half-written state safe

- **One record, written whole:** webbox's `store.replace` writes a temporary
  file and renames it over, so a record is old or new, never torn. That
  holds on both hosts.
- **Across records:** only C has this problem (a dog in two tiles), and the
  version rule solves it.
- **The world's shape is checked at load:** a record that doesn't read stops
  the start, naming the file (fail, never warn), as today.

## Recommendation

**Per dog now (B), behind a small "kept map" with dirty-tracking and a
one-second debounce, flushed on release and by the requests passing
through.** It's the simplest thing that makes writes proportional to motion,
it has no cross-file rule, and it's an hour or two.

**Move to per tile (C) when lazy loading pays,** meaning a world bigger than
memory, or startup reading too many files. The kept map's seam makes that a
change of key, plus the version rule, not a rewrite.

**Generic KV (D) when a second application asks.** Chat might, for small
settings. Until then, the kept map lives in Dog Park.

One small thing to decide now, because it's cheap now and annoying later:
**give every dog record a version number from the start**, a counter bumped
on every move. Per-dog storage doesn't need it, but per-tile does, and so
will "which update is newer" once two humans and a wandering dog are all
moving things.
