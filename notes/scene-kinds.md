# The scene keeps its kinds too long

You called it a smell when every walk of the scene dragged in each kind's internals. A cold agent traced it. You were right: it is a real smell, if a mild one. One question for you is at the end.

## The cause

`Scene` has seven fields, one per kind of thing in view:

```roc
Scene := { trees : List(Sighted(Conifer)), towers : List(Sighted(Tower)), billboards : ...,
           cats : ..., birds : ..., truck : TruckFate, rails : List(RailQuad) }
```

Each field names a kind. Each kind's block then names its internals: `Billboard.adult_billboard` names Species, Species names `EmojiStill`, and that names `StillPolygon`. The poses, Tower's corners and the rest come in the same way. Those members exist for the makers (the herds, Wildlife, Pond) and the widgets, not for the scene.

The scene never touches a kind's insides. The only thing it does with a kind is hand it to `Pipeline.rendering_of`, after which every kind is one `Rendered`. Production never reads a Scene except to render it at once. Only the gate's per-kind counts and the frame widget's layer filter read the fields one by one.

So the scene keeps every kind typed one step past the last place a kind matters. `Rendered` already erases the kind, and its own doc says so: everything meets in one list because nothing says what sort it is. The scene just stops one step short of it.

A new kind today edits Scene's field, `scene_in_view`, SceneShapes' list, a test fixture, the gate's `empty_scene`, a count and a sum, and the widget's filter.

(Speed and Clock in the walk are not part of the smell. They're the scene's real input: the cat reads the speed, and the tower's beacon reads the clock.)

## The options

**(A) The scene holds rendered things, each tagged with the sighting that found it.** My recommendation.

```roc
SceneSource : [Tree, Bird, Tower, Billboard, Cat, Truck, Rail]
SceneThing : { source : SceneSource, rendering : Rendered }
## In tie order: trees before birds, so a perched bird is drawn over its tree.
Scene :: List(SceneThing).{
    scene_in_view : CameraView, RideFacts -> Scene
    scene_renderings : Scene -> List(Rendered)
    scene_from : Scene, List(SceneSource) -> Scene     # for the frame widget's layers
}
```

- **The walk** then shows Rendered, Picture, Distance, RideFacts, LitTruck, Speed and Clock, and no kind's internals.
- **The tie order** lives in `scene_in_view`, so the perch rule keeps one home. The scene is opaque because its order is a rule.
- **SceneShapes** shrinks to a sort and a join, or folds into Scene.
- **The gate** counts each source against its sighting module, so a dropped kind still fails by name.
- **The frame widget** gets one exhaustive match from source to layer.
- **A new kind** afterwards: one sighting call, one tag, one widget arm, and one count.
- **Pixels** hold.

The catch is that `SceneSource` lists every kind, which looks like the parallel hierarchy you had removed (`DepthSort.Subject`). The difference is that its tags carry no payload, so it names no kind's type. A new tag is a compile error at the widget's match, which forces the decision.

**(B) Keep the seven fields, but make Scene opaque and let it render.** The widget and the gates stop naming fields, but the walk still names every kind. It costs as much as (A) and gains less.

**(C) A tag union of the sighted kinds,** such as `[Tree(Sighted(Conifer)), ...]`. That's exactly the old parallel hierarchy, and its closure is today's. Rejected.

Making the kinds opaque doesn't help either. The members that pull in the internals stay public, because the makers and widgets need them.

## Your call

Is (A)'s payload-free `SceneSource` all right, given the parallel hierarchy it resembles? If yes, it runs after the World split and the FrameView lane, which touch the same code.

The agent also suggests a new entry for the smells guide: "A collection keeps its kinds past their last use. Erase the kind where the last step that needs it runs." I'll add it whichever way you decide.

## Steve's answer, and the decision (2026-11-07)

Steve: "I kinda lean toward B if it avoids the parallel hierarchy. I don't care how much it costs to change if it's better. You decide."

**Decided: B, with the kinds erased inside it.** Scene keeps one named field per source, so there's no separate list of kinds and no enum. Each field holds what that source rendered, not the kind's type:

```roc
Scene :: {
    trees : List(Rendered), birds : List(Rendered), towers : List(Rendered),
    billboards : List(Rendered), cats : List(Rendered),
    truck : Try(Rendered, [..why there's no truck..]), rails : List(Rendered),
}.{
    scene_in_view : CameraView, RideFacts -> Scene     # sights and renders; it has the view
    scene_renderings : Scene -> List(Rendered)         # joined in tie order, then depth-sorted
}
```

- **No parallel hierarchy.** The fields are the only list of sources. The frame widget maps its layers to fields, as it does today, and the gate counts each field against its sighting.
- **The smell goes.** The kind is erased in `scene_in_view`, the last step that needs it, so walking Scene shows Rendered and RideFacts and no kind's internals.
- **The tie order** is the order `scene_renderings` joins the fields: trees before birds, the perch rule's one home.
- **SceneShapes** folds into Scene or shrinks to the join.

This runs after the World split and the FrameView lane. The smells guide gets the new entry: "A collection keeps its kinds past their last use."
