# Trimming Cobblestone

*2026-09-12, morning. A reflection, written before any code, on what the
project could stop carrying, and on the Roc pivot. Opinions, meant to be
argued with, and nothing here has been said to Damian.*

## What the tree actually holds

Numbers from the u58 checkout, because the argument needs them.

| part | size |
|---|---|
| compiler | 60,000 lines of Codex, self-hosted, bare-metal seed |
| foreword (the standard library) | 438 chapters, 83,000 lines: ai, compress, gpu, sim, game, ui, signal, shell |
| os | 162 chapters, 33,000 lines: kernel, net, sched, trust, verify, replay |
| plugs (backends) | 59: every mainstream language, three ISAs, PTX, SPIR-V, WGSL, a browser, GUI toolkits |
| apps | 69, 239,000 lines: a browser, a mail client, an ERP, a spreadsheet, a piano, a starmap, a globe |

Roughly half a million lines, one author, one collaborator, and a
type-system agenda on top: effects with capability scopes, linear values,
units of measure, hard-real-time budgets, propositional proofs, type
classes, vectors. Every one of those is a research project on its own in
any other language.

The thing to notice is not that this is too much for one person. It is
that it is too much for the *message*. Someone arriving at the repository
cannot say in a sentence what it is, and a project you cannot say in a
sentence is one nobody joins. Recruiting is hard for everyone; it is
hardest when the invitation is "help me with everything".

## The sentence

Here is my candidate for the sentence: **a literate, self-hosting language
whose compiler boots on bare metal, with one proven backend.** Everything
that serves that sentence stays. Everything that does not is a spinoff,
which is a kinder word than a cut and a more accurate one: none of it has
to be deleted, it has to stop being on the critical path and stop being
in the README.

What serves the sentence:

- The compiler and the seed. This is the accomplishment, and it is real.
- The zig plug, because it is the one backend three independent things
  grade (our Rust arm, the Roc ports, the safari specs), the one whose
  gaps get filed and fixed, and the one bare metal is compared against.
- The foreword's core: text, lists, math, CCE, the effect and capability
  vocabulary. The parts the compiler itself cites.
- A small, chosen set of apps as the proof that the language can carry a
  program a person wants: safari (independently written, eye-tested), the
  globe's WGSL kernels, one or two more.
- The test corpus and the Updates. The Update cadence is the project's
  best habit; it is what made every instrument we built possible.

What does not:

- **Fifty-eight plugs.** One backend proven is worth more to a recruit than
  fifty-nine each a little wrong, and each Update touches all of them. The
  C# plug is the best crib and could stay as a second; the rest are a
  generated family that could be regenerated from the zig one the day
  somebody wants Kotlin.
- **Sixty-odd apps.** An ERP and a mail client in a language with a
  half-finished type engine are not demonstrations, they are liabilities:
  every type-system change re-breaks them and the author spends the day on
  the breakage. Keep the ones that are oracles (safari) or that are
  self-contained and striking (globe, fireworks, fishtank); archive the
  rest under `apps/attic/` with a line each saying what they were.
- **The OS.** Kernel, net stack, scheduler, trust, replay. This is a second
  project of the same size wearing the first one's clothes. It is the
  hardest thing to argue for cutting because the seed *is* a kernel, but
  the seed is a kernel that boots a compiler, and the OS is a kernel that
  boots an OS. Spin it out; give it its own sentence.
- **The type-system agenda, sequenced.** Not cut, ordered. Effects and
  linearity are load-bearing (the compiler uses them). Proofs, hard
  real-time budgets, and units are three PhDs that currently have to be
  kept working through every Update because the corpus carries them. Freeze
  them: no new features, corpus units kept green, no Update work spent on
  them until the core is where the author wants it.

What this buys: the Update cadence gets faster because the surface is a
quarter the size; the token budget per Update drops with it; and the
README can say the sentence, followed by "the OS, the fifty-eight other
backends and sixty apps live in these three sibling repositories, each
looking for a maintainer". That last clause is the recruiting pitch that
does not exist today: a bounded thing a person could own.

The honest caveat is that the author does not seem to want a smaller
project; the scope is the point for him. Then the trim is a trim of the
*critical path*, not of the tree: which things must be green for an Update
to ship. That can be done without deleting a file, by moving the apps and
plugs out of the release gate and into a nightly that is allowed to be
red.

## The Roc pivot

Roc is mature enough to grade against (46 ports, all passing on every arm,
found seven real plug defects), and its test suite is the thing we already
know how to use. Two ideas on the table.

**A Rust interpreter as an oracle for Roc.** The irony is noted: they wrote
the compiler in Rust and abandoned it for zig. But the irony cuts the
other way too. Their old Rust compiler is not an oracle for the new
language; the language moved. A *fresh* Rust interpreter, written from
their eval test suite, would be exactly what our Rust arm was for
Cobblestone: an independent second implementation, cheap to run, that
turns every test into a differential check. The week just past is the
evidence that this works and the memory note is the method. Two cautions.
First, an interpreter is only an oracle for values; it will not see a
type error their compiler should raise, so it needs the diagnostics half
of the Roc suite too, which is where their compiler's own error tests come
in. Second, the return on it depends on whether the Roc team wants
findings. They were generous with their tests; before building the
instrument, it is worth one message asking whether a differential-testing
contributor is welcome and where they would want the reports.

**Porting the WGSL apps to Roc, with a plug to automate it.** This is
attractive because the WGSL kernels are self-contained and striking, and
because a "Codex-to-Roc plug" is the same shape as every other plug in the
tree: an emitter from the IR. It would also be the one plug whose output
is graded by a real, independent compiler. The risk is that it pulls us
back into Cobblestone's plug family, which is the thing above I am arguing
to shrink. I would do it only as a port of one app by hand first, to learn
what Roc lacks (a GPU story, mostly), before writing the emitter.

## What I would do first

Nothing for a day, which is what you said. Then, in order: the one
message to the Roc team; a hand port of the globe's kernels to Roc to
learn the shape; and only then decide between the interpreter and the
plug. The Cobblestone conversation with Damian is yours, and the trim
above is offered as a draft of the sentence rather than a plan.

| repo | branch / revision | role |
|---|---|---|
| cobblestone-u58 | u58-candidate 075a4550 | the tree measured above |
| rust-codex-compiler | `zonk-and-default` 77bd70b, chain 15 running | ready to park |
| cobblestone-curated-tests | 94c470a | the 46 Roc ports |
