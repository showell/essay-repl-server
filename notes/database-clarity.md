# Code clarity, borrowed from databases

*2026-11-08. The follow-up you asked for: easy wins for the code, from the one-frame-as-a-database riff. No SQL in the code, not even pseudo-SQL, and no structural overhaul. What a database designer would do with the meaning, kept in Roc.*

---

## What we borrow, and what we don't

What a good schema gives you is mostly not the query language. It's four habits:

1. **Every table says what it is**, and the schema can be read without reading the queries.
2. **Every row has a key**, and a key is never confused with a count or a measurement.
3. **Stored and derived are never mixed**: a column is either a fact or a view, and you can tell which.
4. **Constraints live with the data**: the rules every row must keep are written once, next to the data, and checked.

Safari already does most of this, often by accident. The wins below make it deliberate and visible. Each one is small, local and checkable by the gate.

## 1. Make the static world readable as a schema

`World.roc` builds the whole static world: segments, trees, herds, the pond, which segments get a cat or a bird. Someone opening the file sees functions. A database person would want the schema on the first screen.

**Win:** a header comment in `World.roc` that lists what the world holds, one line per "table": what it is, what it's keyed by, where it's built. Plain prose, no SQL. For example: "The route: a list of segments, numbered from 0 by `Route.SegmentIndex`. Each segment holds its trees, keyed by their place along it; its herds; its pond, if it has one; and its one encounter." It's a comment, so it's cheap, and it makes the static half of the book's diagram readable in the code.

## 2. Say on every module whether it's stored or worked out

The book's spine is "four things are remembered, and everything else is worked out." The code says it only in `RideInstant`'s doc. Every other module leaves the reader to discover whether its value is kept or recomputed.

**Win:** a one-line convention at the top of each module whose main type is shown on screen. "Worked out each frame from the clock." (SunPath, Sky, the headlights.) "Worked out each frame from the encounter plan and the clock." (the cat, the bird.) "Worked out each frame from the rider's place and the route." (every sighting.) "Kept: one of the four things the ride remembers." (Rider, TruckProgress, Clock, EncounterPlan.)

This is a view's definition in one sentence: it names its inputs. It costs one line per module, and a reader who has read the book recognises the spine in every file. A lint could even check that each module with a main type says one or the other, but I wouldn't start there.

## 3. Check the static world's constraints where it's built

A database enforces its constraints on every insert. Safari's static world is built once, by `World`, and it has rules. Today they live in the code that relies on them, or nowhere. `World.roc` has 4 expects:

- every segment's length is positive;
- each segment number appears once, in order from 0;
- a midway tower stands only on a segment longer than a kilometre;
- a cat or a bird only on segments long enough for its encounter to play out;
- every bend's turn is a real turn, neither zero nor straight back (the loud crash added today is the runtime half of this);
- the pond's ducks are inside the water (now checked).

**Win:** a handful of expects in `World.roc`, or a `WorldExpects` in gates/expects, that state these over the real route. They're constraints in the database sense, written once, next to the data, and run on every gate. Today a route edit that breaks one would show up, if at all, as a wrong frame or a crash at some step.

## 4. Keys are types; give the remaining ones a name

`Route.SegmentIndex` is a good key: opaque, can't be added to a count, and looked up in one place (`Route.segment_at`, which crashes on a missing key, like a foreign key that must exist). `Beacon.TowerPlace` (`AtEnd` or `Midway`) is the other half of a tower's key.

**Win:** where something is identified by a pair, name the pair. A tower is identified by `{ segment, place }` in Beacon, TowerSighting and the widget. One named record, `TowerKey`, beside `TowerPlace`, would let a reader see "this is how a tower is known" in one line. Trees are identified by segment plus position, but nothing needs to look a tree up, so they don't need a key type. I'd do towers only.

## 5. Views take only the columns they read

A view names the columns it uses. A function that takes a whole `RideInstant` when it reads only the clock hides that, and it also makes the function harder to test (you need a whole instant).

**Win:** an audit, done by an agent, for functions that take a wide record but read one or two fields of it, and narrow each to what it reads. The type walk already shows each function's inputs, so this is mechanical. I expect few hits, because the step functions already take `{ rider_distance, route }`-style records, but it's the cheapest way to make "what does this depend on?" answerable from a signature. `FrameView.ride_facts` is the place to look first.

## 6. Derived values aren't stored beside their sources

Today's sightings lane already showed the instinct: it made `Spot.drop` a method worked out from the foot, not a stored field. The database rule is the same: don't store what you can derive, or the two will disagree.

**Win:** an audit for records that hold a value next to the source it's derived from. One I know of: `RiderCamera`'s record carries `heading`, which `of` derives from the route and `yaw` (the encounter audit judged it fine, since `of` is the only builder). Most hits will be fine for that reason. The win is a short list, each with a sentence in its doc saying why it's stored (speed, or a single builder), like the one honest cache (`RoadView`'s worked bends) already does.

## 7. Name the filters

The sighting refusals are the `WHERE` clause of the frame: `BehindCamera`, `TooSmall`, and now `BelowHorizon`. They're consistent tags already, but they're spread across Pipeline, the sightings and the critters, and no one place says "these are the reasons something in the world isn't drawn."

**Win:** `Pipeline`'s module doc lists the refusals, each with one line on what it means and where it's decided. That's documentation, not a new type: the error-alias lint rules out a shared alias, and it's right to. It's the place a reader goes to answer "why isn't the cow drawn?"

## What I'd not do

- **No query layer, no table type, no generic "entity".** Records, lists and tags are already the right shapes, and a generic layer would hide them.
- **No renaming to database words.** "Sighting", "spot" and "picture" are better than "row", "projection" and "result". The database is a way of thinking, not a vocabulary.
- **No change to how anything is stored or stepped.** Every win above is a comment, an expect, a named record, or a narrower signature.

## Order

1, 2 and 7 are comments: one small lane, all at once. 3 is expects: one lane. 4, 5 and 6 are audits first, then small fixes. None moves a pixel or changes a type's meaning.

If you like it, I'd start with 3 (constraints on the static world), because it's the one that can catch a real bug. Then 1, 2 and 7 together, because they make the spine visible in every file.
