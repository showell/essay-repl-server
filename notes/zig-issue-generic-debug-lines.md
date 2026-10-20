# Draft: a Zig 0.17.0 issue, for Steve to file on Codeberg

*Found by CC (Cloud Claude) while porting our line-coverage tool, and
reproduced on the box. No one here has a Codeberg login, so this is the
text to paste at https://codeberg.org/ziglang/zig/issues/new. I searched
first and found no existing report.*

---

**Title:** Debug line info: a generic function's prologue/epilogue rows carry line numbers past the end of its file

**Zig version:** 0.17.0 (x86_64-linux). It happens with the self-hosted x86_64 backend and with `-fllvm`.

*(This report was written by Claude, an AI assistant, on behalf of the
reporter. It found the problem while building a line-coverage tool on Zig's
DWARF.)*

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
readelf --debug-dump=decodedline bin | awk '$1=="r2.zig" && $2+0>11'
```

**Actual:** rows naming `r2.zig` at lines 24 and 25 (self-hosted x86_64);
line 24 with `-fllvm`. The raw line program for `pick`'s instance sets the
file to entry 0 (`r2.zig`), the column to 24, and advances the line to 24
for the prologue, then has the body at line 5 and line 25 for the epilogue.

**Expected:** the prologue at line 3 (the `fn` line) and the epilogue
at line 6 (the closing brace), all within the file.

**Notes:**
- It looks like the source location of the generic instance's entry and
  exit, not a backend's: both backends agree on line 24.
- A plain function with a comptime parameter but a simple return type shows
  it too (rows at 15, 16 and 36 in a 12-line file).
- In a larger file, a generic `pick` at line 227 of a 1,221-line file gets
  lines 1291, 1292, 1541 and 1542, column 1081.
- **Impact:** coverage and line-table tools (`addr2line`, our ptrace line
  coverage) either drop these rows or crash indexing the source by them.
