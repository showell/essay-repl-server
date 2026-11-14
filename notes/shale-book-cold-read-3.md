# The ten-chapter cold read: three questions for you

A fresh cold reader went through all ten chapters as an experienced developer new to agents. It called the book **honest**, **concrete** and **well-shaped**, and also **dense**, **insider** and **repetitive**.

Most of what it found are glitches, and an editor agent is fixing them now:
- **Two claims the journals don't support.** One says a server was left running in Session 4, when it was a fault left in the tree. Another says faults were planted only in Session 4, when Sessions 2 and 3 plant them too.
- **Counts that disagree across chapters.**
- **New accidental refrains,** now added to the build's list so it holds them.
- **Quotes that are mostly header comment.**
- **A few blocks pasted by hand** where the journal can supply them.
- **One sentence about Zig,** which is architecture too early.
- **A stale "pictures still to come".**

Three findings are your calls.

## 1. Session 6 has no prompt

Every session is supposed to open with the prompt we gave. The jobs feature began in conversation, when you told me to go ahead with it, rather than from a prompt file. So `journal/prompts/` has nothing for Session 6.

**My recommendation:** open Session 6 with your actual words, quoted exactly from our transcript, and one honest sentence: this session started from a reply in conversation, not a written prompt. That's true, and it shows the reader a second real way a session starts.

## 2. Show the agent side

The reader's top request: this book is about working with agents, yet the reader never learns:
- whether each session is a fresh agent;
- how long a session ran;
- how often you stepped in;
- what an agent's report looks like.

The only hint is "we passed it on to the next session's agent."

**My recommendation:** one short paragraph per session, in a fixed spot right after the prompt: the agent (cold or continuing), its wall time, and how many times we stepped in. Also quote one real report, trimmed, in One loop. The journals and the run records hold these facts, so nothing is invented.

## 3. Density

Session 2 reaches p1, the thresholds, trigrams and T=300 before the reader cares about any of them. Sessions 3 and 5 are similar.

**My recommendation:** each section keeps one number and one point, and the rest moves to "How we work" or goes. That's a real cut, so I'd do it after 1 and 2 land, as a separate pass you can read.
