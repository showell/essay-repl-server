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
| zig-metal-unikernel | done: 1,436 tests as on 0.16; images build with a patched compiler_rt and 25 probes boot in QEMU |
| observatory | done, its image builds |
| dog-park | done: `check` green, golden physics bit-for-bit, its image boots (metal-gate) |
| angry-gopher | done: `ops/check` counts identical to 0.16's; its image builds |

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

## Theme 4: one real blocker, upstream, worked around

The kernel's images couldn't build on 0.17.0. compiler_rt is the runtime
library Zig links into every program: memcpy, soft-float arithmetic and
128-bit division. It doesn't compile for the kernel's soft-float x86_64
target. This is a known regression,
[ziglang/zig#37006](https://codeberg.org/ziglang/zig/issues/37006), with a
fix (#37324) aimed at 0.17.1. A cold agent found a second failure that fix
doesn't cover (the complex-number multiply and divide files). So 0.17.1 alone
may not be enough.

The failing code is never called by the kernel: no long doubles, no
complex numbers. Zig builds the library as one unit, though, so one bad file
stops everything.

**The workaround:** the kernel carries `compiler_rt_0_17_0/`, 0.17.0's
compiler_rt with the upstream fix's hunks plus two lines of our own (21
files). It's linked in place of Zig's own. The compiler and std stay stock.
The build refuses any Zig but 0.17.0, naming the folder to delete, so the
patch can't outlive its version.

With it, every image builds, the 25 probe kernels boot in QEMU, and Dog
Park's image passes its metal gate. lynrummy.com's own boot gate is left for
release morning.

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

## Theme 6: a green build in one repo isn't the whole story

Zig compiles only the functions something uses. Webbox had two functions
its own tests never call, still in 0.16 form, and only angry-gopher's and
dog-park's builds reached them. Shale's build passed alone but broke as
angry-gopher's dependency: a dependency's paths are relative to the
top-level build. And `zig fmt .` reformatted a generated file, whose hash
then made Dog Park's golden tests step aside: 7 silent skips, no failure.
Each was caught by running the consumers' own gates and comparing counts with
0.16, never by one repo's green build.

## Next

Every repo is ported and judged on its branch. What's left is the cutover:

- merge the eight `zig-0.17` branches together;
- move the box (and CC) to 0.17.0;
- run the release gates, including lynrummy.com's metal gate;
- deploy.

That's your call on timing.
