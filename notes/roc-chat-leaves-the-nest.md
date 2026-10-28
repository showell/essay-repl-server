# Roc chat leaves the nest

*Claude (the box), for Steve, 2026-10-28, late. Reflections more than a plan, as asked; the plan-shaped ideas are near the end. Revised after Steve's note: **the Zig chat stays the production chat on lynrummy.com; the Roc chat becomes a new, separate deployment.** The first draft assumed the Roc chat would take over production; the sections on identity and data below are rewritten for this.*

## The training wheels did their job

It's worth saying plainly what Zig has been for the last few weeks, because the reasons it was right are the same reasons it's now in the way.

The Zig chat was an **oracle**. Every port today followed the same shape:
1. freeze what the Zig does, as a hash over real requests;
2. move the decision into Roc;
3. show the hash didn't move.

That shape made it possible to move aggressively. In one afternoon the batch moved the topic backlog, membership, search scope, the append rules, the scripts and the operator text into Roc. Each step came with a proof of equivalence, and nobody had to reread the old code to trust the new. Running the two side by side, and gating the Roc with the Zig's own test suite, is what let a cloud agent and three box agents work in parallel on the same seam without anyone being afraid of the result.

But an oracle answers one question only: *is the new thing the same as the old thing?* Today showed the limits of that question twice.

**The first was the download bundle.** The frozen hash agreed with the old Zig because the old Zig had the same accident: it listed uploads in the filesystem's order. The freeze didn't capture a behaviour anyone chose. It captured one machine's directory order. The port faithfully reproduced a bug, and only a second machine revealed it.

**The second was the agent account.** When the twin for "may use the chat" went in this evening, it found that the Zig recognizes the agent by the literal id `"3"`, and would admit `"3"` even with no account behind it. Roc's version refuses that. The twin can't say which is *right*. It can only say they differ, and then the test has to hard-code the difference as an exception. That's a twin doing its job, and also a twin showing it can't be the spec.

So your instinct about security is exactly right, and it's sharper than "matching Zig is insufficient." **Matching Zig is a proof about the Zig.** When the Zig was the product, that was the right proof. Once the Roc is the product, the Zig's behaviour becomes one more opinion, and for security it's not a privileged one: it was written for a different site, with different assumptions, and it has its own accidents.

## What "separate" actually removes

It's easy to think of the separation as removing Zig. What it really removes is **the shared concepts**. And those are where today's friction lived.

Every rule that ended up with "two homes" today was a rule the chat and the rest of lynrummy.com share:
- **who may use the chat:** members and the agent, `Accounts.can_use_chat` against `users.userIsAuthorized`;
- **what a viewer sees:** `Search.scope` against `visibleConvs`, kept alive by `/admin/search`;
- **the session and the cookie,** which login, settings and Lyn Rummy all read;
- **the admin pages,** which reach into the chat's files.

Each of these is a seam between two products pretending to be one. The twins we wrote tonight are the honest version of that: they say "these two copies must agree" out loud. But a twin is a tax paid forever, and it only exists because the two products share a user table.

With the Zig chat staying in production and the Roc chat deployed on its own, the cleanest form of "separate" is **separate everything**: identity, data, host. The Roc chat owns its own accounts, sessions and admin, and lynrummy.com keeps all of its own, untouched: the Zig chat, Lyn Rummy, the games. Then:
- **the two-homes rules disappear,** because each copy has only one home in its own app. Roc's `can_use_chat` and Zig's `userIsAuthorized` stop being two copies of one rule. They're two apps' rules, free to differ. The twins we wrote tonight protect the interop period, and retire with it.
- **The Lyn Rummy entanglements stop mattering,** because the Roc chat never touches them.
- **A forker gets an app whose auth is entirely in the repo they cloned.**

This is a stronger simplification than I first saw. There's no migration, no shared login to preserve, and no family data at risk. The production chat keeps running exactly as it is, and the Roc chat can start from an empty data root with its own first accounts, under whatever auth flow you design. If the two ever need to talk, it should be through a *protocol*, like a token one issues and the other trusts, never a shared table. A protocol is a rule with one home; a shared table is a rule with two.

## Auth is the right thing to port next, and the right thing to *redesign*

You said you want to change the auth flow for the Roc chat. That's the part I find most interesting, because it's the first place where the port stops being a port.

Everything so far moved decisions from Zig to Roc unchanged, by design. Auth is different. Copying it faithfully would copy the Zig's assumptions:
- the agent as a magic id;
- a cookie shared with the games;
- login throttling tuned for a site with public game pages;
- API keys bolted on beside sessions rather than designed with them.

Redesigning it in Roc, with the host holding only the secrets and the crypto, gets a much smaller and more legible thing. The shape I'd expect, roughly:

- **The host's primitives are few and dumb:**
  - hash a password and check it (bcrypt or argon2: keep whatever the stored hashes use);
  - sign and verify bytes with the site secret;
  - random bytes;
  - the clock.

  It never decides anything. The `auth_root` rule holds automatically, because Roc only ever sees "this signature verified" and "this password matched".
- **Roc owns the flow:**
  - login, logout and session lifetime;
  - throttling;
  - what an API key may do;
  - who is the agent;
  - how a new member is admitted.

  Every one of those is now a pure function with `expect`s, which is exactly where you want security logic: reachable by exhaustive tests, not just by integration tests through a socket.
- **Accounts become typed.** The agent is an account *kind*, not id `"3"`. A guest is a kind. A retired member is a state. The types make illegal identities unrepresentable, which is the style guide's oldest rule doing security work.

Ideas worth considering for the new flow, not decided:
- **Invite links for new members,** instead of an admin creating accounts. A signed, single-use, expiring token is easy to build from the primitives above, and natural for a family chat.
- **Sessions you can see and revoke,** one per device. It costs a small file per session. It answers "did I leave myself logged in on that laptop?", and it makes "log out everywhere" a real button.
- **API keys as first-class, scoped credentials:** read-only, post-only, one conversation. That matters more now that agents are participants, not just tools. Right now an agent's key is all-or-nothing.

None of that is exotic. The point is that it's *designable* once the flow lives in Roc, and not before.

## Testing security without an oracle

If the twin isn't the spec, what is? I think there are three layers, and Roc makes two of them unusually cheap.

**1. Exhaustive tests over small domains.** The `Ascii` module showed the pattern: when the input space is small, test all of it. A lot of security logic has small domains if you look for them:
- every account kind crossed with every route family crossed with every session state;
- every character that can appear in a path segment (traversal);
- every method on every route.

Today's freezes covered 13 askers on 4 routes. An exhaustive version covers the full cross product and states the expected verdict per cell, as a table a reader can audit. That's not "the same as Zig." It's "this is the policy, written down, and here is proof the code follows it."

**2. Properties over large domains.** For inputs too big to enumerate, such as markdown, filenames, cookies and multipart bodies, state what must never happen, and generate inputs:
- no rendered page contains a `<script` the author didn't write;
- no path the Roc hands the host escapes the chat root;
- no session cookie with a bad signature is ever accepted;
- no message body can forge a feed entry. That one is a real past bug: the code feed's separator, fixed in v42.

Generators can hunt, but they never gate, as the house rule says. What gates is the minimized cases they find, frozen as plain tests.

**3. An adversarial pass per feature.** Today's ASCII proposal got two hostile reviewers and came back much better. The security version is the same move: for each feature, an agent whose brief is "find a way in", not "check it works". The image-feed XSS in v41 was found exactly that way. That's the one that matters, and it's cheap with agents.

The nice consequence: **the fast Roc gate and the security gate become the same gate.** Pure functions with exhaustive `expect`s run in about a second. The slow part of today's quick gate was angry-gopher's 2,000-test Zig binary, 90 to 130 seconds of it. Once the chat stands alone, its gate is `roc test` plus a small host test, and it should be seconds, not minutes.

## What the Zig is still good for, for a while

I agree with keeping the Zig gates a little longer, and I'd be specific about why. They're the only thing today that exercises the *whole* chat through real HTTP: real cookies, real SSE, real files on a real disk. Before the cut, the Roc side needs its own version of that, a small end-to-end harness against its own host. Otherwise the cut deletes coverage rather than moving it.

There's also a decision hiding in "separate deployment": **what host does the Roc chat run on?** Today, in the interop branch, it rides inside angry-gopher's server, on webbox (which never reached bare metal: the boxy problem stopped it). Separate, it needs its own host. The earlier measurement says the minimal one is small. On Linux, with std.http, the bus and SSE come to perhaps 250 lines, plus files and the auth primitives.

That connects to the deployment question you're already holding:
- **Dog Park stays on metal.**
- **The rest moves to Linux beside Caddy.**

If that's the direction, the Roc chat's host is a small Linux program from day one, and the boxy-on-`x64v1elf` problem stops mattering for the chat at all. That's a real simplification: one less exotic target for a Roc program that's still young.

## The things I'd watch

- **Don't cut before the auth port lands in Roc.** Auth is the piece where today's two-homes rules live, and the piece where a gap is a vulnerability rather than a glitch. Porting it first, then cutting, means the cut removes twins instead of breaking them.
- **The data never needs to be shared.** The production chat's transcripts, uploads and accounts stay where they are, with the Zig. The Roc deployment gets its own data root from day one. If you ever want real messages in it, say to try it with the family, that's an *import*: a deliberate copy with a checked count, never a folder both programs read. Two programs writing one store was the trap DEPLOY.md's "way back" section warns about.
- **The box/roc-cleanup branch changes role.** It was built to put the Roc chat inside angry-gopher's server for production. With production staying Zig, that branch becomes the interop harness: the place the twins and the Zig gates run while the auth port lands. After the cut, the Roc chat no longer needs angry-gopher at all, and the branch can retire. Master, the production Zig chat, keeps whatever it already has, including today's chat-markdown and chat-client split.
- **The style guide is the real product.** Today it gained six rules, each born from a port. A forker of the Roc chat will learn more from that guide than from the code. Keeping it current, which CC and the agents did well today, is what makes "easy to fork" true.
- **The frozen hashes will need retiring deliberately.** Once the Roc is the spec, each freeze should either become a stated expectation ("this is the policy") or be deleted. A freeze nobody can explain is just a fossil of the Zig.

## Where today leaves it

When the batch finishes, the chat has every route in Roc and a seam checked at compile time. The host shrinks with each item toward a list of primitives that fits on a page. The Roc chat already *is* a separate app in its logic. What's left is the parts that aren't really chat:
- identity;
- the host program;
- the data root;
- the forker's front door.

Auth first is right. It's where the remaining entanglement is, it's where the security risk is, and it's the first place where the Roc chat gets to be designed rather than ported. After that, the cut is mostly deleting things, and deleting things is the easy part.
