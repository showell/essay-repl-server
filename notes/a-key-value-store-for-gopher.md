# A key/value store for gopher (search, draft 2)

*2026-10-10, late night. The second draft of
[searching all of chat](searching-all-of-chat.md), after Steve's notes:
indexes may lag by N seconds, autocomplete must not leak by construction,
a key/value store is the first thing to build, it lives in angry-gopher,
values may be Zig structures rather than JSON, and English means some
ASCII bias is fine. Mostly about the store; search is its first user.*

## Decisions since this draft (Steve, 2026-10-10)

This draft proposed the store first. Its first user turned out not to need it:

- **Search's index lives in memory, derived from the transcripts**, which
  stay the only source. It needs no log: lost on restart, it is rebuilt.
- **Built at boot.** If that gets annoying, it becomes lazy: requests come in
  first, and the index is built at the first search or in the first **idle
  window**.
- **An idle window, eventually a first-class host feature**: chat is bursty
  and idle most of the time, and work that isn't time-critical (an index
  build, compaction, a check) belongs there, in slices, between requests.
- **A new message updates the index as it's appended**, in memory, with no
  disk writes, so there's no N-second lag after all.
- **Search covers what `visibleConvs` lists** (angry-gopher `chat_store`):
  DMs with other members who have passwords, and the viewer's channels. No
  self-DMs, no DMs with passwordless accounts, for now.
- **`/admin/search` is the baseline** (angry-gopher `017b6801`): no index,
  reads every transcript the admin can see. Every smarter search must agree
  with it.
- **The key/value store waits for a user that is a source**, not a derived
  value: the sidecars (`last-seen`, `last-sessions`, `.count`), if we fold
  them together.

The rest of this draft stands as the store's design for that day.

## What production says about memory

From `/admin/host` tonight:

- **997 MB of memory, 90 MB of it in use** (98 MB at most since boot).
- **The chat volume holds about 206 MB**, nearly all of it uploads.
- **The data's page cache holds 100 files in 16 MB** after five hours of
  traffic, so transcripts are small.

So **all of chat's text fits in memory several times over**, and so would
every index we'd build over it. That changes the question from "how do we
page an index in and out" to "what do we keep on disk, and in what shape, so
that memory can be rebuilt at boot." Ordered files on disk (the
alphabet-range question) can wait until memory stops being enough, which at
this size is years away. The store's interface should still be ordered from
day one, so that day changes the inside, not the callers.

## The store

### What it is for

A small, durable map from keys to values, **owned by the application**
(angry-gopher, over `store.zig`, so the same code runs on both hosts and is
judged the same way). First user: search's indexes. Later users, if it
earns them: the sidecars that are each a file today (`.count`, `last-seen`,
`last-sessions`, `last-conv`), which are most of a chat send's disk writes.

### The interface

```zig
pub fn get(kv: *Kv, key: Key) ?Value            // from memory, never the disk
pub fn put(kv: *Kv, key: Key, value: Value) !void  // durable before the response
pub fn delete(kv: *Kv, key: Key) !void
pub fn range(kv: *Kv, from: Key, to: Key) Iterator // keys in order: prefixes, scans
```

- **Keys are bytes, ordered bytewise.** A key carries its own namespace:
  `idx/<conv>/<token>`, `count/<conv>/<sid>`. A prefix query is
  `range("idx/<conv>/lay", "idx/<conv>/laz")`.
- **One handler at a time** makes the store single-threaded by construction:
  no locks, no transactions beyond "one call is atomic".
- **A read never touches the disk.** Everything live is in memory; the disk
  is for surviving a restart.

### The values: Zig structures, carefully

Steve's instinct, values as blobs that map straight to Zig data, fits the
kernel well: no parser, no allocator churn, comptime-checked sizes. It has
one real cost, **versioning**: a changed struct misreads every value written
before the change. So each value is framed:

- a **type tag and version**, two bytes, checked on every read;
- a fixed part as an `extern struct` (defined layout, little-endian, no
  pointers), with `comptime` asserts on its size;
- **variable parts length-prefixed** (a token, a list of postings), since a
  Zig slice is a pointer and can't be stored.

An old version is read by its own decoder and rewritten in the new form, or
refused loudly. Never silently misread. A small hand-written format, still
not JSON, and every format gets a round-trip test.

### On the disk: a log, compacted

One file per key fails on FAT: a folder holds at most 65,536 entries, and
every file costs directory writes. One file per store does better:

1. **Every `put` and `delete` appends a record** to the store's log: key,
   value, and a checksum. An append inside a cluster is ~3 disk requests,
   the same as a chat message's.
2. **At boot, the log is read once** and memory rebuilt: the last record
   for each key wins. A record whose checksum fails is the torn tail a stop
   left, and is dropped (and counted, for the judge).
3. **Compaction** writes the live keys to a new log and swaps it in by
   rename, the same old-or-new step `replace` already proves. It runs when
   the log is, say, 4x its live size, a slice at a time if it must,
   between handlers.

Durability follows the host's existing promise: no response leaves before
its writes are durable. A `put` in a handler is flushed with everything else
that request wrote.

### How it's judged

The same machinery as the rest of the stack:

- host tests for the log's format and the rebuild, every record cut at
  every byte;
- the fault tests for a write that fails or lies mid-append;
- metal-vmm sweeps with a shape that puts and reads back;
- a plant (a record whose checksum is skipped) the judge must catch.

## Search on top of it

### Two shapes, both cheap to try

**(A) All of chat in memory.** At boot, read every transcript once (as
`backfillAll` already walks them) and build per-conv token dictionaries in
memory: token → postings (sid and byte offset of each message containing
it). Appends update it as messages arrive. The store isn't even needed for
the index here; it rebuilds from the transcripts every boot.

- **For it:** the simplest possible search, always exact, no N-second lag.
- **Against:** boot reads every transcript (cold, ~5 ms a disk request), and
  memory grows with chat forever.

**(B) An index 1:1 with each transcript, kept lazily.** Each topic has an
index record in the store, keyed by conv and sid and stamped with the
transcript's size it covers. Topics not yet indexed, or old ones not in
memory, are simply scanned when a search needs them, and their index is
written as a side effect.

- **For it:** boot stays fast, memory holds only what's been searched, and
  the stamp makes staleness a cheap check (as `.count` does today).
- **Against:** a first search after boot may scan a lot (in slices).

Either way, the final search is exact: read each matching topic's postings,
and scan the tail of any transcript past its index's stamp. That tail is at
most N seconds of messages in (B), and nothing in (A).

### Autocomplete, leak-free by construction

**Dictionaries are per conv.** A query consults only the convs the person
can see (the sidebar's own walk), and merges their prefix ranges. There's
no global word list, so a word from a conv you can't see can't appear.
False positives (a word since edited away) and false negatives (a word in
the last N seconds) are acceptable, as Steve said. Leaks aren't possible.

**Tokens:** ASCII lowercased; any byte ≥ 0x80 is a word character, so
non-English text stays whole and matches exactly (case-sensitively). The
browser's single-topic token map moves to the same rule, so the two can
never disagree. One definition, tested on the same strings in Zig and JS.

### Fairness

Each search request is bounded (a slice: at most M disk requests), and the
browser asks for the next slice. Other people's requests run in between,
since the kernel serves one handler at a time. **A per-user rate limit** on
search requests keeps one person from monopolizing even the bounded slices.

## Measurements first

Before building, numbers we can get cheaply:

1. **Total transcript bytes, topics and messages per conv.** A
   `/admin/host` fact, so the measurement runs on production without its
   data leaving the machine.
2. **Distinct tokens per conv, and postings per token.** That sizes (A)'s
   memory. The same pass on a host copy of test data until we have the
   production number.
3. **A cold boot's full read of every transcript,** timed on metal-vmm with
   production's request cost, which is (A)'s boot price.
4. **A full scan's time in slices,** which is (B)'s first-search price.

If (A)'s boot read is a second or two and its memory a few MB, (A) wins on
simplicity, and the store's first job becomes the sidecars instead. If not,
(B) is the plan, and the store holds the indexes.

## Proposed order

1. **The store itself**, with tests, no users. (CC, host only.)
2. **Measurements 1 and 2**, as `/admin/host` facts. (CC; the box reads
   production.)
3. **Choose (A) or (B)** from the numbers. (Steve.)
4. **Search's server side**, then the UI.
