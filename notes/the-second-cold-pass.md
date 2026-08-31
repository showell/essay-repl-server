# The second cold pass

Four cold agents, no shared context, over the eight commits that came out of the
*first* cold pass — cobblestone-safari `ab4612aa` `2660d3af` `e6f09556`,
safari-codex `3942a03` `233173f` `02a90f6` `51e9c3c`, codexzig-safari `7d8f2d8`.
One agent per neighbourhood: the wasm plug, the zig mask split, the harness
scripts, the documents. Everything below that I re-checked myself is marked
**[verified here]**; the rest is the agent's word plus its cited evidence.

The shape of the result is the part worth saying first. The corrections
themselves are sound — the guard walk is right, the mask split is right, the
four mem_probe sub-fixes are each right. What the pass found is that **three of
the new defects are the same class as the ones being corrected**, committed in
the act of correcting them. An argument from a model got audited; the
replacement argument did not.

---

## Tier 1 — wrong answers, and one thing to catch before it is sent

### 1. FINDINGS 9 prescribes a fix that does nothing. Not yet sent.

`FINDINGS.md:628` says "what closes it is one clause", `stop > entry` in place of
`stop > 0`, and then says at 641–643 that the early return "can go at the same
time … but removing it is not what fixes this."

Backwards. `Lexer.codex:263` is `in if stop == st.offset then st` — and on the
only input the finding is about, `stop == st.offset` **exactly**, so the function
returns four lines before the `terminated` test is ever evaluated.
**[verified here]** Changing the clause while leaving the early return in place
is a no-op on the defective input. Both changes are required; the removal is a
necessary condition, not a tidy-up.

The supporting argument is wrong in the same direction: the four sibling
no-op returns cited at `:171 :208 :226 :244` are real, but they have *nothing
after them*, while `scan-string-body` has the terminated test and the error push.
That is precisely why removal is behaviour-preserving there and load-bearing
here.

`PORTING_NOTES.txt:248–255` repeats the framing. Item 9 is **not sent** —
this is catchable before it goes to Cobblestone, which is the good outcome
available today.

### 2. A `when` inside a guard clobbers `$_s`. Silent wrong answer, wasm arm.

`emit-wat-match:1101` puts the scrutinee in the single per-function local `$_s`;
the guard is emitted *inside the condition*, before the else-chain re-reads
`$_s`. A nested match in a guard reassigns it, so when that guard is false every
later branch dispatches on the inner scrutinee.

    zig plug   100 / 205 / 305
    wasm plug  100 / 720575940396056776 / 305

Assembles clean. Reachable without writing a nested `when`: the inliner turns
any single-caller function whose body is a match, called from a guard, into this
shape. Not introduced by `ab4612aa` — but squarely inside the class the new
comment at `:203-216` declares swept, and the fixed walkers cannot see it.

### 3. `e6f09556`'s central claim is false: `needs-blit` is an occurrence test.

`wat-expr-calls-name`'s `IrName` arm is `nm == n` **[verified here]** — it asks
whether the name *appears*, not whether it is *called*. So the comment at
`:3005-3006`, the commit's "asking about call sites", and above all
`:3027-3029` ("`needs-blit` is therefore True only for programs that cannot
assemble anyway") are all wrong.

    f (n) = let blit-framebuf = n * 2 in blit-framebuf + blit-framebuf

emits the `env` import, wat2wasm **accepts** it, and wasmtime fails at
instantiation — the exact failure the conditional import exists to prevent. A
parameter of that name does the same. The commit that says "an argument from a
model is worth an audit of the model" shipped a replacement argument that was
never checked against what the walker does.

### 4. Text-literal *patterns* never reach the string table either.

The walkers now visit guard and body; they still never visit `b.pattern`.
`IrLitPat` carries `Text`, and the emitter splices the raw spelling into
`(i64.const sin)` → `wat2wasm: unexpected token "sin"`. A supported feature with
tests in the corpus. Ranked below the others only because it fails loudly. The
full fix is three things, not one: the literal in the table, `strtab-lookup` at
the emission site, `$text_eq` in place of `i64.eq`.

---

## Tier 2 — the instruments that produce quotable numbers

### 5. `mem_probe.py:230-239` has the exact defect `02a90f6` fixed one file over.

The freshness stamp is sha256(subject) + sha256(HIGH_WATER); `codexzig` is
resolved on the line *after* the stamp check **[verified here]**. Rebuild the
base transpiler — which is what you do when testing an emitter change — and the
probe prints "probe is current" and re-measures binaries from the old compiler.
The sibling commit's own message states the principle: the binary is a function
of both inputs.

### 6. `build_codexwasm.sh:54` has it too, on the binary the fourth arm ships.

Same one-line shape, same consequence, on the thing `wasm_arm.py --native`,
`plug_probe.py` and the 680 MB measurement all consume. Not stale on disk today.

### 7. The deck closes 47 of the 60, not the 60.

Measured: 293.6 + 398.0 + 47.0 = 738.6 against 752.4. The remaining 13.8 is
~8.1 MB of process baseline (measured on a five-line input) and ~5.7 MB
genuinely unexplained. The accounting is *structurally* sound — the deck really
is disjoint from the phase deltas — so this is an overclaim in the prose
(`mem_probe.py:301-307` and the commit message), not a fudge.

### 8. The table's largest row is 520 MB of address space, printed unlabelled.

`deck-adv` is not in the skip list, so it becomes `marks[0]` with `prev = 0` —
the absolute frontier after the 512 MB reservation. The commit labelled the small
real number and left the big fake one explained only in a source comment. Top
line of a table whose numbers get quoted.

### 9. `wasm_arm.py:229-248`: under `--both`, a refusal crashes the sweep.

The comment rewritten by `02a90f6` promises "one failure does not cost the
evidence from the other sixteen". With `both` true the `continue` is skipped and
`Path(None).read_bytes()` raises. The documented behaviour holds only under
`--native` alone.

### 10. `build_codexzig_try.sh`: a failed candidate build prints GREEN about the base compiler.

No `unlink` before the build (unlike `build.py:291`, which has a comment saying
why), so a failed build leaves a new source beside an old binary. Worse, the
documented invocation `CODEXZIG=$(./harness/build_codexzig_try.sh) ./harness/run.sh`
leaves `CODEXZIG` empty on non-zero exit, and empty is treated as unset — the
sweep silently runs the base transpiler and reports GREEN for a candidate that
was never built. The key fix itself is correct and reproduces; three inputs
remain outside it (`$zig` and its version, the `build-exe` flags, the script's
own text — `run.sh:85` folds itself into its key, this does not).

### 11–12. Two latent ones in `mem_probe.py`.

Five phases per arm carry arm-specific names (`czg-` / `cwm-`), so they can never
align; the largest is at 55% of the 512 KB suppression threshold, and past it the
table prints two spurious differing rows in the one tool whose premise is that a
differing row means the emitter and nothing else. The `prefix` field that would
normalise them is defined and never read. Separately, `instrument()` emits all 28
marks in a single write at the top of `act`, so a death in the front end — the
OOM this exists to chase — prints *zero* rows, not the documented truncated table.

---

## Tier 3 — claims, which is what the last pass was for

**The zig mask split.** The failure mode in the comment and commit message is
wrong: `cx_shr` masks its shift exactly as `cx_shl` does **[verified here,
`ZigEmitter.codex:3959` and `:3962`]**, so an alias marks *both* parts — a
superset, never a drop. The file's own rule says an extra root runs in the safe
direction. So "a prelude that keeps a part nothing needs and drops one that is
live: bytes move first, zig complains second" describes something that cannot
happen; the real cost is a bloated prelude and a byte diff. Also: the shift
constant is off by one (N=115 gives shift **64**, not 65, and bit 0 not bit 1 —
in a commit about a wrong written-down number); "neither end is unguarded" is
half-true, since 128 is a ceiling with no assertion behind it and 129 aliases
silently exactly as 115 did; and the enumeration billed as complete still is not
— `defs` is missing and `types-text` does not belong.

**The wasm comment's citations.** All five line numbers given for
`emit-wat-guard-test` are wrong — they are a ~21-line-stale copy of the *TCO*
walker's sites. The real ones are 1124/1130/1133/1136/1151, and the prose never
mentions the second, independent set of five.

**"Seventeen checks byte-identical" is vacuous as evidence for this change.**
There are zero guarded match arms in the port and zero in the foreword; all seven
in the repo are under `codex/test`. Byte-identity was guaranteed by construction.
The commit is honest about the string half and silent about the locals half,
where the risk was real.

**Numbers and counts.** `cat_draw` "10.9 MB in before dying" cannot be right —
the whole finished module is 9.02 MB, and `$g_kd_xy` sits at 7.74 MB. "The two
previous rebuilds recorded `+dirty`" — one did; the one before it was clean.
README carries four stale counts **[verified here]**: sixty-one notes (57), the
*seven* defects in FINDINGS.md (nine — on a line whose second half `51e9c3c`
rewrote from seven to nine, one clause later), eight (nine), a hundred and
seventy lines (278). README also still says the wasm runner is `node:wasi`, which
is both untrue (wasmtime) and contradicted by the document it points at.
`X86_64Builtins.codex:1663-1679` does not contain `cvttsd2si` (it is at 1703) —
the same class of citation error the pass set out to fix. "About four hundred
names" is 484. "plug_probe runs 7 probes" is 8.

Two of mine, from the same file: `FINDINGS.md:7` says "Three are sent and six are
not" over a table with **four** SENT rows and five not **[verified here]**; and
`outbound/item1-…` and `item4-…` are untracked leftovers of issues already sent,
while the item-6 draft is tracked.

---

## Not verified, and worth knowing that

Two cells of the five-unit peak-RSS table (`pond` wasm 17 MB, `critter` zig
253 MB) appear nowhere else and have no artifact behind them. The "14 of 17
identical" `cmp` is now unfalsifiable — no previous-sweep WATs survive in
`build/`. The bracket accounting and the "seventeen other emitters with the same
right-recursive shape" would both need a rebuild or a parse to confirm.

---

## The pattern

The first cold pass caught a false coverage argument and forced a retraction.
Writing the retraction, the same session shipped a new argument about a walker
that was never checked against the walker (#3), a failure mode that cannot
happen (#5's tier-3 entry), and a stale-cache defect one file away from the
stale-cache defect it was fixing (#5). Corrections are written in the same mode
that produced the thing being corrected — fast, from the model in your head,
after the interesting part is over. They deserve the same cold read as the work,
which is what this pass was.
