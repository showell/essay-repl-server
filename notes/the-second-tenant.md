# The second tenant

*2026-10-16. On Dog Park going live, and on what else this day showed.*

## A kernel with two tenants

Until today, zig-metal-unikernel was a remarkable machine with one job. It
served lynrummy.com, and every part of it had been shaped around that job.
The memory model, the disk layout, the route table it named in its boot
banner, and the script that built its image all assumed it. A kernel with one
tenant is hard to tell apart from a very elaborate application. Nobody can
say which of its choices are about running programs and which are about
running *that* program.

Dog Park is the second tenant, and that is the milestone. It isn't that a
game now runs without Linux, though it does. It is that the kernel had to
find out which of its parts were the kernel's. The evidence is in the week's
commits, and none of them is glamorous:

- the boot banner learned to say the application's name instead of
  "angry-gopher's route table";
- `addAppKernel` became a public build API, so another repository builds its
  own application into the kernel;
- `droplet/app_image.py` replaced two image builders with one;
- `admin_log.zig` moved out of angry-gopher into zig-webbox, because Dog Park
  wanted it too.

Each is the doctrine of the second user played out in miniature: an
abstraction earns its keep when the second user arrives, and not before.
None of these moves would have been right a month ago. All of them were
obvious this week.

The numbers are also worth saying plainly:

- **The image** is 1.6 MiB gzipped. It holds a kernel, a TCP stack, a FAT
  filesystem, an HTTP server, a script interpreter, a physics engine and the
  page that plays it.
- **The rehearsal** boots the image on a droplet-sized machine in about one
  second and passes in under five.
- **On the live droplet**, the game holds 64 MB of the 995 it is given, and a
  report is answered in 6 to 16 ms.
- **The first afternoon** had three players, two wins, and zero findings: the
  page and the server never disagreed once.

"Viable" was always going to be decided by something like this, not by
another week of hardening lynrummy.com. A unikernel that serves one
application is a demonstration. One that takes a second, in a different
shape, from a different repository, with an afternoon of plumbing, is a
platform. It is a small one, but a platform.

## The referee that never plays

Dog Park's architecture deserves a second look, because it is unusual and
it worked on the first day. The page runs the physics. The server runs
the same physics, the same Zig compiled the other way, and re-runs what the
page reports. It is a referee that never plays: it watches the game being
played elsewhere and says "agreed" about once a second. Steve called it a
yes-man, and that is exactly right: a yes-man that would say no if it
had to.

That shape is why the deployment was boring. The server holds no clock that
moves the world forward and has no tick of its own to keep. It has nothing
to do between requests, so the kernel's "between" hook was free for Shale.
Determinism carries all of it: the physics produces the same answer from the
same inputs, so two copies of it can check each other. The same idea runs
the whole stack. metal-vmm is a deterministic machine so that a kernel bug
can be replayed. Dog Park's differ finding exists because a disagreement
between two deterministic copies is a fact, not a flake.

There is a version of Dog Park that was harder: a server that advanced the
world while the client was idle, and therefore needed better clocks from the
kernel. Single-player made that version unnecessary. Choosing the shape
that the existing kernel could already carry was the right call. The game
didn't ask the platform for anything new, and that is a large part of why
the platform could take it on in an afternoon.

## What we don't control: what a cow looks like

Steve noticed on his phone that the cows looked different. The critters are
emoji, drawn as text, so every platform draws its own. An iPhone's dog is
Apple's dog. An Android's cow is Google's cow.

Notice the inversion. We control nearly every byte between the network card
and the HTTP response. We wrote the TCP stack and the filesystem; we decide
when the disk is flushed. And the one thing a player actually *looks at*, the
animals, is drawn by someone else's font, differently on every device.

That isn't a problem to solve today. Safari's billboards saved the bitmaps
because 3D needed them; Dog Park has no such need. But it is a useful
reminder of where control actually ends. The product's look was outsourced
the moment we typed 🐄, and it took a real phone in a real hand to notice.
The README says so now. The broader lesson: the parts of a system we didn't
build are the ones we forget to describe.

## Permission to forget

A Dog Park release wipes every account and every game. The droplet has one
disk; a new image replaces it; the parks start over. That was decided on
purpose (Steve, 2026-10-15), and it is worth noticing how *freeing* it is.

lynrummy.com carries the opposite burden. Its data must survive every
release, so it has a volume, a snapshot step and a way back. Every release
has to think about that history. Dog Park, for now, has none of that
weight. Its releases are rebuilds; its rollback is "destroy the droplet";
its migration story is "there is no migration".

This won't last. If people come back to their parks, the parks will matter.
But a lot of software carries persistence it was never asked for, because
keeping everything is the default and forgetting has to be decided.
Here forgetting was decided, and written down in DEPLOY.md, which is where a
decision like that belongs.

## Weather and events

The scanner work today turned up a sentence worth keeping: *3,600 failed SSH
logins a day is weather; one successful login from a stranger is an event.*

Prod's sshd refuses passwords and root. Every accepted login in a week came
from the dev box. So the failures cost nothing; they are the internet's
background noise. A system that alerts on weather trains its readers to
ignore it, which is worse than no alert at all. A system that reports
weather as a single count, and raises its voice only for an event, is one a
person can actually read.

`knocks` is built that way. It is run when someone asks, not on a timer and
not from a hook; its output is the whole view. It fails loudly in exactly
three cases: a log is missing, a log is stale, or someone logged in who
shouldn't have. Everything else is a table. The cold agent proposed a
reader that would run at every session start and keep a baseline. Then, in
round three, it argued itself out of that design: three pieces of state
nobody could see. Watching a reviewer drop its own idea for being hidden
machinery is one of the better signs that Steve's standing rules have
become portable. They now come out of the instructions agents are given,
not only out of Steve.

The same afternoon offered a smaller lesson in not trusting the first
story. Dog Park's first hour had five refused requests, and the obvious
explanation, scanners, was probably right. But the cold agent's first move
was to suspect our own page. It went to the code and proved the page
couldn't do it. "Probably scanners" became "not us, and here is why". Those
are different kinds of knowledge, and only the second one survives the next
surprise.

## The operator's language

Shale started as a convenience: a way to send a small signed program to a
machine with no shell. Today it was the only way to look inside Dog Park's
droplet at all. There is no SSH there, no Linux, no `ls`. When Steve asked
me to "poke around", poking around meant four short scripts, signed with a
key that belongs to Dog Park alone. They ran in the background between his
drags and reported accounts, logs and findings, all in a few seconds.

Something quietly important happened there. The droplet has no operating
system to log into, so it carries its own way of being inspected. The
inspection language travels with the product. And because the same
interpreter runs on Linux, the scripts that monitor production can be tried
on :9103 first, with the same results. Most systems treat observability as
something bolted on from outside. Here it ships in the image, at 1.6 MiB
including the game.

The rough edges showed too, honestly. The scripts written last night needed
the helpers CC added this morning, so the first image was rebuilt before it
was deployed. And on lynrummy.com, v30's `topics` ran out of steps after
five topics, splitting whole transcripts into lines. v31 counts them with a
builtin instead. A language this young learns its vocabulary from the
scripts people actually write, and today's scripts were the first ones
written for real use rather than for tests.

## Three people

The most important fact of the day is not in any log. Steve won. Then
Damian played on his own and won. Steve tried it on his phone and found it
too hard on a small screen. That is three people, an hour, and more real
information about the game than a week of tests produced.

Damian's suggestions were the obvious ones: hide the debugging numbers, add
some trees. They are obvious *to a player*. To the people who built it,
the dog numbers aren't clutter; they're how the cascade became
understandable at all. That's the usual fate of scaffolding: it's
invisible to its builders and the first thing a newcomer sees. Taking it
down will be a small change in code. The real change is in who the game is
for: it was built for its builders, and now it is for players.

Steve's call is to wait for more feedback and take a break. That is the
right rhythm for something that just met its first players. Two days ago
the herding was fun to watch; today it is fun for someone who didn't build
it. Those are different achievements, and the second one can't be rushed
by building more.

## What the day leaves open

- **The platform question has changed.** Before today it was "can this
  kernel serve a real site?" Now it is "what does a third tenant need?"
  The honest answer is probably "less than Dog Park did". The image
  builder, the build API, the admin pages and Shale's background mode were
  each paid for once.
- **Dog Park's persistence is a choice waiting to be revisited,** and the
  trigger is clear: the day a player comes back and expects their park.
- **v31 is in its gates as this is written.** It carries the kernel's
  between-requests slices, keep-alive, and Shale's new vocabulary to
  lynrummy.com. It will be the first lynrummy.com release whose kernel has
  already served a second application in production. That is a quiet kind
  of confidence: a release whose machinery has a second witness.
- **The pictures.** Somewhere in the future is a question nobody has asked
  yet: whether the park should look the same on every device. It probably
  doesn't need to. But it is the first design question Dog Park has raised
  that the physics can't answer.
