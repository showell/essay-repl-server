# What the machine taught us

gopher-metal is parked. Chat runs well on Linux, and the reason to go further
wanted hardware we do not have. So this is not a post-mortem — nothing died —
but it is worth writing down what the last stretch actually taught, because
almost none of it was about running without an operating system.

## The seam was already there

The whole thing rested on one line per file: `const Io = std.Io;`. Because
angry-gopher passed every read, write, open and clock through that interface,
moving fourteen thousand lines off Linux meant writing one implementation of it
— not touching a single call site. `std.http.Server` needed nothing at all: it
is built from a reader and a writer, and a reader and a writer is a thing a
machine with no operating system can produce.

That seam was not put there for this. It was there because zig 0.16 asks for
it and because the application had been written honestly. The lesson is not
"add seams everywhere" — it is that a boundary you named for one reason is
worth an order of magnitude when a reason nobody predicted turns up.

## The oracle was the engine

Every hard question had the same shape: *does this machine answer the way Linux
answers, over the same files?* Not "does it look right" — the same bytes, and
afterwards the same tree on disk, read back by Linux's own driver.

That is what made the work tractable at speed. You do not have to know what
correct looks like; you have to be able to ask something that does. And when
one side was hard to reach, the trick was to synthesize a smaller oracle: our
TCP table running as an ordinary Linux program with **Linux's own TCP as the
peer** turned questions that used to need a QEMU boot into questions answered in
twenty-six seconds.

The blind spot is exact and worth carrying: **a differential test cannot see a
mistake both sides make.** Twice in one day a gate was green because neither
side did anything — two 404s agree perfectly. Once, a cache test passed because
the fallback it was supposed to bypass produced the right answer anyway. The
pattern in all three: *the assertion was satisfiable by something other than
the thing being tested.* That question — what else could make this pass? — is
the one I would ask more often.

## The bugs were where the work looked finished

Nothing interesting went wrong in the application, or in FAT16, or in HTTP. The
expensive defects were in the parts that already worked:

- A connection whose FIN had been acknowledged was forgotten before its peer's
  FIN arrived. Correct-looking, and it made every frame slower all day, because
  the peer kept walking a list that only grew.
- A retransmission timeout of one second, which began as an arbitrary 200
  milliseconds, became a second in response to a bug that was fixed in the same
  commit, and then acquired an RFC citation that made it look like a decision.
  The path measures forty microseconds.

Those two are the same story told twice: **a thing that works is not a thing
that is understood**, and the gap between them is invisible until something
measures it. The ladder — one operation, many times, and the cost per tenth must
not climb — existed for exactly this, and it found the close bug by refusing to
accept "it feels slower lately" as a description.

## What I would say about the constants

If there is one habit worth taking out of this, it is writing down where a
number came from. Not what it is — the code says that — but whether it was
measured, copied from a standard, or chosen in a hurry to make a symptom go
away. A constant with a provenance can be argued with. A constant without one
gets defended by the next reader, who assumes somebody knew.

## On not finishing

The machine never ran on real hardware, and now probably will not — the market
for renting bare metal turns out to be thinner than the idea suggests, and the
one datacenter product I would have used shut down this summer. That is a
slightly funny ending: we could build a machine with no operating system faster
than we could rent a machine to run it on.

But the port was always the exercise and not the product. What is left is a TCP
implementation that a real application has used hard — with a measured clock, a
correct close, and fast retransmit — a FAT16 volume that Linux's own driver
agrees with, and a host layer that turns a freestanding target into something
`std` is happy to run on. Those were shaped by a workload that did not care
about them, which is a better forge than any test suite written to make them
pass.

The open question I would keep on the shelf: **what is the next thing that
wants a machine like this?** Not chat — chat is happy where it is. Something
where the absence of an operating system is the point rather than the
challenge, and where the oracle can be built rather than borrowed. When that
turns up, the hard parts are already written.
