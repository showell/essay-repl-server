# Where we stand

*2026-11-06. A short catch-up on everything but Rocco.*

## Safari

**On master, whole gate green, drawn hash still 3671023915:**

- All the specs are now `expect`s: 1,476 in the source, and `Grade` and `gates/expected/` are gone.
- `Across` has one origin, the middle of the lane.
- The code fix list is done, including the two earth radii. They turned out to be intentional, so they kept their values and got honest names.
- The widgets (cat, sky, bird, beacon), which now respond to touch as well as a mouse.
- The stacking rule, and the rule that an `if` takes braces, are in the guide. Safari hasn't been swept to the stacking rule yet.
- The naming checks run in safari's lints, each held at today's count.

**Running now:** the gate tiers from [the gates essay](safari-gates.md): a fast tier of about 10 seconds with a frame, warm caches at merge, debug wasm by default, and a publish tier. When that lands, Shale's time reporting comes next, with CPU-time budgets and "was 35 s, now 192 s" lines.

**Queued, in order:**

1. The safari stacking sweep.
2. The 16 nitpick renames, the `Beat` and `Beats` split, `Pixels` and the bare-F64 lint, one at a time. Each lowers a held count on its way to zero.

## The tutorial

Every code block and diagram now has a title line, and the icons moved out of the prose. The builder refuses an untitled diagram or a stray icon.

**Next:** the seventh draft on this site is behind the source, so I'll republish it after the sweep. Then comes the real page, on roc-markdown with the block hook you liked, plus the book stylesheet. Later chapters still need the Sky and Cat shape, and a fact-check pass has 13 `[check:]` notes to clear.

## Roc-chat

The rename is finished. `gopher-roc` is gone, and the project is roc-chat in every place that counts: the directory, the binary, the service, the prod paths and the docs. The old program is gone from prod, this box and GitHub, apart from the `roc-chat-original` branch. The runbook now describes only the program that exists. It's deployed at `e886dc9`.

The sweep took `app/` from 25,424 to 23,344 lines, and running the recipes on a second codebase fixed 9 things in them without moving any safari count.

**Running now:** four of your six picks: the twin type names, the `if` layout, `Timestamp`, and `github_id`.

**Small things left:**

- Five mentions of the old name in other repos, which I'll sweep once `roc-apps` is quiet.
- The cookies keep their `__Host-gopher_*` names, because renaming them would sign everyone out. Nobody is using it yet, so that's cheap if you want them changed.

## The box

The disk went from 28 GB free to 108 GB. Every repo is back to one worktree apart from running agents. On 2 cores, parallel agents are the biggest cost we have, so agents now stick to the cheap checks and I run one full gate at a time.

## Waiting on you

- An `@LC` in `projects`, to prove LC's renamed key.
- Removing the backup tar on prod once you're happy with the deploy, since it holds the chat's secrets. Tell me and I'll give you the command.
- Apoorva's GitHub sign-up, whenever it suits him.
