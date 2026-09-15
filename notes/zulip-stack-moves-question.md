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

## Two kinds of copy, kept apart

The question should not blur them.

1. **A record moved by value.** Its cost is the code that moves it: under dev
   that is stack slots, under LLVM mostly registers. It is linear in the
   record's width, and paid once per move.
2. **A list copied because Roc can still reach it.** Roc writes a list in
   place only while its reference count is one. When some spelling of the
   program keeps a second reference alive, every write copies the whole list.
   That is linear in the list's length, paid on every write, and invisible:
   no diagnostic, no type error.

**What we already know about the second kind** (roc-apps `findings/`, nightly
2026-09-11):

| finding | backend | what copies | mmap per 10,000 writes |
|---|---|---|---|
| `threaded-record-copy` | LLVM (the default) | a record holding a list, passed down a recursive function and handed back, then written | 10,001 (2 without the recursion) |
| `threaded-record-copy`, a recursion that only reads the record | LLVM | nothing | 2 |
| `helper-arg-copy` | dev | a helper given the record AND a value read from it (`settle(m, m.fuel)`), then a store through a multi-tag union holding lists | 50,006 (10 with `settle(m, 0)`) |

- **Both are reduced programs** of under 30 lines, with every ingredient cut
  until the copy stops.
- **Neither is understood.** `helper-arg-copy` needs four conditions together,
  and its hypothesis, a borrow held across the call, is not verified.
- **Our BASIC machine lost days to three more shapes** that are not reduced
  (roc-apps memory: a loop that rebuilds a record, a big `match` with inline
  arms, a field read in a separate statement).

## The small program

`roc-apps/findings/zulip-copies/`, built with LLVM and with dev, measured by
how the time scales rather than by one number:

- **`ThreadCopy.roc`, the second kind of copy.**
  - The program makes 20,000 writes into a list inside a state record, at list
    sizes of 4,096, 32,768 and 262,144.
  - Before each write, a recursive walk over a short text either never sees
    the state (`none`), is given it and only reads it (`reads`), or is given it
    and hands it back unchanged (`returns`).
  - A flat time across sizes means the writes happen in place. A time that
    grows with the size means every write copies.
  - `strace` counts each copy as an mmap.
- **`RecordWidth`, the first kind.**
  - The program runs 20 million steps of a loop carrying one record of 4, 32
    or 256 `F64` fields, two of them updated per step.
  - A flat time across widths means the record is not copied per step.

## What the small program shows

**The first try did not copy.** `ThreadCopy`, written from scratch, wrote in
place in every shape under both backends. So the program was rebuilt from
`threaded-record-copy`'s known copier and cut one ingredient at a time
(`findings/zulip-copies/thread/`). Each variant makes 10,000 writes into
`num`, a `List(F64)` inside a record. Figures are at a list of 65,536; the
full table has 286 and 4,096 too.

| variant | what differs from T1 | `--opt=speed` | `--opt=dev` |
|---|---|---|---|
| `T1_walk_returns` | a recursive walk hands the record back; the record has two more lists; the write is inline in the tail call | **1.9 s, 5,003 mmap** | 0.00 s, 3 mmap |
| `T0_no_walk` | no walk | 0.00 s, 3 | 0.00 s, 3 |
| `T4_walk_reads` | the walk only reads the record | 0.00 s, 3 | 0.00 s, 3 |
| `T2_one_list` | no other list in the record | 0.00 s, 3 | 0.00 s, 3 |
| `T3_write_in_helper` | the write in its own function | 0.00 s, 3 | 0.00 s, 3 |
| `T5_bytes_only` | one other list, a `List(U8)` | **1.87 s, 5,003** | 0.00 s, 3 |
| `T6_strs_only` | one other list, a `List(Str)` | **1.87 s, 5,003** | 0.00 s, 3 |
| `T7_one_byte_walk` | the walk recurses once a step | **1.93 s, 5,003** | 0.00 s, 3 |

The copying rows grow with the list: 0.03 s at 286, 0.15 s at 4,096, 1.9 s at
65,536. The count of copies stays at 5,003. **Under LLVM every other write
copies the whole list. The dev backend writes all of them in place.**

**The copy needs three things together:**
1. **A recursive function is given the record and hands it back.** A walk
   that only reads it does not copy, and neither does no walk.
2. **The record holds a second refcounted field besides the written list.**
   Any list will do.
3. **The write is spelled inline in the tail call's argument**
   (`spin({ ..m1, num: List.set(m1.num, 7, 1.0) ?? crash("oob"), pc: i }, ...)`).
   The same update in a helper does not copy.

**The result is the same on nightly-2026-09-11-793f9d8 and
nightly-2026-09-12-220fd47.** nightly-2026-09-15-fe09c42 does not run on this
machine: it dies with SIGILL on any `check` or `build`, on a CPU with AVX2 and
no AVX-512.

**`RecordWidth`, the first kind of copy.**
- 20 million steps take 0.05 s under LLVM at 4, 32 and 256 fields.
- Under dev they take 0.19 to 0.21 s at 4 and 32 fields, and 25 to 26 s at 256
  (both nightlies).
- LLVM does not pay for the width; dev pays heavily past some size.

**Known issues nearby, both closed:**
- roc-lang/roc #10218, "Any read of a loop-carried list makes the next
  mutation copy the whole list" (no longer reproduces);
- #10920, "Tail-call arguments are forced owned, losing borrows from outside
  the SCC", fixed by PR 10990 on 2026-09-03, before either nightly above.

Borrow inference lives in `src/lir/arc_solve.zig`, which as far as we can
tell both backends share. So a copy under LLVM that dev does not make is the
question.

## A draft question

> **`--opt=speed` copies a list on every other write that `--opt=dev` updates in place**
>
> The program below makes 10,000 writes into `m.num`. Built with `--opt=dev` it writes in place: 3 `mmap` calls at any list size. Built with `--opt=speed` (nightly-2026-09-12-220fd47, x86_64 Linux, default platform) it copies the list on every other write: 5,003 `mmap` calls. The time grows with the list: 0.03 s at 286 elements, 0.15 s at 4,096, 1.9 s at 65,536.
>
> It stops copying if any one of these changes:
> - `walk` only reads `m` instead of handing it back;
> - `M` loses `scr` and `out`. Keeping either one alone still copies.
> - the record update in `spin` moves into its own function.
>
> *(T1's 25 lines)*
>
> Three questions:
> 1. Is this a known difference in how reference counting is placed on the LLVM path, and is `arc_solve.zig` (after #10920) the place to look, or something LLVM-specific?
> 2. Is there a way to see where a list write loses uniqueness: a flag, a debug counter, anything better than counting `mmap` calls? And is there a way to map `roc__proc_NNN` in a profile back to source names?
> 3. Under `--opt=dev`, a loop carrying a 256-field record takes about 25 s where LLVM takes 0.05 s, and in our real code most instructions move values between stack slots. Is register allocation for the dev backend planned, or is `--opt=dev` meant only for fast builds?

Written by Claude, working with Steve Howell; Steve decides whether and when
it goes.

## Still to gather before asking

- A nightly after 2026-09-15 that runs here, to check the copy still happens.
- Whether the copy happens for `--target=wasm32` as well as native.
- The ARC placement in the LLVM build of `T1` against `T2` or `T3`, if the
  LIR dump shows where the extra increment comes from. That would turn the
  question from "why" into "is this the line".
- Renderer3D's row loop, a second and different shape of code, only if the
  question needs it.
