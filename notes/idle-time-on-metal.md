# Idle time on metal

*2026-10-10, late night. A brainstorm, not a plan: how gopher-metal could
spend the idle time chat has in abundance, under the same contract as a
request. Nothing here is decided.*

## The short answer

**It's easy, because the kernel already does it once.** The main loop
(`probe/gopher.zig`) serves at most one thing per turn: the oldest ready
request, or else a connection gone quiet. When there's nothing to serve, it
takes **the console's turn**: it writes a bounded slice of the log backlog,
"a little at a time so a request that arrives meanwhile waits at most this
much", and only then rests (`interrupts.rest()`). Idle work generalizes that
one branch, from "the console's turn" to "the next idle task's turn".

The hard part isn't the hook. It's **writing tasks that stop and resume**,
since there are no threads: each task is a state machine that does one
bounded slice and says whether it has more.

## A sketch of the mechanism

```zig
/// One piece of work for the idle time. `step` does one bounded slice and
/// says whether there's more; its state lives in `self`, never on the stack.
pub const Task = struct {
    name: []const u8,
    step: *const fn (self: *Task, ctx: *Ctx) Outcome,
    // ... the task's own state follows, in its own struct
};
pub const Outcome = enum { more, done };
```

- **The queue:** a small fixed array of tasks, round-robin. The host owns it.
  The application adds tasks through the router contract, as it hands the
  host a kept stream today (`bus.keep`).
- **The turn:** in the loop's "nothing to serve" branch, after the console:
  one `step` of the next task, then back to the top. A request that arrives
  meanwhile waits for at most one step.
- **A step looks like a request with no client:** the request heap, reset
  after it; its writes flushed before the next turn, as a response's are;
  its errors logged and the task dropped, never the machine stopped.
- **When the queue is empty, the loop rests as today.** No new timers, no
  power cost.

### What counts as idle

The simplest rule is "nothing ready this turn": a step runs whenever the
loop would otherwise rest. Chat is bursty, so a slightly better rule costs
one comparison: **idle once nothing has arrived for, say, 200 ms.** Then a
step never lands in the middle of a burst (someone typing, a page loading
its assets), and the worst case, a request waiting for one step, happens
only to the first request after a lull.

### The contract, the same shape as a request's

- **A step is bounded:** a budget of disk requests (the honest unit on this
  volume, at ~5.8 ms each), say 16, so ~100 ms. Time is checked too: a
  step past its budget breaks a property ("an idle step overran"), loud in
  coverage builds and counted on `/admin/host` in production, as a slow
  handler would be.
- **A step owns nothing between steps but its task's state**, in the
  long-lived heap, sized when the task is queued.
- **A task is restartable.** If the machine stops mid-task, the next boot
  queues it again from the start, or from where it saved itself.
- **`/admin/host` lists the tasks:** each one's name, steps taken, when it
  last ran, done or not, and the longest step.

## Tasks it could run

**The host's (gopher-metal):**
- **The volume check, sliced.** `Volume.check` walks every directory and
  the FAT. Today it runs at boot, or after a request in coverage builds.
  Sliced, production could check itself continuously and put any damage on
  `/admin/host`. That's the best fit: it's the judge's own question, asked
  in production.
- **A scrub:** read every sector of the volume over a day, to find rot
  before a request does.
- **Fragmentation:** how many files' chains are non-contiguous, as a fact on
  `/admin/host`; later, moving a file to make it contiguous, if it ever
  matters (it costs reads at ~5.8 ms per hop).
- **Warming the page cache** after boot: read the transcripts people will
  open, so their first visit is warm.

**The application's (angry-gopher):**
- **Search's index build**, if building at boot gets annoying: the fallback
  Steve named, with the index answering "not ready yet" until it's built.
- **Compaction of an append log**, when the key/value store exists.
- **The retire tool's work**, which is long and stoppable already.
- **Recomputing derived sidecars** (`.count`) and checking them against the
  transcripts.

## What it costs, and what it risks

- **Latency:** the first request after a lull waits for at most one step.
  With a 200 ms quiet rule and a ~100 ms step, nobody notices.
- **Complexity is in the tasks, not the mechanism.** A resumable walk of a
  directory tree is real work to get right (the `Lister` already resumes
  within a directory; across directories it needs an explicit stack). Each
  task deserves its own tests, including stop-and-resume at every step.
- **Writes during idle time are new.** Today only a request writes, and the
  judge reasons about a run as a sequence of requests. A task that writes
  (compaction, a fragmentation fix) needs the same fault testing a request
  gets. A task that only reads (check, scrub, warm) needs almost none, so
  read-only tasks are where I'd start.
- **The judge learns one thing:** metal-vmm controls time, so a sweep can
  include idle windows on purpose, run the tasks in them, and hold steps to
  their budget. Steps then interleave with requests deterministically, so a
  task that breaks a request shows up as a seed.
- **Linux too, eventually.** The other host serves one handler at a time
  already; an idle step taken under the same turn when its queue is empty
  is the same mechanism. Or idle tasks stay metal-only and the Linux host
  ignores them, which is fine while it's stopped.

## The smallest first version

1. The queue, the turn in the loop with the 200 ms quiet rule, and the
   `/admin/host` lines. A step budget checked by the clock.
2. **One read-only task: the volume check, sliced**, with its findings on
   `/admin/host`. It's useful on day one, and it's the hardest read-only
   task (a resumable tree walk), so it proves the contract.
3. metal-vmm sweeps with idle windows, holding every step to its budget.

Roughly: a day for the mechanism and its tests, more for the sliced check,
most of that in making the walk resumable.
