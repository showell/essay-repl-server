# From today's chat to 100% pure Roc: the map

2026-10-28. A read-only survey: nothing was changed or committed.

**Sources:** roc-webbox `main`; angry-gopher-chat `box/roc-cleanup`; chat-markdown; zig-webbox; CC's open queue (292-302).
**Measured with:** `chat_reach.shale roots=chat` (6,198 code lines, plus markdown's 1,224, which the walker counts as outside) and `zig_census.shale`. The census found 28,198 live chat tokens and 3,817 unreached; 49 routes are the Roc's and 1 is Zig's (Asset); of the hosted functions, 16 are primitive, 22 are "primitive + decisions" and 3 are whole features.

## 1. Classification of the ~7,420 reached Zig lines

| class | lines | what |
|---|---:|---|
| **A** chat logic in Zig | ~1,000 | chat_upload's decisions (~365, QUEUE 292); chat.zig and chat_conv (200: the `.serve` arm, conv and tail checks); chat_sse's backlog replay (80), chat_frame.messageFrame (30), chat_count.numberIn/indexOf (16); chat_paths' visibility walk for search (visibleConvs, memberChannels, channelRosters, channelMembers: ~200); chat_store's torn-line and separator rules (~50); the body limits (16); membership (`principalAuthorized`, ~40) |
| **B** pure computation | ~1,680 | markdown 1,224; chat_codec 115 (a Roc twin exists: Transcript.roc); search_tokens 63 and search_index's pure part (~100: wordAt, holds, costs); chat_search's excerpt window (26); ustar plus the tar writer (~110); decimal 11; ChatMessage and kin (~30) |
| **C** host primitive | ~1,750 | webbox 900 (http 184, store 252, bus 150, sse 46, edge 43, signed* 143, mem_meter 72); auth 259 (HMAC, sessions, API keys, the site's secret); search_index state ~250; the upload's multipart stream and sniff ~150; presence 41; request_time 19; admit 25; counters ~64; gzip and its read ~38 |
| **D** seam glue | ~2,980 | chat_abi 1,116, chat_router 968, chat_route 353, roc_abi 158, sljmp 109, chat_hosted 41; chat_paths validators and joins (~175) and chat_store addressing (~60) that only re-check Roc values |

### What C should shrink to

- **Files:** read, read_at, stat, list, write, append (giving the size after), remove. Today 14 Call members each repeat `dead()`, the root join and `fail`, and four of the appends carry a rule (the torn line, the separator, the block address, the fault). That is about 40% decision or boilerplate.
- **The bus, streams and HTTP:** the bus and streams are already bare (publish; hold a key; serve bytes or a range). HTTP is bare too: header, query, body to a limit (the Roc should pass the limit, not a form tag).
- **Auth:** shrinks to "who is asking", a verified id or none. Whether that id is a Member or an Outsider is the Roc's decision, made from the kinds `list_accounts!` already hands it. The HMAC check and the secret stay.
- **Process-lifetime state** (the presence map, the search index, the rate limit, counters): this is state, not decision. Its decision parts are the online window, the 30 s retry, the rate and the excerpt; those are small.
- **Time and entropy:** both stay host primitives.

### D: can it shrink? Yes, by about half

Each call passes through three layers, not two:

1. Roc to the `roc_chat_X` export in chat_abi, which marshals the arguments.
2. The `Host` fn-pointer vtable: 1,053 tokens, plus 40 panic defaults (`noPublish`, …, about 1,100 tokens).
3. chat_router `Call.X`, which repeats `dead()` 40 times and the chat_root join 14 times.

The vtable exists only because roc-webbox can't import angry-gopher. A comptime host type would do the same job (`roc_chat.Seam(Call)`, exporting the symbols and calling `H.x` directly, with `@hasDecl` panics for a test host). That would delete the vtable and every default, and let `dead()` and the join each live in one place.

`roc glue` at our pin works, as QUEUE 280 found: ZigGlue.roc runs in 2.6 s and agrees with the hand-written records. It can't be the seam's source, for three reasons:

- It names anonymous records by a hash that changes when a record does.
- Its ownership model is per-argument incref/decref, where ours is an arena per call.
- The spec isn't shipped with the compiler.

So glue is a compile-time check, and it should cover every record (item 2 below).

## 2. Ranked queue items (after 292-302)

Tokens are Zig tokens as zig_tokens counts them. Each item is 1-2 h for CC.

1. **A topic's backlog replayed by the Roc.**
   - *Removes:* chat_sse.streamTranscript and backlogFrom, chat_frame.messageFrame, chat_count.numberIn and indexOf, chat_store.openStream (~1,000 tokens).
   - *Adds:* ~80 Roc lines. The resume cursor is a twin of `sse.resumeAt`, which uses std's parseInt with a saturating +1. Then Transcript.decode, Frame, and `render!` for each message. The `stream` decision carries the preamble and the frames.
   - *Verify:* goldens frozen on the old Zig for a fresh stream, `?since`, a junk Last-Event-ID and the maximum one, a refused block mid-transcript, and a missing transcript. Then `resumeAt`'s test table as a twin.
   - *Risk:* "backlog xor live" depends on the read and the subscribe happening in one host turn. Prove that on Linux with a test before relying on it.
   - *Depends on:* nothing.
2. **Glue holds every seam record.**
   - *Change:* extend 280's `chat_glue_test` to all 41 hosted functions, matched by signature.
   - *Removes:* nothing; it is a safety net for items 3, 4 and 8.
   - *Verify:* a planted field swap fails the test.
   - *Steve then decides:* whether the style guide's small-record limit goes.
   - *Depends on:* 297.
3. **One append primitive.**
   - *Change:* `append_line!`, `append_entry!` and `append_message!` become one `append!(path, bytes)` that gives the size after or a fault. The torn-line and separator rules move to the Roc (stat! and a 1-byte read_at!). `index_message!` takes the conversation's directory, which retires Call.resolved and address, ConvRec, and the chat_paths validators from the request path.
   - *Removes:* ~2,000 tokens. *Adds:* ~60 Roc lines.
   - *Verify:* the file goldens are byte-identical (reactions, feeds, transcripts, .count). The torn-line test moves into the seam tests.
   - *Risk:* the fan-out's "never fail the request" rule now has to come from asides.
   - *Can split into:* line plus entry, then message plus index.
4. **The Host vtable becomes a comptime host type.**
   - *Removes:* the vtable, the 40 `noX` defaults, `dead()` written per member, and the join written per member (~2,900 tokens).
   - *Verify:* both repos' tests, chat_crash_test, frozen runs, and item 2's check.
   - *Risk:* `@export` from a generic.
   - *Depends on:* 2 and 3.
5. **Membership decided by the Roc.**
   - *Change:* `check_member!` becomes `identify!`, answering `[Known(id), Stranger]`, and Accounts decides Member or Outsider.
   - *Removes:* ~270 tokens of users.zig from the chat's path.
   - *Verify:* router_identity and chat goldens, covering guest, agent, stranger and an unreadable kind.
   - *Cost:* `list_accounts!` runs on every member request. Measure it.
6. **`.serve` retires.**
   - *Change:* the asset becomes a Roc decision.
   - *Removes:* chat.zig, chat_conv, and the RouteRec, Family/Part/Tail mirrors and assertRocOrder in chat_route (~1,800 tokens).
   - *Verify:* the route corpus test, and the census showing 50 Roc routes and 0 Zig.
   - *Depends on:* 292.
7. **Operator counters as one primitive.**
   - *Change:* `count!(kind, text)` replaces count_malformed_channel!, count_dropped! and report_fanout_failure!, with the text written by the Roc.
   - *Removes:* ~900 tokens. *Adds:* about 40 lines of a generic table.
   - *Verify:* /admin/host goldens.
   - *Depends on:* 3, which settles how faults travel.
8. **Search scope from the Roc.**
   - *Change:* `search_words!` and `search_messages!` search the directories the Roc says the member sees, one `search_scope_add!` at a time, so visibleConvs leaves the chat's path (admin_search keeps it).
   - *Removes:* ~900 tokens.
   - *Verify:* a twin holding the Roc's list equal to visibleConvs over the fixture trees, and the search goldens.
9. **Markdown in Roc: M1 to M8** (section 3). About 8 items, 12-16 h in all.
10. **Tar framing in Roc.**
    - *Change:* the ustar header and padding are written in Roc; `bundle_add!` becomes `read!` plus `stat!`; the host keeps one `serve_gzipped!` primitive.
    - *Removes:* ~600 tokens.
    - *Verify:* a twin of `ustar.header` (long names, prefix split), and the download golden gunzipped, its tar compared byte for byte.
11. **Sweep the dead chat Zig.**
    - *Removes:* the census's 3,817 unreached tokens, after any twin whose oracle that code is has been frozen into goldens.
    - *Verify:* the census and the gates. Small.

QUEUE 294 (re-triage) is largely this list. Use this plan as its input, or retire 294.

## 3. Markdown in Roc

**Feasible at the pin.**
- The parser is byte-level parsing "at the door", so it works on `List(U8)` and needs no `Str.len`.
- `while`, `for` and `var` exist; the chat already uses them.
- `List.set` is in place on a unique list, so the inline pass's linked node list (an ArrayList with prev/next indexes) ports directly.
- Recursion is bounded by `max_block_depth = 16`.

**Two traps:**
1. Per-byte recursion could overflow the stack, and a stack overflow is not a crash sljmp can catch. Use loops.
2. Rendering on the dev backend may be several times slower than the Zig. Measure it in M8; Steve sets the bound.

**Size:** 1,224 Zig code lines become an estimated 1,800-2,400 Roc code lines with expects. Two pieces exist already: SafeImg.roc is a twin of `safeImgAt`, and Feeds has the fence grammar. Both should move under the markdown modules, so each rule has one home.

**Verification:**
- **The gate:** every frozen case in gold (10,103), adversarial (29) and dialect (3) renders to identical html through twin.roc. A new angry-gopher `markdown_twin_test.zig` prints only counts and FAILIDs, never message text. During M1 to M7 a ratchet file holds the pass count, which may only rise.
- **The hostility judge:** `workUnits` must be equal number for number on every case and on generated hostile shapes, so the Roc's verdict is the Zig's.
- **A differential fuzzer:** it hunts for differences; it does not gate.

**Items:**
- **M1:** the harness and ratchet, text and escaping, paragraphs and hard wraps, headings, fences.
- **M2:** code spans, MSG_ refs, URL and email autolinks with monotonic cursors, external-link attributes.
- **M3:** `[t](u)` links and the dangerous-URL rule.
- **M4:** emphasis: the delimiter stack, flanking, the rule of 3.
- **M5:** img and video through SafeImg, and the raw HTML block.
- **M6:** lists (tight and loose, nested, the depth cap) and blockquotes.
- **M7:** the budget, exactly; `hostileReason`; trusted rendering.
- **M8:** the switch. render!, render_preview!, check_hostile! and serve_rendered! retire; the Roc answers the 400 itself and counts it (item 7). This removes 1,224 lines plus ~800 seam tokens.

**Where it lives:** as flat `Md*.roc` modules in roc-webbox/chat for now, because the twin harness and the corpora are there and in angry-gopher. It should move to chat-markdown/roc, beside the Zig, as the dialect's one home, once a 1 h probe proves a Roc package dependency across repos at the pin. roc-webbox has none today (`packages {}` everywhere). The Zig renderer stays regardless for resume_page and safari_download.

## 4. What blocks 100% pure Roc after all of this

1. **State that outlives a call:** presence, the search index, the rate limit, counters. Today the Roc's memory belongs to the request. This needs either a host key/value primitive (bytes by key, the Roc owning the formats) or a platform that carries a Roc model from one call to the next. That is a design decision for Steve.
2. **Work at boot:** the search build and the count backfill. With no boot entry for the Roc, either add one or retire them (the Roc already recounts on a miss).
3. **Connections and big bytes:** held SSE connections, the bus, multipart to disk, range serving. These are I/O, and stay primitives.
4. **Crypto, secrets, entropy, the clock:** HMAC and constant-time compares, upload names, time.
5. **Rules shared with the Zig site:** sessions and login, accounts, admin search and retire. Porting only the chat's copy makes two homes for one rule.
6. **gzip:** keep it as a primitive. A Roc version using stored deflate blocks is easy but makes downloads larger; real deflate can't match Zig's bytes.
7. **The seam itself:** chat_abi, roc_abi and sljmp exist as long as the host is Zig.

**The minimal host** is webbox's ~900 lines plus a thin seam, offering about 15 primitives: request in, response out, hold a stream, publish; read, read_at, stat, list, write, append, remove; clock; random bytes; HMAC verify; key/value state; gzip; count.
