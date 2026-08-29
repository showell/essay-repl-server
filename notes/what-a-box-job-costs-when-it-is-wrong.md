# What a BOX job costs when it is wrong

*2026-08-29. Drafting the before/during/after checklist for compute jobs on
the ladder droplet. The checklist is at the bottom; this is the argument for
why it has the items it has.*

## The failure mode is not a crash

Go through the incidents this project has actually paid for and a pattern
shows up immediately. Almost none of them are crashes, hangs, or jobs that
died. They are jobs that **completed, reported a verdict, and the verdict was
about something other than what we thought.**

A partial ledger, all from the last three weeks:

- Natives built from the bare u49 pin while the tier set's expectations came
  from PR 77's tip. The set read **RED 8, green 11**. Rebuilt on the right
  commit it read **green 15, noted 6**. Nothing failed. A regression was
  invented out of a base mismatch, and the tell had been sitting in
  `git status` for half an hour.
- `native/codexir` reported to Damian's lane as "the compiler," when it is the
  compiler *as our own zig plug renders it*. Their tree refused the same
  program at four seed revisions back. The report was wrong at the instrument,
  not at the reasoning.
- A type-def prune added to the driver, the whole 589-program corpus pushed
  through, and the gate answered **578 clean, 0 broken**. It was clean because
  nothing had been pruned — the ladder keeps its own copy of the driver's emit
  call, so the corpus never went through the driver at all. `Tup2` was still
  declared in 578 of 578 programs, and that is the check nobody ran.
- 94 phantom regressions from a resume that printed "emitted zig
  byte-identical, toolchain unmoved" having verified neither, because its
  baseline file had been overwritten by the same script's earlier stage.
- A copied list of emit roots that had drifted in **both** harnesses at once.
  Being wrong together looks exactly like being right.
- `grep | tail -8` read as "the highest row number is 1.73." The file was not
  in numeric order. Two backlog rows were written over live entries in another
  lane.
- `ringplug_build.sh` piping a compile through `grep -E "error|SIZE" | head`.
  The refusal matched neither word, so the caller printed a bare
  `PLUG COMPILE FAILED` with no diagnostic — and the pipe ate the exit code
  besides.

Seven incidents, one shape. **Every one is an attribution failure.** The
machine did what it was told. What it was told was about a different thing
than the name on the result suggested.

That matters for what a checklist is *for*. If the risk were crashes, the
checklist would be about robustness — retries, timeouts, resource headroom.
It isn't. The risk is a plausible number, and the checklist's job is to make
every result **attributable**: to a tree, to an arm, to a baseline, to a
change that demonstrably executed.

## Latency is what makes it expensive

At the keyboard a wrong assumption costs seconds. You notice, you fix it, you
move on. On the box the same wrong assumption costs the whole run before it
even becomes visible:

    cycle.sh (plug rebuild)        ~2 min
    tiers_run.py (the set)         ~3 min
    stack_probe.py                 ~5 min
    corpus census (--changed)      ~10 min
    native_build.sh                ~13 min
    allcycles.sh (sweep, 14 rungs) ~27 min
    rebank_all.sh (truths+sweep)   ~60 min

Against that, `ladder_status.py` is instant and `check_paths.py` is five
seconds. The asymmetry is so extreme that the interesting question is not
"which checks are worth running" but "why would you ever skip one." The honest
answer is that skipping isn't a decision — it's what happens when there is no
list, and the run seems obvious, and you are already thinking about the
result.

There is a second cost that only shows up later. A run's answer is usually
read by a *different session* than the one that launched it. Whatever wasn't
written down at launch is gone: which branch, which natives, what the run was
supposed to settle. So half of what a before-checklist does is not checking —
it is **recording**, for a reader who is not you.

## The lock's ledger is the argument for a checklist over more machinery

The compute lock is worth studying because someone already did the accounting.
The hazard it guards — two 3 GB guests thrashing at 2% CPU each — has fired
**once**, on 2026-08-20. The mechanism guarding it has fired *against us* four
times: a rebank refusing itself beside its own launcher, twice; a watcher
matching its own `pgrep` and waiting for itself; and three spellings of the
rule drifting apart.

And the detail that should stay in the mind of anyone tempted to write another
guard: when the lock was rebuilt, seven entry points turned out to have
**never taken it at all**. They had been starting guests unguarded for months
with nothing going wrong.

> The discipline was doing the work.

That is the case for a checklist rather than more code. A guard has to be
right in advance about every path; a person reading six lines can adapt. It is
also a warning about *this* checklist: every item costs attention on every
run, and an item that has never caught anything is a tax. Keep it to what has
actually cost something, and be willing to delete.

## What the three phases are actually for

They are not one activity split by time. They answer three different
questions.

**BEFORE — make the run attributable.** Decide and write down which tree,
which arm, which baseline, and what question this is settling. The step people
skip is not a check, it's the *sentence*: what result would change my mind? A
run with no falsifier gets read as confirming whatever was hoped for. And
`. ../env` belongs here as a mechanical item, because without it a sandbox is
decoration — `CODEX_ROOT` still points at the shared checkout and the run
reads exactly the stale artifacts the sandbox existed to avoid.

The other item that belongs before rather than after is the **presence check**.
"Is anything broken" and "did anything happen" are different questions, and
only the second catches a no-op. Designing it afterwards is how you end up
with 578 clean and nothing pruned. Design it while you still have to state
what the change should visibly do.

**DURING — do not disturb the measurement, and do not lose the launch.** The
tree the run is reading is part of the instrument; a mid-run checkout cost a
90-minute sweep once, because the plug rebuilds from whatever the tree holds
*now*. The box has two dedicated CPUs, so this is emphatically not "wait
quietly" — one COMPUTE job at a time, not one task at a time. Reading,
editing, PR-writing, light `zig run` all belong beside a running sweep, and
spending the wait on them is the intended use.

Two specific traps live here. A Monitor piped through `head` buffers, so
nothing is delivered until N matches accumulate — a finished build once sat
unnoticed for nine minutes behind a watch that could not report. And killing a
chain does not kill what the chain started: `kill` on `verify_emitter.sh` left
`allcycles.sh` running, which then started a *fresh* guest after the chain was
already gone. `pkill -f` is not the fix and must not become it — run from a
session shell, a pattern broad enough to catch the legs matches the shell
issuing it.

**AFTER — get the answer out before the tree that holds it disappears.** A
commit made in a sandbox worktree lives on no branch; it is reachable only by
SHA and vanishes from view when the sandbox is pruned. That has already
happened twice in one day, to verified branches. Pushing costs nothing and the
window is short.

This is also where truncation does its damage, because the "after" is when
claims get made. `head` and `tail` are for looking, never for concluding: any
sentence of the form *the highest / the only / there is no / none of them* has
to come from a command that saw everything.

And the last item is the one that is easiest to feel finished without: record
the answer where it survives the session. A number that lives only in terminal
scrollback did not happen.

## What I am deliberately not putting in

Resource headroom. The box has 115 GB free with `runs/` at 2.9 GB across six
sandboxes; memory is 8 GB with a guest capped at 3,072 MB by
`~/.codex_ladder_env` because the seed dies *silently* above that. All of it is
true, none of it has ever cost us anything, and a checklist that lists
everything true gets skimmed. The guest cap is already in the env file, which
is the right place for it — a fact enforced by a file does not need a line in
a list.

Same reasoning for the compute lock: it is one line at one door
(`codex_vm.launch`), it cannot be forgotten, and asking a human to check it is
duplicating a machine that is better at it. `--probe` earns its single line
only because a script about to *detach* wants the refusal to reach the
terminal rather than a log nobody is tailing.

---

# BOX.md — first draft

**Before**

1. `python3 ladder_status.py` — seed, banks, tag, lock, what is computing. If
   any line disagrees with what you believe, stop and find out why.
2. Write one line: what this run settles, and **what result would change my
   mind.** No falsifier means the answer will confirm whatever was hoped.
3. Name the tree and the arm — which repo, which branch, which commit, and
   bare metal (the seed under QEMU) or ours (`native/codexir`). A question
   about *the compiler* takes the seed. "Whatever was in front of me" is not
   an answer.
4. `./sandbox.sh <label>`, then `cd <path>/ladder && . ../env`. Without
   `. ../env` the sandbox is decoration and `CODEX_ROOT` still points at the
   shared checkout.
5. Design the **presence check** now: one baseline-free assertion that the
   change is visible in the output. A soundness gate is blind to a no-op.
6. `python3 check_paths.py` (5 s), `compute_lock.py --probe` if detaching,
   and say the expected cost out loud before launching anything over 20 s.

**During**

1. Detach with a log, announce the path, watch with a Monitor — never piped
   through `head`.
2. Do not change HEAD, check out, or edit anything in the tree the run is
   reading. Branch surgery waits for the verdict.
3. Nothing in the codex tree gets run by hand while a sweep is up —
   `build/compile.ps1` boots a 3 GB guest and asks nobody.
4. Keyboard work belongs here. Two CPUs: one COMPUTE job at a time, not one
   task at a time.
5. To abort: signal the process group, then check for orphan guests. Never
   `pkill -f` from a session shell.

**After**

1. Read the verdict from the file. Any claim of a maximum, count, set, or
   absence must come from a command that saw everything.
2. Run the presence check. A *perfectly* clean result on a change that should
   move bytes is a suspect, not a win.
3. Push any branch out of the sandbox immediately — a sandbox commit lives on
   no branch and dies with the prune.
4. Carry the artifacts back (banks, gold, logs) before pruning; `KEEP` with a
   reason on its first line if the run is an oracle rather than a by-product.
5. Stamp provenance: ladder commit, codex commit, sandbox, natives.
6. Record the answer where it survives the session — log, PRIORITIES, the
   register, JUSTIFICATIONS — then commit, clear untracked clutter, and close
   the PRIORITIES item the task came from.
