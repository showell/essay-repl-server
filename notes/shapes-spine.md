# Shapes: the spine

*One sentence per paragraph. The chapter comes after Billboard Critters and before the far tree. Every quote is real code on master.*

1. **A far tree is a box of trunk under eight triangles, so before we draw a tree, we draw its two shapes: a triangle and a rectangle.**
2. **In Roc a shape is a value that describes a region of the screen and a fill for it, and the `Shape` type has one tag for each kind of region the ride needs: `Triangle`, `Quad`, `Disc` and `Polygon`.**
3. **So here's a triangle, and the code that makes it: a `Triangle` whose record names its three corners, so every triangle has exactly three.**
   *[The triangle widget.]*
4. **Its corners are measured in `Pixels`, a type of its own, so a number on the screen and a number on the road never mix.**
5. **But a shape only describes, so the picture hands the platform a list, the background and then the triangle, and the platform paints it first to last.**
6. **So next, a rectangle: `Shapes.rectangle` is a function that takes a corner, a width and a height, and gives back a `Quad` whose sides are square to the screen.**
   *[The rectangle widget.]*
7. **That's both of a far tree's shapes, so next we put them together, with functions of our own.**

## Notes

- **Cut:** the leaning quads, and the list of what each tag draws. Paragraph 2 names the four tags and says they come from what the ride needs, and nothing more.
- **Things' shape counts** get refreshed to the new tags: 868 triangles, 727 quads, 518 polygons and 8 discs.
