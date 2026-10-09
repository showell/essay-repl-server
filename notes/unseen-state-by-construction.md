# Unseen state, prevented by construction

*A cold agent's answer, 2026-10-09 evening, to question #2 of
[questions to ask](questions-to-ask.md), "what can the oracle not see?":
state that never renders (orphans, counters, stale keys, a cache that
disagrees with the disk). **Testing was off limits.** It was asked only how
the code itself could make such state impossible, or unable to last. Edited
lightly. ★ marks a claim the box checked in the code. A second agent's
answer on testing follows in [unseen state, tested](unseen-state-tested.md).*

## Principles

1. **One fact, one file, one atomic step.** An entity spread over several
   files can be left by a crash in a state no code ever made on purpose.
   Each entity should be one record, always written with `store.replace`.
2. **A failed mutation must be visible to whoever reports success.** A
   delete becomes a commit point (a tombstone) plus a sweep that runs until
   the data is gone. A failed delete is then pending work, not a lie.
3. **Derive; don't store.** Counters, mirrored names, `.lastauthor` and "is a
   member" are computed from what exists. Where a stored value is needed,
   keep it as a cache that checks itself, as the chat `.count` sidecar
   already does.
4. **Every identity has an incarnation.** A random value in the account
   record, bound into everything that refers to the account (cookies,
   mirrors). A stale reference can then never attach to a released or
   reissued id.
5. **Reconciliation at boot is normal operation.** Every boot finishes
   tombstoned deletes, removes stray temp files and re-derives high-water
   marks.

## Proposals, most unseen state removed per unit of effort first

1. **All state written through `replace`; `store.write` made private
   (small).** ★ `write` empties and then fills, and it still writes:
   - the password (`users.zig:558`);
   - the API key (322);
   - `upload-bytes` (293);
   - `touchUser`;
   - `.lastauthor`;
   - the session meta files (storage.zig).

   "Is a member" means "the password file exists". So a stop in the middle
   of a password change silently demotes the member, and their name is
   then free for a stranger. The same window resets `upload-bytes` to a
   fresh allowance. Keep `write` only for files written once (uploads).
2. **A missing counter starts from what exists, not from 1 (small).** ★
   `counter.current` still returns 1 when the file is absent (105 fixed
   only the unreadable case). Make the value max(file, highest existing id
   + 1), from `listUserIDs`, `player.list` and `listSessionIDs`. Better
   still: derive it at boot, keep it in memory, and treat the file as its
   copy.
3. **Release becomes tombstone-then-sweep (medium).** One `replace` of
   `auth/<id>/released` is the commit point, and every resolver treats a
   released id as absent. A sweeper deletes `data/<id>`, `users/<id>` and
   the player row, retrying at every boot. The tombstone stays, so the id
   stays burned. This also fixes:
   - `storage.deleteUserData` swallowing its own `removeTree` error;
   - logout's ordering (login.zig ~250);
   - a released member's mirrored player row that is never deleted, so the
     member still appears in the roster.
4. **Revoke is a write, and nothing that changes state returns `void`
   (small).**
   - `clearUserAPIKey` becomes `replace(api-key, "revoked")`; the key
     checks already reject a key with no `<id>-` prefix.
   - `clearUserAPIKey`, `deleteUserRecord`, `player.deleteRecord` and
     `touchUser` return `!void`.
   - A `catch {}` after a call that changes state needs an `absent-ok:` tag,
     enforced by the existing lint.
5. **Session cookies bind the incarnation (small to medium).** Sessions are
   stateless HMAC cookies lasting 365 days. Logout only clears the
   browser's copy, so a copied cookie outlives a release or a reissued id.
   - Sign (id, incarnation, time).
   - Release, a password change and "log out everywhere" each replace the
     incarnation, which kills every outstanding cookie at once.
   - The same goes for `uid_cookie`.
6. **One record per account (structural).** `auth/<id>/account` holds the
   name, hash, key, incarnation and released flag in one `replace`. The
   account exists exactly when that file does.
   - This removes a named account with no password, left by a stop
     between `allocateUser` and `setUserPassword`.
   - It makes upgrading a guest to a member one write.
   - Cost: migrating prod's files, read by both hosts.
7. **Delete stored duplicates (small).**
   - Remove `.lastauthor`, a non-atomic copy of what the `.count` sidecar
     holds.
   - Stop copying the account's name into the player record; read it from
     the account.
8. **A boot reconciliation pass (medium):**
   - remove `~xxxxxxxx.tmp` files left by an interrupted `replace`;
   - finish tombstone sweeps;
   - fix the counters' high-water marks;
   - reclaim leaked clusters on the writable mount, if the boot check only
     reports them today (unchecked).
9. **Appends keep only whole records (medium).** A stop in the middle of
   `store.append` leaves a partial chat block or DSL line, and the next
   append is written onto its end. Before appending, trim back to the last
   record boundary. FAT may need a truncate.
10. **Page cache coherence in one place (small, gopher-metal).** `io.zig`
    tells the page cache about changes from five places. Route them all
    through one `mutate(path, op)` that forgets the path first and
    repopulates only on success, so a future operation can't skip it.
11. **A distinct `Uid` type (small to medium).** Paths are built only from
    a type that validation or allocation constructs, with account and
    player ids kept apart. That replaces the `allDigits` and `isSafeID`
    checks repeated at each call site.

## What it would not do

- **No database, journal or transactions spanning files.** On FAT and two
  hosts, one record per file plus tombstones gets most of the benefit for
  little of the risk.
- **No name-to-id index:** one more copy that can disagree.
- **No change to the chat `.count` sidecar.** It is the model the rest
  copies.
- **No silent deletion of a released member's DMs.** They are also the
  other person's history, so that is Steve's policy call.
- **No flushes added inside angry-gopher.** `durable.zig` already holds
  output until writes are flushed.
- **No retries that hide errors.** A retry that eventually says "done" is
  the same lie as `catch {}`, only later.
