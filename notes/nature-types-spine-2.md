# Nature types: the spine, second version

*Why a second version: the first repeated "The pieces as types", which already teaches `Geom.Placed` and its type variable, `Pipeline.Sighted`, the refusal tags, and `Rendered` with its one sorted list. The truth-and-order reader caught it, and I should have re-read chapter 4 first. This version teaches only what's new: the kind itself, and how one pipeline asks any kind for what it needs.*

1. **"The pieces as types" followed a thing through three forms with its kind inside, so this chapter opens a kind: a `Conifer` describes a kind of tree, nothing more.**
   (`{{module Conifer}}` whole, then the four-conifer picture.)
2. **But the pipeline that sights and renders every thing is the same code for every kind, so it must ask each kind for what it needs without knowing which kind it holds.**
   (One plain sentence on the design choice. Name the five kinds that go through: trees, critters, towers, cats and birds.)
3. **So `rendering_of` asks for the kind's sprite with a `where` clause: any kind with a `scenery_sprite` of that type will do.**
   (`Pipeline.rendering_of`, five lines. New: `where`. One clause glosses `Sprite.LensAndLight` as the lens and the light.)
4. **And sighting asks for the kind's height the same way, to test whether its top shows over the horizon and whether it stands tall enough to draw, and it answers with a `Try`.**
   (`scenery_sighting_of`'s annotation. New: `Try`, by name: chapter 4 showed the refusal tags but not the type that carries them. Truthfully: the ride's callers keep only the `Ok`s.)
5. **Roc matches a `where` by name and type alone, so the names say what they're for: `scenery_height` and `scenery_sprite`.**
   (Two sentences, here rather than in paragraph 3, so no paragraph carries two new ideas.)
6. **So a kind meets the pipeline by having two functions, and `Conifer` is one such kind among five.**

## For you

- **The title.** The chapter is now about kinds and how the pipeline asks them, not "nature" in general. "Nature types" still fits loosely, since the tree is the example. "Kinds" fits exactly. Your call.
- **Shorter:** six paragraphs, and two new Roc ideas (`where`, `Try`). The diagram goes, since chapter 4's three forms already did that job.
