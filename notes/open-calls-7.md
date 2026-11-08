# Open calls, round 7: roc-types at 11-07, and your patched Zig

**Answered (Steve, 2026-11-08):** agrees with the leans. Run the experiment, and keep everything on 11-03 meanwhile.

*2026-11-08. One call, with my lean at the end.*

**What happened.** roc-types is the type-walking tool that roc-chat's and Safari's method hunts need, built for each Roc pin. Building it for nightly 11-07 failed on GitHub after about 18 minutes. The crash is an LLVM assertion in its debug-info code (`FrameIndexExprs.size() == 1 || ...`), and it happens while patched Zig 0.17.0+patched.2 is compiling roc-types itself.

The same build with **stock Zig 0.17.0** passed (showell/shale run 42508848075, branch `roc-types-1107-stock-zig`) and produced the asset, `roc-types-1-ad3a5d2-linux-x86_64.tar.gz`. Nothing is installed or published yet. roc-chat, dog-park and roc-webbox are on 11-03, where roc-types already exists, so nothing is blocked.

**What it means.** The crash comes with your patched Zig, but that doesn't yet prove the patch is to blame. Two things differ between the builds:
- **The patches.** Patch 1, the generic-function debug line rows, changes debug info, which is exactly where the assertion fires. The other two are the arena growth and the `createDirPath` loop.
- **The LLVM.** The patched release is built against Zig's CI LLVM bundle, which I believe has LLVM assertions on. The official release's LLVM probably has them off. If so, stock Zig may make the same bad debug info and just not abort. I haven't confirmed which LLVM has assertions.

The experiment that settles it holds LLVM fixed: build your patched-zig-compiler at its `upstream-0.17.0` tag (the same LLVM bundle, no patches) and build roc-types with that. If it still crashes, the bug is upstream in Zig or LLVM, and Roc 11-07's code is what exposes it. If it passes, patch 1 is the suspect, and the next run drops only patch 1. Each run is about 25 minutes on GitHub, under showell.

**The call.**
1. Run that experiment (and the patch-1-only follow-up if needed) on GitHub, as the fifth-slot Roc track.
2. Meanwhile, either:
   - (a) leave 11-07 roc-types unbuilt, and keep everything on 11-03 until the cause is known; or
   - (b) install the stock-Zig 11-07 roc-types now, so roc-chat and roc-apps can move to 11-07.

*My lean:* yes to the experiment, and (a). Nothing needs 11-07 today, and a roc-types built with a different Zig than every other tool is a second thing to keep track of. If the experiment points at patch 1, that's a finding for your patched-zig repo, and a bug you'd want to know about anyway, since it's your Zig.
