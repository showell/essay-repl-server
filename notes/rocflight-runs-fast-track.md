# rocflight runs Fast Track: the update for 2026-09-25

Yesterday ended with Fast Track running as Rust. Today was the other half:
Brian's interpreter, rocflight, running Fast Track as Roc.

## The headline

**rocflight's interpreter plays all 80 games of `exp_table`, and its output
matches the `roc` build's, all 98 lines.**

| exp_table, 80 games | time | peak memory |
|---|---|---|
| Rust translation (roc2rust) | 3.3 s | 6.5 MB |
| `roc build --opt=speed` | 3.6 s | 4.2 MB |
| rocflight, interpreting | 20.5 s | 22 MB |

So the interpreter is about 6× slower than compiled code on a real program.

The caveat is the platform. That run used rocflight's built-in `echo!` in
place of Fast Track's own `cli/` platform, with the app header and the print
calls changed in a scratch copy. The real platform works too, but only when
linked by hand; see "Still open" below.

**The ported corpus is at 521 of 521 on our fork.** The last three programs
needed `List.starts_with`. The gate run that showed 521 had its binary
replaced partway through, so a clean run is going now to confirm it.

## What it took: eight gaps, one at a time

Each gap stopped the run. Each got a small repro, a fix, and a test that fails
without the fix, and the run then went one step further. In the order they
appeared:

1. **An imported module's `expect`s ran with the app.** `roc` runs them only
   under `roc test`. In Fast Track, `ElmRandom.roc`'s expects call a helper
   outside its namespace block, and the app died on load with
   `Undefined variable: draws`. The app's own top level was already flattened
   carefully, and modules now go through the same code. *Sent: PR #1, its
   sixth commit.*
2. **`List.keep_if` / `List.drop_if` always returned a lazy iterator.** This
   happened even on a literal: `List.keep_if([1, 2, 3], p)` printed
   `<opaque>`. A call that names `List.` can't mean the lazy `Iter.keep_if`,
   so it now compiles to a loop. *Sent: PR #15.*
3. **Top-level constants were initialized in file order.** Roc lets a
   constant read one declared below it, and `Board.roc`'s tables read
   `squares`, declared three lines further down. rocflight now orders
   constants by what they read, including through the functions they call.
4. **Five `List` functions had no native implementation:** `join_map`,
   `find_last`, `map_with_index`, `starts_with` and `ends_with`. rocflight's
   pinned `Builtin.roc` declares all five, and nothing ran them.
5. **`Try.map_ok(t, f)` was unknown,** although `t.map_ok(f)` worked. The
   qualified form now reaches the same code.
6. **A platform named by a path** (`platform "cli/platform/main.roc"`) was
   refused: only a URL that `roc` had already downloaded could name one. It
   now resolves next to the app, as a local package already did.
7. **rocflight's host library didn't compile** after an upstream change to
   how type names are stored. It's a one-line fix, and no existing check
   builds that library, so nothing had noticed.
8. **Linking Fast Track's Zig host needs Rust's `libunwind.a`.** rocflight's
   host library is Rust, and a Rust host supplies that library while a Zig
   host doesn't. With it added by hand, rocflight ran both hello-world and
   `exp_table` on Fast Track's own platform.

## What the cold reviews caught

Every change gets a review from a fresh agent told to act as Brian's
reviewer, before anything goes out. Today that paid off three times:

- **PR #15:** the code was sound, but my explanation was wrong. I said the
  call went lazy only when the checker couldn't tell the receiver was a list.
  The reviewer predicted that every qualified call went lazy, and yesterday's
  binary confirmed it. The fix covered more than I'd claimed, and the PR now
  says so.
- **The constant ordering** broke two programs that run today, and the full
  gates passed anyway:
  - one where a lambda parameter shares a constant's name: `|b| b + 1` next
    to a constant `b`;
  - one where a function reads a constant only on a branch that never runs.

  I reproduced both, then reworked the fix. Names that a lambda, `let` or
  pattern binds no longer count as reads. Constants that seem to read each
  other keep file order, which uses the same method as a strongly connected
  components pass. Both programs are now regression tests.
- **The local-platform change** keyed its linked executable only on the host
  library's timestamp, which could leave it stale. The key now covers the
  platform's `main.roc` and every file in its link recipe.

## A correction you prompted: the pin

You asked whether I remembered that rocflight pins an old `roc`. I had been
sloppy about it:

- **rocflight pins `roc` nightly-2026-09-03.** Its vendored `Builtin.roc` is
  that compiler's, copied in by Brian's 09-17 commit, not a later re-sync.
- **Brian's `main` hasn't moved since 09-21**, before we started, and
  "upstream" in my messages always means his `main`.
- **Issue #5 was wrong.** It blamed the pin for `List.starts_with`, but the
  09-03 `Builtin.roc` declares it; rocflight just lacked the code to run it.
  #5 now has a correcting comment.
- **I re-checked every "`roc` prints X" claim** in the PRs and issues against
  the 09-07 nightly, the closest I have to the pin. All of them hold.

The rule now in memory: when a builtin fails, first check whether the pinned
`Builtin.roc` declares it, and verify claims against 09-07.

## Where things stand upstream

Brian hasn't responded to anything yet.

- **Sent today:**
  - PR #1's sixth commit (module `expect`s);
  - PR #15 (`List.keep_if` / `drop_if`);
  - issue #16: a program's own `Set` namespace collides with the builtin
    `Set`. `roc` runs both repro programs; rocflight rejects one and crashes
    on the other.
- **Ready, waiting on a clean gate run:** four PRs off Brian's `main`:
  - constant ordering (the reworked version);
  - the five `List` functions plus qualified `Try`;
  - the host-library build fix;
  - local platforms. This one says plainly that a Zig host still needs
    `libunwind.a`, and the link now names that library when it fails,
    instead of printing a page of undefined `_Unwind_*` symbols.

## Still open

- **Shipping `libunwind.a`.** The likely fix is to bundle it with rocflight,
  as rocflight already bundles its host library. That's Brian's design to
  decide, so it goes to him as a question.
- **A namespace member should shadow a top-level name.** Inside `Board`, a
  bare `count` means `Board.count` to `roc` but the top-level `count` to
  rocflight (`roc` prints `(3, 3)`). On Brian's `main`, the program fails
  with "Used before it was defined". An issue is being written.
- **An unannotated top-level number,** read by a constant declared above it,
  is typed as a fraction: rocflight prints `31.0` where `roc` prints `31`.
  It's the same file-order assumption, this time in the type checker.
- **Method syntax on a list, `[1, 2, 3].keep_if(p)`, is still lazy.** Brian's
  own comments explain why method syntax can't tell `List` from `Iter`;
  fixing it needs an iterator that is its own kind of value.
- **The other four Fast Track experiments** haven't been run on the
  interpreter yet; only `exp_table` has.

## Next

1. The clean gate run, then gate each of the four branches on its own, then
   send the PRs, citing 09-07.
2. File the name-shadowing issue.
3. Run the other four experiments on rocflight, one game first each time.
