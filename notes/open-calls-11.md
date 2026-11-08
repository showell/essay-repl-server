# Open calls 11: five from the queue

*2026-11-08. None of these is about the truck. Each has a lean; a word inline is enough.*

---

## 1. Widget colours that differ for the same job

The palette lane gathered the shared colours into `WidgetPalette`, keeping every value exactly. That surfaced three places where one job has slightly different colours:

| Job | Today | Lean |
|---|---|---|
| Plain picture background | shapes `0xf7f5f0`, stills `0xf7f5ef`, frame `0xE8E6DF` | one `picture_background_color`, `0xf7f5f0`, for shapes and stills (those two are one step apart, surely meant equal); the frame keeps its grey only if you meant it |
| The yellow "where the rider aims or looks" mark | bends `0xf0d040`, gaze `0xf6d743`, rehearsal `0xe8c84a` | one `aim_color` |
| Grass | cat `0x7fa650`, plan view `0x6f9a55` | keep both: a side view and a map view on purpose |

Widget pictures would change slightly. The game's frames would not.

## 2. Nominal types with no stated reason

`Segment` and `CowHerd` are both nominal (`:=`, fields readable outside), and neither doc says why. The style guide says opaque is the default, and that wanting to build values by hand isn't a reason for nominal.

- `Segment`'s fields (`.length`, `.trees`, `.ending`) are read all over the code.
- `CowHerd` is built by hand in World and in one test.

**Lean:** keep `Segment` nominal and write the reason down: many modules read its fields, and every value is valid. Make `CowHerd` opaque with one maker, since its readers are few.

## 3. One word for "still"

"Still" means two things: a critter's drawn pose (`Still`, `StillShapes`, the stills widget), and a page that doesn't move (the "still" widgets that show one picture, such as the truck widget). The book uses both.

**Lean:** "still" keeps the drawn-pose sense, which is in the code's types. The other sense becomes "a picture" or "a fixed picture" in prose and widget docs. It's your word, though, if you prefer another.

## 4. The pause and step keys have three homes

SafariApp, Trick or Treat and the widgets' VcrButtons each decide what the pause, forward and back keys mean.

**Lean:** leave it. They're three apps with three slightly different needs, and pulling them into one shared lib module ties them together for little gain. Revisit if a fourth app wants the same keys.

## 5. Old experiment branches on GitHub

These are leftovers from the roc-types experiments: 3 branches on showell/shale and 2 on showell/patched-zig-compiler. The bisect branches (`bisect-*`) are still in use; the bisect looks like it may be chasing an intermittent crash, and reruns are going.

**Lean:** delete the five experiment branches now, and the `bisect-*` ones once the bisect is written up. It's an outward action, so it needs your yes.
