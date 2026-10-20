# Shale: what the Zig 0.17 port taught it

*2026-10-20. The Shale changes that came out of the upgrade, and a diagnosis
of why I kept escaping past Shale.*

## What happened

The gate lets me run only a `shale` launch, or an escape that is logged with
a reason. Over two days I escaped **694 times**. I tallied the log with Shale
by the program each escape ran:

| program | escapes |
|---|---|
| `grep` | 195 |
| `sed` (mostly `sed -n a,bp`, reading line ranges) | 120 |
| `git` | 98 |
| `zig build ... \| grep` | about 70 |
| everything else | the rest |

Then I asked of each kind whether Shale already had what I needed.

## The diagnosis

**Mostly it did.** Two kinds of failure, in about equal measure.

**1. Documentation: Shale could do it, and nothing led me there.** The clearest
case is git. Shale's git prelude reads logs, diffs and files at a revision,
commits (message on stdin) and pushes. I escaped to plain `git` 98 times
anyway, because:

- the memory note I read at the start of every session never mentions the
  git prelude;
- the agent doc describes it about 160 lines in.

Per your rule, I treated that as a documentation failure:

- **The agent doc** now opens, right after the launch basics, with **"Before
  you reach for the shell"**: a table from each habit (`sed -n`, `grep -rn`,
  `zig build | grep`, `git log`, `git commit && git push`) to its Shale form.
- **My session memory** carries a short version of that table, and the rule
  itself: avoiding Shale where it already works is a docs bug, not a habit
  to repeat.

**2. Friction: Shale could do it, but only by writing a script each time.**
`grep(p, text)`, `lines` and `walk_all` covered every search and line-range
read, but each quick look meant a heredoc of five lines. A shell one-liner
won every time, and two places I was reading (Zig 0.17's library, the
`~/zig17` worktrees) weren't reachable at all.

## What changed

- **`cookbook/look.shale`:** one launch for both reads.
  - `at=f:40-80,g:5-9` prints line ranges from several files.
  - `find=text in=src,build.zig like=*.zig` prints a literal's lines across
    files and folders. It skips `.git`, `.zig-cache`, `zig-out` and
    `node_modules`, and says when it cuts output short rather than cutting
    silently.
- **`cookbook/zig_build.shale`:** runs a build and prints what matters: the
  Build Summary, each distinct error once with its count, failed tests by
  name, and a failed run's last lines. The full output is kept in a log, so
  a later `look` can find the rest. `zig=zig017:zig` picks the 0.17
  compiler.
- **Launching a script through a mount:** `shale cookbook:look.shale` works
  from any checkout, where before it needed the recipe's full path. A name
  that matches no mount says so. Tested red first, in the CLI tests.
- **Two new mounts:** `zig017` (Zig 0.17.0's install, read-only) and `zig17`
  (the upgrade's worktrees).
- **The wants ledger** (`docs/SHALE-WANTS.md`) has today's six rows,
  including the git one marked as a documentation failure.

I used each new piece for real before committing, and each one caught its own
bugs:

- `zig_build` first passed `--summary` to the step instead of to the build.
- `look` first refused `in=.`, and later walked into `.git`.
- Running doc-check through `zig_build` found two stale paths in the docs,
  one of them in the upgrade notes I'd written that morning.

The commits themselves went through Shale's git prelude, not an escape.

## One question for you

The guard in `run` refuses a program, by path, that git doesn't track. That
catches a script that was just written. It also refuses
`~/zig-0.17.0/zig`, so `zig_build` passes the documented override (`want`) for
a mounted compiler, and **every such build logs a "want"**. That's honest but
noisy.

Should a program under a **read-only** mount (a toolchain's install) pass the
guard without the override? It's a one-line policy change. I left it for you
to decide.

## What's still open from the ledger

- **Skipped tests:** Shale's 15 and the kernel's 1, noted earlier and queued
  for after the cutover.
- **Tree patches:** copying and patching a tree (`git archive | tar`,
  `patch`) for Roc work is still done in bash.
