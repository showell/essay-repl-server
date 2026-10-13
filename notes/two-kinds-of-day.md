# Two kinds of day

*2026-10-13, written at the end of a long day, before the merges.*

Two very different kinds of work ran side by side today. One was Dog Park,
which went from a design doc to a toy that is actually fun. The other was
the metal stack, where the job was renaming, splitting, removing locks,
and finding out which of the code's claims about itself are true. Both
used the same people, the same box and the same habits. The work did not
feel alike, and I think the difference is worth writing down while it is
fresh.

## Dog Park: a hypothesis, built fast enough to be tested by feel

The commit log tells the story with timestamps (UTC).

- **14:25 to 17:38, the doc.** `docs/PHYSICS.md` went through fourteen
  drafts and twelve cold reviews. Each review found something; each of your
  answers became a numbered decision. The leashed dog is the most alpha but
  only its own breed follows. The tiles are not the sphere. The world is
  64 × 64 for now. By the end the doc fixed everything: determinism, the
  wire, the region's size derived from the rules' reaches, and what a page
  does when the server disagrees.
- **17:40 to 18:11, the page split into seams** (CC's plan): a blitter that
  knows nothing about dogs, a pure pointer, and an engine with no DOM.
- **18:45 to 19:03, the physics core**: about twenty minutes, by an agent,
  against the doc. The doc's worked example became a golden test on both
  the native and the wasm build.
- **19:18 to 19:23, the server's protocol. 19:37 to 20:07, the page on the
  wasm.**
- **20:25 to 21:12, you played it.** In under an hour you went through five
  rounds of tuning: faster dogs, longer and shorter reaches, a new first
  layout, a green ring for "dragging", a longer leash, then slower dogs and
  a bigger sphere. Then came the change that made it fun: **dogs move per
  pixel-tick.** For each pixel the leashed dog moves, every awake dog gets
  to move up to a pixel. The pack keeps pace with your hand, and it never
  forms a line.

You said I basically one-shotted it apart from a few tweaks. I want to be
accurate about what that means, because the credit belongs to the three
hours before, not the twenty minutes of building. The pixel-tick change was
about twenty lines in `physics.zig`. It was that small because the cascade
had been designed as functions over one tick's scene: `wishes(scene, most)`
already existed, and the change called it once more inside each internal
step of the drag, with the leashed dog's own step as the limit. The page
needed no change at all. The page and the server run the same Zig, compiled
twice, so a new physics is a new hash and nothing else. CC's test for the
seams was that "the biggest change to the game should touch no page code".
The first real change passed it on the first try.

Two decisions made the speed possible:

- **The spec was argued out before any code existed,** with reviewers who
  had no stake in it. Fourteen drafts feels slow on the afternoon you write
  them. It is much cheaper than fourteen rewrites of a protocol.
- **The game was playable before it was finished.** The eureka moment came
  less than an hour after the first playable build, because the tuning
  loop was a rebuild and a restart, measured in seconds.

The fast day left costs behind, and they are real:

- **The tests pin numbers, not properties.** Twenty-eight Zig tests fail
  now. Nothing broke; each one asserted a starting number (1 px a second, a
  400 px scare box, 250 dogs) that playing replaced within the hour. A test
  that pins a tuning knob in a game whose knobs change hourly is a tax on
  every eureka. The test-speed review you asked for will now also have to
  ask which tests state what the game *is*, and which only state what it
  happened to be at 19:00.
- **The tests were slow in ways nobody chose.** The engine's tests spent 29
  seconds waiting on a real 50 ms timer, for 0.9 seconds of work, and now
  take 0.7. The cold review found worse in the build: the physics hash is
  computed at compile time over 115 KB of source, costing about 4.4 seconds
  in each of four artifacts. That is most of the edit loop, and it is
  incidental, not load-bearing.
- **Pixel-ticks cost time.** A tick went from 21 µs to about 5 ms during a
  fast drag, and replaying 32 ticks can take a tenth of a second. That is
  fine for experimenting, and an easy fix waits for it: a neighbour list per
  tick.
- **The doc is now behind the code.** PHYSICS.md doesn't mention
  pixel-ticks, the new numbers, or the reset on every load. In a project
  this young, the doc is how the next agent and the next reviewer find out
  what the game is, so it has to catch up.
- **One page reload is still unexplained.** The page now stops and writes
  its reason to the console instead of reloading, so the next one will say
  what it was.

## The metal stack: making claims true

The other thread had no eureka moments, and wasn't meant to.

- **gopher-metal became zig-metal-unikernel,** and the web library left
  angry-gopher for its own repo, zig-webbox, keeping its 136-commit history.
- **The application lost its last seven locks.** For each one, an agent
  traced every caller to confirm that nothing outside the one-handler-at-a-
  time rule could reach it, then deleted the lock.
- **HOST.md was rewritten per host,** because some of what it said had
  stopped being true.
- **CC landed the counters (193), the should-fix five (194), a README for a
  stranger (195), an honest account of "battle tested" (196), and the
  checks in four tiers (197).** Writing tier-0 tests for code only the
  emulator had reached, CC found two real bugs. The disk driver read a
  disk's error reports in only one of the two standard formats. The boot
  config accepted volume names written with `+` or `_`.

The legacy work is mostly archaeology. Asked why `request-door` was still
lurking, the answer was that its Linux durability had never landed, though
HOST.md said it had. So we built it. Then, hours later, a Dog Park test log
showed the line "a sync of the data's filesystems failed" over and over: the
sync had failed every single time since it landed. The folder handle was
opened in a mode the sync call refuses. The tests never noticed, because
they replaced the sync with a fake. One test that makes the real call now
stands guard, and the class hunt for other fakes standing in for system
calls is item 198.6 in CC's queue.

That bug is the clearest picture of how the two threads differ:

- **The danger in legacy code is a claim that outlives its truth.** A doc
  says durable, a test says green, a log line says "ok", and none of them
  checks the thing itself. The work is to make each claim answerable:
  counters that make a zero mean zero, tiers that say what each one proves,
  and tests that make the real syscall.
- **The danger in new code is the opposite: a claim made too early.** A
  test pins today's guess, a doc decides what play has not tried yet, and
  every pinned number becomes a small cost on the next experiment.

It's nice that the new project found the legacy bug. Dog Park's scratch
server was the first heavy writer on the Linux host since the durability
work, and it was noisy where the old tests were quiet.

## What was the same

The habits held in both threads, though they were turned to different
settings:

- **Determinism:** in Dog Park it makes replay and agreement free; in the
  metal stack it makes a seed a bug report.
- **Red first:** the sync test, and CC's two bugs.
- **Fail, never warn:** the page that stops instead of reloading is the
  same rule as the kernel that refuses a bad config.
- **One compute job at a time.**
- **Cold reviewers,** used heavily: twelve for one doc, one for the test
  speeds, and one checking every lock.

The settings differ in what counts as done:

- **Legacy code** is done when every claim is checked: the gates, the long
  tier, your go before a release.
- **New code** is done when you laugh at the screen. Everything before that
  is scaffolding for getting there quickly.

Today's lesson for Dog Park, I think, is to keep the scaffolding light on
purpose: test properties rather than knobs, keep builds fast enough that
the tuning loop is seconds, and write the doc as the record of what play
decided rather than a forecast of it.

## Still to do

There is a lot. Dog Park:

- the tests updated for tonight's physics;
- the test-speed fixes, the old routes dropped, and the test essay;
- PHYSICS.md caught up with the code;
- the pixel-tick cost.

The metal stack:

- CC's branch merged once its check finishes;
- item 198, ten parts, now queued for CC;
- v30, with your go.

The packs are dynamic and never in a line, and that's what the day was for.
