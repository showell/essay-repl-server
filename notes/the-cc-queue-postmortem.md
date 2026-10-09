# 128 items later: a postmortem on the CC queue

*Written 2026-10-09, evening, while CC works on 127-128. It draws on
metal-vmm's QUEUE.md, its archive, FEEDBACK.md and CLOUD_WORK.md's history,
and every repo's log since 10-05.*

## The count

In five days the queue handed CC 128 items. Sorted by what they found:

- **About 20 bugs in code that serves lynrummy.com.** Most were in the
  kernel's disk code, and a handful of the most serious were in
  angry-gopher.
- **A larger number of bugs in the test machinery.** These were in
  metal-vmm, the simulators and the SDK.
- **About 25 items that were really about the judge:** an excuse too wide,
  an excuse too narrow, or a judge that never ran.
- **Most of the rest built capability that has found nothing yet:** knobs,
  simulators, report tools.

Of the served-code bugs, nearly all need something to go wrong first: a
disk that refuses or rots, a power cut, a stat call that fails, a flood.
Only one is plainly reachable by ordinary users on an ordinary day: a
flood with one lost ACK reset a real client (24/33/47, shipped in v17).

So your sense is right. True bugs have got harder to find, and the tweaks
keep coming. The question is what that means, and what to do about it.

## What actually found the bugs

This is the most useful table I could make, because it says where to
point effort:

| how | served-code bugs | examples |
|---|---|---|
| reading against a spec | 4 | no flush ever sent (44); a reset turns the cache back on (119, SPC-4); SCSI config offsets (53) |
| hunting one *class* of bug across the code | 5-6 | "failure read as absence": the counter reissues IDs (105), a second account under a member's name (108), an unreadable doc answers 404 (114) |
| simulators of one module | 4 | the flood reset (24/33); a full log ring reads empty (35); a looped FAT chain (36); crash ordering on a cached volume (112) |
| attacks on the box's own fixes | 3-4 | an unreadable folder stops the boot (103); the backup cut short (118) |
| the real kernel under metal-vmm, at about 400,000 seeds | 3-4 | the rotted FAT copy written over the good one; a refused repair stopping the boot; the handler error answered with silence |
| mutation testing (85 mutants) | 0 | it added four checks and found no defect |
| knobs proposed in batches (lists F/H/I/J/K/N) | 0 directly | they made the nightly possible |

The most serious bugs of the whole stretch were the counter reissuing
member IDs and the duplicate account under a member's name, which is a
security bug. Both were in angry-gopher, the mature code, and both were
found by naming a **class** of mistake and walking the code for every
instance of it. No seed could have found them, because the sweep has no
way to make a `stat` fail inside the app.

**Reading and class-hunting beat running.** The nightly's job turned out to
be different: it confirms that the fixes hold, and it catches the rare
interaction (two of its four finds were the box's own fresh mistakes in
FAT healing). That is worth having, but it is not where most bugs came
from.

## Why the tweaks keep coming

Most of today's churn has one shape. The sweep judges a hurt run by
comparing it with the unhurt run, so every legitimate difference needs an
**excuse**:

- a cut-short page;
- a 5xx after a disk fault;
- a lying disk;
- a stop's leftovers;
- the request limit going to another client;
- now rot breaking a property (128).

Every excuse widens what passes, so it earns a review. The review narrows
it. The narrower rule then fails a correct run, and that needs a finer
excuse. Since 10-08, items 109, 117, 120, 122, 124, 127 and 128 have gone
round that loop. The lint went about six rounds; the FAT copies' weighing
broke four times.

The excuse list is growing because **the judge is asking the wrong
question**. "Is this run the same as the unhurt one, except where a fault
explains it?" invites an endless list of explanations. The question we
actually care about is narrower: **"did anything happen that must never
happen?"** For example:

- a write we said was saved is gone after a power cut;
- one user sees another's data;
- the boot stops without saying why;
- the server answers with nothing at all.

Judging by statements like these needs almost no excuses, because a fault
cannot excuse breaking one.

We have half of this already. The coverage properties are statements of
this kind inside the kernel, and the durability judge ("told 303, so it
must be there") is one end to end. Moving the weight of judgment from
"same page" to "nothing forbidden" would shrink sweep.sh's excuses,
rather than grow them every night.

## What we didn't state, and could have

**What a bug costs.** We never wrote down which failures matter for this
site. It's a small games site, and the costly outcomes are few:

1. losing an account or a game;
2. a security hole;
3. the site down until someone notices;
4. a page that is wrong.

Without that list, every difference was treated as equally worth chasing.
A torn sector on a FAT copy got the same attention as a duplicate account.
If each queue item named the outcome it protects, items that protect none
would wait, and most of the knob batches would have.

**How likely each fault is.** The fault model is broader than
DigitalOcean's block storage:

- **Plausible on a droplet:** a power loss or reboot, a lost or slow
  packet, rude clients, a volume going away.
- **Disk lying or rotting under us:** possible in principle, but far rarer.

Most excuses exist to cover the second kind. **Two tiers** would help:
- plausible faults judged strictly, with no excuses at all;
- the disk lying or rotting judged only on "nothing forbidden happened, and
  the kernel noticed".

Tonight's rot failure is that second tier asking to be treated
differently.

**When to stop.** No item said what "done enough" meant, so no area was
ever done. The nightly had no stop rule either. Today you stopped it by
feel, and you were right: the property count had stopped moving. A rule
would make that call for us: **report new properties reached per hour, and
when it's flat for a few hours, the night has nothing more to say.**
Change the inputs instead of adding seeds.

**The order of the goals.** On 10-08 the goal became convergence: steering
the real kernel. Its foundation, the snapshot (`docs/SNAPSHOT.md`), has
been "next for the box" every day since and hasn't been started, because
each night's findings jumped the queue. That may be the right call, but it
was never made as a choice. A stated order would have made it one. For
example:
1. correctness under plausible faults;
2. a judge we trust;
3. convergence.

So would a limit on how many judge-tweak items are open at once.

## How the delegation changed

Four phases, each visible in the queue:

1. **Builder (10-05 to 10-06, items 1-91).** CC built metal-vmm's devices,
   knobs, the simulators and the Store, at high speed. Served-code bugs
   came out of its simulators and its spec reading, not out of what it
   built.
2. **Adversary (10-07, 93-102).** Your explicit shift: "you become the
   adversary." The explorer builds moved to the box. Mutation testing
   found nothing in the kernel, but reviewing the box's explorer found
   real flaws in it.
3. **Adversary that can't run things (10-08, 103-118).** "Build what needs
   no emulator, and anything adversarial; where a claim needs a real boot,
   write the recipe." **This was the highest-yield phase:** 103's attack,
   the lint (105 onward), 112's crash ordering, and 119's reset all came
   from it.
4. **Mutual adversaries (10-09, 119-128).** The box cold-reviews CC's work
   and CC attacks the box's. Quality went up, and so did the loops: most
   of today's items are holes in yesterday's fixes.

The pattern across all four: **CC is strongest reasoning against something
fixed** (a spec, an RFC, a class of mistake, someone else's diff). **It is
weakest deriving facts about a running guest.** The knobs marked "not yet
run on the kernel", 125-126's recipes, and today's request limit of 1 each
cost a round trip, because CC can't boot anything.

## Ideas, in the order I'd take them

1. **Ship what's already fixed.** The two worst bugs found (the counter
   reissuing IDs, and the duplicate account) are fixed on master and **not
   in v20**. So are the boot-stopping folder, the reset re-enabling the
   cache, and WCE=0. We have been finding faster than shipping. A release
   with these is worth more than any item in the queue. It's your go.
2. **Write the outcome list and the fault tiers** (half a page, in
   metal-vmm's README or CLOUD_WORK.md). Ask each new queue item which
   outcome it protects.
3. **Judge by "nothing forbidden".** Make the durability rule and the
   cross-user rule first-class in the sweep, and in the plausible tier,
   stop adding excuses to the page comparison. That should end the
   excuse loop.
4. **Point CC at classes, not features.** "Failure read as absence" was
   the best single item in the queue. Candidates for the next ones:
   - **a request that changes state before it has checked who is asking;**
   - **a reply sent before the write it promises;**
   - **one user's value reaching another's page;**
   - **an error path that leaves a lock, slot or file half-made.**

   Each is a walk over angry-gopher plus the kernel's seams, needs no
   emulator, and ends in red tests.
5. **Let the app's own I/O fail, not just the disk.** The worst bugs lived
   where a `stat` or `read` fails inside angry-gopher. That seam
   (store_sim's) is cheaper and more targeted than rotting sectors and
   hoping the effect climbs up to the app.
6. **Keep a standing set of planted bugs**: one in the network, one on the
   disk, one in the app. Run them whenever the judge changes. Today's
   planted bug proved the method once. Run every time, it would catch a
   too-wide excuse the day it is written, without needing a cold review.
7. **Close CC's round trip.** Add a script on the box that fetches CC's
   branch, builds it, and runs every shape's unhurt run, run the moment CC
   pushes. Today that check took the box five minutes and saved CC a
   day's wrong turn. Also: one feedback file per writer would end the
   merge conflict at the top of FEEDBACK.md every round.
8. **Decide about the snapshot.** Start convergence, or park it in so many
   words. "Next" for four days is neither.

## The short version

The kernel is in decent shape for what we send it. Most of what remains is
our judge arguing with itself. The bugs worth finding now live in classes
of mistake and in the app's failure paths. The fixes worth the most are
already written and waiting for a release.
