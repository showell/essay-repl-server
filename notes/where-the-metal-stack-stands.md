# Where the metal stack stands

*2026-10-07, afternoon. For Steve: the state of the four repos, what the
overnight work actually found, the Store question, and where things can
quietly drift apart.*

## The short version

- **Production:** v18 serves. A slow afternoon on DigitalOcean's block
  storage (each disk request went from about 1 ms to 3–5 ms, and is
  recovering now) made sends take a second. **v19** is in its last gate.
  It keeps folders in memory, which cuts a send from about 466 disk
  requests to 88, so the next slow afternoon costs a fifth as much.
- **Cloud Claude** finished the long overnight assignment and is now the
  adversary: it plants deliberate bugs to see which ones the tests miss,
  and it reviews my explorer commits. Both are already paying off.
- **The seed explorer** is built (tape, named choices, re-roll and flip,
  aimed flips). Its first honest benchmark on `fat_sim` was a tie; the
  three-way comparison runs after the gates.
- **The Store** has a real question in it: angry-gopher already has its
  own, and the one we built overnight isn't the one production uses. I
  recommend unifying them, as described below.

## What the overnight work found

The assignment was two goals: name every refusal in the kernel, and build
the Store. Both are done. What's worth knowing is what came out of them.

**Findings about the code:**

1. **`fat16.remove` accepts a folder.** It drops the folder's entry and
   leaks everything under it, where Linux refuses with "is a directory." No
   caller in angry-gopher passes a folder today, so it's latent. It's
   queued as B22, with CC's red test waiting for the fix.
2. **FAT writes forbidden characters if asked.** `fat16` checks a name's
   length but not characters like `:` or `?`. Every server write goes
   through angry-gopher's own store, which refuses them first, so nothing
   reaches it today. It matters only if some future code writes around the
   store.
3. **Two of CC's own oracles were wrong before the code was.** The memory
   allocator keeps a page for its own bookkeeping, and freeing memory from
   the wrong owner panics on purpose. Both were the simulator's mistakes,
   corrected. This is the seed-23953 lesson again: a model can be wrong.

**Findings about coverage:**

4. **Every module in gopher-metal now has a row** in `COVERAGE.md`, and the
   simulator floor went from about 200 properties to about 250. Before,
   only TCP and FAT were measured; now each refusal has a name, and a
   report says which ones a run reached.
5. **Some refusals only a real device can cause**: the clock chip silent,
   the disk's sector size wrong. CC listed them and then built metal-vmm
   knobs for five of them (item 82). They aren't yet run on the box, and
   they aren't on the metal floor. That's the box's next coverage chore.

**Findings about the design:**

6. **angry-gopher already has a Store.** This was the overnight surprise,
   and it's the subject of the next section.
7. **A seam under `stream.zig`**: CC proposed pulling the "is this
   connection still worth waiting for?" decisions out as pure logic, so a
   simulator can reach seven more refusals. You approved it; it's parked
   behind the adversary work.

**Today's adversary work, so far:** four planted bugs survived every test,
and each one now has a test that catches it:
- a resend that keeps timing a segment (Karn's rule, in TCP);
- an option of length one before the maximum-segment-size option, in a
  TCP handshake;
- a chunked request that also states a length;
- a file name containing the DEL character.

Each is a place where code ran under test, but nothing would have noticed
it being wrong. Coverage can't see that; mutation testing can.

## The Store: we built the right thing in the wrong place

Here's the situation in plain terms. There are two Stores now:

- **angry-gopher's `store.zig`**, written in early October: twelve
  operations (read, write, replace, append, list, remove, plus `stat`,
  `has`, `readAt`, `makeDir`, `removeTree`, `resolve`). Every chat, game
  and user file goes through it. It already enforces FAT's naming rules on
  every host, which was your call on 2026-10-02.
- **gopher-metal's Store**, built overnight: seven operations, three
  implementations (an in-memory model, one over `fat16`, a strict Linux
  one), and `store_sim`, which judges them against each other with power
  cuts and full volumes.

The catch: **production never runs gopher-metal's Store.** On the droplet,
a chat message goes angry-gopher `store.zig` → metal's `io.zig` (zig's
standard I/O interface, reimplemented for metal) → `fat16`. Our judge
proves `fat16`, plus a store layer that production doesn't use. It
doesn't prove `io.zig`, and it doesn't prove angry-gopher's store. That's
exactly the layer where "replace is wholly old or wholly new" is actually
kept or broken.

So yes, they should be unified, and I'd do it this way:

1. **One interface**, taken from what the application actually needs. The
   census says that's the six, plus `readAt` (now approved), plus `stat`
   and `has` (13 calls between them), `makeDir`, and `removeTree`.
   `resolve` stays inside the store. That's about eleven operations, and
   it matches angry-gopher's store almost exactly.
2. **angry-gopher's `store.zig` is the Linux implementation** of that
   interface. It already is, in all but name.
3. **The metal implementation is the same `store.zig`, ported**, over
   `io.zig`, as production runs it.
4. **`store_sim` drives those two plus the model.** That puts the
   production stack under the judge: angry-gopher's store, `io.zig` and
   `fat16` together, with power cuts.

gopher-metal's own three Store implementations then become the model and
the spec. The strict Linux store's rules already live in angry-gopher's
`fatName`; nothing is lost.

That's real work, but it's the most valuable test change on the table:
it moves the strongest judge we have onto the code that holds real data.
It's also exactly the platform seam the "web server in a box" needs: one
data interface, a Linux twin as strict as metal, and the judge for free.

## Where things can drift apart

"Drift" here means two places that must agree, with nothing checking that
they do. Ranked by what it would cost:

1. **The two Stores** (above). Until they're one, any rule changed in one
   isn't changed in the other.
2. **Limits angry-gopher copies from gopher-metal by hand.** angry-gopher's
   `store.zig` restates `fat16`'s longest name (96), `io.zig`'s longest
   path (256) and the deepest tree (16), each with a comment naming where
   it came from. I checked them today and they agree, including the depth,
   which the two repos count differently (16 parts counting the file and
   the root, against 15 folders). But nothing would notice if one moved.
   B5 moved the depth two days ago, and it happened to stay consistent.
   **A small gate check** that reads both files and compares would catch
   this for good.
3. **The SDK's commit isn't part of a release verdict.** gopher-metal builds
   against whatever SDK checkout sits beside it, so a verdict can describe
   code it didn't run. That's queued as B16; I nearly tripped on it today.
4. **Each named choice must keep the draw order of the code it replaced**,
   or saved seeds stop reproducing (CC's review). The replay tests catch a
   wrong order. A doc comment now says so.
5. **The docs against the code.** Yesterday's README sweep found four
   "defects" written in the present tense that had been fixed for weeks,
   and a knob list that was wrong. A cold review every couple of weeks is
   cheap.
6. **Simulator models against the RFCs.** Twice now, a model was wrong
   before the code was. The guard is the habit "read the RFC, not the
   model, before blaming the code", which CC already keeps.

Two places that look like drift risks but are already covered:
- **metal-vmm against QEMU:** `check.sh` holds the default machine to QEMU
  on every merge.
- **angry-gopher's code against the metal port:** `tools/lint_portable.py`
  refuses a server file that reaches around the I/O seam.

## What I'd do next, in order

1. **Ship v19** once its gates pass and you say go.
2. **The three-way explorer benchmark** on `fat_sim` and `store_sim`, and an
   honest write-up of where steering helps and where it doesn't.
3. **Unify the Store** as above. This is a good long assignment for CC,
   since it's all host-side and the judge already exists, while I keep the
   explorer.
4. **The limits check** in `gates.sh`, and **B16** (the SDK in the
   verdict), both small.
5. **Run CC's new device knobs on the box** and put what they reach on the
   metal floor.
