# Roc chat: auth, first draft

*Claude (the box), for Steve, 2026-10-28. A design to argue with, not a plan to execute. Your stated requirements are marked **(Steve)**; everything else is a proposal. **Revised with Steve's answers the same evening** (section 8).*

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
- **A public conversation:** anyone signed in can see it, and nobody signed out **(Steve)**.
- **Human-to-human conversations are always private (Steve).** Only human/agent and agent/agent conversations have a visibility to elect.
- **Agents can start conversations (Steve),** with humans or with other agents.
- **Who elects.** Humans elect **(Steve)**: for a human/agent conversation, its human; for agent/agent, the agents' owners.
  - My proposal: a conversation is public only while **every human involved** has elected public, and any one of them can make it private again. That's safe by default, and it means one owner can never expose another owner's agent's words.
  - Your DM with CC is the motivating case: you're the only human involved, so it's your call alone **(Steve)**.
- **Seeing isn't posting.** Public means readable, not writable. Posting stays with participants.

**Channels** wait **(Steve)**. When they come, a channel is a conversation whose participants are a roster, and `can_see` doesn't change.

**The test is the spec:** every kind of principal crossed with every kind of conversation (human/human, human/agent, agent/agent, bot), each in both visibilities, plus "elected public, then one owner withdraws". That's a few hundred cells, written as a table of expected answers. It's the "exhaustive tests over small domains" idea from the last essay, applied where it matters most.

## 5. Sign-up

**Open at first (Steve):** anyone with a GitHub account can sign in and create an account, giving a display name. No invites, until strangers become a real problem, which is unlikely. A new human sees only the conversations they're in, plus public ones. That makes open sign-up safe by default: it costs a stranger nothing and gives them nothing private.

Invites can come later as a gate in front of step 5 of the flow, without changing anything else.

## 6. Bots and the GitHub commit bot

**Bots are their own kind (Steve), and come after humans and agents.** The GitHub commit bot will almost certainly be the first one.

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

## 8. Steve's answers (2026-10-28)

1. **Public means signed-in users only.**
2. **Human/human conversations are always private.**
3. **Agents can absolutely start conversations.**
4. **Bots are their own kind,** lower priority than humans and agents; a GitHub bot will almost certainly be first.
5. **Sign-up is totally open at first;** users only need to identify as GitHub users. No invites until strangers show up.
6. **It runs with or without a domain; no domain for now.**

**What "no domain" means for auth (a technical note, not a question):**
- GitHub's OAuth app takes any callback URL, including an IP address and port, so the flow itself works without a domain.
- **The session cookie is the catch.** A cookie that must not leak needs HTTPS: `Secure`, and the `__Host-` prefix, which requires `Secure`. HTTPS on a bare IP needs a certificate for the IP. Let's Encrypt began issuing short-lived IP-address certificates in 2025, but whether Caddy on prod gets one cleanly needs checking.
- The fallbacks are worse:
  - plain HTTP, where a session cookie can be stolen on the wire;
  - or a path under lynrummy.com, which is a domain after all.
- So the design keeps `Secure` cookies, and the first deployment's job is HTTPS on an IP. The code stays the same either way: the host is told its public origin, and the Roc builds the callback and cookie attributes from it, so moving to a domain later is configuration only.

## How I'd build it (when you say go)

- **First, the pure core, with no network:**
  - `Principal`, `Conversation`, `can_see`, scopes, the key checks;
  - the OAuth `state` checks;
  - the exhaustive `can_see` table.

  All of it is Roc and `expect`s, testable in seconds.
- **Then the host primitives,** each with a small test, plus a fake GitHub for the flow's end-to-end test.
- **The adversarial pass** before it's exposed: one agent whose brief is "get into a conversation you can't see, or post as someone you aren't".
