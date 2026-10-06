# CC: the floor and the Store (QUEUE items 76–81)

*The text of `QUEUE.md`'s items 76–81 as they go to Cloud Claude,
2026-10-06. Background: [the Store and the census,
interleaved](the-store-and-the-census-interleaved.md).*

---

**The mission (the box, for Steve, 2026-10-06).** This is a long assignment,
meant to run all night without anyone to ask, so it hands you more judgment
than usual. Two goals, interleaved: **name every refusal in gopher-metal's
floor**, so a coverage report says which ones any run has reached, and
**build the Store**, the narrow data door a web server in a box will give its
applications, with three implementations judged against each other by a
simulator. Everything here can be proven with `zig build test`, `zig build
properties` and python; none of it needs KVM, the box, or prod. Finish the
item in hand (K3), then take 76–80 in order; K4 and K5 come after 80, or as a
rest whenever a phase waits on a question. The tactics below matter as much
as the items: **park instead of grinding, ask in writing and keep going, and
write every shortcut down instead of avoiding it.**

**What is in and out.** TCP is part of the floor, not the Store. The floor is
everything under an application's `handle(request) -> response`; the Store
is one door into it (data, as named files), as requests and responses are
another. Out of scope: DHCP (the box's, B18); any change to angry-gopher's
code; any change to what the kernel *does*. A property observes; it never
steers.

**How to work (also in `CLOUD_WORK.md`, "Long assignments"):**

- **Every item ends in a command and a number.** Say in the commit what
  `zig build properties` (or the test) printed: "`proto`: 11 of 12 reached;
  the 12th is under Questions".
- **Park after about three attempts.** If an item has taken about three
  tries without a passing test, write what you know under Questions (what
  you tried, what failed, the shortest reproduction), mark the item
  **parked**, and take the next one. Parked is not failed; the box can often
  settle it in a minute with KVM.
- **A refusal is reported, never routed around.** If your own checks stop
  you, say what stopped you under Questions and move on.
- **You decide:** names, file layout, test structure, which simulator reaches
  which property, module order within a phase, and fixes to your own earlier
  work. **You ask, under Questions, and keep going:** a seventh Store
  operation, anything that changes kernel behavior, anything in angry-gopher,
  and anything that looks like a bug in production.
- **A found bug is a test first.** Write the failing case. If the fix is in a
  pure layer and small, fix it in the same commit. Otherwise file it under
  Questions as a bug, with the test committed but left out of the default run
  *and named there*, so it's visible, never silently skipped. Then move on.
- **Green at every push.** Each commit leaves `zig build test` and `zig build
  properties` passing. Push after every item. Merge `interrupts` and
  `antithesis-sdk` into your branches at phase boundaries, not mid-phase.
- **A phase report, five lines,** under the phase's item when it's done:
  what was reached, what's parked, what was asked, what surprised you, and
  the floor's count before and after.

**Debt, calibrated.** Leave freely, and write one line in **the debt
ledger** (a new section at the end of `QUEUE.md`: what, where, what fixing it
would take): duplicated helpers across simulators, a crude generator that
still reaches the property, an awkward property name, a module reached only
by a host test so far. **Never**, whatever it saves: a test weakened or an
oracle loosened until it passes; a property that can't fire, written to make
the count look good; a skip without a name; kernel behavior changed as a side
effect of adding a property.

---

76. **Phase A: the ground under the Store** (gopher-metal). Name the refusals
    and invariants in the modules the Store will sit on: `fat16` (its
    refusals not yet named), `page_cache`, `io.durable`, the block driver's
    `flush` in `virtio.zig`, `kept_log`, `log_ring`, `gpt`. A `reachable` for
    each refusal (an early return, an error answer), the way "tcp: a damaged
    segment is dropped" is named; an `always` for each invariant, with item
    61's numeric comparisons where there's a limit. Reach each one from a
    simulator or a host test, extending `fat_sim`, `page_sim` or `pure_sim`,
    or adding a small one. Start a table in `COVERAGE.md`: module,
    properties, reached, by what. Raise `coverage/floor-sim.txt` to what is
    reached. **Done when** each of these modules has its row and the floor
    holds them. Keep a list as you go: every error each module can answer.
    Phase B's error list comes from it.

77. **Phase B: the door** (gopher-metal). The Store, as [a web server in a
    box](a-web-server-in-a-box.md) drafts it: **read whole, write whole,
    append, list, remove, replace**, and nothing else. Write:
    - the interface, as a zig type, with the errors it can answer, taken
      from phase A's list (each Store error says which refusals map to it);
    - what "replace" promises: after a power cut at any point, the file is
      wholly old or wholly new, never half of each;
    - **the model**, in memory, as plain as you can make it: the oracle;
    - **the FAT store**, over `fat16.zig`, on the in-memory disk the tests
      use (`test_disk.zig`), with its power cuts and torn writes.

    Names are short and case doesn't matter, as on FAT. **Done when** a host
    test runs every operation against the model and the FAT store, with a
    power cut at every write of a `replace`, and they agree. If the interface
    seems to need a seventh operation, ask under Questions, and in the
    meantime write the case down as a test that the six can't express.

78. **Phase C: the other side of the floor** (gopher-metal). The same work
    as phase A, for `proto`, `arp`, `stream` and `Spill`, and `request_heap`;
    plus B15: a `-Dcoverage` kernel calls `tcp_check.check` after every
    `handle` and `transmit` as one `always("tcp: the table's invariants
    hold")`, and FAT's own `check` at the end of a run (production builds
    unchanged; the box runs it under metal-vmm). For parsers, build inputs
    field by field and make one field wrong, rather than random bytes.
    **Done when** these modules have their rows and the floor holds them.

79. **Phase D: the twin and the judge** (gopher-metal).
    - **The strict Linux store**, over `std.Io`'s filesystem in a temp
      directory. It enforces FAT's rules (case folding, name length,
      forbidden characters, `max_tree_depth`) *before* touching the disk, so
      a laptop refuses what the droplet would.
    - **`store_sim`**: seeded sequences of operations, with power cuts on
      the FAT side, against the model, the FAT store and the strict Linux
      store. Every answer matches the model; FAT and Linux refuse the same
      names for the same reason; after any cut, every replaced file is
      wholly old or wholly new. Its properties go in the catalog, with a
      floor, and `zig build properties` runs it.

    **Done when** `store_sim` runs 1,000 seeds clean in `zig build
    properties`, and its properties are on the floor.

80. **Phase E: the rest, and the census** (gopher-metal, with a doc about
    angry-gopher).
    - The rest of the floor, as in phases A and C: `scsi`, `virtio`'s rings,
      `pvh`'s memory map, `civil`, `wallclock`, `restart`. **Every** module
      in `src/` ends with a row in `COVERAGE.md`'s table, even one that says
      "nothing to name, because...".
    - **The census** (`STORE-CENSUS.md` in gopher-metal): every place
      angry-gopher's `zig-server/src` reaches the disk (about 104 call
      sites), each in a row: file and line, what it does, which Store
      operation it is, and which refusals can reach it. The calls that fit
      none of the six get their own section. Each is a question about the
      seam, for Steve. **Describe only; change nothing in angry-gopher.**
      If angry-gopher isn't in your environment, park the census and say so.

    **Done when** every module has a row and every disk call has a row.

81. **Your proposals again** when 76–80 and K4–K5 are done, or when
    everything left is parked.

---

**To start:** ask Steve to say "go" if you understand, or ask Steve to wake up
local Claude if you need more clarity.
