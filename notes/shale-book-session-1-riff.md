# Session 1, honest without being boring

*2026-11-14. A riff on your reading note: Session 1 is drowning in detail. Reply to any paragraph.*

## What's wrong with it

The chapter is a faithful tour of the journal, and that's the problem. The journal for Session 1 is 527 lines, with 52 code blocks and 7 stops. The chapter shows 9 output blocks and explains 5 of the stops down to their mechanism: step budgets, the arena, `yield()`, the 64-program cap, job records, curl's start-up time. Each one is accurate. Together they read like an incident log.

It also contradicts your earlier note about Shale's output. You don't read those stop lines; the agent reads them and tells you what they mean. Session 1 asks the reader to read every one.

Real work feels like work when every step weighs the same. A good account of real work picks the step that mattered and tells the rest at a glance.

## What the chapter has to get across

Only three things, and the rest serves them:

- **The prompt sets the mission,** and the agent works for twelve minutes without Steve.
- **A green is a claim:** the first gate passes, and only counting the tests shows they ran.
- **Real data finds what your tests can't:** the audit of 500 real notes found two bugs every hand-written test missed.

The third is the payoff, and today it arrives in the last 200 words, after the reader is tired.

## Seven ideas

1. **One story, named in the title.** "A server and a number" promises the number, which MISSION Z says a first version shouldn't care about. Something like "Session 1: the bugs the tests missed" tells the reader where the chapter is going, so each step has a reason to be there.

2. **The stops become a glance, not a lecture.** Show one stop raw, then the other six as a table of what the agent did about each, the way it actually works: the agent reads the line, and you read its fix. The real seven:

   | The stop | What the agent did next |
   |---|---|
   | index 0 is outside the list | `lines` splits a string, not a file, so it read the file instead |
   | the step budget ran out | a regex over 500 notes; it switched to a builtin |
   | the arena budget ran out | it held every note at once; now one note at a time |
   | no key "mtime" in the map | a guessed field name, fixed in the next call |
   | fail: gofmt | its own new gate, doing its job |
   | no function `first` | a guessed builtin |
   | 64 programs a run | one request per note; one curl for all of them |

   That's the honest record in about 80 words, and the lesson is in its shape: seven stops, each one line, and each fixed in the next call.

3. **The mechanics move out.** `yield()`, the arena, job records and curl's clock are true and dull in a story. Meet Shale already lists budgets. Session 1 says *what* happened ("it held every note at once"), not *how Shale counts*. A reader who wants the how has the docs, as the agent did.

4. **One stop gets told in full,** the one with stakes: the program cap stopped the audit after the server had started, so a server was left running. That's the only stop that could have hurt, and it explains why `audit.shale` fetches everything with one curl and stops the server before judging anything. It's also a better story than any budget.

5. **Stop glossing syntax the reader skims.** "`{path = ..., bytes = ...}` is a map, and `#` is a length" teaches a reader who scans for calls to read variables. You don't, and the reader shouldn't need to.

6. **The number shrinks to a clause.** "The agent saved a benchmark too; a note takes about a tenth of a millisecond." The curl start-up mistake is a good small honesty, but it's the third mistake in a row; it can go to the table or out.

7. **Abridge out loud.** Fidelity doesn't require completeness. It requires that nothing shown is tidied, and that the reader knows what was left out: "The journal records 52 runs; here are four." That one sentence keeps the chapter honest while it skips most of what happened.

## The shape, at about 600 words

- The prompt, and a paragraph on what it asks.
- **Seven stops in twelve minutes:** one raw, the table, one sentence of lesson.
- **A gate, and a count:** `check.shale`, the green, the 69 tests.
- **The audit:** the stop that left a server running, the fix, the two bugs, the lesson.
- **The gates now.**

Four output blocks instead of nine, and the payoff by the middle instead of the end.

## The rest of the book

Sessions 2 to 7 were written the same way, so they likely have the same weight, if less of it. My recommendation is to rework Session 1 myself as the pilot, in one voice. Once you've read it and it reads right, a cold reader with a new persona, the bored reader, marks the tedium in the other sessions, and one editor applies the same moves. A gate could hold the line afterward, such as a cap on output blocks a chapter, but I'd wait to see the pilot before fixing a number.

The weekday cleanup is editing these same drafts right now, so the pilot starts once it lands.
