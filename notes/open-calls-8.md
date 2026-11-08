# Open calls 8: five design calls from the audits

*2026-11-08. These are the five weightiest of the queued calls. Each has a lean; a word inline is enough.*

---

## 1. An `Encounter` type

Each segment has one of three encounters: a cat crosses, a bird is there, or the road is quiet. Today `[CatCrosses, BirdHere, QuietRoad]` is spelled out by hand in four modules, with `has_cat` and `has_bird` helpers beside it. World also has crashes for branches that can't happen.

A named type gives the union one home. The helpers become matches, and the impossible branches go away.

**Lean:** a new module, `Encounter.roc`, rather than nesting it in Segment. The cat, bird and throttle chapters all name it, and it reads better as its own noun.

## 2. Beacon and LitBeacon

`LitBeacon` has the adjective smell your naming rule rules out. It's also false at brightness 0, when the beacon isn't lit at all. The fix matches SunPath/Sun and TruckJourney/Truck:

| Today | After |
|---|---|
| `Beacon` (the blinking over time) | `BeaconBlink`, the activity |
| `LitBeacon` (what the scene draws) | `Beacon`, the thing |

**Lean:** yes. It reaches the beacons chapter and its widget, and it's one cleanup lane's work.

## 3. Everything sits on the curved ground

The ground curves away from the rider. The ground patches and the truck sink with it, but trees, stills, billboards and birds stand on the flat level. At 300 m that's about a pixel, and it's a rule with two answers.

The truck lane is already making `EarthCurve.raised_ground_point` the one home for lowering a point. Every object could stand on it.

**Lean:** yes, after the truck lane merges. Pixels move, so the held hashes are re-pinned once in that commit. They'd move by about a pixel at the horizon.

## 4. CanvasApp.sounds: a cap of 32 tones

`sounds` returns one U32 with a bit per tone, so an app can never signal a 33rd tone. Nothing says so, and WasmApp's crash names the wrong limit.

- **A:** keep the bit set, and refuse an app with more than 32 tones when it starts, with the number named. It stays cheap at the wasm edge.
- **B:** `List(U32)` of tone indices. There's no cap, but it touches pong, breakout, snake and workshop, and the JS edge.

**Lean:** A. No app comes close to 32, and the failure becomes loud.

## 5. Two point types in lib

`Point.Point` is `{x, y}` in F64, and it's what Point, Shapes and Brush use. `Math.Vec2` is `{x, y}` in F32, copied from roc-ray along with Camera, Mouse, Keys and Random. Camera converts between them by hand, field by field.

- **Keep both:** examples ported from roc-ray change only their import line.
- **One home:** one point type, at the cost of differing from roc-ray.

**Lean:** keep both, but make Camera's conversion one named function in one place, so the seam is visible and has one home.

---

Still queued behind these: SegmentPlace's rename, FocalLength, the widget palette and captions, the platform items, and a few smaller ones. They're the next note.
