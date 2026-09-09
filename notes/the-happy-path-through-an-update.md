# The happy path through an Update

Drafted 2026-09-08, the day Update 56 landed. Revised 2026-09-09 after the
first Update walk that leaned on it, and after adding the Firefox/WGSL arm.

Suppose the Update is a good one. Suppose the two patches it needs are already
written and the rest of it is a genuine step forward. What is the *right order*
to walk our tools, and what does each one buy?

This is deliberately not the adversarial plan. The adversarial plan asks where
the defect is hiding. This one asks a narrower question: given that everything
is fine, what sequence of measurements would let us **say so honestly** — and
what would we still not have proven at the end?

## The pipeline is a ladder of trust

The repos are not a menu. Each stage's *output* is the next stage's
*instrument*:

    the checkout + its seed
      -> cobblestone-qemu        the transport, and native tools built through it
        -> codex-zig-transpiler  the fixed point, and codexir + codexcheck
          -> rust-codex-compiler graded against those oracles
            -> the subjects      curated 28, then safari

A defect at stage N does not merely fail stage N. It silently poisons every
measurement after it, because later stages *borrow stage N's binaries*. That is
the whole reason the order is forced rather than a matter of taste, and the
reason provenance is not bookkeeping: a borrowed executable carries its own pin,
and if it does not say so, a later green run is measuring something nobody
named.

So the rule underneath everything below is: **never let a stage consume an
artifact whose pin it cannot state.**

And a pin is the most dangerous copy of all, because a second copy of a pin
drifts in silence. This bit twice on the first walk. A safari-only Cobblestone
pin sat two Updates behind the transpilers it was grading against; a curated
set's units were cut one Update behind the oracle they were checked against.
Both were green, both were wrong, and neither said so until someone read the
pin. The fix each time was the same as for any stale copy: derive the pin from
the borrowed artifact's own provenance rather than name it a second time, so the
two cannot disagree. A stage that borrows an executable should read that
executable's recorded pin, not a number we keep beside it.

## Four coordinates

Any measurement sits at a point in a four-dimensional space, and naming all
four is how you avoid comparing two things that were never comparable.

| axis | values |
|---|---|
| toolchain | Rust · Zig · Wasm · QEMU |
| subject | fib · curated 28 · safari · the compiler itself |
| version | the release · a candidate branch |
| layer | frontend → IR → plug → binary |

The happy path **fixes the version first**, then walks the toolchain from
cheapest to most expensive, then walks the subject from smallest to largest.
Version first because a moving pin makes every other axis unreadable.

## Stage 0 — identity and statics. Seconds, no guest.

Before anything boots, three questions that cost nothing:

**Is this the checkout it claims to be?** The seed named in a release note is
the sha256 prefix of `seed/Codex.cdx`. One `sha256sum` confirms the checkout
and the note agree. It is the cheapest possible check and it is free.

**Do our scripts still fit the tree?** Upstream reorganises. Our bundlers name
chapters and pages, and a name that moved fails *inside a guest*, minutes into
a build, as a missing file or a pile of undefined names. The linters answer
this in under a second: `xref arity` for calls whose argument count moved,
`xref dangling` for names nothing defines, and a page-set check for any chapter
we bundle by parts.

The general form is worth stating: **anything our side keeps as a hand-written
copy of an upstream fact is a landmine on release day.** The fix is not to
update the copy; it is to derive it from the checkout, so the question cannot
be stale. A chapter's own `Page N of M` footers are the page order. Read those.

**What did the Update actually touch?** Read the release note in
`docs/PM/Active/GitHubUpdates/`, not the commit subject — the subject is one
line by convention and the credit and the detail live in the note. Take from it
the list of things to watch, and write down predictions *before* measuring.
A prediction registered in advance is the strongest test available, and it
costs a sentence.

## Stage 1 — the transport. `cobblestone-qemu`, fib, about a minute.

`fib` cites nothing, so it needs no bundler. That is exactly what makes it the
smoke test: it exercises the whole transport — bundle, compile through the seed
under QEMU, transpile through the ring plug under QEMU, `zig build-exe` — with
none of the bundling that could fail for uninteresting reasons.

It answers one question: **does this Update's compiler run at all on real
hardware, and does the thing it produces compute the right answer?** If fib
does not print 55 and 610, nothing further down is worth running, and you have
saved yourself an hour.

Cheapest first, and stop at the first red. The failure modes are shared: a deck
overflow or a ring-size wall hits every subject the same way, and finding that
out on fib costs a minute where finding it out on the compiler costs half an
hour.

## Stage 2 — the compiler through the transport. Same repo, about ten minutes.

Now build `codexir` and `zigemit` as native tools *through bare metal*. Two
things come out of this, and the second is easy to miss.

The obvious one: the compiler itself survives the whole transport. It is a much
larger subject than fib and it exercises the parts fib never reaches.

The valuable one: afterwards, `codexir < prog.codex 2> prog.ir` is **two native
processes and no guest**. Every question downstream gets cheaper by two orders
of magnitude. Stage 2 is what buys the speed that makes stages 5 and 7
affordable at all.

And this is the only stage where `address-of`, boxing, the deck and memory are
*real* rather than modelled. Bare metal boxes every variant value, so
`address-of` there is the identity and cannot fail. Any question about those
primitives has exactly one authoritative answer, and it is here.

The check that matters is not "did it print the right number". It is the diff
of the IR bare metal produced against the IR the native tool produced from the
same bytes. Those two roads share a source and nothing else, so a difference
is attributable with no third explanation. A verifier that only checked the
printed answer once passed a compiler that typed every comparison `error`
where bare metal said `boolean` — the program still printed 55 and 610.

One caution from doing this today, and it is about the temptation this stage
creates rather than about the stage itself.

The comparison reported the two roads disagreeing on line 1: bare metal named
the chapter `Program`, the native tool named it after the file's own title. It
is very easy to call that a *road* difference — two ways of invoking a
compiler, naturally naming things differently — normalise it away, and move on
with a green check. I did exactly that, and it was wrong.

`opening.codex` passes the literal `"Program"` at every `compile-frontend`
call site, and it reaches `desugar-document` through `compile-checked`, where
it becomes the IR's `(chapter ...)`. Bare metal goes through the real driver,
so bare metal was right. Our harness passed the document's own title in that
argument position and emitted a chapter name no driver ever produces. A second
harness in another repo already passed the literal and asserted it, so the two
were disagreeing about the compiler's own convention.

The general rule is worth more than the instance: **a difference you explain
before you have located its cause is a difference you have decided not to
find.** Normalising it does not make it go away, it makes it permanent and
invisible, and every later comparison then carries a hard-coded excuse. The
cost of getting this wrong compounds, because the whole point of a two-road
comparison is that it has no third explanation — and a normalisation is
exactly a third explanation, written by us, in advance.

If a check really must ignore something, the reason has to be a fact about the
two roads that survives being chased to the bottom. Ours did not survive five
minutes of chasing.

And report the line count, so an empty comparison cannot pass as agreement.

## Stage 3 — the fixed point. `codex-zig-transpiler`, about eight minutes.

The emitter compiles its own source, and the binary it produced must emit the
same bytes for that source again.

    blob -> QEMU -> zig -> exe -> (the same source again) -> zig -> diff

This is the largest subject that exists and it exercises every chapter of the
frontend and the whole emitter. It is also the stage that **produces the
oracles** — `codexir` and `codexcheck` as native binaries, and
`codexcheck-subject.codex`, which is the compiler's own source at this pin and
therefore the specification the Rust arm is written against.

Two facts about this stage that are easy to get wrong, and I got both wrong
today.

**It is self-consistency, not correctness.** Both passes share upstream's
frontend, so a frontend defect is invisible to it *by construction*. A holding
fixed point never validates an Update. It says the emitter agrees with itself
on the largest input available, which is a strong and narrow claim.

**Not everything in its output directory is its output.** The oracles are
emitted by a *different* generator, on its own schedule, and can sit at a
different pin than the artifact beside them. If the provenance file does not
say which generator owns which file, a reader will assume one owner and be
wrong. Derive that list from the build's own declarations rather than writing
it down twice.

Expect to run this stage twice, and budget for it. The first run hunts; the
second is due diligence on the fixes — **including the prose** — and on the
provenance story. Batch every source edit before the second run, because each
additional edit costs a whole run rather than a diff.

## Stage 4 — the second plug. `codex-wasm-transpiler`.

The same property through a different emitter, and the reason to spend the time
is specific: **a component shared by two arms is unfalsifiable by those two
arms.** If zig and wasm both move, the cause is upstream of both — in the
frontend they share. If only one moves, it is that plug's. Running one arm
gives you a number; running both gives you an attribution.

This is also where a ratchet earns its keep. Not "did it pass" but "did it get
better or worse than the last release", measured the same way each time.

## Stage 5 — repin the Rust arm, and change NOTHING. The Update's report card.

Here is the stage that actually reviews the Update, and its discipline is the
hardest of the lot.

`rust-codex-compiler` is an independent implementation of the frontend. It did
not read the release note; it cannot rationalise; it has no idea what the
Update was trying to do. When it and `codexir` disagree, that disagreement is
*information*, in a way that no test written by the people who made the change
can be.

The protocol:

1. **Bank the baseline before repinning.** The five graded counters on the
   self-host, the per-definition byte-identity count, the corpus refusal list
   by name and reason, the diagnostic agreement by code, the counter agreement
   per unit, the set of byte-identical units. A delta is unreadable without
   one, and afterwards is too late.
2. **Repin, and change nothing else.** This is under the most pressure, because
   the moment you repin you will see things you know how to fix. Do not fix
   them. Every diff measured in this phase is caused by the Update. Change our
   code too and attribution is gone.
3. **Triage every delta before closing any of it.** They changed the IR on
   purpose and we move with them — that is independent confirmation, and worth
   saying out loud. They changed their own source and we cannot parse the new
   construct — that is our gap. We agreed, we now disagree, and nothing in the
   Update says why — that is the bucket to work first.
4. **Only now close our own gaps**, re-measure, and send what survives.

The trap in this stage has a name: the subject is both the specification and
the input. We *port from* `codexcheck-subject.codex` and we *compile* it, and
on a repin both change at once. Read the new subject before measuring against
it and the independent read is gone — we would be conforming to the new answer
rather than testing it. **Measure first. Port second. Every time.**

Four instruments here, and each is blind to something:

- **the counters** are cheap and sensitive to allocation *order*, which is the
  hardest property to hold — and blind to names, and to anything a later pass
  prunes. A change can leave every counter exact and every emitted byte
  identical while naming four definitions `"    "`, because unreachable
  definitions are pruned before emission. Necessary, never sufficient.
- **the IR bytes** are decisive and noisy: one early divergence renumbers
  everything after it. Diff by *definition*, not by file. "2,845 of 2,846" is a
  sentence; "412 differing lines" is not.
- **the diagnostics** catch what neither can — a program both sides accept but
  only one should. Did we invent an error the oracle does not raise?
- **the refusal list**, where a refusal with a reason is inventory and a crash
  is a defect.

## Stage 6 — close the gaps, re-measure, ratchet.

Now the work. The ratchet is the honest summary: identical up, refusals down,
and `identical` **goes up, never down**. If it went down, that is the first
thing to chase, ahead of anything new.

## Stage 7 — the subjects. `cobblestone-curated-tests`, then `safari-codex`.

Everything above compiles *the compiler*. Stage 7 compiles programs, and it is
where upstream's own expected output becomes the oracle.

The **curated 28** are resolved units — self-contained, citing nothing, no
`CODEX_ROOT`, no quire registry, no cite resolution. A program is one file and
its answer is one file. That is what makes them a stable subject across
releases: nothing about them can drift because upstream reorganised a
directory. Run them on every road you have.

**safari-codex** is the application, four arms on one source, and it is last
for two reasons. It is the largest, and it *borrows executables from other
repos* — which makes it the stage where the provenance discipline either holds
or embarrasses you. A safari result is keyed by what BUILT the binary, not by
the checkout sitting next to it. Its resolver already fingerprints the
transpiler's emitted zig, because this went wrong before.

**The WGSL kernels are the Firefox arm, and naga is their oracle.** They are
generated compute shaders, and Firefox validates WGSL with naga while Chrome
uses the more permissive Tint — so a kernel that renders in Chrome and is
rejected in Firefox is the expected direction, and naga run offline is the only
way to see it without the browser. `cobblestone-qemu/wgsl/check.sh` runs naga
over every committed `.wgsl` in under a second — the per-Update gate — and
`regen.sh` rebuilds a red one from the checkout's own plug under QEMU, which
doubles as proof that a candidate's plug changes did not break the shaders. A
generated kernel goes stale the way any copy does: `GlobeKernels.wgsl` sat
naga-red from Update 55 to 58 because the emitter fix at U56 regenerated
`apps/gpushow` and missed `apps/globe`, and nothing said so until naga was run
over the whole tree. The eye test itself needs a secure context, so it is
served on loopback and reached over an ssh tunnel — and the server must send
`no-store`, or the browser hands you back a kernel you already fixed. The
tunnel command and the pages to open live in `cobblestone-qemu/wgsl/README.md`;
this essay does not repeat them.

## What we still have not proven

Even with every stage green, an honest summary has to say what is *not*
covered:

- The fixed points say the emitters agree with themselves. They say nothing
  about whether the frontend is right, because both passes share it.
- The Rust arm sees above the IR, but only for constructs it implements. A
  refusal is a hole in our port, not a verdict on theirs.
- The curated 28 are 28 programs. The corpus is over a thousand.
- Bare metal is authoritative about memory and identity, and we run one small
  program there routinely because the large ones are expensive.
- naga is Firefox's front end, but the naga we run offline is a pinned version
  and a given Firefox ships its own. A naga-clean kernel is Firefox-clean only
  to the precision of that version match, which we have not established.

Saying that out loud is not hedging. It is the difference between "the Update
is fine" and "here is precisely what we checked, and here is what would have to
be false for us to have missed something".

## The one-line version

Fix the version, walk the toolchain cheapest to dearest, walk the subject
smallest to largest, and never let a stage consume an artifact whose pin it
cannot state.
