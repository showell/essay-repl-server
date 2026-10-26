# Draft: a Zig issue with its fix, for Steve to file on Codeberg

*Found by CC while porting our line-coverage tool; reproduced on the box
with 0.17.0 and with master `0.18.0-dev.610+720939f8c` (2026-10-25); the
cause found in Sema. The fix is the structural one (one decoder of a
function's ZIR payload), built and tested here; attach
[zig-fnpayload.patch](zig-fnpayload.patch) or paste it as a PR.*

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
instructions) is not skipped:

```zig
const ret_ty: Type = if (extra.data.ret_ty.is_generic)
    .generic_poison
else switch (extra.data.ret_ty.body_len) {
    1 => blk: { ...; extra_index += 1; ... },
    else => blk: { ...; extra_index += ret_ty_body.len; ... },
    ...
};
...
extra_index += extra.data.body_len;
src_locs = sema.code.extraData(Zir.Inst.Func.SrcLocs, extra_index).data;
```

so `src_locs` is read `ret_ty.body_len` words early, from the end of the
function body, and `lbrace_line`/`rbrace_line` are two consecutive
instruction indices (21/22 above, after the decl line). That fits what is
seen: the bogus lines move with the declaration but not with the body's
length, are always one apart, both backends agree, and a function whose
return type does not name a parameter is fine.

The line numbers themselves are fine: AstGen records them correctly
(relative to the declaration, so moving a function does not change its
ZIR), and the body's `dbg_stmt` rows come out right. Only the read of the
`Func` payload is off.

**Why it could happen:** the trailing data of `func`/`func_inferred`
(`Inst.Func`) and `func_fancy` (`Inst.FuncFancy`) is walked by hand in six
places, each with its own `extra_index` arithmetic: `Zir.getFnInfo`,
`Zir.getAssociatedSrcHash`, `Zir.findTrackableInner`, `Sema.zirFunc`,
`Sema.zirFuncFancy`, and `print_zir`'s `writeFunc`/`writeFuncFancy`. Five
get it right; `zirFunc` skips a step on one branch.

**Fix: decode the payload in one place.** A new `Zir.getFnPayload` walks
either layout once and returns every part of it:

```zig
pub const FnPayload = struct {
    param_block: Inst.Index,
    cc_ref: Inst.Ref, // .none when cc_body is used or the convention is omitted
    cc_body: []const Inst.Index,
    ret_ty_ref: Inst.Ref, // .void_type when omitted; .none when ret_ty_body is used
    ret_ty_body: []const Inst.Index,
    ret_ty_is_generic: bool,
    is_inferred_error: bool,
    is_var_args: bool,
    is_noinline: bool,
    noalias_bits: u32,
    body: []const Inst.Index, // empty for a prototype
    src_locs: ?Inst.Func.SrcLocs, // present exactly when body is not empty
    proto_hash: ?std.zig.SrcHash, // likewise
};
```

and all six readers use it; none keeps an `extra_index` of its own. In
`zirFunc` the return type and the brace lines become:

```zig
const payload = sema.code.getFnPayload(inst);
...
const ret_ty: Type = if (payload.ret_ty_is_generic)
    .generic_poison
else if (payload.ret_ty_body.len != 0) blk: {
    const ret_ty_val = try sema.resolveGenericBody(block, ret_ty_src, payload.ret_ty_body, inst, .type, .{ .simple = .fn_ret_ty });
    break :blk ret_ty_val.toType();
} else if (payload.ret_ty_ref == .void_type)
    .void
else
    try sema.resolveType(block, ret_ty_src, payload.ret_ty_ref);

const has_body = payload.body.len != 0;
const src_locs = payload.src_locs orelse undefined;
```

`getAssociatedSrcHash`'s two hand-walks become `return
zir.getFnPayload(inst).proto_hash`, `findTrackableInner`'s two branches
become one, and `print_zir`'s two writers become one. Net: +169 / -328
lines over `lib/std/zig/Zir.zig`, `src/Sema.zig` and `src/print_zir.zig`;
the whole diff, against master `720939f8c`:
[zig-fnpayload.patch](zig-fnpayload.patch).

One visible change: `print_zir` now prints an omitted return type as
`void_type` for `func_fancy` too, as it already did for `func`. Nothing
compares printed ZIR.

**Tested** with a Debug build of the patched compiler (no LLVM): the repro
gives 3, 5, 6, the `anytype` one 1, 2, 3, and a function moved down or
given a longer body moves its rows with it; `zig test test/behavior.zig
-fno-llvm -fno-lld`: 2194 passed, 27 skipped, 0 failed, the same result
test by test as unpatched master.

**Impact:** `addr2line`, coverage and other line-table tools either drop
these rows or index past the end of the source.
