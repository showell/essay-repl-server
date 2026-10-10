# Protocols in prose: what the hunt found

*2026-10-10, night. Two cold, read-only reviews looked for "a protocol
specified in a comment instead of enforced by code", the shape of the old host
contract (now `router.start`): numbered steps, "call A before B", globals set
by hand in an order nobody checks, lists kept in step by hand. 22 findings;
triaged below, with owners and three yes/no questions at the end.*

Verified by me before writing: the kept-stream leak (A2), the coverage catalog
being a hand list (K1), and the two files whose tests are on no list (K2). The
rest are the reviewers' claims until each one's red test shows it.

## The pattern's worst cases: lists kept in step by hand, already drifted

These are the most valuable, because they are holes in the *instruments*:

- **K1. The coverage catalog is a hand list of 26 files** (gopher-metal
  `build.zig`). Nine files with properties are not on it (stream, scsi,
  virtio, store_model, io, pci, idle, idle_check, machine). A property in them
  that is never reached is never declared, so it never shows as a MISS: a
  silent hole in what the sweeps say they covered. Today's new properties
  (idle, store_model) fell into it. **Fix:** the build lists `src/` itself
  and catalogs every file that uses properties; any file left out is named in
  a `not_cataloged` list with its reason.
- **K2. Two files' tests are on no test list** (`io.zig`'s site-cache test,
  `test_disk.zig`'s write-cache test), so they likely never run. The build
  checks one direction only (what `unit_tests.zig` imports matches its list).
  **Fix:** the build requires every file with a `test` to be on a list.
- **K3. Scripts judge whatever binary is on disk.** `probe/run.sh`, metal-vmm's
  `sweep.sh` and several others check only that the file exists; `gates.sh`
  records this already went wrong once ("judged yesterday's kernel and
  passed") and fixed it for itself alone. **Fix:** one shared check that the
  binary's embedded commit is HEAD, or each script runs `zig build` (free when
  cached).

## In the app (angry-gopher)

- **A1. Every game write must ask `admit` first** (the game store's limits),
  and nothing checks it; each caller recomputes the byte count by hand, and one
  writer writes compacted JSON while its caller counted the raw body. **Fix:**
  one storage call per kind of write that builds the line, admits its exact
  length, and writes it.
- **A2. A kept stream must be served or dropped, and the host must remember.**
  *Verified:* Linux's `server.zig` does `try routed;` before looking at
  `bus.kept`, so a handler that keeps its stream and then fails leaves a
  subscriber in the Hub forever. **Fix:** `route` returns the kept stream
  (`!?Kept`), which Zig makes the caller handle, and drops it itself on error.
- **A3. Three test fixtures copy the list of eight globals `roots.point`
  sets**, restored by index; add a root and they silently stop restoring it.
  **Fix:** a `pointForTest` returning a handle to `defer` (or the roots as one
  struct, saved and restored in one assignment).
- **A4. Leftovers of the old host contract** (mine, from this evening): five
  comments still say "the host calls this once", and `router.zig` still
  re-exports whole modules, so a host can call `roots.point` after `start`.
  **Fix:** reword, and export only the types hosts need.
- **A5-A7. Values the client copies from the server:** upload caps and types
  (`chat_compose.js`, "must match"), search's word rules and its 20-word cap
  (`chat_search.js`, mine, already drifted on Unicode spaces), and
  `check_zig`'s list of built bundles. **Fix:** the server hands them to the
  page as data (or a checker compares, as the Caddy limits checker does).
- **A8-A10, smaller:** `mem_meter.init` before `start` (could be a value
  `start` requires); the chat page's widgets "MUST run first / AFTER" (each
  `init` could return what the next needs); tests restoring module globals by
  hand.

## In the kernel and the judge (gopher-metal, metal-vmm)

- **K4. Seventeen hand-copied panic handlers.** The serial log promises a
  panic writes its whole backlog, and the restart that a panic restarts; only
  the served kernel's handler does both. **Fix:** one `serial.panic` every
  probe names.
- **K5. The restart's numbered three steps**: forget the first (reserving the
  kept log's pages) and the log is written over memory the allocator handed
  out, silently. **Fix:** `begin` takes a token only the reservation returns.
- **K6. A stale copy of the old host contract** in `probe/gopher.zig`'s header
  (mine). Delete it.
- **K7-K8. Setup by hand:** `io`'s three setters in an order nobody checks,
  and a volume's bring-up (mount, FAT cap, cache, dir burst, dirs) written out
  in four places. **Fix:** one `io.setup(...)`, one `vol.hold(memory)`.
- **K9-K12, smaller:** two lists of which faults excuse a 5xx (shell and Zig);
  `plants.sh`'s build skipping the port check; three stream globals set
  together by hand; the "rest only after an empty turn" rule copied at four
  call sites.

Already good, noted by the reviewers: the unit-test list is compile-checked
against its importer; a plant without coverage is a compile error;
`plants.sh` reads the build's `Plant` enum; metal-vmm's settings table is held
to its knobs by a test; `sweep.sh` refuses before any seed when it cannot
judge.

## Questions (default yes)

1. **I fix A4 and K6 now**: they are leftovers of my own `router.start` work,
   an hour at most.
2. **The box takes K1-K3 next** (the instruments: coverage holes, tests never
   run, stale binaries), then K4-K12.
3. **The app's (A1-A3, A5-A10) go to CC as a queue item after 156**, A2 and
   A1 first.
