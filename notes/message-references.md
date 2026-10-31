# Message references: the problem, and the fix for both chats

*2026-10-31. LC, from reading the code as it is: chat-client `ac97b6d`,
angry-gopher `ccfa838`, chat-markdown and roc-markdown main, and CC's
channel model on roc-chat `claude/roc-chat`.*

## What a message reference is

In both chats you can write `MSG_plans_3` in a message. It means
"message 3 of the topic `plans`", and it renders as a link:
- **The renderer** (chat-markdown in Zig, roc-markdown in Roc) turns
  `MSG_<topic>_<n>` into `<a href="#msg-plans_3" class="msg-ref">`. It
  knows nothing of conversations.
- **The browser client** decides where the link goes when you click it
  (chat-client `js/chat.js:150-162`, `navigateRef`):
  - It cuts the id at its last `_`, so the topic is `plans`.
  - If that topic is the topic of the page you're on, it scrolls to
    message 3 there.
  - Otherwise it opens `/chat/msg/plans_3` and lets the server work out
    where that is.
- **Production's server** answers `/chat/msg/<id>` (angry-gopher
  `zig-server/src/chat.zig:549-569`, `redirectToMsg`). It walks the
  viewer's DMs, then the viewer's channels, and redirects to **the first
  conversation that has a topic of that name.**

## The problem statement

**A reference names a topic but not the conversation the topic is in, and
topic names aren't unique across conversations.** `ChitChat`, the default,
can be in every DM and every channel, and nothing stops two channels from
both having `plans`. So the reference is ambiguous, and both halves of the
system resolve it by guessing.

**Two concrete failures, both in production today:**
1. **The wrong message, silently, on the same page.** Ann writes
   `MSG_ChitChat_5` in #Cobblestone's ChitChat, meaning #Cobblestone's
   message 5. Bob reads a copy of it, say in a quote, while on #General's
   ChitChat page. The client sees the topic `ChitChat`, matches it to the
   current page's topic, and scrolls Bob to **#General's** message 5. No
   error, just the wrong message.
2. **A different conversation for each viewer.** From any other page, the
   client opens `/chat/msg/ChitChat_5`. The server picks the viewer's first
   DM with a ChitChat (in the order of the user list), else the viewer's
   first channel with one. Ann and Bob, clicking the same link, can land in
   different conversations, and neither may be the one Ann meant. A
   reference into someone else's DM can't resolve at all. The viewer's own
   DM of the same topic name is found instead.

**So, to your question: this isn't new in Roc chat. It's been a bug in the
Zig chat all along.** It stays mostly hidden because people tend to give
topics distinct names, and references mostly point within the same page.
roc-chat only surfaced it because your channel decision says plainly that
topic names are scoped to their channel or DM. Once you say that, an
unscoped reference can't be right.

## The proposal

One reference form, spelled the same way in both chats, written by the
same client, rendered by both renderers, resolved exactly by both servers.

**1. The long form names the conversation.**
- **A channel's message:** `MSG_<channel>.<topic>_<n>`, for example
  `MSG_Cobblestone.ChitChat_5`. Channel names start with a letter, and
  neither channel nor topic names can hold `.` or `_`, so it splits one
  way only: channel before the first `.`, number after the last `_`, topic
  between. That's CC's proposal for roc-chat.
- **A DM's message** (production has DMs, and roc-chat may): the DM's pair
  of user ids with a hyphen, `MSG_1-3.ChitChat_5`. A leading digit can
  never be a channel name, so the two never collide. Its readers are the
  DM's two participants, as for the page itself.

**2. The short form keeps meaning "this topic, on this page", and only
that.** `MSG_plans_3` stays valid, so old transcripts don't break:
- the client resolves it only against the page's own conversation and
  topic;
- nothing guesses across conversations any more.

**3. Who writes which.**
- The client writes the long form whenever it writes a reference meant to
  travel: copying a message's reference, or quoting into another place. It
  knows the page's conversation from `<conv-base>` and the topic from the
  page.
- Edits (`Edit of MSG_<topic>_<n>`) stay short, because an edit is always
  in its own topic.

**4. The renderers stay host-agnostic.** chat-markdown and roc-markdown
each learn the long pattern and emit it the way they emit the short one:
`<a href="#msg-Cobblestone.ChitChat_5" class="msg-ref">`. They still
decide no URLs, the same split as the uploads predicate: the markdown
knows the syntax, and the host knows where things live. Until a renderer
learns it, the long form shows as plain text, never as a wrong link.

**5. The client compares the whole place.** `navigateRef`:
- parses either form;
- treats a reference as same-page only when both the conversation and the
  topic match the page;
- otherwise opens `/chat/msg/<long id>`.

This is one change in the shared chat-client, serving both chats.

**6. Each server resolves exactly, or refuses.** `/chat/msg/<long id>`:
- finds that channel (or that DM) and that topic, by name;
- checks the viewer may read it;
- redirects there;
- otherwise answers the same 404 a page gives, so it leaks nothing about
  what exists.

A short id that reaches the server (an old link) redirects only when the
viewer has exactly one topic of that name. Otherwise it answers "this
reference is ambiguous" instead of guessing.

## The matching work, chat by chat

| Piece | Zig chat (production) | Roc chat |
|---|---|---|
| Renderer learns the long form | chat-markdown `src/markdown_links.zig` (`msgRefEnd`) | roc-markdown `package/MdChat.roc` |
| Client parses and compares the whole place | chat-client `navigateRef`, shared: one change | the same change |
| Client writes the long form when copying or quoting | chat-client, shared | the same change |
| Server resolves exactly, refuses ambiguity | angry-gopher `redirectToMsg` | roc-chat's `/chat/msg` route, with CC's `MessageRef` and `Topic.find` |
| Tests | chat-markdown's judge, chat-client's contract test (a reference across channels, the same-name trap), angry-gopher's unit tests | roc-markdown's judge, the same contract test, roc-chat's e2e steps |

No divergence is needed. The client change is shared, both renderers learn
the same pattern, and each server gets the same exact rule. The only
asymmetry is timing: roc-chat's server side lands with its channel routes,
while production can take its whole fix as soon as you want it, with a
v47 or a v46.

## Questions for you

1. **The DM spelling,** `MSG_1-3.ChitChat_5`: fine, or do you want DMs
   left short-form only, since DMs are private and a reference into one
   only ever helps its two participants?
2. **Old short references across conversations** (in existing
   transcripts): an "ambiguous" answer when there's more than one match,
   as proposed, or always the page's own conversation?
3. **Order:** production's fix first, since that's where the bug lives
   today, then roc-chat's alongside its routes?

## The survey, and Steve's answers (2026-10-31)

Two read-only Shale scripts ran on lynrummy.com (`/admin/script`, background):
- **Repeated topic names:** 30 topics in 8 conversations; two names appear
  in more than one: `general` (four DMs and #Cobblestone) and `marketing`
  (one DM and #Cobblestone). `ChitChat` is in none twice.
- **References to those names:** 125 across the 30 transcripts (1.7 MiB),
  every one written inside its own topic and pointing to an earlier message
  there. None crosses a topic or a conversation, and none points forward, so
  none looks meant for another conversation. **The bug has never bitten on
  prod**, and there is no old data to fix.

Steve's answers:
1. **DMs stay short-form.** Only channel references get the long form,
   `MSG_<channel>.<topic>_<n>`.
2. **Old data:** nothing to fix, per the survey.
3. **Production first.**
