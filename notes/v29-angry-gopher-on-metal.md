# v29, and where angry-gopher on metal stands

*2026-10-13. v29 has served lynrummy.com since 12:43 UTC. The first half
is the release notes, which I never sent you as such: the tags only say
"deployed". The second half is the state of the whole arrangement, and
what is coming. Companions:
[gopher as a platform](gopher-as-a-platform.md),
[three repos, one library](three-repos-one-library.md).*

## v29 release notes

**What it is.** gopher-metal `0519d8c` with angry-gopher `24e0b21a`
(tagged `v29` in both), image sha256 `e9c76c4f…` (the `.img.gz`). The
gates passed in 21 minutes and the long tier in 31. Both chat judges, the
microvm and the droplet-shaped machine, answered all 15 requests as Linux
did. v28 is the way back.

**What you would notice**

- **Big uploads stop costing seconds.** A 100 MB video took 2,017 disk
  requests on v28 and takes 115 now. At prod's ~2 ms per request, the
  pause it causes drops from about 4 s to about a quarter of a second.
  A phone photo goes from 93 requests to 59, and a 10 MB image from 218
  to 26.
  - Two changes did it: requests of up to 1 MiB (they were 64 KiB), and
    the file table written in runs instead of a sector at a time.
  - The kernel now asks each disk its own largest request before using
    1 MiB, so a disk with a smaller limit is not overrun. `/admin/host`
    shows "disk request most 1024 KiB" for both disks.
- **A crash any member could cause is gone.** A stream reconnecting with
  the largest possible `Last-Event-ID` overflowed a counter and panicked
  the machine. The same kind of bug had hit prod once before, with the
  cookie MAC. A new harness now sends 28 extreme numbers to every place a
  request carries one, 532 requests in about a second, and that harness
  caught this bug on v28.
- **Sign-ups:** two accounts an hour per address, down from five.

**Hardening you would not notice**

- **Things that could grow without limit now have limits:**
  - the reading-list cache, at most 32 lists and 8 MiB;
  - the search index, 64 MiB of text;
  - on the Linux host, a request's headers must arrive within 10 s, and
    at most 64 streams are held.
- **Four ways a strange disk could panic the boot** are now refused with
  a message.
- **Smaller fixes:**
  - `Expect: 100-continue` is answered on every host. Metal had answered
    nothing.
  - A cookie marker dated in the future now fails closed.
  - A chat message can no longer plant a fake gallery entry.
  - An upload name that isn't UTF-8 is answered properly.
  - A logout that is refused now clears its cookies.

**Under the hood**

- **No more copying.** The kernel compiles angry-gopher straight from
  its checkout. `port.sh`, the copy-and-sed step every release used to
  begin with, is gone (Phase B).
- **Every gate run names exactly the code it judged,** by the content of
  both applications' files. An edit made during a run keeps no verdict,
  and no image can be built from uncommitted code.
- **The gates include a second app's judge** (below).

**Not in it:** CC's item 188, two fixes for rare disk faults. Both landed
on master today and ride the next release:
- an overwrite reads its commit back before freeing the old copy;
- a disk whose two file tables can't be reconciled at boot refuses writes
  (a polite 503) until they can be.

## angry-gopher on metal, as it stands

**The arrangement.** lynrummy.com is one droplet running no operating
system. Our kernel boots from our own BIOS loader. It speaks to the
network and the two disks itself, through its own TCP and its own FAT.
Inside it runs angry-gopher's server, built from the same source as the
Linux binary, nothing changed. A second droplet runs Caddy for TLS and
forwards over the private network. That is the whole production
footprint.

**What it serves:** all of angry-gopher.
- chat with live streams, uploads and search;
- Lyn Rummy and the other games, docs and the blog;
- the admin pages, including `/admin/backup` (a streamed tar) and
  `/admin/host`.

The judges send the whole route table and long stories to it: 40-step
member sessions, a 71-step capability story, 300 requests to one boot.
Every answer and every file left on disk has to match the Linux build of
the same code, byte for byte. That rule has held since the first
releases, and it is the reason "it works on metal" means something.

**How it is kept honest.** Four layers, cheapest first:
- **Unit tests and simulators:** the FAT, TCP and the page cache each have
  a simulator, with properties held over seeded runs.
- **metal-vmm,** our deterministic hypervisor, where time is ours to jump,
  so timeouts are tested in the machine's own time.
- **The chat judges on QEMU,** including a machine laid out like a
  DigitalOcean droplet, booting through our loader with chat's data on a
  SCSI volume.
- **Real releases on a real droplet.**

**What hurt, and what we learned.** The bugs that reached prod in the
last week were all one kind: arithmetic on a number the client chooses,
which in a checked build is a panic. The answer was not one more fix but a
harness for the whole class (the number-edges harness above). The same
pattern worked twice more:
- **a cold review of a risky change,** with findings confirmed by
  experiment before they count;
- **a hunt by bug class rather than by symptom.**

The time spent waiting on gates for a one-line fix was better spent on
hunts like those.

**What is still thin**

- **Backups are not routine.** `/admin/backup` and `droplet/backup.sh`
  work; nothing runs them on a schedule.
- **Restart-on-failure is built and switched off.** It has never been
  tried on a real droplet.
- **The log is small.** The kernel keeps 64 KiB, a few minutes of
  traffic, and the host page shows the newest 60 lines. CC's next item
  (189) makes it 20 times bigger, timestamps every line, and adds a
  plain-text view an agent can fetch and search: uploads, errors, slow
  requests, counts by route. A pure-text message is logged as its length
  only.
- **Product limits not yet chosen:** no overall cap on accounts, files
  that grow forever (a topic's transcript, its reactions), and no disk
  quota for chat, docs or uploads.
- **gopher-metal's README status table is behind.** Several rows still
  say "on master, not served" for things v29 serves.

## The second app

Dog Park is the second application on the same library, webbox. It
exists to prove that the kernel hosts *an app*, not just angry-gopher:
- an app is a root file exporting its site, plus a list of the files it
  serves;
- the kernel build takes any such app;
- `probe/judge_dogpark.py` runs in every gate, in about 4 seconds,
  holding Dog Park on metal to Dog Park on Linux, request by request and
  file by file.

## What clock ticks will do to metal

Dog Park is about to have critters that move on their own, paced at
least partly by the server. That is the first time the server does
anything **without a request**, and it touches the kernel in several
places:

- **The loop needs a timer the app can ask for.**
  - **How the loop runs now:** it wakes for a network frame, or every 1
    ms on the APIC timer, and spends quiet moments (200 ms with nothing
    arriving) on idle work, such as re-checking the disks.
  - **What an app needs:** a way to say "call me every N ms" (or at a
    given time). The loop then has to schedule that alongside requests,
    streams and idle work, on one core with no threads.
  - **A tick is a turn like a request's:** it must be short, and a slow
    one delays everyone's requests.
- **The machine rests less.** Today the droplet sleeps between frames,
  which is what took the slow tenth of requests from 3-5 ms to 0.5 ms.
  A steady tick keeps waking it, so the tick rate has a real cost. Ticks
  that run only while someone is watching, or only while a critter has
  somewhere to go, would keep most of the benefit.
- **The two hosts must tick alike.** webbox's contract will need a tick
  call that Linux and metal both drive, from the same monotonic clock.
  The judge will have to control time, or "the same answer as Linux"
  becomes a race. metal-vmm was built for exactly this: it tests the
  logic in the machine's time, not wall time.
- **Pushing to the browser becomes the main path.** Server-paced motion
  only shows if the server tells the pages. Chat's streams already work
  on metal, so the mechanism exists; the new part is many small updates
  a second, fanned out to every page subscribed to that part of the
  park. That puts the stream send path and its budgets under a new kind
  of load.
- **Writes get a rhythm.** A critter that moves ten times a second
  cannot write the disk ten times a second. The "kept map" design already
  signed off for Dog Park (memory is the truth, written about once a
  second when something changed) becomes necessary rather than optional.

None of this is hard, but it is the first change to the kernel's
contract with applications since Phase B, and webbox is where it should
be designed. That makes it a good moment for the next section.

## Renaming gopher-metal, and giving webbox its own repo

Today webbox lives inside angry-gopher (`zig-server/src`), and
gopher-metal is named after one of its two apps. Now that the kernel
hosts any webbox app, both names mislead. Some candidates, plainest
first.

**For gopher-metal** (the kernel and its tools):
- **`webbox-metal`.** It says what it is for: webbox apps, on metal.
  Its sibling would be the Linux host, inside webbox. My pick.
- **`zig-droplet-unikernel`.** Says exactly what it is. Long, and it
  names DigitalOcean, which may not stay true.
- **`baremetal-host`** or **`metal-host`.** Short and neutral, but they
  say nothing of what runs on it.

**For the library:** **`webbox`**, the name the code already uses
everywhere. The repo would hold the portable library (`webbox`), the
Linux host (`webbox_linux`) and `host_io`'s two halves.

**metal-vmm** keeps its name. It is a hypervisor that judges any of
this, and it already says so.

**Questions before we do it**

1. **Names.** `webbox` and `webbox-metal`, or others?
2. **History.** Extract webbox with its git history (a filter of
   angry-gopher's `zig-server/src` files that are library, not app), or
   start the new repo fresh? I would keep history; `git log` on a webbox
   file is how we answer "why is it like this".
3. **Where the line falls.** Some files are clearly library (`site`,
   `store`, `signed_cookie`, `body`, `http`) and some clearly app (chat,
   games). A few are in between: the admin pages, `login_throttle`,
   uploads. I would list each file with its side and have you look
   before anything moves.
4. **How the three repos find each other.** Today they are sibling
   checkouts found by relative paths (`../angry-gopher`, `../dog-park`),
   and the gates name code by its content. Staying with siblings is
   simplest, with the verdict id covering webbox's files too. The
   alternative is Zig's package hashes, which pin versions but make
   every library change a two-step dance.
5. **Timing.** CC has item 189 in flight in gopher-metal. A rename in the
   middle of it means rebasing CC's branch across moved files. I would
   rename once 189 lands and CC's queue is empty, then do the webbox
   extraction, then design the tick contract in its new home.
6. **Public or private** on GitHub, for each new repo?
7. **Release notes.** The tags have said only "deployed, image hash".
   Should the next tag carry notes like the first half of this essay,
   or should they live in a file in the repo?
