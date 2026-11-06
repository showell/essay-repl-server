# Rocco's Roc, through Shale's recipes

*2026-11-06. [Pixelsprout/rocco-engine](https://github.com/Pixelsprout/rocco-engine) at commit 6a436bf, by Braeden Foster, UPL. Read-only: nothing here was built, run or sent anywhere. Nothing has been shown to Braeden.*

## Findings

**The recipes gave 1,644 findings over 56 files, and none of them is a bug.** Two are real naming questions, both from `families`. The real finds came from reading the code around the findings, and the best one is a dead function that no recipe could see.

The code is careful. The hand-kept copies of platform types match, every number I checked in a doc comment matches the engine, and the only `??` fallbacks in production code are three small ones.

**A first contribution could be one small PR with no change in behavior:** delete `end_game`, use `Ui.pad_all` in two places, fix two stale comments, and remove a stray binary. Each item is below. None of it has been compiled at Rocco's pin or tested, because the tests would run his code.

| | Where | What | Size |
|---|---|---|---|
| 1 | `examples/pong/main.roc:238` | `end_game` is dead, and both its branches return `m` | delete 6 lines |
| 2 | `packages/ui/Button.roc:58`, `Accordion.roc:38` | They spell out what `Ui.pad_all` does | 2 lines |
| 3 | `packages/ui/Widget.roc:27`, `packages/camera/Camera.roc:65` | Two comments say something untrue | 2 comments |
| 4 | `main` at the repo root | A tracked macOS binary, 796 KB | delete 1 file |
| 5 | `examples/entity-game/main.roc:443` | A `?? 0.0` that can't fire today and would hide a bug if it did | 1 to 2 lines |
| 6 | `packages/ui/Focus.roc`, `Dropdown.roc` | Keyboard focus is lost after picking a menu item | ask first |
| 7 | `Pose`, in two packages | One word, two meanings | ask first |
| 8 | `platform/QueryResults.roc` | The readers are uneven | ask first |
| 9 | `Ui.Node` | Named like the 3D tree, shaped like the UI tree | ask first |

## Real, and small enough for a first PR

### 1. `end_game` does nothing, and nothing calls it

```roc
end_game : Model -> Model
end_game = |m| {
	if m.score.left >= max_score or m.score.right >= max_score {
		m
	} else m
}
```

Those two lines of its definition are the only mentions of the name in the code, the guide, the README or `CONTEXT.md`. `game_state`, a few lines above it, does the real work: its `else if` on the same condition sets `EndGame`. It looks like a leftover from before that logic moved. The function sits just after an `# endregion`, so no guide page quotes it. `roc check` gives no warning for it.

### 2. `Ui.pad_all` exists, and two widgets don't use it

`Ui.pad_all(look.pad)` gives the same record as `pad: { left: look.pad, right: look.pad, top: look.pad, bottom: look.pad }`, which `Button.roc:58` and `Accordion.roc:38` both write out. Both files already import `Ui`. Pong and the bench already call it.

### 3. Two comments are out of date

- `packages/ui/Widget.roc:27` says `idle`, `hover`, `down` and `focus` "colour a button and the scrollbar thumb". The thumb uses only `down` and `idle`, as `Scroll.view`'s own doc says.
- `packages/camera/Camera.roc:65` says "The host's SCENE_NEAR and UP_EPSILON in engine/frame_render.odin". `UP_EPSILON` is in `engine/math.odin:6`. Both values match.

### 4. A binary is committed at the root

`main` is a Mach-O arm64 executable, tracked and not ignored. `.gitignore` covers `*.bin` in the build folders, but not this name. Its strings hold paths under `/Users/braedenfoster/`. I read it with `file` and `strings` and did not run it.

### 5. The one real silent fallback

`spawn_drops` in `examples/entity-game/main.roc` keeps two facts apart: `drops_per_pickup = 6` at line 428, and a list of six delays at line 437. Line 443 joins them with `List.get(drop_delays, slot) ?? 0.0`. It can't fire today. If someone sets `drops_per_pickup` to 7, the seventh drop quietly gets no delay. His own guide covers this case: "never to paper over a case that can't happen", and "`crash` on the impossible". Deriving the count from the list's length removes the second fact.

## Real, and worth asking about first

These change behavior or a public name, so they're questions rather than patches.

### 6. Keyboard focus is lost after a Dropdown selection

I traced this by hand and did not run it. In `examples/widgets`, the Tab order with the menu open is `[1, 2, 10, 11, 12, 13, 4, 5, 7]`.

1. Focus is on item 11, and the player presses Enter. `Focus.update` gives `Clicked(11)`, and `Dropdown` selects it and closes.
2. On the next step the order is `[1, 2, 4, 5, 7]`, and the focus is still `Focused(11)`, because line 42 of `Focus.roc` returns `focus`, not `in_order`.
3. No visible Panel has the focus now, and Enter does nothing.
4. Tab goes to id 1, the first in the form, not to the Dropdown's button or the widget after it.

The same happens if a mouse press closes the menu while an item has the focus. If the menu then reopens, the focus reappears on the old item.

`Focus` behaves as documented, and an `expect` asserts that a Tab from an id that left the order goes to the first id. The gap is between the two modules: nothing hands the focus back to the button. No `expect` covers it. The example's own text says "Tab moves the focus. Enter clicks.", so a keyboard user is who this reaches. The smallest fix may be in the game's `step`, setting `Focus.on(filter_id)` on `Selected`, but where it belongs is Braeden's call.

### 7. `Pose` means two things

- In `packages/linalg/Pose.roc`, a Pose is a position and a rotation.
- In `platform/Pose.roc` and `Vocabulary.Pose` (line 223), a Pose is two Clips, their times and a fade.

`Vocabulary.roc` uses both in its docs: line 223 for Clips, and lines 230, 360, 365 and 389 for a position and a rotation. `CONTEXT.md` defines **Pose** twice, at lines 203 and 691. In the entity game, `draw` takes a parameter `pose` of the linalg kind and fills a `Draw` whose `pose` field is the other kind.

Braeden knows about the module clash. Chapter 10 says "If your game needs both, import one of them under another name". The cost that remains is the word itself, in a project whose glossary exists to fix words. It's a public rename, so it's only worth raising as a question.

### 8. `QueryResults` reads less than its docs say

`Vocabulary.roc:251` says "Read it with the functions in `QueryResults`". There's no function for `contacts`, and every example reads `results.contacts` directly, which is fine, but the sentence doesn't cover it. Also, `Query.overlap` has a slot-0 form beside `overlap_slot`, and `QueryResults.ray` has one beside `ray_slot`, but `QueryResults.overlaps` always takes the slot. So the entity game writes `QueryResults.overlaps(results, p.id, 0)` for a query it built without naming a slot.

### 9. `Ui.Node` is named for the other tree

`Ui.Node` has the shape of `Vocabulary.Element`. `Vocabulary.Node` is the 3D tree. The glossary is deliberate about this: `CONTEXT.md:333` lists "Node (the 3D tree), Ui.Node (the package tree)" under `Element`'s `_Avoid_`, and a package can't name `Element`. The name is still the same word for the opposite tree. This is the weakest of the four, because he has already decided it on purpose.

## Where the code departs from his own guide

Rocco has `docs/roc-style.md`, a copy of Luke Boswell's guide, and `AGENTS.md` adds two rules. **This changes the sorting you asked for: stacking is not only our house style.** His guide says "Stack anything with three or more parts". The code mostly doesn't, so the guide and the code disagree. That's his to settle, and these aren't faults to present. They're here so you know which findings rest on his text and which on ours.

| His rule | Recipe | Count | Note |
|---|---|---|---|
| "Stack anything with three or more parts", and about 100 columns | `stack` | 1,242 to stack, 143 long, 18 wide strings | Most of the `stack` total |
| "A function returning `Bool` is a question" | `name_hunt` `question` | 9 in the platform | `Key.held`, `Key.pressed`, `MouseButton.released`. `packages/ui/Seam.roc` has the `is_key_held` form, so the repo holds both. `Key.pressed(input, T)` does read well |
| "A function with three or more arguments takes a record" | `stack` | 91, about 20 in packages and platform | `Query.ray` has two `Vec3`s in a row, and `Collider.capsule` two `F32`s. The `loaded` and `step` hits in the apps, and the four in `platform/main.roc`, aren't his to change: see below |
| "Put a `##` doc comment directly before every top-level `expect`" | none, counted by hand | 76 of 320 sampled have it | `packages/ui` and `widgets` follow it. Camera, linalg and pong use `#`, so `roc test` prints no name. Changing 36 `#` to `##` would be a cheap second PR |
| Call a method on its receiver (`AGENTS.md`) | none, counted by grep | about 178 `List.x(...)` calls | |
| One `List.join`, no chained `.concat` (`AGENTS.md`) | none, counted by grep | 7 files, one each | Pong and tutorial chapters 5 to 10 |

The 320 is the eight trees I counted: the four packages, the platform, pong, widgets and the entity game.

## House style only

These are our habits, and he has no such rule or the opposite one. None of them should reach him as a fault.

- **`parens`, 58 findings.** Our guide rejects `if (x) a else b` and braceless branches. His says the opposite: "`roc fmt` parenthesises an `if` condition when the branch isn't a block: `if (n < 0) -n else n`. Write it that way." 37 of the 57 lines have the parentheses, and most of them are in `packages/ui`. The other 20 have a braceless branch and no parentheses.
- **`nest_depth`, 47.** Nearly all are tests, or formulas like `V.add(model.pos, V.scale(V.normalize(dir), speed * dt))`, which read fine as math.
- **`boundaries` `single`, 33.** Small named steps in tutorial apps, repeated across chapter copies. In a tutorial, a name is the point.
- **`abbreviation`, 22.** All `pos` but one `accel`. `pos` is a field of `Draw`, and the glossary fixes it.
- **Other participles and container words, 17.** `touched`, `caught`, `collected` and `placed` are mostly test helpers. `items`, `Node` and `Element` are ordinary here.

## Checked and found sound

- `Ui`'s types match `Vocabulary`'s, field by field, as the comment at the top of `Ui.roc` demands. So do `Mesh.Manifest` and `Camera.View`.
- `Seam`'s nine key codes match `platform/Key.roc`.
- `Quat.mul`, `rotate`, `between` and `Pose.compose` are correct by hand, and `Camera.project` follows the host's `up` fallback rule exactly.
- `Launch.default`'s numbers match its doc. `SHADOW_DISTANCE` is 150, `MAX_LIGHTS` is 8, and overlaps do come in id order.
- `view_for_host` doesn't free the Model: `seam_view` increfs first, with a comment saying why (`engine/seam.odin:235`).
- A thumb taller than its track gives a negative pad, but `ui_px` clamps it (`engine/ui.odin:452`), so I dropped that lead.
- **`Mesh.resolve` giving 0 is a decision, not a silent fallback.** Chapter 2 says why: "a misspelt name shows up on the screen". Our doctrine would ask for a `Try`, and that's a difference of taste with a stated reason.
- A scan of public names in `packages/` and `platform/` found none unused, though `Vec3.lerp` is reached only by its test. The scan is by name, so it's a good sign and not a proof.

## The counts

Over `packages/` (19 files), `platform/` (20) and `examples/` (17). `boundaries` read the whole tree of 71 files, as its header asks, and the count is of findings in those three folders.

| Recipe | Findings | Real faults | Mostly |
|---|---|---|---|
| `name_hunt` | 45 | 0 | `loaded` 17, `question` 10, other participles 11 |
| `errors` | 7 | 0 | `None` in `[Words, None]` |
| `nest_depth` | 47 | 0 | House style |
| `parens` | 58 | 0 | House style, against his guide |
| `boundaries` | 37 | 0 | `single` 33, `fixed` 4 |
| `stack` | 1,411 | 0 | His guide's rule, not followed |
| `families` | 14 by folder, 27 whole tree | 2 naming questions | The rest are forced copies |
| `plain_names` | 25 | 0 | `pos` 21, generated files |

Run by folder, `families` missed its two best findings, because the twins are in different folders. Only the whole-tree run saw them.

`errors` found no `set_fallback`, and that zero says little: the repo has no `.set(` at all. It found three placeholders, all in `scripts/`, which is outside this review.

## What the false findings say about our recipes

Nothing in Shale was edited.

1. **No recipe finds a function with no callers.** `boundaries` counts calls and reports exactly one caller, so zero falls through. That's why the best find of the day came from reading. A `dead` check on non-exposed top-level names looks like a few lines there, and the two-branches-the-same shape of `end_game` could go with it.
2. **`name_hunt` and `stack` should exempt what the platform dictates.** 17 of the 26 `bare_participle` hits in the examples are `loaded`, named in the app header, and `stack` tells an app to "take a record" 17 times for `loaded`'s signature and 18 times for `step`'s. `families` already has this exemption, with the reason in its header: "every app declares what its platform asks for". The other two could share it.
3. **`twin_name` should compare shapes.** All 13 platform hits are a namespace module, `Collider := [].{`, beside `Vocabulary.Collider`. A module like that builds the type and doesn't declare a second one. Most of the rest are copies forced because a package can't import the platform. A twin with the same shape is a copy, and a twin with a different shape is a collision. That rule would have kept `Pose` and `Node` and dropped nearly everything else, which turns the noisiest naming check into the most useful one.
4. **`fixed` shouldn't judge an exposed function by its callers in the tree.** `Pose.still`'s `0, 0.0` is a public API whose only in-repo callers are benches. `Seam.is_button_pressed` with `Left` is a real API that happens to be used for one button so far.
5. **`optional_tag` reads `[Words, None]` as an optional.** No tag there carries a value, so it's a two-way mode, and `None` is Clay's word. The check could require a sibling with a payload. Run by folder, it also says "no type here says what it is" about a type that's in the next folder.
6. **`module_doc` flags generated files.** `Font` and `TextCorpus` start with a `Generated by` comment. `Seam` has a good `#` comment and isn't exposed, so it has no public doc to write.
7. **`errors` `placeholder` only reads strings.** A numeric `?? 0.0` like item 5 passes it.
8. **`stack`'s message cites `roc-style.md`,** which would mislead on a tree with a different `roc-style.md`. Rocco's happens to agree on that rule.
9. **`parens` contradicts Luke's public guide.** It's right for our tree, by our decision in commit a3b911d. If we recommend these recipes to anyone else, it needs saying, or it should be opt-in.

## How it ran

- **All 71 files parsed.** roc-ast refused nothing, so the 10-11 pin made no difference to parsing.
- All recipes ran read-only, with no `write=1`, under `nice -n 15`, one at a time.
- Roc 10-11 isn't installed, so `roc check` ran with `~/roc-nightly-2026-10-09-258ab27/roc`. All four packages passed. Ten example apps, sampled across the tree, gave 0 errors and only the two pin-mismatch warnings. That's a weaker claim than a check at his pin.
- I read `scripts/` and `bench/` only where a recipe pointed at them.
- The scratch copy is `/tmp/claude-1000/-home-steve-showell-repos-codex-zig-ladder/ba149522-b67f-42d0-8165-02712ad26c2d/scratchpad/rocco-audit/`, with each recipe's output in `out/`.

## Before a PR

`AGENTS.md` asks for conventional commits, simple language, and no em-dashes. It also says "Do not add a `Co-Authored-By:` trailer", which conflicts with how we commit, and "Avoid adding the author to commits, such as *Generated by Claude Code*". Our rule for outbound work is to say it's Claude. That can go in the PR text and stay out of the commit, but it's your decision. There's no CONTRIBUTING file. Tasks live in `.dex/tasks.jsonl`.
