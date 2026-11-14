# The lessons reader's first pass

The new lessons reader went through the book under MISSION AI. Every chapter from One loop on has material for a lesson. Many lessons are already **sharp**, but several are **buried**: the chapter describes what happened, or credits it to the agent, and never states it as a rule. One loop has no lesson yet.

Below are the proposed lessons, one block per chapter. Reply to any you'd change or drop. Unless you say otherwise, I'll have an editor put them all in, each at the moment that earns it, and fix the overreach list at the end.

## One loop

- **New:** "Attach each reply to the sentence it answers. Then four words are a complete instruction." Earned by "add a defensive check".
- **Sharpen** "read it at scroll speed" with its reason.

## Session 1

- **Rewrite** the agent's "write the audit before the tests next time" as: "Run your code over real data before you trust your own tests." Earned by the 500 real notes that found two bugs every hand-written test missed.

## Session 2

- **Rewrite:** "When a guess can be wrong, prefer an honest failure to a confident wrong answer." Earned by the 345 misplaced paragraphs out of 22,928.
- **Rewrite:** "Turn each miss into a check."

## Session 3

- Already sharp: "a count can be checked, and 'ok' can't"; budgets in CPU time, never wall time; slowness is a finding.
- **New:** "After seeding a fault, count how many tests went red against how many should have. A test that panics hides every test after it." Earned by 3 red that became 12.

## Session 4

- Already sharp: seeded faults catch tests that test nothing; out of scope means unchecked, not removed.
- **New:** "Test every field that reaches the page, not just the one you thought about." Earned by the escaping hole.
- **New:** "A script that edits files to test something must put them back on any stop." Earned by "Plants 1 to 5 had been lucky".

## Session 5

- Already sharp: a fault the full check catches proves nothing about the rollback.
- **New:** "Announce readiness only after you hold the resource." Earned by the server that said "listening" before it owned the port, so a check talked to the wrong server.

## Session 6

- Already sharp: a third cleanup by hand means asking what word the language is missing.
- **Rewrite:** "Put recovery in a process that outlives the failure." Earned by the child run.
- **New:** "When you change what a primitive means, run the gates of everything built on it." Earned by the consumers gate.

## Session 7

- Already sharp: a finder that reports nothing proves little until it has found something.
- **New:** "Copy your outputs aside before any change, so you can compare the after byte for byte." Earned by the before snapshot.

## How we work

- Already sharp: a gate you've never seen fail is untested; keep only cheap fixtures permanent; gates hold only what you already know to check.

## Overreach, to fix regardless

- **One loop:**
  - "enough to trust the change" claims a lot for one manual run.
  - "can't hang" ignores a kill from outside, which Session 6 admits.
- **Session 5:** "took the most care" and "the same every time" are unmeasured.
- **Session 6:** "the best feature so far came from the most annoying chore" is two unmeasured superlatives.
- **Session 7:**
  - "Nothing in this session was new" is false: the URL finder and the comparison script are new.
  - It points back to a lesson Session 1 never states. The Session 1 rewrite above would fix that.
- **How we work:**
  - "Nothing in this project was planned in advance" is contradicted by the prompts for Sessions 3 and 5, which asked for the checks and the release.
  - "Measure a baseline" brings in hunts that no session tells, and shows no decision changing. I'd cut it, or tie it to a real moment.
