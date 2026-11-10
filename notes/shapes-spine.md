# Shapes: the spine

*One sentence per paragraph. The chapter comes after Billboard Critters and before the far tree. Every quote is real code on master: `Shapes.Shape`, `ShapesWidgetApp.green_triangle`, `Shapes.rectangle` and `ShapesWidgetApp.brown_rectangle`.*

1. **A far tree is a box of trunk under eight triangles, so before we draw a tree, we draw its two shapes: a triangle and a rectangle.**
2. **In Roc a shape is a value that describes something to paint, a region of the screen and a fill for it, and the `Shape` type has one tag for each kind of region the ride needs: a `Triangle` for a tree's tiers, a `Quad` for boxes, rails and tower legs, a `Disc` for the lights, and a `Polygon` for traced animals and mountains.** *(This is your "the shape types come from what the app demands", said up front. The include shows the four region tags only; the marks, images and text wait.)*
3. **So here's a triangle, and the code that makes it: a `Triangle` tag whose record names its three corners, so every triangle has exactly three, by construction.**
   *[The triangle widget.]*
4. **Its corners are measured in `Pixels`, a type of its own around an `F64`, so a number on the screen and a number on the road never mix.** *(Roc is just as happy with plain `F64`s, if you prefer that style.)*
5. **But a shape is only a description, so the picture hands the platform a list, the background and then the triangle, and the platform paints it from first to last.**
6. **So next, a rectangle: `Shapes.rectangle` is a function that takes a corner, a width and a height, and gives back a `Quad` whose sides are square to the screen.** *(The first time the book builds a shape with a function, and it sets up the far tree's functions.)*
   *[The rectangle widget.]*
7. **But a quad is any four corners, so the rails and tower legs lean, and the rectangle is the upright one the trunk needs.**
8. **That's both of a far tree's shapes, so next we put them together, with functions of our own.**

## Notes

- **Two new Roc ideas at most per paragraph.** Paragraph 2 carries the tag-union recap, since tags carrying records were taught in Billboard Critters, and the "what the ride needs" framing. Paragraph 6 carries the first function that builds a shape, and a record argument.
- **Paragraph 7 is the one I'd cut first** if the chapter runs long. It keeps a reader from thinking a quad means a rectangle, since the far tree's chapter and later ones draw leaning quads.
- **No step-1,529 counts here.** "Things" already gives them, and they have changed: 868 triangles, 727 quads, 518 polygons and 8 discs. I'll refresh Things' sentence to match.
- **Paint order (paragraph 5)** stays where you approved it, after the first shape is on screen.
