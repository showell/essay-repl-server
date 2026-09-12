# Effects as state: emitting Cobblestone's kernels, and what it was worth

*2026-09-12, at the end of the gpu track. The lowering rocemit gained, the
gallery it made possible, and an honest answer to Steve's question: did this
lay infrastructure, or was it niche?*

The gallery: <http://143.244.172.148:9204/gallery.html>. All thirty-nine of
Cobblestone's gpushow pages, their forty-six Codex kernels emitted to Roc,
in one module, eye-tested. Each demo links to its emitted Roc and its Codex.

## The rule

A Codex kernel runs under the `Device` effect: it loads and stores buffer
words and asks for its thread index. Roc has no such effect, so rocemit
lowers it to state. The rule fits in five lines:

- A definition whose type carries `[Device]` takes the device as its first
  parameter and answers it back, paired with its result.
- In an `act`, `x <- e` becomes `(dev1, x) = e'`, where `e'` is `e` with
  the current device passed in; each statement hands the next a fresh name.
- A `let`, an `if`, a call of another `[Device]` definition: the device
  goes in and comes out, unchanged in shape.
- A pure expression in an effectful position is paired with the device as
  it stands.
- `device-load b i` is `Device.load(dev, b, i)`; the other operations
  likewise, on a hand-written module of forty lines.

The fountain kernel, as emitted:

    cp_step : Device.Device, I32, I32, I32, I32 -> (Device.Device, I32)
    cp_step = |dev, inb, outb, frame, gid| ({
        (dev1, px) = Device.load(dev, inb, I32.times_wrap(gid, 4))
        (dev2, py) = Device.load(dev1, inb, I32.plus_wrap(I32.times_wrap(gid, 4), 1))
        ...
        ({
            nvy = I32.plus_wrap(vy, cp_grav)
            ...
            ({
                (dev5, _s0) = Device.store(dev4, outb, I32.times_wrap(gid, 4), rpx)
                ...
                Device.store(dev7, outb, I32.plus_wrap(I32.times_wrap(gid, 4), 3), rvy)
            })
        })
    })

Two facts about Roc make this a program and not a demonstration. `List.set`
on a list nobody else holds writes in place, so a store is a store. And the
compiler turns the tail-recursive dispatch into a loop, so 786,432 threads
in sequence do not touch the stack.

The wrapping arithmetic is the second thing the track added: a unit with a
kernel is spelled in I32 and F32, because that is what the wgsl plug's
shaders compute in, with WGSL's total division and remainder. A kernel that
packs an alpha of 255 times 2^24 needs the wrap. Every other unit stays
I64 and F64. The emitter's numeric spellings became parameters of the
context to make this one choice, which is small but permanent.

The third thing is a library mode: a unit with no opening emits its chapters
and no app. Safari could not have used it, since its specs are openings; a
real app, whose entry is hand-written Roc calling emitted chapters, needs
nothing else.

## The gallery as a machine

A page is a plan: its buffers by size or by what seeds them, its passes in
order with the buffer each binding is, whether odd frames swap the pair, and
how the page draws the words. Twenty-six pages are the plasma shape and
their plan is read off the page. Thirteen have theirs written by hand from
their bind groups, as a table in the generator, because that is the page's
knowledge and not the kernel's. From the plans the generator writes one Roc
app, a boxed model with `step` and `view`, and a manifest for the page.

The oracles are the method from safari, reused: a Python evaluation of the
Codex source over the plug's integer semantics, compared by checksum. Plasma
and the fountain match to the word, the fountain including the page's own
random seeding, a linear congruential generator in JavaScript doubles whose
product passes 2^53, emulated in F64.

## Was it worth it? The honest accounting

**What became infrastructure.** Four things, in decreasing weight.

1. *Library mode.* Every real app will be hand-written Roc over emitted
   chapters. This is the mode they all need, and it did not exist.
2. *The effect-threading skeleton.* Codex has other effects, and a Roc
   platform will lack most of them. The skeleton (a typed definition takes
   and returns the state; an act threads it; let, if and calls pass it) is
   general; what is Device-specific is a table of five operations and the
   forty-line module. The next effect costs the table.
3. *The model platform, twice.* Safari's platform and the gallery's are the
   same shape: one boxed model, a step, a view, a host that owns one
   reference and keeps one list. Two users is the point at which the
   doctrine says an abstraction has earned its keep, and this one has. One
   shared platform is a morning's work and would make the third app cheap.
4. *The oracle method.* Python over the Codex semantics, a checksum, and a
   Node smoke that renders every demo headless with its time. Nothing in it
   is about GPUs.

**What was niche.** Device mode's WGSL rules; the generator reading Damian's
HTML for buffers and entries; the seeds; the canvas draws that mimic five
vertex shaders. Roughly four hundred lines that serve Cobblestone's gallery
and nothing else. Fine for a demo, and not a foundation.

**What it did not touch, which is the part that matters for the next
choice.** The forty-six kernels are integer and real arithmetic under one
effect. They exercised none of the emitter's hard parts. The forms rocemit
still refuses, by name, are: `handle`, `try`, `with-timeout`, field-store,
char literals, a lambda as a value, vector patterns, a `match` under an
effect, and any effect but Device and the opening's Console. Safari hit the
type system, sums, records and matches; the gpu track hit effects and
numeric semantics; the handlers and the text-and-char machinery have been
hit by nothing. A port that used them would find real gaps in a day, the
way plasma found the wrapping in an hour.

**The verdict.** Not too niche, because the three heavy pieces (library
mode, effect threading, the model platform) are what any next app needs,
and the demo is a good one. But the track is at its end in terms of what it
can teach the emitter, and a second gallery-shaped port would teach nothing.

## What I would port next

Something with handlers and text. The emitter's refusals are concentrated
there, and Codex programs that matter, the compiler and its tools among
them, are made of `handle`, `try`, records with stores, and characters.
Candidates, by how much they would teach:

- **A Codex tool with a `handle`.** The smallest program in the corpus that
  installs an effect handler and reads text. It would force the question
  the Device work sidestepped: a handler is a function from an effect's
  operations to a state, and its Roc spelling is a record of closures
  around the same threading. Twenty units in the curated set have one.
- **Safari's sibling, the night walk.** Same shape as safari, so cheap, and
  a second screensaver on the same platform is what makes the shared
  platform real. It teaches the emitter little.
- **A roc-lang port going home.** The twenty-nine roc-lang programs in the
  curated corpus were ported from Roc to Codex; emitting them back gives an
  oracle nothing else has, the original Roc, and they lean on text, chars
  and matches. The result is a comparison, not an app.

The first is the one I would take. It is where the refusals are.
