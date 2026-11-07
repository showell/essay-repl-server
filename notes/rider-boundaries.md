# The rider's boundaries

Steve: "Rider is quite heavy (so it should delegate to motorcycle). The RiderState class is really light… It defines a structure and way to initialize one, but then it has no API to create the 2nd, 3rd, etc. That feels asymmetric… This is the most fundamental type of the system."

## What's there today

- **`RiderState`** (21 lines): a record `{ segment_index, motorcycle, eyes }` and `initial`. That's all.
- **`Motorcycle`** (130 lines): `{ along, across, yaw, speed, lean }` in the *segment's* frame, with `initial` and `motorcycle_at_next_step(controls)`, the pure physics of one step.
- **`RiderEyes`** (15 lines): `{ gaze_yaw, look_depth }` and `initial`. `Gaze` moves it.
- **`Rider`** (233 lines with tests): a bag of functions over the other three.
  - `rider_state_at_next_step` is **RiderState's** transition.
  - `is_finished` is a question about **RiderState**.
  - `decide`, the lean search plus the throttle, is the rider's **mind**.
  - `rider_on_next_segment` rewrites the motorcycle's `along`, `across` and `yaw` into the next segment's frame with a record update. That's **Motorcycle's** geometry, done from outside.
  - `stopped_at` and `is_at_segment_end` are **Motorcycle** questions, asked from outside.

So you read it right: the type that defines the state doesn't define its next state. The step lives in a namespace beside it, and that namespace reaches into Motorcycle's fields to do Motorcycle's work.

## The deeper smell: the rider's location is split in two

`motorcycle.along` means nothing without `segment_index`, which lives one level up in RiderState. Crossing a bend changes both together: the index goes up by one, and the motorcycle's coordinates are re-anchored to the new segment. Neither type owns that move, so Rider does it by hand, touching both. That's the real reason the step can't live in either type today.

## A proposal

Give each noun its own job:

1. **Motorcycle owns everything about where it is in its segment's frame.** It already does the physics. It gains `crossed(bend) -> Motorcycle` (re-anchored onto the next segment), `stopped_at(along)` and `has_reached(length)`. Rider stops doing record updates on it.
2. **RiderState owns its own step, so it gains `next`.**
   - `RiderState.initial` and `RiderState.next(state, { route, encounter_timing }) -> RiderState` sit side by side, plus `is_finished`. That's the symmetry you asked for.
   - Inside, `next` asks the mind for controls, moves the motorcycle, crosses the bend when the move puts it past the bend and still on the next segment's road (the cross-or-not decision stays here, because it needs the index and the route), and then moves the eyes.
   - RiderState is the one place where the segment index and the motorcycle move together.
3. **Rider shrinks to the rider's mind:** `Rider.controls(motorcycle, road) -> Motorcycle.Controls`, the lean search plus the throttle. The look stays in Gaze, the eyes' mind, as now.

The call chain is then: RiderState (bookkeeping) → Rider (decides) → Motorcycle (moves) → Gaze (looks). Each one is small, and none reaches into another's fields.

## A naming option, which follows from that

Once Rider is only the mind and RiderState is the thing that rides, the names are backwards. The thing should be **`Rider`**, with `Rider.initial` and `Rider.next`, and the mind module should be something like **`RiderMind`** (or `Riding`). That rename reaches about 30 files and the parked book, so it's optional and separate from the restructuring.

## Steve's answer (2026-11-07)

"Do your suggestions first. It seems kinda crazy that motorcycle doesn't already hold a RoutePlace. We never actually draw a motorcycle. So the Motorcycle type's job is to keep track of where it is, how fast it's moving, etc."

Plan: lane 1 does the proposal above (Motorcycle owns its geometry, `RiderState.next`, Rider shrinks to the mind). Lane 2 then gives Motorcycle a `RoutePlace`, so it holds where it is on the route. The rename (Rider and RiderMind) waits until after lane 2.

## Not proposed (yet) (superseded: Steve wants RoutePlace)

The bigger fix for the split location would be one `RoutePlace { segment_index, along, across }` that a motorcycle holds, so its coordinates carry their segment. I think that goes too far: the physics is cleaner in a frame that doesn't know about the route, and with `next` owning the crossing, the split stays contained in one function.

## Cost

- No pixel should move: same arithmetic, same order.
- Reach: Rider, RiderState, Motorcycle, Tour and RideInstant (which call `rider_state_at_next_step` and `is_finished`), FrameBench, CME, and the gaze, step and rehearsal widgets.
- RiderState and Motorcycle stay nominal (your call on item 1 of open-calls covers it). The transitions move into the types, which is the style guide's state-machine rule.
