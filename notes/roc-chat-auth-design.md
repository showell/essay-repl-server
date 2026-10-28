# Roc chat: auth, first draft

*Claude (the box), for Steve, 2026-10-28. A design to argue with, not a plan to execute. Your stated requirements are marked **(Steve)**; everything else is a proposal.*

## What the Roc chat is for now

The production chat stays Zig, on lynrummy.com. The Roc chat is a clean slate, and you've named what it's for:
- **Agent conversations are first-class (Steve):** human/agent and agent/agent conversation, not a human chat that tolerates bots.
- **Bots and integrations,** Zulip-style. The first is a GitHub commit bot that posts when things merge across the many repos.

That changes what auth is about. In the Zig chat, auth answers "is this one of the family?". In the Roc chat it answers three questions:
- **Who is this human?** GitHub.
- **Which agent or bot is acting, and for whom?** API keys.
- **Can this principal see this conversation?** One function.

## 1. Principals

Every request acts as exactly one **principal**. There are three kinds:

- **Human:** signs in with GitHub **(Steve)**. Has a display name they choose, which needn't be real **(Steve)**, and their GitHub account. The account is keyed by **GitHub's numeric user id**, not the login, because logins can be renamed and ids can't. The login is kept for display and for the GitHub link.
- **Agent:** an account a human creates and owns. Claude, CC, a future research agent. It has a display name and an owner (a human). It never signs in through a browser; it acts only through API keys.
- **Bot:** an integration, like the GitHub commit bot. It's an agent in every way that matters for auth, but it's fed by an outside system (a webhook) rather than by a model.

Whether bot needs to be its own kind, or is just an agent with a flag, is open. My lean is its own kind, because a bot's input arrives on a webhook with its own verification (below), and its posts may want a different look.

In Roc this is one tag union. The agent stops being a magic id, `"3"`, and becomes a kind the types can't confuse:
```roc
Principal : [
    Human({ id : GitHubId, name : Str }),
    Agent({ id : AgentId, name : Str, owner : GitHubId }),
    Bot({ id : AgentId, name : Str, owner : GitHubId }),
]
```

## 2. Humans sign in with GitHub

**The flow,** standard OAuth for a web app:
1. `/login` redirects to GitHub's authorize URL, with a `state` the Roc makes: random bytes, plus a signed, short-lived value tied to this browser.
2. GitHub redirects back to `/login/github?code=…&state=…`.
3. The Roc checks `state` (this is what stops login CSRF). The host exchanges `code` for a token at GitHub, server to server, and then asks GitHub `GET /user` for the id and login.
4. **A known id:** the Roc issues a session.
5. **An unknown id:** the Roc asks for a display name **(Steve)**, then creates the account, if invites allow it (section 5).

**What the host must provide:**
- **An outbound HTTPS request.** Webbox already has `linux_fetch`. It's the one new kind of primitive.
- **The OAuth app's client secret,** which stays in the host.
- **Random bytes, signing, the clock.**

The Roc never sees the secret, or GitHub's token past the one `/user` call. We don't keep that token at all, since we need nothing more from GitHub than who you are. Asking for no scopes beyond identity keeps the blast radius at zero if anything leaks.

**Sessions:**
- A cookie (`__Host-`, Secure, HttpOnly, SameSite=Lax) carries a random session id.
- The session itself is a small record on disk: principal, device label, created, last seen.
- That's what makes "sessions you can see and revoke" and "log out everywhere" real. A signed-only cookie can't be revoked.

**No passwords at all.** That removes password hashing, throttling of guesses, and resets: a whole category of code and of risk.

## 3. API keys, first-class and scoped (Steve)

A key acts **as one principal**: a human (for their own scripts), or one of their agents or bots. A human creates and revokes keys for themselves and for the agents they own.

```roc
Key : {
    id : KeyId,           # public, shown in lists
    acts_as : PrincipalId,
    scope : Scope,
    created : Time,
    expires : [Never, At(Time)],
    last_used : [Never, At(Time)],
}
```

The scope is deliberately coarse:
- **Read:** the conversations its principal can see. That's the same visibility function, so a key can never see more than its principal.
- **Post:** to the conversations its principal is in.
- **Optional narrowing:** to a listed set of conversations. That's for a bot that should only ever post to `#commits`.

**Storage:**
- The key is shown to its owner **once**. The host stores only a hash of it.
- Presenting a key is `Authorization: Bearer …`. The host hashes and looks up; the Roc decides what the key may do.
- Keys have no browser session, so they can't be ridden by CSRF.

**Agent-to-agent:** two agents, each with its own key, talking in a conversation is just two principals posting. Nothing special is needed beyond the agent kind. What *is* needed for agents is a good **API surface**: list my conversations, read since a cursor, post, and maybe a long-poll or SSE stream an agent can hold. That's a design of its own, after auth.

## 4. Who can see a conversation

You put it exactly: in the end every conversation has one decision, **can this principal see this conversation?** Make it one pure function, and test it exhaustively:

```roc
can_see : Principal, Conversation -> Bool
```

**A conversation:**
- its participants (principals);
- its visibility, `[Private, Public]`, **no more granular (Steve)**.

**The rules:**
- **A participant can always see it.**
- **A public conversation:** anyone signed in can see it. Open: should it be readable by the whole internet, signed out?
- **Human-to-human conversations stay private.** You named the elected visibility for human/agent and agent/agent conversations, so I read human/human as always private. Tell me if that's wrong.
- **Who elects.** Humans elect **(Steve)**: for a human/agent conversation, its human; for agent/agent, the agents' owners.
  - My proposal: a conversation is public only while **every human involved** has elected public, and any one of them can make it private again. That's safe by default, and it means one owner can never expose another owner's agent's words.
  - Your DM with CC is the motivating case: you're the only human involved, so it's your call alone **(Steve)**.
- **Seeing isn't posting.** Public means readable, not writable. Posting stays with participants.

**Channels** wait **(Steve)**. When they come, a channel is a conversation whose participants are a roster, and `can_see` doesn't change.

**The test is the spec:** every kind of principal crossed with every kind of conversation (human/human, human/agent, agent/agent, bot), each in both visibilities, plus "elected public, then one owner withdraws". That's a few hundred cells, written as a table of expected answers. It's the "exhaustive tests over small domains" idea from the last essay, applied where it matters most.

## 5. Invites

You want to change the invite structure **(Steve)**. With GitHub sign-in, the question becomes **which GitHub accounts may create an account here?** Options, simplest first:
- **An allowlist of GitHub ids,** set by the admin.
- **Invite links:** signed, single-use, expiring, made by any human member, each naming who made it.
- **Open sign-up,** with new humans able to see only public conversations until someone starts a conversation with them.

These can combine. My lean for a first version: invite links, plus the admin allowlist as the bootstrap for the first account.

## 6. Bots and the GitHub commit bot

The commit bot is a **bot principal** whose input is GitHub's webhooks:
- GitHub POSTs to `/hooks/github/<bot id>`, signed with a webhook secret (`X-Hub-Signature-256`, HMAC-SHA256).
- **The host verifies the signature,** since the secret stays in the host, and hands the Roc the verified payload. A bad signature is a 401 that never reaches the Roc.
- The Roc turns a push or merge event into a message: repo, branch, commits, and links. It posts as the bot to the bot's narrowed conversations, say `#commits`.

One bot can watch many repos: each repo's webhook points at the same bot with the same secret. That fits your many-repos setup. A merge in roc-webbox, chat-client or metal-vmm all land in one place.

## 7. What the host keeps (the whole list)

- the session cookie's random id, and reading it back;
- **random bytes**, **HMAC/sign and verify**, **hash** (for API keys), **the clock**;
- **one outbound HTTPS request**, for the GitHub token exchange and `/user`;
- **the secrets:** the OAuth client secret, the webhook secrets, the signing key.

Everything else is the Roc's:
- the OAuth `state` and the flow;
- sessions and their lifetime;
- keys and their scopes;
- `can_see`, the invites, the bot's message text.

That's the "hosted function answers a fact, never a verdict" rule from today's style guide, applied to auth.

## 8. Open questions

1. **Public to whom:** signed-in users, or the open internet? Most of the design follows from this.
2. **Are human/human conversations always private?**
3. **Can an agent start a conversation,** or only join one a human started?
4. **Bot as its own kind, or an agent with a flag?**
5. **First account and invites:** allowlist bootstrap plus invite links?
6. **The domain.** GitHub OAuth needs a registered callback URL, e.g. `roc-chat.lynrummy.com`, or a new name. Registering the OAuth app is yours to do, since it creates a GitHub credential.

## How I'd build it (when you say go)

- **First, the pure core, with no network:**
  - `Principal`, `Conversation`, `can_see`, scopes, the key checks;
  - the OAuth `state` checks;
  - the exhaustive `can_see` table.

  All of it is Roc and `expect`s, testable in seconds.
- **Then the host primitives,** each with a small test, plus a fake GitHub for the flow's end-to-end test.
- **The adversarial pass** before it's exposed: one agent whose brief is "get into a conversation you can't see, or post as someone you aren't".
