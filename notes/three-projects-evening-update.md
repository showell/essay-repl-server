# Three projects: an evening update (2026-10-27)

## Shale

Shale is in good shape. Today's work was mostly hardening, done through use.

- **CC's QUEUE 250** brought the opaque-validation pattern to the Zig side:
  - Seals on `http.Target`, the signed-cookie ids, `Uid` and `UserName`, each enforced by a lint (`cookbook/sealed.shale`). The lint now reads all five consumer trees, not just zig-webbox.
  - Each sealed type's payload is reachable only through a method.
  - `redirectWith` is the one other way to set a `location` header.
  - `Target.format` now fails loudly instead of silently answering `/`.
- **I merged CC's follow-ups** into every repo. The merge waits on the consumers gate before I push: the first run timed out on a box busy with Roc builds, and the rerun is going now.
- **CC's next items:**
  - 252: make Shale's slow gate steps prove they catch something cheaper steps don't, and run them after the cheap ones;
  - 251: pin each tutorial cell's output, so the live tutorial can't quietly drift;
  - 253: capture groups in `re_find`. CC hit that limit twice today.
- **What dogfooding taught me.** Shale's guard rails keep firing on me in useful ways:
  - `run` insists on a timeout and on saying what output to keep;
  - it refuses to run a script nobody has read;
  - a long string must say its level.

  Each refusal cost me a retry, but each one was the kind of slip that bites later.

## The Roc chat

The "text is `Str` inside, bytes only at the door" conversion is most of the way through.

- **Run 4 landed:**
  - user ids are an opaque `Uid :: Str`, decoded once at the door, and a non-canonical id fails the request;
  - `ChatPath` is an opaque `Str`;
  - a conversation key holds its two `Uid`s;
  - the old byte-based twin copies of the path and fan-out functions are gone, along with the hunt that watched them.
- **Twins giving way to types is paying off.** Several twin test cases were dropped or reshaped, because the types now rule out what they used to check.
- **The quick gate** runs in under 10 seconds on a quiet box.
- **Run 5 is under way:** the pages and sidebar views, the recent feed, the message author's id, and the last of the temporary byte conversions.
- **After that, the queue:**
  - the `bool_returns` renames;
  - `::` modules with private helpers;
  - moving the low-hanging Zig into Roc;
  - a `roc glue` test drive;
  - the remaining ports;
  - and finally the style-guide rewrite for outside readers.
- **The heads-up you gave** (its own repository, Linux deploys, a late check that it still runs on bare metal) hasn't changed any of this. It does make "as purely Roc as possible" feel like the right priority.

## The Roc alignment hunt

This is the new project, and it found a real bug within its first hour.

**How the compiler gets alignment right.** Four read-only surveys covered:
- static data;
- layout and code generation;
- the runtime and the host boundary;
- the compiler's own memory.

The compiler mostly gets it right the same way: a single source of truth (the layout store, or `@alignOf(T)`), and every consumer asks it. The strongest form carries the alignment *with the bytes*: each static-data export row has an `alignment` field, and every backend applies it.

**Where it goes wrong.** The weakness is just as uniform: the same arithmetic is copied, and each copy must remember to ask.
- The static string blob's image is built four times. Only one copy has a test, and #12641 was the copy that used `word_size` instead of asking.
- The refcount-header formula appears in the builtins, in wasm codegen, and in two glue generators.
- The entrypoint argument layout exists in about five copies, and they already disagree.

**Why the tests miss it.** The test hosts are kind:
- they over-align every block to 16;
- they ignore the alignment passed to free, though production's allocator depends on it;
- LLVM, the only backend that turns a misalignment into a crash, is opt-in in the eval tests.

**The new bug, reproduced.** Under `roc build --opt=interpreter`, an entrypoint with several small arguments receives the wrong values. `U32, U32` called with (7, 300) sees (7, 0). The cause: LLVM's wrapper writes the arguments into 8-byte slots, and the interpreter reads them back at their plain sizes. Dev and LLVM builds are correct. No one has reported it upstream. The repro builds and runs in about a second.

**The more foolproof pattern.** Make the wrong alignment hard to write:
- carry the alignment inside a type, so no allocator or emitter takes a bare number;
- have one function for each layout rule, called by every backend;
- make the test hosts adversarial instead of kind.

**In flight:**
- **The fix PR for the entrypoint bug.** The slot rule moves into one function in `src/layout/` that the writer and the reader both call, with a red test first. Their checks run locally first, and the branch goes to our fork. I'll review it before anything goes upstream.
- **A catch-all for the eval tests.** A hostile test allocator gives each block exactly the alignment requested and never more, and checks that every free passes the same alignment its allocation did. That turns every existing eval test into an alignment test at no build cost. The same agent is finding out why the LLVM column is opt-in, and what a small alignment corpus under LLVM would cost, rather than switching it on wholesale. You said to be mindful of their build; this is how I'm taking that.
- **#12641 is still waiting** on reviewers. Its CI is green.

**Smaller finds for later:**
- a serialized cache marker that the cache validator never visits;
- a cache header size that is checked one way and sliced another (in a tool's dead path);
- wasm temporaries that hard-code alignment 8 for 16-byte values (harmless on wasm, but the same shape).

I'll turn the survey greps into a reusable Shale hunt, so the copies can't drift unnoticed again.
