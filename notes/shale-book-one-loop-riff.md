# One loop, from the reader's seat

*2026-11-14. A riff on the chapter's shape, for your replies.*

## What the reader wants here

By this point the reader has heard the book's claim, that agents write Shale and humans read it, and has had a fast tour of the language. They're interested, and a little wary. What they want from "One loop" is a picture of their own working day:

- **What do I actually do?** How much of my time does a turn take, and what do I type?
- **What does the agent do while I'm away?**
- **How much Shale do I have to read,** and what am I looking for when I read it?
- **How do I know the change is right** without reading the Go?

If the chapter answers those four, the reader turns the page reassured and holding one technique. Right now it answers them only in pieces.

## What the chapter does now

It walks one real turn: the agent reports at the end of Session 3, Steve replies "add a defensive check", the agent adds the check with a test and a planted fault, and runs the real server once. Then the chapter reads that script with the three questions, and closes on why Shale beats bash.

The story is good. The trouble is how it's told:

- **The diagram and the text tell different stories.** The diagram is the general loop (a prompt, then gates, a report, replies). The text starts at a report, never shows a prompt or a gate, and brings in an orchestrator the diagram doesn't have. The diagram's gate label still says "fast, full, release", which are the old script names.
- **It opens with a jump.** "Here we preview the end of Session 3", then "as Session 2 explains", then "already at work on Session 4". A reader who hasn't met any session yet has to hold three of them at once.
- **The reply is shown as a JSON line,** with its `prev` and `next` fingerprints. That's the server's view. The reader's view is a paragraph and four words.
- **"What we read" mixes reading a script with reading its output.** By the new rule, the agent reads the output and you read the script.
- **"Why Shale, and not bash" repeats Meet Shale,** and its last line, "slightly longer scripts", now contradicts "terse by design".

## Proposal: draw the turn the chapter tells

I'd make the diagram match the account, as you suggest is more honest. One diagram of this one turn, with its real parts:

- the agent's report, with its line "The comments folder's parent must exist when the server starts";
- Steve's reply on that line, "add a defensive check";
- the orchestrator passing the reply to the agent already working on Session 4;
- the change, in `store.go`, with its test and one planted fault;
- the agent's one run of the real server, in Shale, which scrolls past Steve;
- the checks, green, and back to a report (which checks ran in this turn, the rewrite confirms against the journal).

One sentence under it says the claim: every session in this book runs this same loop, simplified here to one turn. Then the text walks the diagram top to bottom, a short section for each box, so the reader can see where they are.

## The shape, at about 600 words

1. **What one turn costs you:** a few minutes, and four words of yours. Then the diagram.
2. **The report,** shown the way you saw it: one line of the agent's report, and your reply under it. The JSON line goes.
3. **Your reply works because it's attached.** The paragraph carries the context, so four words are a complete instruction. That's the chapter's first lesson.
4. **The handoff:** one sentence on the orchestrator.
5. **The change and its proof:** the Go excerpt, then a sentence each for the test, the planted fault and the green checks. That's how you know it's right without reading the Go: the agent proves it, and the gate holds it.
6. **What scrolls by:** the script itself, read with the three questions about what it reads and runs, and one line saying what the agent told you about its ending. That's the second lesson: you read scripts, not output.
7. **Close on the two lessons:** reply where the context is, and read the script, not the output. "Why Shale, and not bash" goes, since Meet Shale's "What you get" already says it better.

## One question

**Should the general loop appear anywhere?** My recommendation is no, beyond that one sentence. The specific diagram teaches the loop better than an abstract one, and How we work can carry the general shape if it's ever needed.
