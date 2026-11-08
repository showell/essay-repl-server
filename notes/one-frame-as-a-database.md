# One frame as a database

*2026-11-08. A riff on your thought experiment: forget time, and render a single frame. What does Safari look like if it's a database?*

---

## The tables

Freeze the ride at one step. Everything in the picture is a row somewhere.

| Table | Key | Columns | Where it lives today |
|---|---|---|---|
| segments | `SegmentIndex` | length, turn at the end, scheme, encounter, herds | `World.bending_plans` |
| trees | (segment, position) | along, across, `Conifer` | `Segment.trees`, built once |
| herds | segment | cow count, rows, bull, pigs | `CowHerd`, `PigHerd` |
| ducks | (segment, n) | where on the pond, facing | `Pond.placed_ducks` |
| towers | (segment, `AtEnd` or `Midway`) | none: everything about a tower follows from its key | `TowerSighting` |
| rider | the one row | place, yaw, speed, lean, gaze | `RideInstant.rider` |
| truck | the one row | route position, speed, pace | `RideInstant.truck` |
| clock | the one row | step | `RideInstant.clock` |
| encounter plan | the one row | when the encounter on this segment starts | `RideInstant.encounter_plan` |

The first five are the static world: built once, only ever read. The last four are the book's spine, the four things remembered. Those are the only rows that ever get updated.

The towers row is the best one: the table has a key and no columns. A tower is fully determined by where it is. A database person would say it isn't a table at all, just a view over segments, and they'd be right. That's exactly what `TowerSighting` is.

## Everything else is a view

The sun, the sky's colors, the beacons' brightness, the headlights, the cat's pose, the bird's place in its flight: none of them are stored. Each is a view: a query over the four rows and the static tables.

- **The sun:** `SELECT direction FROM clock`. It's a pure function of one column.
- **A beacon:** `SELECT brightness FROM towers JOIN clock`: its key gives the stagger, the clock gives the phase.
- **The cat:** `SELECT pose FROM encounter_plan JOIN clock`.
- **The headlights:** `SELECT darkness >= 0.412 FROM clock`.

"Worked out, not stored" is the database rule against derived columns: never store what a view can compute, because two copies can disagree. "One home for a rule" is the same discipline applied to code: one definition, everything else reads it.

There's one honest exception, and it's honest in both worlds. `RoadAhead.RoadView` keeps the worked bends beside the route, a cache documented as a cache. In database terms that's a materialized view: derived, stored for speed, and labeled as such.

## Rendering is one query

Your agent that "renders everything in the database" would write this:

```sql
SELECT picture FROM sightings      -- every entity the camera can see
WHERE NOT behind_camera AND NOT too_small AND NOT below_horizon
ORDER BY depth DESC                -- far to near
```

That's `FrameView` and `Scene`, almost line for line:

- `Pipeline.sighting_of` is the join of each entity with the camera.
- The refusals (`BehindCamera`, `TooSmall`, and now `BelowHorizon`) are the `WHERE` clause.
- `Scene.scene_renderings` is the `ORDER BY`.

Your sightings question this evening was, in these terms, "why isn't the drop a column of the sightings view?" Once it is, the `WHERE` clause can filter below-the-horizon rows up front, the way a query planner pushes a filter down to where the data is.

The three sorts (solids, cards, far scenery) are three ways to turn a row into pixels. In a database they'd be three render methods keyed on a type column. Roc does that with a tag and a `match` that must cover every tag.

## Correct by construction, both ways

You put it well: in a badly modeled database the data is ambiguous, and in badly typed Roc you get `crash "unreachable"`. The tools for keeping shapes right line up:

| Database | Roc |
|---|---|
| a `CHECK (0 <= x AND x <= 1)` constraint | `Fraction`, an opaque type whose only maker checks |
| a domain type (`metres`, not `float`) | `Distance`, `Along`, `Across` |
| a foreign key | a `SegmentIndex` that can't be confused with a count |
| `NOT NULL` | no optional fields: a missing thing is a tag (`NoBendAhead`) |
| a type column plus rules about which columns apply | a tag union with a payload per tag |
| a view | a function |
| normalization | one home for a rule |

The last two rows of the first half are where the two worlds part ways. Databases are bad at sum types: "a crown is either cones with a shade, or triangles" becomes a type column plus a nullable `shade` column plus a rule nobody enforces. Roc says it in one line, and the compiler holds every `match` to it. That's also, I think, the real content of Richard's pushback on ORMs. It isn't that Roc has no objects. Records and lists map to rows and tables easily, but tags don't map cleanly to anything in SQL, and tags are where Roc's correctness lives.

## Where time comes back in

You set time aside, and it's worth saying what we set aside:

- **The four rows that change** are the only part that needs history. A database would keep them in a log table, and that's exactly `Tour`: an append-only list of instants, so stepping back is reading an earlier row, not undoing anything.
- **The order within a step** is the transaction order. The rider reads the old clock's encounter stage, then moves, then the truck reads the moved rider. In database terms those are three statements in one transaction whose order matters, because each reads what the last wrote. It's the same mutual effect the book's spine is about, and databases find it just as hard: it's why isolation levels exist.
- **The truck** can't be a view of the clock, because it depends on the rider's history. That's the line between a derived column and a stored one, drawn by the data itself.

## What this suggests for the book

Tables are good for people, and the book already leans on them: the four-at-a-glance table, the three sorts, the first-pig table, the proof's frame table. The thought experiment suggests three more that would show the program as data:

1. **The route as a table.** `World.bending_plans` is already configuration; show the first few segments as rows (length, turn, scheme, encounter, herds) beside the code that declares them. It's the "it reads like configuration" point made visible.
2. **One frame's sightings as a table.** At step 1,529: kind, `right`, `forward`, depth, and which refusal (if any) dropped it. That's the `WHERE` clause and the `ORDER BY` shown with real rows. The numbers can be pinned by expects, the way the 1,529 counts now are.
3. **Stored or worked out, per thing.** Every visible thing in one column, and in the next either "stored (one of the four)" or "worked out from …". It's the spine as a lookup table, and short.

None of these needs a database; they need the program's own values printed as rows. I'd put the first two where the route and the sightings are introduced, and the third in Zooming back out, next to the four-at-a-glance table.
