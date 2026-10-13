# The renames: zig-webbox and zig-metal-unikernel

*2026-10-13. The plan, for review before anything moves. Two jobs, done
by the box with local helpers (not CC), in this order: extract `webbox`
from angry-gopher into its own repo, **zig-webbox**; then rename
gopher-metal to **zig-metal-unikernel**. The code freeze holds until
both are done and the gates and long tier pass.*

## What the survey found

- **The split is already clean.** Of angry-gopher's 105 source files, 24
  are the library: everything reachable from `webbox.zig`,
  `webbox_linux.zig` and `host_io_std.zig`. Not one of them imports a
  file outside those 24.
- **The app only imports the library by module name** (164 uses), never
  by file path. So the extraction moves files and rewires three builds;
  no app file's code changes.
- **The 24:** `site`, `body`, `http`, `edge`, `signed`, `site_secret`,
  `signed_cookie`, `html`, `bus`, `sse`, `mem_meter`, `host_facts`,
  `log_view`, `traffic`, `store`, `counter`, `client_address`,
  `free_space`, `bind`, `webbox`, `webbox_linux`, `linux_host`,
  `linux_config`, `host_io_std`.
- **Where "gopher-metal" appears:**

  | repo | files | lines | what |
  |---|---|---|---|
  | gopher-metal | 78 | 179 | its own name, paths, strings |
  | metal-vmm | 53 | 578 | mostly QUEUE and FEEDBACK history; a handful of scripts |
  | angry-gopher | 50 | 131 | README's "Where it runs", docs, comments |
  | essay-repl-server | 55 | 242 | essays (history) |
  | zig-coverage-sdk | 6 | 13 | mentions |
  | dog-park | 4 | 4 | mentions |

  Plus 24 memory files, my CLAUDE.md, and `~/build/gopher-metal`, where
  every build, verdict and image lives.
- **Nothing on prod's data volume carries the name.**
  `gopher-metal.conf` is on the boot disk, which every release rebuilds.
  So the kernel and the image builder can change together in one release.
- **`git filter-repo` isn't installed.** Git's own `filter-branch` can do
  the history extraction instead, which avoids a new dependency.

## Before starting

- **The gates on 189 pass,** so 189 has landed. They're running now.
- **CC is told, in FEEDBACK:** the queue pauses, its branch will need
  to follow the moves, and the new paths are given.

## Part 1: zig-webbox

1. **The new repo, with history.** A clone of angry-gopher, filtered to
   the 24 files' history, with each moved from `zig-server/src/` to
   `src/`. Then add `build.zig` and `build.zig.zon`, whose package name
   stays `webbox`, so `@import("webbox")` changes nowhere. Also a short
   README with a status table, and its tests running on their own
   (`zig build test`).
2. **angry-gopher:** delete the 24 files. `zig-server/build.zig.zon`
   depends on `../../zig-webbox` by path, and `build.zig` takes the
   `webbox`, `webbox_linux` and `host_io` modules from it. Checks:
   `ops/check_zig`, `ops/check_chat`.
3. **dog-park:** `build.zig.zon` points at `../zig-webbox` instead of
   `../angry-gopher/zig-server`. Check: `zig build test`, and the
   agreement test.
4. **gopher-metal:**
   - `build.zig` takes webbox from `-Dwebbox-root` (default
     `../zig-webbox`), and each app from its own root as now.
   - `host_io_metal.zig` stays: it is the unikernel's half of `host_io`.
   - `tools/verdicts.py`'s content id gains zig-webbox's files, a third
     named repo.
   - `judge_dogpark`'s "one webbox on both sides" check points at
     zig-webbox.
   - Checks: `zig build test`, both kernels, then the full gates.
5. **metal-vmm:** `check-cc.sh` and `plants.sh` learn the new paths.

## Part 2: gopher-metal becomes zig-metal-unikernel

1. **GitHub:** rename the repo. GitHub redirects the old URL, so old links
   and clones keep working.
2. **On the box:**
   - move `~/showell_repos/gopher-metal` to `zig-metal-unikernel`, and
     the worktrees' paths with it;
   - move `~/build/gopher-metal` to `~/build/zig-metal-unikernel`. Old
     verdicts lapse anyway, since the paths are in the content id.
3. **Code and current docs:**
   - the README and docs, where they name the repo;
   - scripts' paths, in this repo and in metal-vmm and angry-gopher;
   - the strings a person or a judge reads:
     - the boot log and `/admin/host` ("host gopher-metal, with no
       operating system");
     - the loader's banner ("gopher-metal loader"), which the judge
       requires, so the two change in one commit;
     - `gopher-metal.conf`, which is renamed and changes with the image
       builder in one release.
4. **Current text, not history.** Dated QUEUE and FEEDBACK entries,
   archives, review notes and essays describe the past under its name
   then; they stay as written. A sweep for live references (scripts,
   READMEs, status tables) is the part I'd hand to a local helper,
   checked by a grep afterwards that finds no old name outside history.
5. **Memory and CLAUDE.md** follow last, so they describe what exists.

## Then

- **The full gates and the long tier** on the renamed trees.
- **An image** under its new name, for v30 whenever you say.
- **A final pass over the docs,** by me or a local helper, plus a check
  that every README's status table is current. gopher-metal's is already
  behind.

## Your calls

1. **zig-webbox public or private?** Today's repos are public, I believe;
   I'd match.
2. **Keep the 24 files' history in zig-webbox?** I'd keep it: `git log`
   on a library file is how we answer "why is it like this".
3. **The GitHub renames and the new repo:** I can do them with `gh`, or
   you can. They're outward-facing, so I'll wait for a yes either way.
4. **The release image's name.** `gopher-metal-chat-v30.img` would
   become what? I'd suggest `angry-gopher-v30.img.gz`: the app, built on
   the unikernel.
5. **History stays as written:** dated entries, archives and essays keep
   the old name?
6. **Only the 24 move.** Some app files are library-shaped
   (`login_throttle`, `uid_cookie`, `markdown`, `ustar`). By "abstraction
   earns its keep on the second user", they stay in angry-gopher until
   Dog Park or another app needs them.
