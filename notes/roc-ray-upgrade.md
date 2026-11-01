# roc-ray upgrade: discovery and plan (2026-11-01)

*2026-11-01. A cold agent's discovery, for Steve: upgrading roc-ray to 0.12.0, what it forces (a Roc nightly move for roc-apps), and five questions.*

Discovery only: nothing was changed, built or installed. `git fetch` in
`~/showell_repos/roc-ray` was the one write (new tags and remote branches).

## 1. Where upstream is

| | |
|---|---|
| remote | `origin` = github.com/lukewilliamboswell/roc-ray, branch `main`, the only remote |
| our checkout | `main` at `3b9b7dc` (2026-10-11, PR #240 "roc-nightly-2026-10-09"), `0.10.0-6-g3b9b7dc0`, clean (untracked: built `platform/targets/*`, `zig-pkg/`) |
| upstream | `origin/main` = `23eec6e8` (2026-11-01 04:49Z), tag **0.12.0**, released today; 82 commits ahead of us |
| roc-apps' real base | `e100c95` (2026-09-14), 187 commits *behind* our checkout: README, `.github/workflows/{macos,windows}.yml`, site links all name it |

Releases since our checkout: 0.11.0 and 0.11.1 (10-24), 0.12.0 (11-01).

**Roc nightly.** Since 0.11.0 the platform names *no* compiler ("No compiler
pin": the `roc:` field is gone from `platform/main.roc` and app headers; a
`check_no_pins.roc` script enforces it). CI resolves the latest nightly per run
(`gh api repos/roc-lang/nightlies/releases/latest`). 0.12.0 says: "Built and
tested with Roc `nightly-2026-10-31-f7bef6b`".
The nightly-compat job (`.github/workflows/nightly.yml`, issue #266) shows the
window: 0.11.1 passed 10-26..10-28 and **fails on 10-29, 10-30 and 10-31**.
0.12.0's "restores compatibility" commit `2bb5d3a8` attaches methods
explicitly to receiver types (Draw.Frame, Math.Vec2, Physics, Gamepad
Snapshot): that is Roc's removal of receiver extensions (roc-lang/roc#12630,
landed 10-28). So:
- 0.11.x needs nightly ≤ 10-28; 0.12.0 needs ≥ 10-29 (tested on 10-31).
- 10-30 → 10-31 is 19 roc commits, none about methods or the platform ABI
  (codec, monotype scoping, case-of-case joins, LangRef). 0.12.0 on 10-30 is
  very likely fine but **untested upstream**; step 2 below tests it.

**Host build needs** (`build.zig.zon`, CI):
- **Zig 0.17.0** (`minimum_zig_version`; our checkout wants 0.16.0). The box
  has `zig 0.17.0+patched.2` on PATH, and `~/zig-0.16.0` for the old one.
- One Zig package: `zio` (git, lalinsky/zio @be65431).
- raylib, libvpx, sqlite, msf_gif are **not built**: they are "linker inputs"
  downloaded from a content-addressed release locked in
  `link-inputs.lock.json` (`link-inputs-sha256-9b4be6fc…`, ~5 MB per target,
  `scripts/link_inputs.py install`, python3, rehashed every run). raylib's
  header is consumed through a translate-c module.
- macOS hosts need a downloaded interface tree (`scripts/prepare_dependencies.py`).
- Linux link uses stubs (`platform/targets/x64v1glibc/libc_stub.s`, Scrt1/crti);
  no system dev packages to *build*. To *run*, libX11.so.6 and libGL.so.1,
  both present on the box (headless mode draws nothing).

**Prebuilt hosts: yes.** Each release ships two platform bundles:
- default `…/0.12.0/79nt7eRxopFeMc2RcTHhPmjDxdRZjpNWLa9Na5xVGw9p.tar.zst`
  (14.7 MB): x64mac, arm64mac, x64win, x64v1glibc (X11);
- Wayland `…/0.12.0/FywVsZM7cow5ddCwFH4Y9Z4jvM5rtFeyC3gwoxq7kTHt.tar.zst`
  (3.3 MB): x64v1glibc with Wayland raylib.
Release hosts are ReleaseFast (`check-release-hosts`). Plus
`roc-ray-examples-0.12.0.zip` (examples + `spec.json` of headless output) and docs.

**Targets.** `x64glibc` was renamed `x64v1glibc` on 2026-09-28 (`1fdd71b7`,
"baseline x86-64"). Platform targets now: x64mac, arm64mac, x64v1glibc, x64win.

## 2. The gap, as it touches us

The users of `~/showell_repos/roc-ray`, all by sibling path:
1. **roc-apps canvas apps**: 8 `<app>/main.roc` and `canvas_apps/native/main.roc`
   (`../../../roc-ray/platform/main.roc`). Only `native/CanvasAppRunner.roc`
   (520 lines) imports roc-ray modules: App, Assets, Camera, Color, Devices,
   Mouse, Draw, Math. `lib/` only mirrors roc-ray's names, and imports none.
2. **dog-park** `roc/native.roc` (`../../roc-ray/platform/main.roc`), on
   nightly 10-09 (`dog-park/roc/roc-version`), and its
   `.github/workflows/native.yml` defaults `roc_ray_ref` to **3b9b7dc**. This
   is the one user of today's checkout; the brief didn't list it. It uses no
   shaders.
3. roc-apps workflows `macos.yml` and `windows.yml` check out roc-ray
   `e100c95` with Zig 0.16.0 and nightly 09-22.

Why `native.sh safari` fails today: `native.sh` defaults `TARGET=x64glibc`. Our
3b9b7dc platform declares `x64v1glibc`, so roc says "does not support the
x64glibc target" (`~/build/roc-apps/canvas_apps/safari/build-x64glibc-dev.log`).
`platform/targets/x64glibc/` holds stale 09-15 hosts from the e100c95 era, and
`targets/x64v1glibc/` has no `libhost.a` because `zig build` hasn't been run
since the pull. And 3b9b7dc wants nightly 10-09 while roc-apps is on 09-22.

API changes e100c95 → 0.12.0 that the runner meets (I checked each signature
at both ends):
- **Breaking: shaders (0.11.0).** `Draw.Shader`, `uniform_f32!`,
  `uniform_vec4!`, `Draw.F32Uniform` / `Vec4Uniform` and `.set!` are gone. Now
  `Shader.from_source!(src, uniforms_record)` checks a record against the GLSL
  once. `frame.with_shader!(shader.with_uniforms(record), |f| …)` supplies all
  values per scope, and the update is pure. CanvasAppRunner uses exactly the old API: lines 42-50
  (Gpu record), 77-87 (init), 401-460 (`set_uniforms!`). The port:
  - `import rr.Shader`; `Gpu.shader : Shader.Shader({ mode : F32, clip : Math.Vec4, … })`;
  - the field names must equal the GLSL names (`UniformFormat.rename_field` is
    the identity). BrushGlsl uses camelCase (`colorA`, `geomA`…), so rename the
    GLSL uniforms to snake_case in `lib/BrushGlsl.roc`. Only the native runner
    reads them; `shapewire.js` merely mentions BrushGlsl in a comment;
  - `set_uniforms!` becomes a pure `uniforms_of(fill, clip) -> record`;
    unused slots get zero, because every field is sent each time;
  - the init error row: `UniformNotFound` becomes `UniformNotFound(Str)`, plus
    `UniformReflectionUnavailable`, `UniformTypeMismatch({…})` and
    `UnsupportedUniformType(Str)`.
- Target rename `x64glibc` → `x64v1glibc`: `native.sh`'s default, and the
  README's.
- Unchanged in signature: `with_render_texture!`, `with_camera!`,
  `with_blend_mode!`, `convex_polygon!`, `circle!`, `rectangle!`, `texture!`,
  `Draw.filled`, `Draw.additive_blend`, `Draw.RenderTexture.load!` (its error
  row is now closed, which `?` into init's row still accepts),
  `Assets.set_texture_filter!`, `App.init/with_title/with_size/with_frame_pacing`,
  `Camera.new`, Devices/Mouse snapshot methods.
- 0.10-era files and permissions changes: the runner uses no files, HTTP or
  permissions, so nothing to declare.
- 0.12.0 scissors now belong to their surface. The runner clips in the shader,
  not with scissors, so this shouldn't affect it.
- dog-park `native.roc` (3b9b7dc → 0.12.0): no shader use; it needs a
  nightly ≥ 10-29 and whatever receiver-extension rewrites its own code needs.

New in 0.12.0 that could pay off later (not part of the upgrade):
`frame.triangles!` / `triangle_fan!` / `triangle_strip!` would draw a
`Pieces` (from `Shapes.cut`) in one call instead of one `convex_polygon!` per
triangle. `ring!`, `ellipse!`, `line_strip!` and `circle_sector!` exist too,
but the page has to draw the same thing, so the shared polygon builders stay.

## 3. The upgrade path

### It forces a Roc nightly move
Any roc-ray past e100c95 needs a newer Roc than roc-apps' 09-22: 3b9b7dc wants
10-09, 0.11 wants 10-23..10-28, and 0.12.0 wants ≥ 10-29. **Target: 0.12.0 on
nightly-2026-10-30-0602c5f**, the pin roc-chat, roc-markdown and Shale's
roc-ast and roc-types already use. It is installed at
`~/tools/roc-nightly-2026-10-30-0602c5f`, and roc-apps' own release
`toolchain-2026-10-30-0602c5f` carries it. One Roc for the recipes, `roc fmt`
and the canvas apps is then on the table. 10-31 would be upstream's exact
compiler; 10-30 trades one untested day for one compiler across repos.

What the move means for roc-apps (`roc-nightly.txt` is one pin for the whole
repo):
- **Scope.** `roc-nightly.txt` is read by `canvas_apps/{native,build}.sh`,
  `basic/build.sh`, `fasttrack/{build,run_exp}.sh`, `tests/ladder.sh` and
  `findings/from-quote-quadratic/run.sh`; the GitHub workflows hard-code 09-22.
  Moving it moves basic, fasttrack and the ladder too, unless canvas_apps gets
  its own pin (open question).
- **09-22 → 10-09 is uncharted on this box.** roc-chat and roc-markdown went
  10-09 → 10-29 → 10-30. What they met: receiver extensions removed (10-28),
  `roc fmt` parenthesizing a one-line `if` condition (a format-only diff), and
  `roc` naming files relative to the run start. The span 09-22 → 10-09 has
  never been crossed here: possible glue API changes (`glue/JsGlue.roc`
  follows 09-22's API, and `build.sh` runs `roc glue`), builtins
  (`List`/`Str` method names), and the 09-23 brk allocator (a speed change,
  for the better). `roc check` at 10-30 is the census. Use roc-chat's
  `tools/chat_glue.shale` for a glue that works at 10-30.
- **Receiver extensions.** roc-apps code written at 09-22 may call a
  module's function as a method on another module's type (for example on
  `Input.Snapshot` or `CanvasApp`). 10-28+ refuses that. `roc check` finds
  them; each fix is to move the function into the type's `.{ }` block or
  call it as a function.
- **Web path.** It does **not** use roc-ray; it is `canvas_apps/web/` (wasm
  platform, `host.zig`, Zig 0.16 at `~/zig-0.16.0`). It breaks only through
  the Roc move: the wasm build, `roc glue`'s JsGlue output, the host's ABI and
  the 09-22 fresh-cache SIGSEGV workaround (re-check whether it is still needed).
  The page check (`node canvas_apps/web/page_check.mjs <app>`, run by
  `build.sh`) is the judge.

### Order of steps, each with its check
0. **Decide the two forks** (open questions 1-2) before touching anything.
1. **Census, nothing changed** (minutes, box). `roc check` with 10-30 on
   every canvas app's `web.roc` (no roc-ray involved) and on `lib/main.roc`.
   Count the errors and sort them into syntax, builtins and receiver
   extensions. The same for the other roc-apps trees if they move with the pin.
2. **roc-ray to 0.12.0** (box, light). Either use the release bundle URL
   (no host build) or `git -C ~/showell_repos/roc-ray merge --ff-only
   origin/main`, then `nice -n 19 zig build hosts -j1`. That builds only
   hosts, without the link-input download; add `zig build link-inputs-install`
   for the locked raylib and friends. Check roc-ray's own tests:
   `zig build test -Droc-tests=false` (Zig unit tests, light), then a
   handful of examples headless with 10-30:
   `roc build examples/{snake,pong,breakout,camera,particles,post_process}/main.roc --target=x64v1glibc --opt=dev`
   and run each with `--host-headless --host-headless-frames=3`. Compare
   against `spec.json` in `roc-ray-examples-0.12.0.zip`. This step alone
   shows whether 0.12.0 works on 10-30.
3. **roc-apps Roc move to 10-30**, as its own commit (CLAUDE.md §2): the
   pin, `roc fmt` (the format-only diff, kept out of logic commits), the
   census fixes, glue. Check: `build.sh` for all 8 apps (page check plus
   shot); the safari spec apps (see below); the trees the pin moves.
4. **The runner port**: shaders, `TARGET=x64v1glibc` default in native.sh,
   BrushGlsl uniform names. Check: `canvas_apps/native.sh <app>` for all 8
   apps, then each exe headless (`--host-headless --host-headless-frames=3`).
   Then a visual check: the gradient brushes (safari's sky, glow) on a real
   display. That's an eye test, so Steve does it on a desktop when he likes;
   it doesn't block.
5. **Workflows**: `windows.yml` and `macos.yml` move to Zig 0.17.0,
   `roc_ray_ref` 23eec6e (or the bundle), and `roc_nightly`
   nightly-2026-10-30-0602c5f. Their dispatch inputs already allow a probe of
   a new pair before the defaults move: `gh workflow run windows.yml -f
   roc_ray_ref=23eec6e8 -f roc_nightly=nightly-2026-10-30-0602c5f -f apps=snake`.
   That needs Zig 0.17 first, so the Zig bump goes in before the probe.
   Then update the README's "taken at e100c95" note: the apps' *provenance*
   stays e100c95, and the platform they run on becomes 0.12.0.
6. **dog-park native** (if the checkout moves): nightly ≥ 10-29 for
   `roc/native.roc`, and `native.yml`'s `roc_ray_ref` and Zig version. Or
   leave dog-park on 3b9b7dc via the bundle choice (question 2).

**Safari's 54 spec apps**: each is a headless `main!` program (no app header,
no roc-ray), so they test the Roc move, not roc-ray. Their runners
(`safari/emitted.sh`, `retest.sh`) are retired and exit 2, so nothing runs them
today. A small Shale runner (`roc` each with 10-30, diff against the 09-22
output) would be needed. Capture the 09-22 outputs **before** the pin moves.

## 4. The box's limits

| step | weight | where |
|---|---|---|
| `roc check` / `roc build --opt=dev` of a canvas app or example | light (seconds; dev backend) | box |
| `--opt=speed` (LLVM) builds | heavier; upstream's CI avoids it on hosted runners for the large examples | box, one at a time, niced; not in the fix loop |
| `zig build hosts` (4 cross hosts: x64mac, arm64mac, x64v1glibc, x64win; Debug by default; ~2.3 MB of Zig in `src/` plus translate-c of raylib.h, and zio) | moderate: four compiles, likely minutes each, peak memory maybe 1-3 GB per compile | box with `nice -n 19 … -j1`, so the four compiles run one at a time; there is no single-target option, and building only x64v1glibc means editing `all_native_targets`, which we shouldn't |
| `zig build` default | above + link-input download (~25 MB) + macOS interfaces download | box, fine |
| `zig build test` (default `roc-tests=true` builds every Roc example) | heavy | not on the box; use `-Droc-tests=false` |
| raylib / libvpx (linker inputs) | heavy, but never built: downloaded and hash-checked | n/a |
| Roc compiler | forbidden here | not needed: nightlies are prebuilt |
| Windows exe; macOS | can't link here | roc-apps `windows.yml` and `macos.yml` (workflow_dispatch, under showell), after the Zig 0.17 bump |

**The cheapest option of all: the release bundle.** Pointing the canvas apps
at `…/0.12.0/79nt7e….tar.zst` needs no host build on the box and no
`zig build` in the workflows, and pins by content hash. The cost: the README's
deliberate "roc-ray is a sibling path" rule changes, and a local roc-ray patch
can't be tried without switching back.

## 5. Risks
- 0.12.0 on 10-30 is untested upstream (10-31 was). Mitigation: step 2, or
  pin 10-31.
- The 09-22 → 10-09 span is uncharted here: glue API, builtins, receiver
  extensions. The size is unknown until step 1's census.
- A regression in safari or other trees from the Roc move (a codegen change,
  not a compile error). The spec apps and page checks are the judges, and the
  spec apps have no live runner.
- Shader per-scope cost: `with_uniforms` re-encodes all 8 uniforms into a list
  per gradient shape, where the old API made one `set!` per used uniform.
  Safari draws many gradient shapes, so frame time could move. Measure with
  `FrameBench` / headless frame timing before and after.
- A shared checkout: dog-park native and the canvas apps both use
  `~/showell_repos/roc-ray`, so moving it moves both.
- Upstream moves fast: three releases in eight days, and it floats on the
  latest nightly. Pin a tag (0.12.0 / 23eec6e), not `main`.
- Disk: 36 GB free (77%); hosts plus link inputs are small.

## 6. Open questions for Steve
1. Move all of roc-apps to 10-30 (one pin, which also moves basic, fasttrack
   and the ladder), or give canvas_apps its own pin first?
2. Sibling checkout, or the 0.12.0 release bundle URL? The bundle means no
   host builds anywhere and leaves dog-park on 3b9b7dc. The checkout keeps the
   README's rule and moves dog-park native too.
3. 10-30 (one Roc across repos) or 10-31 (upstream's tested compiler)?
4. Bring dog-park's native to 0.12.0 in the same sweep, or leave it?
5. The safari spec apps: write a small 10-30 runner for them, and capture
   their 09-22 outputs first?
