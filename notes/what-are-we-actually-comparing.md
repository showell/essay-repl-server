# What are we actually comparing?

Drafted 2026-09-08, the night Update 56 landed.

Nearly everything we do is one shape. Take a function, evaluate it twice, and
require the two answers to be equal:

    f(w, x, y, z)  ==  f(a, b, c, d)

A fixed point is that. A two-road comparison is that. Grading the Rust front
end against `codexir` is that. Booting the emitted x86 and checking it prints
6765 is that, with a human-legible constant on one side.

The whole discipline is in choosing which of the four coordinates differ and
which are pinned — and in *knowing*, at the moment you read the answer, which
was which. Everything is easy while you know. The trouble is never the algebra.
The trouble is that a coordinate moves without telling you, and then the
equation you thought you were solving is not the equation you solved.

## The four coordinates

**Toolchain** — Rust, Zig, Wasm, QEMU. Which machine ran it.

**Version** — which pin of the Cobblestone source. A release, a candidate
branch, a worktree somebody made in August.

**Subject** — what got compiled. `fib`, the curated 28, safari, or the compiler
itself.

**Stage** — how far down we went. Frontend, IR, plug, binary.

A useful comparison holds three and varies one. The zig fixed point varies
*toolchain* only: same version, same subject, same stage, one pass under QEMU
and one as a native binary. The wasm two-road check does the same thing through
a different plug. Grading Rust against `codexir` varies *toolchain*, holding
version, subject and stage — which is why a disagreement is attributable, and
why it is the only arm that can see a defect above the IR.

Vary two on purpose and you can still reason, if you say so out loud. Vary one
by accident and the result is worse than noise, because it looks exactly like a
result.

## What actually goes wrong

I expected, before tonight, that the hard part would be experimental design —
picking the right comparison. It is not. Every comparison in these repos was
already well designed by somebody who thought about it carefully. Four things
went wrong today, and all four were the same thing:

**A coordinate moved inside an artifact, and nothing made it say so.**

- The wasm `self` road ran a tracked `codexwasm.wasm` built at `422405d0`
  against a checkout at `e941ba11`. Two versions in one comparison. The build
  reported "a defect in one of the two, and the source is the same source". The
  *subject* was the same source. The emitters were two different versions, one
  line apart — and one line was 34,742 bytes of divergence and one function in
  the table.
- The Rust arm's oracles sat two days behind the checkout everything else was
  using. Nothing said so; they are gitignored, so mtime was the only evidence,
  and mtime says *when*, never *what*.
- `native.sh` borrows `generated/local/codexir` by path. Run it on the wrong
  evening and it compares our port against an oracle from another version while
  every name in sight says otherwise.
- A hand-kept list of a chapter's pages was right for one checkout and wrong
  for the next, and killed a build inside a guest.

None of those is a design error. Each is a **reference that moved after the
comparison was designed.**

## The coordinate that is not on the list

There is a fifth axis, and it is the one that has cost us the most.

Bare metal named a chapter `Program`; our `codexir` named it after the file's
own title. Same toolchain family, same version, same subject, same stage. The
difference was **who called the compiler and with what arguments** — the real
driver passes the literal `"Program"` at every call site, and our harness
passed the document's title in that argument position.

Call it the *harness* coordinate, or the *invocation*. Our repositories are
full of harnesses standing in for `opening.codex`, because the driver does
things a test cannot easily do. Every one of them inherits the driver's phases
and re-implements its setup, and the setup is where they drift. This is
recorded in our own notes with six instances in a single day, and it happened
again tonight.

It deserves to be named alongside the other four, because a coordinate you have
no name for is a coordinate nobody checks.

## Version is not one number

The deeper reason this feels harder than it should: **the four coordinates
describe an artifact, and a comparison involves many artifacts.**

A single `--road both` run reaches for the checkout, the tracked wasm module,
a borrowed `codexzig` binary, the wabt pin, node, and the bundler's chapter
list. Six inputs, each with its own version coordinate. The comparison is only
as pinned as its *least* pinned input, and nothing about the shape of
`f(w,x,y,z) == f(a,b,c,d)` hints that `w` is really six numbers wearing a
trench coat.

That is why the receipts matter more than they look like they should. A
provenance file is not bookkeeping. It is the only place the full coordinate of
an artifact is written down, and an artifact without one can only be located by
its mtime — which is to say, not at all.

## Deliberate differences must be declared in advance

Some differences are expected. The Rust front end refuses programs it cannot
yet parse; that is a hole in our port, not a verdict on theirs. Upstream
changes the IR on purpose and we should move with them.

The failure mode is not having expected differences. It is **discovering a
difference and then deciding it was expected.** That is indistinguishable, from
the inside, from finding a real defect and explaining it away — and I did
exactly that tonight, twice, before being caught both times.

The only defence I know is to write the expectation down *before* the
measurement. A prediction registered in advance costs a sentence and cannot be
retrofitted. "On repin, expect 2,846 of 2,846" is worth something precisely
because it was written when it could still have been wrong.

A normalisation added *after* seeing a diff is the same mistake in a more
durable form: it does not remove the discrepancy, it makes it permanent and
invisible, and every later comparison inherits an excuse written by us.

## The metaphor: this is surveying, not experiment design

I kept reaching for the controlled experiment — hold everything, vary one
thing, that is the scientific method. It is not wrong, and it is not much help,
because experimental design assumes your instruments and your references are
*stable*. Ours are neither. They are generated, they are borrowed across
repositories, and they move.

The better fit is **surveying**.

A surveyor never measures absolute position. They measure differences from
marks whose positions are already known — and the entire craft is about the
marks. A benchmark is a brass disc cemented into bedrock, stamped with its
identity, published in a register. A datum is the reference frame the marks are
expressed in. You triangulate from at least two known points. And when you have
walked a long traverse, you *close* it: return to a known mark and check that
your accumulated measurement still agrees with it.

Every piece of our practice has a name in that vocabulary:

- the pin, a Cobblestone sha, is the **datum**
- the banked baseline — 864 identical, five exact counters — is a **benchmark**
- `generated/PROVENANCE` is the **stamp on the disc**
- the cold `--force` rebuild is **closing the traverse**: walk the whole chain
  again and check you arrive back at the same artifact
- bare metal, where `address-of` is the identity and cannot fail, is **bedrock**
- two independent front ends agreeing on twelve units is **triangulation**

And the failure mode has a name too. A benchmark can subside. Geodesy takes
this seriously enough to put the *epoch* in the name of the frame — NAD83(2011)
is not NAD83(1986), because the continent moved and pretending otherwise would
silently corrupt every measurement expressed in it. A datum with a date on it
is exactly a pin with a sha on it, and for exactly the same reason.

That is the thing our repos keep rediscovering. An artifact without its epoch
is a survey mark with no stamp: it looks authoritative, it is in the right
place, and there is no way to tell whether it is the mark you think it is.

The metaphor also predicts where to look next. Surveyors do not trust a mark
because it is there; they check it against two others before using it. We have
four toolchains and rarely cross-check more than two. Surveyors re-observe
marks on a schedule, because subsidence is silent. Our memory bank in the wasm
arm has not been re-taken since before a memory improvement, so it sits 32%
above the current peak — a mark that has drifted, still being used as a
reference, and reporting `-24.07%` as though that were good news.

## What follows from taking it seriously

**Every generated artifact carries its epoch, or it is not evidence.** Not in a
sibling file that can be lost — in something that travels with it, or in a
receipt that is checked rather than merely written.

**A comparison states its coordinates before it states its answer.** Ours now
print them: `state e941ba11`, `module generation 1 was built at e941ba11,
matching the checkout`. Two lines of preflight replaced a warning we had
reasoned past on every run.

**Check the property, not the proxy.** We asked for a *detached* checkout as a
way of getting an *unmoving* one. Detached was cheap to check and did not
answer the question; comparing the sha and the dirty flag across the build does,
and catches a mid-build edit that no pin scheme prevents.

**Close the traverse on purpose, and know that is what you are doing.** A build
that says HOLDS in four seconds from cache and a build that says HOLDS in 481
seconds having re-run three guests are different claims wearing the same word.

## The one-line version

Every test is a difference measured from a mark. Stamp the marks, put the date
on the datum, and close the traverse — and when two answers disagree, ask which
mark moved before you ask which side is wrong.
