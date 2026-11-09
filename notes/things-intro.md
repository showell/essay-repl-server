# Opening the Things part

You're right that the jump is abrupt. Chapter 3 ends looking at the whole program from a great height, and the next page is a `Poly` with a list of coordinates. Two things are missing in between. The reader needs to know what a thing is in this program before they care how its shapes are built. And the reader needs to see the part's shape: which things we'll draw, in what order, and why shapes come first.

Here are three ways to open the part, then my recommendation, then a reworked last paragraph for chapter 3.

## One fact that shapes every option

Every kind of thing beside the road draws itself the same way. `Conifer`, `Billboard`, `Cat`, `Bird` and `Tower` each have a function called `scenery_sprite`, and they all have the same shape of type:

```
scenery_sprite : Billboard, Sprite.Setting({}) -> Sprite
```

A `Sprite.Setting` is the record a thing draws from: its `spot` (where it stands in the frame), the lens's `focal_length`, and a `context` for whatever else that kind needs. The truck is the exception, with its own `truck_sprite`.

There's a wrinkle here. The spot comes from the rider's view, which is piece 3, so drawing a thing already leans on piece 3. The code has an honest answer, though. `Spot.at` lets you build a spot by hand, "to draw from a foot it chooses", and every widget that shows one thing alone does exactly that. So in the Things part, we draw each thing standing where we put it. The rider's camera puts it there for real in part 3. That's a clean promise, and it's easy to pay.

## Way 1: one contract, many kinds

A short opening chapter, "Things", that's top-down (C1):

1. **Open on a cow.** A cow standing on the grass by the road, seen from an angle (H0). One picture.
2. **The contract.** Every kind answers the same question: given where it stands and the lens, what's its sprite? Show the one-line type above, and the `Sprite.Setting` record. That's two small includes, and both are types, which continues chapter 3's theme.
3. **The roster, in the order the part takes them:** nature (trees and grass), then man-made (the road, the rails and the towers), then critters standing still (the cow, the elephant). One sentence each. This is C6's order made visible.
4. **The way in.** Every sprite is a list of shapes. So before any kind, we learn the shapes, and the simplest one is a triangle.

- **For it:** it pays chapter 3's "each one's functions come in its own chapters" right away, by showing the one function every kind shares. It's also the forest before the trees.
- **Against it:** step 2 is abstract. The reader sees a contract before they've seen anything fulfil it.

## Way 2: a gallery first

Open the part with pictures and almost no code: a tree, a cow, a tower and the truck, each drawn alone where we put it, with one sentence each on what it's made of ("a far tree is a trunk under eight triangles"). Then "every one of these is a list of shapes, so we start with shapes."

- **For it:** it's concrete, warm and fast. It tells the reader what they're about to build.
- **Against it:**
  - We don't have this widget. The tree, truck and stills widgets each show one sort, not a gallery side by side. A gallery is new widget code, a thin wrapper by H0's rule, but still work.
  - It also skips the contract, which is the most teachable idea in the part.

## Way 3: walk one thing all the way down

Pick one thing, the far tree, and follow it top to bottom: the `Conifer` kind, its `scenery_sprite`, the sprite, and the triangles. Then come back up for the others.

- **For it:** C5, finish one thing before the next.
- **Against it:** it puts a tree's whole story ahead of the shapes it's made of. That's the "Simple tree" chapter arriving early, and it would have to stop at "and these are triangles, which we'll explain".

## My recommendation

**Way 1, with Way 2's opening picture.** A short chapter, "Things", about the length of "The problem":

- **the cow picture:** one widget, and it needs H0's cow on the grass;
- **the contract:** the `scenery_sprite` type and the `Sprite.Setting` record;
- **one line on the spot:** we place each thing ourselves for now, and the camera places it in part 3;
- **the roster in C6's order;**
- **then "every sprite is a list of shapes, so we start there."**

The Shapes chapter then starts with its own first sentence unchanged, because the reader already knows why they're looking at polygons.

The cost is one new widget (or a `frame` widget address that shows only the critters), and one short chapter.

**One open question for you:** do the sun, the sky and the mountains belong to Things? They're drawn, but they aren't things beside the road. They have no `scenery_sprite`, and they sit in the backdrop or the skyline. I'd treat them as the backdrop, a short section late in the part, framed as "the things that stay put behind everything else".

## The last paragraph of chapter 3, reworked

With a Things chapter in between, chapter 3 no longer has to land on the triangle. It only has to hand off to things:

> That's five pieces, and the types that answer them. The book builds the pieces in order, and each piece's functions come in its own part. So we start with things: what a tree, a cow or a tower is in the code, and how each one becomes a sprite.

The "2,121 shapes, all but eight polygons, and the simplest is a triangle" line moves to the end of the Things chapter, where the reader is one step from Shapes.
