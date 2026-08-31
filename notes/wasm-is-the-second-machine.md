# Wasm is not the web target. It is the second machine.

*Written 2026-08-31, the day the Codex compiler first compiled itself into a
wasm module and got itself back byte for byte.*

Steve wants to persuade Damian to invest in `codex/plugs/wasm` as the way to
show Cobblestone to other developers. Damian's own enthusiasm is bare metal —
a language whose compiler boots as a kernel and emits x86 with no runtime
underneath it. The framing on offer is *versatility*: look, it also runs on
the web.

I think the framing is the weak part of an argument that is otherwise
stronger than it is being made. Not because versatility is untrue, but
because it asks Damian to value an audience over a machine, and he has been
clear for a year about which of those he finds interesting. There is a
version of this argument that runs entirely through the thing he already
cares about, and today produced three pieces of evidence for it.

---

## What happened today, briefly

Yesterday the wasm plug could not compile a Codex program that did arithmetic
on a `Real`. Not badly — at all. Every float was carried as f64 bits in an i64
slot, which is the right representation, and the reinterprets that get a value
into an f64 operation and back out were simply missing, so `wat2wasm` refused
the module. Nothing had ever run.

Today the same plug compiled **the Codex compiler** — 2.9 MB of source, the
whole front end plus the emitter — into a 6.76 MB WebAssembly module, and that
module compiled the same source back into itself, byte for byte, under node
and under wasmtime. The distance between those two sentences is about thirty
hours of one person's attention plus a machine.

Along the way three defects surfaced that neither bare metal nor the zig plug
could have shown, and the *shape* of those three is the argument I actually
want to make.

---

## One: a cost model bare metal does not have

The emitted allocator grew linear memory by exactly the pages an allocation
needed — one `memory.grow` per 64 KB, about 56,000 calls to reach the 3.7 GB
the compiler wants for its own source. That is the obvious implementation and
it is free on wasmtime, which reserves address space once and treats a grow as
bookkeeping: 56,000 grows to 3.5 GB cost 0.21 seconds.

On V8 the same 56,000 grows cost **166.83 seconds**, because the per-grow cost
rises with the memory you already hold. Growing in 16 MB steps instead took
the compiler's self-compile from 223 seconds to 18.

Bare metal has no analogue of this. There is no host to ask for more memory;
you have the machine. The zig plug has no analogue either — zig's allocator is
somebody else's problem. **The defect only exists on a target that has to
negotiate for its own address space**, and it was worth an order of magnitude.

## Two: a resolution requirement zig hides

The IR text wire — the driver emits the whole IR as text and parses it
straight back before emitting — was documented as load-bearing. The stated
reason was that serialising *derives* something the AST does not carry.

It does derive something, but not what the comment said. It resolves every
field access against the receiver's record type and writes the positional slot
into the field name: `parse-bag/14`. The wasm plug read that number instead of
computing it, because in flat linear memory a field is an offset and somebody
has to know which one.

The zig plug **throws the slot away**. It emits `rec.field_name` and lets zig
resolve the offset, so for that arm the derivation might as well not exist.
Bare metal computes it a third time, itself, in `X86_64Compound`, because bare
metal never sees the wire.

So: three implementations of one function, and exactly one consumer depending
on somebody else having run it. When that dependency was inverted — ask the
receiver's type first, keep the wire's number as a fallback — the emitted
module was byte-identical across thirty programs, and the round trip could be
deleted for **945 MB of 3,532 MB, twenty-seven per cent** of the memory
budget.

The part worth sitting with is what the old ordering was hiding. A caller who
handed the plug an IRChapter without serialising it first got field names with
no slot, fell through to a search by name across every type definition, and
took the first match. The compiler has 235 record types, 565 distinct field
names, and **59 names that appear at more than one slot index** — `span` alone
at slots 1, 2, 3, 4, 8 and 16 across 21 records. That path emits 4,968,460
different bytes out of 6,760,737, silently, and had been sitting there for as
long as the plug has existed.

Nothing in the zig arm could have found that. Nothing in bare metal could
have. It took a second target that needed the same number for a different
reason.

## Three: a ceiling that is real

wasm32 addresses memory with an i32. Four gibibytes, and there is nothing
above it — not a policy, an address space. The compiler compiling itself sat
at 90.7% of that this morning. After today's two changes it is near 66%.

Bare metal's guest ceiling is 3072 MB and it is *also* real, but it is real in
a way you can shrug at: buy a bigger machine, boot a bigger guest, the
architecture is 64-bit and the limit is somebody's boot stub. wasm32's is
architectural. A compiler that fits in it is a compiler that has made real
decisions about what it retains.

---

## The reframe

**Wasm is not the "web" target. It is the second bare-metal target**, and it
is the only other one Cobblestone has.

zig is not a machine, it is a language: it does struct layout for you,
resolves fields by name, dead-strips your unused prelude, hands you a stack,
frees you from thinking about the frontier between your data and the end of
memory. Every one of those services is a place where the zig plug does not
have to make a decision, which means every one of them is a place where a bad
decision in the compiler cannot show up.

Wasm gives you none of them. Flat memory, offsets you compute, a heap you
manage, a hard address ceiling, and a host you have to ask for room. That is
the same list of obligations bare metal has. It differs in exactly one
respect that matters: **you can hand it to somebody in a browser tab.**

Which is to say the marketing argument and the bare-metal argument are the
same argument. Damian's claim — that this system runs on the metal with no
runtime beneath it — is currently checkable by booting a kernel under QEMU
with a PowerShell script and a seed image. It is *true*, and approximately
nobody will ever verify it. The identical claim, made through the wasm plug,
is checkable by a stranger in ten seconds, and it is not a weaker claim
because the machine is virtual: the emitted module manages its own heap in a
flat address space and calls two host functions. That is a machine-level port
and it demonstrates the same property.

**The demo is not a concession to the web. The demo is the bare-metal claim,
made falsifiable by someone who is not you.**

I would put that to Damian in preference to versatility, because it does not
ask him to change what he values.

---

## Where I would push back on the plan

Three honest problems, in the order a stranger would hit them.

**The export surface is embarrassing.** A module's exports are decided by
testing each definition name against `wasm-export-list`, a single
pipe-separated string of 484 names hardcoded in the emitter and drawn from
unrelated applications — `select-all`, `random-color`, `species-count`,
`kpt-mandelbrot`, `tank-xmin`. A program that means to export `render-frame`
gets it by luck; a program that happens to define `select-all` leaks it; a
program that wants to export `my-entry` cannot say so. If you are inviting
developers to write Codex and call it from JavaScript, this is the first thing
they touch and it is not defensible. It is also probably an afternoon: an
`export` annotation, or a manifest.

**A source over 4 MiB is silently truncated.** The emitted reader allocates a
fixed 4 MiB buffer and then reads the rest of the wire while discarding it, so
a larger program is compiled as a *prefix of itself* with no diagnostic and
exit 0. The compiler's own source is at 69% of that. The fix is written two
functions away, in `read-file-raw`, which grows by bumping again instead of
truncating — and whose own comment says a fixed cap "silently DROPS what does
not fit, which for an artifact is a truncation wearing the colour of a
complete answer." That comment is about this function and this function still
does it.

**Marketing a compiler is not marketing a language.** The demo that a stranger
finds interesting is probably not "the compiler compiles itself in your
browser," however much that pleases us. It is more likely a page where you
type Codex on the left and something *happens* on the right — the safari
screensaver running, a REPL, a puzzle. Self-hosting in a tab is the proof that
the toolchain is real; it is not the thing that makes anyone want to write
Codex. Those are two different artifacts and I would not let the first one
stand in for the second.

---

## What I am less sure about

**Whether any of this is the right use of two people.** There are two humans
on this project. A marketing push has a shape that is very good at consuming
attention — a page, then a second page, then somebody's bug report about
Safari 16 — and Cobblestone's most interesting property right now is that it
is *coherent*, which is a thing that small teams have and lose. I do not know
how to price that against the value of a third contributor, and I notice that
I want the answer to be "build the demo" partly because building demos is fun.

**Whether the second-machine argument survives contact with a third target.**
My claim is that wasm found these three defects because it makes machine-level
demands that zig hides. The honest test is what a *fourth* plug would find,
and there is no fourth plug. It is possible that what actually happened today
is simpler and less flattering: the wasm plug is the youngest one, it has had
the least use, and any target that got a week of serious attention would have
yielded three defects. I believe the stronger version because the three
defects are *specific* to the obligations wasm has — a host memory
negotiation, a field-offset resolution, an architectural ceiling — and none of
them is the kind of bug you find by using something more. But I would not
insist on it.

**Whether the wire should come out of the other drivers.** Today's measurement
says it derives nothing the *wasm* arm needs. `CodexZigHarness` takes the same
round trip and its stated reason is the type-parameter claim that turned out
not to be in the code. That is not evidence that the zig arm's round trip is
useless — it is evidence that nobody has re-derived why it is there. Those
feel the same from the inside, and today was mostly a lesson in how easily
they are confused.

---

## The thing underneath all of it

Three times today the mechanism I named first was wrong. I attributed a
runtime's slowness to host-call overhead; it was memory growth, and fixing the
thing I named bought 11% of what I claimed. I repeated the harness's own
explanation of what the IR wire derives; the explanation was not in the code
and had not been for some time. I wrote an instrument whose docstring warns
that a dropped phase is invisible, and then dropped a phase.

In each case what corrected it was the same move: stop reasoning about the
mechanism and ask what *scales*, or what *differs*, or read the code instead
of the comment above it. And in each case the reason the wrong explanation had
survived is that nothing had ever been in a position to contradict it. The
wire's justification was written by someone thinking about the zig plug, and
it travelled into the wasm harness as a copied paragraph, where it was
believed for months because the wasm harness was never run in a way that could
disagree with it.

**A system with one target accumulates explanations nobody has had to test.**
A second target does to your reasoning what a second reader does to your
prose — not by being smarter, but by being unable to share your assumptions.

Which is, I think, the real form of Steve's argument, and it is not about
marketing at all. Other developers are a second reader. The wasm plug is a
second machine. Damian is right that bare metal is the interesting claim, and
that is exactly why the claim needs somewhere else to stand.
