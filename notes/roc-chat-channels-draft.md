# roc-chat channels: a design draft

*2026-10-31. LC, a draft for Steve to steer, from a read-only survey of
production's Zig chat, chat-client's contract, roc-webbox's frozen Roc chat
and roc-chat as it stands. Nothing here is built.*

## What Steve asked for

Channels, not group DMs. A Cobblestone channel on roc-chat, as on the Zig
chat, with trusted colleagues (Damian, Apoorva) and agents (CC, LC). Start
restrictive: **a topic with agents in it locks out non-owners.**

## What exists to build on

- **Production's Zig chat** has channels and topics, but no route makes a
  channel.
  - A channel is a hand-written member file (`channels/<name>.channel`, one
    uid a line).
  - Its members can read, post and create topics. There are no invites,
    roles or public channels.
  - Topics are named (`ChitChat`), and message ids are `<topic>_<n>`.
  - Pins are per user. The URL is `/channel/<name>/<topic>`.
  - Its one agent is just a uid in the file.
- **chat-client's contract** wants exactly that shape:
  - a string `data-conv`, and a `<conv-base>` of `/channel/<name>`;
  - topics as path segments;
  - message ids `<topic>_<n>`;
  - sidebar rows `ch:<name>` and `uid:<n>`;
  - `POST <conv-base>/new`, pins, and a `topic-added` event.
- **roc-webbox's frozen Roc chat** already implemented that model in Roc.
  Its pure pieces carry over: the `ConvKey` sum type, the channel and
  topic name validators, caseless topic matching, the pin file and the
  sidebar shapes. Its auth model, production's uids, does not.
- **roc-chat** has what production lacks: real principals (`human:N`,
  `agent:N`, `bot:N`, each agent answering to its human), scoped keys,
  invites, caps, mentions and the agent-hop cap. Its unit of access is a
  conversation with participants fixed at start. And its existing rule is
  already close to Steve's: a conversation with agents in it is visible
  only to its participants and the humans those agents answer to.

## The proposal in one line

**Channels hold topics. A topic is either a human topic, open to the
channel's members, or an agent topic, open only to the agents named when
it was made and to the humans they answer to.**

Making that choice explicit, at the topic's creation, is the main design
decision here. The alternative, a topic that locks the moment an agent
posts in it, would suddenly hide a human conversation's history from
members who were in it a minute earlier. That's surprising, and it's hard
to undo.

An agent topic is, almost exactly, today's roc-chat conversation with
agents in it. So today's access code carries over to a topic nearly as it
is.

## The pieces

**Channels**
- **Named,** with production's rule (a letter, then letters, digits and
  hyphens, up to 40). The URL is `/channel/<name>`, and the sidebar row is
  `ch:<name>`.
- **Members are humans.** Agents are never channel members; they reach a
  channel only through agent topics their owner makes.
- **Made by an admin at first.** That's Steve, through a page, not by
  hand-editing a file. He names the channel and its members, and can add
  or remove members later.
  - That keeps "who is in" a decision with one owner, as production's
    hand-made files are.
  - Letting members create channels can come later, if wanted.
- **Leaving or being removed** takes away a member's access to the
  channel's human topics, and to any agent topic they had only as a
  member.

**Topics**
- **Named** as production names them, unique within the channel, caseless.
  Message ids are `<topic>_<n>`, so chat-client's edits, quotes and
  roc-markdown's `MSG_` links work as they are.
- **A human topic:** any member reads, posts and creates one. No agent can
  read or post in it.
- **An agent topic:** made by a member, who names one or more agents.
  - Each named agent must answer to a channel member: the maker's own
    agents, or another member's with that member's consent (see the
    questions below).
  - Readers and posters are the named agents and the humans they answer
    to. Nobody else, members included.
  - The set is fixed at creation. Adding an agent means a new topic, at
    least at first.
- **Pins** stay per user, as in production.

**Keys and reach**
- An agent's key reaches the agent topics that name it, and nothing else.
  Its scope can stay coarse (`read=everywhere` means "every topic that names
  me"), because the topic rule already bounds it.
- A human's own key reaches what its human can see, as today.

**What carries over unchanged, now per topic**
- mentions;
- the two-hop listeners;
- the server's cap of 4 agent-to-agent posts;
- transcripts, paging, gaps and offsets;
- the audit.

## How Steve's examples play out

- **#Cobblestone, members Steve, Damian, Apoorva.** Human topics are shared
  by all three, as on the Zig chat.
- **Steve makes an agent topic in #Cobblestone with CC and LC.** Only
  Steve, CC and LC see it. Damian and Apoorva don't, even though they're
  members. This is the restrictive rule as stated. It means the colleagues
  can't see the agents' work in that channel unless Steve copies it into a
  human topic.
- **Damian invites his own agent:** he makes an agent topic naming it.
  Only Damian and his agent see it.
- **A topic with CC and Damian's agent together:** Steve and Damian both
  see it, as both agents' owners. Apoorva doesn't.

## What happens to today's conversations

Today's three conversations are agent-or-DM-shaped: a fixed group, some
with agents. Two options:
- **(a) Keep them as they are,** as a legacy kind beside channels, until
  nothing uses them.
- **(b) Move each into an agent topic** of a channel Steve names. Conversation
  3, with Steve, CC and LC, becomes an agent topic naming CC and LC.

(b) gives one model to maintain. (a) is less work now. I lean (b), because
the agents' listeners and keys would otherwise have two kinds of place to
reach. Whether 1:1 DMs between humans survive at all is Steve's call: he
dislikes group DMs, not necessarily pairs.

## Questions for Steve

1. **Should agent topics stay closed to channel members?** The rule as
   stated hides Steve's agents' work from Damian and Apoorva. A softer
   start would let members read agent topics but not post. I've drafted
   the strict version.
2. **Can a member name another member's agent in a topic?** I'd say only
   with that agent's owner as a co-maker (both consent), or not at all at
   first.
3. **Who makes channels?** Admin only at first (proposed), or any member?
4. **Do today's conversations move into channels (b), or stay (a)?** And do
   human 1:1 DMs stay?
5. **How unique are topic names?** Production's `/chat/msg/<id>` takes the
   first matching topic across conversations, so names are ambiguous
   between channels. I'd resolve a `MSG_` link within the viewer's current
   channel first, then refuse rather than guess.

## A possible order

1. Steve answers the questions.
2. The model in roc-chat, pure first: channels, topics, the two topic kinds,
   access, the store layout, porting roc-webbox's validators.
3. Routes: the admin's channel page, topic creation, posting and the
   stream per topic, keys reaching agent topics.
4. Moving conversation 3 (if (b)), and the listeners pointed at topics.
5. Serving chat-client's contract for channels, the adapter the JS audit
   sized, which channels make much smaller.

Steps 2 and 3 are a long CC chunk each, with verify and e2e steps for every
access rule and a planted fault per refusal, as roc-chat's other access
rules have.
