# Part Two's first prompt, for your replies

This is the draft prompt for Session 8, the first session of Part Two. Reply to any line, and when it reads right, I'll save it to `journal/prompts/` and hand it to a cold agent. Under MISSION PD, the agent's first report is a set of Roc types and nothing else, so its report comes back to you as a note before any code exists.

## The prompt

> The essay surface works, and I use it every day. Now I want notes that can do more than markdown does. A note should be able to hold a diagram, drawn from a dot description, and later a small widget. Markdown isn't a good fit for that, so we're going to build our own format, inspired by markdown but designed from first principles for exactly what I do. It needs nothing like markdown's full power, and none of CommonMark's rules.
>
> The features will be written in Roc. Go keeps doing the plumbing it does now, and the front end stays plain JavaScript. Where Roc runs, on the server or in the browser, is for the requirements to decide, so don't decide it yet.
>
> Start with the types, not the code. Read my real notes in `notes/` to see what I actually write. Then propose the Roc types for a note in the new format: its blocks, the text inside them, and a diagram block. Leave room for widgets without designing them yet. For each type, say in a sentence what it's for, and what it deliberately leaves out. Tell me which things in my real notes the new format would drop, and how many notes use each.
>
> Write no Roc functions and no Go yet. Your report is the types, as a note I can reply to. We'll argue about them before anything is built on them.
>
> My existing notes keep rendering exactly as they do now. The new format is for new notes.

## Why each part is there

- **"Inspired by markdown, from first principles" (PB).** The agent starts from what you write, not from a spec.
- **"Read my real notes."** Your 500-odd notes are the requirements. Counting what the new format drops turns "we don't need that" into a number you can judge.
- **"What it deliberately leaves out."** This is the half of type design that gets skipped. It also gives the book its first honest place to be wrong: an omission you reply to.
- **"Don't decide where Roc runs yet" (PC).** The first feature that needs it will force that choice.
- **"No functions, no Go."** This holds the paradigm (PD). The report is types alone, so the session's first gate is your reply.
- **"Existing notes keep rendering."** Nothing in your daily use moves while Part Two experiments. This is the one constraint that's a standard rather than the mission.

## One question

**What's a new-format note called on disk?** The server needs to tell the two kinds apart. A new extension, such as `.essay`, keeps that obvious at a glance. Or the agent can propose one along with the types. My recommendation is to let the agent propose it, since it's part of the format's design.
