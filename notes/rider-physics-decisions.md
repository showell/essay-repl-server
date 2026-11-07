# Rider physics: the calls that are yours

A review of the rider's motion (Rider, RiderState, Throttle, LeanSearch, Bike, Coast, VehicleLimits, Gaze, CrossingReaction, RideFocal, ViewYaw) checked the earlier notes in rider-physics-findings.md. Every finding there still holds; only names were fixed. The review also found new ones. This is the part that moves pixels or needs your judgment. My recommendation follows each item.

## Already decided, pixels hold (a lane after the spot merge)

**Motion and the eyes come apart.** Motion never reads the eyes, but the modules tangle them.
- Gawking, which is a throttle limit, lives in Gaze. A new `Gawking` module takes it, and Throttle imports Gawking, not Gaze.
- `CrossingReaction.Reaction` packs a throttle answer with a camera answer, each read by a different module. It becomes two functions.
- Throttle's four limits, which today take four argument shapes, all answer `[NoLimit, AtMost(Acceleration)]`, folded with `min`.

The private helpers leave the public blocks too, and `base_speed` becomes `starting_speed`.

## Clear, but they move pixels (an eye test each)

1. **The ride ends by teleport.** A rider within 60 m of the end and slower than 0.1 jumps to the end. Brake to a stop instead. Only the last frames change. *Recommend: yes.*
2. **Round trips through `Decision`.** The best lean becomes a delta and is added back, and the allowed speed becomes an acceleration and is applied back. Bike should take `Controls : { lean, speed }` directly. `s + (x - s)` isn't always `x` in floats, and the ride is chaotic, so the whole ride drifts slightly. *Recommend: yes, with an eye test.*
3. **Coast counts from 0.** A rider who leaves the road on the first step gets `after: 0`, and a `max(1.0)` papers over it. Count from 1. *Recommend: yes.*

## Design deletions (the earlier notes leaned toward deleting all four)

4. **The lift to exit speed.** Near a bend, a rider below the turn speed jumps up to it in one step. It never raised speed in 7,000 steps, but its gawking exception fired 533 times to defeat it, and that exception is the only reason `is_gawking` has to outlast the look. *Recommend: delete.*
5. **`lean_target`.** It aims 30% of the rider's own offset back toward the middle, so it moves with the rider: a gain, not a line on the road. It jumps at 0.04: `target_of(0.039)` aims outward and `target_of(0.04)` aims inward. *Recommend: aim at the middle and delete the rule. If you want a line, it should be a place the route chooses.* The other side: the weave may read as life.
6. **`lean_hold` (2°).** It holds the throttle off at 2° of lean or more. It fired on 792 steps, and turning it off kept the ride on the road. *Recommend: delete.*
7. **Gaze's three numbers for the return.** A 5% geometric ease never reaches zero, so a snap ends it, and the depth fade starts only once the snap lands. `clamped_within` reaches zero by itself, so one return rate would do. *Recommend: one rate, with an eye test.*

## Numbers that stand for nothing yet

8. **`bend_approach` (60 m)** stands in for a braking distance, and it now carries three meanings: where the bend brake starts, the stop zone, and the truck's brake distance. The physical rule is to start braking when the distance left equals the braking distance at a firm brake. *Recommend: `VehicleLimits.firmest_brake`, and let the bend brake start when it's needed.* The other side: 60 m works, and 40 m and 120 m both stay on the road.
9. **The six `turn_speeds`** were fitted to a formula within 0.85%, with no derivation. The table also copies World's turns, and `turn_speed` crashes on any other. *Recommend: derive it before the Motion chapter; until then leave it.*
10. **The brake's `e^(-n/20)` fade, and `turn_per_lean` 0.1** have no derivation. *Recommend: leave until the Motion chapter.*

## Questions for the Motion chapter

11. **One record for the rider, or two?** RiderState holds both the bike's motion and the eyes. Split, motion stands alone, which the Motion chapter wants. *Recommend: split, after the in-flight lanes, since it needs RideInstant.*
12. **`heading` is stored twice over**, in RiderState and in Bike, and its only readers are the mountains and the sun. Store one angle. *Recommend: with the World lane, which gives each segment an entry bearing.*
13. **The bike turns in place.** `yaw += 0.1 × lean` on every step, even at speed 0, so a stopped bike that leans pivots, and no rule caps the lean. Either the turn per step depends on speed, or the type gains a maximum lean. *Recommend: turn with speed. That's physics, and it's the Motion chapter's first lesson.*

Mark each with a word or a number.

## Steve's answers (2026-11-07)

Agreed to every recommendation. Each one that moves pixels gets a careful eye test.

**A Motorcycle module.** Steve: "It's always just felt wrong that we don't have one, and it seems to fit some of the spirit of splitting rider state. The rider is on the Motorcycle, which keeps state for throttling and lean. RiderState then can have RiderEyes or similar for gaze." The shape for the split, item 11:

- `Motorcycle` owns the motion: where it is, its speed, lean and heading, and the controls it takes (`Bike.Controls` from item 2 becomes `Motorcycle.Controls`). Today's small `Bike` module, which holds the motion step, grows into it.
- `RiderEyes` holds the gaze and the look depth.
- `RiderState` is the rider on the motorcycle: `{ motorcycle, eyes }`. Throttle and LeanSearch read the motorcycle, and Gaze reads the eyes.

This lands with the rider lane, after the spot lane merges.
