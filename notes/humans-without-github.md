# Humans without GitHub: invites, reserved names, no passwords

*2026-10-31. LC, a design draft for Steve to steer. Nothing here is built.*

## What Steve asked for

- **Anyone with a GitHub account can join today.** A human without one,
  so far only Steve's sister, joins by invite, and **any human member may
  invite** their friends.
- **No passwords at first.** Debbie signs in only from the device where she
  redeems her invite, and stays signed in as long as she isn't idle for more
  than 30 days at a time.
- **Names are unique, caselessly,** and that invariant is absolute. An
  invite reserves its name at once: Steve types "Debbie", and the name is
  hers before she ever sees the link.
- **Redeeming shows her name already filled in.** She can keep it, or
  change it to "Debra" or "Debbie Benton" if that name is free.
- **The redeem page explains sign-in simply.** The first paragraph is plain
  words: no password, this device, 30 days. All the mechanism follows as
  fine print, styled as fine print.
- **The invite carries a welcome.** Steve picks a topic (default `ChitChat`)
  and a message (default "Hi! This is an automated message from Steve"),
  and the conversation exists at once, so Steve can add more before Debbie
  arrives. Cleaning up unredeemed conversations comes later.

## What roc-chat has today, and what has to change

| Today | Has to become |
|---|---|
| A display name is any visible text, and two people can share one. Look-alikes are left alone on purpose (`DisplayName.roc`) | Unique across the system, compared caselessly. That's a new rule on top of the existing one |
| A human *is* their GitHub id: `Principal.Human(GitHubId)`, and wire ids like `human:142908` are GitHub ids | A human has an id of roc-chat's own. GitHub becomes one way to sign in |
| A session expires after a day idle, measured from its last use | Debbie needs 30 days idle |
| Agents have single-use, ten-minute invites. Humans have none | Human invites: longer-lived, carrying a reserved name and a welcome |
| Conversations have fixed participants and no topics; channels with topics are being built | The welcome needs a two-person conversation with topics, a DM |

The second row is the deep one, and the clean slate makes it cheap to do
properly: no existing ids need carrying over.

## The proposal

### 1. One namespace of names, compared caselessly

- **Every principal's name is unique:** humans, agents and bots, all in one
  namespace. That also ends the spoofing the JS audit found: no agent can
  be called "Steve Howell" while Steve is.
- **"The same name" means equal after folding case and collapsing runs of
  spaces.** So `debbie`, `DEBBIE` and `Debbie` are one name, and so are
  `Debbie Benton` and `Debbie  Benton`. The name keeps the spelling it was
  given, for display.
- **Look-alikes from other scripts stay allowed,** as now (a Cyrillic "А" in
  "Аnn"). The kind-and-owner label is the defence there. Folding them too
  would need a confusables table, which isn't worth it yet.
- **A name is held by an account, live or reserved,** and is released only
  when its account is deleted. A renamed account frees its old name.

### 2. Humans get roc-chat's own ids

- **`human:<n>` comes from a counter,** like agents' ids today, and is never
  reused.
- **An account records how it signs in.** For a GitHub user that's the
  GitHub id, which sign-in maps to the account. Debbie's account has
  none, only device sessions.
- **The rest of roc-chat keeps asking `answers_to`** and the account's
  binding. Only identity and sign-in change. Moving everything else over is
  mechanical, and the clean slate means no existing data needs migrating.

### 3. Human invites

- **Any human member** makes one with a name, a topic (default `ChitChat`)
  and a welcome message (default "Hi! This is an automated message from
  <inviter's name>").
- **At once,** with nothing left half-made if any step fails:
  - a **reserved** account is created, holding the name;
  - a **DM** between the inviter and that account is created, with the topic;
  - the welcome is posted there, as the inviter;
  - a **single-use code** is made and shown to the inviter once, as a link
    to send by text or email.
- **The code lives 7 days** (proposed), and can be revoked from the inviter's
  page. A lapsed or revoked invite leaves the reserved account and its DM in
  place for the later cleanup.
- **Caps,** as for agents: a human may have a few unredeemed invites open
  at once (proposed: 10), so nobody can reserve a thousand names.
- **Audited** like agent invites, never with the code.

### 4. The link, and keeping the code out of logs

The link is `https://chat.lynrummy.com/join#<code>`. The code sits after the
`#`, which a browser never sends to the server, so it can't land in Caddy's
access log or a referrer header. The page's script reads it and sends it in
the body of the redeem request. That keeps it out of logs and URLs,
where a code in the path wouldn't be.

### 5. The redeem page

**The first paragraph, a draft** (plain, large):

> **Welcome, Debbie!** There's no password to remember here. Pick the name
> people will see, and you're in. You'll stay signed in on this phone or
> computer as long as you use the chat at least once every 30 days.

Then the name box, filled with "Debbie", and one button: **Join**.
- If she changes the name to one that's free, it's hers, and "Debbie" is
  released.
- If the name is taken, she's told plainly and asked for another.

**The fine print** (small, muted, below):
- Signing in is tied to this browser on this device, by a cookie the chat
  sets when you join. Clearing your browser's cookies for this site signs
  you out.
- Being away for more than 30 days in a row also signs you out.
- If you're signed out, or want to use another device, ask <inviter> (or
  any admin) for a new invite link. It signs you back in to the same name
  and the same conversations.
- The link you were sent works once and lasts 7 days.
- No password is stored anywhere.

### 6. Sessions

- **A device session for an invited human expires after 30 days idle,**
  measured from its last use, with no fixed lifetime beyond that.
  Otherwise Debbie would be locked out on a schedule she can't see.
- **GitHub users keep a day idle** (proposed): they can always sign in
  again, so a short window costs them nothing and lowers the risk of a
  stolen cookie.
- **A re-invite:** the inviter or an admin makes a sign-in invite for an
  existing invited human. It has the same link and page, the name is
  already fixed, and it adds a session on whatever device redeems it. This
  covers a lost phone and a second device alike.

### 7. The welcome DM

The welcome needs a two-person conversation with topics. That fits the
channels work: a **DM** is a pair of humans with human topics, using the
same topic machinery, transcripts and message ids as a channel. Its
message references stay short-form, as Steve decided for DMs. So human DMs
join the channels plan, as a second container beside channels.

## Questions for Steve

1. **Should agent and bot names share the one unique namespace with
   humans?** That's proposed, and it ends name spoofing.
2. **What counts as "the same name"?** Proposed: case folded and runs of
   spaces collapsed; look-alikes from other scripts still allowed.
3. **Invite code lifetime:** 7 days (proposed)? And a cap of 10 unredeemed
   invites per human?
4. **Idle windows:** 30 days for invited humans and a day for GitHub users
   (proposed), or 30 days for everyone?
5. **Who can sign a lost Debbie back in:** her inviter and admins
   (proposed), or any member?
6. **Should invited humans be able to invite others in turn?** Your
   "any human member" says yes, but this means anyone can reach the
   chat through a chain of invites. That's fine at your scale, and worth
   saying out loud.

## A possible order

1. **Names unique and caseless,** across all principals: the invariant first,
   since everything else relies on it.
2. **Human ids of roc-chat's own,** GitHub as a sign-in method (a CC chunk).
3. **Human DMs with topics,** beside channels.
4. **Human invites, the redeem page, 30-day device sessions and re-invites,**
   with e2e steps and a planted fault per refusal.
