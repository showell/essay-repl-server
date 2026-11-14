# What a true story, retold, can build on

*2026-11-14. Every artifact Part One can draw on, sorted by one question: is it a record of what happened, or a living asset we can improve? Reply to any paragraph, or to the table.*

Under a true story, retold (MISSION AV), the book draws on two kinds of material, and they follow opposite rules.

- **Records** are what happened: prompts, journals, the scripts as they ran, their output, the stops, your replies. We select from them, group them and reorder them, but we quote them exactly and never improve them. Fidelity is fixed.
- **Living assets** are what we still own: the project's scripts, the cookbook, Shale itself, its docs, the product's code. We quote them as they stand today, and if one is hard to read, we fix it rather than apologize for it. We've done that all day: verb names for 67 recipes, full names in the commit check, a corrected guide.

A third kind is made by the book: its prose and its diagrams. They answer only to the reader.

<table>
<thead>
<tr><th>The artifact</th><th>Where it lives, and how much</th><th>Fidelity</th><th>How the book uses it</th></tr>
</thead>
<tbody>
<tr><td colspan="4"><strong>Records: what happened</strong></td></tr>
<tr><td>The prompts</td><td><code>essay-surface/journal/prompts/</code>: 8 prompts (Session 6 began from a reply), each 150 to 260 words</td><td>A record, written by Claude as your proxy. Quote exactly, or summarize and say so; never rewrite.</td><td>Sparingly. A long, complete prompt suggests one message carries a session, which isn't how you work. Prefer the one-line ask behind it, in the simple workflow (AU), and quote an excerpt where its wording teaches.</td></tr>
<tr><td>The journals</td><td><code>essay-surface/journal/session-1.md</code> to <code>session-9.md</code>: 9 journals, each the agent's own account with every script verbatim</td><td>A record. Select freely, quote exactly.</td><td>The evidence pool, and the book's main source. A chapter can draw on any session's moment (AV). The journals keep their old script names, which is fine: they're history.</td></tr>
<tr><td>The ad hoc scripts</td><td>Inside the journals: 166 Shale blocks, most of them heredocs</td><td>A record: they ran as written.</td><td>Quote the few that teach, at scroll speed. Their terse names stay, since terseness is a feature and they're one-offs (AQ). Where a clearer one-off would teach better, rerun it in today's Shale and quote that run, the way Meet Shale's heredoc was.</td></tr>
<tr><td>The output</td><td>Inside the journals: 199 output blocks</td><td>A record.</td><td>Rarely raw. Output is for the agent (AP), so the book gives its meaning, and shows a raw line only beside that meaning, and only when its shape is the lesson.</td></tr>
<tr><td>The stumbles</td><td>Inside the journals: 53 stops, a left-running server, a test whose panic hid twelve others, invisible reply buttons</td><td>A record. Never tidied into a smoother story (D, AN).</td><td>A few, chosen for their lesson, and none before the reader knows what a working run looks like (AN). The best: the test that hid others, the hidden buttons, and the audit that left a server running. The rest are covered by one honest sentence each.</td></tr>
<tr><td>Your replies</td><td><code>~/essay-dogfood/comments/</code>: 17 replies across 6 notes, plus your console messages</td><td>A record, quoted exactly.</td><td>Short and few. "add a defensive check" is the model. You appear as a witness, not the subject (AR).</td></tr>
<tr><td>The agents' reports</td><td>The journals' Report sections, and the notes written from them</td><td>A record.</td><td>One line at a time: the line you replied to, a call to unmake. A whole report reads like the status report the book is avoiding.</td></tr>
<tr><td>Measurements</td><td>Inside the journals: timings, counts, request latencies</td><td>A record of that moment. A new number needs a new run.</td><td>Only where a number is the point: 69 tests counted, 37 pages flagged then 2. Speed stays a clause (Z).</td></tr>
<tr><td>Git history</td><td>The commits of essay-surface, shale and the book</td><td>A record.</td><td>Mostly offstage. It's how the fact-checker confirms timing and order, and it's rarely quoted.</td></tr>
<tr><td colspan="4"><strong>Living assets: improve, then quote as they stand</strong></td></tr>
<tr><td>The project's scripts</td><td><code>essay-surface/scripts/</code>: 11, with a README</td><td>Living. Improve freely.</td><td>Quoted from the live file, so a fix lands in the book on the next build. Already improved today: verb names, full variable names, a README.</td></tr>
<tr><td>The cookbook</td><td><code>shale/cookbook/</code>: 84 recipes, an index, a naming gate</td><td>Living. Improve freely.</td><td>The secret sauce, introduced in Meet Shale. A hard-to-read recipe gets fixed, never apologized for. Recipes the story leans on, such as the negatives lint, can be shown as the reader's to keep.</td></tr>
<tr><td>Shale itself</td><td>The language, its prelude, its built-ins</td><td>Living. Agents improve it.</td><td>Taught as it stands today, with no "it used to". Its fixes during the build (jobs that stop with their run, the regex built-ins, the match groups) are a positive story for later: maintaining Shale costs you little, because agents fix languages well.</td></tr>
<tr><td>Shale's docs</td><td>The README, the agent guide, the cookbook index</td><td>Living. Kept true by checks.</td><td>Mentioned where the reader's agent would find them. The doc-truth pass fixes contradictions before a reader meets them.</td></tr>
<tr><td>The product's code</td><td><code>essay-surface</code>: the Go server, the markdown renderer, the page script</td><td>Living, but it's the app, not the lesson.</td><td>A little Go, now and then, so the reader sees what's being checked: a few lines like the parent check. We improve it only for the product's sake.</td></tr>
<tr><td>The Roc format</td><td><code>essay-surface/format/</code>, for Part Two</td><td>Living.</td><td>Part Two's subject, told closer to the record, since it's being built now in the simple workflow.</td></tr>
<tr><td colspan="4"><strong>Made by the book: serve the reader</strong></td></tr>
<tr><td>Diagrams</td><td>Dot blocks in the drafts</td><td>Free, within one rule: never claim what the text can't commit to (AS).</td><td>One small diagram a chapter, its arrows the chapter's headings (AT).</td></tr>
<tr><td>Prose</td><td>The drafts</td><td>Free, within the contract: nothing false, nothing tidied.</td><td>Lesson first, story as setting, simple workflow, authoritative.</td></tr>
<tr><td>The orchestration</td><td>How this book was really built: cold agents, an orchestrator, memory files, short reads</td><td>A record, but of an advanced technique.</td><td>Late, as an advanced technique, if at all (AU). It's the honest answer to "how was this built", which the rewritten introduction can give in a sentence.</td></tr>
<tr><td>The book's own tooling</td><td>The build, its gates, the personas, MISSION.md</td><td>Living.</td><td>Offstage. Programmers want to build apps, not books, so this stays an aside.</td></tr>
</tbody>
</table>

## Where the focus belongs

Three things stand out from the table.

- **The journals are a pool, not a script.** With 166 scripts and 53 stops to choose from, each chapter can pick the clearest real example of its lesson. That's the freedom a true story, retold, buys.
- **The living assets carry the teaching.** The scripts and recipes the reader will actually keep are the ones we can improve without limit. So the book should lean on them, and quote the records mainly for the story's moments.
- **The prompts are the weakest material.** They're long, polished, and written by Claude, and the simple workflow you actually use runs on short asks and replies. The book shows the short ask more than the long prompt.

## A question to settle next

**Should the book show the session prompts at all?** My recommendation: one, early, in excerpt, to show what a first ask looks like. After that, short asks and replies, which is closer to how you really work.
