# The client drives: Dog Park with ticks, the server as notary

*2026-10-13. A first architecture for the next Dog Park feature: dogs near
your dog move on every tick (same breeds herd, different breeds keep
their distance). Single player; everything else in the park is the
machine's. The page runs the physics and the server mostly checks and
keeps what the page did. Written before any code. The questions at the
end are the decisions this needs from you.*

## The short version

- **The page is the game.** It runs every tick of the physics: your dog's
  moves and every automated dog near it. It never waits for the server
  to see what happens next.
- **The server is a notary.** The page sends what happened, tick by tick,
  as a report that is also a proof: the inputs, plus enough of the
  results to check. The server re-runs the same physics on the same
  inputs, and if it gets the same answer, stores it and says "kept
  through tick T".
- **The only brake is the ack.** The page may run at most N ticks past the
  last tick the server has kept. A fast server on a fast network acks
  long before the page gets there, so nobody notices it exists. A slow
  server slows the game down. It never makes the game wrong.
- **A refutation means rewinding.** If the server's re-run disagrees, it
  says where, and gives its own state at that tick. The page rewinds to
  that state, replays its own inputs from there, and carries on.
- **No server timer, no push to the browser.** The server answers
  requests, as it does today. Nothing in this design needs a clock tick
  inside the kernel or a stream to the page.

## Why this shape

The cows taught us the main lesson. Page and server agreed **to the bit**
only once they ran the *same compiled rule*: `cows.zig`, built natively for
the server and as wasm for the page. They also had to feed it the same
inputs in the same order. Every other agreement we tried drifted:
- a straight line where the page had recorded a path;
- a heading rebuilt from a chord;
- a whole-pixel rounding that wasn't the server's.

With a shared rule and shared inputs, prediction is not a guess: the page
*knows* what the server will compute.

So turn the arrangement around. Instead of the server computing and the
page predicting, **the page computes and the server checks**. Single
player makes that natural: nobody else's actions arrive between your
ticks, so the page has everything it needs.

## The tick

- **A tick is a step of the simulation, not a frame.** The page draws
  60 or more frames a second and interpolates between ticks. The
  simulation advances in fixed ticks, say 20 a second: each tick is the
  same amount of park time, so the physics does not depend on a
  browser's frame rate or a slow laptop.
- **A tick's inputs are only what the human did during it:** "dog 219
  was dragged along these points". Everything else is the rule's.
- **The rule is a pure function:** the state before, plus the tick's
  inputs, gives the state after.
  - **The state:** the active dogs' positions and anything they remember,
    such as a heading or a herd.
  - **The randomness:** a generator seeded from the park's seed and the
  tick number, so "random" is the same on both sides.
  - **The arithmetic:** integers, half pixels as the cows ended up, so
    nothing depends on how a machine rounds.
  - **The order:** dogs taken in id order, and neighbours found by a
    rule both sides compute the same way.
- **The active set is part of the rule.** "Dogs near the main dog" must
  mean exactly the same dogs on both sides, decided by the rule itself.
  For example: dogs within R of your dog at the start of the tick, plus
  any dog still moving from an earlier tick. Dogs outside it don't
  move, which keeps both the page's work and the server's re-run small.
- **The physics is local per dog,** as you said. Each active dog looks
  at its neighbours within a radius and decides its step:
  - **toward the centre of nearby dogs of its breed,** for herding;
  - **away from nearby dogs of other breeds,** for spacing;
  - **away from the main dog** if that turns out to feel right.

  Local rules are what make herds emerge, and they keep the cost
  proportional to the dogs actually moving.

## The report: a status that is also a proof

The page sends a report covering the ticks since its last one, one at a
time, as it does with moves today. A report is a small text language,
one line per tick, readable by a person and an agent alike:

```
dogpark-report v1 physics 7 from tick 1040
1041 drag 219 3456,4630 3455,4630 3453,4631
1041 hash 9f3a1c07
1042 hash 4b17e2d0
1043 drag 219 3450,4633
1043 moved 219 3450,4633 · 220 3441,4612 · 221 3466,4659
1043 hash 0c88f913
```

- **The header says what the report is:**
  - the physics version, so a page running old code is caught at once;
  - the tick it starts from, which is the last tick the server kept.
- **`drag` lines are the inputs:** the only things the server cannot
  work out for itself.
- **`hash` lines are the proof:** each is a hash of the whole active
  state after that tick. The server re-runs the tick and compares
  hashes. A hash per tick costs a few bytes and pins down exactly *which*
  tick went wrong.
- **`moved` lines are optional detail:** positions in plain text, for a
  person or an agent reading the log, and for working out *what* differed
  when a hash doesn't match. The page can send them every few ticks, or
  only for dogs your dog touched.
- **It doubles as the log.** Kept as-is, the reports are the game's
  history. The server can store them in an append-only file, which is
  exactly what a "proof of physics" should be: anyone can replay it.

## The server's job

For each report:

1. **Check the header.** If the physics version is wrong, answer "reload"
   and do nothing else. If the report starts at a tick other than the
   last one kept, answer with what the server has (see below).
2. **Re-run the ticks,** from its own copy of the state at the starting
   tick, with the report's inputs, comparing hashes as it goes.
3. **On agreement,** append the report to the game's log and answer
   "kept through tick T". Every so many ticks, say every 1,000 or every
   few seconds, also write a snapshot of the whole state. A restart then
   loads the last snapshot and replays the log since.
4. **On the first disagreement, at tick k:** keep everything before k,
   and answer "kept through k − 1; at k I have this", with the full
   active state at k.

**What "kept" means is a choice.** It could mean the tick was checked
and appended to the log on disk; then a crash never loses an acked
tick. On metal that costs about one disk request per report, a few
milliseconds at prod's ~2 ms, which a report every 100-200 ms easily
absorbs. I'd make "kept" mean "on disk", since that's the promise the
page relies on when it lets go of its own copy of those ticks.

## When the acks get slow

The page keeps every tick the server hasn't acked yet: its inputs, and its
state at the last acked tick. The window is N ticks.

- **Normally it is invisible.** A report every few ticks, acked within a
  couple of round trips, and the page never gets near N.
- **When acks lag,** reports simply get bigger. The page sends everything
  since the last ack in one report, and one report is in flight at a
  time, as today. A slow server sees fewer, larger reports, which is the
  cheapest shape for it.
- **When the page reaches N ticks ahead,** it stops advancing the
  simulation. Drags still show your dog under the pointer, but the
  automated dogs pause, or better, slow down smoothly as the page nears
  N. Small N means a short pause; large N means more to rewind after a
  refutation. N around 20-40 ticks, one to two seconds at 20 a second,
  seems right to start.
- **If the server is gone,** the game stops after N ticks and says so.
  Nothing past the last ack was promised, and a reload starts from the
  server's last kept tick. You lose at most N ticks of play.

So "the server's role is to slow the client down" falls out as one
number, N, and no extra machinery.

## When the server refutes the physics

A refutation means the page and the server ran the same rule on what the
page *thinks* were the same inputs and got different answers. It should
be rare, and each cause has its own answer:

| Cause | How it shows | What happens |
|---|---|---|
| The page runs older code than the server (a deploy mid-game) | the header's physics version | the server answers "reload"; the page reloads and resumes from the last kept tick |
| A determinism bug: something that differs between wasm and native (floating point, iteration order, an uninitialised value) | a hash mismatch on an ordinary tick | rewind to the server's state at tick k and replay. And it is a **bug report**: log the report and both states, because it will happen again |
| The server's copy differs: a restart lost something, or a second tab moved the same dog | the report's start tick doesn't match the server's last kept tick | the server answers with its state; the page takes it and continues from there |
| A tampered page | a mismatch where the rule is clear | the same rewind. Single player, so cheating only cheats yourself; the server's copy stays the truth |

**The rewind the page does:**
1. Take the server's state at tick k.
2. Re-run its own recorded inputs from k up to now.
3. Draw the result.

If the difference is small, the dogs glide to their corrected places over
a few frames instead of jumping. The jump log we built for the cows stays
useful here: every correction gets logged with its tick and its cause.

**What we would watch for.** The cows also showed the failure that this
design is most exposed to: a rule that is *right* but surprising, such as
a quantised heading or a sign flip near zero. The page and server would
agree perfectly on wrong motion. A hash can't catch that. Playing it,
with the debugging overlays you mentioned (the squares, the trails),
can.

## What this asks of metal

Very little, which is the point.

- **No kernel clock for apps, no streams.** Requests and answers, as
  today.
- **Bigger request bodies.** Dog Park's limit is 4 KiB. A report of 40
  ticks with drags and hashes could pass that. The body rule
  (drain before the turn, budgets) is built for this; the app just
  declares a larger limit for `/report`.
- **CPU per report.** The server re-runs every tick it acks, so the
  physics' cost per tick times the active dogs is the server's cost too.
  On one core, a slow physics step delays everyone's requests. The rule
  should be cheap enough that 40 ticks re-run in a few milliseconds, and
  the judge can measure that on metal.
- **Appends and snapshots.** A small append per report, a snapshot every
  few seconds. The 1 MiB requests and FAT runs we just shipped make both
  cheap. The "kept map" design already signed off for Dog Park (write
  what changed, about once a second) is the snapshot here.
- **The judge.** It already holds metal to Linux for Dog Park. Feeding
  both the same report and comparing their acks and logs covers the new
  route completely. Time doesn't enter at all, because the page owns it.

The clock-ticking and server-push work from the previous essay is
deferred, not cancelled: it comes back when there are two players, or a
park that moves while nobody is watching. By then we'll know what the
physics costs and what a report looks like, which is a much better place
to design a kernel timer from.

## Questions for you

1. **Tick rate.** 20 a second? It sets the feel of the automated dogs and
   the size of reports.
2. **N, the window.** 20-40 ticks (1-2 s) to start? And at the window:
   pause the automated dogs, or slow them down as the page nears it?
3. **What "kept" means.** On disk before acking (my pick), or checked but
   written in batches, with a crash able to lose acked ticks?
4. **The proof.** A hash every tick, with positions only every few ticks
   (my pick), or full positions every tick (bigger, and more readable)?
5. **The report's form.** The line-per-tick text above, or JSON? Text is
   easier to read and to log; JSON is easier to parse safely.
6. **Arithmetic.** Integers (half pixels) again for the dogs' physics, so
   we never chase a rounding difference?
7. **The active set.** Dogs within some R of your dog, plus any still
   moving. Does R track the screen, or a fixed park distance?
