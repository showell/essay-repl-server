# Dog Park v9: play it, then deploy

*2026-11-08. Prod still serves v8 (image `dogpark-74dda6f5e712`). Nothing has touched prod.*

## 1. Play it

The release candidate is on the dev server:

- the park: http://143.244.172.148:9103/
- the list: http://143.244.172.148:9103/todo/

It's the same build as the image (dog-park 5d8a122, roc-webbox a79623d, Roc nightly-2026-10-30). The dev server now serves the combination, park plus `/todo`, the way prod does. Its old data was moved aside to `data.pre-v9`, so it starts empty.

## 2. Read this before deploying

**A deploy restores the droplet from a fresh image, so prod starts empty: every account, game and TODO list goes.** The physics hash changed too, so any open page reloads once. If anything on prod should survive, say so before step 3 and I'll find out whether DEPLOY.md has a way to carry data across.

## What v9 carries since v8

- **The Roc pin**, 10-09 → 10-30. With it, `build.zig` drops the `--` that roc 10-30 now passes to the printers, and `Walk.drag` reads the leashed dog out of `k3` before putting it back. At 10-30 the old code made a copy of the list, and the physics' allocation guard caught it.
- **Gates with no skips.** The golden runs fail instead of stepping aside, node runs fail on any warning, the wasm tests fail on a skip, and the new-kind test runs alone. The one suppression left is open call #2 in round 4.
- **The builds find their own Roc** at `~/tools/roc-<pin>/roc` and refuse any other version, in both dog-park and roc-webbox. The old nightly on the PATH can no longer sneak into a build.
- **The TODO list's frozen chat builds again**, and roc-webbox's gate is clean: 17 of 17 steps, 36 of 36 tests.

## The checks behind it

- metal-gate passes in QEMU on both `dogpark.elf` and `dogpark-todo.elf`.
- `node droplet/image.mjs` built the image, ran its rehearsal (`rehearse PASS`) and printed `ready to deploy`.
- Image: `~/dogpark-images/dogpark-5d8a122bbe0e.img.gz`, 1.9 MiB, sha256 `7841faa8…f19f1`.

## 3. Deploy (DEPLOY.md, "A new release")

1. Serve the image to DigitalOcean:
   ```
   shale <<'SHALE'
   job_start({"busybox", "httpd", "-f", "-p", "9301", "-h", "/home/steve/dogpark-images"}, {log = "scratch:dogpark-images-http.log", want = "file-server: busybox's httpd serves the image to DigitalOcean's import"})
   SHALE
   ```
2. In DigitalOcean, go to Custom Images, then Import via URL:
   - URL: `http://143.244.172.148:9301/dogpark-5d8a122bbe0e.img.gz`
   - Name: `dogpark-5d8a122bbe0e`
   - Distribution: Unknown
   - Region: nyc2

   When it says ready, stop the file server:
   ```
   shale <<'SHALE'
   job_stop("scratch:dogpark-images-http.log.job")
   SHALE
   ```
3. On the `dogpark` droplet, choose Destroy, then Restore base image, from `dogpark-5d8a122bbe0e`. Check both names first.
4. Tell me it's done, and I'll run the smoke test (the home page, `/admin/game` with and without the key, a TODO post, `/version` naming 5d8a122) and tag v9.
