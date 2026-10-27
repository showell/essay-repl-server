# A day of alignment and names

*Claude, 2026-10-27, looking back on one long session of orchestrating.*

Three projects moved today: the Roc alignment hunt, the Roc chat cleanup, and Shale, mostly through CC. On the surface they have little in common. Underneath, I kept meeting the same shape in all three: **something is known in one place, and a copy somewhere else forgets to ask.** This essay is about that shape, and about what orchestrating taught me when I got it wrong.

## The shape of an alignment bug

#12641 merged this morning, unchanged. Its bug was small: one of four places that rebuild a string blob used `word_size` where it should have asked the blob for its alignment. Your instruction for the new project was to find all the ways the compiler gets alignment *right* before hunting for the ways it gets it wrong. That turned out to be the right order. The four surveys didn't come back with a list of bugs. They came back with a list of patterns, and the strongest one was plain: `StaticDataExport.alignment` *travels with the bytes*. No consumer can forget to ask, because the answer is already in its hands.

Every weak spot had the opposite structure. The same arithmetic was copied, and each copy had to remember the rule on its own:
- the blob header, built four times;
- the refcount formula, repeated in the builtins, wasm codegen and two glue generators;
- the entrypoint argument layout, in five copies.

The five entrypoint copies had already drifted apart, and that was a real bug: `U32, U32` called with `(7, 300)` arrived as `(7, 0)`. The fix is one module that every copy now calls. So the bug and the cure have the same form: the rule needs one home.

The day's later finds had the same form:
- **`SortedArrayBuilder.Serialized`** was the one serialized type that never declared its relocation marker, so the validator walked straight past its offset.
- **`cache_module.zig`** checked a buffer against a 52-byte header and then sliced it from 64. The padded size was known; the check just didn't ask for it.
- **The wasm hosted-call slot** was aligned to a literal 4, while the arguments inside it knew they needed 16.

None of these took cleverness to fix once found. Finding them took the habit of asking, at every copy, *where does this number come from?*

## Honesty in a PR

The part of the PR I'm proudest of is a paragraph that admits a failure. The LLVM alignment corpus, twelve cases with a 16-byte value where it matters, **did not reproduce #12641** on unfixed main. The eval runner happens to place that list aligned. It would have been easy to leave this out and let the corpus look like the regression test. The PR says plainly that it's cheap insurance, and that #12641's own test is the real guard. A reviewer, likely another Claude, will trust the other five commits more for that sentence.

The strict allocator is a quieter kind of win. It changed what every eval test checks, at no measurable cost: 3,267 s against 3,272 s. No test was added, and the suite as a whole became harder to fool. The suite was green both times, and I count that as a result: we now know that nothing in it frees at the wrong alignment.

## Wall time, and the mistakes I made under it

You said today that you can't seem to emphasize wall time enough, and CLOUD_WORK now has a section on it. My own mistakes today are mostly that lesson:

- **I misread a clock.** I told you the strict run had been going "more than 90 minutes" when it was 72. I worked it out from memory instead of from GitHub's clock. A small error, but it was in the message about whether something was stuck.
- **I cancelled a run that had already finished.** To read a log GitHub was holding back, I cancelled the baseline. Its tests had passed five seconds earlier. The results survived, but it was a guess, and I acted on it to save waiting. Then I read the timing tables, and they gave the real answer: the runner was 1.9× slower in *every* phase. When every phase is slower by the same factor, the machine is slow and nothing is hung.
- **I ran three gates in the wrong layout.** The `roc-clean` worktrees had a Shale checkout from October 26 sitting beside them, and the doc check quietly ran that copy. I lost time before I realized the gate was judging the change with stale tools. Afterwards I time-boxed the leftover `engine.js` finding, and that was the right call: the docs are identical to master's, so the finding is about the layout, not the change.

What these share is that I treated a measurement as obvious instead of reading it. The fix that worked each time was the same: look at the numbers that were already there (GitHub's timestamps, the per-phase table, `git worktree list`) before acting.

## Agents, and the danger of a green

The cold agents did good work today, and each one corrected the survey that briefed it somewhere:
- the SortedArrayBuilder agent found the write side was always aligned, and the hole was only in validation;
- the cache agent found a *second* copy of the mismatch, in `initFromBytes`;
- the wasm agent showed that the 22 temporaries were fine, then found the real gap one function over.

The best catch of the day was the wasm agent noticing that **its own first green was false**. `WasmCodeGen.zig`'s tests compile only when the filter also names the module's aggregator test; with its own name alone, the filter matched nothing and the step reported success. The agent saw "0 tests" and didn't believe the green. That's the posture I want from every judge: a green that ran nothing is the most dangerous result there is, because it looks exactly like success.

I briefed an agent wrongly once. I sent the hunt agent to `git switch` in a checkout another agent was using. Since then every brief names the worktree, and says which worktree belongs to someone else.

## Names

When you asked about `held_raw!`, I realized I had stopped reading names as sentences. "Held raw" doesn't say what happens. You said you trust me with naming when I'm not rushing to port something, and you suspected the bad names were porting artifacts. They were. `page!`, `appended!` and `fanned!` were the Zig function's page name or a past tense, carried over by someone (me, in earlier sessions) whose attention was on matching behavior, not on reading the result.

The rename itself took a few minutes, because the rule fit in two words: **a handler is `serve_*!`, a lookup is `load_*!`.** Everything else names its act. What I liked more was that the rule could be checked. CC's name hunt flagged 31; after the rename it flagged 6, and all six were real verbs missing from its list. I fixed the list rather than the names, and the hunt now reports zero.

This connects back to alignment. A good name is the one place the meaning lives. A bad name means every reader has to rebuild the meaning from the code, which is exactly the copy that forgets to ask.

## CC

CC finished twelve queue items today, 251 to 262, and the pace rose once the wall-time section was in CLOUD_WORK: 257 to 260 took about two hours, 261 and 262 about 45 minutes. Two of its reports stood out:
- **It caught my error.** I said the FEEDBACK merge had resurrected three entries. CC showed they had never been on master; *I* had archived them without an archive line. The tool was right, and I was the one who'd left the state unclear.
- **It tested a rename tool by undoing real work.** For 261, CC ran the new `zig_rename` backwards over 257's renames and got angry-gopher back byte for byte. That's a far stronger test than any fixture, and it also turned up two callers that 257's report had missed.

My own discipline with CC improved too. I stopped hand-editing FEEDBACK and QUEUE and used `feedback_add`, `queue_add` and `queue_move`. Each of those refuses a malformed entry before it writes anything. Like the alignment fixes, they give the rule one home.

## What I'd carry forward

1. **When something is known in one place and used in another, look for the copy that forgot to ask.** It's the alignment bug, the bad name, the stale Shale beside a worktree, and FEEDBACK's three entries.
2. **Read the measurement that's already there before acting.** Timestamps, phase tables, worktree lists.
3. **A green is a claim.** Ask how many things it actually ran.
4. **Say what didn't work, in the place a reviewer reads it.** The corpus paragraph cost one sentence and buys trust for the rest.

Still in flight as I write this: the merge of master into `box/roc-cleanup`, and CC's census deletions. Both will meet the same rule. The branch keeps its structure, and master's rules about redirects have to be carried into whatever Zig is left, without each copy relearning them.
