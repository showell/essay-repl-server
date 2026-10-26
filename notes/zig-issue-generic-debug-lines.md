# Draft: a Zig issue with its fix, for Steve to file on Codeberg

*Found by CC while porting our line-coverage tool; reproduced on the box
with 0.17.0 and with master `0.18.0-dev.610+720939f8c` (2026-10-25); the
cause found in Sema. **The fix is not yet built and tested here**: that
runs after today's KVM judge, and this line goes when it has.*

---

**Title:** Sema: `zirFunc` reads `SrcLocs` from the wrong offset when the return type is generic, giving bogus debug line info

**Zig version:** 0.17.0 and master `0.18.0-dev.610+720939f8c`, x86_64-linux, self-hosted x86_64 backend and `-fllvm`.

**Repro** (`r2.zig`, 11 lines):

```zig
const std = @import("std");

pub fn pick(r: std.Random, comptime weights: anytype) std.meta.FieldEnum(@TypeOf(weights)) {
    _ = r;
    return @enumFromInt(0);
}

test "pick" {
    var prng: std.Random.DefaultPrng = .init(1);
    _ = pick(prng.random(), .{ .a = 3, .b = 1 });
}
```

```sh
zig test r2.zig --test-no-exec -femit-bin=bin
readelf --debug-dump=decodedline bin | awk '$1=="r2.zig"'
```

**Actual:** `pick`'s rows are at lines 24, 5, 25 (self-hosted) and 24, 5
(`-fllvm`), past the end of the file. **Expected:** 3, 5, 6.

A smaller one, no `std`:

```zig
pub fn pick(x: anytype) @TypeOf(x) {
    return x;
}

test "pick" {
    _ = pick(@as(u32, 3));
}
```

gives 9, 2, 10 in a 7-line file.

**Cause:** in `src/Sema.zig` `zirFunc`, when `ret_ty.is_generic` is set
the return type's trailing data (one `Ref`, or a body of `body_len`
instructions) is not skipped, so `extra_index` stays short by
`ret_ty.body_len`, and `src_locs` is read from the last words of the
function body. `lbrace_line`/`rbrace_line` become two consecutive
instruction indices (hence 21/22 above, after the decl line). That fits
what is seen: the bogus lines move with the declaration but not with the
body's length, are always one apart, both backends agree, and a function
whose return type does not name a parameter is fine. `zirFuncFancy` skips
the return type before checking `ret_ty_is_generic`, and
`Zir.getAssociatedSrcHash` adds `ret_ty.body_len` unconditionally; only
`zirFunc` misses it.

**Fix:**

```diff
--- a/src/Sema.zig
+++ b/src/Sema.zig
@@ fn zirFunc(
     var extra_index = extra.end;
 
-    const ret_ty: Type = if (extra.data.ret_ty.is_generic)
-        .generic_poison
-    else switch (extra.data.ret_ty.body_len) {
+    const ret_ty: Type = if (extra.data.ret_ty.is_generic) blk: {
+        // Skip the return type's trailing `Ref` or body, or `src_locs` below is read from the body.
+        extra_index += extra.data.ret_ty.body_len;
+        break :blk .generic_poison;
+    } else switch (extra.data.ret_ty.body_len) {
         0 => .void,
```

(`body_len` 0 has no trailing data, 1 is one `Ref`, more is that many
instructions, so adding `body_len` covers all three.)

The line numbers themselves are fine: AstGen records them correctly
(relative to the declaration, so moving a function does not change its
ZIR), and the body's `dbg_stmt` rows come out right. Only the read of the
`Func` payload is off.

**A sturdier fix:** the `Func` payload's layout is walked by hand in
several places: `Zir.getFnInfo` (correct, but it stops after the body),
`Sema.zirFunc` (this bug), `Sema.zirFuncFancy` and
`Zir.getAssociatedSrcHash`. If `getFnInfo` also returned `src_locs` (and
the proto hash), and those three used it, the layout would be decoded in
one place and this kind of bug could not recur in a second reader.

**Impact:** `addr2line`, coverage and other line-table tools either drop
these rows or index past the end of the source.
