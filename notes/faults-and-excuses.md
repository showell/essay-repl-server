# Faults, and what an excuse is

*How metal-vmm hurts the machine on purpose, how a hurt run is judged, and
what "differs (allowed: DISK_REFUSE)" means. Written 2026-10-08, the day the
excuses were narrowed.*

## A fault is the world misbehaving on purpose

gopher-metal's kernel runs inside metal-vmm, and everything outside the kernel
is metal-vmm's to play: the network cable, the client on the other end, the
boot disk, the data volume, the clocks. A **fault** is one of those things
misbehaving in a way the real world sometimes does:

| where | what it can do (each a knob) |
|---|---|
| the wire | lose the guest's frame #n (`WIRE_EAT`), lose one in k, delay every frame |
| the peer's frames | lose them, damage their checksum, send a lying copy first (`PEER_MANGLE`) |
| the client itself | reset the connection, vanish mid-answer, shut its receive window, flood the guest with SYNs, send its request a byte at a time |
| the boot disk | refuse request #n (`DISK_REFUSE`), lose power after write #n, tear a write in half, rot a byte silently, a bad sector |
| the volume | a write cache that lies or loses what wasn't flushed, a failed SYNCHRONIZE, the volume vanishing or going read-only, a transfer that moves half (`VOLUME_SHORT_AT`) |
| the clocks | no RTC, an RTC stuck mid-update, a timer that never counts |

Each fault is a **knob**: an environment setting with a number. Numbers, not
rates: "lose frame 14" can be swept, frame 1, frame 2, … every frame in turn,
which is a proof over all of them rather than a sample. Since this week every
knob's value is checked before the run starts (`checked.zig`): a value that
doesn't mean what it says stops the run instead of quietly meaning "no fault".

**A seed is a whole schedule.** `FAULT_SEED=73` draws a set of knobs from one
number (that seed is a lost frame, two lost peer frames, a damaged one, the
100th disk request refused, a vanishing client, a small flood…). The run
prints the knobs it drew, so it can be repeated with the seed or with the
knobs alone.

**Every run is a function of the kernel and its knobs.** Time inside is
counted, not measured, so the same knobs give the same run byte for byte,
every time. A failure is never "flaky": it is a recipe.

## Judging a hurt run: against an unhurt one

A faulted run is judged against the **unhurt run**: the same kernel, the same
disks, the same request, no faults. Three outcomes:

- **ok** — the same status and the same page. The fault cost time, not the
  answer.
- **differs (allowed: …)** — the answer differs, and a fault that was turned
  can account for the difference. That fault is the **excuse**.
- **FAIL** — the answer differs and nothing turned explains it, or something
  is wrong whatever the page: the machine crashed or hung, a disk was left
  unsound, a coverage property was broken.

## What an excuse is

Some faults **owe the client nothing**. A client that reset its connection or
vanished halfway through cannot be given the rest of the page; a disk that
refused a read cannot have its file served; a machine whose power was cut
answers nothing more. When such a fault is in the schedule and the answer came
out shorter or missing, that is the server behaving correctly in a broken
world, and the sweep says so by naming the fault: `differs (allowed:
PEER_VANISH_AFTER, the peer vanished)`.

Other faults **excuse nothing**. A lost frame, a delay, a damaged frame, a
SYN flood: TCP's whole promise is that these cost time and never the answer.
long.sh holds the kernel to that hardest: for each route it loses the 1st
frame, then the 2nd, and so on through every frame the route sends, and every
one of those runs must serve exactly the unhurt page.

A few excuses are the harness's, not the world's. "The stop cut it": in a
test the machine is told to serve one request and stop two seconds later, so a
client still slow-reading then gets part of its page; the kernel now says so
in its log, and the sweep excuses it. A machine in production never stops.

## Narrowed today: an excuse covers less of the page, never another page

Until today an excuse covered **any** difference. If `DISK_REFUSE` was in the
schedule and the answer differed in any way — a 404, a different page, a 200
where the unhurt run got a redirect — the sweep said "allowed". CC pointed out
that a disk refusal turning into a wrong 200 would pass unseen.

The rule now (your call this afternoon):

- A fault may excuse **no answer at all**, or **the unhurt status with its
  page cut short** (a true prefix of the unhurt page).
- It never excuses **another status**, nor **another page under the same
  status**.
- One exception, decided while doing it: **a 5xx after a fault on the disk or
  the volume.** A server that answers "500, I failed" because its disk failed
  is telling the truth; that is the honest outcome, and only a disk fault can
  excuse it.

**It found a bug within a minute.** Two seeds that refuse a read of the boot
disk got a 200 page of 7,799 bytes where the unhurt one is 13,681: the home
page's handler, unable to read `pages/home.txt`, answered "Home unavailable"
— with status 200. The words were honest; the status said success, so a
cache, a monitor or a sweep counted it as a page served. It answers 500 now
(angry-gopher `0b5239f5`), and those seeds read `differs (allowed:
DISK_REFUSE (a 500))`. Under the old excuses it had been passing.

## The other judge: durability

The sweep has a second mode for the volume, and a different question. Each
seed **posts a chat message** with the power set to fail when the guest stops,
then boots the machine again on what the volume kept and reads the message
back. Being told "303, sent" and then not finding the message is a lost
write. Only two faults excuse that: **a write cache that lies** (it said it
writes through, and didn't) and **a SYNCHRONIZE that failed**. Every other
fault must leave a message that was acknowledged on the disk. (This mode
still needs a request with a real session cookie before it can run against
the real kernel; it's on the list.)

## Why excuses matter so much from here

An excuse is part of the **oracle**: the thing that decides whether a run was
right. Everything ahead (nightly sweeps of thousands of seeds, and then the
explorer steering the real kernel) finds bugs only as well as its oracle
judges. An excuse too broad hides bugs, as today's home page shows. An excuse
too narrow cries wolf, and a sweep that cries wolf gets ignored. So each
excuse should be a claim about the world ("a client that left is owed
nothing"), small enough to be obviously true, and tested both ways:
`sweep_test.sh` now holds a 404 after a refusal and another page after a
reset to FAIL, a 500 after a refusal to pass, and a 500 after a reset to
FAIL.

The honest summary: **faults make the world misbehave; excuses say which
misbehaviour a correct server may pass on to its client, and how.**
Everything else must come out the same.
