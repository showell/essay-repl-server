# The pipeline gets its own chapter

*You asked for the pipeline to have a chapter of its own, so that "Asking a kind" reaches `where` with a clear mind. Below are the order I recommend, a spine for the new chapter, and the new opening spine for "Asking a kind". One call for you: the order.*

## The order: the pipeline before Nature types

| # | Chapter | What it's about |
|---|---|---|
| 8 | A far tree | (passed) |
| **9** | **The pipeline** | **new:** a thing's trip to the screen, through three types |
| 10 | Nature types | (passed) one kind, `Conifer`, a nominal type |
| 11 | Asking a kind | `where`, and nothing else new |

I recommend putting the pipeline **before** Nature types, not between Nature types and Asking a kind:

- "Nature types" already opens by explaining the three forms and naming the pipeline, in a few sentences, before it gets to `Conifer`. With the pipeline chapter first, that opening shrinks to one sentence pointing back, and the chapter is only about `Conifer`.
- **The run reads in a line:** the trip, then what rides on it (a kind), then how the trip asks the kind for things (`where`).
- The pipeline chapter needs a kind in its types, and the far tree is fresh, so `Geom.Placed(Conifer)` is its example. It says only "a `Conifer` is the tree's kind; the next chapter looks inside it."

The other order (Nature types, then the pipeline, then Asking a kind) leaves Nature types as it is, but its opening would then preview a chapter that comes after it.

## The pipeline: the spine

One sentence per paragraph.

1. **The trip.** Every thing beside the road takes the same trip to the screen each frame, and the `Pipeline` module carries it, so we call it the pipeline. *(picture: the real frame at step 1,529, with its trees, critters, tower and truck)*
2. **The diagram.** So here's the trip in one diagram: placed, sighted, rendered, then sorted and painted, with the function that does each move on its edge.
3. **Placed.** The trip starts from a `Geom.Placed(kind)`: where on the road a thing stands, how far off the ground, and its kind. *(the type, whole: three fields)*
4. **Sighted.** But the screen shows what the camera sees, so sighting turns a place on the road into a `Pipeline.Sighted(kind)`: a spot in the camera's view, carrying the same kind. *(the type, whole: two fields)*
5. **Refusals.** But not everything placed is in view, so a sighting is a `Try`, and its refusals are tags that say why: `BehindCamera`, `BelowHorizon` or `TooSmall`. *(a table from step 1,529, of real sightings and what each one decides, pinned by an expect; the old draft has one, which I'd re-check and re-pin)*
6. **Rendered.** So each sighting that passes is rendered as a `Rendered`: its sprite and its depth, and the kind is gone. *(the type, with its accessors elided)*
7. **One list.** Every rendering has that one type, so the frame puts them all in one list, and `Rendered.depth_sorted_renderings` orders it far to near, so near things paint over far ones. *(the scene's gathering, elided to a few lines)*
8. **The close.** So a kind rides through the first two types and leaves at the third. That raises the next chapters' question: what is a kind, and how does one pipeline get a sprite out of every kind?

**New in this chapter:** three types, and `Try` with refusal tags. The animation ideas are the camera's view, the depth and paint order, all named in "The problem" and "The pieces as types". I'd keep the functions to their annotations, each move on the diagram's edges, with no bodies. The bodies of `scenery_sighting_of` and `rendering_of` carry `where`, which waits.

## Asking a kind: the new opening

The `Rendered` type and the trip leave this chapter, so its opening thins to one line of thought:

1. One function, `Pipeline.rendering_of`, renders every kind of thing beside the road. *(the five-kinds picture)*
2. It can because of the `where` clause, which constrains a type variable to types that have certain methods.
3. A `Sighted(kind)` goes in and a `Rendered` comes out, as "The pipeline" showed, and only the kind has its sprite, so `rendering_of` calls the kind's own `scenery_sprite`.
4. But `kind` is a type variable, so it could be any type, and only some types have a `scenery_sprite`. So `rendering_of` needs a constraint. *(then the code, the table, and the rest as it stands)*

## For you

The order: the pipeline **before** Nature types (my recommendation), or between Nature types and Asking a kind?
