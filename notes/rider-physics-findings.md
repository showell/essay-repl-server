# Rider physics findings

*2026-11-07. From a cold review, measured on full rides of 7,071 steps. Saved for after the drawing half of the code is clean. All of these move the ride, so each is Steve's call. The ride is chaotic: any small change moves the step count (6,773 to 7,508 in trials) and most frames. Off-road steps are the safety measure, and the base ride has none.*

Steve's order: first, all the code that draws objects relative to the rider, one step at a time, gets super clean, and the book follows it. The rider's location comes from a mostly orthogonal set of rules. Cleaning those up is the first step toward improving the second half of the book, Motion.

| Finding | Where | Evidence | Lean |
|---|---|---|---|
| Lift to exit speed, and its gawking exception | `Throttle.roc:133-145`, `Gaze.roc:147-153` | Fired 16 steps and never raised speed; its exception fired 533 steps to defeat it. Off: off-road 0, 6,955 steps, max lean 16.3° | Delete both. `allowed_speed` becomes `v.min(top).max(at_rest)`. Settles how the crawl ends |
| `lean_target` aims 4 cm off center, at center | `LeanSearch.roc:20-36` | 4,106 of 7,071 steps in the epsilon branch. Aim at `Across.middle`: off-road 0, 6,935 steps, max lean 17.46° | Delete `asymptote_tuning`, `center_road_epsilon`, `lean_target`, if Steve's eye agrees; the weave may read as life |
| `lean_hold` | `Throttle.roc:19-20,151` | Fired 792 steps. Off: off-road 0, 6,906 steps, max lean 17.43° | Delete unless the look needs it |
| Six `turn_speeds` | `VehicleLimits.roc:29-52` | `0.102 * (1 - cos turn)^(-3/4)` fits within 0.85%. Close to "the road's width at full lean rate", no exact derivation. x0.9 to x1.5 stay on the road | Find the derivation, replace the table |
| Ending by teleport | `Rider.roc:23-25,66-81`, `Throttle.roc:159` | Braking to rest over the distance left never arrives; a 0.25 m jump ends the ride. Brake to 0.1 and drop `in_zone`: same 7,071 steps | Do it |
| `heading` stored twice over | `RiderState.roc:24`, `Bike.roc:50`, `Rider.roc:62` | Equals past `exit_turn`s plus `yaw`, gap at most 1.1e-14. Expects build riders where the two disagree | Store one angle; each segment gets an entry bearing |
| `Decision` round trips | `Rider.roc:21,31`, `Throttle.roc:184-187`, `Bike.roc:38-39` | Lean and speed go through a delta and back. Not measured | `Decision` holds `{ lean, speed }` |
| Shoulder brake | `Throttle.roc:72-73,93-100` | Load-bearing: off gives 16 off-road steps, 2.72 m. `-v/(2n) * e^(-n/20)` has no derivation; `n.max(1.0)` papers over `after` being 0 | Keep, then derive from what recovery needs; count from 1 |
| Tuned constants nothing rests on | Various | All off-road 0: `clear_distance` 15 and 40; `straighten_margin` 0 and 0.2; `lean_search_rounds` 4 to 20; `bend_approach` 40 and 120. Rounds 6 runs in 2.1 s against 3.4 s, and 20 halves the sign flips | Keep or derive; none is derived today |
| Gaze's three return numbers | `Gaze.roc` | Read, not measured: `look_return_rate`, `look_return_ease`, `look_return_snap` are three numbers for one return. A linear return reaches zero by itself | Drop ease and snap, if it looks right |

The lift, `lean_target` and `lean_hold` deleted together: off-road 0, 6,773 steps, max lean 18.3°.

Also noted: `turn_per_lean` is independent of speed, unlike a real bike, which is why turn speed depends on lean rate, not lean.

Earlier open calls that belong here: the gaze crawl's end, the look depth's linger, swivel speed, and whether the cat starts behind its tree.

Probe, while scratch lasts: `/tmp/claude-1000/-home-steve-showell-repos-codex-zig-ladder/ba149522-b67f-42d0-8165-02712ad26c2d/scratchpad/safari/gates/Probe.roc`.
