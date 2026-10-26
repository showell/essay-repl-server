# Draft: a second Zig issue, for Steve to file on Codeberg

*Found on the box while explaining why a Roc chat route took 6x its
payload in request memory (metal-vmm FEEDBACK, 2026-10-26: two of the six
were this). Reproduced with 0.17.0 and master `0.18.0-dev.610+720939f8c`;
the lines are unchanged on Codeberg master today. The fix was checked on a
patched copy of the file: the repro, and the file's own tests, the
multi-threaded fuzz included.*

---

**Title:** `std.heap.ArenaAllocator`: a request that doesn't fit the current node grows it by twice the request

**Zig version:** 0.17.0 and master `0.18.0-dev.610+720939f8c`, x86_64-linux.

**Repro** (`overshoot.zig`): an arena over a child that can grow its last
allocation in place (`FixedBufferAllocator`), with a logging wrapper so the
child's requests show.

```zig
const std = @import("std");

const Logging = struct {
    child: std.mem.Allocator,

    fn allocator(self: *Logging) std.mem.Allocator {
        return .{ .ptr = self, .vtable = &.{ .alloc = alloc, .resize = resize, .remap = remap, .free = free } };
    }
    fn alloc(ctx: *anyopaque, n: usize, a: std.mem.Alignment, ra: usize) ?[*]u8 {
        const self: *Logging = @ptrCast(@alignCast(ctx));
        std.debug.print("  child alloc  {d}\n", .{n});
        return self.child.rawAlloc(n, a, ra);
    }
    fn resize(ctx: *anyopaque, m: []u8, a: std.mem.Alignment, n: usize, ra: usize) bool {
        const self: *Logging = @ptrCast(@alignCast(ctx));
        std.debug.print("  child resize {d} -> {d}\n", .{ m.len, n });
        return self.child.rawResize(m, a, n, ra);
    }
    fn remap(ctx: *anyopaque, m: []u8, a: std.mem.Alignment, n: usize, ra: usize) ?[*]u8 {
        const self: *Logging = @ptrCast(@alignCast(ctx));
        return self.child.rawRemap(m, a, n, ra);
    }
    fn free(ctx: *anyopaque, m: []u8, a: std.mem.Alignment, ra: usize) void {
        const self: *Logging = @ptrCast(@alignCast(ctx));
        self.child.rawFree(m, a, ra);
    }
};

pub fn main() !void {
    var buf: [1 << 20]u8 = undefined;
    var fba: std.heap.FixedBufferAllocator = .init(&buf);
    var logging: Logging = .{ .child = fba.allocator() };
    var arena: std.heap.ArenaAllocator = .init(logging.allocator());
    defer arena.deinit();
    const a = arena.allocator();

    std.debug.print("alloc 100:\n", .{});
    _ = try a.alloc(u8, 100);
    std.debug.print("alloc 100000 (does not fit the first node):\n", .{});
    _ = try a.alloc(u8, 100_000);
    std.debug.print("arena holds {d} bytes for 100,100 requested\n", .{arena.queryCapacity()});
}
```

```sh
zig run overshoot.zig
```

**Actual:**

```
alloc 100:
  child alloc  212
alloc 100000 (does not fit the first node):
  child resize 212 -> 200124
arena holds 200100 bytes for 100,100 requested
```

**Expected:** a resize to about 100,124 (the 24-byte header, the 100 bytes
in use, the 100,000 requested); about 100,100 held.

**Cause:** `alloc`'s fast path reserves with an atomic add before it checks
the fit (`ArenaAllocator.zig:358`):

```zig
const end_index = @atomicRmw(usize, &node.end_index, .Add, alignable, .acquire);
...
if (aligned_index + n > buf.len) break :first_node .{ node, buf.len };
```

A request that doesn't fit leaves its reservation in `node.end_index`,
past the end of `buf`. The resize path then reads that `end_index` back and
computes the new size from it (`:387-389`):

```zig
const end_index = @atomicLoad(usize, &node.end_index, .monotonic);
const aligned_index = alignedIndex(buf.ptr, end_index, alignment);
const new_size = mem.alignForward(usize, @sizeOf(Node) + aligned_index + n, 2);
```

so `n` is counted twice: once as the failed reservation, once as the
request. On success the `cmpxchg` sets `end_index` to `aligned_index + n`,
so the first `n` bytes after the old end are never used.

**Impact:** any arena that grows by resizing pays up to twice for its
large allocations. `reset(.retain_capacity)` then keeps the doubled
capacity, and when it can't resize it allocates a block that size afresh.
In our server a request copying an N-byte buffer through an arena cost 2N
for the copy, then 2N more held by the reset.

**Fix:** nothing past `buf.len` is in use (every allocation that
succeeded ended at or before it), so grow from there when `end_index` has
overshot:

```diff
--- a/lib/std/heap/ArenaAllocator.zig
+++ b/lib/std/heap/ArenaAllocator.zig
@@ fn alloc(
             const buf = allocated_slice[@sizeOf(Node)..];
             const end_index = @atomicLoad(usize, &node.end_index, .monotonic);
-            const aligned_index = alignedIndex(buf.ptr, end_index, alignment);
+            // A fast-path reservation that did not fit is left in `end_index`, past
+            // the end of `buf`; nothing beyond `buf.len` is in use, so grow from there,
+            // not from the overshoot, or the node grows by the request twice.
+            const aligned_index = alignedIndex(buf.ptr, @min(end_index, buf.len), alignment);
             const new_size = mem.alignForward(usize, @sizeOf(Node) + aligned_index + n, 2);
```

The `cmpxchg` after the resize still expects the loaded `end_index`, so a
concurrent allocation between the load and the swap fails it as before.
With the fix the repro prints `child resize 212 -> 100212` and `arena holds
100188 bytes`, and the file's tests (the multi-threaded fuzz included)
pass. The old node's unused tail (88 bytes here) is still skipped; using
the failing caller's own pre-add `end_index` would reclaim it in the
single-threaded case, at the cost of carrying it out of the fast path.
