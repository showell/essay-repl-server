# Where roc-chat and roc-markdown stand

*2026-10-29, evening. The state of the two new repos after a long day, what's between here and a chat people can use, and a first look at reorganizing the markdown package, which I think should come next.*

## In one table

| | roc-chat | roc-markdown |
|---|---|---|
| **What it is** | a standalone chat: a Zig host on std.http, all decisions in Roc | the chat's markdown, as a Roc package any app can import |
| **Size** | Roc: 24 app modules (11,405 lines) and 4 platform modules (438). Zig host: 29 files (8,734 lines, the seam's generated snapshot included) | Roc: 9 modules (3,235 lines). The judge: 2 Zig files (1,016 lines) |
| **Held by** | 1,704 Roc expects (roc-markdown's among them) and the host's tests, end to end against a real server and a fake GitHub | 1,413 frozen cases, the CommonMark and GFM spec corpora, 1,032 hostile cases, and gold's 10,103 real messages; `tools/verify.shale` runs it all in one command |
| **License** | UPL-1.0 | UPL-1.0 |
| **Serving** | nothing yet | nothing directly; production still renders with chat-markdown's Zig |

## roc-chat

**Built today, the host design's steps 1 to 5:**
- **The server:**
  - **Concurrency:** one task per connection, and "the turn", a single mutex held only while a handler runs.
  - **Deadlines:** for heads, bodies, idle connections and writes.
  - **Scripts:** the chat client's, served with their ETags.
- **The bus and SSE:**
  - **Gap-free:** a stream subscribes in the same turn as its backlog read, so no message is missed or duplicated.
  - **Bounded:** at most 64 streams; a reader 17 frames behind is ended.
  - **Pings** keep a quiet stream alive.
  - **Generic:** `platform/Sse.roc` knows nothing of chat, so any Roc app can use it.
- **Files:**
  - **Safe writes:** every write is atomic and synced, and folders are walked without following a link.
  - **Honest reads:** "missing" is never the same answer as "failed".
  - **Cleanup:** a crashed write's temporary files are swept at start.
- **Sign-in through the Roc:**
  - **Out of the turn:** GitHub's token exchange runs between two Roc calls, outside the turn.
  - **The core decides:** the 16-module auth core makes every decision.
  - **Secrets stay in the host:** signing, hashing and secrets are Zig. The Roc never holds a key, and the GitHub token never crosses the seam.
- **Crashes:** any Roc crash, including a stack overflow from deep recursion, is a 500 and the server keeps serving. 15 planted crashes prove it.
- **Topology:**
  - **The store:** `Store.roc` is the only module that names a file.
  - **Sign-in:** `SignIn.roc` holds its routes.
  - **The routes:** `main.roc` is the route table alone.
  - **Tests:** the core's tests share one cast of principals.

**Between here and a chat people can use**, the design's steps 6 to 9:
1. **Step 6, the smallest end to end.** Sign in, post, read, and a second client streaming live. This replaces both stubs. New records (transcripts, conversations) go into `Store.roc` from the start.
2. **Step 7, API keys.** The core already has scoped keys, generations and revocation. What's missing is minting from a session, presenting a key in an `Authorization` header, and the tests. This is what Steve's Claudes need to join.
3. **Step 8, breadth.** Port the rest of the frozen chat: topics, DMs, presence, reactions, recent, docs, admin with its audit, and a `Chrome.roc` page shell with the CSS check. Links is dropped. This is the biggest step. The frozen chat already did it once in Roc, so most of the work is moving code onto the new seam rather than writing it.
4. **Step 9, deploy.** chat.lynrummy.com behind Caddy, a systemd unit, the GitHub OAuth app, and an adversarial pass whose brief is "get into a conversation you can't see". **You own** the subdomain and the OAuth app.

**Decisions waiting on you:**
- whether the platform's `Chat` module becomes `Web` (it matters only if the platform is to be offered on its own);
- a design for leaving a conversation (later; nothing needs it yet).

## roc-markdown

**Where it is:**
- **Its own dialect now:**
  - It diverged from chat-markdown's Zig on purpose today.
  - Link targets balance their parens.
  - GFM pipe tables render.
  - A blank line inside a list item stays in the item.
  - Emphasis pairs as CommonMark says.
- **Agreement with the spec:**
  - 246 of 277 spec cases match CommonMark or GFM.
  - The other 31 are listed as deliberate dialect, and the check fails if the list goes stale either way.
- **A judge of its own:**
  - No Zig markdown is left in it, and no angry-gopher.
  - The fuzzer that needed the Zig as its oracle is gone.
  - A cheap replacement is noted for later: random input, checked only for crashes and time.
- **Gold:**
  - Re-frozen once today, every move explained without printing a message.
  - The moves: four tables, one link with parens, and 68 messages whose links now cost different work units.
- **The remaining gaps are dialect,** your call: nested link brackets, a code span taking precedence over a link's brackets, lazy continuation in nested quotes, and four tiny edge cases.
- **Docs mode gets minimal effort** until you start using it.

**Production is still Zig, and stays so.** v44 serves the Zig renderer, with today's paren fix.

## The markdown package's topology: what I see

I read the package's shape (not yet every line, as I did for the chat). The same kind of review would find this:

| Module | Lines | What it holds |
|---|---|---|
| `Md` | 1,082 | every block kind (paragraphs, headings, fences, lists, quotes, tables, raw HTML), their dispatch, the public API, the modes |
| `MdInline` | 1,096 | the emphasis engine; links and their parens; autolinks and their URL and email ends; code spans; the chat's `MSG_` references; the dangerous-URL check; every inline tag |
| `MdText` | 180 | the work budget, escaping, and byte classes |
| `MdFence` | 153 | where a fence opens and closes |
| `MdMedia` | 309 | the one place a member's tag gets through: a same-origin `<img>` or `<video>`, rebuilt |
| `MdTable` | 102 | a table row's cells and alignments |
| `Ascii`, `Bytes` | 305 | byte helpers, still headed "as Zig's std.ascii / std.mem has them" |

**What forks will want to change, most likely first:**
1. **The HTML it emits.** Classes and tags for a skin: a table wrapper for scrolling, a class on code blocks, different link attributes. Today the tag constants are spread across `Md` (`p_open`, `br`, `heading_space`, the table cells) and `MdInline` (`a_open`, `em_open`, `strong_open`, `code_open`, `external_attrs`). **An `MdHtml` module holding every tag and attribute** makes a skin one file. It's also what chat-client's contract will check the markdown classes against.
2. **The dialect's chat-specific extensions.** `MSG_` references, the `~~~ quote` fence, and same-origin media. Each is ours, not CommonMark's. A fork building a non-chat app wants them off, and a fork building a different chat wants its own: `@mentions`, `#channel` links, emoji shortcodes. **Gathering the extensions into one module** (`MdChat`, or a small record of hooks the renderer consults) separates "markdown" from "our chat's markdown". It's an indirection, but a cheap one per call.
3. **Safety policy.** Dangerous schemes, which links are external, and the media origin rule. Today these sit inside the inline pass. **One `MdSafety` home** is easier for us to audit, and the first thing a security-minded fork reads.
4. **Adding a block kind** (callouts, details and summary). `Md`'s block dispatch would read better as a dispatcher over block modules. Lists and quotes are the container blocks, with the depth and laziness rules, and they're most of `Md`. They'd move to `MdList` and `MdQuote`, leaving `Md` as the API, the modes and the dispatch.
5. **The inline pass splits along its seams.** The emphasis engine (delimiter runs, the floor, flanking) is self-contained and the hardest code in the package, so it becomes `MdEmphasis`. Links, autolinks and parens become `MdLinks`.

**Ergonomics first, as you said.** Each split above is along a line the code already has. None adds a layer that every change has to pass through.

**Speed.** The judge already prints its time: about 44 s without gold, mostly the 8,191-size hostile shapes. A refactor held to "within 10% of that, the same work units and the same HTML for every case" can't slow things down unnoticed. The extra function calls cost nothing measurable at chat sizes.

**Behavior.** It's preserved by construction: all 1,413 frozen cases and gold's 10,103 must hold byte for byte, with no re-freeze allowed. That's the cleanest refactor setup we have anywhere.

**Your call, as you said, so here's mine: do it next, before step 6 needs the renderer.** The dust has settled: CC's tables are merged, gold is re-frozen, and the judge stands alone. It's a good long chunk for CC with the verify-script finish, the plants and "no re-freeze" in the script. Or it's local agents, now that the box is free. I'd have it finish before any new syntax lands, so new syntax arrives into the new shape.

## How the work itself moved today

- **CC's new finish works:**
  - **Proof:** a committed `verify.shale` with plants.
  - **The box's part:** one command, plus gold.
  - **Steady state:** CC now runs every test as a `steve` user, and a test that means nothing as root fails loudly there.
  - **The remaining manual step:** explaining gold's moves before a re-freeze. That's inherent: only the box can see gold.
- **The gates caught our own text.** A QUEUE path in backticks is a claim the release's doc check holds, and v44's first gate run failed on mine. The doc check now knows the new repos, and the lesson is in memory.
- **Branch cleanup is a recipe.** `shale cookbook:branch_prune.shale` deleted 27 merged branches, keeping 11 that still have real commits.
- **Production:**
  - **v44 is live,** with the paren fix and Links gone.
  - **v45 is lined up:** the Cobblestone apps removed (11.8% smaller, 24% faster to build), `>` as quote-reply, and chat-client's contract.
