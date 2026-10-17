# Shale, dogfooded

*2026-10-18. The design for Steve's thought experiment, "ban Claude from
running bash and Python, which forces us to dogfood Shale", after six rounds
with cold reviewers: five to build it, and a sixth by an adversary who cared
only about metal. The full design, with every detail settled, is zig-webbox's
`docs/designs/DESIGN-shale-dogfood.md`; this is the version to read.*

## The answer, in one paragraph

**It works, and the evidence says so.** We replayed 80 real consecutive
commands from my own work under the ban: one needed the escape (a Python FAT
reader), eleven were awkward, and the rest were clean, thirty of them simply
Claude Code's own Read, Grep, Edit and Write tools. Two real bash bugs from
those same stretches disappear (`cmd | tail -3 && next` testing tail's exit
code; `setsid … & P=$!` capturing the wrong PID). Linux's Shale becomes a
superset: it runs programs, keeps git, waits on jobs, names folders outside
the repo. **Metal's Shale gains about 400 lines and changes nothing a site
script sees**, behind one builtin and one hook that metal leaves empty, with
no comptime split.

## What I actually do all day

The design started from evidence, not guesses: every Bash call in this long
session, 6,609 of them.

| what | about | what Shale needs |
|---|---|---|
| file edits (1,484 of my 1,680 `python3` calls were multi-line exact replacements, each asserted to occur once) | 2,000 | multi-line strings, and several edits all-or-nothing |
| filtering another program's output (`2>&1 \| grep \| head`, `\| tail`) | 2,800 | run a program; filter and keep lines natively |
| builds and tests (`zig build`, repo scripts, `VAR=value` prefixes) | 1,400 | the same, with a timeout and an environment |
| git | 1,900 | a git layer over running git |
| reading code | 2,600 | nothing: Claude Code's Read and Grep do it better |
| long jobs (`setsid nohup`, waiting on a file, `kill`) | 1,000 | start a job, find it again later, wait, stop it |

What I wanted back from a program was small and specific: **a filtered
piece, by lines, from both ends, long lines cut.** `head -20`, `tail -3`,
`cut -c1-200`. About 2-4 KiB. That became the heart of `run`.

## Who writes Shale

A well-meaning agent who makes mistakes. So the design is not paranoid about
hostile scripts (no defence against a lexer denial of service), but careful
about slips: a mistake must end in a clear stop, never a wrong answer, a
panic, or damage. The lexer is still fuzzed before long strings land, for the
shapes a slip takes (an unclosed long string, a wrong level), because on metal
a lexer bug panics the serving kernel where a clean stop was owed.

## Two rules

**Shale does text itself.** It runs another program only for what that
program alone can give: git's view of a repository, a compiler's verdict, a
server's answer. What happens to the text after is Shale's own: filtering,
slicing, matching, editing. `run` refuses `head`, `sed`, `grep` and the rest
by name (and `bash` and `python3`), so the habit cannot creep back in through
a side door. The text work is then budgeted, deterministic, held identical by
the two engines' gate, and the same on metal.

**Zig for bytes and the world, Shale for thin policy.** Your lean. A builtin
does real work on bytes or touches the outside: regex, the edit transaction,
long strings, running programs, jobs. Prelude Shale is only for a thin layer
whose cost is in the builtins it calls, and that was measured: filtering
16 KiB of output spends 164k steps in the regex and 3k in the loop around it.
The git layer, `must`, and a few text helpers are prelude, Linux-only, so
metal's image never carries them.

## What I will type

An edit and a build check, the shape of a thousand python heredocs:

```
cd ~/showell_repos/dog-park && shale --write <<'SHALE'
edit("src/play/app.zig", {
  {old = [==[const body = try versionText(alloc, ...);]==],
   new = [==[const body = try versionText(alloc, commit, ...);]==]},
})
local r = must(run({"zig", "build", "test"},
  {timeout_ms = 600000, re = "error|FAIL", head = 20, tail = 5}))
print(r.matched_lines, "lines matched; exit", r.code)
SHALE
```

The edits are asserted (each must match exactly once) and applied in
sequence, all or none. The build's exit code is kept: no `PIPESTATUS`. The
output comes back filtered first, then kept from both ends, with a line saying
how much was left out. A commit, a push, the log:

```
commit("", [==[Dog Park's /version ...

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>]==],
  {add = "tracked"})
git_push("")
for c in git_log("", {n = 1}) do print(c.hash, c.subject) end
```

A long job, started in one call and found again in the next:

```
job_start({"./tier3.sh"}, {log = "runs:t3/tier3.log", cwd = "repos:zig-metal-unikernel"})
-- a later call:
local w = job_wait("runs:t3/tier3.log.job", {timeout_ms = 590000})
print(w.ended, w.code)
```

## Mounts, in detail

**The problem.** Shale reads and writes only beneath its root, the folder it
was started in, and that confinement is one of its best features: a script
cannot reach what it was not given. But a day's work lives in several places
at once. A gate's log belongs in a scratch folder, not the repo (untracked
clutter, and a dirty gated checkout). Long jobs keep their folders in
`~/runs`. My memory is under `~/.claude/projects/…`. A change spans two repos
under `~/showell_repos`. With one root, every one of those is either
unreachable or a reason to open the root wide.

**The idea.** A path may begin with a name and a colon, and the name stands
for a folder:

```
read("runs:gates/summary")
edit("memory:MEMORY.md", {...})
replace("repos:dog-park/README.md", text)
run({...}, {secrets = {K = "home:.gopher_api_key"}})
```

**Where the names come from.** One file, `~/.config/shale/mounts`, a line
each:

```
# name = folder
home   = ~
runs   = ~/runs
repos  = ~/showell_repos
memory = ~/.claude/projects/-home-steve-showell-repos-codex-zig-ladder/memory
```

Nothing on the command line: you dislike CLI arguments, and a mount named
once serves every call. A malformed line or a duplicate name stops the run,
naming the line; using a mount that isn't in the file stops it too, listing
the ones that are. Tests point `SHALE_MOUNTS` at a fixture file, never at a
user's.

**The rules inside a mount are the root's rules.** No `..`, no absolute
paths: `runs:../secrets` is refused, exactly as `../secrets` is beneath a
root. `runs:` alone is the mount's top folder; `""` is the root itself. A first
path part containing `:` is always a mount's name, which costs nothing,
because FAT's names (still the rule, on Linux too) never contain one.

**What it is not: a sandbox.** The confinement is lexical. A symlink inside a
mount leads wherever it leads, and `run` can reach anything anyway. Mounts
make paths short and the same in every session; they do not make anything
safe, and the design says so in those words.

**Crossing into a program.** A program knows nothing of mounts: it takes real
operating-system paths. So the line is drawn by what an argument is:

- **`run`'s own path options are Shale paths** (`cwd`, `log`, the files
  `secrets` reads), and the host turns them into real paths.
- **The program's argv is passed exactly as written.** Strings that look
  like mount paths must pass untouched: `master:src/x.zig` to git,
  `::gopher-metal.conf` to mtools, `boot.img@@1048576`, every URL. A guess
  would break them.
- **`real("runs:x/boot.img")` gives a Shale path's real path**, when argv
  needs one.

**In what Shale prints**, paths appear as the script wrote them,
`runs:gates/summary`, never expanded. That is shorter, and it reads the same
across sessions, which matters when a log or a want is read later.

**Why metal never sees any of it.** Round 6's adversary showed that mounts in
the core would put a path producer that can leave the root inside the serving
kernel. So mounts live entirely in the Linux host, behind one hook at the top
of the core's path check. With no hook, which is metal's case, that check is
byte for byte what it is today.

**Deferred:** a session's own scratchpad has a different path each session;
a mount whose value names an environment variable (set by a session-start
hook) will cover it when a need comes. Until then, `runs` holds everything.

## Running programs, honestly

`run` needs a timeout every time (a default is a decision nobody made) and a
choice of what to keep. My own defaults, `head = 20, tail = 5, width = 200`,
live in my user prelude as a helper, not in the language. Its environment
adds to the inherited one. **Secrets never become values:** the host reads the
key file straight into the child's environment, and replaces the key's bytes
in anything the child prints, because `curl -v` echoes its headers.

Building it is real work, about 900 lines: Zig 0.16's own spawn cannot set a
death signal or a new session, and its kill can wait forever. The first step
is a one-minute experiment, how Claude Code ends a Bash call that runs past
its timeout, because "a run never outlives its call" depends on the answer.

**The dry run is a preview, not the everyday safety.** A program escapes any
dry run: `zig build` writes into the tree, and even `git status` rewrites the
index. So a dry run runs no program. It prints every edit's diff and stops at
the first `run`, with a stop that `attempt` cannot catch. I will pass
`--write` on nearly every call that runs a program, and the design says that
plainly rather than pretend otherwise.

## Making the ban real

A remembered rule fails; this one is enforced. A Claude Code hook on every
Bash call, user-wide so cold subagents are held to it too, passes exactly two
things:

- **a `shale` launch:** `cd X && shale --write <<'SHALE'` … `SHALE`, with
  plain words only, so nothing else hides in the command;
- **an escape:** a first line `# want: <tag>: <what Shale lacks>` or
  `# out-of-scope: <tag>: <why it isn't Shale's>`, which runs and is logged
  outside every repo.

I curate that log into `docs/SHALE-WANTS.md`; a tag seen three times goes on
the queue. It fails closed: a missing hook binary refuses rather than lets
everything through. Your litmus is in the rule: a job too big for Shale is a
zig tool in the repo's `tools/`, its compile time earned by being run more
than once, and Python is only a throwaway oracle, through the escape.

**What stays bash, through the escape:** QEMU and KVM gates, `sudo`, ssh to
prod, anything interactive.

## The queue, in Shale

Your addition. The live queue's items run 232, 231, 230, 229, 228, 227,
**223, 224, 225, 226**, 222: an increasing run inside a decreasing one, the
trace of inserts anchored to the wrong neighbour. The fix is structural:
QUEUE.md's grammar written down (sections, items from `**N. ` to the next,
numbers unique across the queue and its archive together, newest first within
a section), and a small library in metal-vmm's own prelude:

- `queue_check()` names every violation with its line;
- `queue_add(section, title, body)` computes the number (one past the highest
  in either file) and inserts it at the top of its section;
- `queue_archive({...})` moves items into the archive as one line each, both
  files or neither;
- `feedback_add` and `feedback_archive` for FEEDBACK.md.

Every changing call checks first and refuses a misordered file rather than
guess; reordering is its own call, with its diff shown. Its tests are Shale
too, on fixtures that include today's real misorder.

## How six rounds changed it

1. **The workload, counted** from my 6,609 commands, and the first shape:
   a host table, `run` first, git over `run`.
2. **The five commonest workflows written out:** the "safe programs" list for
   dry runs was unsound, so a dry run runs no program; output kept by lines
   from both ends; mounts; alternation.
3. **Feasibility in Zig 0.16** (a raw spawn), and **filter before keep**
   (keeping first loses the middle of any long output); secrets; the hook.
4. **Coherence:** names made consistent (`re_` for a regex, `_lines` for a
   file), thin helpers moved to the prelude, measured.
5. **Eighty real commands replayed:** one escape; jobs found again by a
   file; a git layer with ranges and fields; case-insensitive regex and `\b`;
   untracked scripts refused, closing the "write a bash script and run it"
   hole.
6. **The metal adversary**, whose pushback I mostly accepted, because it cost
   Linux no feature: one `host` builtin in place of six, mounts behind a hook,
   no looser name policy (all 1,140 tracked files already pass FAT's), the dry
   run on the existing mechanism, `last` in place of a negative `take`, and a
   regex-cache bug caught before it was written. **Vetoed:** dropping runtime
   preludes (the queue tool needs a repo's prelude), and a few small cuts that
   would have cost Linux a helpful message for a few lines saved.

## For you to decide

- **Adopt the fallback rule** as written in the design (and so the ban).
- **Claude Code's Read, Grep, Edit and Write stay allowed.** The ban is on
  bash and Python; the Edit tool beats a python heredoc for one replacement.
- **The hook goes in user-wide** (`~/.claude/settings.json`), when CC's
  chunks 2-6 have landed: before that there is no Shale to be held to.
- **Hand the rest to CC now.** CC is already building the core pieces
  (QUEUE 232: long strings, `edit`'s list form, `last`, `fail`, regex `|`,
  `\b` and `nocase`). The rest, in order: the seam and `run`; the Linux
  prelude; git; jobs; the hook; the queue tool; the docs. Its own repo earns
  its keep once the seam exists.
