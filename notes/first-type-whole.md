# The book's first type, shown whole

"Numbers at the bottom" shows `Distance` only up to `Distance :: F64.{`, so the reader never sees where the type ends. You asked for the whole syntax.

## What I found

- **No small number type exists.** Every number type in the ride spans 25 to 60 lines, because its functions live inside its `.{ … }`. `Distance` runs 58 lines (from `Distance ::` to the closing `}`), with 17 functions. All of them have the same shape: a signature line, then a one-line body.
- **The two snippets after it stop the same way.** `Billboard` stops at `}.{` and `Sprite` at `).{`. Once the first type has been shown whole, the reader knows what comes after `.{`, so those two can stay as they are.

## Options

1. **Show `Distance` whole, all 58 lines, then a table that reads its parts:** `Distance ::`, `F64`, `.{`, one signature, one body, a `##` comment, `is_eq : _`, and the closing `}`. The length is honest, and every function repeats one pattern. The cost is a long block in a chapter that promises "the functions come later".
2. **Trim `Distance` in the code first, then do 1.** I'd remove any function the ride doesn't call. That's a code cleanup the book has found, like `Point.Point`. It needs a short audit, and I don't yet know how much it removes.
3. **Make a smaller real type the first one.** The only short types in the code are tag unions like `ThrottleLimit := [NoLimit, AtMost(Acceleration)].{ is_eq : _ }`. That would break the section's "numbers at the bottom" order.

**My recommendation is 2, then 1.** Audit `Distance` for functions nothing calls and delete those. Then show what's left whole, with the table. The reader sees one complete type, and the code gets more honest.
