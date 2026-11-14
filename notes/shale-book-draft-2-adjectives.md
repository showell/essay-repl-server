# Draft 2 in six adjectives

A cold reader went through the whole of draft 2 as its intended reader would: an experienced developer, new to agents. It read the built book with every quote filled in, and nothing else. It named three strengths and three weaknesses, one adjective each. Its words are below, lightly trimmed, followed by my three suggested action items.

## Positive

**Honest.** "The book shows its mistakes and makes them part of the lesson. On Monday 'Nine milliseconds was the wrong number', because the benchmark had timed curl starting up. Tuesday ends with every check green and Steve finding 'no way to reply'. Thursday shows a stored-XSS hole that 'every stage of the full check passed', and Friday shows a release that left a trial 'serving a build nobody had checked.' For a reader deciding whether to trust agents, these failures persuade more than any success story could."

**Empirical.** "Decisions rest on measurements of real data, not on taste. The Tuesday anchoring design is 'argued from Steve's own paragraphs': 22,900 of them, scored and simulated before the resolver existed. Monday's audit of 503 real notes 'found two bugs that 62 hand-written renderer tests missed.' An experienced developer will recognize this as how good engineering really works."

**Cumulative.** "The week builds on itself. Monday's `check.shale` becomes Wednesday's `fast.shale` and `full.shale`. Thursday proves each stage can fail, Friday wraps them in a release, and Saturday turns a trap first noted on Monday into a language rule. By Friday the reader feels how each gate was earned."

## Negative

**Dense.** "Many pages are walls of raw output and numbers: percentile tables, threshold simulations, timing lines with four figures each. The point of each block is usually one sentence, but the reader has to dig through 20 lines to find it. Some sentences pack too much: 'Three stages are the only ones that see their faults: race, bench and the smoke.' I read that three times and still wasn't sure what it claimed."

**Insular.** "It assumes context only Steve and his box have. 'A cold agent built it', 'the consumers gate', 'the prelude', `repos:` paths, `dir=` arguments, `essay-repl-server`, 'the old surface' and `want = \"tag: why\"` all arrive with little or no explanation. There are leftover cross-references too: 'Chapter 5 makes that trick a habit', though the chapters are named by day. A newcomer to agents will feel like a guest at someone else's standup."

**Repetitive.** "'A green is a claim' appears at least five times. 'Shale builds nothing itself' appears almost word for word in the Introduction, on Monday and on Friday. 'Slowness is a finding' and the definition of a plant also recur. Repetition can teach, but here the lines read like refrains."

**The reader's one change:** "Open with a short chapter that shows one complete agent loop (prompt, the agent's script, Steve's reading of it, his reply), argues why the agent writes Shale and not bash, and defines the insider terms, so the target reader knows what they're learning to judge before Monday's detail piles up."

## My commentary

The three strengths are the ones the book was built for: the journals made it honest, the real notes made it empirical, and letting the work ask for gates made it cumulative. I'd protect all three.

The three weaknesses share one root cause. The chapters were drafted by three agents from journals written for us, and nobody has yet edited them for a newcomer. That's the editing pass I said was still to come, and this review gives it a target. Two of the weaknesses can also become gates, in keeping with the book's own argument.

## Three suggested action items

1. **Open on one loop, and define our words.** Add a short first chapter, or a section of the introduction, that walks one complete loop: a prompt, the agent's Shale, our reading of it at scroll speed, and a reply. Use a real moment from Monday. It ends with a small glossary of the insider terms the book can't avoid: agent, cold agent, mount, prelude, job, gate, fixture. Every other insider term gets defined where it first appears, or cut.

2. **One point per output block, held by a gate.** Trim each quoted output to the lines that carry its point, and put the point in the sentence before it. Then gate it: the build stops on a quoted output block over about 12 lines, unless it's on a short list with a reason. That fixes density the way the 900-word gate fixed length.

3. **Say each refrain once, held by a gate.** Keep each catchphrase ("a green is a claim", "Shale builds nothing itself", "slowness is a finding") in the one chapter where it lands best, and cut the rest. A small phrase lint, on the Roc book's negatives model, holds each to one use. A second check catches "chapter 4"-style numbers in a book whose chapters are named by day.
