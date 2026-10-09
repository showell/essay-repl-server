# Questions to ask: classes over features

*A cold agent's answer, 2026-10-09 evening, to "what questions should we be
asking?", edited lightly. It read [the postmortem](the-cc-queue-postmortem.md)
and skimmed the code. Paths are angry-gopher `zig-server/src/` and
gopher-metal `src/`. One spot check is confirmed (★), the rest are its
leads. Feeds [the plan](the-plan-after-the-postmortem.md).*

## Classes worth a full walk, by expected yield

1. **Where does a revoke or delete fail quietly?** `catch {}` on a call
   that removes authority or data leaves a credential or orphan behind
   while the user is told it's done. Grep `catch {}` / `catch continue`
   (chat_store 22, chat_retire 18, users 13, uid_cookie 9, roots 8,
   login 7) and ask of each: does this remove authority or data?
   - ★ **Confirmed:** `users.clearUserAPIKey` is `store.remove(...) catch
     {}`. Both callers (settings, admin) then redirect with `keyrevoked=1`.
     A failed remove leaves the old key working.
   - Logout's release: `deleteUserData(...) catch {}`, then the record is
     deleted anyway.
2. **Where does a reply promise what isn't written, or written whole?**
   - `store.write` (truncate, then fill) where `replace` is safe, such as
     `api-key`.
   - `io.durable()` sends the response even when the flush failed. That is
     deliberate, but the judge needs a stated position on it.
3. **Where does a failure read as absence?** The walk isn't finished:
   - the `readOrEmpty` callers (chat_store, code_store, images_store,
     chat_state, docs_store, uid_cookie, reading_list);
   - `statOrNull`, `has`.

   An I/O error must never reach a branch that creates, resets or allows.
4. **Where does a check-then-act span a lock?** `counter.peek` offers an id
   without reserving it (puzzles). `replace`'s sibling name is one per path,
   so two writers to one path, each without their own lock, collide.
5. **Where does state change before the requester, or the target's owner,
   is checked?** Any write whose path takes a client-supplied
   id/sid/conv_key (reactions' `msg_num`, game sessions, chat_conv, admin_*)
   without comparing it to the current user.
6. **Where does an error leave a half-made thing that a later "exists"
   trusts?**
   - `ensurePuzzleSession`: the folder is made, but its meta is not.
   - A chat append's `.lastauthor` sidecar.
   - signup's four steps.
7. **Where is a cache answered from after the disk refused the write?**
   page_cache's `wrote`/`replaced`/`renamed`, on partial success.
8. **Where does output leave without `Stream.sendAll`?** A FIN, an RST, an
   SSE frame, or a download a client can read as "done" before the flush.
9. **Where is a length, offset or count read from disk and trusted?**
   - fat16 (chains, entries, sizes), the chat sidecar's count, ustar;
   - the restart record, gpt.

   Rot one field and expect a refusal, not a panic, loop or overread.
10. **Where can one user's value reach another's page?** bus keys,
    presence, chat SSE, the recent feed, the page cache (case folding,
    `~hash.tmp`), buffers reused across streams.
11. **Where does boot repair choose between copies without a quorum?**
    Found twice already. Walk every boot write: what evidence chose it,
    and what happens if it's refused.
12. **What driver or protocol state survives a reset it shouldn't, or is
    lost in one it should keep?** Found once (WCE). Read reset.zig, scsi,
    virtio queues and tcp over restart against SPC-4, virtio 1.2 and RFC
    9293.
13. **Where do retirement and backup race live writers?** chat_retire
    swallows 18 errors; the backup was already cut short once.

## Things that must never happen, checkable per run

1. Something the server confirmed is missing after the run (a 303, a 200
   on a POST, an SSE echo).
2. Two principals share an id, or one name has two records (scan the
   volume).
3. The counter is at or below an id already handed out.
4. A response carries another user's canary, or a cookie names someone
   other than who logged in on that connection.
5. A connection gets nothing at all when no fault touched its path.
6. The boot stops or loops without saying why; or the guest says "clean"
   while offline fsck finds cross-linked or looped chains.
7. A revoked credential still authenticates.
8. A rotted or refused sector produces a page with no 5xx and no note from
   the kernel.

## Questions about the method

1. **Which faults can reach the app's error branches at all?** Coverage per
   `catch` site under the sweep would show it. 105 and 108 lived where no
   seed reaches.
2. **What can the oracle not see?** State that never renders: orphans,
   counters, stale keys, a cache that disagrees with the disk. Judge the
   volume afterwards, and a second boot's reads.
3. **Are faults correlated the way real ones are?** Independent draws
   rarely hit a window between two named writes. Aim at them on purpose:
   cut at the Nth write of a named request.
4. **Is the unhurt run itself right?** If it isn't, equality certifies the
   bug. Run the "never" checks on it too.
5. **Does the workload contain the adversary?** With no second user, no
   forged ids, no replayed cookies and no concurrent tabs, classes 4, 5
   and 10 can't fire under any fault plan.
