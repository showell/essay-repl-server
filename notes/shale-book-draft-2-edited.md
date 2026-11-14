# Draft 2, edited, with its first diagram

**Read it here:** http://143.244.172.148:9210/shale-book/

All three of the cold reviewer's action items are in, along with your two notes on mantras. The book is now nine chapters, and the build passes every gate.

## What changed

- **A new chapter, "One loop",** sits between the introduction and Monday. It walks one real turn of the loop from Thursday:
  - the agent's report;
  - your four-word reply ("add a defensive check"), as the JSON line the server stored;
  - the agent's Go change;
  - its run of the real server, read at scroll speed;
  - why the same check in bash could hang the agent's shell, and Shale's can't;
  - a twelve-term glossary.
- **The first diagram** is the loop itself: you, the agent, its gates and the essay surface, with the prompt, the verdict, the report and the replies on the arrows. The build draws it from a ```` ```dot ```` fence with Graphviz at build time, so it changes with the chapter around it.
- **Dense, fixed by a gate.** A quoted output block over 12 lines now stops the build. Three editors cut every day's blocks to the lines that make their point, with the point in the sentence before. Thursday's blocks went from 30 lines to 16, and Wednesday's from 49 to 20.
- **Insular, fixed in the prose.** Every insider term is now in the glossary, or defined where it first appears, or cut: `want`, the job record, the consumers gate, the old surface's notes folder. "Chapter 4" and "chapter 5" are now Wednesday and Thursday, and a gate stops the build on any chapter named by number.
- **Repetitive, fixed by a gate, with your moderation.**
  - `book/refrains.txt` holds each accidental refrain to one use: "a green is a claim" lives in Monday, "Shale builds nothing itself" in the introduction, and "slowness is a finding" in Wednesday.
  - **Green again ✅** is a mantra, allowed as often as it's earned. The editors used it about once a chapter, where a check passed after a red.
  - MISSION now says a mantra is short.
- **Honesty is unchanged.** Every mistake and stop from the journals is still there. Saturday's one claim with no source, the runaway loop planted in the child run, now has one: `journal/saturday.md`, written from that agent's report.

## Diagrams next, if you want them

The loop is the obvious one. Three more would each carry a chapter's main idea in one picture:
1. **The three checks by moment** (Wednesday): fast for each edit, full before shipping, release for shipping, with their times.
2. **How a reply finds its paragraph** (Tuesday): same text, else same neighbors, else most similar, else orphaned.
3. **The release as a parent and a child** (Saturday): the child does the swap and its checks, and the parent restores the old server if the child stops.

Shale's own architecture (the Zig interpreter, the host, the preludes) waits until after the Monday-to-Saturday story, as you said. That's now in MISSION too.
