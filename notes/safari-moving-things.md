# The other things that change during safari's ride

*A recommendation for Steve on how the truck, the sun and the beacons should relate to the new `Animation` type, dated 2026-11-05. It comes from reading roc-apps at 3e94bc0. No code was changed, nothing was compiled and no gate was run.*

## The recommendation

Nothing else should move onto `Animation`: not the truck, not its brake lights, not the sun, not the beacons, and no `over_clock` or pulse helper either. What's worth having is a shared explanation and a few renames, and the explanation is already in the code. `Safari.Ride` has three fields:

```roc
Ride : { rider : Pose.RiderState, truck : Truck.TruckState, clock : F64 }
```

Those three are all that's stored between steps. Everything else that changes is worked out from them each frame. That gives three kinds of moving thing, and the walkthrough can be built on them:

| Kind | Things | How it works |
|---|---|---|
| Stepped | The rider, the truck | Stored in `Ride`, and moved once a step from where it was |
| Rider-driven | The cat, the bird | Worked out from the rider's approach, nothing stored |
| Clock-driven | The sun, the sky, the mountains' colours, the beacons, the headlights | Worked out from the clock, nothing stored |

For each of your three judgements:

- **The truck.** Make it consistent in its names and in how it's drawn, and leave its rules alone. It should get its lights the way a cat gets its pose, through the plan.
- **The sun.** You're right that it deserves its own logic. It's nearly clean, and what's left is naming and one no-op.
- **The beacons.** You're right that they shouldn't be generalized. The blink should move from `Tower` into `TowerPlan`, for a reason that has nothing to do with `Animation`.

One rule ties these together: **a plan decides how a thing looks, and drawing only paints it.** Cats and birds already work this way. If the truck and the beacons follow, `ItemDraw.Context` shrinks to `{ road, cam_focal }`, and the clock stops reaching the drawing code at all.

### Where I disagree with you

1. **"The truck isn't vastly different from the cats and birds."** That's true of how it's found and drawn, but not of its rules. Its rules are a second vehicle, and its nearest relative is the rider. So the consistency to look for in its rules is with `Throttle`, not `Cat`.
2. **"Probably too complicated to run directly on top of Animation."** The conclusion is right but the reason isn't. The truck has no timeline at all, so complexity isn't what stops it. A timeline has a known length and tells you the critter at any point along it. The truck has neither: its next step depends on its last.
3. **Time-driven against rider-driven** is one kind short. The truck is neither. It never reads the clock, and the rider's position only sets its target.

## What each thing runs on

Everything is seen through the camera, so that isn't counted here. "From scratch" means you could work it out at any frame without playing the ride up to it.

| Thing | The rider's approach | The ride's clock | Its own stored state | From scratch? | Affects the rider? |
|---|---|---|---|---|---|
| Cat | Gap and speed, `Cat.crossing_stage` | No | None | Yes | Yes: throttle and eye, through `CrossingReaction` |
| Bird | Gap only, `BirdFlight.flight_stage` | No | None | Yes | No |
| Truck's place and speed | No `Approach`. The rider's distance along the route sets `scheduled_position`, and the route's turns matter too | Never read, though it moves once a step | `route_position`, `speed` | No | No |
| Truck's brake lights | No | No | `is_braking` | No | No |
| Truck's headlights | No | Yes, `Mountains.is_sun_behind_mountains` | None | Yes | No |
| Sun's height, sky, rock and snow | No | Yes, and nothing else | None | Yes | No |
| Sun's place on screen | The rider's heading and focal length, as for anything on screen | Its height | None | Yes | No |
| Beacons | No | Yes, plus an offset per mast | None | Yes | No |
| The rider, to compare | | No | All nine fields | No | |

Only `Safari` and the specs import `Truck`. `Rider`, `Throttle`, `Gaze` and `RideFocal` never see it. Trees, cows and pigs don't change at all. A pig's gaze is the rider's own stored state.

## The truck

### Is it stateful, and does that matter?

Yes. `Truck.advance` makes the next `TruckState` from the last one, and the speed it stores is what makes it a vehicle. Here is what that changes:

- **It has to live in `Ride`.** Stepping back works for the truck only because `SafariRide.hist` keeps whole rides. Cats and birds need no history, because they follow the rider's snapshot back.
- **You can't ask about step 4000 directly.** A cat can be tested at any gap with one call. A truck has to be played there, or handed a made-up `TruckState`, as `TruckSpec` does.
- **Order matters.** `Safari.ride_step` moves the rider first, and the truck reads where the rider has just got to. `sf-order` in `SafariSpec` pins that.
- **A mistake builds up.** A wrong critter rule is wrong in the frames it touches. A wrong truck rule moves the truck for the rest of the ride.

It changes nothing from `TruckPlan` onward. Once the position is known, the truck is found and drawn much as a cat is. That's where the line falls, and it's why your instinct and mine both have some truth in them.

**Could the truck be stateless?** Yes, and it's worth saying what that would cost. `scheduled_position` is already a pure function of the rider's distance, so the truck could simply be there. But then it would stop when the rider stops for the pigs, and take its own corners at whatever pace the rider happens to be doing elsewhere. Slowing for its own turns is the reason to have the state. I'd keep it.

### Can any part of it use `Animation`?

I tried each part:

| Part | Why it doesn't fit |
|---|---|
| Position | A timeline needs its length up front, and the truck's depends on the rider |
| Speed through a turn | It looks like `over_gap` on the distance to the turn, but the speed at any distance depends on the speed it arrived with |
| Brake lights | They're on when this step's speed is below the last, so they go off when the truck has settled at its turn speed, even inside `brake_distance`. There's no length and no progress, so two tracks would carry one bit |
| Headlights | One switch at a fixed step, about 4,040 by hand from the constants. A timeline would be a lot of machinery for one `if` |

Nothing else on the truck moves. Its tyres are fixed polygons.

### What I'd change and what I'd leave

| Idea | Verdict | Why |
|---|---|---|
| A reaction through `CrossingReaction` | Leave | The truck doesn't affect the rider. `Rider.get_next_rider_state` isn't even handed it. If it ever should, `CrossingReaction` is still the wrong home, because it matches on a segment's crossing and the truck isn't one |
| `Stage` | Leave | `advance`, `advance_braking` and `advance_on_schedule` already read well. A `Stage`-like tag wouldn't line up with the brake lights, for the reason in the table above |
| `Approach` | Leave | `TruckPlan.View.lead` is the same quantity as `Approach.gap`, but "lead" suits something being chased, and nothing wants the speed beside it. Say in the walkthrough that they're the same thing |
| `Moment`, `Spot` | Leave | A `Spot` is relative to a critter's home. The truck has a route position and needs no home |
| Calling its look a pose | Leave | `Cat.Pose` picks one still. The truck's two lamps are independent, so `Lights` is the honest name. The walkthrough can say the lights are to the truck what a pose is to a cat |
| Plan, draw, state split | **Change** | The modules are there, but the lights go round the plan. See below |
| `is_braking` | **Change** | It has one reader, and `Safari.ride_frame` turns it straight into `On` or `Off`. Store `brake_lights : [On, Off]` instead. That's your enums-over-booleans rule, and it costs 17 spec lines |
| `least_braking_distance` | **Change** | This is the consistency with the rider. `Truck.least_braking_distance` and the `F64.from_bits(4517329193108106637)` in `Throttle.corner_brake` are the same number, 0.000001, doing the same job. Nothing makes them agree but a copy. Give it one home in `VehicleLimits`, beside `approach_intersection_dist`, which they already share. It doesn't change any float |
| `get_next_rider_state` | **Change** | `Rider.advance`, to match `Truck.advance`. Stepped things should share a verb. It's four lines |

### How the lights should travel

A cat's look travels through its plan: `Cat`, then `CatPlan.CatItem.pose`, then `CatDraw`. The truck's look doesn't. `brake_lights` is put into `ItemDraw.Context` by `Safari`, and `ItemDraw.draw_truck` works out the headlights itself from `Mountains`. `TruckAt` also has no `across`, so `Scenery.lane_width / 2.0` is written in both `TruckPlan.truck_on_segment` and `ItemDraw.draw_truck`.

What I'd do:

- Move `Lights` from `TruckDraw` to `Truck`, as `Cat.Pose` lives in `Cat`.
- Add `Safari.truck_lights : Safari.Ride -> Truck.Lights`, the one place that says when each lamp is on. It has to be up here, because `Mountains` and `Sky` are drawing-side modules that `Truck` mustn't import.
- `Render.Viewpoint.truck_position` becomes `truck : { route_position : F64, lights : Truck.Lights }`.
- `TruckPlan.TruckAt`'s `Ahead` gains `across` and `lights`.
- `ItemDraw.draw_truck` just passes those on, and `ItemDraw` drops `Mountains`.

This is the `draw_truck` row in the smells note, taken one step further, through the plan.

## The sun

**Does it deserve its own logic?** Yes. Three things rule out `Animation`. `Looks` picks between poses, and the sky is continuous colour. A `Spot` is a place on the road, and the sun has none. And the sky is really three curves off one number: height is a straight line, dusk is a curve and then a line, and warmth is a tent. Worked by hand from the constants, warmth starts about step 2,190, the sun's centre reaches the horizon about 3,980, the sun is fully set about 4,730, dusk is complete about 5,480, and warmth is gone about 5,780. Forcing that into stretches would hide it.

**Is it clean?** Mostly. Everything in `Sky` is a pure function of the clock, except `sun_pos`, which also needs the camera. What's left:

| Where | The smell | What I'd do |
|---|---|---|
| `Sky`, `Mountains.is_sun_behind_mountains` | The clock is called `step` here, and `step` also means a timeline's position in `Animation.at_step` | Call it `clock` |
| `Sky.sun_set_fraction` | It returns how far toward dusk the sky is, and `Mountains.draw` calls that `dusk` | `Sky.dusk_at` |
| `dusk_while_up` | Its `real_max(0.0, ...)` does nothing: a positive constant times a square can't be negative | Delete it |
| `SafariShapes.is_sun_shown` | `scale` is one focal length over another, so this looks always true. I didn't read `Lens.cam_focal` to confirm | Check, then delete it here and in `gates/SunPixels.roc` |
| `SafariRide.sky_top`, `sky_horizon`, `sun` | Three calls by two routes, for what `SafariShapes.frame` takes as one record | One `SafariRide.sky`, giving that record |

`is_sun_behind_mountains` is in the right place. It needs the skyline and the sun, and `Mountains` already imports `Sky`. Only its caller is wrong.

One question that's yours, not a cleanliness point: dusk reaches the sky, the rock and the snow, and nothing else. `Mountains.land`, the grass, the road and the trees stay at full daylight while the truck's headlights come on. If that's deliberate, leave it.

### Is the clock passed around consistently?

No. It's one number under three names, and it's read at six places across three modules, one of them in the drawing code:

| Read at | Goes to | Called there |
|---|---|---|
| `SafariRide.sky_top` | `Sky.sky_color` | `step` |
| `SafariRide.sky_horizon` | `Sky.horizon_color` | `step` |
| `Safari.ride_frame` | `Sky.sun_set_fraction`, then `Mountains.draw` | `step`, then `dusk` |
| `Safari.ride_sun` | `Sky.sun_pos` | `step` |
| `ItemDraw.draw_tower`, through `Context.clock` | `Tower.draw` | `beacon_phase` |
| `ItemDraw.draw_truck`, through `Context.clock` | `Mountains.is_sun_behind_mountains` | `step` |

After the changes here, `Safari` and `SafariRide` read the clock, it's called `clock` everywhere, and it stops at `Sky`, `Mountains` and `TowerPlan`. I wouldn't make a nominal `Clock` type. Few places would take one, and a mix-up is unlikely. Reconsider if it starts travelling further.

## The beacons

I agree with you. I read "too easy to generalize" as: the shared part would be so small that generalizing it is a trap. The code bears that out.

- **There's only one user.** A beacon is the only thing in the game that repeats on the clock. Your rule is that an abstraction earns its keep on its second user.
- **The nearest relative is a poor match.** `Alternates` also follows a wave, but it takes the sign and gives a pose. The beacon takes `(1 - cos) / 2` and gives an opacity. The shared part would be one expression, and the two compute it in different orders: `(step / over) * count * two_pi` against `((2.0 * pi) * wrapped) / period`. That opacity goes straight into pixels.
- **`over_clock` has no customer.** It would answer a `Stage`, but a beacon is never `Past`, and the sky has no use for one.
- **The door is already open.** `Animation` keeps its rules apart from its timelines, and `at_step` takes any step. If something clock-driven with real poses ever turns up, a third rule beside `over_gap` and `over_steps` is a few lines. Nothing needs doing in advance.

The beacons do need three small fixes of their own:

| Where | The smell | What I'd do |
|---|---|---|
| `Tower.beacon_offset_for` | Writes `120` twice as a literal, beside `beacon_period`, and the `37` has no name. Two homes for one fact | `Num_.mod_real(n.to_f64() * 37.0, beacon_period)`, with the 37 named. It's exact for whole numbers |
| `Tower.beacon_brightness` | Wraps twice, but `Num_.mod_real` floors, so one wrap already covers a negative phase | One wrap. The clock and the offsets are whole numbers, so this is exact too |
| `Tower` and `TowerPlan` | How a beacon blinks is a rule, and `TowerPlan` imports `Tower` for `beacon_offset_for` alone, which the smells note flagged | Move `beacon_period`, `beacon_offset_for` and `beacon_brightness` to `TowerPlan`. `TowerItem.beacon_offset` becomes `beacon_brightness`, `TowerPlan.View` and `Render.Viewpoint` gain `clock`, and `Tower.draw` takes a brightness. `TowerPlan` then drops `import Tower`, and `Context.clock` goes |

`mid_tower_beacon_step = 60` is better than its comment says: 60 times 37 is half a period past a multiple of 120, so a mid mast blinks exactly opposite its end mast. The comment should say so.

## A vocabulary for the walkthrough

No new type is needed. These are words the code nearly has, once `state` is fixed.

**`state` is the word to fix.** `Cat.state`, `BirdFlight.state` and `BirdFlight.state_on` are the functions that prove critters have no state, and they return a `Moment`. `TruckState` and `RiderState` mean something stored. A bottom-up tutorial can't say "cats are stateless" and then show `Cat.state`. I'd rename them `Cat.moment_at`, `BirdFlight.moment_at` and `BirdFlight.moment_on`, along with the `state` locals in `CatPlan` and `BirdPlan`. That's about fifteen lines of game code and six in the specs, all mechanical.

| Word | Means |
|---|---|
| step | The ride's one unit of time. Speeds are metres a step, and a timeline's length is in steps |
| clock | How many steps the ride has run |
| state | What's stored in `Ride` and carried to the next step, and nothing else |
| stepped | Stored in `Ride`, and moved from where it was: the rider, the truck |
| rider-driven | Worked out from an `Approach`: the cat, the bird |
| clock-driven | Worked out from the clock: the sky, the beacons, the headlights |
| stage, moment, pose, spot | As `Animation` defines them, for rider-driven things only |
| plan | Finds a thing in view and decides how it looks |
| draw | Paints what the plan decided |

Pausing and stepping back then explain themselves. The clock counts the ride's steps, not real time, so a pause freezes the beacons, and a step back raises the sun.

`Safari.Ride` has no doc comment, and it's the natural place for this:

```roc
## All that is kept from one step to the next: the rider and the truck, each
## moved once a step from where it was, and the clock, which counts the steps.
## Everything else that changes is worked out from these three.
```

## What I'd do first

All of this should leave `RasterFrame`'s hashes alone, and each step is a commit.

1. **The names.** `Cat.state` and its siblings, `step` to `clock`, `sun_set_fraction` to `dusk_at`, `get_next_rider_state` to `advance`. Add the `Ride` comment. There's no arithmetic in this.
2. **The small fixes.** `least_braking_distance` into `VehicleLimits`, the `real_max` in `dusk_while_up`, and the literal `120`, the double wrap and the mid-mast comment in `Tower`.
3. **Check the gate can see the truck's lights.** `run.shale` says the frame at 5700 shows the truck at dusk with its lights on, but I can't tell from reading whether any proof frame has a braking truck in view. If none does, a brake light wired to `Off` passes. Find a step where one is, and add it first, as was done for the cat.
4. **The truck's lights through its plan,** and `brake_lights` in place of `is_braking`. `ItemDraw` drops `Mountains`.
5. **The blink into `TowerPlan`.** `Context.clock` goes, so `Context` is `{ road, cam_focal }`. The `TowerSpec` offset and brightness checks move to `TowerPlanSpec`, and those expected files change.
6. **`SafariRide.sky`,** if it still looks worthwhile once the smells note's `Ride` and `RideFrame` split is settled. It could wait for that.

Steps 4 and 5 touch `Render.Viewpoint` and the plans' `View` records, which the smells note's viewpoint work also rewrites. Either order works, but do them one after the other, not at once.

## Limits of this review

- Nothing here was compiled. "Hashes unchanged" and "exact" come from reading the arithmetic, and the gate is what decides.
- The step numbers for the sun are hand arithmetic from the constants, and they're approximate.
- I read the modules you named in full, plus `ItemDraw`, `TruckDraw`, `Render`, `CatPlan`, `BirdPlan`, `RideFocal`, `Speed` and `Num_`. `Lens` and the herd modules I checked only by searching.
