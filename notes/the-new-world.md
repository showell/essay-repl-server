# The new world: after the renames

*2026-10-13, evening. What changed today, what it showed, and what comes
next. Written while the gates and the long tier run on the renamed trees,
before CC wakes. Companions: [the renaming plan](renaming-plan.md),
[the client drives](the-client-drives.md),
[dog physics and the report](dog-physics-and-the-report.md).*

## Where things are now

There are six repos where there were five, and two of them have new
names.

| repo | what it is |
|---|---|
| **zig-webbox** | the library: HTTP, cookies, streams, the store, the Linux host. 24 files and their history (136 commits), public |
| **angry-gopher** | an application of zig-webbox: chat, the games, the docs |
| **dog-park** | the other application of zig-webbox |
| **zig-metal-unikernel** | the machine (was gopher-metal): it boots any webbox application with no operating system |
| **metal-vmm** | the deterministic hypervisor that judges the machine |
| **zig-coverage-sdk** | the coverage properties the judges read |

All of them sit side by side in one directory and find each other by path.
The gates name the exact code they judged by its content, now across three
application-side repos instead of two. The old names stay where they were
history: dated queue entries, reviews, essays, and the DigitalOcean droplet,
which is still called gopher-metal and serves lynrummy.com on v29.

## What the move found

I expected the renames to be clerical. Mostly they were. Moving files
from one repo to another took an afternoon; sweeping a name through 400
live lines took a minute of `sed`. What took the time was everything the
old layout had been holding together without saying so. Each one became
visible only because the move broke it:

- **A test reached across the line by path.** One of angry-gopher's tests
  read the library's `store.zig` as text, to check that a list in the app
  matched what the store's function assigns. When the file left, the test
  failed to compile in 21 places at once. Nothing had ever forbidden an app
  file from embedding a library file. Now a lint does, and it fires on the
  old line.
- **A lint quietly stopped seeing half its subject.** The store-absence
  lint, the one that keeps a failed disk read from turning into "the file
  isn't there", still read only angry-gopher's folder. It passed, because
  everything it could see was clean. CC caught it cold, with a planted bug
  in the library that the lint missed.
- **The library's own tests ran nowhere.** They had run as part of
  angry-gopher's test list. After the move, nothing called them. A broken
  library test would have failed in no place a merge looks.
- **A gate had been judging an old disk.** The PC-shaped machine in
  metal-vmm was being handed whatever site image a past manual run had
  left at a default path. Nobody knew, because the image was always close
  enough. The rename's new guard (a boot disk with the old config file's
  name refuses to boot) tripped on it, and the stale image was the first
  thing it caught.
- **Two tests spent two minutes waiting.** The library's tests took 136 s
  of wall time for 4 s of work. Two stream tests sat through 25-second
  keepalive pings while shutting down. They take 12 s now, which is what
  made it cheap to put them in every check.

None of these were bugs in what the site does. They were all places where
the system's checks were weaker than they looked. I think that is the
real yield of a rename: it is an audit nobody would schedule. Every
implicit dependency has to declare itself or break, and the ones that
break quietly are the ones that were already quietly broken.

One mistake was mine. Committing the rename moved the coverage SDK's
commit, and the kernel's build pins that commit exactly, so the first
gates run refused every build. The pin did its job. I should have
remembered it was there.

## The physics, eleven reviews in

The physics doc for Dog Park has now been through ten cold reviews, and
the eleventh is reading draft 11. That is more than I expected, and the
shape of what they found is worth saying.

**The physics settled early.** The cascade, the wishes, the pushes and
jumps, the arithmetic in 256ths: after about the fifth review, the
findings there were small. Review 9 said outright that the tick rule had
no undefined state beyond two small gaps.

**The protocol kept yielding,** and for a while each review found a new
way to get stuck: a tile that left the view and came back was never sent
again; a resend on a slow link looped forever; a page reload forgot a
leash the server had already kept. Each fix was correct, and each draft
grew. Review 9's findings mostly shared one root: an answer didn't say
which request it answered. Draft 10 added a request number and deleted
four rules that had been patching around its absence. The doc got shorter
for the first time, and the next review found fewer protocol problems.

So when a review loop keeps finding the same kind of thing in new places,
the missing piece is probably structural. More patches make the doc
longer and the next review just as productive. I could have seen it two
drafts sooner.

**Your two decisions did the same thing for the tiles.** I had tied the
subscription to the leash, so the physics' inputs depended on the
screen. Decision 13 cut that: the page subscribes for its display,
proactively, and the physics sees only a fixed region around the leashed
dog. Review 10 then found the one place it still leaked, at the moment of
a leash. The answer was the simplest rule available: the page runs no tick
until the region's tiles are held. A separate rule (the stall) disappeared
with it.

**The region's size is derived now,** not felt: the 500 px sphere, plus
how far a cow can move, plus the critter it lands on, plus a jump, plus
half a square. That comes to 930 px, rounded up to 1000. Reviewer 11 is
checking that sum against the cow code itself, which is where a missed
reach would hide.

**The torus is back** (decision 14), deferred properly: a 64 × 64 world
with today's park in the middle, so your testing never meets an edge, and
every edge rule marked as a placeholder for wrap.

What "100% solid" means for a design doc is worth a sentence too. No
review will ever say "solid" and mean nothing is left to find. What I'm
looking for is reviews whose findings are local and cheap: a sentence
here, a missing grammar row there. The doc now ends with nineteen tests
to write first, and those will find the rest. At some point the tests
are better reviewers than another cold read.

## CC, read-only

CC spent the renames on read-only work, and it was some of its best.

- **The census** of every place the old name appeared, with the dangerous
  ones ranked, was my checklist for the rename. Its worst warning, that a
  renamed config file would make prod boot silently on defaults, became
  the boot guard. That guard then caught the stale disk image.
- **Its cold look at the finished move** found the two weakened checks
  above.
- **Your hunch about /admin/host was right, and understated.** The TCP
  counters exist but print only in a log prod never reaches. Disk
  failures aren't counted at all. A device that stops answering hangs the
  machine with no record. The quiet you saw is partly real (a single
  well-behaved peer on a private network) and partly blindness. Item 193
  fixes that, with a red test for each gap.
- **Its seams report on the page code** (192) found the problem in one
  function. `start()` turns pointer events into game meaning, decides the
  drag's rules and builds the frame, all in closures, so nothing in it
  can be tested without a browser. CC's dividing rule is a good one: what
  decides a line on the wire goes in the shared Zig; what decides only
  what you see stays in JS. Its last test of the seams is also good: when
  the dogs' wishes finally arrive, no page file should change.

## What's next

1. **The gates, then the long tier,** on all six repos as they stand. If
   the gates pass, 193 (the counters) and 194 (189's five should-fix
   items) go to CC.
2. **v30,** when you say: 188's disk fixes, 189's host page and log with
   194's fixes, 193's counters, and the renamed machine. It's the first
   image to carry `zig-metal-unikernel.conf`, which the image builder and
   the kernel change together, and the first to boot a release named for
   what it is.
3. **The physics reviews** continue until they turn local, then the tests.
4. **Dog Park's page,** in CC's ten steps, by local agents with you in the
   loop: make the page importable, the drawing contract, the pointer's
   meaning, the engine, the tick clock, then the physics in wasm, then the
   report. The overview becomes a scrolling window on the bigger world.

The code freeze ends when these gates pass.
