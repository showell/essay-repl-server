# What Render would not give up

Render started the day at 111 definitions. It is at 92. Twenty-one came out as
four separate liftings, and the interesting half of this note is the ninety-two
that stayed — because the reason they stayed is not that nobody tried.

The question was: **how much of the safari's renderer is not about the safari?**
The honest answer is about a fifth, it does not come out in one piece, and two
of the four pieces were not in Render's own sections at all.

## What came out

**`Frame` — the route walk and the coordinate change.** Nine definitions: the
chain, the rider pose, the composition, the mappers. It is the piece a different
screensaver keeps whole.

```
  compose-down : List Segment, List Integer, Integer, Real, Real -> AX
  compose-down (segs) (ch) (k) (a) (x) =
    if k <= 0 then AX { a = a, x = x }
    else let seg = list-at segs (list-at ch (k - 1))
    in let p = next-to-cur a x seg.length seg.exit-angle seg.exit-right seg.width
    in compose-down segs ch (k - 1) p.a p.x

  at : List Segment, List Integer, Pose, Integer, Real, Real -> RiderPt
  at (segs) (ch) (pose) (d) (a) (x) =
    let p = compose-down segs ch d a x
    in to-rider p.a p.x pose.along pose.across pose.yaw pose.hw
```

Nothing in those nine mentions a tree, a tower, a cow, a cat, a rail or the
truck. And the four names other chapters already read from Render —
`build-chain`, `at`, `prev-map`, `map-pt` — were all in this half. The export
list and the dominator tree were answering the same question from opposite ends.

**`Billboards` — a sprite placed in the rider's frame, and the two culls.**

```
  verdict : RiderPt, Real, Integer, Boolean -> Placed
  verdict (rp) (h) (cp) (fr) =
    if rp.forward <= near
      then Placed { b = no-billboard, kept = False, size-culled = False }
      else if h / rp.forward * focal < min-critter-px
        then Placed { b = no-billboard, kept = False, size-culled = True }
        else Placed { b = Billboard { right = rp.right, fwd = rp.forward,
                                      height = h, cp = cp, face-right = fr },
                      kept = True, size-culled = False }
```

`verdict` does not know what the sprite is of, and it never did — every emoji
animal in the safari collects to the same `Billboard`, so the rule was written
once for all of them. **The callers differ; the verdict does not.** That is
exactly the shape that lifts.

It carries one detail a re-implementation would lose, so it is worth keeping in
view: a placement records its own verdict rather than being dropped, because the
near-plane cull is *silent* in the zig — it `continue`s without touching a
counter — so a placement can be neither `kept` nor `size-culled`. That third
state has to survive, and a boolean would have eaten it.

**`Ground` — a quad on the floor.** Drop each corner by the curvature at its
distance, clip to the near plane, project, paint. Four definitions, and it does
not know whether it is painting a road, a corner's pavement or a pond.

```
  ground-vert : RiderPt -> Vec3
  ground-vert (p) =
    Vec3 { right = p.right, forward = p.forward,
           height = 0.0 - ground-drop p.right p.forward }
```

Ground quads never enter the depth sort — they are painted first, in walk order,
and everything that stands up is sorted and painted over them. So this is a
pipeline of its own rather than a stage of that one, which is why it detaches
cleanly.

**And two definitions that were simply in the wrong chapter.** Those were not
found by looking at Render at all; they fell out of asking `xref who` where a
name lives.

```
project-all    defined in GuardRail    read by Render, TruckDraw, Ground
ceil-real      defined in Render       ceil x = -floor(-x)
```

`project-all` is `Camera.project` in a loop:

```
  project-all : List Vec3, Real, Real, Integer -> List ScreenPt
  project-all (ps) (cf) (view-w) (i) =
    if i >= list-length ps then []
    else [project (list-at ps i) cf view-w] & project-all ps cf view-w (i + 1)
```

It lived in `GuardRail` because that is where the first caller happened to be.
The consequence is the kind of thing nobody notices from inside: **a rail
chapter was on the cite line of everything in the program that projects a
polygon.** It is beside `project` now. `ceil-real` went to `Num`, where a
rounding identity belongs and where nothing about it is a road.

## What would not come out, and why

### The depth sort is generic in shape and monomorphic in type

This is the one I expected to lift and could not. The sort itself is
scene-independent to look at — a stable merge sort, far to near, with a
carefully argued epsilon:

```
  sort-tie : Real
  sort-tie = 0.00000006

  deeper-than : Real, Real -> Boolean
  deeper-than (x) (y) = x - y > sort-tie * real-max (real-abs y) 1.0

  sort-items : List Item -> List Item
  sort-items (xs) =
    if list-length xs <= 1 then xs
    else merge-items (sort-items (list-take xs (list-length xs / 2)))
                     (sort-items (list-drop xs (list-length xs / 2))) 0 0
```

Then two declarations above it:

```
  Kind =
   | KTree
   | KTower
   | KCow
   | KCat
   | KTruck
   | KRail

  Item = record {
    fwd : Real,
    kind : Kind,
    i : Integer
  }
```

`sort-items : List Item -> List Item`, and `Item` names the six things a safari
contains. A night walk sorting lamp-posts and doorways would need the identical
algorithm and could not call this function.

**The fix is not a move, it is a design change**, and that is the honest reason
it stayed. Either `Item` becomes generic in its payload — which needs a type
parameter this code does not have and which the whole collect-then-merge design
would have to be rewritten around — or `Kind` becomes an `Integer` tag and the
compiler stops checking that a `KRail` index indexes the rail list. The second
is cheaper and worse. `deeper-than` and `sort-tie` are liftable on their own,
but a two-definition chapter holding one comparison is a filing decision
dressed as a design.

So: the sort is a place where **Codex's type system is doing its job and the
cost of that job is a reuse boundary.** I would rather write that down than
paper it over.

### The culls are named for what they cull

```
  min-scenery-px : Real       farm-seg-reach : Integer
  min-critter-px : Real       safari-seg-reach : Integer
  max-vis-trees : Integer     max-vis-towers : Integer
  max-vis-critters : Integer  max-vis-cats : Integer
```

`min-critter-px` went with `Billboards` because `verdict` reads it. The rest
are budgets for a specific bestiary, and the surrounding prose is emphatic
that the two culls are deliberately different and both must stay live. There is
no generic chapter hiding in a list of safari budgets.

### And `collect` is still 67 definitions of safari

The dominator tree has not changed its mind: `collect` owns 67 and
`frame-ground` owns 24, and the two sets remain disjoint. But every one of the
91 is about trees, towers, critters, the crossing cat, the guard rails, the
chased truck, the road strip or the pond. **Render being big is not the same as
Render being confused**, which is the reading TruckDraw earned earlier today —
one exported name owning sixty-four others — and Render is closer to that than
it looked.

## The number, and what it actually means

    Render     111 defs  ->  92 defs
    lifted      21       Frame 9, Billboards 7, Ground 4, ceil-real 1
    rehomed      1       project-all, GuardRail -> Camera

Nineteen percent, in four pieces, none of them large. If the hope was a clean
half, the code said no.

But the reusable set is not really "what came out of Render" — it is what the
tree already sorted itself into. Asking which chapters reach the drawing spine
(`Camera`, `Frame`, `Paint`, `Blit`, `Lens`) partitions the port **22 model to
11 view, with nothing straddling**:

```
MODEL   Cat Truck World Trees Herd Pigs Scenery Pond Rider Gaze Geom
        Camera Lens Frame Num Trig Pose Stills CatStills EmojiStills
        SafariCritter Ground Billboards
VIEW    CatDraw TruckDraw Tree Tower GuardRail Critter Mountains Sky
        Render Safari Blit
```

`Camera`, `Lens`, `Frame`, `Geom`, `Ground`, `Billboards`, `Num`, `Trig`,
`Paint`, `Pose` — that is the reusable set, and it is now ten chapters rather
than a fraction of one big one. The safari lives in the view column, and a
variation replaces that column wholesale.

Which is the answer to the original question, arrived at from the other side:
**not much of Render is non-safari, and that is fine, because Render is the
view.** The parts worth reusing were never going to be a slice of it. They were
the chapters underneath, and the work was getting them out from under.

## The quire, and why it is not today's move

The obvious next thought is that `Camera`, `Lens`, `Frame`, `Geom`, `Trig`,
`Num`, `Paint`, `Pose`, `Ground` and `Billboards` should stop being
`Safari chapter <X>` and become a QUIRE of their own -- a fifth directory
beside `port/`, `judge/`, `gold/` and `poc/`, registered in `harness/bundle.py`
the way those four are, and cited as `Spine chapter Camera` or whatever it ends
up called.

Steve's call, and it is the right one: **not until the night walk exists.**

The argument is the one about abstraction earning its keep on the second user.
Right now there is exactly one user of that set, and every judgement about
where its boundary runs is being made from a single example. Two of today's
five decisions would have been guesses under those conditions and both would
have been wrong in a way that is only visible from outside: `project-all`
looked like a guard-rail function until a third caller appeared, and `Scenery`
exists at all because the call graph proposed a cut the types refused. A quire
drawn now would freeze exactly that quality of judgement into a directory
boundary and a cite prefix, which is a much more expensive thing to move than a
chapter.

The night walk is the second user, and it is the only thing that can say which
of the ten are actually spine and which are safari-shaped by accident. `Frame`
is the obvious suspect -- it still cites `World` for `Segment`, and a route of
straight runs joined by turns is an assumption, not a universal. A city walk
either keeps that assumption or replaces `World` beneath it, and which of those
happens is a fact about a program nobody has written yet.

So the chapters get to be chapters for now. The partition is legible from
`xref` whenever anyone wants to see it, which is most of the value a directory
would have added, and none of the cost.

## One caveat that has not moved

Every seam here is a seam in the CALL graph. `Billboards` and `Ground` are also
clean in the type graph — I checked by hand, which is the admission — but the
tool does not check it, and `Scenery` exists in the World split precisely
because the call graph proposed a cut that the types refused. Until the
dominator tree reads the type references the cross-chapter index already
collects, a proposed cut means "the calls permit this" and a human still has to
ask whether anything else objects.
