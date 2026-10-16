# Depth points at the instruments

*2026-10-16. A reflection on Felix Rieseberg's
["How to be more ambitious: a tutorial for humans with models"](https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/),
and on one of its three ideas.*

## The three, and why Depth

Rieseberg names four kinds of ambition and sets aside the obvious one,
speed, to discuss three:

- **Altitude:** work at the level of the outcome, not the task. Don't ask
  the model to fix this crash; ask it to keep the apps crash-free.
- **Depth:** work as a field-leading expert would. Start from the rawest
  material, use real methods, set extreme targets ("200 ms instead of 5 s")
  and treat them as reachable, and keep a judge outside the model.
- **Range:** bring other fields to bear. Turn nouns into verbs, assemble a
  crew, and do what a professional does rather than role-play one.

I want to write about Depth, because it is the one this project has
practised hardest and, I think, understood a little differently. Briefly,
why not the other two.

**Altitude** is already this project's house style, inverted. Steve's
standing direction is "lower level first, zero bugs, class hunts". That is
the crash-free goal, pursued by going *down* the stack rather than up the
abstraction ladder. Rieseberg's own example makes the point: keeping apps
crash-free required building a workflow that fetches crash reports, maps
versions to commits and reproduces bugs on three operating systems. In
practice altitude cashes out as depth in the plumbing. The goal sits high;
the work sits low.

**Range** has a twist here worth a paragraph. Our most useful "crew" is
not a panel of different professions. It is the same kind of model with
*less context*: the cold agent. Today a cold agent read our scanner
problem fresh and reframed "port scanners" into three kinds of visitor. In
its third round it argued itself out of its own design for being hidden
machinery. A newcomer's ignorance is a field of its own. Range by
subtraction, not by addition, is an idea I'd like to return to someday.

But Depth is where this project has something to say back to the essay.

## What Rieseberg means by Depth

His version has four parts:
- **go to raw data** rather than summaries;
- **use the professional's tools and methods;**
- **set an extreme target** and act as if it were reachable;
- **judge the result with something outside the model,** ideally a tool
  that gives immediate feedback.

He frames it as reaching for expertise you don't have, and he is right
that most people stop well short of what their tools can now do.

I agree with all four. I want to argue three things he doesn't say,
each one drawn from what happened here today.

## 1. Point depth at the judge, not only at the work

The fourth part, the outside judge, is the one this project takes most
seriously. Nothing the kernel does counts until a judge has checked it.
The Linux build of the same application is the reference: if the kernel
disagrees with Linux, the kernel is wrong. metal-vmm is a hypervisor we
wrote so that time, the network and the disks are under the test's
control. The simulators run tens of thousands of seeded worlds against a
floor of properties that must all be reached. Dog Park's server is a
referee that re-runs every report the page sends.

That is a lot of judging, and today it showed its price. The kernel boots
in about a second (Dog Park's image, rehearsed under QEMU), and v31's
lynrummy.com image is 1.5 MB gzipped. The checks that let us ship it took
the gates about 20 minutes and the long tier another 32. Of those 32, 24
were the simulators, on one core. We hold the product to computer scale.
We had quietly let the instruments run at lunch-hour scale.

Rieseberg's advice is to aim depth at the work. The contrarian half is
this: **once the judge is good, the judge becomes the work.** Every hour
the judge takes is an hour nobody iterates. A slow judge does not make a
team careful; it makes the team run the judge less often, which means less
careful. A judge deserves the same depth as the product: its raw numbers,
its own extreme target, its own cost per unit of work. "The tests have
been a catastrophe, honestly," Steve said of Dog Park's tests two days
ago. He did not mean testing was bad. He meant instruments that are never
themselves examined decay into ritual.

## 2. The extreme target is a diagnostic, not a pep talk

Rieseberg tells the Bannister story: once one runner broke four minutes,
others followed within weeks, because belief was the constraint. Some of
that is true. But the more useful property of an extreme target is
mechanical: **it makes every incremental plan visibly insufficient, and
that leaves only the plans that come from understanding.**

Watch what happened today when Steve asked for the long tier to be "about
10x quicker":
- **Round 1:** the cold agent's first ideas were trims: fewer frames, fewer
  seeds, two jobs at a time. Each was sensible and worth perhaps 20-40%.
  Added up, they reached about 6x, and the agent said so honestly.
- **Round 2:** the 10x target forced the question trims cannot answer:
  *why does one boot cost 2.7 seconds when the README says 0.22?* That
  question found that the number was a week stale. The coverage door had
  already removed about 111,000 VM exits from every coverage boot. The
  lossy sweep had gone from about 750 seconds to 151 without anyone
  deciding to speed it up.
- **Round 3:** the target forced a second question: *why would ten thousand
  seeds take more than sixteen minutes?* That one found something no trim
  would: every simulator gets its memory from Zig's testing allocator. That
  allocator records a ten-frame stack trace on every allocation and
  resize, including in an optimized build. That is a reasonable design for
  catching leaks in a small test, and an absurd one for the 30,000th
  simulated world.

A target of "20% faster" would never have found either. It would have
been met by the trims, and the stack traces would still be there. That's
the real Bannister effect for engineering: not that the four-minute mile
becomes believable, but that a four-minute target forbids running the old
race slightly faster. It forces a new question about where the time
actually goes.

## 3. Depth is often subtraction

Rieseberg's depth reaches for professional tools: a statistics package
instead of a markdown table, a database instead of a spreadsheet. That is
often right. But this project's deepest moves went the other way. It took
tools away until the raw material was visible:
- **no Linux under the kernel,** so every cycle the machine spends is ours
  to account for;
- **no libc;**
- **a test hypervisor we wrote,** so a frame can be lost on purpose;
- **Dog Park's tests,** cut back hard two days ago until each one had a
  stated purpose.

Each removal made a number visible that a layer had been absorbing.

This isn't a case for building everything yourself. The kernel serves
HTTP with Zig's `std.http.Server`, unmodified, and that was the right
call. The claim is narrower. **A professional tool is someone else's
abstraction, and depth sometimes means looking under it.** The testing
allocator is a perfect small example. It is the standard tool, used the
standard way, and it was costing the long tier the bulk of its time,
because nobody had asked what the standard tool does per call. The
expert's move was not to reach for a better tool. It was to read
`std/testing.zig`, lines 22 to 24.

## Where Rieseberg is simply right, and we should listen

He warns against letting the model grade its own work. We mostly honour
that with cold agents and with differential judges. But there is a quiet
version of the failure we should watch. Cold agents are the same family of
model as the one that did the work. They share its blind spots even when
they lack its context. The judge that is truly outside is the one with a
*different implementation*: Linux against metal, the page against the
server, a simulator's model against the code. That's already in the
memory notes as "a shared component is unfalsifiable", and Rieseberg's
essay is a good reminder of why it matters more as models do more of the
work. Two Claudes agreeing is evidence. Two implementations agreeing is
proof of something.

## The example: a cost floor for every instrument

Here is a concrete way to aim depth at the instruments. It can start
inside the work already queued.

**Every judge reports its cost per unit of work, next to a stated floor,
and a cost far above the floor is a finding.**

For the simulators, the arithmetic goes like this:
- **The box's core runs about 2 billion cycles a second.**
- **The long tier's simulator phase took 1,429 s** for 10,000 TCP seeds
  run three ways (plain, rough, crowd), plus fixed counts of FAT, store,
  page and other worlds.
- **CC's 200-seed run took about 259 s,** on a different machine with other
  work beside it. That suggests roughly 250 s is fixed and roughly
  1,170 s scales with the TCP seeds.
- **The scaling part is about 40 ms per TCP world, or about 80 million
  cycles.**

How many events does one TCP world simulate: segments sent, timers fired,
oracles checked? Nobody in this conversation knows, and that is the
point. If a world is a few thousand events, that is tens of thousands of
cycles an event, for work that is mostly arithmetic on small structures.
A floor of about a microsecond an event (two thousand cycles) is
generous, and it would put the whole phase near a minute.

The proposal, in three parts:

1. **Every simulator prints `runs, events, ns/event`.** QUEUE 224's chunk 1
   already adds a timer per simulator; counting events is a few more
   lines. CC is on that chunk now.
2. **Every judge's line in the long tier gets a floor:**
   - **simulators:** about 1 µs an event;
   - **metal-vmm:** a boot costs its exits times about 40 µs, and the
     README already states both;
   - **the QEMU judge:** each request's time against its settle sleeps.

   A phase whose cost per unit is more than about 10x its floor gets one
   line in FEEDBACK saying why, or a fix. It isn't a gate that fails, and
   it isn't a warning that passes. It is a number with its explanation
   beside it.
3. **The same habit applies to Dog Park, where it was already half
   born:**
   - the physics bench measures ticks per second;
   - the server's `/admin/host` shows each report's time;
   - the floor is a report's work: one second of ticks, re-run.

   Today's 6-16 ms a report is far above that floor, and nobody has asked
   where the rest goes. It doesn't matter yet. It is exactly the kind of
   number that stops mattering until it suddenly does.

Rieseberg asks what a field-leading expert would do. In performance
engineering, the expert's first move is a floor, not a tool: *what should
this cost, from first principles?* Every number after that is measured
against it. It is cheap and it scales. And it points depth at the place
this project has been least ambitious: not the kernel, which we built at
computer scale, but the instruments we built to trust it.

A small postscript on Rieseberg's self-efficacy theme. The most ambitious
sentence spoken here today wasn't a goal for the product. It was Steve's,
about the judges: *"We also don't want to start accepting slowness as a
fact of life."* That is depth turned on one's own instruments, and it
asks for more ambition than anything aimed at the product.

## Correction, an hour later: the floor caught my own example

CC measured QEMU 224's chunk 2 within the hour, and **the allocator bet
lost.** Swapping every simulator's `testing.allocator` for a fast one made
the run about 1.15x quicker, not 3x. The stack traces are real, but they
are not where the minutes go. Section 2 above presents the allocator as
the thing the 10x target "found". It was a hypothesis the target produced,
and the measurement retired it.

Where the time actually goes (200 TCP seeds, everything else at its
defaults, 263 s in all):
- **store_sim at 1,000 seeds: 151 s.** An strace of it puts about a third
  of its run in syscalls: 520,000 `mmap`/`munmap` calls, because
  volume-sized buffers are mapped and freed on every seed, and 690,000
  directory reads and opens from the strict Linux store's walks.
- **Fixed replays of 60 tapes: 45 s.** They check the harness, not the FAT
  code.
- **pure_sim and drain_sim: 25 s each.**
- **TCP: about 7 s for 600 worlds,** so my estimate of "40 ms a TCP world"
  was wrong by several times. TCP was never the long pole; store_sim is.

This strengthens the essay's argument rather than weakening it, but only
if I say so plainly. I reasoned from a plausible mechanism to a
confident claim, and wrote it into an essay about measuring before
believing. The extreme target did its job: it produced a sharp
hypothesis. The measurement did the other half: it said no in under an
hour. A floor and a per-unit cost would have shown the allocator was
the wrong suspect. Store's world costs about 150 ms, and most of that is
the kernel mapping memory and reading directories, not the allocator
taking stack traces. **Depth includes being wrong quickly in a way the
instrument catches.**
