# While you were reading: Saturday's work

Your server on 9301 is running the newest build. It went out through the release script just now, by the new child-run path you chose, in 24 seconds, with all 7 of your comments where they were. Here's what landed since this morning. Reply anywhere.

## Shale got two features today

- **A stopped run ends the jobs it started** (unless one is started with `keep_on_stop`). It passed Shale's full test suite and the consumers gate, the gates of every repo built on Shale, and it's merged and pushed. On the way, I fixed a test that was already failing on Shale's master: a recipe called a function declared below it.
- **Go, read by its own parser.** `go_tree` is a new built-in over a small `go-ast` tool, sharing one reader with Roc's tree. Three Go hunts sit on top: names, nesting and smells, each with fixtures in the style of Go's own analyzer tests. It passed the consumers gate and is pushed too.

## What the Go hunts found in essay-surface

Very little, which backs up your "it always just kinda worked":
- **Names:** no vague function names and no misnamed bools. A few `info` and `item` locals, and two of those are CommonMark's own term.
- **Nesting:** nothing four calls deep.
- **Smells:** `markdown.go`'s `inline` (117 lines) and `link` (91) are long and nest five deep, and `tight` and `image` are bool flags.

**Is this worth a short section in the book?** A hunt that finds little in good code is honest evidence, and the two long functions would make a natural "the hunts point at the next refactor" moment.

## The release is safer

The swap and its checks now run as a child run. On dev, a runaway loop was planted in the child's checks. The budget stopped the child, the parent put the old server back, and both test comments were on its page. The real release you just got took that path's good side.

One leftover the agent noticed: after a *failed* release, there's no `.prev` binary left, so an immediate `rollback=1` refuses. That was true before today's change too. **Fine as is?** A failed release has already put the old server back, so there's nothing to roll back to.

## The recipes read better

Before the book quotes them:
- `full.shale`'s stages are a list of named rows;
- `fast.shale`'s known-bad check is four named checks, each proved to fail once;
- `bench.shale` lost a leftover;
- `release.shale` has clearer names and no repeated block.

Every gate stayed green, and the book's anchors caught the one quote that moved.

## Draft 2 kept up

- **The roles:** Monday's and Tuesday's prompts say "I write notes" and "I read those comments". The book now says, once each, that the agent writes and you reply.
- **Friday** now quotes its release as it was on Friday: the build's `{{show}}` include can quote an old commit between two anchors.
- **Saturday** quotes the child run, and says `keep_on_stop` went into Shale's main line, with a reader's own fork as where a dialect begins.
- **The length gate** caught Saturday at 903 words, so one sentence went.

http://143.244.172.148:9210/shale-book/

## One small thing outside the book

The cross-repo doc check flags two paths in roc-chat's `docs/code-quality.md` (`roc-apps/CLAUDE.md`, `roc-apps/docs/roc-style.md`) as gone, though both files exist. It looks like a doc-check quirk, not a dead link, and it predates today. I'll look into it when we're between books.
