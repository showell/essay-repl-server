# Cow → Billboards → Far tree: five pros, five cons

*For Steve, before you finalize today's direction. I checked the code first: the `match` on `Facing` (Billboard.roc:54) and `BendLife := [Quiet, Animal(BendAnimal), DuckPond]` (Segment.roc:57) are both real, so the billboards sketch quotes code that exists.*

## The pros

1. **One new Roc idea per chapter, each on something the reader already knows.** Things teaches records, the first function body and an `if`. Billboards adds tag unions and `match`. The far tree adds a real function: local names, `map` and paint order. Each step is small, and each lands on a cow, a giraffe or a tree, never on machinery (A0).

2. **`match` comes before static dispatch, as you wanted.** Tag unions are the most direct way to show the mission's theme early: types that leave a wrong state nowhere to live. A `Facing` is one of two tags, and every `match` on it has to handle both. That's "correct by construction" in four lines, in chapter 6 instead of chapter 15.

3. **Billboards pays a promise from Things quickly.** Things shows `scenery_sprite` as an annotation alone and says its `match` comes later. Under this order, "later" is the next chapter (C12). The reader also still has `Billboard` and `Species` fresh in mind, so the new chapter adds the tags and nothing else.

4. **The charm comes early, and it's cheap.** Eight critters in a row on the grass is a thin wrapper around the ride's own billboards, much like the cow widget (H0). It's the most delightful picture we can make with the least new code, and it keeps a reader who just met the cow turning pages.

5. **The far tree is now the cleanest functions chapter in the book.** A far tree never moves. It's a rectangle and eight triangles, and since the shapes redesign it reads as exactly that: `Triangle` and `Rectangle` tags on typed points. Giving trees one chapter keeps the book short, and it frees every other Roc idea to land on some other thing.

## The cons

1. **MISSION has to change, and only you can change it.** Section 3's order of the pass still lists Nature types and A simple tree before Stills and Herds, and C6 says nature, then man-made, then critters. This order puts critters first. The fix is two edits to MISSION, but they need your approval ("Change it only when he does").

2. **Things' close becomes an orphan.** It ends: "A sprite is shapes, so shapes come next: a triangle and a rectangle. Then we build things from them, starting with a tree." Under this order, billboards come next instead, so the close needs a rewrite before the billboards chapter starts. That's small, but it's exactly the kind of stale sentence we keep missing after restructures.

3. **`BendLife` leans on the world's plans.** The sketch's second tag union comes from the route's bends. The pieces chapter shows `World.last_plan` and the route map, so the reader has seen plans, but not a bend's life in detail (C3). The chapter has to introduce a bend in a sentence or two before its type, or use a different example that carries a value.

4. **The first triangle arrives later.** The reader sees a cow drawn in chapter 5, but doesn't see how anything is drawn until the far tree, two chapters on. A reader who wants to know "how does a picture get made" waits longer. Billboards softens this a little, since its `match` picks a mirrored or as-drawn emoji, but the shapes themselves wait.

5. **Trees lose their "honest cheat" story.** MISSION A0 names it outright: "the news is that the ride draws two versions of a tree, and why." With one far-tree chapter, that news shrinks to the "what you're missing" paragraph. The honest-cheats axis needs another home, or A0's example changes. Folding Shapes into the far tree is also still open, and a folded chapter could run long.

## My recommendation

Approve it. Every con has a small, known fix. Cons 1 and 2 are a MISSION edit and a rewritten close, which I'd do first thing. Con 3 gets settled in the billboards chapter's why questions. Cons 4 and 5 wait for the far-tree chapter, where you decide whether Shapes folds in. The trunk refactor runs alongside the billboards chapter and finishes before the far tree's draft.
