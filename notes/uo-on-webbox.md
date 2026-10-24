# UO on webbox: a proof-of-concept plan

**The question:** can Damian's UO shard (`cobblestone-pin/apps/uoaix`, ~846 Codex files) run on webbox? Proof of concept only: a couple of typical host interactions, not the game.

This note condenses four design memos written by agents on 2026-10-24. **They read the code but built and ran nothing**, so every claim here is a reading, still to be confirmed.

## The answer, in short

It looks feasible, and the first step is small. Damian's own proofs already build small worlds in code, with no EA map files, and each has a `.expected` output to compare against. Running two of them through cobble-webbox's existing path (Codex → Zig → webbox host), and matching their expected output, proves the code runs. A one-second world tick behind an SSE feed, plus a tiny watcher page, proves the "host" part.

## What stands in the way

- **No EA data.** The box has no client and no `.MUL` files, and they aren't ours to publish. The full server refuses to boot without a map cache built from them. The proofs don't need it: they make flat maps in memory (`walk-map-new`, `walk-set-land`).
- **Primitives the Zig emitter doesn't support.** The proofs use `poke-qword` (hundreds of calls), `get-ticks` and probably `device-seed`, and Damian's Zig emitter has no entry for them. Each becomes a Zig compile error until it's added. The emitter's prelude is at 126 of its 128 parts. The plan is to fold `poke-qword` into the existing peek part, and give the clock and the seed one shared part.
- **Hardware reads.** `hpet-ticks` reads `#FED00000`, and the full server reads fixed kernel addresses. Under Zig these land in the Codex heap and return garbage *without failing*. The proofs may avoid them; the first real run will tell.
- **Stack.** The live server reserves 64 MB of stack on bare metal, and one town fill recurses about 28k cells deep. Webbox gives 16 MB. `stack.onStack` measures this directly.
- **Heap.** The server already keeps lasting state below a mark and rolls scratch back, so mark-before-tick and roll-back-after should hold. Long runs still grow (UOAIX-246), which doesn't matter for a proof of concept.

## The ladder

| Step | What runs | Proves | Oracle |
|---|---|---|---|
| 1 | `proofs/GameVendorReplay.codex` (294 lines plus the chapters it pulls in): real buy and sell packets against a vendor | the Codex compiles to Zig and runs under a webbox host | `GameVendorReplay.expected`, 31 PASS lines |
| 2 | `proofs/TownLiveProof.codex`: the Britain economy on a flat map, residents walking to lodging and work | the town tick runs; the stack and heap hold | `TownLiveProof.expected` |
| 3 | The same town, ticked once a second from webbox, with positions published as SSE | a long-running Codex world served by webbox | it keeps ticking; the watcher page shows people moving |

`GameSessionProof` (login, character creation, movement, speech through `gs-handle`) can replace step 1 if the vendor proof is awkward.

**Out of scope for now:**
- the real server on TCP 2593, which webbox can't do: it serves HTTP only;
- the map cache;
- the admin protocol;
- the full observer feed;
- bare metal.

## The watcher

**One HTML file:**
- a canvas of generated grass tiles;
- each person an emoji on a disc colored by job;
- speech bubbles;
- a "town crier" ticker of events.

**The feed:** step 3's SSE sends a snapshot, then one delta a second.

**Why the town moves with no one watching:** Damian's notes suggest the town only advances while a player is in game, but the code disagrees. The world tick walks the townsfolk once the economy is open, and a 301-game-hour run with no player confirms it.

The client memo budgets v0 at about 330 lines. For the proof of concept, the first ~150 of those are enough: the map, the people and smooth motion.

## Wall time

The anatomy agent estimates 1–2 days of agent time for steps 1–3. The biggest unknown is what the emitter refuses once the real code is emitted. I'll measure step 1 first, about half a day, and re-estimate from what it shows before committing to steps 2–3.

## Rulings for later (not needed for the proof of concept)

- Damian's notes put public internet exposure out of scope until he rules (`UOAIX.md:19-20`).
- A few committed tables (house floor boxes, sea lanes) were computed from EA files.
- Exact walls in a watcher would need a walk mask from EA's map. The design leaves it out.

The four memos, with file:line evidence, are in this session's scratchpad (`uo-design/1-4`). Ask if you want any of them published.
