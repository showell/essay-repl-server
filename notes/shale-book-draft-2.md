# The Shale book, draft 2

**Read it here:** http://143.244.172.148:9210/shale-book/

Eight chapters, each under 900 words of prose, built from the week's journals:
1. **Introduction:** who it's for, the side project, what Shale adds, gates, dialects.
2. **Monday: a server and a number.**
3. **Tuesday: replies that stay put.**
4. **Wednesday: a check for each moment.**
5. **Thursday: making the checks fail.**
6. **Friday: shipping should be boring.**
7. **Saturday: the language gets better.**
8. **How we work.**

I wrote the introduction and the close. Three agents drafted the days, two each, under the book's new `MISSION.md`, which holds all of your calls from yesterday. Every prompt and every script is quoted from its file at build time: prompts by `{{quote}}`, journal scripts by `{{fence}}`, and recipes by anchors. The editing pass for one voice is still to come, so expect seams between the days.

## What the drafters caught

- **My brief had a fact wrong,** and the drafter followed the journal over me. The fault that turned only 3 of 12 tests red on Wednesday was a deafened file watcher, not a renderer bug. The Wednesday essay said "renderer" too, and it's corrected.
- **The reply button became "reply" in two steps** (opacity first, with the "note" label, then the rename), and the chapter tells it that way.
- **The recipes need polish before they're quoted:** a bare number argument in `full.shale`, a leftover in `bench.shale`, and a long `if` in `fast.shale`. An agent is polishing them now, keeping every gate green. The book's anchors will tell us where the quotes moved.

## One design question, from Saturday's chapter

Shale now ends a stopped run's jobs, and `release.shale` keeps the old server it puts back. But there's a gap, which the drafter worked out from the code. If a release stops on a budget *after* the swap, while it's checking the new server, the new server is ended with the run, and the old one never comes back. Nothing serves until someone runs `rollback=1`. That's a loud failure in place of the old quiet one (an unchecked server left running), but it's still a failure.

Three ways to close it:
1. **Accept it.** The release's budget is about twenty times what a release uses, so this needs a runaway, and the stop says what happened.
2. **Keep the new server too.** That brings back the original trap.
3. **Run the swap and its checks as a child run.** The release script launches them with `run`, a separate Shale process. A child that stops on a budget just exits nonzero, and the parent, still running, puts the old server back. This uses Shale as it is today, and it's the same shape `run.shale` uses for its parts.

**I'd do 3.** It closes the gap completely, it's small, and it makes a good paragraph for Friday's chapter: a script that can't catch its own stop hands the risky part to a child it can watch.
