# Notes toward a Zulip question: stack moves, and seeing where copies go

Not a question yet. Steve wants one polished question for the Roc Zulip about
the dev backend's stack moves and about analyzing copy slowness in general,
asked when the evidence is strong enough to deserve a real audience. This
file collects the evidence and the rough edges until then.

## The program

Codex (Cobblestone's language) emitted as Roc by our own emitter, rocemit.
The case in hand is Cobblestone's Raytracer drawing two spheres over a plane
at 160 x 120, as a native bench (roc-apps `framebuffer/bench/`) and as a
wasm32 page. It is floating-point code over small records: a 3-vector is
`{ vx : F64, vy : F64, vz : F64 }`, and a hit is a record of a flag, a
distance, two 3-vectors and a material. Details: the essay
`notes/raytrace-case-study.md`.

## Evidence so far (2026-09-15, Roc nightly)

**The dev backend's code is mostly stack moves.** In the hottest function of
the native `--opt=dev` bench, 1,503 of 1,749 instructions (86%) move a value
to or from a stack slot, and 54 are floating-point arithmetic. The next
hottest: 1,712 of 1,936 moves, no arithmetic. The hottest instructions in
`perf annotate` are `movsd` to a slot. A record moves field by field, slot to
slot.

**The same program, `--opt=dev` against `--opt=speed`,** 30 frames, native,
the same checksums:

| | dev | speed (LLVM, a 2 s build) |
|---|---|---|
| closest hits only | 0.585 s | 0.037 s |
| the whole render | 0.837 s | 0.083 s |

**Reshaping the program helps a little under dev and less under LLVM.**
Carrying a distance instead of a whole hit record through the closest-hit
walk: about 12% under dev, about 11% of the closest-hit time and about 1% of
the render under LLVM. Writing the vector arithmetic inline instead of calling
one-line functions: nothing measurable under dev.

**A change to the program that a compiled backend rewards, dev barely sees.**
Raytracer's closest-hit walk rewritten to compare distances and build one hit
per ray (a Cobblestone PR) takes 12% off the whole render through
Cobblestone's zig plug, in Debug and ReleaseFast alike. The same source,
emitted as Roc, moves the render by 2% or less under dev and under LLVM, and
the walk alone by 1% under dev and 8% under LLVM. The work removed is real;
under dev it is not where the time goes.

**Copies through libc are not where it goes.** `perf` finds no memcpy in the
top functions and under 1% in reference counting.

## What made this hard to see

- **A wasm function is named by id.** Even with `roc build --debug`, the name
  section says `roc__proc_313`. `ROC_LIR_DUMP=` names procedures by source
  (`Raytracer.rt_closest`), but under different numbers (`p19`). We matched
  the two by the constants each function holds and what it calls, with a
  hand-written decoder of the code section.
- **A native build has the same `roc__proc_NNN` symbols,** so `perf` has the
  same problem.
- **The LIR shows the copies** (a record taken apart into twelve scalars and
  built again each loop step) but not what they cost; that took counting
  instructions in the disassembly.

## Candidate questions, not yet chosen

1. Is register allocation for the dev backend planned, and is there a known
   pattern of source that keeps floating-point values out of stack slots
   under dev today?
2. What is the recommended way to find where copy time goes in a Roc
   program: a proc-id to source-name map for `perf` and wasm profiles, or a
   flag that writes source names into the symbols?
3. For code that passes small records by value, is `--opt=dev` expected to be
   an order of magnitude behind `--opt=speed`, or is 16x a sign of something
   specific in how we emit?

## Still to gather before asking

- A minimal Roc program, independent of Codex and rocemit, that shows the
  same pattern, so the question does not need our emitter to reproduce.
- The same comparison for Renderer3D's hot row loop, a second, different
  shape of code.
- Whether wasm32 under dev shows the same ratio as native.
