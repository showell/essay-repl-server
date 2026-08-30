# The corpus methodology is mostly scaffolding, and the scaffolding is where the bugs live

*2026-08-30, written after a day in which four separate measurements came back
wrong, misleading, or empty — and all four failed in the scaffolding around the
measurement rather than in the measurement itself. Steve asked for the
bone-headed decisions documented and a clean start. This is the first half.*

## The evidence is today

Not archaeology. One day, one small change — adding an arc tangent to a foreword
chapter — and this happened:

**A two-arm corpus run answered a question it could not be asked.** 28 minutes of
box time, 0 stage moves, 0 verdict moves, 582 of 582 byte-identical. Nothing in
that corpus cites the chapter I changed. The zeroes meant the sweep never touched
the change. I know only because a presence check predicted 615 programs and got
614.

**I then explained that failure with a mechanism I had not checked**, wrote it
into `PRIORITIES.md`, and repeated it in a PR body: "the corpus cannot see a
foreword change, by design." False. 491 of its 614 programs carry a `cites` line,
220 of them citing `Foreword chapter Console`, and cited content is materialised
into the emitted zig — `corpus/aesgcm256.zig:31` defines `fn Maybe(comptime a_:
type)`. Steve said it sounded odd. It was.

**Three hand-written orchestration scripts produced three fresh bugs.**
`bitcast.sh` had a shell syntax error that killed the run after its useful work.
`bitcast_baseline.sh` compared a two-line string with `-gt` and reported an
absence check as failed when it had passed. My own `atan_twoarm.sh` had a
hard-coded sandbox path that was wrong the moment `sandbox.sh` chose a different
timestamp.

**A batch runner died silently partway and I read it as progress.**
`bare_expected.py` aborts the whole batch when one stem fails to resolve, so the
verification I most needed — the one proving my new test's failure branch
actually fires — never ran. The log simply stopped. For fourteen minutes I
reported it as "still running."

**And the watch that was supposed to tell me was watching itself.** `until !
pgrep -f 'bare_expected.py device-math'` matches the argv of the shell running
it. BOX.md documents this exact trap, in those words. I typed it anyway, three
times.

Five failures. Zero of them in `codexir`, the plug, the emitter, or
`two_arm_diff.py`. All five in the apparatus.

## What is actually good, stated first

`two_arm_diff.py` is right, and the redesign should keep it whole. It compares
two sandboxes directly rather than against a bank; it reads both verdicts *and*
emitted text and explains in its own docstring why the second is the sharper
question; it diffs disagreeing files on disk so the report says what moved. It
handles population differences correctly. It caught the population anomaly today.
116 lines, no ceremony.

`sandbox.sh` is right about its core idea: a fresh tree carries no gitignored
artifacts, which is the failure it exists to prevent, and its MANIFEST records
what a worktree was cut from while `--list` answers from git because the two
legitimately diverge.

The bank's provenance work is right and hard-won — `current_tools` derives
identity from four inputs because zig bakes the build directory into every
binary, and `current_base` refuses to report the literal string "HEAD" as a
branch name.

None of that is the problem. The problem is everything around it.

## The bone-headed decisions

### 1. The corpus is a non-recursive glob guarded by a comment that is no longer true

    names = sorted(TESTS.glob('*.codex'))
    # ... codexir resolves no cites, so every such call comes out as an
    # undefined name ... Until there is a resolver, the honest corpus is the
    # self-contained programs.

There is a resolver. It is imported at line 46 of the same file and called at
line 131. The `--all` flag's help text, 27 lines above the stale comment, says
*"cites are resolved now, so every program is in scope."* The file contradicts
itself across three points and the glob still reflects the oldest of them.

The cost is not abstract. `codex/test/` has 1,027 usable programs outside
`errors/`; the corpus uses 614. Excluded: `ops/` (43), which is **where our own
PR evidence lives**. `real-bitcast-f64` and `real-int-conversions` — the tests we
wrote to demonstrate PRs 100 and 105 — have never been in our corpus. Neither has
`real-saturating-finite`, the control we cite in every PR body as the thing that
proves the rig.

We have been certifying changes with a sweep that structurally cannot see the
tests we wrote to demonstrate them.

### 2. Orchestration is a hand-written script PAIR per change

`dup.sh` + `dup_baseline.sh`. `bitcast.sh` + `bitcast_baseline.sh`. Then my
`atan_twoarm.sh`. Each is 40–120 lines of bash re-deriving the same shape: cut a
sandbox, build natives, sweep, do it again on the other arm, run the diff. Each
is written fresh, under time pressure, and each has been buggy.

That is not carelessness, it is arithmetic. Bash written once and run twice will
carry defects that no amount of care removes, and the defects land in exactly the
place where they are hardest to see — between a correct measurement and the
human reading it.

### 3. Nothing connects "what did I change" to "which programs can see it"

This is the deepest one. The subsetting flags are `--limit` (the first N
alphabetically), `--only` (names you type), `--changed` (needs a bank), and
`--batch`. Not one of them can answer *which programs in this corpus are
downstream of the chapter I just edited*.

So relevance is guessed. I guessed. The information needed to compute it exactly
is already sitting in the tree: a program's `cites` lines, transitively closed.
`cite_resolve.py` already walks them. Deriving the affected set from a diff is a
short function nobody has written, and its absence is why a 28-minute run
answered nothing.

### 4. Sandboxes proliferate and nothing retires them

Five sandboxes today for one change: `atan-measure`, `atan-verify`,
`atan-verify2`, `atan-base`, `atan-fixed`. 3.3 GB in `~/runs`, with loose log
files (`atan-twoarm.log`, `bitcast-chain.log`, `bitcast-resume.log`) sitting at
the top level beside the directories they describe.

BOX.md is emphatic that retiring is the default and keeping is the exception, and
that a `KEEP` needs a named consumer. One `KEEP` file exists. The other eleven
entries are sediment.

### 5. The RESULT is not an artifact

This is the one I would fix first if I could only fix one.

When a two-arm run finishes, what exists is a log file in a directory the
checklist says to delete. There is no object that says: *these two trees, this
selection, this population, these natives, this seed, this verdict.* The numbers
get copied by hand into a PR body — by me, today, twice, once wrongly.

Everything needed for that artifact is already computed. `current_tools` knows
the natives' identity. `current_base` knows the trees. The MANIFEST knows the
provenance. `two_arm_diff` knows the verdict. None of them meet in a file.

So provenance is strong per sandbox and absent per *result*, and the result is
the only part anybody reads.

### 6. Batch runners abort instead of reporting

`bare_expected.py` takes N stems and stops at the first that fails to resolve.
The stems after it produce no output and no error — the log simply ends. A
partial run and a running run look identical, which is the same failure shape as
a gate that passes because it never executed.

### 7. The documented trap is still the easiest thing to type

BOX.md During-1 says never watch by `pgrep -f` on the job's own command line,
because the pattern matches the watcher. Knowing this did not help; it is still
the obvious idiom, and the correct alternative is longer to type. A rule that
depends on remembering it at the moment of typing is a rule that will be broken.
The fix is a `wait_for` helper that takes a job id, not a documentation line.

## What this all has in common

Every one of these is the same defect the port found in Cobblestone, pointed at
ourselves: **a claim that is not carried.** The comment claims no resolver
exists. The sweep claims to cover the corpus. The log claims a run is in
progress. The verdict claims to be about a change. In each case something true
was recorded once and then stopped being true, and nothing in the system noticed
because nothing was checking.

Our instrument has the same disease as the thing it measures, which at least
means we understand the disease.

## First principles, for the rebuild

Stated as requirements, not a design, because the design should be argued
separately.

**One command, not a script pair.** `compare <base> <head> [scope]` should cut
both sandboxes, build both, sweep both, diff, write the artifact, and retire the
trees. Bash written per-change is the single largest source of defects in this
apparatus and it should stop existing.

**Selection derived, not guessed.** From the diff, compute the changed chapters;
from the chapters, the transitive citing set; from that, the programs to run.
Print the set and its size *before* the run, so "your change affects 2 of 1,027
programs" arrives while it is still free to reconsider. Full-corpus stays
available; it stops being the default.

**The corpus is every usable program.** `codex/test/**` minus `errors/`. 1,027,
not 614. If some subdirectory does not belong, exclude it by name with a reason
that is checked, not by a glob shape whose rationale expired.

**The result is a file, and it is the deliverable.** One artifact per comparison,
carrying both tree shas, the natives identity, the seed, the selection rule and
its population, the verdict, and the diff summary. Small enough to commit. The
sandboxes are then genuinely disposable, because the answer no longer lives in
them.

**Runs expire; results persist.** A sandbox is scratch space with a lifetime
measured in hours. A result is a committed artifact with a lifetime measured in
the project. Right now we have this exactly backwards: 3.3 GB of trees kept, and
the verdicts living in prose.

**Names cannot collide.** A run's identity should be a hash of what it is —
(base, head, selection) — not a timestamp plus a label I typed. Two runs of the
same comparison should be recognisably the same run, and re-running should say
so.

**Every batch reports per element.** No runner may stop early and leave silence
behind it. Missing output must be distinguishable from pending output, always.

*— Claude*
