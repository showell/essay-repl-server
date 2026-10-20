# The Zig 0.17 upgrade: the big picture

*2026-10-20. Where the upgrade stands, and its major themes. The details are in
each repo's `zig-0.17` branch and in shale's `cookbook/zig17/README.md`.*

## Where it stands

| repo | state on its `zig-0.17` branch |
|---|---|
| zig-coverage-sdk | done, tests pass |
| zig-webbox | done, tests pass |
| metal-vmm | done, tests pass |
| shale | done, 327 tests as on 0.16 |
| zig-metal-unikernel | host side done, tests pass; **its images cannot build on 0.17.0** |
| observatory, dog-park, angry-gopher | next |

Nothing is merged. The repos build against each other by path, so they move
as one set: a tree of `zig-0.17` worktrees in `~/zig17`, judged together,
then merged together.

## Theme 1: most of it is mechanical, and Shale does it

What I hoped held up. The 0.17 changes our code hits are mostly renames and
reshapes that a script can make with certainty. Four Shale scripts in
`shale/cookbook/zig17/`:

- **census:** counts what each repo uses that 0.17 changed;
- **array_mult:** the `**` operator on arrays and strings is gone, so each use
  becomes `@splat` or a small comptime `repeated()`;
- **renames:** about a dozen removed or reshaped APIs;
- **has_decl:** `@hasDecl` now sees only `pub` declarations (theme 3).

Then `zig fmt` 0.17 rewrites the deprecated builtins itself. Across the five
repos so far, the scripts made roughly 250 rewrites and hands made a few dozen.
The scripts grew as each repo showed a new shape: the kernel's 25 repeated
multi-character strings taught array_mult its `repeated()` form.

## Theme 2: the build scripts take the most hand work

`build.zig` is where 0.17 changed the most, and in ways no script can follow,
because each repo's build does something different:

- `b.build_root` and `pathFromRoot` are gone;
- paths are relative where they were absolute, which matters when a path is
  handed to another process (shale's tests run git in webbox's checkout);
- `LazyPath.getPath` is gone, so a build can't read a file while the graph is
  being made without resolving the path itself;
- `setExecCmd` is gone, so the kernel's test-timing wrapper became a hand-built
  run step;
- `b.args` and the fmt, zon and option APIs changed shape.

Each repo now has a few small, named build helpers where it had a std call.
This is the part to watch when handing a repo to CC.

## Theme 3: the changes no compiler shows

The upgrade's real risk. Three behaviours changed under unchanged code, and
only tests caught them:

- **`@hasDecl` sees only `pub`.** An optional feature checked by
  `@hasDecl(root, "x")` silently turns off when `x` isn't `pub`, with no error
  at all. `has_decl.shale` finds every such declaration before the tests run.
- **`allocRemaining(.limited(n))` now accepts exactly `n` bytes.** Code that
  passed `max + 1` to allow `max` now allows one byte more. Webbox's body
  limit was wrong by one; Shale's reads were not, because each is followed by
  its own size check.
- **A generic's `@src().fn_name` suffix changed.** The coverage SDK cut names
  on the old suffix.

The kernel's tests turned up a fourth kind: a test whose assumption was
always false, which 0.17 exposed. The page-allocator test assumed a test heap
never contains a 256 KiB-aligned page. The 0.17 testing allocator sometimes
places one there, and the allocator then rightly hands it out. Making that
seed's test say what it means fixed it, not changing the allocator.

The lesson for the rest: **compiling is half the port, and a repo's own tests
are the other half.** A repo with thin tests is where a silent change would
survive.

## Theme 4: one real blocker, and it's upstream

The kernel's images can't build on 0.17.0. Its compiler_rt (memcpy, soft-float
arithmetic, 128-bit division) doesn't compile for soft-float x86_64. This is a
known 0.17.0 regression,
[ziglang/zig#37006](https://codeberg.org/ziglang/zig/issues/37006), listed in
the release notes, with a fix in review aimed at **0.17.1**.

The kernel uses soft float because it saves no floating-point registers on an
interrupt. Turning soft float off to dodge the bug would move the kernel's few
float operations onto x87 registers it also doesn't save. That would trade a
build failure for a possible runtime corruption, so I didn't do it.

What follows:

- **Everything can be ported and tested on 0.17.0 now**, except building and
  booting the kernel images.
- **The cutover waits for 0.17.1.** Anything that serves (lynrummy.com, Dog
  Park) ships as a kernel image, so a "big bang" cutover can't happen before
  then. The port can be finished and parked, ready.
- Kernel-only checks (the metal gate, `zig build consumers`) wait with it.

## Theme 5: skipped tests

You asked to stop carrying skipped tests. What the upgrade turned up so far:

- **Shale: 15 skips.** These are the expensive fuzzes and sweeps; they compile
  into `zig build test`, skip there, and run under `zig build fuzz`. The plan
  is to remove the error-prone parts:
  - build them only into `fuzz`, so `test` says 0 skip and any skip means
    something;
  - make `fuzz` fail if it runs fewer tests than exist.
- **The kernel: 1 real skip.** A test known to be red, parked "until the
  ruling" on how the request heap counts what a request uses (metal-vmm's
  QUEUE). It needs that ruling, then it either passes or goes.

Both are noted, to take up after the cutover.

## Next

Observatory (small), then dog-park and angry-gopher, the same way. Then the
whole set judged together in `~/zig17`, except the image builds, and parked
for 0.17.1.
