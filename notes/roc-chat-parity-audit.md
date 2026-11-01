# Roc chat vs Zig chat: parity audit for Apoorva and Damian's GitHub sign-in

Date: 2026-11-01. Read-only. roc-chat at `d18638a` (main), angry-gopher's checkout as it stands, chat-client at `7b6358b8`.
Live checks were signed-out curl fetches only, against chat.lynrummy.com and lynrummy.com.

## The headline

**The Roc chat does not use chat-client at all.** Every Roc page is a small
hand-written HTML page with its own inline `<script>` (app/Pages.roc:630-771,
app/HumanInvites.roc:777-800). No page has a `<script src=...>`. The host
serves chat-client's 29 scripts at `/<name>.js` (app/main.roc:120-127,
host/assets.zig). Live, `https://chat.lynrummy.com/chat.js` returns 200 with
20,232 bytes, the same size as the pinned `js/chat.js` and lynrummy.com's
`/chat/chat.js`. But no page loads them. DECISIONS.md:80 says chat-client "is
used verbatim for human conversations". That decision has not been built.

So for "all the browser JS works": the JS that runs (the inline scripts) is
small and probably works. The JS Apoorva and Damian know from the Zig chat
never runs. They will see a different, much plainer app, not the Zig chat.

Second headline: **human DMs and channel topics have no browser page.** They
exist only as JSON routes (`/dms`, `/dms/<n>/topics/...`,
`/channels/<name>/topics/...`; README.md:66-71, app/Topics.roc). `/chat`
lists only the older "conversations" kind (app/Pages.roc:184-205, through
`Conversations.load_mine!`, app/Conversations.roc:104-124, which reads the
conversations index alone). A channel an admin admits them to, or a DM
someone opens with them, is invisible in the browser.

## Ranked gaps

### Blockers (the bar "looks and behaves like the Zig chat" fails, or they land nowhere)

| # | Gap | Zig chat | Roc chat | Confidence | Suggested fix |
|---|---|---|---|---|---|
| B1 | **No chat-client UI.** No three-pane layout, sidebar, topics rail, compose rail, keyboard navigation, quote/edit/react, emoji, search, help panel, theme, or mobile drawer. | chat_page.zig:27-31 and :102 load the page scripts; chat_chrome.zig:50 and :146-147 load the head scripts (colors, viewport, theme, drawer) | Pages.roc:591-615 is a bare page with 9 lines of CSS (:617-628) and inline JS; main.roc:120-127 serves the scripts, but nothing references them | Verified from code. Live: `/chat.js` serves (200). Not checked signed in. | Build the chat-client page shell (`#chat-root`, its `data-*`, `#chat-sidebar-data`, `.chat-layout`, top bar) for DM and channel topics, behind an adapter for the routes below (see the contract table). |
| B2 | **DMs and channel topics cannot be opened in a browser.** A human DM, the welcome DM a human invite makes, and admitted channels never show on any page. | The sidebar lists every other member as a DM and every channel the viewer is in (chat_page.zig:110-135). `/channel/<name>` and `/chat/c/<pair>/<sid>` are pages (chat.zig:168-258). | Pages.route knows only `/chat`, `/chat/agents`, `/chat/channels` and `/chat/<n>` (Pages.roc:86-103). Topics are JSON: `GET /channels/Lobby/topics` is a 401 signed out, a JSON list signed in (README.md:69). | Verified from code. Live: the topic route is a 401 signed out, as coded. | A topic page (`/channels/<n>/topics/<t>` and `/dms/<n>/topics/<t>` as HTML for a browser), and a list of channels and DMs on `/chat`. |
| B3 | **They land on an empty page and have no way to find anyone.** `/chat` says "None yet." above a form asking for ids ("human:2, agent:7"), plus an agents link and an "Invite someone" form. There is no user directory. | Zig `/chat` resumes the last conversation (chat.zig:104-110, :498-511). The sidebar lists every member at once, so Steve is one click away. | Pages.roc:188-189 shows "None yet."; Pages.roc:259-261 has the id-typed start form; the only place a human sees an id is their own, at Pages.roc:224-227. | Verified from code. | Short term: Steve gets their ids and starts a conversation (`POST /conversations with=human:A,human:D,human:1`) so it shows on `/chat`. Real fix: B2, plus a people list. |
| B4 | **An admin's channel is the wrong tool today.** Making a channel and admitting them (`/chat/channels`) gives them nothing visible, because of B2. Steve also needs their ids first, since there is no account list. | Channels show in the sidebar for members (chat_page.zig:128-135). | Channels.roc and Pages.roc:394-456: an admin page listing members by id; no topic page. | Verified from code. | Until B2 lands, use a multi-person *conversation* (it shows on `/chat` and has a live page), not a channel. |

### Visible differences (they will notice, but can chat)

| # | Gap | Zig | Roc | Confidence | Fix |
|---|---|---|---|---|---|
| V1 | Sign-in is GitHub, not their password. They must pick a display name, which starts empty, and names are unique across everyone. | `/login/full`, password (login.zig:3-4, :66-69) | SignIn.roc:520-532 name form, unique names (DECISIONS "Names are unique") | Verified from code. Live: `/login` gives a 303 to github.com/login/oauth/authorize with client_id and redirect_uri. Callback not exercised. | Tell them in advance; consider prefilling the name with the GitHub login. |
| V2 | **No sign-out anywhere in the UI.** `POST /logout` exists (main.roc:66-67, SignIn.roc:106-125), but no page links or posts to it. | The top bar has "Log out" (chat_chrome.zig:157) | No logout button in Pages.roc | Verified from code (grep finds no logout in Pages.roc) | Add a sign-out button that posts to `/logout`. |
| V3 | Mobile: the hello page, the name form and the refusal page have **no viewport meta**, so they render zoomed out on Apoorva's phone. The pages that have one (Pages.roc:606) are single-column and readable, but there is no drawer or responsive chat layout. | viewport meta (chat_chrome.zig:136), viewport.js and chat_responsive.js, the drawer | SignIn.roc:445, :494, :528: `<!doctype html><title>` with no viewport | Verified from code. Live `/` body matches (109 bytes, no viewport). | Route these three through `Pages.standalone` (it already has the viewport). |
| V4 | The conversation page: one flat list of `<article>`s, no bubbles or colors, no "mine" styling, no topics. Enter sends and there is no Send button, so on a phone there is no way to add a newline (Shift-Enter) and no visible send control. Whether that works on iOS was not tested. No edit, quote, react, upload, emoji or search. | message.js and message_view.js bubbles, chat_compose.js, chat_reactions.js, chat_search.js | Pages.roc:728-771 | Verified from code | Comes with B1. |
| V5 | No notifications: no status strip, no favicon alert, no presence dots, no cross-conversation pings. They will miss replies in conversations they are not looking at. | `/chat/notifications`, `/chat/sidebar/stream` (chat.zig:158-163), notify.js | None | Verified from code | chat-client's notify and sidebar streams (contract rows), when B1 lands. |
| V6 | Message references: `MSG_x_3` renders as `<a href="#msg-x_3" class="msg-ref">` (roc-markdown MdChat.roc:115-120, which matches the contract), but the Roc page's articles are `id=m<n>` (Pages.roc:555) and there is no `/chat/msg/<id>`. A reference click goes nowhere. A conversation's messages have no reference of their own. | `/chat/msg/<id>` redirects to the topic (chat.zig:149, :553-580); a click jumps to the bubble (chat.js:165) | No route (live `/chat/msg/x` is a 404) | Verified from code and live | Comes with B1 and B2 (topics carry `ref`). |
| V7 | Images: only `/user_uploads/` images render, and there is no upload route, so no image can be posted. A pasted external image is text. | Drag-in upload (chat_upload.zig, `<session-base>/upload`) | Conversations.roc:132-137 says "no uploads yet" | Verified from code | Upload route, plus chat_compose.js. |
| V8 | Recent, Images, Code and Docs surfaces are missing. | chat_chrome.zig:88-93 nav | None | Verified from code | Later. |

### Minor

- M1: README.md:269 and main.roc:17-19 still say topics and messages are "not yet routed"; they are routed (README.md:66-71, Topics.roc). This is doc drift. Fix: update the layout row.
- M2: The hello page says "Your conversations are at /chat" (SignIn.roc:440-441), which is true but sounds technical. `/chat` is the landing after sign-in anyway (SignInWeb.roc:226-230).
- M3: The Roc chat's identity line shows `(human:N)` and the start form asks for ids. That is jargon for Apoorva and Damian, but useful for exchanging ids today.
- M4: The join page (HumanInvites.roc:799) lands on `/chat`, where the welcome DM it just made is invisible (B2). This doesn't affect GitHub users, but it does affect anyone Steve invites without GitHub.
- M5: The host holds at most 64 streams server-wide (README.md:250-251). This is fine now, but chat-client opens about 3 streams per tab (topic, sidebar, notifications), so it matters once B1 lands.

## The JS contract: what roc-chat would owe chat-client (CONTRACT.md)

Both repos pin the same rev, `7b6358b8` (roc-chat/chat-client-rev, angry-gopher/chat-client-rev). The pin only gates the bytes Roc serves; no Roc page exercises them. If the pages adopted the client as is, here is what roc-chat lacks:

| Contract item | Client expects | Roc has | Gap |
|---|---|---|---|
| Page shell | `#chat-root` with `data-conv`, `data-session`, `data-conv-base`, `data-me`, `data-me-name`, `data-search-min`, three `data-upload-*` (init throws without them: CONTRACT.md:71-81); `#chat-left-sidebar`, `#chat-sidebar-data`, `#chat-feed`, `#chat-right-sidebar`, `.chat-layout`, `#chat-notify`, top-bar classes | `<body data-conv=N>` only | All missing |
| Topic stream | `<session-base>/stream?since=0`; a `backlog-size` event first, then `message` frames `{index, from, from_uid, at (RFC 3339), html, markdown, id "<sid>_<n>", cid?}` | `.../stream`; `message` frames `{id (int), at (unix int), by, kind, owner, login, markdown, mentions, html}` (Conversations.roc:1088-1114), and a `gap` event; no `backlog-size` | Event and shape mismatch. Without `backlog-size`, chat.js treats every backlog frame as live (chat.js:279-310). |
| Send | POST `<session-base>/send`, form `markdown`, `cid`, header `X-Chat-Async: 1`, then a `cid` echo on the stream within 3 s | POST `.../messages`, raw body, returns 201 and the message | Path, body and echo all differ; the client would report "The host may be down" |
| New topic | POST `<conv-base>/new`, form `topic` → `{sid}` | POST `/channels/<n>/topics`, form `name` → `{channel, topic, kind, agents}` | Path, field and answer differ |
| Sidebar | inline `sidebar_data` `{conversations[{id,label,url,active,online?}], pinned_sessions, topics}`, `/chat/sidebar/stream` | None | Missing |
| Reactions, saved, upload, raw, download, pin and unpin | `<session-base>/{reactions,react,saved,upload,raw,download}`, `<conv-base>/<sid>/{pin,unpin}` | None | Missing (a missing `saved` shows an error notice: chat.js:58) |
| Search | `/chat/search/words`, `/chat/search/messages` | None | Missing |
| References | `/chat/msg/<id>` | None (404) | Missing |
| Notifications, recent, code, images, docs | `/chat/notifications`, `/chat/recent/stream`, ... | None | Missing |
| Rendered markdown | `a.msg-ref` with `#msg-<id>`, `pre.chat-quote`, `target=_blank rel=noopener` | roc-markdown emits exactly these (MdChat.roc:115-120, MdHtml.roc:53, :159) | **Matches** |
| Script URLs | Any; the host chooses `src` | `/<name>.js`, ETag and no-cache (host/assets.zig) | Fine; the Zig chat uses `/chat/<name>` |

The cheapest path is to make Roc's topic URL layout the client's
`<conv-base>/<sid>` (conv-base `/channels/<n>/topics` or `/dms/<n>/topics`).
The stream path then nearly lines up, and the remaining work is aliases
(`send`, `new`), the frame translation (`index`, `from`, `from_uid`, RFC 3339
`at`, `<sid>_<n>` ids, `backlog-size`, `cid` echo), and stubs for `saved`
and `reactions` that answer empty instead of failing.
`node tools/test_contract.mjs --check-page/--check-stream` in chat-client
then checks the result.

## The journey

| Step | Zig chat (lynrummy.com) | Roc chat (chat.lynrummy.com) | Gap |
|---|---|---|---|
| Landing | Home page; `/chat` gives a 303 to `/login/full?next=/chat` (live) | `/` is a 3-line page, "You're not signed in. Sign in with GitHub." (live, SignIn.roc:434-445), with no viewport | Plain, and tiny on a phone (V3) |
| Login | Name and password (login.zig) | `/login` gives a 303 to GitHub OAuth (live), state cookie SameSite=Lax (SignInWeb.roc:138); callback in two calls (SignIn.roc) | Different method (V1). The callback was not tested live. The dogfood doc says Steve's normal browser "seemed to fail; the cause is still unknown" (docs/design/dogfood-sign-up-and-listening.md); README.md:39 now clears leftover cookies. |
| Name form | None (the name comes with the account) | An empty "Your name in the chat" form, unique names, no viewport (SignIn.roc:520-532) | V1, V3 |
| First page | Resumes the last conversation, or "You do not have any conversations." (chat.zig:498-511, chat_page.zig:181-188) | `/chat`: "Your conversations / None yet.", a start-by-id form, Invite someone, an agents link, "Signed in as X (human:N)" (Pages.roc:207-231) | B3 |
| Conversation list | The left sidebar: every member (with a presence dot) plus channels (chat_page.zig:110-135) | A `<ul>` of conversations by participants' names; DMs and channels never listed | B2, B3 |
| Opening one | Its topic page; the topics rail; pinned topics | `/chat/<n>`: one stream of messages, no topics | B1, B2 |
| History | Backlog over SSE with `backlog-size`; transcript `raw`/`download` | The newest 100 server-rendered, and an "Earlier messages" button (Pages.roc:750-758) | Works, differently |
| Live updates | SSE per topic, plus sidebar and notifications streams | SSE per conversation; `gap` reloads (Pages.roc:759-761) | Works in the open conversation only (V5) |
| Posting | The compose rail, emoji autocomplete, drag-in uploads, cid echo | A textarea; Enter sends, Shift-Enter adds a line; no button (Pages.roc:540, :762-771) | V4, V7 |
| Editing | "Edit of MSG_<id>", author only (chat.js:91-97, :206) | None; such a message is plain text | V4 |
| Markdown | chat-markdown | roc-markdown; same classes for refs, quotes, links | Close; dialect differences not audited |
| References | `MSG_` links jump, or open `/chat/msg/<id>` | Rendered, but go nowhere | V6 |
| DMs | Automatic with every member | JSON only (`/dms`); invisible | B2 |
| Channels and topics | `/channel/<n>/<topic>` pages | Admin JSON plus an admin page; topics JSON only | B2, B4 |
| Unread | No counts in either; Zig has the favicon alert and status-strip pings | None | V5 |
| Notifications | notify.js strip and favicon | None | V5 |
| Mobile | Responsive layout and drawer (viewport.js, chat_responsive.js) | Single column; three pages without viewport | V3 |
| Sign-out | "Log out" in the top bar | None in the UI | V2 |

## What the Roc chat has that the Zig chat lacks

- Agents owned by humans, ten-minute single-use invites, scoped and revocable API keys (`/chat/agents`), and one stream per agent.
- Invites for humans without GitHub (`/join#<code>`).
- Server-side `mentions` and the agent-hop cap.
- A GitHub login shown beside display names, so look-alike names can't impersonate.
- Paged history with `?before=`, and resume by `Last-Event-ID`.
- An audit log.

## Who must do what so Apoorva and Damian land somewhere with people

1. Apoorva and Damian sign in with GitHub, pick names, and read their own id from the bottom of `/chat` ("Signed in as ... (human:N)"). Steve is `human:1` after the 2026-11-01 wipe.
2. Someone (Steve) starts a conversation on `/chat` by typing `human:A, human:D` in "Anyone else, by id". Steve is in it automatically, because the signed-in human is always included (README.md:44). It then shows on all three `/chat` pages, with live updates.
3. Don't rely on a channel, a DM or a human invite for them yet. Each works on the wire but has no page (B2).

## What I could not determine

- Whether the GitHub callback and name form succeed live. I fetched signed out only.
- The production store's current accounts: who exists, and Steve's id.
- How roc-markdown's dialect differs from chat-markdown on real messages.
- Whether the inline scripts behave on iOS Safari. I read the code; nothing ran.
