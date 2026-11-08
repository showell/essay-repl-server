# The brake overshoots its target

**Answered (Steve, 2026-11-08):** "for braking I agree with your conservatism." So (b): keep the ride; `braking_to` fails loudly on the impossible case; its doc says the steady brake may land a little under the target.

One call for you, on the ride's physics.

## What we found

`VehicleLimits.braking_to` works out the steady deceleration that brings a speed to a target over the distance left. When very little distance is left, one step of that deceleration takes the speed **below** the target:

- **At the very first bend:** the rider is going 0.239 m a step, the bend's speed is 0.222, and 0.115 m is left. One steady brake lands on 0.205, under the bend's speed. The truck does the same, but its own `target_speed.max(...)` hides it.
- **The worst case is a crash.** In a made-up state (299.9 m along the last segment at 0.5 m a step), the brake would take the speed below zero, and `Speed` now refuses a negative. The real ride never gets there: its approach to the route's end settles gently. Only hand-made test states hit it.

## The choice

- **(a) Fix the physics: the brake never goes below its target in a step.** It's the honest rule, but **the ride moves**. Every held frame from the first cat on changes, the finish moves from step 6746 to 6727, and it needs an eye test and a re-hold. It also needs a rule for how the stop at the route's end ends: with the clamp, the rider halts 0.1 m short and never "finishes", so the finish condition has to change too.
- **(b) Keep the ride exactly as it is, and make the impossible case fail loudly.** `braking_to` crashes with a reason ("a brake that would take the speed below zero; the ride never brakes this hard") instead of letting `Speed` crash somewhere less clear. The first-bend undershoot stays as it is, and its doc says so plainly: the brake is steady and may land a little under the target.

## My lean

**(b)**, because you've asked before that physics changes preserve the ride's behaviour unless there's a reason to move it, and nobody sees a 0.017 m-a-step undershoot. (a) is the cleaner rule if you'd rather the physics be exact; it's a contained lane with an eye test.
