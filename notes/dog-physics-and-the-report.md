# Dog physics, and the report that carries it

*2026-10-13. A proposal for how the other dogs move, and for the little
language the page sends the server. Written during the code freeze for the
repo renames: nothing here is built. It follows
[the client drives](the-client-drives.md), and takes your rules from
today as given:*
- *no randomness;*
- *lower number means more alpha;*
- *each tick cascades: the leashed dog, then the cows, then the other dogs
  from most alpha down;*
- *physics stays local to the leashed dog, with nothing acting more than
  a tile's width away.*

## The short version

- **Each tick is a pure function:** the board before, plus what the human
  did during the tick, gives the board after. No randomness, no wall
  clock.
- **One rule makes it settle: a dog only answers to those above it in the
  cascade.**
  - **Who's above it:** the leashed dog, the cows, and more alpha dogs.
  - **Who it ignores:** dogs further down, so a beta never pushes an
    alpha.
  - **Why that settles:** every dog's move depends only on dogs that have
    already moved this tick. Nothing can chase anything in a circle, so a
    board left alone comes to rest.
- **A dog wants three things, each with a comfortable band:**
  - to keep its distance from dogs of other breeds above it;
  - to keep near, but not on top of, the nearest more-alpha dog of its
    own breed;
  - to keep clear of the leashed dog and the cows.

  It moves only while something is outside its band. Once all three are
  satisfied, it rests.
- **About 1 px a second,** kept in thousandths of a pixel so a slow dog
  really is slow. That's 50 thousandths per tick at 20 ticks a second.
- **Awake means close.** Only critters within one tile's width (500 px) of
  the leashed dog take part. With no dog leashed, the park sleeps, and
  when every awake dog is resting, the page stops ticking and sends
  nothing.
- **The report is text,** one line per tick with the human's input, and a
  hash of the awake critters every few ticks. The server answers `kept`,
  `differ` with its own state, or `reload`.

## The cascade, and why it settles

Within a tick, in this order:

1. **The leashed dog** moves along the human's drag. Physics never moves
   it.
2. **The cows** react to the leashed dog, as they do today: the grid
   rule, each part of the move scaring the cows ahead of it. Cows ignore
   the other dogs.
3. **Every awake dog, by number, smallest first.** Each sees the positions
   of everything above it *as already moved this tick*: the leashed dog's
   new place, the cows' new places, and the more-alpha dogs' new places.
   It does not look at dogs below it at all.

That last rule carries the stability:
- **The most alpha awake dog** answers only to the leashed dog and the
  cows. Once you stop dragging, it settles.
- **The next dog** answers to that one too, which has settled, so it
  settles.
- **And so on down.** Each dog is chasing something that stops, so the
  whole board comes to rest.

Without the rule, two dogs that each step away from the other can
oscillate for ever, and an iteration order or a rounding decides who
wins. With it, the board has a direction: alphas set the scene and betas
fit around them.

It also gives you followers for free, as you wanted. A beta's anchor is
always someone more alpha, so a herd forms as a chain or tree hanging off
its most-alpha member. When you push the alpha around, the herd trails
after it at 1 px a second.

## What a dog wants

For one awake dog, call it D, each tick:

**1. Room from other breeds above it.** For each dog of another breed
above D, within the *wary* distance, D wants to be farther away. Its wish
is a step straight away from that dog, as long as the shortfall. These
add up, so a dog squeezed between two strangers is pushed out sideways.

**2. Its place in the herd.** D's *anchor* is the nearest dog of its own
breed that is more alpha, within the *follow* distance. If D has no
anchor, it is the herd's head and only keeps its room. Against the anchor:
- **Too far** (beyond the band's outer edge): D wants to step toward it.
- **Too close** (inside the inner edge): D wants to step away. This is
  "near but not on top".
- **In the band:** content.

**3. Room from the leashed dog and the cows.** The same as 1, with its own
distances. The leashed dog is the human's, so everyone gives it room.
Cows are big, so they get room too.

**The step.**
1. Add up the wishes.
2. If the total is zero, D rests this tick.
3. Otherwise D moves along the total, by the total's length or its speed
   per tick, whichever is less.

That "whichever is less" is what lets a dog arrive and stop instead of
overshooting and jittering around its place.

**Resting.** A dog all of whose wishes are zero has nothing to do. It
stays put until something above it moves into one of its bands. When
every awake dog rests and the human isn't dragging, the page stops
ticking altogether: no reports, no work for the server, until the next
drag.

**Breeds.** Today's five looks, which take turns by number (dog n has look
n mod 5). Same breed means the same look, so a breed's dogs are every
fifth number, spread through the park. Herds would form as you lead an
alpha among its kind.

**Starting numbers,** all to be tuned by playing:

| | |
|---|---|
| speed | 1 px a second: 50 thousandths of a pixel a tick at 20 ticks a second |
| awake | within 500 px (one tile) of the leashed dog, centre to centre, at the tick's start |
| wary of another breed | 150 px centre to centre |
| follow: looks for an anchor within | 400 px |
| herd band, to the anchor | 60 to 100 px: squares 20 to 60 px apart |
| room for the leashed dog | 80 px |
| room for a cow | 90 px |

Every distance is under 500 px, so the invariant holds: nothing reaches
further than a tile's width.

**Two dogs exactly on top of each other** have no "away" direction, and
the rule needs one. Take a fixed answer: the beta steps east, or north if
east is the wall. It will almost never happen, but a determinism bug
waits in exactly that kind of corner.

**Arithmetic.** Positions in thousandths of a pixel, as integers, with an
integer square root for distances. The cows taught us that page and
server agree to the bit only through the same compiled code. Integers
also make the report readable: a position is written as `3441.250`, and
that is exactly what is kept.

## What "awake" should mean

You said: asleep outside the subscribed tiles, and asleep inside them too
when the leashed dog is far enough away. One part of that needs a
decision.

**Subscriptions depend on the screen,** its size and where you've
scrolled. If they decided who is awake, the size of a browser window
would change the physics. The server would then need the subscriptions as
an input to every tick, and two windows of different sizes would disagree.

So I'd define awake purely as **within 500 px of the leashed dog**. Then
the page keeps one promise: it always subscribes at least 500 px around
the leashed dog. That already holds while the dog is on screen and the
margins are a tile; where it doesn't, the page subscribes the extra
tiles. The physics stays a function of the board and the human's input
alone, as you put it.

## The report

One report per round trip, as moves are sent today: everything since the
last tick the server kept. Lines, one thing per line, readable by you, by
an agent, and by a five-line parser:

```
dogpark 1 physics 1
from 1040 3c1f09a2
leash 219
t 1041 3456,4630 3455,4630 3453,4631
t 1042 3452,4631
t 1043
t 1044 3450,4633
h 1044 0c88f913
t 1045..1063
h 1063 77e1b0c4
rest 1063
```

| line | says |
|---|---|
| `dogpark 1 physics 1` | the language's version and the physics' version. A mismatch means "reload", nothing else |
| `from T H` | the tick the report starts after (the last one the server kept) and the hash the page has for it: both sides check they start from the same board |
| `leash D`, `release D` | the human's leash, which decides who is awake |
| `t T x,y …` | tick T, and the whole pixels the leashed dog was dragged through during it. `t T` alone: a tick with no drag |
| `t A..B` | ticks A to B, none with a drag: the board settling. A long stretch costs one line |
| `h T H` | the hash of every awake critter after tick T (each one's number, kind and position, in cascade order). One every few ticks, and always the last |
| `rest T` | after tick T every awake dog rests: the page stops ticking until the next drag |

Optional, for people more than for the server, every so often or after a
correction:

```
at 1044 dog 220 3441.250,4612.000 dog 221 3466.500,4659.000 cow 23 3354.0,4622.5
```

**The server's answers:**

```
kept 1063
```
```
kept 1043
differ 1044
board 1044 dog 219 3450,4633 dog 220 3441.250,4612.000 cow 23 3354.0,4622.5 …
```
```
reload physics 2
```

- **`kept T`:** checked, written to the game's log on disk, and safe.
- **`differ T`** with a **`board`:** the first tick the server's re-run
  disagreed. Everything before it is kept. The board is the server's,
  every awake critter, and the page rewinds to it and replays its own
  ticks from there.
- **`reload`:** the page's physics is not the server's. Reload and resume
  from the last kept tick.

**Why it's cheap to check.** The server keeps the board at its last kept
tick and re-runs the report's ticks: the cascade over the awake critters,
each looking only at neighbours within 500 px. With tens of awake dogs,
40 ticks is a small amount of arithmetic, a few milliseconds even on
metal's one core. The judge can hold that to a number.

**The log is the reports, as written.** The server appends each kept
report to the game's log file. Its sizes:
- **A drag:** about 30 bytes a tick.
- **A settling stretch:** one `t A..B` line, however long.
- **A hash:** a few per report.

Every few seconds the server also writes a snapshot of the whole board.
A restart then loads the last snapshot and replays the log after it,
which is exactly the re-run the server does for every report anyway.

## What this leaves open

1. **The asymmetry.** Betas yield and alphas never do. That's what makes
   it settle, and it reads naturally ("the alpha doesn't move for you").
   But a big herd jammed against an alpha won't budge it. Is that the
   behaviour you want?
2. **Awake by distance alone,** 500 px from the leashed dog, with
   subscriptions only promising to cover it?
3. **The anchor.** The *nearest* more-alpha dog of the breed gives chains
   and clumps. Following the herd's head, the most alpha in range, gives
   tighter herds that all orbit one dog. I'd start with nearest.
4. **Cows ignore dogs other than the leashed one.** Simple, and keeps cows
   near the top of the cascade. Should other dogs ever push cows?
5. **The numbers.** All of them are guesses. Since the board settles and
   nothing is random, a page-only "replay this drag at 10× speed" would
   make tuning fast. That would be a debugging tool, not a game feature.
6. **The hash's cadence.** Every 10 ticks and at the end of each report?
   More often pinpoints a bug faster; less often makes reports shorter.
7. **What a tick is when nothing is leashed.** The proposal: no ticks at
   all, and the park is frozen. A dog let go stays awake for the leash's
   5 s, then the park sleeps. Or should it keep settling until it rests?
