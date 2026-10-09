# The plan after the postmortem

*Written 2026-10-09, evening. It follows
[the postmortem](the-cc-queue-postmortem.md), with your answers on its
eight ideas folded in. One idea is dropped: ranking bugs by cost. The goal
is zero bugs, and we were finding the expensive ones first anyway.*

## The shape of it

**Three things change:**
- **What the judge asks.** "Did anything happen that must never happen?"
  replaces "Is this the same page, except where a fault explains it?"
- **What CC mostly does.** Hunt classes of mistake, read-only, and attack
  the box's work as the box attacks CC's.
- **How we know the judge still works.** A standing set of planted bugs,
  run whenever the judge changes.

Everything else is plumbing to make those cheap.

## 1. v21 (now)

**This is already moving.**
- The pair is gopher-metal `7b2beb3` and angry-gopher `a30a1542`.
- `gates.sh` and then `long.sh` are running detached on the box.
- A cold agent is reviewing the served diff since v20.

**What it carries:**
- the counter that reissued IDs;
- the duplicate-account hole;
- the write cache off at boot, and turned off again after a reset;
- the tie and refused-repair fixes;
- a faster boot.

When both gates pass and the review is clean, I build the image and hand
you the usual steps. CC's 123 fix (a handler error answered with a 500)
stays out: it's still incomplete for requests with a body (127b), so it
goes in v22.

## 2. Two tiers of fault

The faults split by how often they happen on a DigitalOcean droplet:

- **Ordinary:** power loss or reboot, a lost, late or duplicated packet,
  rude and slow clients, the volume detaching. **Judged strictly.** A run
  must meet every rule in section 3, and the page excuses shrink to the few
  a lost connection forces (no answer, or a true prefix of one).
- **Rare:** a sector that rots, a disk that lies about its cache, a refused
  or torn write. **Judged on two things only:** nothing forbidden
  happened, and the kernel said what it saw. The page may differ, and so
  may the volume; silence about damage may not.

Each knob gets its tier in `knobs.zig`, and the report line says which tier
a seed drew. The tier also lets a night choose. For example, ordinary
faults only, to judge the ordinary path at full strictness. Tonight's two
rot failures (128) belong to the rare tier and pass under its rule.

## 3. The judge asks "did anything forbidden happen?"

**The rules, each checkable from outside the guest:**

- **A write the server said was saved survives a power cut.** The
  durability judge already checks this. 125 makes it a shape, so every
  night checks it.
- **No client ever sees another client's data.** Two clients with
  different cookies, each page checked for the other's name.
- **The server never answers a whole request with nothing**, unless the
  connection itself was lost.
- **The boot reaches "serving", or says why it stopped.**
- **After any run, the volume is sound**, or the kernel said it wasn't.
- **The kernel breaks none of its own properties**, outside the rare tier's
  damage properties.

The page comparison stays, but as a diagnosis: when a rule breaks, the
page diff helps find out why. It stops being the verdict that every excuse
argues with. **New excuses stop being added**; each one already there gets
reviewed once against the rules and kept only if a rule needs it.

The cold agent's [questions to ask](questions-to-ask.md) adds two rules
worth taking: no counter at or below an id already handed out, and no
revoked credential that still authenticates. It also says to run the rules
on the unhurt run as well, since a wrong baseline certifies its own bug.

## 4. CC hunts classes, and attacks what's new

**CC's main work becomes class hunts.** Each one starts as a sharp question
about one kind of mistake, then a walk over all the code for every place it
could happen, ending in red tests. "A failure read as absence" was the
first and the best. [The cold agent's list](questions-to-ask.md) seeds
the next ones, starting with its first two:
- **a revoke or delete that fails quietly.** Already one confirmed
  instance: a failed API-key revoke says "revoked" and leaves the key
  working;
- **a reply that promises what isn't written, or written whole.**

**The frenemy loop keeps going, in both directions:**
- **CC attacks each day's box changes**, as in 103, 119 and 122.
- **The box cold-reviews each CC branch before merging**, as in 124 and
  127.

Both stay read-only adversaries: whoever finds the hole writes the red test,
and the owner fixes it.

**Fewer build items for CC.** It builds only what a class hunt or an attack
needs. Knob batches stop unless a class asks for one.

## 5. A standing set of planted bugs

The 10-09 plant proved the method once. It becomes a fixture:
- a small set of kernels, each carrying one deliberate bug;
- one plant per layer: the network (a wrong byte delivered), the disk (a
  write reordered before its flush), the app (a cross-client leak);
- each planted bug lives on a branch that is never merged, and its built
  kernel is kept in `~/nightly/kernels`.

**`plants.sh` runs each kernel for a few hundred seeds.** Every plant must
be caught; and the clean kernel, given the same seeds, must show no
failures. It runs after every change to the judge, the box's or CC's, and
fails loudly if a plant goes uncaught. A too-wide excuse then shows up the
day it's written, rather than in the next cold review.

## 6. Smoother round trips with CC

- **`check-cc.sh` on the box:**
  - fetch CC's branch in all repos;
  - build it in a worktree;
  - run every shape's unhurt run and `plants.sh`;
  - write the result into FEEDBACK.

  It runs when you say CC has pushed. It does in five minutes what cost
  127(h) a round trip today.
- **One feedback file per writer** (`FEEDBACK-box.md`, `FEEDBACK-cc.md`),
  each newest first. Each side reads both and writes only its own, so
  nothing collides on a merge again.
- **Each recipe CC derives but can't run is marked "unrun"** in QUEUE. The
  box runs every unrun recipe before reviewing the code.

## 7. The app's own failures (parked)

Making angry-gopher's `stat` and `read` fail directly, rather than rotting a
sector and hoping the effect reaches the app, is the best tool for the app
layer. You called it outside this effort's scope, so it waits. Class hunts
over the app (section 4) cover much of the same ground by reading.

## 8. The snapshot, explained, and what to do with it

**What it is:**
- metal-vmm boots the kernel once;
- it saves the entire machine at that point: CPU registers, all of memory,
  every device;
- each run of a sweep then starts from that saved machine instead of
  booting again.

**What it buys:**
- **Cheaper runs.** A boot is about 86% of a run's work, so runs get about
  four times cheaper.
- **The ground for steering.** An explorer that wants to try "the same run,
  but drop packet 12 instead of 11" restores the machine from just before
  packet 11 instead of re-running everything up to there. That's the
  "convergence" goal from 10-08: steering the real kernel toward code no
  shape reaches.

The plan is written (`metal-vmm/docs/SNAPSHOT.md`). It's a few days of box
work, all of it delicate KVM state.

**My recommendation is to park it**, and say so. Nights are free while you
sleep, so cheaper runs buy little. Steering is worth less than a judge that
asks the right question, and class hunts are finding more than seeds. Look
again when the plants and the new judge are in, and the nightly's property
count has gone flat.

## Order

1. **Now:** v21. CC finishes 127-128.
2. **Next for the box:** the plants (5) and `check-cc.sh` (6). Both are
   small, and every later step leans on them.
3. **Next for CC:** the first two class hunts (4), from the cold agent's
   list.
4. **Then the box:** the judge's rules and the fault tiers (2, 3), with
   the plants run against each change.
5. **The nightlies** keep running while you sleep. Each one is on the
   newest judge, and its report says how many new properties it reached.
   When that's zero for a few nights in a row, change the shapes, not the
   seed count.
