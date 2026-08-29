# Update 53, and the checklist's first day

*2026-08-29, written between the safari sweep and whatever comes next. Eighteen
ladder commits since noon, three in Cobblestone, four in the transpiler. The
recommendation is the last paragraph.*

## Update 53 is what it claimed to be, and four instruments say so

The headline first, because it is unusual to be able to state it this plainly.
Four independent measurements agree that Update 53 changed almost nothing we
can observe:

| instrument | what it compares | result |
|---|---|---|
| the fourteen rungs | zig arm vs bare metal, same seed | **14/14 green, 0 diffs** |
| `bank_diff u51 -> u53` | bare metal vs bare metal, across two seeds | 3 truths moved, **11 held** |
| tier gold | bare metal behaviour on 26 primitive tiers | **26/26 byte-identical** |
| safari's 69 artifacts | emitted zig, U52-based vs U53-based transpiler | **69/69 byte-identical** |

Plus the transpiler's own invariant, which held twice: `codexzig` re-emitting
its own 2.4 MB source byte-for-byte, once on plain U53 and again on U53 plus
the real conversions.

The three truths that did move are `ir_to_x86_on_fib`, `ir_to_x86_on_cce` and
`passes_to_x86_on_mid` — and **not** `lir_to_x86` or `passes_to_x86_on_arith`,
which is worth saying precisely, because "the x86 rungs moved" is the tidier
sentence and it is false. A subset moved. That is consistent with ~330 lines
of changed `Emit/X86_64*` touching some emission paths and not others.

The number that matters most is 14/14, because Update 52 was **6/14 and could
not be transpiled to zig at all**. Update 53 is the release that unblocked the
arm, and the ladder now honestly agrees with a seed for the first time since
Update 51.

## The five-second probe that paid for the day

Ceremony step 2 is a canary: compile one subject with the old seed and the new
one, five seconds each, before committing an hour. It found something before a
single second of real compute was spent — `seed_identity.py` did not recognise
Update 53's release note, and would have banked a real release as
`truth/seed-b066ceb5` instead of `truth/u53`, silently, leaving it out of
everything that references a `uNN`.

The cause is one word. Update 52 wrote:

    **The proofs, all at the release head against seed `61C81B04D0C3CC2E`:**

and Update 53 wrote:

    **The proofs, all at the release head against `B066CEB5FE8FC9E8`:**

The same line to the character except that `seed` is gone, and our matcher was
keyed on `SEED \`<hash>``. Second time this function has needed teaching by a
new release form.

Then the canary did its other job: it **predicted the bank diff**. Diagnostics
byte-identical between the two seeds, image 1,552 bytes larger, diverging from
byte 9. Front end holds, image moves — which is exactly the shape the rebank
produced forty minutes later. A five-second probe called the result of a
forty-three-minute run.

## What the checklist caught, and what it did not

Today was `BOX.md`'s first outing, so the honest accounting matters more than
the flattering one.

**It caught things.** Every presence check earned its keep. The tier gold run
came back 26 fresh and **0 cache hits**, which is the only thing separating "we
measured 26 columns" from "we read last Update's bank and called it green."
`build.py` is three seconds warm, so its 448-second cold run is what says it
rebuilt rather than re-certifying Update 52's artifacts. Safari's sweep took 44
seconds instead of 3, which is what says it re-transpiled every module with the
new binary. In each case the *timing* was the evidence, not the verdict.

The new Before item about what a job writes fired on its first use: it revealed
that safari tracks 56 files under `build/` — I had assumed that directory was
scratch. That is the only reason the 69/69 byte-identity result above is
attributable rather than a wall of unexplained churn.

**It also caught me being wrong about its own machinery.** I proposed retiring
a sandbox whose `KEEP` file existed precisely to explain why not, and the file
argued back.

**And it did not catch the worst thing that happened.** The transpiler's
`build.py` writes `generated/local/codexzig` — gitignored, therefore one slot
shared by every branch, invisible to `git status`, unswitched by any checkout —
and safari-codex resolves that exact path. Running the ceremony's codexzig gate
overwrote the binary safari depends on. I found it by accident, reading
`PROVENANCE` for an unrelated reason, with the job already armed to fire. The
checklist had no item for it. It has one now.

Worse was the recovery. I restored the binary with `cp -p`, preserving the
mtime — and mtime is an input to safari's own cache key, whose entire job is to
notice that the transpiler changed. I chose the flag that made a transpiler
swap invisible to the mechanism built to catch one. It was safe only because
the bytes happened to be identical and I checked by hand afterwards; the
mechanism was defeated, not satisfied. Steve caught that, not the list.

Three other self-inflicted problems, all small, all worth naming: a completion
watch that waited on itself because `pgrep -f "tiers_run.py --bare"` matched
the watcher's own argv (an incident already in this repo's record, which I
reproduced anyway); a push that failed non-fast-forward after a rebase while my
own unconditional `echo` reported success; and a comment on an outbound PR that
apologised at length for the instruction it was replacing, which is a thing
nobody three days from now needs to read.

**So the pattern.** A checklist catches the classes it already has items for.
New classes get caught by whoever happens to be paying attention — and then
become items. `BOX.md` grew from 6/5/7 to 8/5/8 today, and every one of the
three additions came from a failure that happened today. The growth rate is
the signal, not the length.

## The bank rules, re-derived

Two rules in `bank_truth.py` turned out to be working against the file's own
stated purpose — "banking is what makes two Updates comparable."

The green-arms rule refused to bank an Update whose zig arms were red. It cost
us Update 52 entirely: those truths were measured, were byte-identical to u51's,
and were discarded — so today's diff reaches back two seeds instead of one, for
nothing. A truth is a bare-metal measurement and the plug's arms cannot reach
one, so a red arm was never grounds to withhold a good measurement. What the
arms said is now *recorded* instead, in an `ARMS` file beside `SEED`, with three
states rather than two, because absent is not red — `zig_arm` returns before it
diffs anything when the zig will not build, which is exactly what "6 of 14"
meant.

`--keep 3` had already deleted u45 through u48 from the working tree and would
have taken u49 on the next bank. A bank is 1.2 MB of text against a 31 MB
`.git`, and removing one from the working tree does not shrink git anyway. Its
stated reason was legibility — "small enough to scan" — but nobody scans 332 KB
of x86 output; `bank_diff.sh` is what makes a bank legible.

What survives is the rule that catches a real lie: one seed, one harness
content sha, refuse a mixed bank. That one is in code and earns its keep.

## The detour, and what it was actually for

safari-codex is a heavy consumer of `codexzig` and boots no guests, which is
why its whole sweep is 44 seconds instead of a ladder-scale job. It needed
`real-to-int` and `real-from-int`, which live on a branch of ours that was
never upstream.

Rebasing that branch onto Update 53 was nearly free, and the reason is worth
keeping: our tree-shaking branch's emitter **is** Update 53's emitter, byte for
byte, because PR 98 was absorbed verbatim. So the reals sat two commits above a
base that had become the release. `ZigEmitter.codex` replayed without conflict;
only the backlog fought, where upstream had renumbered our drafts.

The rebuild then produced a `codexzig` that is Update 53 plus the reals, with
real provenance — replacing a binary that had been put in place by hand. Safari
greens on it, and every one of its 69 tracked artifacts is byte-identical to
what the Update 52-based transpiler produced. Sixty-five of those were rewritten
during the sweep, which is the difference between "regenerated and inert" and
"never touched", and only the second one would be a false green.

That detour also cleared a second thing I had disturbed without noticing:
safari's `CODEX_ROOT` points at the shared Cobblestone checkout, which I moved
to the u53 pin. It grades clean against Update 53's foreword chapters.

## What is still outstanding

An inventory, because the answer to "what do we have that Update 53 does not"
turned out to be longer than either of us thought:

- **The second compiler PR** — findings 57, 58 and 59. Update 53's release note
  *opens* its open-items list asking for these by name: "RESERVED for him in the
  COMPILER-30 row. Absorb on arrival."
- **The reals**, now rebased onto U53 and proven, owed as a PR.
- **PR 99**, sent today: the prelude parts table shipped an instruction that
  cannot be followed, and it is our error, shipped by our own PR 98.
- **Findings 60 and 61** — the discard rule and a nullary generic call, five
  commits on a branch that predates the shaker and needs extracting rather than
  rebasing. Safari does not need them.
- **`roc-ports-batch2`** — eighteen corpus test cases, unsent.
- **Plugs row 2.02**, routed back to us and unowned: the zig plug has no
  equivalent of the duplicate-arm drop C# got.
- **The type-def prune**, parked with defects that can drop a live type
  silently.
- **Four findings owed from safari** — `OvError` silently wrapping, a Cordic
  accuracy claim wrong by 4.5x, a function named `d` colliding with `Tup4`'s
  comptime parameter, and a one-word bounds under-count in angry-gopher's
  `pushGradPoly`. The `d` collision is the same `Tup4` fact PR 98's row recorded
  from the other direction — two projects hitting one defect independently,
  which is a stronger report than either alone.

## What to do next

**Build the natives and run the tier set and the corpus census, as one detached
chain.** Everything green today is a *regression* result — it says the same
things still work. Nothing today was a *discovery* instrument, and that is the
half of the original question still unanswered: whether Update 53 introduced
scenarios that expose latent problems. The fourteen rungs cannot answer it;
they are fourteen fixed subjects, all of them the compiler compiling itself.
The corpus is 580 programs and the tier set is the live COMPILER-18 detector
that once caught a stale row a `--zig`-only run could not see. Both need
`native/`, and the natives in the main checkout are from **2026-08-26**, built
from a U50-era pin — three days and three Updates stale, so they cannot measure
this release at all. That makes the ordering obvious: `native_build.sh` (~13
min), then `tiers_run.py` as a set (~3 min, and the bare columns are already
banked so only the zig arm costs anything), then the corpus census (~10 min+,
and every emitted program will move because the emitter did). One chain, one
compute lock, roughly half an hour, and it converts today's "nothing broke"
into "we looked where new things would show up." The outbound queue — the
second compiler PR especially, since they are waiting on it by name — is
keyboard work and belongs in the gaps while that chain runs.
