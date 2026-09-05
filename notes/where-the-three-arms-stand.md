# Where the three arms stand

You asked which milestone is at 100%, whether we are on to safari, and whether
codexir is good for safari or we are stuck on the plug. Short answers first,
then the evidence.

**Done, at 100%:** the interpreter runs Cobblestone's own front end. Not just
for `fib` — for 63 of the first 80 real corpus programs, byte-identical to
bare metal.

**Done, at 100%, and it was not on the plan this morning:** `codexir` at our own
pin, landed in codex-zig-transpiler, 97 seconds to build, no guests.

**Not started:** safari. Not because we are stuck — because codexir only
finished an hour ago and it is the piece safari was waiting on.

**Not stuck on the plug.** The plug defect is real, root-caused, and *narrow*.
It costs us one field of the IR. Everything else agrees.

---

## The number that matters

Take 40 corpus programs. Compile each one two ways — through the Rust
interpreter running the compiler, and through `codexir`, the same compiler
compiled to zig. Both at `safari-u56`, same source, different host. Diff the IR
text.

    identical                                    0
    identical once effect labels are normalised  35
    still differ                                 0
    not compared                                 5

**Thirty-five of thirty-five.** One field differs, and nothing else does — not a
type, not a `(tvar N)`, not a parameter order, not a byte. Two independently
built hosts running a 6,431-definition compiler and landing on the same text.

That is the milestone, and it is bigger than "fib works". `fib` was two
definitions and proved the interpreter could get through the door. This is the
interpreter being *right*, on real programs, against an arm that shares no code
with it.

## What "100%" means for each thing

**Rust interprets the front end to IR.** 100%. `fib` was the proof of life on
Friday; the corpus is the proof of correctness. 63 of the first 80 programs
byte-identical to the bare-metal bank at `53b3b213`, and the seven that were not
have since been attributed — see below. Getting there cost three interpreter
defects, each pinned by a failing test before it was fixed:

- `list-set-at` copied where it must write through. The compiler's skip list
  links its nodes by nothing but that side effect, so every insert bumped a
  counter and linked nothing, and a function's own parameter came back
  `CDX3002 Undefined name`.
- A cached nullary handed out one list. `skip-list-text-empty` calls nothing
  impure, so the purity fixpoint left it cacheable — and every insert in the
  program spliced into the one empty list it handed out.
- `list-push` allocated where it writes through. I had pinned that the *wrong
  way round* on the reasoning that an aliasing accumulator is a footgun, and the
  compiler said otherwise within the hour.

Plus two pieces of infrastructure: a flat byte-addressed memory (the type
checker's memo tables are raw memory — the essay's earlier claim that this arm
could not see memory was too strong; what is missing is *reclamation*, not
addressing), and a correctly-rounded `text-to-double-bits`, which is
deliberately issue 125's better answer.

**codexir at our pin.** 100%, landed at `e9e1751`. This is the thing I did not
expect to build today and would now call the highest-value artifact of the
week. It is the same compiler as `codexzig`, stopping at the IR wire instead of
continuing into the emitter — `generated/codexzig.ir` as a program you can run,
rather than an artifact one guest produced once.

The reason it is cheap is worth stating, because it is why it belongs in
codex-zig-transpiler and not in codex-qemu. The ladder built its codexir through
the seed: bundle, boot a kernel, compile to IR on bare metal, push that through
the ring plug, build the emitted zig. Four stages, two of them guests. But
`codexzig` exists now and is a verified fixed point, so the chain is three host
steps — swap one chapter, transpile, `zig build-exe`. **No QEMU at all.** If we
ever want a codexir that is *bare metal's own* answer rather than the zig arm's,
that is a guest job and it belongs in codex-qemu. This is not that.

**Attribution.** 100%, and it was the first thing codexir did. Seven corpus
programs disagreed with the bank. All seven disagree with it on the zig arm too
— so all seven are Update 55 drift, not interpreter defects. That question is
closed, and it could not have been closed without a same-pin arm: the bank is 23
commits and about 3,000 changed compiler lines behind us.

## Are we on to safari?

Not yet, and the ordering was right. Safari needs an IR oracle and we did not
have one this morning. Now we do.

The route I would take is the one you called (b), and it is stronger than a text
diff: **the safari specs are self-checking.** They carry their own expected
values and print their own verdict. So take a spec, compile it to IR through the
interpreter, feed that IR to the zig emitter, build it, and *run* it. If it
prints its `ok N` lines, the IR is right in every way that program can
distinguish. No gold to bank, no gold to maintain, and it grades the whole
pipeline rather than one serialisation.

The text diff against codexir is still worth having as the cheap daily check.
The run is the one that means something.

## Is codexir good for safari?

**For the run route: yes, and there is evidence rather than hope.** The zig arm
passes all 54 specs today and its fixed point holds — and it carries this exact
defect internally while doing so. Collapsed effect labels demonstrably do not
change the zig that gets emitted for these programs. So the defect does not
stand between us and the safari plan.

**For the text-diff route: not for effect rows.** A program with effects will
have wrong labels in codexir's IR, so a byte comparison there is measuring the
plug. Everything else compares cleanly, which the 35-of-35 number is exactly
about.

So: not stuck. The plug bug is a thing we *found* with the new arm, not a thing
blocking it.

## What the plug bug actually is

Worth writing down because the chain is short and every link is measured.

A six-line program:

    literal 0  other 0  computed 6291456  empty 0  heap 6291621

`address-of` on a **source-literal Text answers 0** on the zig arm — the same
value the *empty* text answers. A computed text gets a real address. The cause
is one line of the prelude:

```zig
if (cx_pi.size == .slice and v.len == 0) return 0;          // documented
const cx_p = ...;  const cx_base = @intFromPtr(cx_heap_base());
return if (cx_p >= cx_base) @intCast(cx_p - cx_base) else 0; // .rodata → 0
```

The empty-slice case documents 0 as a deliberate sentinel meaning "no pointer,
share as-is". The guard's fall-through then hands that *same sentinel* to every
literal in `.rodata`, which is below the heap base.

And the compiler reads the sentinel as an answer:

    mcopy-name-fresh (nm) (a) (slot) (mc) =
       let tv = mcopy-text (nm.value) mc
       in let k = cons-norm (cons-mix 701 (address-of tv))
       in let v = cons-lookup k mc
       in if v /= 0 then mcopy-name-adopt slot v mc

A `Name`'s entire content key is the address of its canonicalised text. That is
sound when `address-of` is faithful, and bare metal satisfies it. With every
literal answering 0, every literal-named `Name` collides on one key and the
first one copied is adopted by all the rest.

The observable: one program, six effect labels.

| arm | labels |
|---|---|
| bare metal @ `53b3b213` | `Device.Mmio`×3, `Device.Port`×2, `Console.Write`×1 |
| bare metal @ `safari-u56` | distinct |
| Rust interpreter @ u56 | `Device.Mmio`×3, `Device.Port`×2, `Console.Write`×1 |
| zig arm @ u56 | `Device.Mmio`×**6** |

**Why it stayed invisible for so long.** `mcopy-name` only runs on names inside
the copied region, and names from *user source* are computed texts with real
addresses. Only names built from literals in the **compiler's own source** hit
the zero path — which is essentially the builtin table's effect labels. Nothing
in the fixed point or in the specs reads those back. Both arms were green with
it, because it never reached anything either arm looks at.

The comment sitting directly above `cx_address_of` describes this exact failure
mode as Finding 31 — *"answering a constant 0 made every object identical to
every other one AND to null, and the compiler reads that as an answer."* That
was fixed for the constant case. The `.rodata` residue survived it.

## Two things I am not claiming

**Whether the emitted zig changes.** The corruption is in the shipped `-cdx`
path's IR, so it is the plug and not my harness. But the specs passing suggests
effect labels do not reach zig codegen for these programs, and I have not shown
what, if anything, they *do* reach. That is part of the digging you asked for
before we file.

**That our own `address-of` is right.** It returns a raw host pointer where the
plug's is heap-relative — and the compiler compares those answers against
`__heap-save` values with `a < mc.mc-floor` and `__heap-save >= mc.mc-ceiling`.
Our comparisons are being answered on incomparable scales. We get the right
labels; I have not shown we get them for the right reason. That is ours to write
down, and it is exactly the sort of thing that looks fine for months.

## What is genuinely not done

- **Self-compile** — the interpreter compiling the *compiler* to IR. Not
  started. The oracle exists at our pin (`generated/codexzig.ir`), so the answer
  is a byte comparison rather than a judgement. The risk is entirely cost: `fib`
  is two definitions and the compiler is 6,431, and one small corpus program
  already wanted a gigabyte in our interpreter on an 8 GB box. I would measure a
  ramp — one chapter, five, twenty, with steps *and* peak RSS — before
  committing to the whole thing.
- **Safari IR.** Unblocked as of an hour ago, not begun.
- **The plug fix.** Root-caused, not written.

## The order I would take next

1. Fix the plug. It is one function and the diagnosis is complete.
2. Re-run the 35 and see them go to 35 identical with nothing normalised.
3. Then safari, by the run route.
4. Then the self-compile ramp.

And, per your instinct: keep digging before filing. The thing I most want to
know is what *else* keys on `address-of` of a literal — because if it is only
effect labels we have found a cosmetic wire defect, and if it is anything the
emitter branches on we have found something much worse that two green arms have
been carrying.
