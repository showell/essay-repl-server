# Style proposals from the 2026-11-01 sweep

*2026-11-01. LC, for Steve: what the Roc sweep (Shale's syntax-only recipes over our Roc apps) suggests for roc-apps' guides. Drafts only; each rule and each policy question is yours.*


Branch `box/style-sweep` in roc-apps (worktree `~/build/lanes/style-sweep`), off
master `e1bbb6b`; not pushed or merged. Two commits: `d91a5ac` (roc-style.md),
`317b71d` (CLAUDE.md). Yours to keep, edit or drop.

## Proposed rules

| rule, in one line | where | evidence |
|---|---|---|
| A placeholder is not a value: crash where the index can't be wrong, tag the absence where it can | roc-style "Errors and failure", after "a case that can happen"; pointer in CLAUDE.md §12, cross-link in §7's six shapes | fasttrack Board.roc:132 `?? "bogus"`, Arena.roc:150,153 `?? "?"`, Arena.roc:78 and Tables.roc:25 `?? 4` for no winner, Piece.roc:27,30 `?? l`; safari `Arc.no_frames = 1e9`, TruckSpec.roc:48 |
| A pure function taking only `{}` is a constant, unless generic over a type variable or heavy at compile time | roc-style "Name what travels together", after "a parameter every caller passes the same value" | snake SnakeDraw.roc:82 `board`; roc-chat Access.roc:63 `signed_out`, :421 `everywhere` (generic over `id`, so they stay) |
| A top-level value or a field is never one letter; locals and lambda params may be | roc-style "Naming", after "plain word" | snake SnakeDraw.roc:19-22 `w`, `h` |
| A state that changes in steps names each step, even two deep | roc-style "Layout", after the nest rule | fasttrack Game.roc:50,52, Piece.roc:110 |
| A test module apart from its code is `<Module>Spec.roc`, which the hunts read as tests | roc-style "Testing and enforcement", second bullet | safari README:36 (54 `*Spec.roc`); boundaries.shale:150 `is_test_file` |
| `List.fold_with_index` and `List.from_iter(U64.until(0, n))`, never `map_with_index(xs, \|_, i\| i)` | roc-style "`Str` and the builtins at the pin", the fold sentence | fasttrack Piece.roc:108; Builtin.roc at 0602c5f lines 4988, 3970, 12761 |
| An experiment or benchmark calls the code it measures, never a copy | CLAUDE.md §7 (measuring) | fasttrack Search.roc:185 = exp_search_size.roc:120 |

**Already covered, so not added:** crash on the impossible and no optionals
(roc-style "Errors and failure") carry most of the placeholder rule; the new
bullet only names the sentinel. "A call nested three deep... else a named middle
step" (Layout) covers three-deep state pipelines; the new bullet extends it to
two. "One home for a rule" (Principles) is the root of the experiment rule.
"A flag a caller passes is a tag" already covers fasttrack's Bool parameters.

**The generic-constant answer:** a constant can't be generic. The 10-30 pin's
`roc check` on a scratch module with `empty_pair : (List(a), List(a))` and
`nobody : [SignedOut, In(id)]` says "value is not polymorphic... make it a
function that takes {}". So the rule carries that exception, and boundaries'
coming `constant` check should skip a `{}`-function whose type has a variable.

**Not verified by the compiler:** `List.from_iter(U64.until(0, n))`, read
from the builtins' signatures and docs only.

## Policy questions (from BRIEF.md), with a recommendation each

1. **noun_effect on device-prefixed effects** (`port_out_32!`, `uefi_read_key!`)? Recommend: allow a short per-repo list of namespace prefixes and judge the word after it. The prefix is a namespace and the act follows it.
2. **preposition_split on language keywords** (BASIC's `do_for`/`do_on`)? Recommend: exempt by a per-file word list. FOR and ON are the interpreted language's names, not relations.
3. **container on a parser's `value`** (`{ value, rest }`)? Recommend: keep the check; the `##` doc that says whose is the exemption. It costs one line and the doc helps.
4. **state_effect on finder names** (`unused_slug!`)? Recommend: keep, and rename to the act (`pick_unused_slug!`). The guide already says an effect is named for its act.
5. **boundaries `single` on near-identical getters, one by one?** Recommend: keep the findings and add to the guide's "a function earns its boundary" that a run of them wants one shared helper. The finding points at the right place; the fix is the merge.
6. **boundaries `fixed` on general helpers whose callers pass one constant?** Recommend: skip exposed members of a library module (lib/, a package). A math helper's parameter is its API; the fix is at the caller.
7. **pinned.shale reads only `roc-version`; roc-apps uses `roc-nightly.txt`?** Recommend: move roc-apps to `roc-version` at its next pin move. CLAUDE.md §2 already names that file as the one home.
8. **nest_depth on fan-outs** (`pack(shade(r(c)), shade(g(c)), shade(b(c)))`)? Recommend: keep, and say in the guide that a fan-out takes named parts, not a chain. Named channels read better than either form.
9. **stack on math tuples and test tables?** Recommend: exempt a list or tuple whose items are all literals and fit the line. A table's row is one thing to scan.
10. **name_hunt `question` on test-table values; `noun_effect` repeated on copied helpers?** Recommend: judge `question` on functions only (a bug, really); fix the copies, not the hunt (54 copies of `line!` want one shared helper).

Also raised in stage 3, for the same list: drawing effects named for their
shape (`line!`, `circle!`; recommend allow, it is the platform's API),
markdown's `*_at`/`*_onto` suffix convention (recommend exempt a suffix used
package-wide), and `is_playing!` as an effectful question (recommend allow a
question effect that asks the host about live state).
