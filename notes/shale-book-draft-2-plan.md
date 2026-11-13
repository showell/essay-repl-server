# Draft 2: the week, as it's happening

Two days into the week, the book is writing itself in a way draft 1 never could. Each day has a prompt we wrote, an agent that did the work, and a journal of every Shale script it ran. This essay proposes how draft 2 turns that into chapters. Reply anywhere you disagree.

## The book is a week

Each chapter is a day on the essay surface, told from our side of the desk. A chapter opens with the prompt we gave the agent, quoted whole. It follows the work through the agent's own Shale, quoted from the journal. It ends with what we decided to keep. The reader learns Shale the way you did this week: by reading what went by and judging it.

## Monday: a server and a number

Monday's chapter teaches scroll speed. The scripts are short heredocs: copy some notes, build, run the server as a job, fetch a page, time it. The numbers make the case for Go on their own: 0.13 ms for a note, 2 ms for the index. The turn of the chapter is `audit.shale`, a heredoc that rendered all 503 real notes and found two bugs that 62 unit tests missed. That's the first time the reader sees a check over real data beat the tests, and it plants the idea of gates on day one.

## Tuesday: a design argued from data

Tuesday's chapter teaches review speed. The agent didn't guess how comments should stay attached. It tested four rules against 22,900 real paragraphs and kept the combination that won. The chapter quotes that measurement script, because it's the best example in the week of an agent using Shale to make a design decision instead of a test. Tuesday also shows the agent improving Monday's scripts, which is the recipe rung arriving naturally.

## Wednesday: the habits

Wednesday's chapter is where the work habits come in, early as you wanted: a fast check for each edit and a full check before anything ships. If the agent's scripts come out clean, this chapter quotes them whole, and the reader sees the tiers as something a project grows into by its third day.

## The human's eye

The best story so far isn't in any journal. Every check passed on Tuesday, and you opened the page and found no way to reply. The buttons were invisible until hovered. No browser on the box could have caught it. Draft 2 should tell that story plainly: gates hold what we know to check, and a human's first look finds what we didn't know. Then the fix, and then the question of whether that check can become a gate too.

## Thursday and Friday, still open

Thursday is meant for plants and a held gate. The likeliest candidate is anchoring: plants made of note edits that must keep their comments, and edits that must orphan them, held at today's numbers. Friday is the release, and maybe the "new feature arrives" chapter, where the markdown moves to roc-markdown.

## Shale gets better as we go

Three changes to Shale have earned their place already. A run that stops should stop the jobs it started, since that left a server running on both days. `http_get` should time a page without curl's start-up in the number. And `lines()` should say clearly that it takes a string. Each one can be a short section in the chapter where it bit, with the fix in Shale's own history.

## What draft 2 drops

The Roc book's scripts move to a sidebar at most. The week's own scripts carry the argument, and they're about building an app, which is what programmers want to read about.
