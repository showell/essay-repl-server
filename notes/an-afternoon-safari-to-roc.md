# An afternoon: safari, from Codex to Roc

*2026-09-11, night. Written the evening the Roc bird first sat on its tree.
Open-ended on purpose: this is what happened, what it seems to mean, and
what I do not know yet.*

## What happened

At noon safari was a Codex program: fifty-four spec chapters, a browser
harness, and a wasm module compiled by a zig transpiler. By nine in the
evening the same screensaver was running in the same browser page from a
wasm module compiled by Roc, from Roc modules emitted by our own compiler,
with a purple origami bird on the fifth tree on the right of every segment
that the Codex version does not have. The fifty-four specs pass under Roc,
byte for byte against the verdicts the Codex interpreter froze, in
twenty-seven seconds.

The order of the day, because the order was the method:

1. Two specs ported by hand, ViewYaw and SceneLimits. They found the Roc
   facts the emitter would need: every Real is an annotated `F64` because a
   bare fraction is a `Dec`; `main!` takes args and answers a `Try`; the
   Echo platform's `echo!` writes no newline; `List.len` is a `U64` and
   Codex's Integer is an `I64`, so the conversions live at three seams.
2. The subset, counted. A script over the fifty-four frozen IRs said
   exactly which forms safari uses: records, literals, calls, `F64`
   arithmetic, `if`, `let`, `match` over four sums and Maybe, list
   literals, field access, fifteen builtins. Nothing else. That bounded the
   emitter to an afternoon.
3. The emitter, on the typed IR. Every node in our compiler's IR carries its
   type, so the emitter never infers: it re-spells. Its first sweep passed
   forty-nine of fifty-four. The five failures were two Roc facts, a lifted
   lambda's name and Roc's refusal to shadow.
4. The layout that matters: one Roc type module per Codex chapter, whole,
   as written, and the spec as an app importing them. That is the shape a
   screensaver imports too. Three more Roc facts: a module named Cat whose
   type is Cat sees a bare `Cat` as its own void type; a chapter's text must
   not depend on which spec is attached, so binder freshening and the
   driver's inlining are scoped to the chapter; derived definitions belong
   to the chapter that declared their type.
5. The platform. Roc's own test tree had the pattern: a platform that
   `provides` named functions over a boxed model, a zig host that calls them
   as C externs, `roc build --target=wasm32`. The host is a hundred lines
   and the app is a hundred lines; the sixteen exports the page's
   JavaScript binds are the same sixteen the zig shim had.
6. The speed. The first frame was 110 ms. Codex builds a list by `x & f
   rest`, and in Roc each level of that copies everything below it; the
   emitter now recognises the shape and writes an accumulator loop,
   appending one element at a time, because appending by concatenation is
   fifty times slower. The frame is 15 ms.
7. The bird.

## The bird, in Roc

This is the first Roc in safari that was written rather than emitted, and it
is short because everything it needs was already there as a chapter: the
frame that places a point on the road in the rider's frame, the camera that
projects it, the still machinery that maps a polygon onto an anchor at a
depth. The logo is roc-lang.org's SVG, six polygons, in the same unit frame
the baked animals use.

```roc
RocBird :: [].{
	# The logo as a still, beak toward +x. Colours are the site's logo-dark
	# and logo-light.
	polys : List(Stills.StillPoly)
	polys = [
		{ color: 6368222, grad: [], pts: [{ x: -0.0344, y: 0.5715 }, { x: -0.148, y: 0.0 }, { x: 0.0368, y: 0.1469 }, { x: 0.0183, y: 0.2577 }] },
		{ color: 8542181, grad: [], pts: [{ x: 0.2216, y: 0.6413 }, { x: 0.3497, y: 0.5025 }, { x: 0.3679, y: 0.5849 }, { x: 0.3862, y: 0.6862 }] },
		# ... four more, the whole logo is six polygons
	]

	# A bird stands this tall, in metres, on its treetop.
	height : F64
	height = 2.2

	# The fifth tree on the right: trees are planted in pairs, left then right,
	# and across > 0 is the right side.
	fifth_right : List(Scenery.Tree), I64, I64 -> [Found(Scenery.Tree), NoTree]
	fifth_right = |trees, i, seen| match List.get(trees, I64.to_u64_wrap(i)) {
		Err(_) => NoTree
		Ok(t) => if t.across > 0.0 {
			if seen == 4 { Found(t) } else { fifth_right(trees, i + 1, seen + 1) }
		} else {
			fifth_right(trees, i + 1, seen)
		}
	}

	# The bird for chain position d, or nothing when its tree is behind the
	# near plane or too small to draw.
	perch : List(World.Segment), List(I64), Frame.Pose, F64, F64, I64 -> List(Paint.DrawCmd)
	perch = |segs, ch, pose, cf, view_w, d| {
		seg_idx = List.get(ch, I64.to_u64_wrap(d)) ?? crash("chain index")
		seg = List.get(segs, I64.to_u64_wrap(seg_idx)) ?? crash("segment")
		match fifth_right(seg.trees, 0, 0) {
			NoTree => []
			Found(t) => {
				rp = Frame.at(segs, ch, pose, d, t.along, t.across + seg.width / 2.0)
				if rp.forward <= Geom.near {
					[]
				} else {
					ht = (height / rp.forward) * cf
					if ht < SceneLimits.min_scenery_px {
						[]
					} else {
						top = Camera.project({ right: rp.right, forward: rp.forward, height: t.height }, cf, view_w)
						# Facing the road, which is to a right-side tree's left.
						Critter.critter_polys(top, Critter.facing(False), ht, polys, 0)
					}
				}
			}
		}
	}

	# Every bird in the chain, nearest segment first.
	draw_all : List(World.Segment), List(I64), Frame.Pose, F64, F64 -> List(Paint.DrawCmd)
	draw_all = |segs, ch, pose, cf, view_w| draw_from(segs, ch, pose, cf, view_w, 0, [])

	draw_from : List(World.Segment), List(I64), Frame.Pose, F64, F64, I64, List(Paint.DrawCmd) -> List(Paint.DrawCmd)
	draw_from = |segs, ch, pose, cf, view_w, d, acc|
		if d >= U64.to_i64_wrap(List.len(ch)) { acc } else {
			draw_from(segs, ch, pose, cf, view_w, d + 1, List.concat(acc, perch(segs, ch, pose, cf, view_w, d)))
		}
}
```

The app appends `RocBird.draw_all(...)` to the frame before the expansion
that turns draw commands into what the canvas can paint. Twelve polygons
more in the first frame, two birds; two and a half milliseconds more per
frame.

## What it seems to mean

**The IR was the asset.** The whole emitter is one file that re-spells a
typed tree. There was no type inference, no scoping, no name resolution to
write, because the compiler that produces the IR had done all of it and had
been graded to 100% against the reference before this day began. The
afternoon was cheap because the month before it was not.

**Roc's module system fits a chapter.** A void module, `Slug :: [].{ ... }`,
with the chapter's types and definitions as associated items, reached as
`Slug.name` from anywhere else: that is a Codex chapter, and it is also what
an app imports. The one wrinkle was a module and a type sharing a name, and
the fix was to always qualify.

**The gate did the work.** Every change to the emitter was a full sweep,
fifty-four units against frozen verdicts, and every sweep was green or
named its failures by cause. The three regressions of the day (the tuple
equality, the shadowing, the chapter identity) were each one cause, found
by the sweep, fixed in one commit. When the debug compiler made the sweep
five minutes it was still tolerable; the nightly made it twenty-seven
seconds, and the difference is the difference between checking and
guessing.

**Measure before working around.** The literal-checker slowdown looked like
Roc being slow; it was the debug build's assertion loop, and a release
build made it vanish. The cons-by-concat slowdown looked like the same
kind of thing and was not: it is the language's cost model, and the
emitter had to change shape. The two took the same first step, a profile
and a micro-benchmark, and went opposite ways from there. I lost half an
hour of the second one to a benchmark harness that read the wrong argument
and measured the default branch; the clock said fast and the output would
have said otherwise, had I read it.

## What I do not know yet

- Whether the bird is on the right. I chose the positive-across tree of
  each planted pair; Steve's eyes decide.
- Whether painting the birds last is ever wrong on screen. A treetop is
  rarely behind anything, but "rarely" is not the depth sort.
- Whether the remaining 15 ms is list copying at the frame's big
  concatenations or something in the render itself; the profile has no
  names in wasm and the native run is dominated by its allocator.
- What the Codex version of safari should now be. The Roc chapters are
  emitted from it, so it is still the source; the bird is not in it. That
  is the first divergence, and it is deliberate.

## What is next

The polish that a milestone leaves behind: the emitter's single-file mode
can go, the README should say what the repository is now, and the probes
in the platform want a decision. Then the eye test, for as long as Steve
wants to watch a bird ride a tree.

| repo | revision | role |
|---|---|---|
| roc-lang/nightlies | nightly-2026-09-11-793f9d8 | the compiler |
| roc-apps | eed80e1 | modules, app, platform, the bird, the page on :9201 |
| rust-codex-compiler | aa0cfc0 | `rocemit` |
| safari-codex | units of 2026-09-10 | the Codex source and the verdicts |
