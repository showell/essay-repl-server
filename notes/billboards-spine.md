# Billboards: the spine

*One sentence per paragraph. Every quote is real code: `Billboard.Facing`, `Billboard.scenery_sprite`, `BendAnimal` with `species_of`, `Segment.BendLife` and `Segment.bend_billboards`.*

1. **The ride's billboard animals have faces, so each one faces left or right, and at a bend the animal and its baby face the way the road turns, which draws the rider's eyes into the turn.**
   *[Picture: the eight billboard animals in a row on the grass: cow, bull, pig, duck, elephant, giraffe, zebra, rhino.]*
2. **So `Facing` is a type with two tags, `FacesLeft` and `FacesRight`, and a type made of tags is a tag union.**
3. **But every emoji is drawn facing left, so `scenery_sprite` uses a `match` to turn each tag into how to draw the still, as drawn or mirrored, and the compiler checks that the `match` handles both.** *(This pays Things' promise: here is the body whose annotation Things showed alone.)*
4. **So the four bend animals are a tag union too, and `species_of` matches each one to its record: an emoji and a height, like the cow's.**
5. **But a bend has room for one thing at most, so a bend's life is `Quiet`, `DuckPond` or `Animal(BendAnimal)`, and that last tag carries a value.**
   *[Diagram: `BendLife` with its three tags; `Animal` carries one of `Elephant`, `Giraffe`, `Zebra` and `Rhino`. Edges: "is one of", "carries".]*
6. **So `bend_billboards` takes a bend's life apart with a `match`, and its `Animal(animal)` line names the animal it carries, ready to use: the code has the same shape as the type.**
7. **So the route's plans read like a list of sights, `Animal(Elephant)` bend after bend, and that's on purpose: elephants are the fixture, so a giraffe, a zebra or a rhino is a surprise.**
8. **A tag union says everything a value can be, and a `match` handles every case, so next we put functions to work drawing a thing of our own from shapes: a tree far off.**

## Notes

- **Two new Roc ideas:** the tag union, and `match`, including a tag that carries a value. `:=` and the dot call already came up in "The pieces as types" and Things, and they're read plainly here.
- **The first `match`, in paragraph 3,** is the one from Things' promise. `species_of` in paragraph 4 is the simplest one in the code: a tag in, a record out.
- **Paragraph 7 has no count.** A number like "14 of 18 bends" would need an expect behind it (B2). I'd rather say "most bends" than add a test just for the prose. Tell me if you want the number.
- **The widget is new:** the lineup of eight, a thin wrapper like the cow widget.
- **The close hands off to the far tree.** If Shapes survives as its own chapter, the close names shapes instead.
