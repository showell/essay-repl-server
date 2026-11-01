# The browser that was already signed in

*roc-chat, 2026-11-01. Written by Claude (LC) for Steve at the day's stopping point.*

Most of today went into the shape of a conversation. The day ended with a
bug in sign-in. The two have more in common than it looks, and the second
one is the more useful lesson.

## Part one: agreeing on what a conversation is

The morning started with a model nobody had decided. Roc-chat had numbered
"conversations", with a kind, and a three-way one (conversation 3: Steve,
LC and Cloud) that belonged to no channel and had no name. The rule we
settled on took several rounds. I kept running ahead of it. I would state a
rule from the spike's code as though it were the design, or put four steps
on the screen before Steve had answered the first question.

The rule, once we agreed on it, fits in four sentences:

- Every conversation has a transcript.
- Every conversation has a topic.
- Every conversation has at least one participant.
- Some conversations, but not all, happen on a channel. DMs have one or
  two participants; three or more means a channel's topic.

After that, the code followed quickly, each step deployed and checked by Steve:

1. Conversation 3 became RocChatDev/initial-work.
2. Agents can be channel members.
3. Channel names and user names share one namespace.
4. Agent topics went away.
5. The conversation kind went away entirely, so a conversation without a
   topic can't be created at all, rather than being refused at runtime.
6. A one-off script cleaned the leftovers off prod. It worked on the first
   try.
7. Keys lost `only:`. A key now says who you are, and membership decides
   what you can reach.
8. The agents' hop limit moved to topics.
9. Humans got self-DMs; agents don't.

The lesson I wrote down from that part (it's in memory now): **agree on the
key noun first, ask one fundamental question at a time, and don't code
until we agree.** Each wrong turn this morning came from my side, from
treating what the code happened to do as a rule someone had chosen.

## Part two: the bug

Mid-afternoon Steve invited Bob. He opened the invite link in his normal
browser, the one signed in as Steve. Redeeming it signed that browser in as
Bob, and the Steve session was gone. There was no Log out button on the page
he landed on, so getting back meant deleting the cookie by hand.

Steve asked the right question: *"I don't know how our agent-review process
missed this."* Here is my honest answer.

### Why nothing caught it

Every test of sign-in and invites started from a **clean browser**:

- The host's sign-in tests start from an empty world: no accounts, no
  cookie. "Signing in again goes straight to a session" was tested, but in
  a browser that held nothing.
- The e2e invite step (step 69) has Alice redeem her invite in a browser of
  her own. That's the scenario the feature was designed for, so that's the
  one we tested.
- The agent-invite path *did* refuse a request carrying a cookie. Somebody
  thought about it there, but the human invite path was built separately and
  didn't ask the question again.

The reviews (cold agents, hunts, my own reading) all looked at what was in
front of them: is this function correct, is this name good, is this
boundary tight. None of them asked about the **user's journey**: what does
this browser already hold when it arrives? A reviewer reading `join!` sees
a function that redeems an invite and sets a cookie, and it does that
correctly. The bug is not in any line. It's in an assumption that never got
written down: *the browser arriving here is nobody*.

That's the same failure as this morning's, at a different scale. The spike's
code made an assumption ("conversations can be anonymous", "a browser at
/join is fresh"), and nobody decided it. Our doctrine already covers this:
*a default is a decision nobody made*. Here the default was "the arriving
browser holds no session", and it was invisible because no test ever
contradicted it.

### What changed

- `/join/name` and `POST /join` refuse a signed-in browser with a 409 that
  names who it is signed in as, and the invite stays unspent. Steve chose
  refusal over the alternatives.
- Every sign-in, through GitHub or a join, **ends the session the browser
  held first**. Before, signing in again left the old session alive, still
  usable from wherever that cookie had been copied.
- Log out is now on `/` and `/chat`, the pages a sign-in or a join lands
  on, as well as the top bar it was already in.

### How we know the returning-GitHub path is right

Steve's second question: the GitHub flow was tested before the Steve
account existed, so how do we know it does the right thing now that it does?

Reading the code, it already did: `GitHubSignIn.resolve` finds the GitHub id
already linked to an account and signs straight in as that human, with no
name form. But "I read it and it looks right" is a claim, not a proof. The
new e2e step (82, "one session a browser") tests it in a crowded world:

- Sam has a session in one browser.
- Jasper's invite is opened in Sam's browser, giving a 409 that names Sam
  and leaves the invite unspent.
- A fresh browser redeems it.
- Sam then signs in with GitHub from Jasper's browser and comes back as
  the same human id.
- Jasper's cookie is now dead, and Sam's other browser is still signed in.
- Log out appears when signed in, and not when signed out.

I broke the code twice on purpose (no refusal in `POST /join`; no ended
session in `sign_in!`). Step 82 went red both times, so it catches both
bugs, not just runs.

### The question to carry forward

For anything that touches a session or a cookie, the review checklist should
include: **what does the caller already hold?** A signed-in browser, a stale
cookie, a second tab, a session from another device. Most of our tests set
up exactly one actor in exactly one state. The bugs live where two states
meet.

## Still open for Steve

An invited human with no GitHub account whose session expires can only sign
back in through GitHub, and that makes a second account. Whether to link
accounts, and how, is a design decision rather than a bug, so it waits for
you.

## Where things are

| what | where |
|---|---|
| code | `~/showell_repos/roc-chat`, `main` at 203059c, pushed |
| prod | https://chat.lynrummy.com runs 203059c |
| checks | verify 161 of 161; e2e 83 of 83 |
| branches | the sign-in lane and branch removed after merging |
