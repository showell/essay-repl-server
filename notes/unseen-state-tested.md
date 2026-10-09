# Unseen state, tested

*A second cold agent's answer, 2026-10-09 evening, to question #2 of
[questions to ask](questions-to-ask.md), "what can the oracle not see?",
written after reading the first agent's
[unseen state, by construction](unseen-state-by-construction.md). This one
was asked only about testing. Edited lightly.*

## Principles

1. **Judge the volume as the app's state, not only as a filesystem.**
   `sound.sh` asks whether FAT is intact, and the page comparison sees what
   one request rendered. Neither reads `auth/`, `users/`, `data/` or the
   counters.
2. **Unseen state shows up on the next request, so add one.** Every run
   should end with a second boot and a fixed probe.
3. **Aim the cut; don't sample it.** Independent draws rarely land between
   `allocateUser` and `setUserPassword`. Count a request's writes and cut at
   each one.
4. **The workload must hold the adversary.** With no stale cookie, revoked
   key or released id in the workload, those rules can't fire under any
   seed.

## Strategies, most yield per effort first

1. **`volcheck`: an offline checker of the volume image (small to
   medium; the highest yield).** A host tool over the image, run after
   `sound.sh` on every run, the unhurt run included. It checks that:
   - every counter is above every id it handed out;
   - every named account has a password, unless it is a guest by design;
   - every `api-key` carries its folder's `<id>-`;
   - no `data/<id>` or player row lacks an owner;
   - no `~*.tmp` is left behind;
   - `upload-bytes` parses and covers the user's uploads;
   - chat sidecars agree with their blocks;
   - every append ends on a record boundary;
   - no two members share a name.

   A broken rule is a "forbidden" verdict. In the rare tier it applies only
   when the kernel reported no damage.
2. **Power cut at each write of a request (small).** A knob cuts power at
   the Nth device write after request K. The sweep tries N = 1..W, with W
   counted in the shape's unhurt run, then boots again and runs `volcheck`
   and the probe. That hits exactly the windows in the construction note:
   - the empty-then-fill writes of the password, the API key and
     `upload-bytes`;
   - account creation;
   - logout's ordering;
   - a half-written append.

   It is deterministic, and the one strategy that replaces random seeds for
   this class.
3. **A second boot with a fixed read-back probe (small).** Generalise the
   durability mode's `READ_BACK` into `read-everything.http`:
   - log in as each setup account;
   - fetch the roster, the settings page, the API-key page and a chat;
   - register a fresh name, and then a taken one.

   Judge the result by the rules, against the same probe on the unhurt
   volume. It sees a counter handing out a used id, a cache that disagreed
   with the disk (now read cold), and a name freed by a demotion.
4. **Adversary shapes (small each).** Each comes with its setup and a
   "never" rule:
   - a stale cookie after a release, a logout or a password change;
   - a revoked key used again;
   - an old `uid_cookie` after an id is reissued;
   - p3 asking for p2's things.

   Run these unhurt every night, then under ordinary faults, since a revoke
   that fails under a fault is the interesting case.
5. **A model of the account lifecycle, on the host (medium).** A seeded
   random walk over register, login, password, key, revoke, logout, release
   and upload. It runs against angry-gopher on Linux, beside a tiny
   reference model. After each step:
   - credentials the model calls dead must fail;
   - live ones must work;
   - the tree must pass `volcheck`'s rules.

   It finds logic bugs in seconds, and the sequences it finds become shapes
   (4).
6. **The store judge with power cuts and failures (medium).** STORE.md
   says "no power cuts yet". Cut at every write inside each operation, and
   require STORE.md's promises: `replace` leaves old or new, never empty;
   `append` leaves a prefix. Then fail `remove` and `removeTree`, and
   require the caller to hear about it. Every `catch {}` site becomes a red
   test.
7. **A shadow check of the page cache (small).** In a coverage kernel,
   every page-cache hit also reads the disk and asserts the two are
   byte-equal, as a kernel property. A cache serving what the disk doesn't
   hold is invisible on a page by definition, because the cache *is* what
   renders.
8. **Linux against metal on the same script (medium).** Compare the final
   trees, with timestamps, keys and HMACs normalised out, and the
   responses. It sees divergences from the port, FAT's name folding, list
   order and the cache. It's an oracle for the unhurt run that doesn't
   certify itself.
9. **Metamorphic pairs (small, each narrow):**
   - release-then-register leaves the counter higher than register alone;
   - a duplicated idempotent request leaves the same volume;
   - two orders of independent requests leave the same accounts;
   - logout plus login leaves the same `auth/` tree.
10. **Plants for the new judges (small, required).** Without them, a new
    judge can go green because it never ran. One plant per judge, each
    caught by the judge it targets:
    - the counter returns 1 again;
    - revoke does nothing;
    - one cache forget is skipped;
    - one `write` where a `replace` belongs.
11. **A boot reconciliation audit (small; only once boot reconciliation
    exists).** Hand-made dirty images must come out of one boot clean by
    `volcheck`.

## How construction and testing divide the work

**Construction retires or shrinks these tests:**

| construction | the test it retires or shrinks |
|---|---|
| only `replace` | most of the per-write power cuts (2): only the gaps between files remain |
| one record per account | the rest of those gaps, and "named but no password" |
| derived counter, boot reconciliation | the probe's id collision becomes a boot invariant; keep the cheap check |
| no stored duplicates | the cross-file agreement checks |
| one `mutate()` for the cache | most of the per-site worry; keep the shadow read |
| no `void` mutators | the `catch {}` hunt, now a lint rule; failure injection still proves the error arrives |

**These stay regardless:**
- **`volcheck`:** construction is a claim, and this is its proof on the
  real disk.
- **The adversary shapes and the lifecycle model:** policy questions need
  executable answers, such as "does a password change kill sessions?" and
  "is a released id burned?".
- **Aimed power cuts, at a smaller scope:** tombstones and reconciliation
  open windows of their own.
- **The shadow read:** a cache is a cache.
- **The Linux comparison and the plants:** the judges' own judges.

**The rule:** construction removes the states; testing proves they're gone
and catches the next one. Build `volcheck` first, since every other strategy
reports through it.
