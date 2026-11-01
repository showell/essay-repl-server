# A day of judges

*2026-11-01. LC, for Steve: a look back over today, across roc-chat, Shale
and the Roc apps.*

Two projects ran side by side today, the browser client for roc-chat and
Shale's Roc refactoring tools. They kept rhyming. The same idea turned up
in both, in different clothes: **progress comes from a better judge.**

## A judge that sees more

In the morning, `methods.shale` could only rewrite `Module.fn(x)` as
`x.fn()` by trial: write every candidate into the file, let `roc check`
object, and work backwards from the errors. It was honest but blunt. We
spent the morning teaching it to read the compiler's complaints better: a
missing method reported on the line that defines a value, and a warning on
another line caused by a bad rewrite. Each fix was real, and each one
showed how much the recipe was guessing.

Then route B landed. `roc-types` links the compiler's own checker, walks
every expression and prints its type: 83,000 typed nodes across roc-chat in
under five seconds. With types, `methods` stops guessing which calls might
be wrong. The gate result was the moment of the day: **411 rewrites where
the trial loop alone found 77, losing none of the 77.** The other 334 had
been valid all along, thrown away beside a wrong-typed neighbour or a
stray error. The tool wasn't too cautious. It was blind, and now it can
see.

The chat work had the same shape. The browser client is a port, and a
port has a judge waiting for it: the old app. Every step went past a cold
reviewer whose first question was "where does this differ from Gopher
Chat, and why?" Those reviews found things no test would: a colour hash
that gave 16% of channel names a different colour; a Recent stream whose
audience had become a third copy of the read rule; a scroll guard missing
from one callback. Each was a small divergence from a program people
already trust. Steps 1 to 5 are merged, steps 1 and 2 are live, and step 6
is under review. Recent, the page everyone uses constantly, matches the
old one tile for tile, colour for colour.

`roc-types` and the cold review are the same move. Each finds an oracle
that already knows the answer, the compiler's type checker in one case and
the old app in the other, and asks it directly instead of reconstructing
its verdict from the outside.

## The recipes and the code judged each other

The afternoon's sweep turned Shale's recipes loose on every Roc program we
have, mostly toys, plus safari and FastTrack, which deserve real care. The
stated goal was finding flaws in the recipes, and it did: missing verbs
(`draw`, `play`, `sleep`, `begin`), a `fixed` check that would have broken
roc-markdown's renderer, a boundaries rule that measured decisions in
lines instead of in the tree, and a self-test that couldn't see a
misnamed plant.

But the judging ran both ways. The recipes found habits in our own Roc:
placeholders like `?? "bogus"` where a crash belongs, `List.set(...) ?? l`
copying FastTrack's board on every move, Bool flags passed by position,
and 54 copies of one test helper in safari. Some fixes went into the
code. Some went into the guide, since roc-style.md and CLAUDE.md now say
that a placeholder isn't a value, that a `{}`-function is a constant
unless it's generic, and that `crash` is a keyword. Some went back into
the recipes, as new checks: `short_name`, `constant`, `set_fallback`,
`placeholder`, `entry`, `worker_name`.

That is a healthy loop. A rule is proposed, run over real code, argued
with, sharpened, written down, and enforced. Your policy answers and the
"go with your recommendations" calls kept it moving without making it
bureaucratic.

The best small example: the boundaries recipe told roc-markdown to drop a
parameter that its own recursive calls varied. Fixing that bug produced a
better rule than the original. A recursion's start belongs in an **entry
function**. That led to your naming question, and now the convention has
words: the entry function takes the plain name, and the worker is named
for what it adds, `_from`, `_onto` or `_with`. It began as a false
positive and ended as a guide rule, a check and a rename sweep.

## One home, again and again

The doctrine that kept surfacing was one home for a rule:
- roc-chat's read rule (`Topics.readers`) and its stream-resume arithmetic
  each collapsed into one function after review;
- `roc-types` got one reader, `types.shale`, for every recipe;
- safari's gates moved out of a scratch folder into
  `canvas_apps/safari/gates/`, with their expected outputs beside them;
- styling moved into the JS widgets that own the DOM: delete a widget and
  its styles go with it;
- generators now generate proper code. FastTrack's square values and Dog
  Park's page data are fixed at the source, not excused as "generated".

Each of these removes a place where two things could drift apart, which is
what most of today's bugs were.

## Letting go is progress too

Some of the day's best work was deletion. Dog Park's native game on
roc-ray went, then its Windows workflow, its art, `Game.roc` and the game
judge. The roc-ray upgrade had a careful discovery plan, and its real
value was showing the cost: a Roc nightly move for all of roc-apps,
shaders reworked. The decision to punt came from knowing that cost. The
canvas apps keep their native side, labelled honestly as a spike that
proved its point. Dog Park ends the day smaller, with every gate green and
its page data byte-identical.

## The box as a collaborator

The day had a rhythm by the afternoon:
- Cloud building chat steps;
- four cold agents at a time, each with a short, specific brief;
- verifies running niced and detached;
- heavy builds sent to GitHub.

That last habit came from the box itself. Linking the compiler locally
swamped it this morning. The lesson became architecture: `roc-types`
builds only on GitHub, publishes as a release asset, installs with a
checksum, and Shale's CI confirmed the whole path green by evening. A
constraint turned into a cleaner pipeline than we'd have built without it.

Small shared fixtures matter too. One symlink, `~/build/lanes/roc`, turned
out to be load-bearing for every roc-apps worktree. Now it's permanent and
written down.

## Where things stand

- **Safari:** cleaned up, formatted, its gates in the repo, live on
  roc.lynrummy.com, and getting its worker names fixed now.
- **FastTrack:** a frozen solver test, a gold check, cleaner Roc, and a
  generator that writes code the formatter accepts.
- **Shale:** about fifteen recipe improvements merged today, and a
  type-aware `methods` waiting for its moment.
- **roc-chat:** halfway through the browser client, with the hard parts
  (live updates, compose, Recent, selection and keys) behind us.
- **Dog Park:** its image building for deploy, with the TODO list riding
  along on the same metal.

The thread through all of it is a better judge. When the compiler, the
old app or the formatter already knows the answer, asking it directly beats
reconstructing its verdict. When no judge exists, the work is to build
one: a frozen solver test, 54 spec outputs, an 11-game gold check. Then
the rest of the work goes faster and safer.
