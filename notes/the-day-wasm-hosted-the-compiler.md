# The day wasm hosted the compiler

*2026-08-31. Written at the end of it, for whoever picks this up next —
probably me, with none of today's context.*

Yesterday `codex/plugs/wasm` could not compile a Codex program that did
arithmetic on a `Real`. Not badly — at all. Today the Codex compiler compiles
its own 2.9 MB of source **into a WebAssembly module, which then compiles that
same source and gets byte-identical WAT back**, under node and under wasmtime,
in about fifteen seconds.

The fixed point held on the first attempt, which was the surprise of the
morning. Everything else today came from *hosting* being a much harder customer
than *running a screensaver*.

## What the day actually did

| | |
|---|---|
| peak memory, compiler compiling itself | 3,716 MB → **2,180 MB** |
| of wasm32's hard 4 GiB ceiling | 90.7% → **53.2%** |
| the self-check, under node | 223 s → **15 s** |
| corpus programs that assemble | 411 → **568** of 580 |
| corpus programs that match a hand-verified oracle | **338** of the 364 that run |

Nine commits went out as [PR 112](https://github.com/damiant3/Cobblestone/pull/112),
stacked on #111. Two of them are silent wrong answers, one is a
never-worked-at-all, one turns 161 confusing refusals into one clear message,
and three are memory. A design question went out as
[issue 113](https://github.com/damiant3/Cobblestone/issues/113).

## The thing I would tell myself at the start of the day

**Five times today I named a mechanism from reading the code and the
measurement disagreed.**

- Node was 12× slower than wasmtime. I blamed host-call overhead — one `fd_read`
  per byte, 2.9 million of them, which is real and which I fixed. It bought 11%.
  The actual cause was `memory.grow`, called 56,000 times because the allocator
  grew by the minimum, and V8's per-grow cost rises with the memory it already
  holds. **167 seconds of a 223-second compile.** What found it was not more
  reading; it was asking *what scales* — node was 2.2× slower on a 696 KB input
  and 11.7× on a 2.9 MB one, and something that grows with size is not a
  per-byte constant.
- The driver's own prose said the IR text wire derives a record's implicit type
  parameters. That is not in the code and has not been for some time. It derives
  a **field slot**.
- I predicted a one-caller export could not be saved by rooting it, from reading
  `keep-single-caller`. Wrong: inlining *substitutes*, pruning *deletes*, so a
  root does save it. I had read two passes as one mechanism because they have the
  same effect on the common case.
- I wrote that a 4 MiB source truncation was a silent wrong answer. Measured, it
  is loud and *misleading* — `CDX3002 Undefined name: final-answer` about a file
  that plainly defines it.
- I blamed the ctor binders for a scrutinee bug. It was `__record-set` mutating
  in place.

There is no version of this where I stop being wrong about mechanisms. What
changes is how fast the wrongness surfaces, and today the answer was always the
same shape: **build the smallest thing that would distinguish the hypotheses,
and run it.** The microbenchmark that isolated `memory.grow` took four minutes.
The three-variant bisect that found the guard leak took ten. Both were faster
than the reading that preceded them and did not settle anything.

Related: one of those bisect rounds measured a **stale binary** — I had rebuilt
the sweep binary and not the source-in one — and reported a mismatch that was
already fixed. Rebuild and measure want to be one step, not two.

## What the corpus did that thirty programs could not

Everything in codex-wasm-transpiler had been checked against thirty programs:
the compiler's own source, twenty-nine safari units, two samples. All chosen by
what we happened to be working on.

The ladder's corpus is 580, chosen by somebody else, and it holds them as **IR
text** — which is what the plug's own driver consumes, so nothing needs
compiling. A driver that reads IR from stdin, and `wat2wasm` on every result,
found 169 refusals in an afternoon.

**`wat2wasm` is the instrument, and that is the transferable part.** A builtin
the plug has no arm for is not emitted as a bad call — the name is treated as a
value, reaches the funcref path, and comes out as `call_indirect` against a
local nothing declared. No grep finds that. The assembler names it and the line.
Any target with a real checker downstream has this lever: **run the checker over
a corpus you did not choose.**

Then the same modules against the hand-verified `.expected` beside each program,
which is where wrong *answers* live rather than refused modules. 338 match, 162
trap on refusals we emit deliberately, 26 differ — and cross-referencing the zig
arm cut those 26 to **17 that are wasm's alone**. Of those, four are one bug:
`let` is lexically scoped and wasm locals are not.

## The strategic frame, which is Steve's and I think is right

We are not going to make the wasm plug perfect. There are ~50 plugs, one of
them is ours in any real sense, and the corpus still has 12 refusals and 26
diffs. Perfection is not the goal and pretending otherwise would just spend the
next session on the long tail.

**What we actually want is two repositories that keep working.**
`codex-wasm-transpiler` is the proof the toolchain is real — a compiler that
compiles itself, in a browser-sized memory. `safari-codex` is the proof it does
something a person would want — a real program, verified four ways. Between
them they describe what wasm has to do in the world. Everything else is
optional.

That reframes the backlog. A defect matters if it threatens one of those two;
otherwise it is a finding to write down and send.

**And the browser is deliberately not ours.** We never got to it today and that
is fine — Damian's agents already run wasm in a browser in prism, and that is
their competence, not ours. What we owe them is a plug that does not silently
lie, which is most of what today was.

## Where I would start next time

**1. Re-pin safari-codex to the fixed plug, and re-verify its four arms.**
This is the top item and it is not glamorous. The two repositories have
**diverged**: safari's fourth arm still builds against the plug from before
today's nine commits. It benefits most from the memory work — its `cat_draw`
and `safari` units were the ones that used to die at 4 GiB — but re-pinning
means re-running its checks, its byte comparisons and its bare-metal arm.

It is also the closest thing available to a second opinion on today's work: a
different consumer, different programs, an oracle we did not write. If the nine
commits are wrong somewhere, safari is where it shows.

**2. The eight device stubs that answer plausibly instead of refusing.**
`block-sector-count` returns 0 because there is no disk; the four `fat16-*`
programs read an absent image; `manifest-pin` reports a zero-sized manifest.
These are the *same standing hazard* we fixed today, one step further in: not a
builtin with no arm, but a builtin whose arm quietly answers zero. The plug's
own prose names it — *"Emitting something plausible instead is this quire's
first standing hazard"* — and the fix is the same, `(unreachable)` with a
comment. Mechanical, and it converts eight silent wrong answers into eight
honest refusals.

**3. The runtime namespace.** About 45 emitted helpers carry no prefix, so
`list_at`, `char_at`, `substring`, `read_byte` are all names a program may not
use; four corpus programs already collide. One prefix, every helper, every call
site. It moves every byte of every module, which means the fixed point is the
only thing that will catch a slip — so do it deliberately, with the corpus
before-and-after.

**4. Wait on issue 113 before touching the scoping bug.** It is four silent
wrong answers in ordinary code and it is the most alarming thing we found, but
the fix is a design call about whether the IR should carry a suggested rename
alongside the source name. Damian's agents should weigh in. Doing it in the plug
first would be a fifth backend inventing a fourth answer.

## What is fragile, in the order I would worry

- **The two repos are pinned to different plug revisions.** Until item 1 is
  done, "both repos work" is true of a state that no longer exists in one of
  them.
- **Generation 1 still comes from `codexzig`.** No zig runs to *use* the
  artifact, and the `self` road rebuilds it with none in sight — but the first
  generation traces back through the zig plug. The guest road would remove that
  and is designed, not built.
- **codex-wasm-transpiler's roots list carries five names inherited from
  `opening.codex` that name nothing in our subject.** Harmless only because
  `opening` is first: `ir-prune-roots-indexed` returns the chapter *unpruned* if
  the FIRST root names no definition. That is a loaded gun with the safety on.
- **The memory ratchet is armed at 2,180 MB and nothing else watches the
  ceiling.** It fires on growth, which is right, but it is one number in one
  repository.

## One last thing worth keeping

The single most useful instrument built today was not a fix. It was
`runwasm.mjs` noticing that **every `memory.grow` is a free sample** — the views
have to be rebuilt when the buffer is replaced anyway, so recording the time and
size costs nothing, and a module whose allocator only ever grows gives you an
allocation profile for free. That, plus the observation that the driver writes
its diagnostics immediately *before* it emits — so the first `fd_write` is the
front end's last moment — split the whole budget two ways with no code change
at all.

Both of those came from asking what the program was already telling us. That is
cheaper than instrumenting, and it worked twice in one day.
