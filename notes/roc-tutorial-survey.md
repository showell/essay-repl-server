# What the official Roc tutorial can teach the Safari Ride tour

*Survey of roc-lang.org/tutorial and the langref it hands off to, against the draft and design of 2026-11-05. Safari references were checked in roc-apps at 384e35f.*

## 1. Their order

The tutorial is not older than ours in any way that matters. It moved onto the website on 2026-10-29, and the site's Windows installer names nightly-2026-11-02, a day before our pin. I wrote 13 small files using its forms (`?`, `where`, `dbg`, `.ok_or`, `1..=10`, list patterns, `Color := [...]`, block `expect` and others), and all had 0 errors under `roc check` at nightly-2026-11-03. The langref is `docs/main` and says it describes the development version, so it may run ahead of the pin.

No syntax has to change. The differences are of style, and most look like leftovers from rocemit. Safari writes `if (x) a else b` on 39 of its 193 `if` lines, where theirs has no parentheses. It wraps whole bodies, as in `|clock| (sun_start_px - (...))`. It writes `2.0` where they write `2`, and uses `F64` throughout where their default is `Dec`. The langref's rule of thumb recommends floats for graphics, so one sentence covers that.

| Their topic | Verdict | Safari code that would show it |
|---|---|---|
| Hello World, REPL, `main!` | skip | |
| Pure and effectful functions | cover | `Sky.sun_height_px`. No game module has a `!` function or a `=>` type; `main!` appears only in the 60 spec apps |
| Constants, interpolation | skip | Interpolation is only in `Grade` |
| `expect`, `roc test` | cover, as an absence | Safari has none. `CatSpec` and `Grade.reals` do that job |
| `for`, `var`, `return` | cover | `Animation.playing_at`, `Paint.flatten_screen`. These are the only two `for` loops in the game |
| `fold` | cover | `Tree.convex_hull`, `World.route_length` |
| Blocks, statements, `dbg` | skip | |
| `crash` | cover | `World.route_segment`, `ItemDraw.draw_truck` |
| `if` | skip | |
| Records, update, destructuring | cover | `Bike.with_tilt`, `Rider.rider_state_for_next_segment`, `Animation.over_steps` |
| Lists, list patterns | cover | `Truck.next_turn_on`, with `[segment, .. as later_segments]` |
| Method calling | cover | `Sky.sun_pos`; `Speed.is_lte` for the langref's well-known methods |
| Tags, exhaustiveness | cover | `Animation.Stage`, `Sky.SunPos`, `CrossingReaction.reaction_to` |
| `Try`, `?` | mention only | One real match, in `DepthSort`. No `?`. All 8 uses of `??` are `?? crash` |
| Annotations, type parameters | cover | `Animation.Timeline(pose)`, `Animation.Track(kind)` |
| `where` | skip | Safari has none |
| Structural types | cover | `Bike.Motion(others)` |
| Nominal types | cover | `Speed`, `Acceleration` (`::`); `Animation.Timeline` (`:=`) |
| Upgrading from alpha-4 | skip | |
| Dependencies, platforms | cover | `web.roc`, `SafariApp.canvas_app`, `game.roc`. `main.roc` is the spike the README says is not kept current, so "the same app on two platforms" needs that caveat |

Comparing the draft with their definitions turned up four corrections:

- The draft calls `Angle.Bearing` and `Angle.Turn` opaque, and says only `Angle` can build one. The source declares them with `:=`, so any module can. No module outside `Angle` does. A small file with the same shape, nested `::` types unwrapping each other, passes `roc check` at the pin, so `Angle` can probably become what the draft says.
- `reaction_to` names `..others` and never uses the name. The langref keeps naming for a rest that appears twice, and plain `..` passes at the pin. `Bike.Motion(others)` is the example that needs the name.
- "Won't compile" is loose for this audience, because `roc` runs past type errors by design. "Is a compile-time error" is exact.
- `Safari :: [].{ ... }` has an official name, a void module.

## 2. Worth emulating

1. Keep snippets short. Their longest block is 13 lines, with a median of 3; ours are 60 and 7. They cut with `# ...the rest of the function would go here`. `{{code Name}}` includes whole definitions only, so `crossing_timeline` would need an elided form of the include.
2. Say what the reader can stop thinking about: "if you don't see the `$`, there's no need to think about that possibility." Ours could say the same of `->`, and of a type with no `$` in sight.
3. Show the code that fails: "This code would give an error:". A `Turn` passed as a `Bearing`, with the real compiler message, would prove what the draft only asserts. The builder could generate it, so that it stays true.
4. Name the bug the feature prevents. With `_ => 0`, "we would have been silently handling the `Err(BadNumStr)` case". The draft says `Waiting` isn't 0 but could show what would go wrong if it were.
5. State a limit in one flat line: "`crash` is not for error handling." Ours can say as flatly that Safari has no `where`, no `?` and no `expect`, and why.
6. Show the same thing twice. `digits_to_num` comes as `for` and as `fold`, and `?` comes with its desugaring. `over_steps` beside `over_gap` would do this for us.

## 3. Not worth copying

- The voice ("let's get into the adventure!", "Hooray!"). The design settled on a neutral voice with no I or we.
- A section per keyword, with `crash`, `expect` and `dbg` each under a heading. That suits a catalogue, and our chapters are scenes.
- Leaving types until late ("So far we haven't seen any types"). Safari annotates everything, and the arrow is our first evidence.

## 4. A proposed chapter order

1. The ride and `Ride`: a record alias, a void module, and pure functions with no `!` in the game.
2. Things that never change: `Herd.cows`, `Trees`, `World.route`. This brings in `fold` and `crash`, and possibly compile-time evaluation. The langref says top-level values are evaluated at compile time; these sit inside `.{ }` blocks, so that needs confirming before the tour claims it. `Scenery.eq_Scheme` is best left unquoted: it is hand-written equality on a structural type, which gets `==` for free.
3. Clock-driven: `Sky`, `TowerPlan`. Tags, methods, the first nominal types. Headlights fit here too, through `Mountains.is_sun_behind_mountains(r.clock)` in `Safari`.
4. Rider-driven: `Cat`, `Animation`, `RocBird`. Payload tags, type parameters, `for` with `var` and `return`, open records.
5. Stepped: `Bike`, `Rider`, `Truck`. Record update, list patterns, `Speed` and `Acceleration` arithmetic.
6. Proving it: spec apps, frame hashes.
7. The platform: `web.roc`, and where effects finally live.

The kinds conflict with their order in four places, and ours wins in each as proposed:

- Nominal and opaque types come last in theirs and third in ours. The design wants them repeated throughout, and the sky needs `Angle`.
- `for` and `var` come early in theirs, but the one good example is in `Animation`, so they arrive in chapter 4. `fold` in chapter 2 keeps part of their order.
- Record update comes mid-tutorial in theirs and fifth in ours, because Safari's real uses are in the stepped modules.
- `expect` comes early in theirs. Ours waits for chapter 6, as the design says, and Safari uses spec apps rather than `expect`, unlike the rule in `roc-apps/CLAUDE.md`. This survey found no written reason, and a reader who knows the tutorial will ask.

Two points agree: tags before type parameters, and platforms last. `Try` has no home in any order, because Safari barely uses it, and the tour can say so. Whether to accept these four conflicts is Steve's call.

The langref was read in full for types, tag unions, static dispatch, records, errors and loops, and in part for modules, functions, pattern matching, expressions, statements, compile-time and numbers. The all-syntax example was read in part as text, and was not compiled.
