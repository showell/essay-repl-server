# Open calls, round 4

One call. My lean is at the end.

1. **Publishing roc-types for the 11-07 nightly.** You asked to move the Roc pins today. roc-markdown moved to nightly-2026-11-07-ad3a5d2 with no source changes; its whole verify passed and it's on main. roc-chat moved too, and every check passed but one: the `methods` hunt needs **roc-types**, the type-walking tool, built for the same nightly. There's one for 10-30 and one for 11-03, but none for 11-07. roc-apps will hit the same wall when its pin moves.

   roc-types is never built on this box. It's built by Shale's `roc-types.yml` workflow on GitHub, under showell, and published as a release asset, `roc-types-1-ad3a5d2-linux-x86_64.tar.gz`. Then Shale's `tools/roc_types/roc-version` and `release` get bumped, and it's installed beside the old ones. The 10-30 and 11-03 trees keep their own copies. roc-types' source may also need changes for the new compiler; nobody has checked yet.

   Running the workflow and uploading the asset are outward steps, so they're yours to approve.

   *My lean:* yes. Run the workflow and publish the asset. If roc-types won't build at 11-07, I'll stop and tell you, and roc-chat and roc-apps would stop at 11-03 instead, where roc-types already exists.
