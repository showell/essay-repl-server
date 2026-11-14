# The cookbook, as a catalog

*2026-11-14. What's in Shale's cookbook, grouped by the job each recipe does rather than by the language it reads. Each group is specific to Steve's work, and each one is a shape any project can use.*

The cookbook holds about ninety entries in `shale/cookbook/`: recipes you run, and libraries a recipe loads with `use`. Agents wrote every one, each the moment some real work needed it. Read by folder, it looks like a Zig, Roc and Go toolbox. Read by job, it's eight kinds of automation that any project has, with Steve's languages filling them in.

## 1. Guard a run before it starts

`check_disk_space` stops a run when the disk is low, and `check_conflict_markers` stops one when a file still holds git's markers. `check_syntax` checks each file by its kind: Zig, Roc, JavaScript, Shale, Python, shell. `check_seals` holds a Zig rule about where a value may be made. `check_recipe_names` holds the cookbook to its own naming standard.

**The general shape:** fail at the start, with one line that names the problem, so nothing fails halfway through. Every project has a disk, git and files in several languages.

## 2. Run a tool, and keep only its verdict

`run` runs a command line and prints how each program ended, its time and the lines that matter. `run_zig_build` does that for one build step. `build_on_github` sends a long build to GitHub instead of the box. `fetch_page` fetches a page and prints its status and its important lines, or waits until the page says something. The `times` library compares a stage's time with its recent runs.

**The general shape:** a tool talks too much, and the agent needs the verdict. Wrapping each tool once, and naming its verdict, is the commonest recipe there is.

## 3. Read code through its own parser

The hunts: `find_smells`, `hunt_names` and `find_deep_calls` for Go, Roc and Zig. Also `find_dead_code`, `find_clones`, `find_unused_imports`, `find_bool_flags`, `check_name_types`, and a dozen more. Each reads a language through that language's own parser, never with regular expressions. Go comes in through a small tool built on Go's own parser library. Roc and Zig come through their compilers.

**The general shape:** a hunt is a parse tree, a few rules, and plants that prove each rule fires. That it's Go, Roc and Zig is an accident of history: those are the languages this work happened in. Any mainstream language with a parser can be wired in the same way. Covering the ten most popular languages would be a fine project for someone whose work is in them.

## 4. Refactor, with the proof attached

`rename_words`, Roc's `rename` and Zig's `rename_member` rename across a tree, whole words or whole identifiers. `split_file`, `tidy_file`, `add_missing_pubs` and `rewrite_call_args` move and reshape Zig. `rewrite_method_calls` rewrites Roc calls, and the compiler judges each one. Then come the proofs: `judge_move` and `check_same_tests` show a move changed nothing, `check_const_unchanged` that a constant kept its bytes, and `check_comments_only` that a change touched only comments. `write_tree_patch` turns an edited copy into one patch. Many run under `--undo-on-stop`, so a failed refactor puts every file back.

**The general shape:** a refactor isn't done until something proves it changed only what it meant to. The cookbook pairs every rewrite with its judge.

## 5. Upgrade a toolchain by counting first

The `zig17/` recipes carried a whole family of repos from Zig 0.16 to 0.17. `count_upgrade_changes` counted what each repo used that had changed, and then three rewrites did the mechanical part.

**The general shape:** a compiler upgrade is a census, then rewrites, then the build. Any language that ships breaking releases gets the same three steps.

## 6. Gate the prose too

`find_negatives` finds the sentences a book's voice rule rewrites. `build_term_index` finds the terms a book uses before it teaches them. `find_phrase` finds a phrase across line breaks and edits it. The first two came over from the Roc book today.

**The general shape:** writing gets gates the way code does. Docs, READMEs and books all have rules that can be held mechanically.

## 7. Work with git and the outside world

`merge_conflicts` is a library that parses a conflicted file, so a resolution is a few lines. `prune_merged_branches` finds the branches already merged. `look` shows lines by number across folders, mounts or a git revision. `read_zulip_topic` and `listen` read a chat, one in Zulip and one in Steve's own chat app.

**The general shape:** the services every team uses, wrapped once so an agent stops reinventing them.

## 8. Read back what the agents did

`read_wants` reads the log of every time a script used the gate's escape, with counts by kind and session. `color_shale` turns Shale into colored HTML pages.

**The general shape:** agents leave a record, and a recipe makes it readable at a glance.

## The story the catalog tells

Every recipe is specific, and every group is general. The cookbook grew the way Steve's work grew: a Roc book, a Zig upgrade, a Go server, a chat app. Nothing in it was built in advance of a need, which is what "Shale isn't speculative" means in practice. Your cookbook would grow from your work in exactly the same way: the same eight jobs, filled in with your languages, your services and your rules.

That's also the strongest case for adopting Shale. You get Steve's recipes, but they matter less than the habit behind them: every repeated task becomes a recipe, every recipe has a self-test with plants, and an agent reaches for the cookbook before it writes anything new.

## For the book

- **Meet Shale** can carry a short version of this: the eight jobs, one line each.
- **A keeper per chapter** can come from these groups. For example, the commit gate (group 2), a hunt (group 3), a refactor with its proof (group 4), and a prose gate (group 6).
- **The accident of history** gets one plain sentence, so a reader working in Python or TypeScript sees their own cookbook in it, not Steve's.
