# The beacon, from first principles

*2026-11-08. This answers your comment on open-calls-8: the alternatives, with their type signatures.*

---

## What's there now

The beacon is already one module, `Beacon.roc`, but it holds two types:

```roc
Beacon :: Steps                  # the head start: how far into its blink at step 0
    of_segment : Route.SegmentIndex -> Beacon
    opposite   : Beacon -> Beacon          # the mid tower's, half a blink on
    lit_at     : Beacon, Clock -> Beacon.LitBeacon

    LitBeacon :: Fraction        # one moment of the blink: how bright
        brightness : LitBeacon -> Fraction
        disc       : LitBeacon, { center, metre_on_screen } -> Try(Shape, [TooDim, TooSmall])
```

`TowerSighting` calls `Beacon.of_segment(index).lit_at(clock)`, and the mid tower's is `.opposite().lit_at(clock)`. It hands the `LitBeacon` to `Tower`, which holds it as a field and asks it for its disc.

Your model has a beacon with a phase given by the route, a brightness that's a pure function of the clock and that phase, and a pink disc drawn at that brightness. That's one thing with one derived number. `LitBeacon` is the second type that model doesn't need.

## A. The beacon is its phase

```roc
Beacon :: Steps.{
    of_segment    : Route.SegmentIndex -> Beacon
    opposite      : Beacon -> Beacon
    brightness_at : Beacon, Clock -> Fraction
    disc          : Beacon, { clock : Clock, center : Screen.Point, metre_on_screen : Pixels } -> Try(Shape, [TooDim, TooSmall])
}
```

- **What it is:** the beacon is what the route gives it, and brightness is just a `Fraction`, worked out when asked.
- **Who touches the clock:** `Tower` holds a `Beacon` and has to pass the clock through to draw it. So the drawing side needs the clock.

## B. The beacon is how bright it is now

```roc
Beacon :: Fraction.{
    at   : { segment : Route.SegmentIndex, place : [AtEnd, Midway] }, Clock -> Beacon
    disc : Beacon, { center : Screen.Point, metre_on_screen : Pixels } -> Try(Shape, [TooDim, TooSmall])
}
```

- **What it is:** the beacon is what the scene draws, a pink disc at some brightness, like `Truck` is its lamps this frame.
- **Where the rest goes:** the phase never becomes a type. The stagger, the mid tower's half-blink offset and the sinusoid are private helpers inside `at`.
- **Who touches the clock:** the sighting works it out with the clock in hand, and the drawing only paints what it's given. That's "a sighting decides, drawing paints".
- **The stagger's home:** the open tower/beacon question was where the stagger and the mid tower's `.opposite()` should live, since today they're split between Beacon and TowerSighting. In B both are in `at`, and `opposite` goes away.

## C. Keep the phase, drop the second type

This is A, with B's single place for the clock:

```roc
Beacon :: Steps.{
    of_tower      : { segment : Route.SegmentIndex, place : [AtEnd, Midway] } -> Beacon
    brightness_at : Beacon, Clock -> Fraction
}
```

`Tower` holds `{ yaw, brightness : Fraction }`, and draws the disc itself with a private `beacon_disc`.

- **What it is:** the beacon is its phase, and the tower holds a plain number.
- **The catch:** the disc's look (pink, 3 m, the too-dim and too-small rules) moves into `Tower`, so the beacon's appearance no longer lives with the beacon.

## Lean: B

It has one type and one module, and the type is the thing on screen, which follows your naming rule. It also settles the stagger question. The blink stays a pure function of the clock and the segment, as you described it. What it costs is that "phase" no longer has a name in the types; it's only a word in `at`'s comment.

The pixels hold under all three, since the arithmetic stays the same.

---

## Also from your replies

- **The ground curve:** towers are the odd ones out on purpose. They sink on `exaggerated_drop`, a curve five times tighter, so a far tower goes behind the horizon at 1.8 km. Trees, critters and billboards don't sink at all, and the truck and ground patches use the real curve. A lane will check whether one rule through `EarthCurve.raised_ground_point` for every sprite makes the code smaller. It acts only if the answer is yes, with towers kept on their own curve. Either way it reports first.
- **Sounds:** this doesn't affect Safari, which has no tones. I'll take A, the loud refusal of a 33rd tone, as a quick win in lib.
- **The `Encounter` type and the point conversion:** both go to lanes now.
