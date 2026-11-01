# Shale's Roc tools: roc-parser for syntax, the compiler for types

*2026-11-01. LC, for Steve. A catch-up and a design sketch: where Shale's Roc
refactoring stands, the move toward Luke Boswell's roc-parser, and how we get
**type information** out of the compiler now, without waiting for `roc tooling`.*

## Where we are

**Shale's Roc recipes read one tree,** `roc_tree`, which comes from `roc-ast`:
our small Zig wrapper that links the compiler's `parse` module, pinned to
roc-chat's Roc (nightly 10-30). Its `--flat` output carries a versioned header.
Five recipes run on it:

| recipe | what it does | reads types? |
|---|---|---|
| `nest_depth` | flags deep nesting | no |
| `errors` | error-handling style checks | annotations, syntactically |
| `boundaries` | module and effect boundaries | annotations, syntactically |
| `name_hunt` | naming rules, e.g. tags in command tense | declared tag unions, syntactically |
| `methods` | rewrites `Module.fn(x, ...)` as `x.fn(...)` | **needs them; asks the compiler by trial** |

**The roc-parser experiment (Cloud, last night)** produced a Roc emitter that
writes roc-parser's tree in roc-ast's `--flat` shape, so `roc_tree` reads
either.
- **`nest_depth` is identical** on every repo, including roc-apps' 1,452 files.
- **`methods` is identical** on 2,578 candidates. The one difference was a bug
  in `methods.shale` itself (a `match` the compiler gives no span), fixed and
  merged this morning.
- **Spans over 1.2M compiler nodes:** the only real disagreement is #101, a
  function type inside parentheses starting one byte early. It occurs 311 times
  in that corpus.

## #101 doesn't block us

You're right. The bug moves the **start** of an inner function type by one
byte, onto its `(`. Nothing else is affected.
- **Most likely no recipe depends on that byte,** though I haven't checked
  this recipe by recipe. Our recipes mostly read a type annotation's *kind*
  and *children*, and `nest_depth` and `methods` came out identical. The
  old-against-new runs below settle it for the other three.
- **It's being fixed anyway.** Luke's PR #102 fixes it and widens his oracle to
  compare every node's span (that oracle flagged 1,105 of 2,606 function types
  before the fix). His CI is red for reasons he names on `main` too: basic-cli's
  `Stream` warning, and a compile hang on nightly 10-31.

Cloud's caution ("keep roc-ast for the type-reading recipes until the paren
span is fixed") was conservative.

**The migration I'd do:**
1. **`nest_depth` and `methods`:** read roc-parser by default now. Both are
   proven identical.
2. **`errors`, `boundaries`, `name_hunt`:** run old against new over every repo,
   as Cloud did for the first two. Any difference that isn't one of the 311
   paren starts is a finding; then switch.
3. **roc-ast stays,** as the compiler's ground truth for cross-checking spans,
   and as the place our type work (below) starts.

**What roc-parser costs us:** about 500 lines of Roc in the emitter, a second
parser to pin, basic-cli as a build dependency, and output about twice
roc-ast's size. **What it buys:** a parser written in Roc, typed nodes with
comments and whitespace kept, error recovery, and Luke's maintenance and fuzzing.

**What it doesn't buy: types.** roc-parser is syntax only. Luke on Zulip: "Just
syntax", and a type checker in Roc "would be epic" but is a massive job. **So
the plan has two tracks: syntax from roc-parser, types from the compiler.**

## Why we need types: `methods.shale`

`methods` is the recipe you were remembering. It proposes `Str.concat(a, b)` →
`a.concat(b)`, but a syntax tree can't say whether `a` is a `Str`. So it trial-
writes each candidate into the file and lets `roc check` judge. A `missing
method` error means the first argument wasn't the module's type, and the call
is put back.

**On roc-chat's `app/` that's 2,578 candidates for 68 rewrites:** about 97%
are tried only to be refused. It costs:
- a cap of 64 programs a run, so a tree takes several runs (`from=N`);
- about **7 GB of Roc cache** from one pass over roc-chat;
- attribution trouble: an error is tied to a call by line, so an error the
  compiler reports on the line that *defines* a receiver is blamed on no call
  (Cloud's open item, `Topics.roc:482`).

**With types,** `methods` would ask one question per candidate (what is the
first argument's type?), keep only those whose type is the module's own, and
run `roc check` once per file, to confirm. The trial loop becomes a
confirmation.

## Luke's `roc tooling` proposal, in brief

Grounding, from [Luke's summary gist](https://gist.github.com/lukewilliamboswell/b477d6f6024fc43b9c3d5784a5da20af)
(his agent's synthesis of the threads, checked against the compiler on 1 Nov):
- **The idea:** a tool written in Roc (`SomeLinter.roc`, `SomeLSP.roc`) runs on
  a platform the compiler supplies, as glue does today. The compiler owns
  parsing, names and types; the tool owns the protocol and the logic. Invoked
  as `roc tooling lsp.roc` or `roc tool <plugin.roc> <app.roc>`; neither name is
  settled.
- **What it would expose:** the AST, the CIR (names resolved), types, symbols
  and diagnostics, perhaps the LIR.
- **The open question is the API:**
  - S-expression dumps are easy and good for experiments, but they mirror
    internals and break when the compiler changes;
  - typed Roc data plus compiler operations is the long-term direction, but it
    needs decisions on identity, snapshots and compatibility.

  Richard objected to a file-dump as the *foundation*, since the interactive
  engine needs a live session. Luke suggested dumps for throwaway experiments.
- **Richard's persistent engine:** keep modules in memory, re-check only the
  declarations an edit touches, answer queries about types, references and
  definitions. This is proposed, not built.
- **Status:** `roc tooling` is not implemented. Luke calls it "on the horizon",
  outside the immediate priorities.

**What already exists at our pin (0602c5f), and matters to us:**
- **An embedding API:** another Zig program can import `compile`, `check`,
  `base` and the rest from a pinned Roc commit, drive `Coordinator` through
  checking, and stop there. `test/downstream-compiler` is a working example.
  `src/compile/README.md`, "Embedding", calls it "stable in shape".
- **`roc experimental-lsp`,** in Zig, with hover, definition, references,
  rename, inlay hints and code actions, **all computed from checked types.**
- **The snapshot tool** prints inferred types for every definition and
  expression of a single module (the `# TYPES` section of
  `test/snapshots/*.md`), but without regions.

## Getting types now: four routes

**A. Drive the compiler's LSP from Shale, in batch. Proven today.**
I ran `roc experimental-lsp --stdio` from a Shale heredoc with one framed
batch: initialize (with `trustedWorkspace`), open a file, three hovers, inlay
hints, shut down. **It answered in 26 ms:**
- hover on `shout` gives `a -> b where [a.concat : a, c -> b, ...]`;
- hover on the literal `2` gives `Dec`;
- the inlay hints give `n : U64`, each with the text edit that would write the
  annotation.

**Zero compiler changes.** This is what `methods` needs: hover on each
candidate's first argument.

To find out:
- whether it resolves types **across modules** of an app (trusted mode compiles
  dependencies, so it should);
- the cost on a 1,500-line file;
- whether hover always lands on the expression we mean (positions are UTF-16).

The types come back as rendered strings, which is enough to answer "is this a
`Str`?" but not for richer questions.

**B. `roc-ast --types`: link the checker, as we link the parser.**
roc-ast already links `parse`. The embedding API lets it run `Coordinator`
through checking, then walk the checked module and print, for every expression
and pattern, its **region and its type** in the flat format: one more record
kind, `t node type`, and a header version bump.
- **Our pin and our code,** like roc-ast today.
- **Every expression, not just hover points,** with the same regions as the
  syntax tree, so `roc_tree` nodes get a `type` attribute.
- **The work:** learning the `check` module's types store and renderer. The
  snapshot tool's `# TYPES` code is the model, and the LSP's hover code is the
  other.
- **The risk:** internal APIs move between nightlies, and we pin anyway.

**C. Upstream: region-tagged types from the compiler.** Long term, and
aggressive. A `--types` output that tags each expression with its region,
built from the code the snapshot tool already has, is useful to anyone
building tools now. It fits Luke's "dumps for experiments" and the playground's
need. Beyond that:
- the embedding API grows a supported query ("type at region",
  "references of symbol");
- references and rename work across modules (both are one-document only
  today);
- these become the first operations of the `roc tooling` platform.

We'd propose these with evidence from A and B: here's the tool, here's what it
needed, here's the data.

**D. rocflight's checker. Not for this.** rocflight (our Rust interpreter) has
its own bidirectional checker, and it passes all 1,953 of roc's eval tests. But
it's pinned to nightly 09-03, and its README lists real gaps for a type oracle:
nominal type arguments are dropped (`Dict(Str, U64)` and `Dict(I64, Bool)` are
one type), and `where` constraints aren't verified. The compiler is the arbiter;
rocflight's value here is experience. We have already written a Roc type
checker, and we know where its hard parts are, which helps when we read the
compiler's checker for route B.

## The first experiment

**`methods.shale` with types from the LSP (route A).**
1. Per file, one LSP batch: open the file (and what it imports), hover on each
   candidate's first argument, and read the type's head (`Str`, `List(...)`,
   the module's nominal).
2. Keep only candidates whose type is the module's own. Run the rewrite and one
   `roc check` per file.
3. **The test that can fail:** over roc-chat, the result must equal today's,
   the same 68 rewrites and every left call accounted for, in far fewer
   programs and without the 7 GB of cache.
   - Fewer rewrites means hover missed some.
   - More means trial-and-error was rejecting some for other reasons; each one
     gets read.

If A is fast and exact enough, `methods` keeps it, and B waits until a recipe
needs every expression's type. If A struggles (cross-module, positions, speed),
B is next.

## Questions for you

- **Go ahead with the migration of `nest_depth` and `methods`** to roc-parser
  by default, and the old-against-new runs for the other three?
- **Start with route A in `methods`,** as above? It's one recipe, and the
  comparison is the gate.
- **Upstream:** I'd write up route C once A or B has evidence, and hold it
  until then. Agreed?

## Sources

- Luke's gist, read today (`roc-tooling-design.md`).
- The compiler at 0602c5f: `src/compile/README.md` "Embedding", `src/lsp/README.md`,
  `test/snapshots/*.md` (`# TYPES`).
- rocflight's README.
- Shale `cookbook/roc/methods.shale`'s header; Cloud's report (roc-chat
  conversation 3, #27); roc-parser #101 and PR #102.
- The LSP spike: a Shale heredoc, `roc experimental-lsp --stdio`, 26 ms.
