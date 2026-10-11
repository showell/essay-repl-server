# A web server in a box: what Dog Park needs, and the order to free it

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

**The library is called `webbox`** ("web server in a box"): no "gopher" in
anything Dog Park sees (Steve, 2026-10-11). angry-gopher keeps its name, and
gopher-metal may become something like zig-droplet-unikernel. Three roles,
with dependencies pointing one way:

- **`webbox`, the library.** Serving requests, streams and SSE, the store,
  signed cookies and the session secret, the Linux host, the app contract.
  Each of these is one copy, held in by a lint.
- **gopher-metal, the service.** It exports `addAppKernel` and
  `addDropletImage`. An application's `build.zig` asks for a kernel and an
  image built from *its* sources and *its* asset list.
- **Applications:** dog-park first, angry-gopher eventually. Each one is
  routes, pages, JS and a `build.zig` that pulls from the other two.

**`webbox` is carved in place, inside angry-gopher's server** (`webbox.zig`
names its files). Lifting it into its own repo is a long way off (Steve). In
place, every move is checked by angry-gopher's 2,700 unit tests and the metal
gates as they stand. This morning's first step already works that way:
angry-gopher's server is a package exporting `webbox`, with `http`, `edge`
and `signed`, and a lint fails any library file that imports something
`webbox.zig` doesn't name.

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
3. **The app contract.** `webbox.App(Site)` generates `start`, `route` and
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

1. **The kernel imports `app` and `webbox`, not `router.zig`.** The five
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

## Phase A, as it goes

**Step 1 (angry-gopher `225f0e15`).** Joined the library: `html`, `bus`,
`mem_meter`, and `host_status`, renamed `host_facts`, the name the router
already exported it by. The portability lint checks from two roots, the route
table and `webbox.zig`, so a library file the site never reaches must still
port.

**Step 2 (`ad52ccd7`).** Joined the library: `store` and `counter`.
- The store's tests stop borrowing the app's `roots`; it has its own
  `saveBases`.
- Its prose says what it promises any application. Angry-gopher's folder
  inventory (how far each folder can grow against FAT's limit) moved whole
  to `roots.zig`.

**Step 2b, the library reads as a library.** A cold review of
step 1 found no behaviour change, but found two other problems:
- **The library's prose still named chat, routes, ops scripts and
  gopher-metal.** A prose-only pass moves each such sentence to the app file
  that owns it.
- **The lints had blind spots:**
  - an import split over lines (a form `zig fmt` keeps);
  - a `"http://"` string hiding the rest of its line;
  - a `'{'` character literal holding a test block open, so the code after
    it went unchecked.

  Both lints now read source through one shared reader, `tools/zig_source.py`.
  Each blind spot has a test that fails against the old lint. The library lint
  also refuses `@embedFile`, because what a page serves is the application's.

**Step 2b (`a30bcf38`).** Done as described above. With comments
stripped, the 17 changed files are byte-identical to before.

### Step 3, the app contract: the design, before any code

**Terms.** A *host* is what owns the machine: Linux's `server.zig`, or
gopher-metal's kernel. An *application* is what a site serves: angry-gopher's
route table, or Dog Park's. A **site** is an application made servable:
`webbox.Site(App)` generates everything a host calls, around the
application's own handler. A host never names the application's modules.

**What an application provides** (a Zig type with these declarations, all
required, so no default is a decision nobody made):
- `handle(req, io, alloc, bus) !void`: its route table. Today this is
  `router.routed`, prelude included (the client's address, the cookie
  re-sign).
- `setup(io, base, dirs: ?Dirs) !Setup`: its one-time steps, in its own
  order. For angry-gopher that's the roots, the secret's move, the backfill
  and search's index.
- `Setup`: what those steps did, for the host's log.

**What `Site(App)` gives a host:**
- `route(req, io, alloc, bus) !?Kept`. The serving machinery moves here
  unchanged from `router.zig`: the writer that knows whether a byte went
  out, `settle`, the 500 that names nothing, and the malformed-form 400.
- `start(io, Host) !Started`. In today's exact order:
  1. the store's bases;
  2. `App.setup`;
  3. the host's facts and log;
  4. the free space and the trusted proxy;
  5. the Hub.

  `Started` is `{ hub, app: App.Setup }`.
- `Host` stays the same struct, with `roots` renamed `dirs` (a `Dirs` is
  `{ data_dir, auth_dir }`, today's `Roots`).

**What moves into the library on the way** (step 3a, before the contract):
- **`client.zig`:** `trusted_proxy`, `clientAddress` and
  `plausibleAddress`, out of `game_limits`. Which address a request comes
  from is a fact about the connection and the proxy in front, not a game
  rule.
- **`disk_space.zig`:** `Space` and the host's `free_space` reading, out of
  `game_limits`. The quarter-free floor stays `game_limits`' policy.
- **Routing helpers:** `matchPrefix` and `stripQuery`, into `http`.

**The order of commits:**
- **3a:** the moves above.
- **3b:** `Site(App)` and `route`. angry-gopher's `router.zig` becomes its
  route table, plus a `site` it exports under today's names.
- **3c:** `start`'s split.

Each is checked by angry-gopher's tests, gopher-metal's `zig build check`
and the gates.

**What gopher-metal sees:** the same names from `router.zig`, except
`started.backfilled`, `started.search` and `started.search_ms`, which become
`started.app.…`. That's a three-line kernel edit, and the kernel's serial
lines stay the same. Phase B later removes even that: the application will
report its own startup lines.

**Not in step 3, on purpose:**
- **`router.localTarget` to `http.internalTarget`.** It would be stricter
  about backslashes and control characters, which is a behaviour change. It
  comes after Phase A, as its own commit.
- **`edge.RejectKind`'s app kind.** It stays as is; its keys are
  `/version`'s.

**Open decisions, each waiting for the step that owns it:**
- **`edge.RejectKind`** (step 3, the app contract). It mixes generic kinds
  with one of this app's (`malformed_markdown`). Its names are keys in
  `/version`, so renaming would change behaviour. The contract could let an
  application bring its own kinds.
- **`Bus.peer`** (step 3 or 4). Request context (the client's address, for
  the app's per-address limits) riding on the pub/sub handle.
- **The keepalive setting** (step 4, the Linux host). A mutable global, read
  from a `GOPHER_*` variable.
- **Globals in the library.** `host_facts`' report and log, and the memory
  meter's single instance. These are defensible as process singletons, but
  they should be named as such.
- **Names to weigh:** `html.htmlEscape` reads "html" twice (`html.escape`);
  `signed.Kind` might read better as `signed.Scheme`.
- **The other lints** (`lint_store_absence`, `lint_head_access`) still read
  source line by line, and scan only angry-gopher's tree. That's step 8,
  lints for more than one application.

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

One call: **Phase A, in order, starting now.** Each step is committed and
checked on its own, and nothing ships until the gates say so.

The Dog Park code waits for step 5.
