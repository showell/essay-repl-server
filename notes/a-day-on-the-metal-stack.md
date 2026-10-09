# A day on the metal stack

*Thursday 2026-10-09, written in the evening while a cold agent revises
`fat16.zig`'s comments. A look back over the day, mostly to remind you of
what is easy to forget.*

## The headline: v21 serves

**v21 went live at 20:11 UTC** (gopher-metal `81d7a35`, angry-gopher
`a30a1542`).
- **The gates and `long.sh` both passed.** `long.sh` covered 10,000 TCP
  seeds plain and rough, the chat judge, the lost-frame sweep, the rough
  peer and 100 volume seeds, with nothing failing.
- **What it serves that v20 didn't:**
  - the volume's write cache is turned off at boot, and again after a reset;
  - FAT copies that already agree are left alone;
  - a refused repair no longer stops the mount;
  - rewriting a file leaves the old version or the new one whole, never a
    mix, and a full disk refuses the rewrite and keeps the old file.
- **One correction worth remembering.** The first summary of v21 I gave you
  was wrong: it credited the release with a TCP fix that was only a test
  change. The commit list caught it while I was writing the README line. The
  habit of building the release note from `git log` is worth keeping.

Afterwards, master fast-forwarded to `next`, and `next` was deleted in both
repos. Five merged local branches, three stale worktrees and four old
angry-gopher branches went too, `calculus-experiment` among them. Every repo
is back to master plus CC's branch.

## The lexicon, briefly

Most of the day's thinking went into words. The ones that stuck:
- **For anything held in memory:** a fact has one **source**. Every other copy
  plays a role: **mirror**, **cache**, **derived** or **hint**, each with its
  own rule for when it disagrees with the source.
- **For RAM:** it holds nothing promised. What it does hold is triaged:
  **reconstruct, retry, forget**.
- **For TCP:** **custody** and **debt** are the bookkeeping, and a segment is
  described with RFC 9293's own adjectives.

You rejected **owner** (it implies a hierarchy), **belief**, **word** and
**settlement**.

What I didn't expect was how directly the words turned into code:
- **The FAT's free count and allocation hint were one field doing two jobs.**
  Naming one *derived* and the other a *hint* split them, and gave the
  kernel two new per-request properties.
- **"No debt without a clock" is now a property** in `tcp.zig`: whatever is
  outstanding has its retransmission timer.
- **The cold comment passes kept the lexicon honest.** Both found comments
  that contradicted the code. The worst said a duplicate ACK "older or
  impossible counts too", which the code didn't do.

## What you may have forgotten

**The judge was waiting out its own mistakes.** Three QEMU checks (login
throttle, retire, session secret) ended their stories without reaching their
boot's request limit. So every judge sat out a 60-second kill, and a guest
that hung in those checks passed. Fixing that saved about 300 seconds per
judge, and made a hang a failure. Two follow-ups:
- **QEMU was syncing the box's disk at every guest flush** (`cache=unsafe`
  fixed it). The cap story dropped from 28 s to 11 s, and from 37 s to 18 s on
  the droplet machine.
- **Every boot in the judge must now end cleanly** at its request limit.

**metal-vmm got its mission restated.** You said it tests the logic of
gopher-metal, and being faithful to wall-clock time is not a goal.
- **Two QEMU checks moved onto it.** The silent client and the slow reader
  now run in metal-vmm's `timeouts.sh`: eight runs in five seconds, where
  QEMU took 26 to 34 seconds of real waiting. Each was shown to go red.
- **The lagging stream stayed on QEMU** because it's a throughput check, not
  a timing one. The chat tab's real 25 s keepalive stayed on QEMU too, as one
  of your "one or two expensive sanity checks".

**metal-vmm is also a storage lab.** A cold reviewer, asked for another use
case, proposed crash-consistency testing for small storage code. Its
reasoning: torn writes, power cuts and lying caches, all set by a seed and
all repeatable. You made that one of its stated roles.
- **Two scripts were renamed.** `flaky.sh` became `refused.sh`, because it
  maps refused disk requests, not flaky tests. `rest.sh` became
  `pc_vs_microvm.sh`.
- **The same review caught real doc errors:**
  - the README still described coverage lines arriving over the serial port;
  - `sweep.sh` refused the default kernel, which the docs never said;
  - `clock.zig` had its clock step wrong by a factor of ten.

**A unit test now fails when it breaks an assertion.** Before today, a broken
`always` in a unit test was only recorded, and the test passed. The SDK's new
`on_broken` hook fails the test, naming the property and its line.
- **It caught a real bug within minutes:** a FAT double free that a test had
  been tolerating. CC's branch had already fixed it.
- **The mutation proof held.** Breaking the RTO-cap property failed two TCP
  tests by name.

**`tcp.zig` reached full line coverage.** With no kcov on the box,
`tools/linecov.py` measures line coverage by setting one-shot breakpoints
from the debug line table. `zig build tcp-coverage` shows 509 of 509 lines
run. Coverage was already 99.6%; the gap was a segment arriving ahead of
the handshake's ACK.

**The comment pass on `tcp.zig` found two real bugs:**
- **A duplicate-ACK counter could overflow its byte.** A peer repeating one
  ACK about 256 times would panic the kernel. That's low risk behind Caddy,
  but it was a real path to halting the site.
- **A SYN-ACK sent again was still timed**, against Karn's rule. The first
  round-trip estimate came out as the whole 200 ms timeout.

Both are fixed red first, and both are v22 material.

**CC's last stretch was its best.** It finished 132 through 138 and then
stopped, as you asked, with an empty queue.
- **The early review blocked the merge.** The FAT read-back (H1) could copy
  a rejected FAT copy or rot into memory. CC fixed it by deciding only the one
  entry in doubt, and the first fix's machinery went with it.
- **`check-cc.sh` paid for itself on its first run.** It caught a script
  committed without its executable bit, then a planted-bug patch made stale
  by my own comment pass.
- **The test suite is faster.** The whole suite went from 530 s at v21 to
  194 s on the merge.

**Smaller things worth a line:**
- **B29 is recorded:** stray resets after a reader that paused. It needs a
  frame trace to tell whether the peer or the guest is at fault.
- **A balloon became a decision:** a 64 MiB reserve for small writes, now
  judged in bytes.
- **The nightly found nothing in 46,000 seeds** except injected rot, which
  the kernel correctly flagged.

## Two lessons about working together

**Warn before spending wall time.** I ran the whole test suite and a
10-minute property sweep without a word while you were at the keyboard. The
sweep was also the wrong configuration: its floor is calibrated for 10,000
seeds, not 100. "Wall time isn't free when I'm awake" is a rule, not a
preference.

**Wait for the cold agent.** On `tcp.zig` I worked alongside the comment
agent, in different files. Nothing collided, but my coverage tool measured a
binary built before the agent's edits and printed shifted line numbers. That
looked exactly like the clobbering you worried about. On `fat16.zig`, it waits.

## What's next

`fat16.zig` becomes `disk_fat.zig`, and its directory-entry format moves to
a file of its own: that's the one clean seam, since FAT16 and FAT32 differ
only in a few switches. Then come the review's smaller FAT findings, red
first, and coverage the way `tcp.zig` got it.

Waiting for when you're idle:
- the full-size `check-cc.sh` and plants run;
- a full gates and `long.sh` run to measure the new totals;
- B29.
