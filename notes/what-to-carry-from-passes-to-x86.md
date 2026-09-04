# `passes_to_x86`, and the five-second probe that called it

*2026-09-04. Third in a series about retiring the ladder: what is worth taking.*

`ir_to_x86_on_cce` turned out to be a capacity test that had caught one thing,
on purpose, and we dropped it. `passes_to_x86` is a different animal, and the
difference is worth being precise about, because one of its two rungs is the
most load-bearing thing in the ladder and the other has already done its job.

## What it adds over `ir_to_x86`

The same back end, with the IR pipeline switched on. `emit_harness.py` carries a
`passes` flag: `ir_to_x86`'s two rungs run with it off, `passes_to_x86`'s two run
with it on, and what it inserts is the middle end — `Simplify`, `Occurrence`,
`LambdaLifting`, `Passes`, `IRCheck` — exactly where `compile-frontend-passes`
calls `run-ir-pipeline`.

That is also what decides the unit's contents, in a way worth writing down: IR
emission prunes to what the opening reaches, so **that one call is the only
reason the pass chapters end up in the IR at all.** Remove it and they vanish
from the subject, silently.

## The line that makes `passes_to_x86_on_mid` load-bearing

From its own docstring, and it is the best sentence in the ladder:

> The subject is chosen to make the middle end DO something. Transpiling the
> pass chapters and running them are two different claims, and **fib only tested
> the first**: with fib the pipeline is a no-op — `double` is dead, `fib` is
> recursive so nothing inlines, nothing folds — so `whole.truth` came out
> byte-identical to `ir_to_x86_on_fib.truth` and **the passes could have been
> broken without the oracle noticing.**

That is the exact failure mode this whole retirement exercise is about: a green
check that is green because it never ran. A rung compiled the entire middle end,
emitted a binary, compared it byte for byte against bare metal — and would have
passed with the middle end removed, because the subject gave it nothing to do.

The fix was the subject, not the harness. `Chapter: Mid` is built so each of
`default-ir-pipeline`'s three passes has something to bite on:

| pass | what bites |
|---|---|
| `fold-constants` | a `7 * 6` in the driver |
| `inline-leaf-calls` | `double` is a leaf and is actually called |
| `inline-single-caller` | `scale-by-four` has exactly one call site |

`fib` stays for the recursion, which nothing inlines, so a real call survives in
the emitted code. Everything is integer arithmetic with one printed answer: the
work under test is the compiler, not the program it compiles.

**That is a designed experiment**, and nothing else in the toolchain asks its
question. The transpilers demand a fixed point on the *zig* path. The corpus
checks answers, not the emitted image. Nothing but this compiles the whole
compiler with its middle end live and compares the machine code against bare
metal's, byte for byte.

Its own docstring names the comparison it beats: *"The C# arm pushes the whole
compiler through its plug and stops at 'the emitted C# compiles'; this pushes the
whole compiler through the zig plug and compares the binary it emits, byte for
byte, against bare metal's."*

## `passes_to_x86_on_arith` was built to answer one question, and it answered

The second rung is a different kind of thing: not a standing check but an
instrument built to attribute a specific failure. The hosted compiler compiled
`codex/test/plug-oracle-arith.codex` into a binary that agreed for seventeen
values and then faulted with `!EXC=06` — an invalid opcode — where the
seed-compiled binary printed `100 / -100 / 42`. Those three come from a record
field typed `Integer between -100 and 100 clamping`.

Two hypotheses, and the rung was designed to separate them:

> (a) the zig plug mis-transpiled the clamping path of the x86 emitter, so the
> transpiled compiler emits different x86 than bare metal does;
> (b) the transpilation is faithful and the harness is at fault … or current
> source differs from the frozen seed here.
>
> **If the arms agree, the transpilation is faithful and (b) holds; if they
> differ, (a) does, and the diff names the instruction.**

Today the arms agree. `passes_to_x86_on_arith` is green on `u56-candidate`, and
has been since Update 53. **The experiment ran and returned (b).**

That is a rung that succeeded, and succeeding is not the same as being needed
forever. What it is now is a regression guard on a question already settled —
useful, but a much weaker claim than the one that justified building it, and one
of the two subjects riding in a unit whose compile is 2.58 MB.

## The five-second probe that called the whole sweep

The sharpest thing in this corner of the record has nothing to do with either
rung. `plug-oracle-arith.codex` has a second job: it is the **seed canary**.

At Update 53 it was compiled by both seeds on bare metal — one subject,
unchanged between the releases, so the seed is the only variable — in **five
seconds a side**. From `U53.log`:

> `bank_diff u51 -> u53`: three moved, eleven held. `ir_to_x86_on_fib`,
> `ir_to_x86_on_cce`, `passes_to_x86_on_mid` — but NOT `lir_to_x86` or
> `passes_to_x86_on_arith`, so a subset of the x86 family and not the whole of
> it. **The canary called this shape from a five-second probe.**

A ten-second experiment predicted which of fourteen rungs would move, in a sweep
that costs hours. It also caught something the sweep could not: `seed_identity.py`
did not recognise the new release's note, "the second release form it has needed
teaching, and the canary is where it should be caught."

I do not think that has been given its due. The canary is not a smaller version
of the ladder; it is a different and better instrument for the question "did
anything move", and the rungs' job is the narrower one of saying *what* moved
once you already know something did.

## What I would carry

**Carry the middle-end claim.** One subject, designed so the pipeline has
something to bite on, compiled whole and compared against bare metal. It is the
only check anywhere that the middle end *runs* rather than merely transpiles,
and the docstring's own history proves the naive version of it was vacuous.

**Do not carry the arith rung.** It answered its question in Update 53 and
returned (b). If the clamping fault comes back, the instrument is thirty lines
and a subject that already exists; rebuilding it then is cheaper than running it
until then.

**Carry the canary instead, and give it a name.** Compile one unchanged subject
under two seeds and diff. Five seconds. It called the shape of a multi-hour
sweep and found a tooling gap the sweep could not. In `codex-qemu` that is a
`verify_`-shaped script, not a rung: *did anything move between these two
trees?* — asked before anyone spends six minutes, let alone an afternoon.

**And notice what the three essays have converged on.** Each of the ladder's
expensive things reduced to a cheap question it was answering indirectly:
`ir_to_x86_on_cce` to "who compiles something large to x86"; `f3_run` and
`f4_boot` to "do emitted x86 bytes work"; `passes_to_x86_on_arith` to a
hypothesis that has been settled for three Updates. Only `passes_to_x86_on_mid`
survives contact, and it survives because somebody noticed its first version was
vacuous and fixed the *subject*.

That is the pattern worth carrying, more than any of the code: **the checks that
earned their keep are the ones where somebody asked what the check would look
like if it were passing for the wrong reason.**
