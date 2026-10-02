# Metal: the next few days

*2026-10-02, morning. Written while v6's gates run.*

Yesterday morning metal had never touched DigitalOcean. Now it serves every
page of the site on metal.lynrummy.com, rests between frames, and keeps chat's
data on a volume. That volume is named by its serial number, so the machine
refuses to run on the wrong one. Most of what got it here was checking: a judge
that compares every answer and every file with Linux, run on a machine shaped
like the droplet.

The next stretch is a different kind of work. Making it run is mostly done.
What's left is making it **safe to depend on**, and making it **easy to
operate**. You named those as the two themes, and I think they're the right
ones. This essay is my map of both, plus some thoughts on how to split the work
between CC, me and you.

## Where we're blind

The biggest problem first: **we can't see what the droplet is doing.**

On this box, every boot writes a serial log. That log is how every bug so far
was found. On the droplet, the log goes to DigitalOcean's console, where only
you can see it, and you can't copy text out of it. When something goes wrong on
the droplet, we'll know only that pages stopped coming back.

That shapes everything below. Before metal holds real data, I think it needs
two ways of being seen:

- **A status page.** This would be a small page metal serves itself, showing:
  - which build it is (the git commit);
  - how long it has been up;
  - which volume it's on, and how full that volume is;
  - how many requests it has answered;
  - its memory high-water mark;
  - its clock, next to prod's.

  None of this is secret, but it shouldn't be public either. The simplest gate
  is angry-gopher's own admin login.
- **The log, kept in memory and served.** The last few hundred KB of what it
  would have printed to the serial port, in a ring buffer, readable from the
  same admin page. Then a problem on the droplet can be read from here, the
  same way a problem in QEMU is read today.

Neither is hard. Both change every later step from "Steve, what does the
console say?" to something I can check myself.

## Reliability: what happens when it breaks

I went through the ways metal can fail and what each one does today. Some of it
is reassuring and some isn't.

**A fatal error halts it for good.** When the kernel hits something it refuses
to continue past, it prints why and halts. Examples: a panic, a disk that won't
read, the wrong volume. In QEMU the judge sees the exit. On a droplet the
machine just stops, and stays stopped until someone restarts it by hand. For a
test site that's fine. For lynrummy.com it means one bad request at 3 a.m.
takes the site down until you wake up.

The fix is to tell two kinds of failure apart:

- **Refusals at boot** should keep halting: the volume is missing, the config
  has a typo. Restarting into the same mistake forever helps nobody, and the
  console says why.
- **Failures while serving** should restart the machine. A panic in the middle
  of a request is almost certainly about that request, and a fresh boot takes
  a few seconds. The log ring above would keep the reason for whoever looks
  later.

**A hang is worse than a crash, and we can't catch one yet.** Metal takes
interrupts only while it rests. If the main loop ever gets stuck without
resting, nothing inside the machine can notice. A crash at least ends. So the
watcher has to be outside: prod checks metal every minute or so, and acts when
it stops answering. What "acts" means is a decision (below). Even just raising
the alarm is a big improvement on finding out from a user.

**The data has no journal.** FAT16 writes in place. Metal orders its writes so
that a crash mid-write loses the newest change rather than corrupting older
ones. That ordering is reasoned about in the code, not tested under real power
loss. Two things would make this much safer:

- **Snapshots.** DigitalOcean can snapshot a volume, which is cheap, and a
  snapshot is the real safety net. Before real data goes on the volume, I'd
  like a snapshot habit: daily if DigitalOcean can schedule it, and always
  before any risky deploy.
- **A check at boot.** Metal could walk its own disk at startup and report
  clusters that are allocated but belong to no file: the litter an interrupted
  write leaves. Report only, not repair. Repair stays a job for Linux, from the
  recovery console.

**A full disk is untested.** The volume is 2 GB, and one upload can be 110 MB.
I believe metal answers "no space" cleanly when the disk is full, but no judge
has ever filled a disk. It should, before real users can.

**Metal serves one request at a time.** It holds many connections, but answers
them one after another. That's been fine for page loads. A 110 MB upload from a
slow phone is the case to measure: does everyone else wait while it arrives? If
so, it can be fixed, but first it needs measuring.

**The clock drifts, unmeasured.** Metal reads the hardware clock at boot and
counts from there; nothing corrects it later. Login cookies expire by that
clock. The status page's "its clock, next to prod's" line would turn this from
a worry into a number.

## Operating it: deploys, migration, maintenance

**Deploys** are already fairly safe. There's only ever one image to upload, and
the volume is named by its serial. Two things remain:

- **A check after every deploy, run from prod.** Pages, a login, the status
  page saying the expected build and the expected volume. I run this by hand
  today; it should be a script that ends in PASS or FAIL.
- **Recording which build is live,** in the repo, so "what's running?" never
  depends on memory.

**Migrating prod's data** is the big one. I'd treat it as a rehearsal that
proves itself before anything moves:

1. **Check the names.** CC is writing `check_volume_tree.py`, which lists
   everything in a directory tree that FAT16 can't hold: names that differ only
   in case, characters FAT forbids, and so on. I run it on a copy of prod's
   data.
2. **Build a volume image from that copy, here.** Nothing on a droplet yet.
3. **Compare the two servers on real data.** Boot metal on the copied volume
   and Linux angry-gopher on the same copy. Ask both the same few hundred
   questions: every conversation, every page, a sample of uploads. Compare the
   answers, the way the judge already does with test data. This is the step
   that actually earns confidence. The judge machinery already does nearly all
   of it, pointed at a different data directory.
4. **Only then a cutover,** and only with a rollback plan written first (next
   section).

**Maintenance:** you said you'd prefer web-based admin, for example deleting
old chat streams. angry-gopher's admin pages already run on metal, since
they're part of the route table. Two things to do:

- Make sure the judge covers the deletes the admin pages do.
- Add the status page and the log to the admin area, so admin becomes one
  place to look.

## The cutover question

This is the decision I'd most like to think through with you, well before it
happens.

Pointing lynrummy.com at metal is one line in prod's Caddy file, so switching
is easy. **Switching back is not**, because of the data. Once metal is the
server people use, new messages and uploads land on the volume. If something
goes wrong a week later and we switch back to Linux, Linux has a week-old copy.
So a rollback means copying the volume's data back to prod first. That's
doable, by attaching the volume to a Linux machine, but it should be written
down and rehearsed, not invented in a hurry.

There's a gentler first step: **cut over only the apps that don't write.**
Safari, Seattle Delivery and the puzzles serve files and keep little or no
data. Caddy could send those to metal and keep chat on Linux. If metal falls
over, Caddy can fail those pages over to Linux automatically, and nothing is
lost, because nothing was written. Chat moves later, once the status page, the
restarts and the snapshots exist. One caveat: some apps keep game state, Lyn
Rummy for instance, so "doesn't write" needs checking app by app.

Splitting the site would undo, for a while, your decision that metal serves the
whole site. I'm raising it as an option for you to decide, not a
recommendation.

## Splitting the work three ways

**CC** has no KVM, can't mount a FAT disk, and can't reach a droplet. What
it's shown it does well:

- adversarial reading (both reviews found real things);
- simulators and host tests;
- design notes;
- pure-Python checkers.

So I'd keep giving it work that is reading, designing and host-testable. For
the themes above:

- the hang and restart design;
- the data-integrity check at boot (pure FAT logic, testable on the host with
  an in-memory disk);
- the rollback runbook;
- reviewing every new piece from the adversary's chair.

One thing would help it: **fixtures.** Real serial logs from droplet boots,
committed to the repo, so it can reason from what the machine actually said.
For the FAT checker, perhaps a listing of prod's data **filenames only**, with
no contents. Those names may include user ids or topic names, so whether
that's acceptable is your call.

**Me:** everything that boots, measures or touches a disk image:

- the gates;
- images;
- trials on the droplet-shaped QEMU;
- measuring from prod;
- the migration rehearsal.

Also merging and keeping the README honest.

**You:** DigitalOcean's console, and the decisions. I'll keep the console
steps short, with no long names to type.

## A possible order

1. **v6 and the survival test** (today): the marker message should still be
   there after the rebuild.
2. **Status page and the log in memory.**
3. **Restart on failure while serving;** keep halting on boot refusals.
4. **Snapshot habit** for the volume (you), and the boot-time disk check.
5. **Full-disk and big-upload tests.**
6. **Migration rehearsal on a copy of prod's data,** ending in the
   Linux-versus-metal comparison.
7. **Cutover design, with rollback,** decided before any of it happens.
8. **FAT32,** when the data approaches 1.5 GB. That's far off at 215 MB.

## What I'd like you to decide, when you're ready

- Whether the status page and log sit behind the admin login, or something
  simpler.
- Whether prod should only watch metal and alert, or also fail traffic over to
  Linux automatically for the apps that don't write.
- Whether cutover is all at once or apps first. And if all at once, how stale
  you'd accept a rollback copy being.
- Whether CC may see a listing of prod's data filenames.
- Snapshots: how often, and how many to keep.

None of these block today's work. Steps 1–3 need no decisions at all.
