# Nature types: the spine

*One sentence per paragraph. It follows "A far tree". Every quote is real code on master. Your three answers set the tone: the kind describes, the place wraps the kind, and the sighting sits between them. Each is a plain design choice, stated once, with no defense and no bragging. C14 applies from here: readable code, and call out only what's new.*

1. **The far tree's code draws whatever tree it's handed, so something has to say which tree, and that's `Conifer`, a kind: it describes a kind of tree and nothing else.**
   (`{{module Conifer}}`, whole: four tags, a height and a color for each, and `scenery_sprite` handing both to the `tree_sprite` the reader just read.)
2. **But a tree in the ride also stands somewhere, so `Geom.Placed(kind)` wraps a kind with its place on the road, and `(kind)` is a type variable: the same wrapper places a cow, a tower or a cat.**
   (`Geom.Placed`. New: a type variable in a type's own head.)
3. **So every thing takes three forms on its way to the screen: placed, sighted and rendered.**
   (A small diagram of the three forms, each edge labelled with the function that makes the next. One plain sentence says this is how Safari Ride is built.)
4. **But a placed thing may not show at all, so sighting answers with a `Try`: the sighting, or why there's none (`BehindCamera`, `BelowHorizon` or `TooSmall`).**
   (`scenery_sighting_of`'s annotation. New: `Try`.)
5. **So the size test needs each kind's height, and a `where` clause asks for it by name: any kind with a `scenery_height` will do.**
   (New: `where`. One sentence on the catch: the match is by name and type alone, so the `scenery_` prefix keeps a match deliberate.)
6. **And rendering asks each kind for its `scenery_sprite` the same way, so one function, `rendering_of`, draws a tree, a cow or a cat, and the `Rendered` it gives back has no kind.**
   (`Pipeline.rendering_of`, five lines.)
7. **So every rendering in a frame goes into one list, and the list is sorted far to near before it's painted.**
   (`Rendered` and its `depth_sorted_renderings`, briefly. This pays off the paint order from "A far tree", now across many things.)
8. **So a kind describes, `Placed` places, and `Pipeline` sights and renders any kind it can ask for a height and a sprite.**

## Notes

- **New Roc ideas:** a type variable in a type's head, `Try`, and `where`. That's three, spread over paragraphs 2, 4 and 5.
- **Scope:** short and meaty. The tag-union alternative gets no section of its own. Paragraph 5 can carry one sentence on why a kind is asked by name, if the draft needs it.
- **Out of scope:** the truck and the rails, which make their own renderings, and the sighting modules that find each kind on the road. Each comes with its own chapter.
- **A picture? Your call.** A thin widget of the four conifers side by side, one of each tag, the way far_tree_widget is built, would show that a `Conifer` is all there is to a tree's look. Or the chapter goes without one.
