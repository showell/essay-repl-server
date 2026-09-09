# The issue-125 PR: a regression test that must be red until the fix

Damian said yes to the PR, and the second half of his comment is the part that
shapes it:

> We land the test in the same change as the fix, because a chapter red at head
> blocks every landing through the gate, so it waits on our side until the
> parsers move together.

So this is not an ordinary PR. Its test is **supposed to fail** on today's
compiler, because today's compiler still rounds these literals wrong. The
`.expected` holds the *correctly* rounded bits, the compiler produces the wrong
ones, and the chapter is red at head by design. Damian will hold it and land it
with the parser fix, when the four parsers move together. That is the whole
contract: we ship the regression target, they ship the fix, the two meet.

## What the PR contains

Two files, both upstream's own:

- `codex/test/ops/real-literal-rounding.codex` — add a handful of boundary
  literals to the existing `Report` section, printed the same way the twelve
  already there are: `real-to-bits <literal>`.
- `codex/test/ops/real-literal-rounding.expected` — the correctly rounded bits
  for each, one line each, in the file's existing format.

Nothing else. The existing twelve lines stay; they are all under sixteen
significant digits and already pass.

## The due diligence, because none of this is on our branch

The test is upstream's, so we build the extension fresh, and there are four
things to get right.

1. **Choose the literals deliberately, not at random.** A regression test is
   read by a person. The set should straddle the boundary the mechanism
   predicts — a couple at fifteen significant digits that must stay green, and a
   spread just above it that must be red — and it should carry **both** rounding
   directions, since the defect goes one ULP low and one ULP high. `11.7` (the
   case Damian already measured on his side) earns a place; a value whose
   sibling in the same list rounds the right way, like `5.85`, makes the point
   that it is data-dependent.

2. **The `.expected` is the correctly rounded value, and it must not come from
   Codex.** The file's own header says the expected values are the reference,
   and our standing rule is derive-then-confirm, never capture: taking the
   `.expected` from the current compiler would write the bug in as the oracle,
   which is exactly the failure this test exists to catch. The bits come from a
   correctly rounded conversion — our Rust front end, cross-checked against
   Python's `float()` — the same source that produced the numbers in the issue.

3. **Verify each chosen literal actually diverges today.** A boundary literal
   that happens to round correctly on the current compiler tests nothing and is
   dead weight in the file. Each one goes through both arms first: the Rust
   front end for the correct bits that become `.expected`, and the zig arm for
   the current bits, and it earns its line only if those two disagree. A
   literal at fifteen digits is included precisely because it must *agree* — it
   is the control that proves the boundary is where we say it is.

4. **Keep it small.** A second code path rots, and a test is code. A handful of
   well-chosen lines says everything a random three hundred would, and stays
   legible when someone reads it in two years.

## How it is sent

A clean branch off Cobblestone master, the two files changed, from the fork,
the same way PR 135 went. The PR body says plainly that the chapter is red at
head on purpose and is the regression target for COMPILER-57, so a reviewer is
not surprised by a failing test — Damian already expects it, but the PR should
say so for anyone else who reads it.

Success is not a green PR. Success is a test that is red at head today and turns
green the moment the parsers round correctly, which is the signal Damian is
waiting for.
