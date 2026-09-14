# The screen's architecture: where the time goes, and the choices

The Roc machine now draws Cobblestone's screens: `scene-on-screen`'s 3D
scene, the four GPU widget tests, and `gop-padded-stride`. It draws them
slowly: 3 to 4 seconds for a 320x240 frame in the page's wasm build. This
note is for deciding how the screen should be built before any more
profiling. It sets out what a pixel costs, why, and the choices, with a
recommended order. The questions at the end are Steve's.

## What a pixel costs today

Measured in the page's own build (wasm, Roc's dev backend) unless it says
otherwise. `machine/batch/PERF.md` has the details.

| what | cost |
|---|---|
| `gop-padded-stride`: 123,000 pixel writes, 46,000 reads, one render | 3.0 s |
| `scene-on-screen`: one 320x240 3D render | 3.4 to 4.1 s |
| the same frame's pixels drawn by `MachineGpu` directly (native, dev) | 0.09 s |
| a whole 640x480 GPU frame in `MachineGpu` (native, dev) | 0.37 s |

`MachineGpu` shows what Roc can do with a flat buffer written in place:
about a microsecond a pixel, including a depth test and a colour
interpolation. The emitted programs pay far more per pixel than that, and
the difference is not in the memory itself.

## Why: every pixel copies the whole machine

A Codex program that touches memory or a device is emitted with the machine
threaded through it: every such function takes the machine and hands it
back. One `poke-32` in a loop becomes this Roc:

```roc
fill_fb! = |machine, base, i, n| (if (i >= n) { (machine, 0) } else { ({
	(machine1, _d) = Machine.store(machine, base, (i * 4), sentinel, 4)
	fill_fb!(machine1, base, (i + 1), n)
}) })
```

`Machine.store` finds what backs the address and returns
`{ ..m, gpu: ... }`: a new machine record. **That record is flat, and wide.**
It has 24 fields. The e1000, the NE2000 card, the HPET, the APICs, the PCI
table, the disks and the GPU are records inside it, and a Roc record inside a
record is stored inline. Only lists and dictionaries sit behind a reference.
So every door call copies the whole machine: roughly a kilobyte, an estimate
from the field list, since Roc does not report sizes. It does that twice for
every pixel a program writes and reads back.

**BASIC measured this exact effect.** Its step's cost grew with the machine
record's width:

| added to BASIC's machine record | P134's run time |
|---|---|
| 15 lists, as loose fields | +35% |
| 15 integers, as loose fields | +13% |
| 15 lists, in a nested inline record | the same as loose |
| 15 lists, behind one reference (a one-element list) | about 0 |

BASIC's next step was to split its machine into hot state and a cold part
behind one reference. It was planned, not built.

There is a second, older problem: Roc copies a list it can still reach
(`reference_roc_list_copying`). A value threaded down a recursion and handed
back, or a field taken out of a record in a separate statement, makes the
next write copy. `MachineGpu` avoids it by construction, measured flat at
every size; any new shape has to be measured the same way.

## The three modes

Steve's three modes for the screen, and what each one needs:

1. **Simulated hardware, from boot to image.** The machine as it is: the
   program boots, drives the devices, and the page shows the framebuffer it
   left. This needs the per-pixel cost down, since everything goes through the
   machine's doors.
2. **A zig host verifies.** The same emitted program on a native host (such
   as `machine/native`, whose C allocator already runs `gop-padded-stride` in
   3.1 s against 22.4 s on Roc's default platform), checking the image, for
   instance against a hash. This needs a native build and something to compare
   the image with.
3. **Direct use of the image code in the browser.** Cobblestone's drawing
   chapters (Renderer3D, GopDraw, GpuRender) called directly by a browser app
   that owns a framebuffer, with no machine in between. It needs no boot and
   no devices, so it can animate. It needs its own small platform and app,
   like the games', and a memory model for the chapters' pokes.

## The choices

**A. Split the machine into hot and cold.** The machine keeps the fields a
pixel touches (memory, the GPU's planes, the clock) and puts everything else
behind one reference:
`Machine : { mem, gpu, clock, cold : List(Cold) }`. A memory or GPU door then
copies a few dozen bytes instead of a kilobyte. A device door takes the cold
part out and puts it back inside its own record update, the shape BASIC's
devices proved.

- **Serves:** modes 1 and 2, and the whole ladder, since every machine program
  pays the width today.
- **Cost:** a mechanical rewrite of `Machine.roc`'s device doors, nothing in
  rocemit.
- **Risk:** the copying rules; measured by the `mmap` count at three sizes, as
  `MachineGpu` was.
- **Keeps:** the machine as a value, so snapshots, stepping back and the tests
  all still work.

**B. Memory owned by the host, as effects.** `peek` and `poke` become hosted
calls into a byte array the platform owns, so the machine record stops
carrying memory at all.

- **Serves:** mode 1's speed most directly.
- **Cost:** the machine is no longer a value, so no stepping back and no
  comparing two machines. The ladder's platform and the page's would both have
  to own memory, and every memory door becomes an effect.
- **Risk:** it changes what the machine is. The essay's architecture ("one
  value holding every device") would change with it.

**C. The image code directly (mode 3).** Emit the drawing chapters as a
library, with memory as one flat, bump-allocated arena rather than the
machine's tree. A browser app renders a frame per animation step into a
framebuffer it hands the page.

- **Serves:** mode 3, and a page that moves.
- **Cost:** a platform and app (the games are the template); an arena
  memory model; deciding what a frame's inputs are, such as a camera angle.
- **Risk:** the same copying rules, in a new app; the chapters' pokes still go
  through a door, just a narrower one.

**D. An LLVM build for the finished page.** Steve has agreed to LLVM for a
finished product. BASIC's LLVM build ran 2.7 times faster, and struct copies
are the kind of cost an optimizer can remove.

- **Serves:** every mode's published page; it changes nothing we iterate on.
- **Cost:** BASIC's build took 1,420 s and peaked at 2.2 GB.
- **Risk:** it hides the costs above instead of removing them, and the
  per-pixel cost still shapes what the dev build can show.

**E. Report the copying to Roc.** `roc-apps/findings/` holds reduced programs
for three of the copying rules, and none has been reported. Steve's call.

## A recommended order

1. **A**, measured before and after on the screen programs and the ladder.
   It removes a cost every machine program pays, keeps the machine a value,
   and is the step BASIC had already found.
2. **C**, a first animated page: `scene-on-screen`'s scene turning, using the
   code the machine already runs.
3. **D** when a page is published.

**B** changes what the machine is, and I would not start it without a reason A
leaves behind.

## Questions for Steve

- Is A the right first step, or should the screen move straight to mode 3 (C)?
- For mode 2, what should "verifies" check: a hash of the image, a golden
  image, or the program's own printed output?
- Is stepping back through a machine's history something the screen modes
  should keep? B gives it up.
