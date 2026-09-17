# Chat on bare metal: where it stands

*A status report written before a context compaction, 2026-09-17, with a little
reflection at the end. Earlier notes in this thread:
[angry-gopher without Linux](http://143.244.172.148:9100/notes/angry-gopher-without-linux.md)
(the plan) and
[how chat talks](http://143.244.172.148:9100/notes/chat-over-http-and-sse.md)
(the HTTP/SSE design).*

## The one-paragraph version

gopher-metal now serves **angry-gopher's chat** — login, conversations, docs,
reactions, admin, and **live streams** — on a QEMU machine with no operating
system, and every answer is judged byte for byte against the same source
running on Linux. Since the last compaction it stopped crashing, learned the
date and how much memory it has, got a real allocator, stopped letting a silent
client hold the site, got 2.5 times faster on the disk, learned to hold many
connections, and learned to keep a browser tab's three live streams. Nothing
from this work is deployed. What is left before a real browser should touch it
is the **send side** of TCP, **whole-request readiness** (and with it uploads),
and an unexplained slowdown that real hardware should be able to explain.

## Scope, as Steve set it today

- **Chat only.** Lyn Rummy stays on the Linux droplet; its cases are gone from
  the judge. Docs are part of chat.
- **One subsystem at a time, solid**: built, judged, committed, and measured
  with nothing else running on the box.
- **Not a general-purpose kernel.** Chat asks for HTTP in (including SSE),
  files, some pure computation (markdown, JSON, bcrypt), and a clock, entropy
  and a timer. It makes no outbound requests and starts no processes — checked
  in the code. The kernel is shaped to that.
- **State machines, one loop over them.** No threads, no fibers.
- **The kernel only ever handles complete requests.** Buffering is fine at our
  scale.
- **Prod is the last step**, but the machine should be built to be watched.

## What was built, in order

| | what | how it is judged |
|---|---|---|
| 1 | **The stack is 16 MB and measured** — it was 64 KB, 250× less than Linux gives the same code, and `/chat/recent` triple-faulted. The region is painted; the deepest chat page uses 85 KB. | the member story; a guard that stops the machine |
| 2 | **`.` and `..` are not directory entries**, and names are long names, not 8.3 aliases | the member story |
| 3 | **Single-threaded, enforced** by a compile error | the build |
| 4 | **Files have dates** (chat's "recent activity" is made of them) | the Linux VFAT driver reads them within a second |
| 5 | **The kernel owns the RAM; std's allocator runs on it** — through zig's own `root.os.heap.page_allocator` hook, on memory read from the PVH map | QEMU's `-m`; std's four allocator conformance suites; 18,000 allocations with a flat peak |
| 6 | **Every wait is a measured duration**, with `read_timeout_ms` on the volume | two boots, two settings, the answer moves |
| 7 | **The soak** — thousands of requests, every write read back, the Linux driver checks the volume at the end | runs in minutes |
| 8 | **Storage, 2.5× faster**: the FAT in memory, files read and written a run at a time, and chat numbers messages from a count sidecar instead of re-reading the transcript | byte-identical cached/uncached volumes; a read sweep across every sector and cluster edge; Linux reads the run-written files |
| 9 | **Many connections, one request at a time** — a table of 64; a connection is served only once its request head has arrived | 8 clients at once; a silent client holds nobody up |
| 10 | **Streams are described by the app and kept by the host** — the SSE design, option C | Linux unchanged (leak stress clean with streams held open) |
| 11 | **The machine keeps live streams** — a table drained every loop turn, pinged when quiet, ended when the client leaves | a tab's three streams with cross-user events and pings, on both hosts |
| 12 | **Stream lifecycle** — a stream budget (oldest ended to make room), resets noticed, nothing kept per stream | budget of two with three streams; 5 and 25 streams churned, same final heap |

Every row has mutants that fail its gate — around forty today — and the gates
themselves have 70-odd tests of their own.

## The numbers

- **Soak, 2,500 rounds of chat (5,251 requests):** 13.0 min before the storage
  work, 5.1–5.6 min after. Every message read back by the Linux driver every
  time.
- **The kernel's own answer time still grows over a run** — about 7 ms at the
  start and 115 ms near the end. The disk-request count per route is now flat,
  but *each device request* gets slower, and so does the network. Hardware
  virtualization on this droplet changed nothing: it is itself a VM, so KVM here
  is nested, and a device round trip costs about the same either way.
- **Uploads on prod today:** 344 files, 172 MB, the largest 4 MB. The admin
  screen shows ~250 MB, because its counter is a lifetime quota that deleted
  conversations don't give back.

## What is not done

1. **The send side of TCP.** Frames and responses go out without looking at
   the peer's window, nothing is retransmitted, and a client that vanishes
   without a FIN or reset is never noticed. The emulator's generous buffering
   hides all three.
2. **Whole-request readiness.** "Ready" means the head has arrived; it should
   mean the whole request, with `Expect: 100-continue` answered. That is also
   where uploads live: a request heap that can grow, streaming the body to disk
   on both hosts rather than holding up to 101 MiB in memory, and eventually
   FAT32 (FAT16 tops out near 2 GB; each user's quota is 1 GiB).
3. **The slowdown.** Real hardware would separate our code from the emulator.
   Steve is ready to rent a bare-metal box once file I/O and SSE have closure.
4. **Being watched.** A health route answered by the host, and QEMU's watchdog
   device petted by the main loop.
5. **Deploying anything.** Prod still runs angry-gopher `b7a19333`. Waiting for
   Steve: the portable lint, mem_meter's explicit allocator, auth drawing its
   own salt (this one touches password hashing), roots.zig, the count sidecar,
   the stream seam (which changes the SSE wire from chunked to
   connection-delimited), and two small cleanups.
6. **Open decisions:** how many tabs to size the connection table for, and
   whether the old Safari TypeScript tooling gets a sweep. The answer to the
   second is "delete it when you see it; keep the `.ts` files".

## A little reflection

**The judge is the spine.** Every step above was a claim with a check that
could fail, and the checks found more than the code review did. A writer that
zeroed the tail of an overwrite passed every test until a probe wrote from a
sector boundary. A read-splitting loop could never run at all. A host that
pinged on every turn delivered its ping — 15,339 of them in 28 seconds — and
passed the first version of the ping check. And the stream-churn gate found a
single byte: the kernel kept its own config file's text forever, and
`requests = 28` is one byte longer than `requests = 8`.

**Measuring first kept changing the answer.** The bump allocator I set out to
replace was not leaking at all: the application frees in an order it can take
back. The FAT cache I said would flatten the slowdown did not; the curve was the
transcript being re-read on every send, and after that, device latency. KVM
was going to give real numbers and gave the same ones. Each time, the
measurement was cheaper than the wrong fix would have been.

**The seams keep being the same seam.** zig's `page_allocator` hook let std's
allocator run unchanged on the machine's pages. The per-request `Bus` handle
let the application hand a stream to whichever host it is running on. In both
cases the application stayed one source and the host supplied the part that is
about the machine. Steve corrected me on what that principle means: I argued
that a state-machine design would break "one source, two hosts", and it
doesn't — one source never meant an unchanged application.

**Steve's steering made the kernel smaller.** Chat only; state machines in one
loop; complete requests only. Each of those removed something from the list of
things a kernel must do.

**My own misses today**, briefly: I committed an angry-gopher change after
running its tests but not the gate that would have caught a lint failure; I
built kernels while a soak was running and had to throw its timings away;
several of my mutants didn't compile until rewritten; and I overclaimed what the
FAT cache would do before measuring it.
