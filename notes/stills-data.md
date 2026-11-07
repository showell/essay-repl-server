# The stills' data: two small questions

A review of the stills' drawing (Stills, StillShapes, EmojiStills, and the bird and cat data) found that the drawing code reads well, and that the trouble is in the data's types. I decided almost all of it. Two small questions are yours.

## 1. Is there a tracer that rewrites these files?

EmojiStills.roc and CatStills.roc write negatives as `(0.0 - 0.0476)` thousands of times, and colors in decimal (`RgbColor.of(4493595)`). The style guide says a negative is written negative and a color in hex, and BirdStills already does both. I found no generator in the repo and no generated marker, so they look like hand-kept data, and a mechanical rewrite would fix them with every pixel held.

**Is there a tracer outside the repo that will regenerate these files and undo the rewrite?** If not, I'll rewrite them.

## 2. `EmojiStill`'s code point

Each `EmojiStill` carries `codepoint`, which emoji was traced. Production never reads it, and only World's tests do (CowHerd's already compare `still == EmojiStills.bull`).

- **Drop it:** the tests compare against the constant, and the code point stays as a comment beside each emoji.
- **Keep it:** it records which emoji was traced, as data rather than a comment.

I'd drop it, since a field nothing reads is the smell, but you designed `EmojiStill`, so it's your call.

## Decided without you, for the record

- **`Still := List(Still.Polygon)`**, a plain nominal type, in Still.roc. "A still" has been a bare `List(StillPolygon)` passed everywhere, and that's why the member types stutter (`Stills.StillPolygon`).
- **The gradient is a tag**, `[Linear({ stops, start, end }), Radial({ stops, center, axis_u, axis_v })]`, in place of `kind : I64` (1 means linear) and ten two-letter fields, half of them zero in each case.
- **A polygon's fill is one thing:** `[Flat(RgbColor), Shaded(gradient)]`. Today it's a list of gradients that's never longer than one, beside a color that means nothing when there's a gradient.
- **`Stills.is_drawable` goes.** It was a test-only copy of Polygon's crash rules. The data tests draw every still through the real path instead, so Polygon judges.
- **Stills.roc's ~25 expects that restate record literals go,** StillShapes' three helpers go private, the still's frame ("feet at y 0, y up, height 1") is described in one place, and `StillPt` becomes `Point`.
- **The walk now counts the widgets.** Without it, the review would have made two functions private that the stills widget uses. Every review now walks with the widgets as clients.

Pixels hold throughout. This lane runs after the Polygon lane, which converts the same gradient stops.
