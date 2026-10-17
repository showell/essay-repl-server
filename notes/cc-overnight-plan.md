# An overnight run for CC

*2026-10-17. Steve asked, deliberately open-ended: more Shale tooling for
Zig refactors, some better kind of task, or docs? I formed a view, a cold
agent formed its own without seeing mine, and this is the two side by side,
with a recommendation and three questions only Steve can answer.*

## Where things stand tonight

- **234 is nearly done.** Chunk 3, `zig_rename`, is on CC's branch,
  adapted to the dry run's deletion. Its FEEDBACK report hasn't landed.
  When it does, I review it and merge it. One doc conflict is waiting,
  in SHALE-AGENTS.md, where my dry-run edits meet CC's rename recipe.
  The code merges cleanly.
- **235 is written and reviewed**:
  - `zig_decls`, `zig_move` and `zig_imports` over `std.zig.Ast`;
  - read-only mounts.

  A cold review already reshaped it (13 findings).
- **26 Zig files in our repos are over 1,000 lines.** The biggest:

  | file | lines |
  |---|---|
  | `tcp_test.zig` (kernel) | 3,043 |
  | angry-gopher's `router.zig` | 3,042 |
  | `probe/gopher.zig` | 2,653 |
  | `tcp_sim.zig` | 2,092 |
  | `tcp.zig` | 2,041 |
  | `solver.zig` | 1,956 |

## The candidates

| | what | night alone? | why |
|---|---|---|---|
| a | **235 as written** | **yes** | Every chunk names its red tests from real commits and has a property strong enough to check. The images measure metal. |
| b | **more tooling: cross-repo impact** ("what breaks in the other repos if I change this webbox `pub`") | **no** | `zig build consumers` already gives the compiler's exact answer on every push. The coupling that bit us today was never the API, but checks that knew another repo's file layout. Fix those by hand. A second, weaker reading of what the compiler decides has no second user. |
| c | **a bug-hunting expedition** | **yes, after 235** | Today's four real bugs were all in new Linux-host code, not the interpreter (which already has a fuzzer). Since the ban, that host is my whole toolchain. |
| d | **docs refinement, open-ended** | **no** | No check that passes or fails. SHALE.md (about 1,500 lines) is in decent shape; I keep it current. The useful version, a checker for cited paths and `file:N`, needs a policy call first (question 2). |
| e | **using 235 on real splits** | **yes, with Steve choosing the cut** | This is where the agent and I disagreed. See below. |

## Where we agreed

**235 first.** I'd order it `zig_decls`, `zig_imports`, read-only
mounts, then `zig_move`. `zig_move` carries the most risk of building the
wrong thing. Its four reports (`needs_pub`, `needs_import`,
`needs_from_from`, `uses_left`) are each a judgment about what to report.

**The agent's best idea: CC replays the linux_host split itself.** 235
says the box replays commits 589837e and 35317cf with the new recipe
afterwards. The agent says hand that to CC, as `zig_move`'s acceptance
test. It needs no KVM, and diffing the replay against my hand-made
commits is the strongest check on offer. The night then ends with a
measured diff, not just with `zig_move` passing its own unit tests. **I
agree, with one rule: if the replay disagrees with a hand-made commit,
CC reports the disagreement in FEEDBACK and stops.** It doesn't keep
adjusting the analysis until the numbers match.

**`zig_rename` and `zig_move` share one reading of identifier tokens**,
with a test that holds them to the same answers. Today's `edits_all`
and `edit` drifted apart within an hour of being written. Two token
walkers written separately would do the same.

## Where we disagreed: who picks the cut

I wanted 235's second user tonight: a real split of one long file. Your
"a second non-trivial refactoring will lead to us wanting a bit more" is
the point. The judge for a pure move can run unsupervised:

- the same test names, before and after (`same_tests.shale`);
- `zig build consumers` green;
- **the symbol table unchanged by short name and size.** Zig qualifies a
  symbol by its file, so `linux_host.foo` becomes `linux_writes.foo`,
  and the comparison strips that part. CC already wrote most of this
  tool for chunk 2's image investigation (a Shale script over
  `nm -t d`).

The agent's objection is fair: **where to cut is your taste** ("split so
it can be deleted"). A night of plausible splits is exactly the wrong
thing to build alone. Its answer is that you choose the first split, and
the tools make it cheap.

**My synthesis: you choose the file and the cut points before CC starts.
CC does the moving, with the recipe and the symbol judge.** Then the
judgment is yours, the work is mechanical, and the check needs no one's
eyes. My nominee is **angry-gopher's `router.zig` (3,042 lines)**:
- it's one repo;
- it's application code, so a mistake there costs less than in the kernel;
- `zig build consumers` covers it;
- it has natural seams: the route table, the request-edges test, and the
  admin routes.

A safer but less instructive choice is a test file, such as webbox's
`linux_host_test.zig` (1,523 lines).

## If time is left: hunt in the Linux host

The targets:
- `shale_spawn.zig`, `shale_jobs.zig`, `shale_host_jobs.zig`, `shale_keep.zig`;
- the secret scrubber when a secret spans two chunks of output
  (`shale_host_linux.zig` around :391, the carry);
- path resolution through mounts.

The usual doctrine applies: one expedition, each bug becomes a red unit
test, and nothing new joins the gates.

**One finding is already in, from the agent's open question, which I
settled by experiment:** `read` follows a symlink inside the root out of
it. A link in a scratch folder to `/etc/hostname` read fine. On Linux,
`run` can reach anything anyway, so this is cheap today. But it would
quietly get around 235's read-only mounts, through a link into a
read-only mount. So it goes into 235's mounts chunk as a must-fix.

## Not tonight

- **Cross-repo impact tooling** (b, above). The compiler, through
  `consumers`, is the judge. The remaining checks that know another
  repo's layout are mine to hunt by hand.
- **Docs, open-ended.** The two small stale lines the agent found are
  mine, now.

## Three questions for Steve

1. **The split.** `router.zig`, or another file? And do you want to name
   the cut points, or have me propose them for your OK before CC starts?
2. **`file:N` citations.** Every queue item and doc cites line numbers,
   and those rot by design. Should a doc checker enforce them (hundreds
   of findings), check only that paths and names resolve, or leave them
   alone?
3. **Symlinks in the store.** Should we refuse to follow any symlink, or
   only one that leaves the root or a mount? I'd refuse any. Nothing we
   run needs one, and "refuse" is one rule with no exceptions to test.

## The brief, if you say yes

1. Merge master (the dry run's deletion touches `changeAt`).
2. **235:** `zig_decls`, then `zig_imports`, then read-only mounts (with
   the symlink rule), then `zig_move`, with the replay of 589837e and
   35317cf as its acceptance test. Stop on a disagreement.
3. **The split you choose**, done with the recipe and judged by test
   names, consumers and the symbol table.
4. If time is left, the Linux-host hunt.

Throughout, CC measures both images after each chunk and writes one
FEEDBACK entry per chunk, so whatever finishes can be merged even if the
night stops partway.

## Decided (Steve, later the same evening)

1. **The split is `router.zig`, with the box choosing the cuts.** The file
   turned out to be about 340 lines of route table and 61 tests (not 77,
   as I first said). So the split sorts tests into files by what would
   be deleted together:
   - pages, identity, games, admin, search, chat;
   - the store-failure class;
   - the script route;
   - request edges;
   - **the legacy cookie names' migration**, a file deleted whole the day
     those names retire.

   A harness holds what two or more files share. The two tests of private
   functions stay in `router.zig`. The judges:
   - `gopher.elf` byte-identical once its embedded angry-gopher commit is
     set aside (only test code moves);
   - the same test names;
   - the gates.

   The split also adds a check I found missing: every test block in
   angry-gopher must be enrolled in a test root, the hole that once hid a
   whole test file. QUEUE 236.
2. **The doc checker checks paths and names now, line numbers later**,
   and stays out of the gates until its first report is fixed. QUEUE 237.
3. **Symlinks: refuse any.** It's folded into 235's mounts chunk.

The night's order is in QUEUE's Now line: 235, 236, 237, then the
host hunt if there's time.
