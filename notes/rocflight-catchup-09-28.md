# rocflight catch-up: 09-26 evening to 09-28

*Organized by your three objectives. PR #25 is the only thing that went upstream; Brian is still silent.*

## Where things stand

| Piece | State |
|---|---|
| #25 commit 8: a list's `keep_if` is a list, and `.iter()` gives an iterator | **Pushed.** Fixes GraphTraversal, so `check_examples` is now **19/0** (was 18/1). |
| #25 commit 9: a `for` loop walks the iterator a nominal's `iter` gives | **Pushed.** A regression that commit 8 caused, caught by a cold review. |
| "An iterator is its own type" (checker) | **Done, not pushed.** It waits for static dispatch, because alone it turns two roc-valid programs into type errors. |
| Static dispatch, step 1 of 3 | **Done, not pushed.** Two commits; a second cold review is running now. |
| Everything else | Queued; see the end. |

The unpushed work is on branch `iter-type-wip` on the fork. Its design is at `notes/rocflight-static-dispatch-design.md`.

## 1. Emitted Rust against native roc

**The comparison with roc is unchanged.** Yesterday's result, that roc2rust's Rust is faster than roc and uses about the same memory, still holds. After every checker change, I compared the Rust that roc2rust writes for the five Fast Track experiments with the Rust it wrote before. It has stayed **byte-identical**: 305 to 338 KB of Rust each. Identical source compiles to identical programs, so the measured performance carries over without re-running the 10-game comparison.

That's an argument from identity, and it stops working the first time a checker change alters the Rust. When that happens, the 10-game roc-against-Rust comparison gets re-run.

**Corpus:** roc2rust is 581/581 on the ported corpus at every step. Its own tests pass, and the round trip is steady at 551 pass, 29 refused (the known roc2codex refusals) and 1 where roc itself fails.

## 2. Bug-hunting in Roc

**Nothing new confirmed in roc itself these two days.** roc was the oracle for well over a hundred probes, and its answers were always the ones I then took as correct.

**Two things about roc worth a look, not yet investigated:**
- **`roc check file.roc` reports a warning from a different file:** a stray `/tmp/claude-1000/main.roc` two directories up. It looks like roc searching upward for a `main.roc` it wasn't asked about. That could be deliberate package-root behavior, or a bug.
- **Some diagnostics printed two or three times** in the research agent's probes of static dispatch.

**Both are leads, not findings.** Confirming either means a minimal repro against the pinned nightly, and I haven't done that. Say the word and I will.

**rocflight's bugs, found against roc:**
- **Iterators:** rocflight treated an iterator as a list, both in the checker and at run time.
- **Empty `List.min`/`List.max`** reported `IterWasEmpty` instead of `ListWasEmpty`.
- **`Iter.product`** returned a bare number instead of the `Try` Builtin.roc declares.
- **Methods on an unknown type:** rocflight guessed their result from the method's name. roc checks them where the type becomes known.
- **The most important one:** the checker and every parser numbered type variables from the same starting point. So an unrelated variable with the same number was silently the *same* variable. The rows work hit this trap too and worked around it. It's now fixed at the root, with checker variables numbered in their own range, and it may have been causing rare type errors nobody traced.
- **A `Dict(Str, I64)` annotation is effectively unchecked:** `x : Str = d` is accepted. Queued; it's a bigger hole than it looks.

## 3. No regressions, in the interpreter or in roc2rust

**Every change passes four gates** before it goes anywhere:
- `cargo test`, in debug and in release.
- **Brian's suites, about 6 min:** `check_roc` 97/2, where the 2 fail in roc itself; `check_examples` 19/0; the artifact check.
- **The all-prs gates, about 7 min:** the 581-program ported corpus, and Fast Track on the interpreter, compared with roc's output line by line.
- **The codex-emit gates, about 8 min:** roc2rust 581/581 and the round trip.

**Speed and memory are now gated too,** because you asked on 09-26. Every all-prs run appends Fast Track's time and peak memory per experiment to `~/build/rocflight/ft_timings.tsv`, so a slowdown shows up as a trend. So far:
- **Times** have held: rf_table about 21 s, rf_roll about 10 s.
- **Memory** is up one allocator step, about 120 KB. It's a fixed startup cost, the same on a 1.5 s run and a 21 s run.
- **One open question:** in today's run rf_dup took **8.1 s against its usual 5.8–6.1 s**. A cold review was running probes on the machine at the same time. I'll re-time it alone, before and after, before anything is pushed. It isn't settled until I do.

**Cold reviews keep paying off.** A fresh agent reviews each commit against roc, and every review found real defects:
- The `for` loop regression, which reached #25 and was fixed there.
- Literals accepted as iterators.
- The variable-number collision described above.
- My own claim that `double_all("hello")` is refused, which was false.

In each case the commit messages and PR text were corrected to match.

## On "right layer, not too invasive"

Most of these fixes are small and local:
- The `for` loop fix reorders one branch.
- The `min`/`max` and `product` fixes are a few lines each.
- The variable numbering is one constant.

**Static dispatch is the exception: it changes the checker's core.** It touches unification, generalization and instantiation, and adds about 250 lines. It is the right layer: the name-based guess *was* the approximation, and roc's own algorithm is what replaces it. But it's the most invasive change I've proposed to Brian.

**Two ways to send it.** Stacking it on #25 makes #25 bigger still; that PR is already nine commits. The alternative is a separate PR built on #25. That lets Brian judge static dispatch on its own, and it's what I'd recommend, but it's your call.

## What's next

1. **Finish the current round:** the second cold review, codex-emit's gates, and re-timing rf_dup. Then push the Iter and static-dispatch commits, in whichever shape you choose above.
2. **Static dispatch step 2:** a `where` clause constrains its own variable. Today it's one program-wide list of method names with no signatures.
3. **Static dispatch step 3:** strictness to match roc. A type lacking the method is refused, and an unresolved constraint is an error. This goes last, gated by the corpus, because it's where rocflight could start refusing programs it runs today.
4. **A range's `.iter().map(f)`** builds a list where roc keeps an opaque iterator. The fix touches the range fast path the benchmarks rely on, so it needs before-and-after timings.
5. **The unchecked `Dict` annotations.**
