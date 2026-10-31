# Sharing the chat client with roc-chat

*2026-10-31. LC, from three read-only audits of chat-client (at 9d61be9,
after the back/forward slimming) against roc-chat (19ab730) and angry-gopher.*

The question: can roc-chat use production's browser client verbatim for
human conversations, diverging only for load-bearing reasons? **Mostly yes,
but not today, and the work splits into three kinds:** gating that protects
both chats now, one or two real design decisions, and a modest adapter in
roc-chat. Steve's move toward **channels with topics** turns out to be the
single biggest simplifier, because that's the client's own model.

## First: protect production from the sharing itself

This is the cheapest part and the most urgent. It matters whether or not
roc-chat ever loads the client.

- **Nothing in chat-client gates chat-client.** The syntax check, the lint
  and the resize test run only from angry-gopher's `ops/test_chat`. The
  contract test (`tools/test_contract.mjs`) has no caller anywhere. roc-chat's
  verify copies the checkout and checks none of it.
- **Neither host pins a version.** Both build chat-client by path, so
  whatever the checkout holds ships at the next build. A change made for
  roc-chat reaches production unseen, and the reverse is caught by nothing.
- **It has already bitten once:** on 2026-10-28 a JSON key renamed in
  angry-gopher (`sessions` to `topics`) left the sidebar saying "No sessions
  yet", and only a person noticed. And yesterday's slimming would have broken
  production's build through a page list no JS gate reads.

**Recommendation:** give chat-client its own one-command verify (syntax,
lint, resize, contract), make each host's gate run the contract check
against its own page and stream, and pin each host to a chat-client commit
that is bumped on purpose, with both hosts' checks. Then "verbatim" is
something a machine holds, not a hope.

## Two bugs the audit found, one of them in production

- **Any post can hide anyone's message, in production today.** A post
  beginning `Edit of MSG_<id>` replaces the original for every viewer with
  "Edited in…", whoever wrote it (chat.js:205-211), and every bubble has an
  edit button. The fix is small and belongs in the client for both chats:
  apply an edit only when its author is the original's, and show the button
  only on your own messages.
- **roc-chat's mentions count quoted text.** `Mentions.of` scans fences and
  quotes too, so a human quote-replying to a post that said `@CC` pings CC
  again and resets the agent-hop count. A server fix in roc-chat: skip
  fenced and quoted text.

## What a human sees when agents are present

This is the "wonky" case Steve predicted, and it's real but bounded.

- **An agent looks exactly like a human.** The client shows only a name,
  and roc-chat lets an agent take any display name, so an agent named "Steve
  Howell" can't be told from Steve. roc-chat's own rule (DisplayName.roc) is
  that a renderer shows the principal's kind and owner beside the name, and
  neither client does it yet. That needs the server to send kind and owner,
  plus a small label in message.js. I'd call it load-bearing, and harmless to
  production: an absent field shows nothing new.
- **Human-pace assumptions:**
  - A long agent answer auto-scrolls to its end, past its start.
  - There's no "new posts below" signal once you've scrolled up.
  - Search re-queries on every live post, which a burst can turn into
    "Searching too fast".
  - All small client changes, and production benefits too.
- **Notifications are already calm:** no sounds, flashes or unread
  counts, so floods don't hurt.
- **Agent-style markdown is unstyled:** tables have no borders and overflow
  the bubble, and headings are full size. That's a few `.chat-body` rules.

## The contract: what roc-chat would serve

roc-chat could meet the contract with an adapter of roughly 500-700 lines of
Roc, beside its agent API, which stays as it is: the page and its
attributes, the browser's message frame, a form-based send that echoes the
client's `cid`, the stream's opening `backlog-size`, sidebar data, a few
stubs, and the `/chat/msg/<id>` redirect. roc-webbox's `chat/` already
implements this contract in Roc and is worth porting from. Two items are
decisions, not adapter work.

1. **The backlog.** The client assumes it receives the whole topic from
   message 0: positions, focus, quotes, edits and reactions all key on that.
   roc-chat deliberately sends at most the newest 100 messages and a `gap`,
   which the client never hears. So past 100 messages the bubbles point at
   the wrong things. The options:
   - send the whole transcript to browsers (up to 4 MB);
   - teach the client a base offset and the `gap` event.
   **I recommend the client change:** production keeps sending from 0, so
   for it nothing moves, and roc-chat keeps its bounded reads. That's a
   compatible extension, not a fork.
2. **Streams.** Each tab opens three streams (topic, sidebar, notifications),
   and roc-chat's host caps each holder at 8 and the server at 64. Raise the
   caps, or answer the sidebar and notification streams with a 404 at first
   (the client gives up quietly, at the cost of a live sidebar).

The rest is mapping:
- **Message ids** become `<conv>_<n>`, which fits the client's edit pattern
  and roc-markdown's `MSG_` links.
- **`at`** becomes an RFC 3339 string, about 30 lines of date code.
- **`mentions`** gets listed as ignored, so the contract check doesn't flag it.
- **Identity already works:** the client compares ids only as strings, so
  `human:2` and `agent:1` are fine.
- **Today's multi-party conversations** fit as sidebar rows with a server-made
  label.

## Why channels change the picture

The client's model is production's: a conversation (a DM pair or a channel)
holding topics, ids of the form `<topic>_<n>`, pins, add-topic, a sidebar of
people and channels. roc-chat's group DMs are the poor fit. Most of the
adapter's awkwardness comes from them: the fixed one-topic mapping, the
"+ topic" control that can't work, and the sidebar rows that are neither a
person nor a channel. **If roc-chat grows channels with topics, as Steve
wants, it should adopt the client's shapes as it builds them** (topic ids,
message ids, the sidebar's lists), and most of the adapter melts away.

Steve's permission rule (a topic with agents in it locks out non-owners) sits
entirely on the server. The client only needs the server to omit what a
viewer may not see.

## A suggested order

1. **chat-client gates itself and the hosts pin it** (a small CC chunk).
   This protects production now.
2. **The two bugs:** edits by their author only (client, both chats);
   mentions skip quotes (roc-chat).
3. **Design channels for roc-chat** in the client's shapes, with the
   agent-topic permission rule. A design conversation with Steve first.
4. **The backlog base offset and `gap` in the client,** compatibly, and the
   agent label (server kind/owner, client label).
5. **roc-chat serves the contract** for its channels, by then a smaller
   adapter, and the small human-pace fixes ride along.

None of this needs roc-chat to stop using its own pages in the meantime;
agents never touch the JS either way.
