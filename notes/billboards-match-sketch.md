# Sketch: a billboards chapter that teaches tag unions

*A quick sketch for Steve: five paragraphs of chapter prose in the book's voice, plus placeholders for one picture and one diagram. It assumes the reader has read Things (the cow, `Billboard`, `scenery_sprite`) and nothing about shapes or trees.*

---

**[PICTURE: all eight billboard critters standing in a row on the grass by the road, in the ride's own drawing: cow, pig, bull, duck, elephant, giraffe, zebra, rhino. Half face left and half face right.]**

The ride has eight kinds of billboard animal: the cow, the pig and the bull in the herds, the duck on the ponds, and the elephant, giraffe, zebra and rhino at the bends in the road. Each one is the same idea as the cow: a flat emoji, standing on the grass, turned square to the camera. And each one faces left or right. In the code, that's a type with two tags and nothing else:

```roc
Facing : [FacesLeft, FacesRight]
```

A type made of tags is a tag union. A `Facing` is always exactly one of its two tags, and the compiler knows both by name. The billboard's drawing turns each tag into what to do with a `match`:

```roc
flip =
    match billboard.facing {
        FacesLeft => AsDrawn
        FacesRight => Mirrored
    }
```

Each line of a `match` takes one tag and says what it gives back. An emoji is drawn facing left, so `FacesLeft` draws it as it is, and `FacesRight` draws it mirrored. The `match` is complete, and the compiler checks that it is: a `match` on a `Facing` has to handle both tags. That's what "correct by construction" means in practice. A billboard faces one of exactly two ways, and every `match` on it handles both.

A tag can also carry a value. The world plans what lives at each bend in the road, and the plan is one of three things:

```roc
BendLife := [Quiet, Animal(BendAnimal), DuckPond]
BendAnimal := [Elephant, Giraffe, Zebra, Rhino]
```

A bend is quiet, or it has a duck pond, or it has an animal. `Animal` carries which animal, and that's another tag union, of four. So `Animal(Giraffe)` is a whole value: a bend with a giraffe. The route's plans are full of these. Most bends have `Animal(Elephant)`, and one each has a giraffe, a zebra and a rhino.

**[DIAGRAM: a small tree. `BendLife` at the top, with three branches: `Quiet`; `Animal`, which branches into `Elephant`, `Giraffe`, `Zebra` and `Rhino`; and `DuckPond`. The edges are labeled "is one of" and "carries".]**

The `match` that reads a bend's life takes the value back apart. Its `Animal(animal) =>` line matches any animal bend, and names the animal it carries `animal`, ready to use. That's the payoff of a tag union: the shape of the data and the shape of the code that reads it are the same shape. If the ride ever gains a fifth bend animal, say a hippo, then adding `Hippo` to `BendAnimal` is the whole change to the type. The compiler then lists every `match` that has to learn about hippos.

---

## Notes for Steve

- **Every critter is enumerated, in one sentence plus the picture.** The chapter shows two tag unions, not eight emoji. The roster works as the opening's charm: it's the C6 critter category, but standing still.
- **It needs one new widget,** a lineup of the eight billboards, a thin wrapper like the cow widget.
- **The two snippets are close to the real code** (`Billboard.scenery_sprite`, `Segment.BendLife`, `BendAnimal`), but would come in by include, as the book requires, with whatever the shapes redesign renames.
- **The hippo line is a teaser about the compiler,** not a feature proposal.
- **`match` comes before static dispatch, as you wanted.** The chapter calls no function on a value with a dot.
