# The Shale book: fewer numbers, and the agent side

**Read it here:** http://143.244.172.148:9210/shale-book/

Your replies to the cold read are in, in three passes. The build passes every gate.

## Your rules, in MISSION

- **Z. A first version isn't about speed.** Early sessions keep only the numbers that carry a point.
- **AA. Show the agent side,** in every session.
- **AB. Put yourself in the agent's shoes.**
- **AC. The orchestrator is your proxy.** Cold agents do small tasks.
- **AD. About 80%,** with the creative exception, in your words.

## Fewer numbers

- **Session 2's** big section is now "A reply finds its paragraph". It opens with the idea, and with why plain similarity fails. The scores, thresholds, trigrams and T=300 are gone, along with three output blocks. One figure stays: 345 of 22,928 deleted paragraphs.
- **Session 1** lost its millisecond timings and benchmark output.
- **Session 3** lost the date survey and the before-and-after index timings.
- **Sessions 4, 5 and 7** had lighter trims of CPU and run-time figures.

## Who did the work

Each session now says, right after its prompt, who did the work, roughly how long it ran, and how often you stepped in:
- **Session 1:** I wrote the prompt and briefed a cold agent; about 12 minutes; you didn't step in.
- **Session 2:** a cold agent, about half an hour. You stepped in once, after it finished, with the eye test that found the invisible reply buttons.
- **Session 3:** a cold agent, about half an hour; you didn't step in.
- **Session 4:** a cold agent, about 17 minutes. You stepped in once, with two replies I passed on mid-run.
- **Session 5:** a cold agent built the release and proved it on dev in about 16 minutes; I ran the real one.
- **Session 6:** opens with your words, "go ahead with the jobs feature", and says it began in conversation. A cold agent built the feature in about 16 minutes; I merged it after Shale's gates.
- **Session 7:** you asked in conversation and I wrote the prompt; a cold agent, about 11 minutes; I ran the release.

## Working with agents

"How we work" has a new section, tied to moments already in the book:
- **The agent's shoes.** A cold agent knows only its brief. It reads every doc it's pointed at, and it counts tirelessly, sometimes past what a first version needs. It guesses at names, and it can't see a page: the hidden reply buttons waited for your eye.
- **The split.** Cold agents ran between ten minutes and half an hour each, and the orchestrator, as your proxy, coordinated.
- **The 80%,** and the creative exception, which this book itself is.

The glossary in One loop now defines "orchestrator".

## Still pasted

Two blocks are still pasted by hand, because no file the book can reach holds them:
- **Session 7's release output.** The console was its only record.
- **One loop's stored reply.** It lives in the dogfood comments, which the book's build can't reach.

The second could become an include if the build gets a read-only mount on `~/essay-dogfood/comments`.
