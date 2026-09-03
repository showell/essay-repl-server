# Camera splits in three, and one of the three is a constant it never uses

`port/Camera.codex` is twelve definitions and ninety lines. It is not a big
file and nobody would have flagged it. The cohesion tool flagged it:

    port/Camera.codex     defs 12 (  4 fn)  edges 10  components  3  SPLIT

Three groups of definitions, and no call path between any two of them. This is
the whole chapter, and then what the three groups are.

## The chapter

```
Chapter: Camera
  cites Safari chapter Trig
  cites Safari chapter Geom

 The perspective projection: a rider-relative ground point at a height becomes a
 screen pixel. Owns the lens constants and the near plane. Pure; no drawing, no
 allocation.

Section: Lens

  camera-w : Real
  camera-w = 960.0

  camera-h : Real
  camera-h = 600.0

  eye-h : Real
  eye-h = 1.2

  near : Real
  near = 0.4

  fov-deg : Real
  fov-deg = 70.0

  focal : Real
  focal = (camera-w / 2.0) / r-tan (fov-deg / 2.0 * deg)

Section: Focal Pull-In

  min-focal-factor : Real
  min-focal-factor = 0.35

  min-gaze-focal-factor : Real
  min-gaze-focal-factor = 0.61

  focal-for-lean : Real -> Real
  focal-for-lean (lean-frac) = focal * (1.0 - (1.0 - min-focal-factor) * lean-frac * lean-frac)

  focal-for-gaze : Real -> Real
  focal-for-gaze (attention) = focal * (1.0 - (1.0 - min-gaze-focal-factor) * attention)

  cam-focal : Real, Real -> Real
  cam-focal (lean-frac) (attention) =
    let a = focal-for-lean lean-frac
    in let b = focal-for-gaze attention
    in if a < b then a else b

Section: Projection

  ScreenPt = record {
    x : Real,
    y : Real
  }

  project : Vec3, Real, Real -> ScreenPt
  project (p) (cf) (view-w) =
    ScreenPt {
      x = view-w / 2.0 + (p.right / p.forward) * cf,
      y = camera-h / 2.0 - ((p.height - eye-h) / p.forward) * cf
    }
```

And the three components:

    [1] 8 defs — Lens + Focal Pull-In
          camera-w fov-deg focal min-focal-factor min-gaze-focal-factor
          focal-for-lean focal-for-gaze cam-focal
    [2] 3 defs — Lens + Projection
          camera-h eye-h project
    [3] 1 defs — Lens
          near
    section `Lens` spans components 1, 2, 3

The author drew three sections. The calls draw three groups. **They are not the
same three.** `Lens` is in all of them, and `Focal Pull-In` and `Projection`
each turn out to be a *piece* of a group rather than a group.

## Component 3 is the finding

`near` is alone. Nothing in Camera calls it — not `project`, not `focal`, not
`cam-focal`. The chapter declares it, documents it in its opening paragraph
("Owns the lens constants **and the near plane**"), and never reads it.

Four other files read it:

```
port/GuardRail.codex:183     let clipped = clip-near rp.v near
port/Render.codex:945        else ground-clip (clip-near (ground-verts ps 0) near) color cf view-w
port/TruckBody.codex:349     push-poly color (project-all (clip-near ps near) cf view-w 0)
judge/CameraCheck.codex:134  let cl = clip-near poly near
```

Every one of them is handing it to `clip-near`, which is Geom's:

```
Section: Near-Plane Clipping

  clip-cross : Vec3, Vec3, Real -> List Vec3
  clip-cross (a) (b) (near) =
    let f = (near - a.forward) / (b.forward - a.forward)
    in [Vec3 { right = a.right + f * (b.right - a.right), forward = near, height = a.height + f * (b.height - a.height) }]

  clip-near-edge : List Vec3, Real, Integer -> List Vec3
  clip-near-edge (poly) (near) (i) =
    let n = list-length poly
    in if i >= n then []
    else let a = list-at poly i
    in let b = list-at poly ((i + 1) - (((i + 1) / n) * n))
    in let a-in = a.forward >= near
    in let b-in = b.forward >= near
    in let kept = if a-in then [a] else []
    in let crossed = if both-sides a-in b-in then [] else clip-cross a b near
    in kept & crossed & clip-near-edge poly near (i + 1)

  clip-near : List Vec3, Real -> List Vec3
  clip-near (poly) (near) = clip-near-edge poly near 0
```

So `near` is a value that Camera owns, never uses, and that exists in order to
be carried by four unrelated callers into a different chapter. The parameter it
lands in is even called `near`.

**And the two chapters' prose has been arguing about it the whole time.**
Camera's opening says it owns the near plane. Geom's says:

> Pure rider-relative geometry: the coordinate types, the world-to-rider
> transform, the ground curvature, and **near-plane clipping**. No projection —
> that is Camera.

Both paragraphs are careful, both were written by someone thinking about
exactly this boundary, and they disagree. The call graph does not disagree with
either of them; it just declines to route through Camera at all.

The move costs nothing. Every one of the four consumers already cites both
chapters:

```
port/GuardRail.codex       cites Safari chapter Geom   cites Safari chapter Camera
port/Render.codex          cites Safari chapter Geom   cites Safari chapter Camera
port/TruckBody.codex       cites Safari chapter Geom   cites Safari chapter Camera
judge/CameraCheck.codex    cites Safari chapter Geom   cites Safari chapter Camera
```

`near` moves into `Section: Near-Plane Clipping`, beside the three functions
that are the only reason it exists, and not one `cites` line changes.

## Components 1 and 2 are already separated — the file is the last thing holding them together

Look at what `project` takes:

```
  project : Vec3, Real, Real -> ScreenPt
  project (p) (cf) (view-w) =
```

`cf` is the camera focal. It arrives as an **argument**. The projection does
not call `cam-focal`, does not read `focal`, and does not know the lens exists.
Somebody already cut this seam — at the call, where it counts — and then left
both halves in one file.

That is what makes the two components disjoint, and it is worth being precise
about who reads which half, because the answer is different:

```
camera-w      Camera Safari Drive Scene Spike  + 8 checks
fov-deg       Camera
focal         Camera Gaze Render Safari Sky Trig Mountains Rider Drive Scene Spike + 10 checks
cam-focal     Camera Render Safari Sky Mountains CameraCheck
focal-for-*   Camera Safari

camera-h      Camera Sky Mountains
eye-h         Camera
project       Camera Blit CatDraw Critter Geom GuardRail Render Tower Tree TruckBody Scene + 2 checks
ScreenPt      Camera CatDraw Critter GuardRail Mountains Paint Tower Tree TruckBody Scene
```

Two different populations. `Safari` wants the pull-in and never the transform;
`Blit`, `CatDraw`, `Critter`, `Paint`, `Tower`, `Tree` want the transform and
never the lens. The overlap — `Render`, `Sky`, `Mountains` — wants both, and
will cite both, which is what a chapter boundary is *for*.

## The split

```
Chapter: Lens
  cites Safari chapter Trig

 How wide the camera sees. The base focal at the design width, and the two
 narrowings that pull it in. Knows nothing about where a point lands.

Section: The Base Focal
  camera-w, fov-deg, focal

Section: Focal Pull-In
  min-focal-factor, min-gaze-focal-factor,
  focal-for-lean, focal-for-gaze, cam-focal
```

```
Chapter: Screen
  cites Safari chapter Geom

 Where a rider-relative point lands in pixels, given a focal it is handed.
 Owns the eye height and the screen height; owns no lens.

Section: Projection
  camera-h, eye-h, ScreenPt, project
```

```
Chapter: Geom                       (unchanged except for one constant)

Section: Near-Plane Clipping
  near, clip-cross, both-sides, clip-near-edge, clip-near
```

Three chapters, each of which is one job, and each of whose opening paragraph
can be true.

Note what happened to the section headings. `Lens` — the heading that spanned
all three components — does not survive as a section anywhere. It becomes a
*chapter* name for one of the three groups, and the constants it was holding go
to the group that reads them. A heading that spans every component of its
chapter is usually a chapter trying to get out.

## Why this is safe to do now, and was not before

Every oracle safari-codex has is a **value** oracle. Not one of them is a
structure oracle.

- The four arms — bare metal through the seed, the zig plug, the wasm plug, and
  the Rust interpreter — all compile the *same* Codex source and are required
  to print the same bytes. Moving a definition to another chapter changes what
  each arm compiles, identically, and changes nothing any arm prints.
- `gold/<Mod>Gold.codex` is regenerated from the zig probe. It grades *numbers*.
  It has no opinion about which chapter computed them.
- The eye test is a picture.

So a restructure here is checkable rather than hopeful: make the move, run the
sweep, and either every value is identical or it is not. That is a much
stronger position to refactor from than most codebases ever get.

**And Steve's point today is the one that unlocks it.** These chapter
boundaries are not Codex's — they are `wasm/camera.zig`'s and `wasm/geom.zig`'s
file boundaries, carried over by a port that was right to carry them. Once we
start splitting on cohesion we are no longer shaped like the original program,
and we stop being able to measure ourselves against it structurally. The README
has already said the constraint is gone:

> **Fidelity to the Zig original is no longer a constraint.**

This is the first change that takes it at its word. What we keep is everything
that was actually doing work: four arms that must agree with each other, golds
that grade values against the zig's own numbers, and a picture a human looks at.
What we give up is a resemblance nothing was checking.

## What the tool cannot see, and two greps that lied

The intra-chapter graph is the *tractable* half of this question and it is
honest about being half. A definition that calls nothing in its own chapter is
not thereby independent — it may delegate entirely outward. `Geom` reports six
components and is not six jobs; it is a utility bag whose members all lean on
`Trig` and `Num`. Separating "independent" from "leaf that delegates" needs the
cross-chapter graph, which needs cite resolution, which is the phase the Rust
front end has not finished. Until then, a chapter of singletons reads as a
utility bag — which is itself worth knowing.

Two smaller things, both worth writing down because both cost real minutes:

**`grep -w` cannot find a Codex name.** Codex names carry hyphens and `-` is not
a word character, so `grep -w near` matches inside `clip-near`, `near-plane` and
`clip-near-edge`. Every usage table above had to be rebuilt with an explicit
delimiter class.

**And `grep -E '(^|[^-A-Za-z0-9])near'` silently matches nothing** on this
GNU grep — the `^` inside the alternation kills the match rather than erroring.
The form that works is the plain leading-delimiter one, which loses nothing here
because every Codex definition is indented.

Neither of these produced a wrong *answer* — the first produced twenty-eight
files that read `near`, which was obviously too many to be true, and the second
produced zero, which was obviously too few. The dangerous version of this bug is
the one that returns a plausible number. In a language whose prose lives in the
same file as its code, a text search is not a call graph, and that is most of
the argument for building the tool at all.
