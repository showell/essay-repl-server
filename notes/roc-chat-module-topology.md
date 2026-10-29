# roc-chat's module topology

*2026-10-29. A review of all of roc-chat's Roc as of `main` `97d7808`: 25 modules, about 12,200 lines, half of them expects. The first section reads the code as it is. The second ranks small changes against what people forking the chat will actually change. The third brainstorms the axes along which someone takes most of the app, and what someone might cherry-pick.*

## What is there

| Layer | Modules | Lines (with expects) | Touches the host? |
|---|---|---|---|
| Platform | `Chat` (request and answer), `Host` (effects), `Sse`, `main` | 433 | is the seam |
| App entry | `main.roc`: every route, the sign-in handlers, the store's paths and reads, two stubs | 604 | **every effect the app makes** |
| Sign-in on the wire | `SignInWeb`: tokens, cookies, form, **and two store records** | 331 | no |
| Auth core, generic | `Principal`, `Access`, `ApiKey`, `Session`, `Stored` | about 3,000 | no |
| Auth core, the chat's | `ConvAccess`, `ConvKey` | about 1,800 | no |
| Auth core, sign-in | `GitHubSignIn`, `OAuthState`, `GitHubLogin`, `DisplayName` | about 2,000 | no |
| Auth core, admin | `Admin` | 1,073 | no |
| Codecs | `AccountCodec`, `SessionCodec`, `KeyCodec`, `AuditCodec` | about 2,500 | no |
| Byte helpers | `Ascii`, `Bytes` | 375 | no |

**What's right, and worth keeping on purpose:**
- **The pure/effect split is total.** Every `Host.*` call in the app is in `main.roc`. The 16 core modules decide and never do, so each can be read, tested and replaced without a host.
- **Generic sits under specific.** `Access`, `ApiKey` and `Principal` know nothing of conversations. `ConvAccess` and `ConvKey` are the chat's layer on top. This is the "resources, not conversations" shape you asked for, and it's real in the types: a chat key can't decide on anything but a `ConvAccess.Conv`.
- **One store format, one discipline.** `Stored` is the line format, each record has its own codec, and every codec's decoder is the only door back in.
- **`Sse` already passes the cherry-pick test.** It knows nothing of chat, carries its own example, and needs only `Host.publish!` and `Chat.stream`.

**What's wrong, ranked by how often it would hurt:**

1. **The test cast is written 13 times.** `gid` is defined in 13 modules, `gen` in 12, `aid` in 10, `kid` in 7, `ann` in 7, and `person`, `owned`, `boss`, `accounts`, `session_of` and `token` in 4 to 6 each. They are the same handful of principals, rebuilt in each module's tests. **A change to how a principal is made touches about ten modules.** That's the five-modules smell, already present before a line of chat is ported.
2. **`main.roc` is three things.** It is the route table, the sign-in handlers (about 300 lines), and the store: six paths, `accounts!`, `settings!`, `nonce_use!`, `facts!` and the writes in `signed_in!`. Each of the three changes for a different reason. It will grow into the place every fork has to patch.
3. **`SignInWeb` is a 50% module.** Its header says so: "the settings' record (the generation counter) and the barred ids, which the core's Settings hold and no codec of the core stores." The wire half (tokens, cookies, the form) belongs to sign-in. The record half (`settings_line`, `settings_next`, `barred_line`, `barred`) belongs to the store. A fork moving to SQLite keeps exactly half of it.
4. **The page HTML is inline in handlers.** There are only two pages so far: `hello` and `name_form`, both raw strings in `main.roc`. That's harmless now. It becomes the skinning problem the moment the chat's pages arrive, unless they arrive into a shell module.
5. **Porting leftovers.** `Bytes`'s header says "as Zig's std.mem handles them", and `Bytes.zig_spaces` has no caller. `Ascii` is named for Zig's `std.ascii`. These are names from the port, not from what the modules do here.
6. **The platform's types are called `Chat.*`.** `Chat.Request`, `Chat.Answer`, `Chat.stream`: the bus agent flagged this as the one thing a non-chat app would trip on.

## Small changes first

Each of these is an hour or less, and each removes a reason for a fork to patch more than one file.

**A. One test cast: `app/Cast.roc`.** These are the principals the tests share: `boss`, `ann`, `bea`, their agents and bots, the id makers (`gid`, `aid`, `gen`, `kid`, `sid`, `cid`) and `session_of`. Each module's expects import it, and the 13 copies go. Expect counts must stay exactly 1,678, which makes it a safe refactor.

**B. `main.roc` becomes the route table alone.** The handlers move to `SignIn.roc` (`login!`, `callback!`, `name!`, `me!`, `refused_or!`). `main.roc` keeps `handle!`'s dispatch, about 60 lines, which a fork reads first and patches last. The stubs (`/stub/*`, `/echo`, `notes!`) are deleted at step 6 as planned. They shouldn't move anywhere first.

**C. A `Store.roc`: the only module that names a file.** It takes the six paths, `accounts!`, `settings!`, `nonce_use!`, the session read and write, the audit append and the signed-in writes. Its functions take and give the core's types (`List(Principal)`, `GitHubSignIn.Settings`, `Session`) and hide paths and codecs. `SignInWeb`'s record half moves here, or into a `SettingsCodec` beside the others, so `SignInWeb` is the wire alone.
- **Why it's ergonomic for us:** reading the file layout means reading one module.
- **What the SQLite fork rewrites:** `Store.roc`, plus the host's file functions. It never touches a handler.
- This is the one place I'd accept indirection for segregation, and I think it costs us nothing: those reads were already gathered at the bottom of `main.roc`.

**D. `Chrome.roc` arrives before the first chat page does.** When step 8 ports roc-webbox's `Chrome`, `Pages` and `Docs`, the page shell goes in one module:
- the doctype and head;
- the top bar and the nav;
- the theme toggle and the base CSS;
- the site's name, now hard-coded as "roc-chat" in `hello`.

Each page's body stays in its feature's module. **A skin fork is then `Chrome.roc` plus chat-client's `colors.js`**, and a page-specific tweak is a small patch to one feature module. This is the CSS plan from earlier today, with `Html.style` and the Shale check, given its home.

**E. Rename the porting leftovers.** Drop `zig_spaces`, and rewrite the two headers to say what the modules do here.

**F. Maybe: rename the platform's `Chat` to `Web`.** `Web.Request`, `Web.Answer`, `Web.stream` would read right to anyone cherry-picking the platform. It's the biggest of these, touching every handler and the glue, so I'd do it only if we decide the platform should be offered on its own. One question first: whether the pinned Roc imports modules from subfolders. If it does, `app/auth/` and `app/chat/` would make the core visibly one unit. If it doesn't, flat is fine.

## Where forks will take most of the app

Ordered by how likely I think each is, most likely first.

1. **Chrome and skin.** Name, colors, layout, top bar, fonts. **Fork:** `Chrome.roc` and `colors.js`, after D. This should never need a change to the core or the host.
2. **Who can sign in.** GitHub is a fine default, but a team will want Google, email magic links, or no sign-in at all for a local, single-user chat. Your sister is the first real case of this. **Fork:** `GitHubSignIn`, `OAuthState`, `GitHubLogin`, the sign-in routes, and the host's GitHub client. **What stays:** `Principal`, `Session`, `Access`, `ApiKey` and `Admin`, because the flow ends in an `Admission` and `Session.start` takes nothing else.
   - **The easy win:** name the seam. `Admission` is it. Document it as "a sign-in flow's whole job is to make one", and a second provider is a sibling of `GitHubSignIn` rather than an edit of it.
   - **The GitHub coupling to watch:** `Principal.GitHubId` is a human's identity. A non-GitHub provider wants an id type of its own. That's a real change, but contained in `Principal` and `AccountCodec`. No action now; just don't spread `GitHubId` into chat modules when they're ported. They should take `Principal.Id`.
3. **Persistence.** Files to SQLite or Postgres. **Fork:** `Store.roc` (after C) and the host's file functions. The codecs can stay, as one row's text, or be replaced by columns, the fork's choice. The bar you set is that this should fall out of making our own file store easy to read, and C does both.
4. **Who sees what.** Visibility rules beyond Private and Public: an open team chat where everything is public, invite-only rooms, or your allow-list v2. **Fork:** `ConvAccess` alone. `Access` and `ApiKey` are already generic, so a new policy is a new layer beside `ConvAccess`.
5. **The browser client.** Someone will want React, or a native app. **Fork:** chat-client entirely. **The seam:** CC's `CONTRACT.md`, which the server can now check itself against. This axis is in good shape today.
6. **Markdown.** A different dialect, or plain text for a minimal chat. **Fork:** the roc-markdown package, already its own repo. **The easy win:** when chat pages arrive, render through one call site (`Render.roc`, or a function in the module that owns messages) rather than `Md.render_*` scattered across handlers.
7. **Bots and integrations.** The GitHub commit bot first, then others. `Principal` already has `Bot`, and keys are scoped. **Fork:** one module per integration that turns a webhook into posts. The route table names them, so adding a bot means adding a module and a line, never editing others.
8. **The host.** Fewer people, but some will want another OS, or no Zig at all. **Fork:** `host/`. **The seam:** `Host.roc` and `Chat.roc`, held by glue. This is fine as it is.

## Cherry-picking a concept

For someone building something nearby who wants one idea, not the app:

| Concept | Where it lives now | What they'd need to lift it | Ready? |
|---|---|---|---|
| **SSE with no gap and no duplicate** | `platform/Sse.roc`, `host/bus.zig`, `host/sse.zig`, the turn in `host/server.zig` | the three host files and the subscribe-in-the-turn rule | **yes**, once F or a note explains `Chat.*` |
| **The auth core**: opaque viewers, scoped keys, generations | `Principal`, `Access`, `ApiKey`, `Session`, `Stored` | the five modules, plus `Ascii`/`Bytes` | **nearly**: A removes the test-cast tangle that makes each one hard to lift alone |
| **Sign-in as a state machine** | `GitHubSignIn`, `OAuthState` | the two, plus `Principal` | yes |
| **One-line records** with one spelling, decoders as the only door | `Stored` and the four codecs | `Stored`, `Ascii`, `Bytes` | yes |
| **Atomic, durable files** that tell missing from failed | `host/files.zig`, `host/auth/path_rule.zig` | the two Zig files | yes |
| **A Roc crash is a 500** | `host/seam/sljmp.zig`, `roc_abi.zig`, the guard in `chat_abi.zig` | the seam's guard | yes, but it needs a short doc of its own |
| **A wiping allocator for secrets** | `host/github/wiping.zig` | one file | yes |
| **Markdown with a work budget** | roc-markdown | the package | yes |

## What I'd do, in order

1. **A, the test cast.** It's mechanical, the counts check it, and it's an hour.
2. **C, then B: `Store.roc`, then `main.roc` as the route table.** Do these before step 6 ports the chat's own records, so they land in `Store.roc` from the start rather than in `main.roc`.
3. **D at step 8,** with the CSS plan.
4. **E whenever it's convenient.** F waits for a decision on offering the platform separately.

A, C and B are box work, about half a day. Or a long chunk for CC, with a verify script that holds the expect count at 1,678 and the module list to the new shape.
