# Gopher as a platform: what Dog Park needs, and the order to free it

*2026-10-11. A proposal before any Dog Park code. Two read-only surveys
mapped what a second application would need from angry-gopher and from
gopher-metal, and I checked the claims that matter most against the code.*

## The short version

Nothing a second application needs is hard to separate. The trouble is
*where* things sit, not how tangled they are:

- **In angry-gopher, the platform lives inside the application's router.**
  `router.zig`'s `route` holds about 120 lines of the subtlest serving code
  on the box:
  - the writer that knows whether a byte went out;
  - `settle`, which drops a kept stream on an error;
  - the 500 that says nothing;
  - the malformed-form 400.

  Only `routed` (the route table) and `viewer` are actually the application.
  Startup (`host_start.zig`) interleaves chat's steps with generic ones. A
  second application would have to copy all of that, and the copy would
  drift within a week.
- **In gopher-metal, the kernel is about 90% generic already.** It reaches
  angry-gopher only through about a dozen `router.*` names, plus five
  app-specific bits:
  - the `data`/`auth` folders;
  - the admin password reset;
  - the boot report on chat backfill and search;
  - chat's 10 MiB upload cap, used as the page-cache default;
  - "chat" in a few labels.

  The real obstacle is the build. gopher-metal *pulls* angry-gopher:
  - a shell script copies one folder;
  - a regex scrapes angry-gopher's asset table into a file gopher-metal tracks;
  - `build()` runs git and stamps verdicts for anyone who depends on it.

So the work is mostly moving code and setting up contracts, with tests
proving behaviour doesn't change. Very little is new code.

## The end state

Three kinds of repo, with dependencies pointing one way:

- **`gopher`, the library.** Serving requests, streams and SSE, the store,
  signed cookies and the session secret, the Linux host, the app contract.
  Each of these is one copy, held in by a lint.
- **gopher-metal, the service.** It exports `addAppKernel` and
  `addDropletImage`. An application's `build.zig` asks for a kernel and an
  image built from *its* sources and *its* asset list.
- **Applications:** dog-park first, angry-gopher eventually. Each one is
  routes, pages, JS and a `build.zig` that pulls from the other two.

**Recommendation: carve the library inside angry-gopher first, and lift it
into its own repo later.** In place, every move is checked by angry-gopher's
2,700 unit tests and the metal gates as they stand. Lifting it out is then a
directory move, not a redesign. This morning's first step already works that
way: angry-gopher's server is a package exporting `gopher`, with `http`,
`edge` and `signed`, and a lint fails any library file that imports
something the library doesn't name.

## The order

**Phase A: angry-gopher, no behaviour change.** Each step stands alone,
checked by angry-gopher's tests, then gopher-metal's `zig build check`, then
the gates.

1. **The pieces that already import only std move into the library:**
   - `bus.zig`, the Hub, Bus, held and kept streams;
   - the memory meter (`mem_meter`), host facts (`host_status`), `html`, `bind`.

   The portability lint also widens to cover the library, not only what the
   router reaches.
2. **The store and its counter.** `store.zig` reaches `roots` only in two
   tests (checked); those tests stop doing that.
3. **The app contract.** `gopher.App(Site)` generates `start`, `route` and
   the names the kernel uses, wrapping the serving machinery around the
   application's own handler.
   - `host_start` keeps only chat's startup steps.
   - The client address and the free-space floor move out of `game_limits`.
   - gopher-metal doesn't change, because the names are the same.
4. **The Linux host becomes a library module.** `server.zig` shrinks to
   about ten lines.
5. **Identity.** `secret.zig` takes the session secret's load, the previous
   secret and rotation. A device-cookie module takes resolve, header, renewal
   and the previous-secret fallback. `uid_cookie` keeps only Lyn Rummy's
   policy, such as the legacy unsigned window.
6. **SSE.** `chat_sse`'s generic halves (`forwardUserStream`, `sinceFrom`)
   move out; `streamTranscript` stays chat's.

**Dog Park can start on Linux after step 5:** Alice alone, with files and
cookies. **Its SSE needs step 6.**

**Phase B: gopher-metal as a service.**

1. **The kernel imports `app` and `gopher`, not `router.zig`.** The five
   angry-gopher bits become hooks the application supplies.
2. **The port becomes a build step.** A small Zig tool, run by the build
   over any source folder. port.sh calls the same tool. The tool also
   refuses a `std.Io.Dir` that slips past the alias swap; today one would
   escape silently.
3. **Assets are an input.** `gen/assets.zig` and the regex reader go away.
4. **Export `addAppKernel` and `addDropletImage`.** `build()` stops having
   side effects for dependents. The image builder stops borrowing the
   judge's internals.

Then dog-park's `build.zig` gets a `metal` step. **Later:** a generic "judge
my app on metal against my app on Linux", and angry-gopher builds the same
way dog-park does.

## Cleanup notes, found along the way

None of these blocks anything. Each is small, and most fall out of the
phase that touches the file.

- **Two redirect sanitizers.** `router.localTarget` is a weaker copy of
  `http.internalTarget`: it misses a backslash or control character after
  the second byte. It stays on the same site either way, but it should call
  the one rule.
- **Two HMAC cookie schemes.** `gopher_auth` has its own; it could be a
  `signed.Kind` like `gopher_uid`.
- **Two per-address hourly tables:** `game_limits` and `login_throttle`.
- **A duplicated bound:** `game_limits.id_max = 24` restates `player.isSafeID`.
- **`nowUnix`, written out 29 times in 12 files.**
- **Unused imports:** `server.zig` imports `chat_store`, `config.zig` imports
  `users`.
- **The README is wrong about the secret:** it says to seed it in
  `data/chat`, and the code reads `auth/`.
- **The library lint can't see `@import("build_options")`.**
- **gopher-metal:**
  - "chat" in `/admin/host` labels;
  - `chat.py` borrowing the judge's disk helpers;
  - angry-gopher data tracked in `gen/assets.zig`;
  - git and verdict stamping at configure time.

## What I'd like from you

Two calls:
1. **Carve in place, then lift out.** Is that right, or do you want the
   `gopher` repo now?
2. **Phase A, in order, starting now.** Each step is committed and checked
   on its own, and nothing ships until the gates say so.

The Dog Park code waits for step 5.
