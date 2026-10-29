# The turn toward roc-chat

*2026-10-29. An open-ended look at how the work's focus moved over the last two days. Where I don't know something, I say so; the questions at the end are real.*

## The old question and the new one

Until about a day ago the question was: *how much of the production chat can move into Roc?* The work on angry-gopher's `box/roc-cleanup` answered it well. On that branch, all 50 routes became Roc's, and the chat's Zig shrank from roughly 28,700 tokens to about 21,200. Every step was held to Zig twins and a gold corpus of 10,970 real messages. None of it was ever released: lynrummy.com ran, and still runs, angry-gopher's master, which is all Zig.

The new question is: *what would a chat look like if it were Roc from the start, for people who want their own?* That is a different project. The two-day pivot is mostly the discovery that the first question had been a rehearsal for the second.

Three decisions made the turn:

- **Production stays Zig.** lynrummy.com's chat keeps its Zig, its bare-metal unikernel and its users. The paren fix that went into chat-markdown today is a production fix, and it may be one of the last interesting changes to that renderer.
- **roc-chat is a new deployment,** not a replacement. It's Linux only, forkable, and will live at chat.lynrummy.com. It has its own accounts, its own auth and its own data.
- **Its host is first principles.** It's written fresh on `std.http`, cribbing from webbox rather than depending on it as a package.

Each of these gives something up. Together, I think, they buy the ability to make roc-chat *simple*, which the hybrid never could be: every simplification there had to keep production's shape.

## What the interop period was actually for

It would be easy to call the port to production's Roc a detour. I don't think it was. What it produced was not a chat; it was **trust in a particular way of building one**:

- the comptime host type (`Host.of`), where glue checks every seam record;
- the frozen-answers markdown judge;
- an auth core in pure Roc that survived three adversarial rounds;
- a style guide written in arguments with real code;
- a feel for where Roc at this pin bites. `Str` has no `len`. `roc build` defaults to LLVM, which took 5 minutes against 0.9 seconds with the dev backend. A one-tag union crosses the seam zero-sized.

All of that transfers to roc-chat, mostly by copy. `host/seam/` in roc-chat is about 740 lines cut down from roc-webbox, and each file cites where it came from. The interop period's job, in hindsight, was to pay for those lessons against a judge that couldn't be argued with: production's own behavior.

## The audience changed, and auth followed it

The production chat is for people. roc-chat is first for **conversations involving agents**: human/agent and agent/agent, then bots in the Zulip style, with a GitHub commit bot first.

That one sentence reorganizes the auth design:

- **API keys are first class,** not an afterthought bolted onto cookies. Steve's Claudes get admin keys.
- **Sign-in is GitHub,** which removes passwords from the design entirely, and with them a whole category of things to get wrong.
- **Visibility is per conversation** and coarse: Private or Public, where Public means signed-in users. A conversation between two humans is always private, and admins don't see private conversations.
- **Retirement is a ban for life.** It's the conservative choice, and the one that keeps the code smallest until a softer rule is actually needed.

There's a pattern here worth naming. Each of these choices **removes a state** rather than adding a feature. There's no Unbar, no password reset, no invite tokens, and no visibility levels between the two. It's the "eliminate, don't paper over" doctrine applied at design time instead of at debug time.

## The markdown changed what its judge means

For weeks the markdown judge asked: *does the Roc agree with the Zig?* As of today it asks: *does the Roc agree with what we froze?* The Zig stays as production's renderer, and roc-markdown may diverge from it. Any gap the corpora find beyond the paren fix is fixed in Roc only.

This is a bigger shift than it looks:

- A twin judge borrows its authority from the other implementation. A frozen-answers judge has authority only because someone decided, case by case, that an answer was right. `--refreeze LABEL` names every case that moved, and that makes the decision visible instead of implicit.
- The cost is that the oracle is now *us*. A wrong answer frozen in is as durable as a right one.
- The CommonMark spec cases, 269 of them with 230 agreeing so far, are the outside check that keeps this honest.

Tables are on everywhere as one dialect, and a docs mode is coming. Both make roc-markdown less a port and more a product, one that can render the Roc tutorial and FAQ as they're written.

## Deliberate copies

One home for a rule is a doctrine here, and the turn breaks it on purpose in three places:

- `Ascii` lives in both roc-markdown and the chat;
- the seam is a copy cut down from roc-webbox;
- markdown's Zig and Roc may now disagree.

I think this is right, and the reason is worth stating so it doesn't decay into habit. **A copy is a bug when it is supposed to stay equal to its source and nothing checks that it does.** These copies are not supposed to stay equal: each is the start of a fork, and the forks are what we want. The `roc-bytes` or `roc-util` package waits on the build decision for the same reason. Sharing code across repos before the dependency story is settled would create a coupling we would have to undo.

The risk is the middle case: a copy everyone *assumes* stays equal. Shared security logic is the one to watch. If an auth rule ever lives in two places, it needs a judge or a single home, not good intentions.

## How the work itself changed

The other shift is in who does the work and how much happens at once. Two days ago the pattern was mostly one agent at a time, verified closely. Today four ran in parallel on the box, each with one deliverable:

- the Zig paren fix;
- markdown step 2;
- roc-chat's skeleton;
- the auth primitives.

The constraint that made it work was not the box's cores. It was **briefs narrow enough that the agents never touched the same files**. The one collision so far was harmless and instructive. The skeleton agent noticed an uncommitted edit in roc-markdown, which belonged to the markdown agent, and *reported* it instead of working around it. That's the behavior the briefs asked for. I don't know yet whether it holds when the scopes are less cleanly separable.

CC's role moved too. It went from the main worker on the census to a specialist on longer, self-contained chunks: Shale's budgets, and chat-client's contract. That fits what CC is good at, and it fits what it can't do: CC's sandbox can't build `roc-ast` or fetch Roc's releases.

## What I'd watch

- **The pure-Roc goal against the first-principles host.** The host is Zig, and today it's about 650 lines plus a 740-line seam, with the auth primitives arriving next. The goal is a 100% Roc backend, and "pure" is measured at the seam: Roc makes every decision, while the host keeps secrets, crypto, sockets and files. The thing to watch is the host quietly growing decisions because Zig was where the code already was. The census tools from the interop period could be pointed at roc-chat to keep that honest.
- **The learning-curve promise.** "A Roc developer, with an agent, can fork this and run their own chat" is testable, and we haven't tested it. A cold agent given only the repo and the README, asked to stand up a copy, would be a good judge once the deploy story exists.
- **Dependencies by sibling path.** roc-chat builds against whatever the neighboring checkouts hold. That's fine for us and wrong for a fork. The pinned-tarball plan (D2) is the fix; the question is when.
- **The UPL license** is now on chat-markdown, and is coming to roc-chat in the merge running now. It's the same license as Roc, which makes copying between this work and Roc's ecosystem friction-free in both directions. That seems to fit the forkable intent.

## Open questions

These are for thinking, not for deciding today:

1. When roc-chat is running, does the production chat *ever* move onto it, or are they permanently two products with a shared ancestor?
2. Are bots a kind of agent with narrower keys, or something different enough to deserve their own principal? The auth core has a `Principal` type; bots are the first thing that might strain it.
3. Should agent/agent conversations be visible to the humans who own the agents by default? Today that falls under Private or Public like everything else.
4. How much of roc-markdown's docs mode belongs in chat at all, versus in a docs site that happens to share the renderer?
