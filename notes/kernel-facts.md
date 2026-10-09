# The kernel's facts: one place, one step

*A cold agent's answer, 2026-10-09 evening. The question: the lens "one
fact, one place, one atomic step" from
[unseen state, by construction](unseen-state-by-construction.md), applied to
gopher-metal alone, with angry-gopher only the reality check. It proposed
structure only, not tests. Ranked by how bad the reachable state is ×
how cheap the fix. CONFIRMED means it read the path; ★ means the box checked
it too.*

1. **A `write` over an existing file deletes the old one first.** ★
   CONFIRMED, small.
   - Today `fat16.writeFileIn` removes the entry and frees the chain, then
     allocates and writes. A cut or a full volume in between leaves the
     file gone, which is STORE.md's "old, new, or gone".
   - Fix: write the new chain, point the existing entry at it in one sector
     write, then free the old chain. The file is then wholly old or wholly
     new, a full volume leaves it old, and `write` equals `replace` for
     every caller. **(the box)**
2. **`makeDirIn` can roll back after its commit write.** CONFIRMED path;
   whether a "failed" write can land is a LEAD.
   - A failed-but-landed entry write frees a cluster the directory then
     owns, and the next allocation crosses two chains.
   - Rule: no undo once the commit sector has been attempted.
3. **A failure after the commit is reported as a failed operation.**
   CONFIRMED, small. `rename`'s and `unlinkEntry`'s `freeChain` after the
   commit. The commit write decides the result; a cleanup failure after it
   is a counted leak.
4. **Leaked clusters are never reclaimed.** CONFIRMED, small to medium.
   - The check says them but never mends them, so the volume shrinks over
     its life.
   - Fix: free them at boot when the check finds no damage.
   - That makes reconciliation normal operation, and makes "commit, then
     sweepable cleanup" a valid order everywhere. **(the box)**
5. **`removeTree` isn't atomic** (one entry per round). Medium; needs #4.
   Unlink the top entry as the commit, then free the detached subtree. Its
   STORE.md row becomes "there or gone".
6. **Partial chains leak on errors other than `Full`.** CONFIRMED, small.
   - `allocChain` gives back only on `Full`, and `grow` has no errdefer for
     its fresh cluster.
   - Give-back failures are swallowed.
7. **`fatSet` assumes a failed write didn't land.** CONFIRMED code;
   consequence a LEAD.
   - On a failed FAT write, re-read the sector, as the folder cache already
     does.
   - A second-copy failure isn't the operation's failure.
8. **The kept free count never checks itself in production.** CONFIRMED,
   small. Set it from the boot check's count, and assert equality per
   request in coverage builds.
9. **`Volume` is a copyable value with per-copy mutable bookkeeping.** LEAD
   (no second writer today). Have `io` own the one `Volume` and hand out
   pointers.
10. **A failed flush doesn't stop the response.** CONFIRMED. **Steve's
    decision.** It matters only on a disk whose cache wouldn't turn off.
    Option: answer writes with 503 until a flush succeeds.
11. **The SCSI cache flags can disagree.** CONFIRMED, small.
    `recheckCache` never sets `cache_turned_off = true`. Derive the report
    from `write_cache` plus one bit, "it was on at bring-up".
12. **TCP connection fields hold one fact in several places**
    (`state`/`fin`/`fin_wait_until`/`fin_ever_sent`; the window-update
    trio). Structural. Tagged unions would make the rules `tcp_check`
    enforces impossible to break.

**Already done well; don't redo:**
- `fatSet` is the one place the FAT and the count change.
- `unlinkEntry`'s order.
- `writeEntry` tombstones orphaned long-name parts.
- Rooms are found before anything changes.
- The tie writes neither copy.
- The folder cache drops a sector whose write failed.
- `durable.step` is a pure decision.
- The restart record is checksummed and written first.
- `openEntry` keeps absent apart from unreadable.
- The page cache forgets on any failed change.
