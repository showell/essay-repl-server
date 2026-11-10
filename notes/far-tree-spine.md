# A far tree: the spine

*One sentence per paragraph. It follows Shapes. Every quote is real code on master (5507b433). The tiers are now a map over their hand-tuned widths, frozen by an `expect`, and no pixel moved.*

1. **A far tree is a trunk under eight triangles, so this chapter builds one from small functions: the tiers, a triangle for each tier, the trunk, and the order they're painted in.**
   *[Picture: one far tree, tall in the frame. The tree widget may already do this; I'll check it before drafting.]*
2. **The tiers start as a list of eight widths, chosen by eye, and `map` turns each plain number into a `Fraction`.** (`tier_widths`: a list of floats, and the first `map`.)
3. **But each tier also needs a top and a bottom, so `map_with_index` builds the eight tiers from the widths, stepping each one a tenth of the crown lower than the one above.** (`tiers`: a list made by a function from a list.)
4. **So the tiers are values we can freeze: an `expect` states all eight exactly, and the tests check it on every run.** (The book's first `expect`, as you suggested: the map works out concrete numbers, and the test pins them.)
5. **So each tier becomes a triangle: `tier_triangle` takes the tree's outline on the screen and one tier, names the numbers it works out along the way, and gives back a `Triangle`.** (A function body with local names.)
6. **But the trunk is painted first, so `tree_sprite`'s last line puts the trunk at the front of the list, then the tiers top to bottom, and each wider tier covers the bottom of the one above.** (Paint order, and `map` over the tiers once more. `trunk_shape` is shown by its annotation alone: its body is the `Shapes.rectangle` call from the last chapter.)
7. **But a near tree draws more, and here's what you're missing: within 200 metres its tiers are shaded cones and its trunk looks round, and the ride spends that detail only where it shows.** (One paragraph; the switch is for speed. "A near tree" is framed as later, or simply as what the ride does.)
8. **So a far tree is a handful of small functions over a list, each one easy to check, and the tree beside the road is the same code handed a nearer spot.**

## Notes

- **New Roc ideas:** `map`, `map_with_index`, `expect`, a function body with local names, and `concat`. That's spread across paragraphs 2–6, two at most per paragraph.
- **Paragraph 6's `tree_sprite`** also mentions the crown choice (`crown_of`). I'll show its annotation and its last line only, so the cones stay in paragraph 7.
- **The close** says what the reader has, and leaves the next chapter open, since the order after the far tree isn't settled.
