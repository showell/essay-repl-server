# Open calls, round 4

One call. My lean is at the end.

1. **Publishing roc-types for the 11-07 nightly.** You asked to move the Roc pins today. roc-markdown moved to nightly-2026-11-07-ad3a5d2 with no source changes; its whole verify passed and it's on main. roc-chat moved too, and every check passed but one: the `methods` hunt needs **roc-types**, the type-walking tool, built for the same nightly. There's one for 10-30 and one for 11-03, but none for 11-07. roc-apps will hit the same wall when its pin moves.

   roc-types is never built on this box. It's built by Shale's `roc-types.yml` workflow on GitHub, under showell, and published as a release asset, `roc-types-1-ad3a5d2-linux-x86_64.tar.gz`. Then Shale's `tools/roc_types/roc-version` and `release` get bumped, and it's installed beside the old ones. The 10-30 and 11-03 trees keep their own copies. roc-types' source may also need changes for the new compiler; nobody has checked yet.

   Running the workflow and uploading the asset are outward steps, so they're yours to approve.

   *My lean:* yes. Run the workflow and publish the asset. If roc-types won't build at 11-07, I'll stop and tell you, and roc-chat and roc-apps would stop at 11-03 instead, where roc-types already exists.

2. **Node's "WASI is experimental" warning.** Dog Park's gates now fail on any node warning. `--no-warnings` used to hide them all, and a preload now turns any warning into a failure. One narrow suppression is left: `run_wasi.mjs` passes `--disable-warning=ExperimentalWarning`, because node 22 prints "WASI is experimental" on every run. It's a notice about node itself, not about our code, but it's still a suppression.

   *My lean:* keep it, limited to that one file and that one warning class, with a comment saying why. The alternative is waiting for a node release where WASI is stable.

3. **The Roc crash behind the widget builds: file it, and build a debug compiler.** A three-file program, about 20 lines, crashes the compiler on both nightlies, native and wasm alike, while `roc check` is clean. It's a method call on an annotated nominal-record literal, from a module other than the root, into a method that puts a top-level constant in a list. It's written up in roc-apps `findings/widget-method-segv/README.md`. No upstream issue matches; the closest are #12919 and #12194. A release nightly has no developer diagnostics, so finding the cause needs a debug build, and that's too heavy for this box.

   *My lean:* yes to both. (a) File the issue on roc-lang/roc with the reduced program, saying it's Claude and what didn't work, the way we've filed before. (b) Run a debug build on GitHub under showell, with the repro, to get the named assertion or stack trace. Then a patch and a PR if the fix is small.
