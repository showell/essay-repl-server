# Checks that stopped checking

*2026-10-17, written while v33's gates run. Open-ended: what today's docs
cleanup turned up, the shape underneath it, and a few things I'd change.*

## What turned up

The docs audit was meant to be about prose. Fixing its findings kept running
into checks that had quietly stopped doing their job. In order of discovery:

- **angry-gopher's `ops/check_zig` was red for about fourteen hours** (from
  zig-webbox `ce00a9c` at 01:54 UTC to my fix at 15:46). The sleep work added
  `wake.zig` and `linux_fetch.zig` to zig-webbox, and CC's 230 embedded Shale's
  prelude. Three lints that live in angry-gopher (the webbox-library lint, the
  portable lint's partition test, the request-edges list) didn't know those
  files, and a router test still called `between` the old way. zig-webbox's own
  suite was green the whole time. Nobody ran angry-gopher's.
- **The markdown gate passed without its corpus.** `gold.jsonl`, about 2,584
  real messages and the bulk of the coverage, wasn't on this box. The harness
  printed "cannot read" and passed on the 32 hand-written cases. It had
  probably been like that since the move from the laptop.
- **`host_fetch`'s test never ran.** It was missing from `webbox.zig`'s
  `test {}` block, a list kept by hand.
- **`tools/fresh.sh` said every metal-vmm script judges fresh binaries.** Two
  of them, `pair.sh` and `sleeps.sh`, ran whatever `gopher.elf` was on disk. On
  its first run, the check I added caught a stale `gopher.elf` of my own.
- **The Safari downloads answered 404 on lynrummy.com** since the cutover, and
  nothing would ever have said so. No check asked for them on metal.
- **I wrote "2026-10-18" all day on the 17th**, in about twenty places, and no
  tool could notice.

One check went the other way: **the coverage-SDK pin fired at once** when the
audit's doc-only commits moved the SDK's HEAD. The kernel and Dog Park both
refused to build. It was right to refuse (it can't tell a doc commit from a
code commit), but it was also the only loud failure of the day, and it fired
on a change that couldn't matter.

## Two shapes

These are two failures that look opposite.

**A check that is absent but looks present.** The markdown gate, the test
block, `fresh.sh`'s promise, the downloads. Each of them existed, ran or was
believed to run, and said nothing. The doctrine we already have, "fail, never
warn", covers the markdown gate exactly: it printed something and passed.
The others are subtler. Nothing printed at all, because the check was never
pointed at the thing.

**A check that is present but asks the wrong question.** The pin asks "is the
SDK checkout at exactly this commit?" when the question we care about is "is
the SDK code I'm compiling the code that was verified?" Those agree on code
commits and disagree on doc commits, and because they disagree loudly, the
cost is only friction. That makes it the safer of the two failures. But
friction trains people to pass `-Dcoverage-sdk-unpinned`, and a flag used
casually is a check switched off.

## The common cause: the check lives somewhere else

Look at where each silent check sat compared with the change that broke it.

| broke | the change was in | the check was in | ran on that change? |
|---|---|---|---|
| webbox-library lint | zig-webbox | angry-gopher | no |
| partition test, request edges | zig-webbox | angry-gopher | no |
| router's `between` test | zig-webbox | angry-gopher | no |
| `host_fetch`'s test | zig-webbox | zig-webbox, a hand list | no (not in the list) |
| `fresh.sh`'s promise | metal-vmm scripts | a comment | nothing to run |
| downloads | the cutover | nowhere | — |

Every one is a check that lives away from the change: in another repo, in a
hand-kept list, or in prose. A check catches a change only if something runs
it on that change, and our setup runs checks by repo. zig-webbox has three
consumers, and its gate runs none of their checks. The consumers' gates run
only when the consumer changes.

I made this worse without meaning to. The memory rule "when angry-gopher's
ops/check runs" says it runs when angry-gopher itself changed, before a
deploy, or after a fundamental kernel change. That rule was about **compute**:
don't spend eight minutes on a check that can't have changed. But a webbox
change *can* break angry-gopher, and the rule's wording let me skip it all
day. The rule was right about cost and wrong about scope. Two more things
meant nobody else caught it either:
- the pre-commit hook isn't installed in this clone (`core.hooksPath` is
  unset);
- DEPLOY.md's release steps never run angry-gopher's `ops/check` at all.
  The gates run the chat judges, which compare metal with Linux. Lints and
  angry-gopher's unit tests are not in them.

So the release recipe today would have shipped with angry-gopher's own
checks red. v33 is fine only because I happened to run `check_zig` on the 232
merge an hour before launching it.

## Hand lists are where the rot starts

Three of today's failures were hand-kept lists that went stale when a file
was added: the test block, the lint's partition, the edge-sites table. One of
them is worth looking at closely, because it is half right. The partition
test *derives* the set of files outside the route table's reach, then pins
it with a literal. The derivation is good. The pin is what fired, and it was
right to. A new file outside the set is a decision someone should make. It
fired, but in a repo nobody was testing.

The lesson isn't "never pin". A pin that fires is doing its job. The lesson
is that **a pin about webbox's files belongs in webbox**, where the change
that moves it is made.

## What I'd change

In order of value per hour:

1. **Run angry-gopher's `ops/check_zig` in the release recipe**, as DEPLOY.md
   step 1b, before `release-check.sh`. It's eight minutes against a release
   that already takes thirty, and it is the only check of angry-gopher's own
   code on the way to the site. This is a one-line doc change, and I'd make it
   now.
2. **Move the library's shape checks into zig-webbox.** The webbox-library
   lint and the portable partition describe webbox's files and webbox's rules.
   They live in angry-gopher only because that's where the library was born.
   Moved, they run on every webbox change, by whoever makes it, CC included.
   angry-gopher keeps the half that is about itself: that it imports the
   library by name and never by path.
3. **Derive `webbox.zig`'s test block, or check it.** A test that walks
   `webbox.zig`'s `pub const` imports and fails when one is missing from the
   `test {}` block. That's ten lines, and it would have caught `host_fetch`.
   The audit listed it as a candidate. It's Shale-shaped, too.
4. **Make the coverage pin a content pin.** Pin a hash of the SDK's
   `src/` and `build.zig` instead of its HEAD commit. A doc commit then passes,
   a code commit still stops the build, and nobody learns to reach for
   `-Dcoverage-sdk-unpinned`. This is a design change to a check you asked
   for (2026-10-10), so it's yours to say yes or no to.
5. **A consumer smoke check in zig-webbox's gate:** `zig build` (not the
   tests) of angry-gopher, dog-park and the Observatory against the working
   tree. It would have caught the router's `between` call only if the call
   were in non-test code, so it is weaker than 1 and 2. But it costs seconds
   once warm, and it catches the commonest break: a changed signature.

The one I'm unsure about is whether CC's branch work should run consumer
checks. CC changes zig-webbox constantly. If the shape checks move to webbox
(2), CC gets them for free. Running angry-gopher's whole `check_zig` on every
CC chunk would be 8 minutes of CC's time per chunk for breaks that are rare.
I'd do 2 and 5 and leave it there.

## Where the eight minutes go

A side question from the same investigation: `ops/check_zig` takes about
eight minutes, and most of it is zig-webbox's own suite (7 m 16 s alone, 410
tests). `ops/list` called it "~20s", and `ops/check`, the "pre-commit gate",
runs it, so the pre-commit gate is a nine-minute gate. A hook that slow gets
uninstalled, and ours isn't installed.

I don't yet know where webbox's seven minutes go. My guess is Shale's fuzz
and property runs: 232 added a lexer property of 200,000 sources and 20,000
run-fuzz rounds. That would fit the rule that a test must earn its time
(Steve, 2026-10-14: "a 9-min test must be 500x more insightful than a 1-s
one"). The honest next step is to measure per-test time, not to guess. If the
fuzz is most of it, the obvious split is the one zig-metal-unikernel already
has: a sampled fuzz in the fast tier, the full one in the long tier.

## A coda on v33

The same question applies to the release running now. v33 is the first time
the kernel sleeps for real on a droplet: it halts until a packet, the app's
own next wake, or ten seconds, where v32 woke every millisecond. The way it
could fail is the silent way. A missed wake would mean a request waits up to
ten seconds and is then answered correctly, so every functional check would
still pass. What would tell us is the `Sleeps` counters on `/admin/host`
(a missed wake, a sleep the timer ended with a frame already waiting, is its own count), and the time a request takes when
it arrives after a long quiet stretch. So after the restore I'll leave the
site idle for a minute, then time a request, before calling it served.

That's the general move this essay keeps arriving at. For each check, ask
what change it is supposed to catch, and whether anything runs it when that
change is made.
