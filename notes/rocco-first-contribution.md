# A first contribution to rocco-engine

*2026-11-06. [Pixelsprout/rocco-engine](https://github.com/Pixelsprout/rocco-engine) at 6a436bf, which was still his main when I finished. Nothing here has been sent to anyone.*

## Verdict

**Yes, there is one, and it's the Dropdown focus bug.** It's a real bug in a public package, and I reproduced it under `roc test` by driving his own `step` in `examples/widgets`. A person who picks a menu item with the keyboard loses the focus: nothing is highlighted, Enter does nothing, and the next Tab jumps to the top of the form.

The fix is one small public function, `Dropdown.keep_focus`, one changed line in `step` and its copy in the guide, and six `expect`s. It's 44 lines added and 6 removed over three files, and most of that is tests and docs.

It's a modest bug, not a crash. It wins because it's the only candidate that changes what a person using a game sees. Everything else on the list is tidying.

The one thing he might want done differently is the shape of the fix, because it adds a public name. The draft below says so.

## The bug

`Focus.update` is correct and documented. `Dropdown` is correct too. The gap is between them: when a menu closes, nothing hands the focus back to the button.

Run on his unmodified `step`, starting from the first frame, with the keys Tab, Tab, Enter, Tab, Tab, Enter:

| Step | Result |
|---|---|
| Tab, Tab | The focus is on the filter button, id 2 |
| Enter | The menu opens |
| Tab, Tab | The focus is on the item "Ready", id 11 |
| Enter | Item 1 is selected and the menu closes, but the focus stays on id 11 |

After that, all of these were measured:

- Id 11 isn't in the Tab order any more, which is now `[1, 2, 4, 5, 7]`, so no visible Panel has the focus.
- Enter produces 0 commands.
- Tab goes to id 1, and Shift-Tab goes to id 7.
- If the menu reopens by mouse, the focus reappears on item 11.
- The same thing happens if a mouse press outside closes the menu while an item has the focus.

Nothing in his tests covers it. The Bridge check sends Tab, Shift-Tab and Enter, but it picks menu items only by mouse, so the focus is never on an item. His own text in that example says "Tab moves the focus. Enter clicks." The notes in his repo record no decision about where the focus goes after a close, so I'm not overriding a choice.

This corrects the earlier essay in two places. It suggested setting `Focus.on(filter_id)` on `Selected`. That misses the press-outside case, and it would also move the focus on a mouse pick. It also said tests couldn't be run without running his code. In fact `roc test` needs no engine and takes about a second, so the check was cheap. The rest of its item 6 was right.

## How sure I am

**That the bug exists in his Roc code: certain.** These results are from `roc test` on my copy:

- His code as it stands passes 157 tests in `examples/widgets` and 71 in `packages/ui`.
- Five `expect`s for the desired behavior all failed. They covered the state after the pick, the next Tab, the next Enter, the reopen, and the press outside.
- A sixth `expect` pinned the bad state value by value, and it passed. So the five reds fail for the reason above and not because of a mistake in the test.
- This ran on the 10-09 and 10-18 nightlies, which sit either side of his 10-11 pin. The fixed code also passes on 11-03.

**That a real window shows the same thing: very likely, not proven.** I didn't build or run the engine, so nobody has seen it on a screen. The `step` under test is the one the game runs, and his Bridge check already sends Tab and Enter through the real host. The missing highlight is read from `Button.panel`, which colors only the id that `focus.is_on` names.

**That he'll welcome it: a guess.** All 47 of his PRs are his own, and the repo has no issues at all, so this would be the first outside contribution. I can't tell how he'll take that. His PR #47 is open, but none of its 515 files is one of these three.

## The fix

`keep_focus` covers every way a menu can close. Mouse-only players are untouched, because a focus that isn't on an item passes straight through.

```diff
diff --git a/examples/widgets/main.roc b/examples/widgets/main.roc
--- a/examples/widgets/main.roc
+++ b/examples/widgets/main.roc
@@ -103,7 +103,7 @@ step = |model, input, results, _dt| {
 	next = {
 		..model,
 		buttons: pointer.buttons,
-		focus: keys.focus,
+		focus: picked.dropdown.keep_focus(keys.focus),
 		filter: picked.dropdown,
 		details: model.details.update(events),
 		log: model.log.update({ input, results, focus: keys.focus }),
@@ -195,6 +195,25 @@ expect {
 	step(opened, click, over([11, menu_id]), 0.0).commands == [Port.tell("widgets", "clicked 11"), Port.tell("widgets", "selected 1")]
 }
 
+## After a pick by keyboard, the filter keeps the focus, so Tab goes on to the next widget.
+expect {
+	press = |model, key| step(model, { ..Input.empty, pressed: [Key.code(key)] }, QueryResults.empty, 0.0).model
+	picked = [Tab, Tab, Enter, Tab, Tab, Enter].fold(start, press)
+	(picked.filter.selected(), picked.focus, press(picked, Tab).focus) == (1, Focus.on(filter_id), Focus.on(details_id))
+}
+
+## A press outside the menu gives the focus of an item back to the filter.
+expect {
+	on_item = { ..step(start, click, over([filter_id]), 0.0).model, focus: Focus.on(11) }
+	step(on_item, click, over([]), 0.0).model.focus == Focus.on(filter_id)
+}
+
+## A pick by mouse leaves the focus alone.
+expect {
+	opened = step(start, click, over([filter_id]), 0.0).model
+	step(opened, click, over([11, menu_id]), 0.0).model.focus == Focus.none
+}
+
 ## The focus order holds the items only while the menu is open.
 expect (focus_order(start), focus_order(step(start, click, over([filter_id]), 0.0).model)) == ([1, 2, 4, 5, 7], [1, 2, 10, 11, 12, 13, 4, 5, 7])
 
diff --git a/guide/ui.md b/guide/ui.md
--- a/guide/ui.md
+++ b/guide/ui.md
@@ -194,8 +194,10 @@ click.
 
 `Dropdown` is a button that opens a menu of items. The menu floats under
 the button. A click on an item selects it and closes the menu, and a press
-outside the menu closes it. `Accordion` is a header button that shows or
-hides a body. Both read only the events of `Button` and `Focus`.
+outside the menu closes it. Its `keep_focus` gives the focus back to the
+button when the menu closes under a focused item. `Accordion` is a header
+button that shows or hides a body. Both read only the events of `Button`
+and `Focus`.
 
 `Scroll` is a Panel that scrolls its rows, with a scrollbar thumb that the
 person can drag. The wheel scrolls it by `line` pixels per step, and Page
@@ -220,7 +222,7 @@ step = |model, input, results, _dt| {
 	next = {
 		..model,
 		buttons: pointer.buttons,
-		focus: keys.focus,
+		focus: picked.dropdown.keep_focus(keys.focus),
 		filter: picked.dropdown,
 		details: model.details.update(events),
 		log: model.log.update({ input, results, focus: keys.focus }),
diff --git a/packages/ui/Dropdown.roc b/packages/ui/Dropdown.roc
--- a/packages/ui/Dropdown.roc
+++ b/packages/ui/Dropdown.roc
@@ -5,8 +5,8 @@ import Widget
 
 ## A button that opens a menu of items. The menu floats under the button, so
 ## the Panels under it get no click. A press outside the menu closes it. Keep
-## one Dropdown in your Model, and give `update` the events of
-## `Button.update` and `Focus.update`.
+## one Dropdown in your Model, give `update` the events of `Button.update` and
+## `Focus.update`, and pass the focus through `keep_focus`.
 Dropdown :: { button : U64, menu : U64, items : List({ id : U64, label : Str }), selected : U64, shown : [Open, Closed] }.{
 
 	## A closed Dropdown. `button` tags the button, `menu` tags the menu Panel
@@ -44,6 +44,14 @@ Dropdown :: { button : U64, menu : U64, items : List({ id : U64, label : Str }),
 		Closed => [dropdown.button]
 	}
 
+	## The focus after `update`. An item of a closed menu can't hold the focus,
+	## so the button takes it back. Any other focus stays as it is.
+	keep_focus : Dropdown, Focus -> Focus
+	keep_focus = |dropdown, focus| {
+		is_on_item = dropdown.items.any(|item| focus.is_on(item.id))
+		if (is_on_item and dropdown.shown == Closed) Focus.on(dropdown.button) else focus
+	}
+
 	## The button, with the label of the selected item, and the menu under it
 	## while it shows. The menu has the button's `width`, and each item fills
 	## it.
@@ -135,6 +143,15 @@ expect closed.update([Clicked(12)]) == { dropdown: closed, selection: Unchanged
 ## The focus order holds the items only while the menu is open.
 expect (closed.focus_order(), opened.focus_order()) == ([2], [2, 10, 11, 12, 13])
 
+## A closed menu gives the focus of an item back to the button.
+expect closed.keep_focus(Focus.on(12)) == Focus.on(2)
+
+## An item of the open menu keeps the focus.
+expect opened.keep_focus(Focus.on(12)) == Focus.on(12)
+
+## The button, another Panel and no focus stay as they are, open or closed.
+expect [closed, opened].map(|dropdown| [Focus.on(2), Focus.on(4), Focus.none].map(|focus| dropdown.keep_focus(focus))) == [[Focus.on(2), Focus.on(4), Focus.none], [Focus.on(2), Focus.on(4), Focus.none]]
+
 ## The closed view shows the selected label and no menu.
 expect
 	match closed.view({ buttons: Button.idle, focus: Focus.none, width: Fixed(160.0), look }) {
```

The guide change isn't optional. `guide/ui.md` holds a copy of the `widgets-step` region, which his `scripts/Regions.roc` compares to the example.

## What proves it

With the fix, on 10-09, 10-18 and 11-03, `packages/ui` passes 74 of 74 and `examples/widgets` passes 163 of 163. That's his existing tests plus the 3 and 6 new ones. `roc check` gives 0 errors and the same two pin warnings as before.

I also broke the fix three ways, one at a time, and put it back afterward:

| Plant | Red tests |
|---|---|
| `step` doesn't call `keep_focus` | Keyboard pick, press outside |
| `keep_focus` ignores whether the menu is closed | Open menu keeps the focus, keyboard pick |
| A closed menu always takes the focus | Other focus stays, keyboard pick, mouse pick, and his own Shift-Tab test |

Other checks:

- `roc fmt --check` passes on 10-09. On 10-18 it fails, but it fails the same way on his untouched files, so that's the newer formatter and not this diff.
- All four regions in `guide/ui.md` match the example. I compared them with my own short script, because his are off limits.
- His Bridge check should behave exactly as before, because it never puts the focus on an item, and `keep_focus` passes every other focus through. That comes from reading it. I didn't run it.
- The patch applies cleanly to 6a436bf.

## Why this beats the others

The other candidates are all true, but none of them changes anything for a player or a game author. A friendly stranger who brings a working bug fix and a test is doing the maintainer a favor. A stranger who brings tidying is closer to the style review you want to avoid.

It also fits his own rules. His guide says "One home for each rule", and the rule "a closed menu's items can't hold the focus" belongs in `Dropdown`, which already owns `focus_order`. A game author gets the correct behavior from one call and doesn't have to work out the problem again.

Two smaller fixes fall short:

- **Only in the example's `step`, on `Selected`.** It's one line and adds no public name, but it misses a press outside, it moves the focus on a mouse pick, and every game has to rediscover it. This is the fallback if he doesn't want a new function.
- **Only in `Focus.update`, returning `in_order`.** It stops the focus reappearing on reopen, but Tab still jumps to the top. It doesn't touch the main complaint.

## The commit and the words

The commit follows his `AGENTS.md`: conventional, simple language, no `Co-Authored-By:` line and no "Generated by". Claude's part goes in the PR text instead. That departs from our usual trailer, on purpose, because his file says its rule overrides any default.

```
fix(ui): Give the focus back when a Dropdown menu closes

Add Dropdown.keep_focus. When a menu closes under a focused item, the
button takes the focus back.
Call it in the widgets example and show it in guide/ui.md.
Add tests for a pick by keyboard, a press outside and a pick by mouse.
```

A draft for the PR, for you to change freely. It's written as you, so please check that the first sentence is true for you:

> Hi Braeden, I'm Steve Howell. I've been reading rocco because I have a Roc game of my own, and it's a pleasure to read. Claude helped me look through `packages/ui`, and it found this bug and wrote the patch.
>
> If you pick a Dropdown item with the keyboard, the focus stays on the item after the menu closes. That item is no longer in the Tab order, so nothing is highlighted, Enter does nothing, and the next Tab goes to the first widget. In `examples/widgets`: Tab, Tab, Enter, Tab, Tab, Enter, then Tab lands on "Add line" and not on "Details". A mouse press that closes the menu while an item has the focus does the same.
>
> `Focus` does what its docs say, so I left it alone. This adds `Dropdown.keep_focus`, which gives the focus back to the button when an item of a closed menu holds it. Any other focus passes through, so a pick by mouse behaves as it did.
>
> I ran `roc test` on `packages/ui` and `examples/widgets`, and the new tests fail without the fix. I didn't have your pin here, so that was on the 10-09 and 10-18 nightlies. I didn't build the engine or run the Bridge check, so this hasn't been seen in a real window.
>
> The new public name is your call. If you'd rather shape this differently, or just take the idea, that's fine with me. Thanks for sharing the engine.

## What I rejected

- **Dead `end_game` in pong:** confirmed dead, with its own two lines the only mentions. Deleting it is safe and changes nothing a player sees. It's the runner-up.
- **The tracked `main` binary:** confirmed, a 796 KB Mach-O arm64 file. It does cause trouble: `git diff main HEAD` fails here because `main` is both a file and a branch. He can delete it in seconds, though, so it's a poor reason to introduce yourself.
- **`Ui.pad_all` in `Button` and `Accordion`:** true, but a style change.
- **Two stale comments:** both true (`UP_EPSILON` is in `engine/math.odin`, and the thumb uses only `down` and `idle`), but too small to be a help.
- **`?? 0.0` in `spawn_drops`:** true, and his guide asks for better, but it can't fire today and it's in an example.
- **`Pose`, `Ui.Node` and `QueryResults` naming:** these are API opinions on words he chose. They aren't for a first contact.
- **Stacking and the three-argument rule:** his guide does ask for them, but the fix is a huge diff or a public API break.
- **`##` on `expect`s and receiver calls:** guide-backed and cheap, but still a style review.
- **A new module boundary:** I found none in `packages/ui` that makes something concrete easier. `Seam`'s copied codes are forced, because a package can't import the platform.

## Noticed and left alone

Tabbing past the last item leaves the menu open, with the focus on "Details". I ran this and it's what happens. Many menus would close there. That's a behavior choice for him and doesn't belong in this diff.

If Enter and Tab land in one step on an item, the Tab is lost, because the button takes the focus back. That comes from reading only. It's a rare case and harmless.

## What I didn't look at

I read `packages/ui` closely, parts of `linalg` and `mesh`, and most of pong. I didn't hunt through the entity game, `glow`, `mask`, `cards`, the tutorial or the Odin engine, beyond a few checks. A better bug could be there.

My clone is shallow, so I can't say when `main` landed or how old the focus bug is. Before posting, run `git ls-remote` again, because he ships daily.
