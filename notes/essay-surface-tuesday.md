# The essay surface, Tuesday

Tuesday's agent built paragraph comments. Wednesday's is now at work on a faster index and a set of checks we can keep. Everything is in `~/showell_repos/essay-surface`, in seven new commits (`8c05754` to `0d2c7fc`).

## How a comment finds its paragraph

A comment remembers its paragraph's text, with spacing ignored, and fingerprints of the paragraphs just before and after it. When the note changes, the comment tries, in order:
1. the paragraph with the same text;
2. else the one still between the same two neighbours (edited in place);
3. else the most similar paragraph, if it's similar enough;
4. else it is shown at the foot of the page as **orphaned**. It's never lost.

A comment found by rule 2 or 3 updates what it remembers, so a run of small edits can't shake it loose. Headings, list items, code blocks and tables take comments too, not just paragraphs.

The agent tested the anchoring on 22,900 real paragraphs from your notes, with each kind of edit made to each one:

| Edit | Comments stay right |
|---|---|
| typo, changed word, added sentence, rewrap, paragraph added above | 100% |
| paragraph split in two | 99.4% |
| moved and edited | 93.9% (5.5% orphaned) |
| deleted | 98.5% orphaned, as they should be; 1.5% landed on a look-alike |
| merged into the next paragraph | 57.5%, mostly orphaned |

When a comment's paragraph has changed, the page shows the original text under "on an earlier version", so a wrong landing is visible.

Merging is the weak spot, and worth a call from you: is "orphaned at the foot" acceptable for a merged paragraph, or should a merge carry its comments?

## Storage and speed

- **Storage:** `comments/<note>.md.jsonl`, one JSON line per comment, so a git diff reads as a list of comments. A bad line is an error that names its `file:line`, never skipped. Files are written whole, then renamed into place.
- **Speed:** a page with comments is as fast as one without, within noise: 0.17–0.20 ms median for ordinary notes, and 0.29 ms for the largest note with 100 comments. The box was busy all afternoon, so these run about 1.7× Monday's.
- **The front end:** plain `comments.js` and `comments.css`, inlined into the page, about 8 KB. A quiet button sits in the right margin on wide screens, a faint `+` follows the text on phones, and a name-and-comment form opens under the paragraph. Posts are JSON only, which another site's form can't send without the browser asking first.

## Checks, and how it went

- **Tests:** 32 test functions, clean under Go's race detector, including 40 posts and 40 reads at once with all 40 comments kept. The agent planted three faults, one at a time, and each turned its tests red.
- **Scripts:**
  - `check.shale` now also checks `comments.js` with `node --check`, since `go test` never parses it.
  - `bench.shale` times pages with and without comments.
  - `audit.shale` checks one comment marker per paragraph on all 504 pages (23,959 markers).
  - The new `comments_smoke.shale` runs the whole flow through the real server while it edits a note on disk.
- **What went wrong:**
  - A bench run hit a memory budget, which `attempt` can't catch, and left the server running. That's the second day a stopped run left a job behind, so the case for Shale stopping a run's jobs when the run stops is getting strong.
  - Start-up had slowed from 173 ms to 638 ms. Profiling found the text normalizing, and the fix brought indexing the largest note from 6.6 ms down to about 2.4 ms.
- **Not yet seen by a human:** there's no browser on the box, so nobody has looked at the page or tried it on a phone.

## Try it

The preview on port 9301 now runs Tuesday's build against a scratch copy of all 504 notes, so test comments go nowhere real. Open the tunnel from your laptop, then browse http://localhost:9301/:

```sh
ssh -L 9301:127.0.0.1:9301 steve@143.244.172.148
```

## Wednesday's prompt

`journal/prompts/wednesday.md` asks for two things:
- **The index:** let the server hear about file changes instead of checking 504 files per request, and take dates from the note or git.
- **The checks:** turn the scripts into a **fast** check for each edit and a **full** check before shipping, with timing that a busy box can't break. It also says "I read the scripts' code, not their comments, so make the code say what it does."

That's the work habits arriving on day three, as you wanted, instead of at the end of the book.
