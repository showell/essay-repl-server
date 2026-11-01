# Walking Roc's tree natively in Shale: the tradeoffs

*2026-11-01. LC, for Steve. Tonight's state: roc-ast is in Shale at roc-chat's pin, and `roc_tree` reads every child Roc's printer emits.*

## How it works today

1. **`roc-ast`** (Shale's `tools/roc_ast`, 52 lines of Zig) links Roc's own `parse` module and prints each file's tree with Roc's debug printer, `AST.toSExprStr`.
2. **Shale's prelude** runs it as a program and hands the text to the host.
3. **`shale_host_roc.zig`** reads the text back into nodes (kind, span, attributes, parent, kids), which recipes walk as Shale tables.

The parse is exactly the compiler's. Only the hand-over is text, and that text was written for people to read, not for a program.

## What the text costs us

- **Shapes we have to guess.** Tonight's three reader bugs were all one fact we hadn't read: Roc's printer puts a node's head items on its line and every other child, of any kind, on a line of its own. We now follow the printer's code, but we're still reverse-engineering a format nobody promised to keep stable.
- **Unescaped strings.** The printer writes strings raw, so the reader has to guess where each one ends. Tested tonight: the valid one-line Roc file `x = "a\") (b"` is dumped as `(raw "a\") (b")`, and `roc_tree` stops with "a string that does not end". It fails loudly rather than misreading, but a repo holding such a string can't be linted at all, and nothing about that string is unusual.
- **Size.** roc-apps' dump is 51 MB, against Shale's 64 MB read budget. A bigger repo won't fit.
- **Speed.** Not a problem yet. roc-ast takes about 12 s on roc-apps; reading the text costs steps, not much time.

## The options

### A. Roc's parser inside the Shale binary

`roc_tree` would call `parse` directly and build Shale's tables from the tree in memory. There would be no text, no second program and no size limit.

**What stopped this before is gone:** Roc used to need Zig 0.16 while Shale uses our patched 0.17. Roc at roc-chat's pin needs 0.17, and roc-ast builds fine with our patched Zig.

**What still stands in the way isn't just coding time:**
- **Every Shale build would fetch Roc.** That includes gopher.elf, because zig-metal-unikernel compiles Shale's sources. It can be gated (only the Linux host needs `roc_tree`), but the gate has to hold in three build graphs: Shale's, metal's and the consumers'.
- **Roc's package archive is incomplete.** It leaves out `vendor/`, which `parse` imports. That's why roc-ast builds with `--fork=` pointing at a full Roc worktree. If Shale's own `zig build` needed a local Roc worktree, every checkout of Shale would need one too, including Cloud's and anyone else's. Fixing it means vendoring those files, or a patched package, or a change upstream.
- **Shale would carry Roc's churn.** Each Roc pin bump becomes a Shale rebuild, and a parser API change breaks Shale's build, not a side tool's.
- **A choice inside A: generic or typed.**
  - *Generic:* walk Roc's `SExprTree` structure in memory. Same kinds and attributes as today, so no recipe changes.
  - *Typed:* map Roc's AST node types to tables directly. Richer, but it follows every AST change, and recipes would need rewriting.

### B. roc-ast emits a format made for a program

roc-ast walks the same `SExprTree` *in memory*, rather than calling its printer, and writes each node with explicit structure: kind, span, attributes, children, and escaped strings. Shale reads that instead of guessing.

- **It fixes the real problems:** no guessed shapes, no unescaped strings, and the reader becomes simple.
- **It costs nothing in Shale's build.** It stays a separate program, so metal and every checkout are untouched.
- **Size:** a compact line format, one node a line with explicit parent ids, is about the size of today's dump. JSON would be bigger and push roc-apps over the read budget, so not JSON.
- **The only blocker is the time to code it,** about a hundred lines in roc-ast plus a simpler reader in Shale. Recipes don't change: same kinds, same fields.
- **It keeps the two-step pipeline:** a process boundary and a per-call file list. That's fine at our scale.

### C. Leave it as is

It works on every file we have tonight. But the unescaped-string hole is real, and the next printer change could break us again.

## Recommendation

**B now; A when it pays.** B is the step whose only blocker is coding time, and it removes the two real problems: guessed shapes and unescaped strings. A becomes worth it if the read budget or speed starts to bite, or once Roc's package includes `vendor/`. B's in-memory walk of `SExprTree` is also exactly the code A would need, so B isn't wasted work if we go to A later.

**How B would be proven:**
- Every tracked `.roc` file in the five repos gives the same nodes under the old reader and the new one.
- A test with a string literal holding `") (`, which the old reader gets wrong and the new one gets right.
- The 13 recipe self-tests and roc-chat's verify pass, plus one plant.
