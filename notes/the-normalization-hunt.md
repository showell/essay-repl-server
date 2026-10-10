# The normalization hunt: what it found

*2026-10-10, night. Two cold, read-only reviews hunted "quiet
normalizations" (papering over) across the stack: one over gopher-metal and
the metal-vmm judge, one over angry-gopher. 37 findings in all. Below,
triaged by what they could cost, with owners and two yes/no questions at the
end (default yes).*

I verified the two that matter most before writing this: the open redirect
and the retire tool's keep list are both real, as described. The rest are
the reviewers' claims; each will be checked by its own red test before any
fix lands.

## Bucket A: the app (angry-gopher), people's data and safety

These touch real users. Proposed owner: CC, as one queue item, the first two
first.

1. **An open redirect after login** (`login.zig`, `player.zig`
   `sanitizeNext`). `next=/%5Cevil.com` decodes to `/\evil.com`, which
   passes "starts with one slash", and browsers follow it as `//evil.com`.
   A crafted login link sends someone off-site after they sign in. *Verified.*
2. **The retire tool can delete an account you meant to keep**
   (`chat_retire.zig`). It removes every account whose name isn't in the
   keep list: a typo in a keep name (`Stve`) silently matches nothing, and
   an account whose name file is missing is never kept. Only the dry-run
   preview stands between you and it. *Verified.*
3. **A new topic differing only in case merges into the old one** (`chat.zig`
   topic creation): the duplicate check is case-sensitive, the store isn't.
   `Foo` posted beside `foo` appends to `foo.md`, announces a new topic, and
   leaves that topic's last-message record reading the slow way forever.
4. **A send that stored nothing reports success** (`chat.zig`): a missing
   `markdown` field reads as empty and answers 204. The same code trims a
   first line's indentation (a code block becomes a paragraph), and an
   unused `DROP_ON_FLOOR` hook drops any message starting with it.
5. **The fan-out loses durable index entries** (`chat_store.zig`): one
   surface's failure `continue`s past the others for that member, so an
   image index failure also loses the code index entry, permanently.
6. **A channel file's lines are trusted as uids**: a malformed line becomes a
   path the fan-out writes under (`../../x`), or silently drops a member.
7. **Sign-up rewrites a name instead of refusing it** (`Bob<x>` registers as
   `Bobx`; 60 characters cut to 40).
8. **Sessions:** a session `issued` in the future never expires; a signed
   player cookie never expires server-side.
9. **Smaller:** pins and bookmarks fail silently and answer 204; the login
   mirror swallows its write; the transcript decoder accepts a block with no
   id or author; a missing name reads as ""; two URL decoders disagree;
   account ids aren't held to canonical form; `ops/start` can report the old
   server as ready; chat.js reads a bad backlog size as 0; an admin delete
   of an unknown id says nothing; `metalShape` undercounts a path with an
   empty part.

## Bucket B: the judge (metal-vmm), where a pass could be false

Proposed owner: the box. These are the ones that worry me most for the
project's method, because each can make a run green that shouldn't be.

1. **After a power cut, the judge excuses any amount of leftovers**
   (`sound.sh`): "sound but for what a stop leaves" passes any number of
   reclaimed clusters, orphaned names and differing FATs, and the
   floor-and-ceiling comparison (`counted_leak`) never runs on a cut.
   A rename that leaked 500 clusters every time would pass if a cut came
   next. **This is today's "blanket excuse" again, on the cut path.**
2. **A malformed knob is silently off** (metal-vmm `settings.zig`,
   `main.zig`): `WIRE_LOSS=5%` or a typo'd mangle kind parses to "no fault",
   and the run reports ok.
3. **The gates pass with checks skipped**: without passwordless sudo, three
   Linux read-back checks print `SKIPPED` and `GATES: PASS` stands.
4. **The kernel's after-every-request damage check quietly doesn't run** when
   memory is short or the check itself errors on a damaged volume, exactly
   when it matters (`probe/gopher.zig` `checkVolumes`).
5. **A malformed HTTP status reads as "no answer"**, which a fault then
   excuses.
6. **Smaller:** a garbled coverage line is skipped; a run with no coverage
   counts as zero broken; a shape value is cut at `#` (`MARK=msg#1`); setup
   requests' statuses go unchecked; `untouched.py` ignores walk problems;
   `sound.sh` ignores fsck's exit code.

## Bucket C: the kernel (gopher-metal), served code

Proposed owner: the box.

1. **The rest of today's empty-path fix**: `disk_fat` `parentOf` trims
   trailing slashes, `makePath` skips empty parts, the page cache keys `a//x`
   like `a/x`. `io.zig` blocks all of it today, so it's latent, but the
   volume API should agree with itself.
2. **TCP accepts a peer's MSS of 0**: every send then takes the shut-window
   path, a page crawling out a byte per retransmission timeout. A floor
   (Linux uses 88), named and tested.
3. **Smaller:** `consume` clamps a parser's over-consume instead of
   asserting; the config takes a repeated key's last value silently; the
   free count's increase has no ceiling property; the boot drops the
   FAT-copy weighing silently when memory is short; `createFile` ignores
   `.exclusive`; the image build warns and continues without the
   trusted-proxy file.

## What the hunt says about the method

Three observations:

- **The judge had the most per line.** That fits this morning's essay: as
  the kernel gets cleaner, the instruments hold the bugs. B1 is the same
  shape as the blanket excuses fixed this morning, on a path the morning's
  review didn't look at.
- **The app had the most that touch people.** angry-gopher predates the
  exact-accounting work, and its parsing grew up being liberal.
- **Most findings are cheap.** A refusal and a red test each. The open
  redirect is a few lines.

## Questions (default yes)

1. **Queue Bucket A for CC as item 156, the open redirect and the retire
   keep list first?** CC is between items now (155 is done). Each fix red
   first; the smaller ones may batch.
2. **The box takes Buckets B then C, starting with the cut excuse (B1)?** B1
   needs the kernel's counts on the cut path, which exist now (148-152), so
   the excuse can become a comparison like the rest.
