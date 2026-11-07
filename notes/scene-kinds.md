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
