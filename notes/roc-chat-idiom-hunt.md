# The Roc chat, hunted with Roc's own parser

*2026-10-27. Branch `box/roc-cleanup`, roc-webbox `cbb9328`. Nothing here is changed yet: these are the findings and what I'd do about each, for you to decide.*

## The tools

- **`roc-ast`** (roc-webbox `tools/roc_ast/`) prints the parse tree of any `.roc` file, using roc-lang/roc's own `parse` module at the exact commit `roc-version` pins (258ab27, nightly 2026-10-09). So the tree is what our compiler accepts, not a guess.
  - It's built with Zig 0.16.0, because that Roc's `build.zig` refuses 0.17; Shale itself is still on 0.17.
  - `shale tools/roc_ast/install.shale` checks the pin and installs it at `~/tools/roc-ast/bin/roc-ast`.
- **`hunt.shale`** (`tools/roc_hunt/`) holds six hunts, one named function each, and reads the trees once.
  - Each hunt has a plants file of Roc snippets. The `fires_` ones must be found and the `quiet_` ones must not, before its findings count. All six pass.
  - It covers the production modules (`chat/*.roc`, `chat/platform/*.roc`), not the twin or the test probes.
  - `tools/README.md` indexes all of it.

| Hunt | Found |
|---|---|
| same_typed_args | 68 |
| magic_numbers | 139 definitions |
| bools | 21 |
| positional_lists | 14 |
| if_chains | 15 |
| long_definitions | 1 |

## 1. Neighbouring arguments of one type (68)

Agreed already: nominal types for the four ids that run through everything, and records where a function assembles something from several strings.

- **Nominal `Uid`, `ConvKey`, `Sid`, `ChatPath`.** These cover most of the risk: `pinned_path(uid, key)`, `transcript_path(dir, sid)`, `dm_title(me, key)`, and `Host.write!(path, bytes)`, `publish!(key, bytes)`, `append_line!(path, line)`. Once they're nominal, a swap is a compile error.
- **Records:**
  - `Fanout.notify_event` (4 strings in a row) and `topic_added` (3);
  - `Pages.shell`, `no_topics`, `not_found` (3 each);
  - `Reaction.line` (3, plus a `Bool`);
  - `appended!` (4), `store!`, `announce!`;
  - `Time.days_from_civil(y, m, d)` becomes `{ year, month, day }`.
- **Left alone:**
  - the byte helpers (`find(haystack, needle)`, `starts_with`, `split_seq`), which have `Str.starts_with`'s shape;
  - the comparators (`Recent.before(Row, Row)`, `Bytes.less`);
  - plain maths (`div_floor`).
- **To check first:** whether a nominal type crosses a hosted function as its backing bytes. If it doesn't, `Host.roc` keeps `List(U8)` and the wrapping happens at the edge.

## 2. Magic numbers (139 definitions)

They fall into four groups. Most of them are bytes.

**Bytes written as numbers (most of them).**
- Examples: `95` for `_` (pair keys, ids), `47` for `/`, `10` for newline, `32` for space, `34`, `38`, `60` and `62` in the HTML and JSON escapers, and `48` to `57` for digit ranges.
- Roc at the pin has character literals, and `'_'` types as `U8`, in `match` patterns too. I checked.
- **Fix:** mechanical. `95` becomes `'_'`, `[49]` becomes `['1']`, and `b >= 48 and b <= 57` becomes `b >= '0' and b <= '9'`.

**Lengths tied to a literal.** `Route.under_chat` does `if starts_with(sub, "/search") { with_rest(Search, drop(sub, 7)) }`. The `7` is `"/search".len`, kept in sync by hand. `drop(sub, 5)` after `"/msg/"` and `drop(sub, 3)` after `"/c/"` are the same.
- **Fix:** a `strip_prefix(sub, prefix) : Try(List(U8), [NoMatch])` that returns the rest. The `7` disappears, and so does the 7-deep `if` chain (see section 5).

**HTTP statuses.** `200`, `204`, `400`, `409`, `303` appear in `main.roc` and `Chat.roc`.
- **Fix:** a closed `Status` tag (`[Ok, NoContent, BadRequest, Conflict, ...]`), with one function that gives the number at the seam. The answer then says what it means, and a status we never send can't be typed.

**Real constants.**
- `Time`'s calendar arithmetic (`719468`, `146097`, `153`...) is Howard Hinnant's `days_from_civil`. Those numbers are the algorithm: I'd name the function's source and leave them.
- `86400` and `3600` become `seconds_per_day` and `seconds_per_hour`.
- `Recent.excerpt`'s `350`, `ChatState`'s `255` and `Reaction`'s `16` are limits. Each gets a name, and a comment where it mirrors Zig.

## 3. Bools (21)

- **Arguments:**
  - `pin!(…, pinned : Bool)` and `repin!`;
  - `Reaction.line(…, on : Bool)`, a reaction added or taken back;
  - `store!(…, Bool)`;
  - `Chat.zig(route, presence : Bool)`.
- **Fields:**
  - `Answer.presence` and `nosniff`;
  - `Route.channel`;
  - `Recent.Row.doc` and `dm`;
  - `online` (three places);
  - `Count.current`;
  - `Host.body!`'s `ok`.
- **Fix:** each becomes a two-tag union that says which:
  - `[Pinned, Unpinned]`, `[Add, Retract]`, `[CountsAsPresence, Silent]`;
  - `[Sniffable, NoSniff]`, `[Dm, Channel]`, `[Online, Offline]`;
  - `ok` becomes `[Read, Failed]`, like the file statuses.
- **Exception:** `JsonText.bool` writes a JSON `true`/`false`, so its `Bool` is honest. It stays.
- **At the seam:** a payload-less tag crosses as one byte, so this works at the seam too.

## 4. Lists read by position (14)

- **The real ones:**
  - `Recent.rows_from` reads the host's rows as nine fields each (`doc, secs, uid, name, key, label, topic, markdown, dm`), by index `at(0)` through `at(8)`.
  - `Pages.decode_sidebar` and `counted` read `uid, "1"/"0", key, base, sid, count, others…`, with `at(6 + 3 * k)` arithmetic.
  - `Paths.rosters_from` reads `name, count, member…`.
  - `Chrome.find_src` reads `name, src` pairs.
- **Why they exist:** each is the shape a hosted function returned when everything crossed as `List(List(U8))`.
- **Fix:** records already cross the seam (`Chat.Conv`, `accounts!`'s account records, the file listings' entries). So `recent!`, `srcs!` and `message_parts!` can return a list of records, and the decoder goes away with its index arithmetic.
- **About to go anyway:**
  - `decode_sidebar` is now used only by the twin, since `page!` moved to Roc. When the twin compares records, it can go.
  - `rosters_from` goes when `channel_rosters!` returns `{ name, members }` records.
- **False positives:** `Bytes.split_byte_from`, `Feeds.blocks_from` and `quotes_from` walk lines by index. That's a loop, not a layout, and I'd leave them.

## 5. If chains (15)

- **Worst cases:**
  - `Route.under_chat`, 7 deep: one comparison per path prefix, which becomes the table from section 2;
  - `ZigText.escaped`, 8 deep: one per escaped byte, which becomes a `match` on character literals;
  - `Html.escape`, 5 deep: the same.
- **After character literals** these become exhaustive `match`es:
  ```roc
  match b {
      '"' => ['\\', '"']
      '\\' => ['\\', '\\']
      '\n' => ['\\', 'n']
      ...
  }
  ```
- **In `main.roc`:** the 3-deep chains in `make!` and `store!` decide an HTTP answer from several checks. Some of those are really a `Try` chain with `?`, and I'll look at each one.

## 6. Long definitions (1)

`appended!` (C8a's send) is 61 lines: id, stamp, block, render, frame, store, publish, fan-out. It already reads as numbered steps, so the fix is to split out the fan-out half once C8b's code settles. It's low priority.

## Order I'd do it in

Each step is a cold agent, held by the twins and mutants as before, with the gate lints in both repos.

1. **Character literals and `strip_prefix`.** Mechanical, the biggest readability win, and it unblocks the `match` rewrites.
2. **`match` for the escape and route chains.**
3. **Records out of the hosted functions** (`recent!`, `srcs!`, `channel_rosters!`, `message_parts!`), deleting the positional decoders.
4. **Bools to two-tag unions**, and `Status` as a tag.
5. **The nominal types `Uid`, `ConvKey`, `Sid`, `ChatPath`**, and records for the multi-string builders. This is the biggest diff, so it goes last, once everything else has settled.

After each step, rerun `hunt.shale`. The counts should fall, and whatever remains is a decision we made, not an oversight.
