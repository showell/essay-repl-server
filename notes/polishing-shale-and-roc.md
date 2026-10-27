# Two kinds of polish: Shale and the Roc chat, 2026-10-27

Today had two threads that looked unrelated: tidying the Roc chat's idioms, and
fixing small things in Shale as they came up. They turned out to be the same
activity. In both, the visible flaw was rarely the interesting one. The
interesting one was the *class* behind it, and the default that hid it.

## The day's shape

The Roc thread began as an orderly plan. Roc's own parser gave us syntax
trees, and a Shale script hunted them for the constructs Steve's style
replaces:
- magic numbers;
- `if` chains;
- Bools where a tag would say which case;
- lists read by position;
- runs of same-typed arguments.

The hunt produced counts: 139, 15, 21, 14, 68. There were five steps to work
through, one per kind.

The first step took a cold agent 55 minutes. The second agent, writing a
quick gate, spent twenty of its minutes in a sleep loop, waiting for the
first to leave a clean tree. Steve called the delays unacceptable, and they
were. By evening, a step's agent took two to twelve minutes, and the gate
behind each change took under a minute.

Almost none of that speedup came from working harder. It came from finding
three defaults that nobody had chosen.

## Defaults nobody chose

**`roc build` optimizes by default.** Its `--opt` is `speed`, meaning LLVM.
Our build scripts passed no `--opt`, so every test build of the chat was a
release build:
- 5 minutes 21 seconds from cold with the default;
- 0.9 seconds with `--opt=dev`.

Nobody decided that tests should be built for speed. The flag was simply
never written. One `rocOpt` function in roc-webbox's `build.zig` now ties
Roc's mode to Zig's: Debug gets `dev`, a release gets `speed`. That one
change is most of the difference between a 45-minute agent and a 4-minute
one.

**`now()` is the start of the run.** The gate timed each part with
`now() - t0` and printed 0 s for everything, including a part that had just
taken minutes. That was right by Shale's design: `now()` is the time the
host handed in, fixed for the whole run, for determinism. But the docs said
"the wall clock", and an agent writing a timer reads it that way. The fix
was a sentence in two docs: time a program by `run`'s own `ms`.

**`real(".")` kept its dot.** The gate found its sibling repo by taking the
folder above `real(".")`, and got roc-webbox itself, because the path came
back as `.../roc-webbox/.`. I fixed `absolute()` to resolve paths, and Steve
reminded me we're the maintainers: fix small Shale things where they're
found, with no issue to file.

Within the hour, CC showed the dot was the visible edge of something worse.
A *root* spelled `<dir>/.` or through a symlink let a script write into a
read-only mount and read the secrets mount. The mounts' folders were
resolved to their real paths, the root's was not, and the guard compared
two spellings of one folder.

## Instances and classes

That pattern, one surface flaw over a deeper class, is what Steve asked CC
to chase. QUEUE 244 hunted wrong normal forms. A cold agent then read
Shale's last thirty commits and drafted six more classes for QUEUE 245.
CC found a real defect in every one:
- git taking `--output=x.txt` from a caller's value;
- a secret reaching a program by a relative path;
- `edits_all` checking less than it then did;
- a recipe sized past the host's cap;
- parsers passing by forms they didn't expect;
- a job "stopped" before it had made its process group.

Fourteen defects in all, each with a red test, then its fix.

CC's most useful sentence came at the end: **not one of the fourteen was
caught by the gates or the fuzzers.** Each sat in a path that only an
integration test with mounts, symlinks or a real git reaches. Shale's tests
are thorough about Shale the language and thin about Shale the guest on a
messy filesystem. The proposed remedy is a shared fixture host with the
awkward cases built in: a mount inside the root, a symlink to it, a `/`
mount, a secrets folder. It's the kind of investment that finds bugs nobody
has thought of yet, which is a different job from confirming a fix.

The queue tool had a small case of the same class. Archive lines written in
a slightly different format were invisible to its parser, so `queue_next`
handed out 242 a second time, and the item Steve had told CC about moved to
244 mid-flight. "A parser that skips what it doesn't recognise" was then
item E of CC's batch, and CC found three more. The silently skipped line
seems to be one of this codebase's recurring shapes.

## What the Roc idioms turned out to be

The hunt's counts invited a mechanical reading: 14 `if` chains, so 14
`match`es. The agents read it better than that.

- **`if` chains.** Only five of the fourteen became `match`es. Those five
  each tested one value against constants (`Html.escape`, `ZigText.escaped`,
  the header names in `Transcript`). The other nine test different things in
  turn: a route's part, then its tail, then an effect. They are sequences,
  not cases, and a `match` would have hidden that. The hunt finds
  candidates; it doesn't decide them.
- **Bools.** These went further, 21 down to 6, and the renames carried as
  much as the tags. `on : Bool` became `change : [Added, Removed]`, because
  `on: Added` reads wrong. `online` became `presence : [Online, Offline]`,
  and `current` became `record : [Current, Stale]`. A Bool's name usually
  states one case of a question. Choosing a tag forces you to name the
  question.
- **Magic numbers.** Character literals took 139 down to 61, and the ones
  left are honest numbers: minutes, a date algorithm's constants, length
  limits.
- **`roc fmt`.** It sorted the platform's list of hosted functions
  alphabetically. That's a small gift to the docs-point-at-code rule: the
  inventory is now readable in the code itself.

## Where the type system stops

Step 3, records instead of positional lists across the hosted functions,
held the day's one reverted design.

The first attempt at `srcs!` produced a 30-field record, one field per
script. The Roc side was lovely: a misspelled script name became a compile
error. But the record crossed the Roc/Zig seam, where nothing checks Roc's
layout against Zig's extern struct. The 30 names lived in three places, and
a drift would return a struct of the wrong size: silent memory corruption,
the opposite of failing loudly. We reverted it.

The redo was a list of `{ name, src }` records, where an unknown name
crashes as a 500. That's a third of the size, and it keeps the loud failure
by moving it from compile time to run time, where the tests reach it.

The redo exposed a second, quieter bug. Once a hosted call has failed,
every later one answers empty. A page that rendered after a failure would
now crash on the empty list, and the router checked for the crash before
checking the failure it had kept. The real error, a disk read say, would
have been reported as "Roc crashed". Nothing exercises that path today; the
order is now right before anything does.

Twice in this step, I planted a deliberate fault: two same-typed fields
swapped in a Zig struct. Both times the twins or the route tests caught it
within seconds. The seam isn't type-checked, but it is under test, and
until P8 generates the layouts, that's the guarantee it has.

## Questions I'm left with

- **How far does the fixture-host idea reach?** If a shared awkward
  filesystem would have caught all fourteen Shale defects, does the Roc chat
  have an equivalent gap: paths only a hostile store reaches? The chat's
  failure tests inject failures by hand, one route at a time.
- **Should the hunts learn from the agents' judgment?** The `if_chains` hunt
  now reports nine findings that are correct as they are. A hunt that keeps
  reporting accepted code teaches people to skim it. One option is a
  marker, a comment saying "a sequence, not cases". The other is accepting
  that a hunt is a prompt for review, not a gate.
- **Where else is a default doing the deciding?** `--opt=speed` hid for
  weeks because builds still worked; they were just slow. metal-vmm runs its
  unit tests in ReleaseSafe by an explicit 2026-10-08 decision, which is
  different: that one was made. But the audit only covered flags someone
  wrote down. The defaults nobody wrote down don't show up in a grep.
- **How small can a cold agent's unit of work get?** Today's best runs
  shared three things: one deliverable, a test drive first, and a gate fast
  enough to run after every edit. They took two to twelve minutes. The
  55-minute run had a slow gate, two agents in one tree, and a mutant
  printing megabytes. Is there a floor below which the briefing costs more
  than the work?
- **What is Shale for, now?** It started as the bash ban's replacement and
  has become the language our tools, gates and queue are written in. Today
  it was the thing being fixed and the thing doing the fixing, often in the
  same hour. CC found more of its bugs today than the box did in a week of
  using it. Is that because using a tool and auditing it need different
  eyes, or because nobody had asked the question by class before?
