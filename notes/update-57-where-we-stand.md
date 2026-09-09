# Update 57: where we stand, and what we know is wrong

*2026-09-09. Written while the one-pin ratchet baseline runs.*

## The short version

Update 57 is `49fa9f27`, seed `B63014D717B1A2F9`. All three of our arms are
green against it. It took nothing of ours, and that is correct — our queue was
empty. Its compiler changes move nothing measurable in our Rust arm.

The interesting part of the day was not Update 57. It was what checking Update
57 revealed about our own instruments.

## Update 56 was aborted, and that is not what it sounds like

Damian said Update 56 was broken. The natural reading is "reverted", and it is
wrong. `6cd2ca1b` is still an ancestor of upstream's master. Update 56 was
**superseded**, not withdrawn:

    6cd2ca1b  Update 56              seed D9CF240465C3D0BC   aborted
    3907073c  Withheld block (issue 123)
    49fa9f27  Update 57              seed B63014D717B1A2F9

This distinction is not pedantry. If U56 had been reverted, everything it
carried — including eleven of our PRs — would have come back out, and the first
job would be re-landing them. Because it was superseded, U56's content is still
in the tree and the right question is narrower: *did the abort disturb what U56
took?*

That question has an exact answer rather than a sampled one, precisely because
`6cd2ca1b` is an ancestor. Take the files each of our PR branches touched, and
ask whether U57 moved any of them. Eleven PRs, and the only file that moved
across all of them is `compiler-backlog.md` — the register, which churns every
Update. **Every code file our landed work touched is byte-identical U56 to
U57.**

## What Update 57 actually did

    Core/CdxCodes.codex                +3       CDX2097, a new warning
    Types/TypeCheckerInference.codex   +148     that warning's implementation
    IR/LoweringTypes.codex             +12      COMPILER-66
    Emit/X86_64*.codex                 +84/-48  COMPILER-20, over-application
    opening.codex                      +17      the DISK entry point

Three of these are worth a sentence each.

**COMPILER-66 was the open half of our PR 134** — the one where a definition's
emitted IR type was decided by where an unrelated definition's *name* sorted,
because `all-bindings` holds two differing entries per definition and an
unstable sort picked between them by accident. They fixed it by making the
comparator **total**: a name tie now breaks on the shape of the bound type.
Not by making the sort stable.

That choice matters to us. Our register recorded that they would want our
peak-linear-memory arm *if a stable sort became the repair*. It did not, so
that instrument is not needed, and an owed item closes without work.

And the fix moves **zero bytes**. Across 1,246 corpus units, not one emitted
definition changed. A repair of an ambiguity that changes no output is exactly
what you hope for and rarely get to confirm.

**CDX2097** warns when a `let` binds a partial application of a named function
and nothing reads the binding — the call never completes and its effects never
happen. That is a diagnostic for the exact failure mode that has cost us
mornings: `check-chapter` went from five parameters to nine at U54 and every
harness kept passing five, which under-applies silently and surfaces phases
later as a type error against whatever consumed the function value.

It fires nowhere in 1,246 corpus units. A warning that catches nothing today
still changes what tomorrow looks like.

**COMPILER-20** — our PR 90, originally — got over-application emission in the
x86 back end. `emit-partial-application` now consults a real arity table instead
of assuming `1 + fun-type-arity`.

## The two defects that survive

Two Updates in a row have now declined the same commit of ours: `9cc2052b`, the
boxing half of PR 131. `ZigEmitter.codex` is **byte-identical** between U56 and
U57, so both defects are live at the current release:

- payload-carrying variants are boxed by zig's finite-size rule rather than by a
  rule of ours, so `address-of` is partial
- `cx_real_to_text` declares `var cx_new`, shadowing the prelude's own `cx_new`
  boxing helper — a reserved name at line 122 of the same file

The reason they survive is structural and worth stating plainly: **nothing in
the entire Cobblestone repository invokes the zig toolchain.** No `zig
build-exe`, no `zig cc`, no `zig test`. Their gate checks that the plug *emits*.
It cannot check that what it emits compiles. So an emitter that produces zig
which does not build passes every gate they have, and will keep doing so.

We measured this rather than assumed it: at raw U57, `zigemit` fails on the
`cx_new` shadow. With our three commits cherry-picked onto `49fa9f27` — they
apply clean, since the file never moved — all four subjects build and all four
checkers pass.

## The arms, briefly

**cobblestone-qemu** (real x86 under QEMU): green. fib, zigemit, codexir and
x86emit all build; all four checkers pass, including the one that boots the
emitted binary and reads `6765` off the serial port.

**codex-zig-transpiler** (the compiler as its own subject): the fixed point
holds byte-identical, 494 seconds, three guests.

**codex-wasm-transpiler** (the module compiles its own source): both roads agree
byte for byte; fixed point holds at 8,287,746 bytes.

**rust-codex-compiler** (the independent front end): the corpus wire is
bit-identical across the repin — 865 identical, 164 differs, 3 we-refuse, 204
oracle-refuses, 10 both-refuse — and the counters likewise.

One free measurement fell out. The ring plug's *source* is byte-identical at
both pins, so the compiled kernel isolates the seed's contribution alone:
542,781 → 590,117 bytes, +8.7%, for a program that did not change.

## Now the part that matters: what we found wrong with ourselves

Four defects, all one family. Every one was found by *using* an instrument for
something, never by reading it.

**A gate that reported PASS while comparing nothing.** The self-host step
printed our counters and the oracle's and never diffed them. Its exit code was
`grep`'s. It had been green for as long as it existed because the numbers
happened to match; the day they diverged it still said PASS. I copied it
verbatim into a new script and inherited the defect rather than noticing it.

**A memory bank that gated nothing.** The wasm arm's `MEMORY.bank` was taken
before a memory improvement and never re-taken: 2180.2 MB against a real peak of
1655.6 MB. Every run reported −24% and read as good news. At a 2% ratchet it
could only have fired on a 34% regression.

**A borrowed emitter nobody checked.** The wasm build's *self* road refuses to
run a module built at a different revision than the checkout — correctly, since
that makes the two roads two emitters rather than two machines running one. The
*zig* road reaches the identical hazard through `$CODEXZIG` and was covered by
nothing.

**And the one that cost the most: a corpus wearing the wrong name.** Every
corpus gate defaulted to `~/units-u56`. That directory holds **U55** sources —
of the 19 comparable test files that changed between those Updates, 18 match U55
and none match U56 — and it had been graded against a U57 oracle all night. The
directory *name* was the only claim anything made about its pin.

## The one that nearly went out as a finding

Chasing a single unit whose diagnostics moved, I found the oracle refusing a
program at the lexer where it used to reach the type checker: `CDX8
Unterminated character literal`, on a line whose closing quote is plainly
present. I reduced it to a minimal repro, confirmed the shape, established that
U57 changed no lexer file while U56 changed `Syntax/Lexer.codex`, and wrote it
up as a candidate for a PR.

Then I opened the lexer to write the fix, and the finding evaporated.

Prose in Codex is one-space-indented and is never lexed. Upstream added the CDX8
diagnostic in U56 **and re-indented its own affected files in the same Update**.
Their file has one space. Our corpus copy has three, because our corpus is a
U55-era cut. The entire diff between the two files is those two lines.

`Lexer.codex` already carries an apostrophe rule and the census behind it: a
quote straight after a letter or a digit is an apostrophe and no diagnostic is
raised, measured over 4,025 files with zero false positives. That is why `don't`
and `compiler's` pass. They did this carefully.

The repro was correct. Every measurement in it was correct. The conclusion drawn
from it was wrong, and the only thing that caught it was going to the source to
write a fix instead of stopping at a clean reproduction.

## What is true right now

The corpus has been re-cut at `8570fba1`, 1,269 units, with a `PROVENANCE`
beside it — because a directory name is not a pin. All four gates now print
what they measured: the subject and the checkout it came from, the oracles and
theirs, and the port's own commit with a dirty marker. A corpus with no receipt
reports `REVISION UNKNOWN` rather than passing for pinned.

A run is going now to take the first ratchet baseline where the subject and the
oracle share one pin. **Those numbers will not compare to the old ones**, and
that is the point of taking them: the old ones compared a U55 subject to a U57
oracle and called it one Update.

## What is still owed

**`gen-eq-def` is the whole story on the counter gate.** U56 synthesises
`__eq_<T>` for every comparable sum. Our desugarer does not, so every one of
1,032 units diverges by the same +64 type variables, and the counter gate cannot
be read at all until it lands. On the self-host subject it is the single
definition we emit nothing for.

**`--road guest` is designed and not built** in the wasm arm, and the README
says so in those words.

**And the corpus needs re-cutting every Update now**, which nothing enforces.
The receipt catches a stale corpus after the fact. Nothing yet catches it
before.

---

*The pattern, if there is one: every instrument that failed today failed by
being green. None of them broke. They reported success about a question they
had stopped asking — a gate whose comparison never ran, a bank nothing could
trip, a road whose emitter was never checked, a corpus whose name was its only
claim. A red instrument argues with you. A green one that has quietly stopped
measuring does not, and you carry its number into your notes and your memory and
your next decision.*

*Which is why the useful discipline is not "run the gates". It is: know what
each green thing would have to see in order to go red, and check that it still
can.*
