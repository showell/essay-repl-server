# Several webbox apps on one server: a design

**The goal:** run two or three webbox apps on one server, Linux or our unikernel. One **primary** app owns `/` and its URL space; Gopher Chat's can't easily change. Other apps **piggyback** under their own prefix, as Codex Chat does under `/codex-chat` today. Combos in view:

- Gopher Chat + Codex Chat + UO;
- Dog Park + Roc TODO;
- now and then others.

This is drawn from three design memos written by agents on 2026-10-25, which read the code but built nothing. Every claim below is a reading, still to be confirmed.

## 1. The mechanism: `webbox.combo.Mount`

One new webbox file, `combo.zig`, about 170 lines plus tests:

```zig
pub const site = webbox.combo.Mount(gopher, &.{
    .{ .prefix = "/codex-chat", .root = codex_chat },
    .{ .prefix = "/uo", .root = uo_town },
});
```

Each part is the `site` + `hosting` pair every app already exports, and the result is the same shape. So the Linux host and the unikernel host a combo exactly as they host one app.

- **Routing:** guests' prefixes are checked first, so the primary can't shadow them, and the primary gets everything else, `/` included. A bare `/todo` redirects to `/todo/`. The prefix is stripped, so a guest sees itself at `/`. Guests must use relative URLs in their pages.
- **Setup:** the primary runs first, then the guests in table order. A failure fails the start.
- **Body limits, uploads and request families:** decided by path. A guest that declares no families is counted under its own name.
- **`between`:** every part is called with one bus. Any `.more` wins, else the earliest `.at`, else idle. That's today's hand-written Gopher rule, made general.
- **Start log:** the primary's names, then each guest's lines under its prefix.
- **Data:** each guest is handed `data/<name>/` and `auth/<name>/`, so file use is disjoint **by construction**. Codex Chat's files on lynrummy.com stay where they are, with no migration.
- **The unikernel:** `addAppKernel` gains a `mounts` list of modules and their `assets.zon` files, about 15 lines. Embedded names can't clash, because each module embeds its own. That deletes the kernel's hand-built Codex Chat and UO modules.
- **angry-gopher:** about 40 lines of special cases go: its route arms, family and body-limit cases, most of its `between`, and the guest parts of its startup.
- **Left out, to keep webbox small:**
  - HTML rewriting;
  - bus-key namespacing;
  - nested mounts;
  - mounts configured at run time;
  - a landing-page registry. The primary's home page simply links to its guests, or users get the direct link.

## 2. What the apps need first

**Gopher Chat + Codex Chat + UO** works today; the mechanism tidies it.
- **Cookie handling:** every guest request currently passes through Gopher Chat's cookie handling and refusals. Under `Mount` it stops doing so, which is a behaviour change to accept.
- **`/version`:** should name the guests' commits too.
- **Memory:** the guests take 384 MB of heap at boot (Codex Chat 256, UO 128), to check against the kernel's memory.
- **The UO town's start-over and pace:** open to every watcher. Gating them is a call for when it's deployed.

**Dog Park + Roc TODO** has one real blocker and three small items:
1. **The Roc runtime clash (the largest item).** Both apps define `roc_alloc`, `roc_realloc`, `roc_dealloc` and `roc_crashed`, with different behaviour: Dog Park panics on an unexpected allocation, while TODO allocates from a per-request arena. One binary can't link both. The fix is one shared Roc glue module that routes each call to whichever app's Roc code is running, plus one pinned Roc nightly for both. TODO currently uses whatever `roc` is on the PATH.
2. **TODO under a prefix:** its page calls `/api/todos` absolutely. It needs relative fetches, about 5 routing lines, and the prefix stripped.
3. **Dog Park as primary:** today it answers 0 as the body limit for paths it doesn't know. `Mount` handles that, since guest paths never reach it.
4. **Two other collisions,** for combos nobody asked for yet. Gopher Chat and Dog Park both sign with `auth/_session_secret`, both claim `/admin` and `/version`, and their `data/players` clash (a folder in one, a file in the other). Per-guest `auth/<name>/` fixes the secret, provided whichever of them is the guest is mounted with its own roots.

## 3. Identity: a sticky anonymous visitor, ≤30 lines an app

Webbox already has most of it:
- `signed.zig`, for HMAC;
- `site_secret.zig`, for the secret in the auth folder, with rotation;
- `signed_cookie.zig`, for issue, read and renew, with the `__Host-` handling.

What's missing is one call, about 50 lines plus tests:
- `signed_cookie.visitor(...)`: the visitor's id, a Set-Cookie when one is needed, and whether the visitor is new, returning or unrecognised;
- `site_secret.randomHex`: four apps hand-roll random hex today;
- a plain-http mode for development (`Transport{https, plain_http}`): the cookie header is always Secure today;
- `named`, which picks `__Host-<name>` or `<name>`.

**The id:** 8 random bytes as 16 hex characters in a signed cookie. The signature is the credential, and nothing is stored until the visitor writes something. Checking an opaque id against a file was rejected because it costs a write for every visitor, crawlers included.

**Under a prefix:** a `__Host-` cookie must be `Path=/`, so apps on one origin are kept apart by **cookie name and signing label**, not by path. TODO takes `roc-todo`.

**The multi-user TODO:**
- **The host side:** the Zig host assigns the id before calling Roc.
- **Roc's side:** Roc gets it as a new field, `Http.Request.user`. The list becomes `todo/<user>.json`, about 12 lines of Roc.
- **Identity code:** about 31 lines in TODO's Zig, against about 60 without the helpers.
- **Tests:** two users each see only their own list, and a tampered cookie gets a fresh id.

**Found along the way:**
- Dog Park never renews its cookie, so an active player is still logged out a year after the cookie was signed.
- Codex Chat and the UO town compare tokens in a way that isn't constant-time.
- `nowUnix` is copied in nine places, and a `webbox.unixNow` would serve them all.

## 4. Calls for Steve

1. **Mount's behaviour changes in Gopher Chat:** guests stop passing through its cookie handling, and their requests are counted under their own names. Accept?
2. **The Roc glue:** one shared module, with one pinned nightly for every Roc app, Dog Park's or TODO's version. Which?
3. **Identity:** should the cookie's `transport` be required, which costs one line in each existing caller, or default to https?
4. **TODO's old single list (`todo/todos.json`):** drop it, or give it to the first visitor?
5. **Bare-metal FAT limits:** a folder holds about 21,800 files. Should `todo/` fan out into subfolders now, or later?

## 5. Proposed order

1. **`Mount` in webbox,** with tests, rewriting Gopher Chat's combo onto it. Nothing new ships; the deletions prove the API.
2. **The visitor helper in webbox; multi-user TODO** on Linux and the unikernel.
3. **TODO prefix-clean;** the shared Roc glue.
4. **The Dog Park + TODO combo,** on Linux and then QEMU.
