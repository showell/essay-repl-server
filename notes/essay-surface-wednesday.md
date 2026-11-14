# The essay surface, Wednesday

Wednesday's agent made the index fast and turned the week's scripts into two checks. Thursday's agent is at work on proving those checks can fail. Your dogfood server on 9301 now runs Wednesday's build, with the reply buttons merged in, and your replies carried over.

## The index, from 2 ms to 0.1 ms

The server used to check all 506 notes on every request for the index. Now Linux tells it when a file changes (inotify, with no dependency beyond Go's standard library). Each request starts by draining the kernel's queue, which is one read when nothing changed, and only what changed gets reloaded.

| | before | after |
|---|---|---|
| index, median over HTTP | 2.276 ms | 0.105 ms |
| index, p99 | 4.09 ms | 0.18 ms |

## Dates you can trust

A note's date now comes from the note itself: the first date in its title or the paragraph after (309 notes). Otherwise it comes from its last git commit (197), and only last from the file's time (none today). A fresh clone gives the same index as this box, which `scripts/dates.shale` checks on every full run.

## Two checks, at two moments

- **`scripts/fast.shale`** runs for each edit, in about 3 seconds of CPU (8 s of wall time on the busy box): gofmt, vet, a syntax check of the JavaScript, 44 tests, and a smoke test of commenting through the real server. Its last line is `fast: PASS`.
- **`scripts/full.shale`** runs before shipping, in about 28 seconds: the fast check, Go's race detector, an anchoring simulation of 187,000 edits on your real notes, the audit of every page, the dates check, and the bench. Its last line is `SAFE TO SHIP` or `NOT SAFE:` with the stages named.

Timing is judged by CPU per request, which a busy box can't break: the index is held to 400 µs (it measures 104–160), a note to 400 (136–179), and a page with comments to 800 (324–365). Wall-clock medians count only when the box is under half load, and otherwise the bench says "not judged". When the agent put back the old per-request scan as a test, the check failed it at 2,170 µs against 400.

## A planted fault found a broken test

The agent disabled the server's file watcher on purpose, so it would hear no changes, and expected a dozen tests to fail. Only three did. (Correction, 2026-11-14: this paragraph first said the planted fault was in the renderer. It was in the watcher, as Wednesday's journal records.) One of Tuesday's tests could panic, and its panic stopped every test after it from reporting. So a fault planted once, cheaply, found a test that had been hiding others. That's Thursday's argument in miniature, and why Thursday's prompt asks for one planted fault per stage.

## Cleanups the agent made unasked

- **The helpers** that the scripts had copied from each other now live in one place, `.shale/prelude.shale`.
- **Scratch files:** each script keeps its own scratch folder. Tuesday's audit used to wipe everyone's.
- **The audit** now fails on any leftover markdown, except three pages it names and counts.

## Calls you may want to unmake

1. **The server is Linux only now,** because of inotify.
2. **A note with no date in it keeps its last commit's date** while you edit it, until you commit.
3. **The comments folder's parent must exist** when the server starts.

## One thing outside the project

Passing 197 file names to git took 3.2 s, so the server now asks git about the whole folder (0.7 s). The rest of the cost is the old essay-repl-server repo, which is unpacked: 3,961 loose objects. A `git gc` there would bring the server's start from about 1.0 s to 0.4 s. It's a safe command, but it's your repo, so I've left it alone.

## Still by hand

- an eye test on a phone and a desktop browser;
- rerunning the bench when the box was busy;
- deciding about any new leftover the audit flags;
- reviewing the anchoring rate limits as the notes change.

Thursday's prompt takes on the first of these: a page that hides its reply buttons should fail a check, browser or not.
