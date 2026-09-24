# Fast Track toward Rust: where it stands

Today's thread, from "tackle the three" to "port Fast Track". It is written to
get you up to speed before we compact.

## The six parked programs, and issue #11

The three `roc_iter_*` programs turned out to share a cause with three more:
`eq_generic_recursive`, `hamt_test` and `list_test`. So it is six of the 15
roc2rust failures, not three.

The cause is in rocflight's parser. A type that is referred to before its
declaration is finished loses its arguments. That covers a type inside its own
definition (`ConsList(a)` inside `ConsList`) and a forward reference (`Iter_(a)`
naming `Step(a)`). Either way the reference becomes a stand-in with the name
and no `(a)`. rocflight runs these programs correctly anyway. What is lost is
only the information a translator needs: Rust has to write `ConsList_T<i64>`,
and nothing says `i64`.

Neither roc2rust nor rocemit can repair it from outside. The real fix is to
let a named type carry its arguments. That touches rocflight's core type in
about 112 places. It is the design question #11 already put to Brian, so I
added the new facts to #11 (self-references too, six programs, the shape of
the fix) and parked the six, as you said.
Brian has not answered any of our PRs or issues yet.

## Fast Track as the new target

The Fast Track experiments are small command-line apps. `exp_table`,
`exp_cards` and the rest run whole games through the rules, the search and the
strategy, and print a log that `run_exp.sh` makes deterministic per seed. The
same app built by `roc`, with its log compared line for line against the Rust
one's, is the oracle. It is the same kind of check as the ported tests'
`expected/` files, over about 4,300 lines of real Roc instead of emitted Roc.

**All five experiments now get through rocflight's checker and roc2rust, and
out as Rust.** None compiles yet: `exp_table` has 45 rustc errors, in the
five kinds listed at the end.

### Found on the way in: two rocflight bugs

1. **A module and another module's type that share a name.** The module
   `Player` is `Player :: [].{ .. }`, and `Type.Player` is the player record.
   rocflight looks types up by their last segment, so inside `Player.roc` the
   annotation `Type.Player` meant the file's own empty namespace. Every
   function there failed with "cannot unify the player record with `[]`".
   `Game` and `Move` had the same problem. `roc` is fine with it.

   **Fixed:** a qualified type whose qualifier is not one of this file's own
   types is the import's. It has a regression test (3 small files) that fails
   without the fix. It is committed on `codex-emit` and belongs on PR #1,
   which introduced module loading. Its gates are green, and it is now PR
   #1's fourth commit.

2. **An open record that meets a closed one stays open.** Search's
   `distinct_lines` folds a list of `{ key, i, line }` records. Inside the
   fold, `k.key` gives an element type that is an open `{ key, .. }`.
   Appending a whole `{ key, i, line }` to that list never closed it. So the
   later `a.i` saw a record with no `i`. rocflight has no row variables, so an
   open record cannot learn its other fields from the value it meets.

   **Fixed** the way the checker already grows an open record when it reads a
   new field: when an open record unifies with a closed one, every variable
   bound to that open record is rebound to the closed one. It has a test that
   fails without it. It changes unification, so it waited for the full gates.
   They came back clean: the corpus is still 518, the round trip 514, roc2rust
   506. It went to Brian as its own PR, #12.

   The same gap exists for open tag unions (`[Solo, ..]` never closes to
   `Team`), and it is one of the remaining error kinds below.

### What roc2rust learned

- **Loops and statements:** `var $x`, `while`, `for x in list`, `break`,
  `return`, `expect` and `dbg`. A loop is labeled: a `match` is a labeled Rust
  block, and an unlabeled `break` inside one is a Rust error.
- **String interpolation.**
- **Method calls:** `xs.concat(ys)` and `c.bump()`. The receiver's type names
  the module, and the receiver becomes the first argument.
- **Builtins fasttrack uses:** about twenty list functions (`keep_if`,
  `join_map`, `find_first`, `sort_with`, `map_with_index` and others),
  `Str.join_with`, and `Try.map_ok` and `Try.is_ok`.
- **A builtin's `Err`** carries the program's own tag (`NotFound`,
  `OutOfBounds`). `sort_with`'s `[Before, Same, After]` becomes Rust's
  `Ordering`.
- **The cli platform's `Echo.line!`.**

### Tests, and how Roc tests fit

You asked for tests on the bigger constructs. roc2rust now has its own
`codex/rust-tests/`: small Roc programs, each with what `roc` prints, run by
`codex/rust.sh --tests`. There are three so far: `loops`, `dispatch` and
`open_record`. The two rocflight fixes have Rust tests in rocflight's own
suites (`lang_test`, `types_test`), each checked to fail without its fix.

**On Roc tests in general.** Fast Track's own tests are Roc `expect`s, run by
`roc test`. rocflight already lifts top-level `expect`s out of a file
(`lift_expects`, for its test mode). My proposal: a roc2rust test mode that
writes every `expect` in the program's modules as a Rust `main` that runs them
all and prints `All (N) tests passed` as `roc test` does. Fast Track's expects
would then check the Rust translation from the inside too, beside the logs
checking it from outside. That also gives a coverage question a direct
answer: a function no `expect` reaches and no experiment calls is untested in
both languages.

## What is next (after compaction)

The remaining rustc errors in `exp_table`, by kind:

1. **`Bool.not`** is missing from the runtime. This one is trivial.
2. **The shift amount** of `U64.shr_zf_wrap` gets typed as `u64` where the
   runtime takes `u8`. The runtime will take any integer.
3. **`List.map_with_index(List.repeat(0, n), |_, i| i + 1)`** is how Fast Track
   writes 1..n in four places. The `0` is never used, so it defaults to `Dec`.
   This is the case you described, where the translator stands in for a human
   reader. The idiom is correct, but it builds a list of zeros to count. A
   small `range` helper in Fast Track says what it means, and the problem goes
   away rather than being worked around.
4. **Open tag unions** do not close (the gap in fix 2 above), and a lone
   `Ok(..)` is written as its own union rather than `Result`.
5. **Lambda parameters in generic functions** are written `_`, which rustc
   will not infer inside `Rc::new`.

Then: compile `exp_table`, run it with fewer games, and diff its log against
`run_exp.sh`'s. After that, the `expect` test mode.

## Loose ends

- The two rocflight fixes are with Brian: the qualified-type fix on PR #1,
  the open-record fix as PR #12.
- The gate script lives in the scratchpad. `check_roc` and `check_examples`
  must use the 09-07 nightly: on 09-22, `roc check` exits non-zero on
  warnings, and every pair fails.
