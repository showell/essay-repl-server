# The essay surface, Monday

Monday's agent is done, and Tuesday's (comments) is at work. The prompt it got is the one the book will quote: `journal/prompts/monday.md` in the new repo, `~/showell_repos/essay-surface` (local only, no remote yet).

## What got built

- **A Go server, standard library only:** `server.go` (249 lines) and `markdown.go` (1,026 lines), with 69 tests.
  - It serves `notes/*.md` at `/notes/<name>.md`, with an index at `/`, newest first.
  - It renders each note once and keeps the page until the file changes.
  - The pages work on a phone and have a dark mode.
- **The renderer** handles headings, paragraphs, nested lists, fences, inline code, emphasis, links and tables, plus blockquotes, images and raw HTML blocks.
- **The sample data** is a dozen of your real notes, from 1 KB to 167 KB.

## The numbers

Measured over HTTP on all 503 of your notes (4.7 MB):

| | median | p99 |
|---|---|---|
| a note | 0.133 ms | 0.220 ms |
| the largest note (190 KB page) | 0.149 ms | |
| the index | 2.04 ms | 3.54 ms |

Rendering all 503 at startup takes 173 ms. The agent timed the index in two halves: 1.1 ms of its 1.4 ms goes to checking the folder for changes on every request. Its plan for tomorrow is to let Linux report file changes instead (inotify), which should bring the index near 0.15 ms.

## The scripts it kept

- **`scripts/check.shale`:** gofmt, vet, then the tests, each with its verdict and time. The agent calls it "the gate before a commit", unprompted. It's 19 lines, and it's the first rung of the book's ladder showing up by itself.
- **`scripts/bench.shale`:** the timings above, for any notes folder.
- **`scripts/audit.shale`:** renders every note through the server and counts markdown left outside code.

**The audit found two bugs that 62 renderer tests missed.** Titles kept their backticks in 35 notes, and a lone ``` in a table cell swallowed the rest of the row. Both got fixed, with a test each. That's Thursday's story arriving on Monday: a check over real data finds what unit tests can't, so it deserves to become a gate.

## Where Shale got in the way

This is the "improve Shale" list, from the agent's own report:
1. **`lines()` splits a string, not a file.** The agent expected a file; `read_lines` exists, but the name misled it.
2. **Budgets.** Two scripts and an audit pass ran out of budget until the work was split per file and the slow regex helpers were swapped for builtins.
3. **One `shale` launch per Bash call** (the hook).
4. **`http_get` starts a new curl every time,** so a page timed at 10 ms was mostly curl starting up. Batching URLs into one curl fixed the measurement. A faster HTTP path, or a clear note in the docs, would help every server project.
5. **A stopped run leaves its server running.** A run that stopped after `job_start` left the job alive, and the agent had to stop it by hand. The audit script now stops the server before anything can stop the run. **This is the strongest candidate for a language change:** a job the run started could be stopped when the run stops, unless the script says to keep it.

## Seeing it

The classifier refused to put a preview on a public port, which is right for a server with no login. So the preview runs on localhost: Monday's build, serving all 503 of your notes, on port 9301. Open an SSH tunnel from your laptop, then browse http://localhost:9301/:

```sh
ssh -L 9301:127.0.0.1:9301 steve@143.244.172.148
```

## What's next

- **Tuesday is out:** comments anchored to a paragraph's content, a plain-JavaScript front end, comments in files git can diff, and pages kept fast.
- **Wednesday's prompt** gets written from Tuesday's journal.
- **The book's anchored include** (`{{lines PATH from "A" to "B"}}`) is in, so draft 2 can quote the journals' scripts without drift.
