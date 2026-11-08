# Open calls 10: five smaller design calls

*2026-11-08. These are the next five from the audits. Each has a lean; a word inline is enough.*

---

## 1. "Place" means two things

`RoutePlace` is a point on the route: which segment, and how far along and across it. `SegmentPlace` is where a segment lies from the rider: the one the rider is on, one ahead, or just behind. Both are called a place, and they mean different things.

**Lean:** rename `SegmentPlace` to `SegmentFromRider`, since it answers "where is this segment, seen from the rider?". It's wide: RoadAhead, every sighting and the math layer chapter. The word is yours, though, if you have a better one.

## 2. FarHeight means two things

`FarHeight` is a height far off, as the resting lens draws it. The sun's height above the horizon is one, and so is the size of something at infinity, like the sun's disc. One is a place and the other is a length: the book's "places and distances" again.

**Lean:** add `FarLength` for the sizes, so that a `FarHeight` minus a `FarHeight` gives a `FarLength`. It's small: SunPath, Sun, Lens and the sky.

## 3. A sunk tower is still sighted

A tower that has gone wholly behind the curve of the earth is still sighted, and it draws an empty picture. Every other kind refuses at the sighting (`TooSmall`, `BehindCamera`).

**Lean:** refuse it at the sighting with `BelowHorizon`, so that a sighting always means something is drawn. Pixels hold.

## 4. The bird's pose words

Two widgets name the same bird pose differently: "Side up" in one, "Side on, wings up" in the other.

**Lean:** "Side on, wings up", and the words belong to the kind, as `Bird.pose_name`, with `Cat.pose_name` beside it. Then every widget says the same thing.

## 5. One palette for the widgets

The widgets' colors (captions, plan view, highlights) are spread over several widget modules. PlanView's top-down map has its own set.

**Lean:** one `WidgetPalette` module in widget_kit, holding PlanView's colors too, under names saying what each is for. That's the one home for "what color is a caption".

---

Still queued after these: the widget captions, the "still" word, the platform items, and the smaller ones.
