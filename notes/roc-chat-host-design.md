# roc-chat's host, from first principles

*For Steve, and for the agents who will build it. Box, 2026-10-29. It's a design plus three probes; no repo was changed.*

**Read for this:**
- the essay notes `roc-chat-standalone`, `pure-roc-chat-plan`, `roc-chat-leaves-the-nest` and `roc-chat-auth-design`;
- roc-webbox `main` 5a4314b (`chat/platform/*`, `src/chat_abi.zig`, `src/chat_hosted.zig`, `build.zig`), and `box/auth` 4285218 for the auth core's needs;
- angry-gopher-chat `box/roc-cleanup` da2ed780 (`chat_router.zig`);
- zig-webbox `src/`.

**The probes** are in `scratchpad/probe_{a,b,c}`. Each has a `build.zig` and was built with **stock Zig 0.17.0**.

## The short version

- **The host is about 1,900 Zig lines** outside tests. The chat reaches about 7,450 today. It has eight parts and one seam, the seam copied whole from roc-webbox.
- **`std.http.Server` is a per-connection protocol object, not a server.**
  - `init(reader, writer)`, then `receiveHead` and `respond`/`respondStreaming` in a loop.
  - Concurrency is ours: one `std.Io` task per connection (`Io.Group.concurrent` on the default, threaded Io), and a `std.Io.Mutex` as the turn.
  - That is webbox's model, and probe (a) shows it works at 0.17 from about 200 lines.
- **The hosted functions go from 49 to 29 for v1:**
  - 23 kept;
  - 14 retired;
  - 12 deferred to later;
  - 6 new for auth.

  Two changes are to the seam's records, not hosted functions: an answer carries headers (`Set-Cookie`), and a GitHub sign-in can be a two-call continuation.
- **All three probes passed.**
  - (a) A held SSE stream and concurrent POSTs. The turn holds one handler at a time. Backlog and live have no gap and no duplicate.
  - (b) TLS to api.github.com with the system CA bundle: 606 ms the first time, 9 ms on the pooled connection after.
  - (c) The chat's Roc archive called from a new host outside roc-webbox, through `Host.partly`: 28 µs a decision. `Host.of` on a partial stub fails the build and names the first missing function.

## 1. The hosted functions

Today: the 49 in `chat/platform/main.roc`. "Retire" means the function leaves the platform, and the Roc either does the work through other primitives or the feature goes. "Later" means not in v1; it comes back when the feature does, unchanged unless noted.

| hosted function | v1 | why |
|---|---|---|
| `read!` | keep | file primitive |
| `read_at!` | keep | a cache's read; a transcript's tail |
| `read_stat!` | keep | the torn-line rule, cache staleness |
| `list!` | keep | folders (conversations, topics, sessions, keys) |
| `write!` | keep | **atomic** (tmp + fsync + rename + dir fsync) |
| `append!` | keep | transcripts, feeds, **the audit log** (fsynced) |
| `remove!` | keep | a session revoked, a key revoked |
| `write_cache!` | keep | the `.count` cache; later it could be `write!` inside an aside |
| `publish!` | keep | the bus |
| `read_body!` | keep | **reshape:** the Roc passes the byte limit, not a form tag (plan §1) |
| `read_header!` | keep | the Roc now reads `cookie` and `authorization` itself |
| `read_query!` | keep | |
| `read_time!` | keep | the clock; the request's one time |
| `mark_aside!` | keep | STORED IS DONE |
| `name_fault!` | keep | |
| `fail!` | keep | **reshape:** `KindUnreadable`, `NameUnreadable` and `NotAUid` go with `list_accounts!` |
| `count!` | keep | operator counters, in a table in memory |
| `serve_script!` | keep | chat-client's bundles |
| `list_srcs!` | keep | the bundles' hashed names |
| `serve_file!` | keep | a transcript served whole, held by the host |
| `count_presence!` | keep | process-lifetime state, ~50 host lines |
| `presence_unspent!` | keep | |
| `check_online!` | keep | |
| `render!` | retire | roc-markdown renders |
| `render_preview!` | retire | roc-markdown |
| `check_hostile!` | retire | roc-markdown's budget; the Roc answers the 400 and `count!`s it |
| `serve_rendered!` | retire | the Roc renders a doc and answers its bytes |
| `identify!` | retire | the old auth; the Roc reads the cookie or Bearer token, `hash!`es it, and looks it up |
| `read_uid!` | retire | the Roc knows its principal |
| `list_accounts!` | retire | angry-gopher's Zig user table; accounts are the Roc's files (AccountCodec) |
| `check_welcome!` | retire | gopher's users folder; a Roc file if wanted |
| `clear_welcome!` | retire | the same |
| `retire_asked!` | retire | the Zig-era admin retire; the auth core's retirement plan runs on file primitives |
| `retire_note!` | retire | the same |
| `retire_remove!` | retire | the same |
| `retire_replace!` | retire | the same |
| `retire_user!` | retire | the same |
| `admit!` | later | search's rate limit |
| `search_scope_add!` | later | search |
| `search_words!` | later | search: the index is ~250 lines of state plus the tokens |
| `search_messages!` | later | search |
| `index_message!` | later | search |
| `read_upload!` | later | uploads: multipart, sniffing, slots (~500 host lines) |
| `refuse_upload!` | later | uploads |
| `reserve_upload!` | later | uploads |
| `store_upload!` | later | uploads |
| `serve_upload!` | later | uploads (range serving) |
| `bundle_add!` | later | the tar.gz download; `ustar` could move to Roc (plan item 10) |
| `serve_bundle!` | later | the download |
| **`random_bytes!`** `U64 => List(U8)` | new | nonces, session secrets, key secrets (`io.random`) |
| **`hash!`** `List(U8) => List(U8)` | new | SHA-256 (32 bytes, `Stored.SecretHash`) of a cookie secret or an API key |
| **`sign!`** `List(U8) => List(U8)` | new | HMAC-SHA256 with the site key: the OAuth state, the pending sign-up |
| **`verify!`** `List(U8), List(U8) => [Valid, Invalid]` | new | the same MAC, compared in constant time in the host |
| **`github_identify!`** `List(U8) => { id : U64, login : List(U8), status : [Known, Refused, Failed] }` | new | code → token (POST, with the client secret) → `GET /user` → the id and login; the token is discarded |
| **`read_config!`** `[Origin, GitHubClientId, BootstrapAdmin] => List(U8)` | new | public settings the Roc needs for the authorize URL and the first admin; never a secret |

**Counts:**
- **v1:** 23 kept and 6 new, so **29**.
- **Retired:** 14.
- **Later:** 12.
- **New later:**
  - `verify_webhook!(bot, body, signature)`, for bots (GitHub's `X-Hub-Signature-256`);
  - an opaque `read_stored!`, which §13's "stored bytes came from the store" asks for.

**Not new, on purpose:**
- **Session and key stores, the audit log, the spent-nonce set:** all are files through `read!`, `write!`, `append!` and `list!`.
  - A key or session is looked up by a file named for the hex of its hash, so there's no compare to time.
  - **Check-then-set is atomic because of the turn.** One handler runs at a time, so "is this nonce spent? then spend it" needs no exclusive-create primitive.
  - This depends on the turn. If the turn ever goes, these need `create_new!`.

**Seam changes that aren't hosted functions:**
1. **`Answer` gains `headers : List({ name : List(U8), value : List(U8) })`.** It's needed for `Set-Cookie` on sign-in and sign-out.
   - The host refuses CR or LF, and any name not on its short list (`set-cookie`, `cache-control`, `location`), as a 500 and the Roc's bug.
   - The cookie's attributes (`__Host-`, Secure, HttpOnly, SameSite=Lax) stay the Roc's policy, written once in its Session module.
2. **The GitHub exchange off the turn (decision D1).** The Roc's callback route answers a new decision, `exchange { code, then }`.
   - The host runs `github_identify` on the connection's own task, outside the turn.
   - It then calls `handle!` again with `Request.exchanged = Known({id, login}) | Refused | Failed` and the route's `then`.
   - With this, `github_identify!` is not a hosted function but a step between two Roc calls. The table lists it for the simple variant, which is the exchange inside the turn.
3. **The areas `/chat` and `/channel`** become one root on chat.lynrummy.com (decision D6).

## 2. The host's parts

Sizes are non-test Zig lines, estimated from webbox's code and the probes.

| part | lines | crib | leave behind |
|---|---:|---|---|
| **`main.zig` and `config.zig`** | 120 | linux_config.zig's shape; `portFrom` (port refused unless 1-65535) | the facts, mem_meter, free_space, the between thread, `Options`/`Env` indirection |
| **`server.zig`**: the accept loop, a task per connection, keep-alive, the turn, timeouts | 400 | linux_host.zig: `handleConn`/`serveOne`, `takeTurn` (a `std.Io.Mutex`), the 503 when no task can start, the head deadline (Io.Select race against a watch, or `SO_RCVTIMEO`), idle timeout, `requests_most`, `kept_open_most`; linux_reads.zig: the body read whole *before* the turn, to a limit and a deadline | HeadWatch (we decide keep-alive ourselves before `respond`); Hold/Sent (the answer is copied out of the Roc and written after the turn anyway); upload slots and the small-body budget; between/ring; durable roots |
| **`call.zig`**: the request and response bridge to the seam | 450 | chat_router.zig: `handle` (a decision → a response: `respond`, `redirect`, `found`, `to_login`, `not_found`, `not_allowed`, `stream`, `held`, `answered`), `Call` (`fail`, `dead`, `mark_aside`, the 29 answers); `useRequest`; "one answer, and only one" | everything gopher: users.zig, `toLogin`'s `/login/full`, chrome, search, upload, download, retire, `operator_counts` (it becomes a small table) |
| **`seam/`**: `chat_abi.zig`, `chat_route.zig`, `roc_abi.zig`, `sljmp.zig` | ~1,900 today; ~1,300 after the retirements | **moved whole** from roc-webbox (std only); `Host.of` and the comptime check stay | the `Table` rows that retire, `Area.retire`, the twin |
| **`bus.zig` and `sse.zig`** | 200 | bus.zig: `Subscriber` (ring, `missed`, futex `seq`), `Hub`, `serveKeptCounted`, and the seeded mailbox simulator test; sse.zig: `respond`, `push` (both flushes), `ping`; linux_streams.zig whole (the 64-stream cap, the oldest ended); linux_writes.zig's `WriteWatch` (a stalled reader's socket shut) | `Kept.render`/`ctx` (frames are rendered once by the Roc, so they go out verbatim); `Bus.peer`/`status`; `nextFrame` (metal's); `forward`/`resumeAt` (the Roc's now) |
| **`files.zig`**: the store | 200 | store.zig: `replace` (a sibling temp, then rename), `createNew`, `append` (positional at the end, giving the size after), `list`, `readAt`; the seam's path check (`underRoot`, `onePart`) | FAT names, case-folding `resolve`/`retry`, `max_depth`, `changes`/`durable_now` (we fsync per write: decision D5) |
| **`auth.zig`**: the primitives | 120 | site_secret.zig's create-once, 0600 key file (`createNew`); signed.zig's HMAC use | signed_cookie.zig (sessions are random ids now), the legacy cookie names, visitor ids |
| **`github.zig`**: outbound HTTPS | 150 | nothing: std.http.Client, as in probe (b); std.json for `{id, login}` | linux_fetch.zig and host_fetch.zig (plain HTTP, metal's) |
| **`assets.zig`**: static files | 60 | http.zig `serveEmbedded` (the hash as the ETag, 304, cache rule) over chat-client's `bundles.zig` | `hashedSrc`'s gopher paths |
| **`presence.zig` and `counters.zig`** | 90 | gopher presence.zig (41), operator_counts' table | |
| **total, outside `seam/`** | **~1,800** | | |

**What's left of webbox's 9,400 lines, and why:**
- **Gone:** the site/route-table abstraction (site.zig), combos, edge/traffic/log_view, mem_meter, host_facts, linux_durable's roots, and the between thread. The Roc is the router; there's no background work in v1.
- **Kept, in ~600 lines:** the turn, the deadlines, the stream cap, the mailbox, and atomic writes. Those are the rules webbox paid for.

**The five semantics the Roc relies on, and where each lives:**

| semantic | home |
|---|---|
| one handler at a time | `server.zig`'s turn: the whole Roc call, and only it, under the mutex |
| resume | the Roc (`resumeAt`'s twin); the host passes `Last-Event-ID` through `read_header!` |
| no silent gaps | `Subscriber.missed` ends the stream, so the browser resumes; the subscribe and the backlog read happen in one turn (probe (a)) |
| frames rendered once | published bytes go out verbatim |
| keepalive and a stream cap | `serveKept`'s futex timeout (25 s, an environment setting for tests); `linux_streams`' 64 |

## 3. Repo layout

```
roc-chat/                     Linux x86-64 only; stock Zig 0.17.0; the pinned Roc nightly
  build.zig  build.zig.zon    deps: chat_client and roc_markdown (URL + hash); no zig-webbox
  roc-version  tools/get_roc.sh
  app/        main.roc and the chat's modules, the auth core's among them (from box/auth)
  platform/   main.roc  Chat.roc  Host.roc
  host/       main.zig config.zig server.zig call.zig bus.zig sse.zig files.zig
              auth.zig github.zig assets.zig presence.zig counters.zig
  host/seam/  chat_abi.zig chat_route.zig roc_abi.zig sljmp.zig   (moved from roc-webbox)
  test/       e2e.zig (the server in-process on port 0, a fake GitHub on another port,
              clients by std.http.Client); glue_test.zig; crash_test.zig
  deploy/     Caddyfile snippet, roc-chat.service, the config example
  LICENSE  README.md  docs/roc-style.md
```

**The build:**
- **`zig build`:**
  - checks Roc against `roc-version`, a fatal error naming `get_roc.sh` (crib roc-webbox's `rocCompiler`);
  - runs `roc build app/main.roc --target=x64musl` (dev in Debug, speed in release);
  - links the archive into `zig-out/bin/roc-chat`.
- **A non-Linux or non-x86-64 target fails at configure.**
- **`zig build test`:** `roc test`, the host's unit tests, the glue and crash tests, and e2e. One command runs every test.
- **`zig build serve`:** runs it against `./data` with `./config.zon`.

**Dependencies:**
- **chat_client** is already a Zig package with the module `chat_client`: a zon entry, `@import("chat_client")`. Done.
- **roc_markdown** is a zon dependency too (a tarball by hash). The Roc header names a *path*, so the build lays out a generated tree: `b.addWriteFiles()` copies `app/`, `platform/` and the dependency's `package/` side by side, and `roc build` runs there. The header names `md: "../roc-markdown/main.roc"`. One home, fetched by hash, nothing written into the checkout. The cost is that Roc's errors name the generated path. **Decision D2.**
- **Roc** is pinned by `roc-version`, installed by `get_roc.sh`, and found on PATH. A forker needs stock Zig and that Roc, nothing else.

**One home for the seam.** Once roc-chat exists, roc-webbox's `chat/` and `src/chat_*` are a second copy. Freeze them, and delete them once the interop branch retires, or the seam drifts.

## 4. Build order

The smallest end-to-end comes first, then breadth. Every step has its test, and each step is one commit.

1. **Skeleton.**
   - *Build:* the repo, the pin check, the seam moved, a three-route stub app, `serve`.
   - *Test:* `zig build test` green from a fresh clone with stock 0.17.0 and an empty cache. The glue test holds every remaining record.
2. **Server core.**
   - *Build:* the loop, the turn, keep-alive, deadlines, assets.
   - *Test (e2e):*
     - `GET /chat.js` is a 200 with its ETag, then a 304;
     - a head sent a byte at a time gets a 408;
     - an idle kept-open connection is closed at its timeout;
     - two pipelined requests are answered in order;
     - a body over the limit is a 413 that never enters the turn;
     - "most handlers in the turn at once" is 1 under 50 parallel clients (probe (a)'s counter).
3. **Bus and SSE.**
   - *Test (e2e):*
     - a held stream plus concurrent posts arrive in order;
     - **backlog xor live:** a test hook sleeps between the Roc's read and the subscribe while another client posts, and the message must appear exactly once;
     - 17 publishes to a stalled reader end its stream;
     - a ping arrives at the configured keepalive;
     - the 65th stream ends the oldest;
     - a reader that stops reading is shut after the write deadline.
     - Plus webbox's mailbox simulator.
4. **Files.**
   - *Test:*
     - `write!` is atomic: kill the process between the temp file and the rename (a test hook), and the old file is whole;
     - `append!` gives the size after;
     - `..`, absolute and empty paths are refused;
     - **missing and failed differ** (a 000-mode folder);
     - an fsync failure fails the request.
5. **Auth primitives and the fake GitHub.**
   - *Test:*
     - the RFC 4231 HMAC vectors and the NIST SHA-256 vectors;
     - `verify!` refuses a one-bit flip;
     - the site key is created once, 0600, and a second start reads the same key;
     - `github_identify` against a fake GitHub (in-process; its base URL in the config): success, a 401, a slow answer past the deadline, a malformed JSON body;
     - an opt-in smoke test (`zig build smoke`) does the real `api.github.com/zen`.
6. **The smallest end-to-end.**
   - *Build:* the Roc app reduced to sign-in, post, read and stream, on the auth core.
   - *Test:* one e2e script with two clients:
     1. `/login` redirects to the fake GitHub's authorize URL with a signed state;
     2. the callback with a code reaches the display-name form, then a session cookie (`__Host-`, Secure, HttpOnly);
     3. client A posts a message;
     4. client A reads the transcript and sees it;
     5. client B, already streaming, gets the frame live;
     6. a replayed state and a forged cookie are refused.
7. **API keys.**
   - *Test:* mint a key from a session, post with `Authorization: Bearer`, and see the key refused once revoked or expired. A key can't mint a key.
8. **Breadth.**
   - *Build:* the rest of `chat/*.roc` from roc-webbox, with the retired functions replaced; presence; admin and the audit log; operator counters.
   - *Test:* each route's own e2e case, `roc test`'s exhaustive `can_see` table, and an audit line for every admin action.
9. **Deploy.**
   - *Build:* chat.lynrummy.com behind Caddy on prod, and the systemd unit.
   - *Test:* the e2e suite pointed at the live origin (read-only cases), and **an adversarial pass** whose brief is "get into a conversation you can't see, or post as someone you aren't".
10. **Later:** search, uploads, the download, bots and webhooks, each bringing back its hosted functions.

## 5. Risks

- **The turn and the network.**
  - In the simple variant, `github_identify` holds the turn: 0.6 s at best (probe (b)), unbounded at worst.
  - **std.http.Client has no timeouts.** Race the fetch against a deadline (`Io.Select`, as webbox races the head read) in either variant.
  - Decision D1 moves the exchange off the turn.
- **The head's strings point into the read buffer.** Reading the body overwrote `req.head.target`: probe (a)'s first run sent every POST to the 404. Copy the target and the headers the Roc needs before reading the body.
  - `read_header!` then answers from the copy. The probe does this for the target; the real host must do it for every header it hands to the Roc.
- **Bytes handed to a hosted function belong to the call.** Probe (c)'s stub kept the script name past the call and printed garbage (`UUUUUUU`). A host must copy anything it keeps (`count!`'s text, a published frame).
- **Threads per stream.** Each held SSE stream holds a task on the threaded pool. The stream cap (64) and the kept-open cap (64) bound it at about 130 threads, which is fine for a family and agents. Raising either is a measured change.
- **The weak hosted symbols.** A missing export jumps to address 0. The glue test and `Host.of`'s compile check must travel with the seam (probe (c) shows the check firing).
- **Durability.** Per-write fsync is simple and correct, but slower than webbox's single sync before the response. Measure it at step 4; at chat volumes it should be invisible.
- **Roc nightly churn** across roc-chat and roc-markdown: one pin, moved together.
- **The Zig-era `Retire.roc` must not ship in roc-chat** (auth design §13).
- **Licences:** none of roc-webbox, chat-client or roc-markdown has one, and a forkable repo needs them.

## 6. Decisions for Steve

- **D1. The GitHub exchange:** inside the turn with a deadline (simple; a sign-in stalls everyone for up to the deadline), or **off the turn as a two-call continuation** (~60 more lines and a field on `Request`)? The lean is off the turn.
- **D2. Fetching roc-markdown:** a zon tarball laid out in a generated tree (lean), a git submodule, or Roc's own URL packages (needs a probe at the pin)?
- **D3. Cookies:** `Answer.headers` with a short allowed list (lean), or a `set_cookie!` hosted function whose attributes are fixed by the host?
- **D4. v1's scope:** presence in, with search, uploads, download and bots later, as above?
- **D5. Durability:** fsync per write (lean), or crib linux_durable's sync before each response?
- **D6. URLs:** the chat at `/` on chat.lynrummy.com, dropping the `/chat` and `/channel` areas?
- **D7. Config:** one `config.zon` at a fixed path beside the data root (origin, port, data root, the secrets' paths, the GitHub client id, the bootstrap admin), with no CLI arguments; or environment variables?
- **D8. The seam's one home:** moving it to roc-chat freezes roc-webbox's chat copy. When does roc-webbox's `chat/` go?
- **D9. Licences** for roc-chat and its dependencies.

## Appendix: the probes

All three were built with `~/zig-0.17.0/zig build`, and live under the scratchpad.

**(a) `probe_a/`: std.http.Server, the turn and SSE.** About 200 lines: one task per connection, keep-alive, the turn, and the bus.
- *The run:*
  - one post before any stream;
  - two `curl -N /events` held open;
  - a `/slow` request that holds the turn for 300 ms;
  - two posts.
- *What happened:*
  - both streams got `id: 0 before`, `id: 1 a` and `id: 2 b`, then `: ping` every second;
  - the first post waited 322 ms behind `/slow`, and the second took 10 ms;
  - "most handlers in the turn at once" was 1.
- *The answer:* the std server supports this model with no help, given a task per connection. The threads come from `std.Io`'s pool, not from the server.

**(b) `probe_b/`: std.http.Client and TLS.**
- `GET https://api.github.com/zen` was a 200 in 606 ms, which includes the CA bundle scan of `/etc/ssl/certs` and the handshake.
- The second request on the same client was a 200 in 9 ms.
- A form POST to `github.com/login/oauth/access_token` was a 404 with JSON, because of the bogus client id; the TLS POST path itself works.
- GitHub needs a `User-Agent`.

**(c) `probe_c/`: the Roc archive from a new host.**
- `roc build chat/main.roc --target=x64musl --opt=dev` wrote its output to scratch in 1.7 s.
- A scratch `build.zig` imports roc-webbox's `src/chat_hosted.zig` by absolute path and links the archive. Its own stub types use `Host.partly`.
- *What it answered:*
  - a stranger asking for `/c/1_2/general` gets a 303 to sign-in, after one identify;
  - `/chat.js` is answered by the host;
  - a non-UTF-8 path is a malformed form;
  - each decision takes 28 µs.
- `-Dwhole_stub=true` (`Host.of` on the partial stub) fails the build with: `main.Stranger answers no count_presence (a pub fn count_presence, as Host.roc names it)`.
- roc-webbox's working tree was unchanged afterwards.
- **Seen in passing:** roc-markdown had an uncommitted `<p>`→`<q>` edit to `package/Md.roc`, made 20 s before I looked and after my archive build. It looks like another agent's planted mutation. It isn't mine, and I didn't touch it.
