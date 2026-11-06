# Parens or braces on a short `if`

*2026-11-06. Luke's guide against ours, with two examples from Rocco's real code.*

**My verdict: ours isn't clearly better.** Luke's form wins on short choices, and ours wins on long ones. I'd adopt a rule that uses both, based on length.

**The two rules:**

- **Luke:** "`roc fmt` parenthesises an `if` condition when the branch isn't a block: `if (n < 0) -n else n`. Write it that way."
- **Ours:** an `if` takes braces, always.

**A fact that frames this:** `roc fmt` gives us only two choices. I tried `if rush { 900 } else { 400 }`, and it always stacks that onto five lines. So a one-line `if` must have parentheses, and braces always cost five lines. There is no third form.

## Example 1: a short choice

From `packages/ui/Focus.roc`:

```roc
Focused(id) => if (order.contains(id)) Focused(id) else Unfocused
```

By our rule:

```roc
Focused(id) =>
	if order.contains(id) {
		Focused(id)
	} else {
		Unfocused
	}
```

Luke's is better here. It's one idea on one line, and you see both answers at a glance. Ours spends six lines on it and pushes the rest of the `match` off the screen. The parentheses are the only cost, and they're mild: they do mark where the condition ends.

## Example 2: a long choice

From `packages/ui/Scroll.roc`:

```roc
wheeled = if (under == Ok(sized.id)) dragged - input.pointer.wheel.dy * sized.line else dragged
```

By our rule:

```roc
wheeled =
	if under == Ok(sized.id) {
		dragged - input.pointer.wheel.dy * sized.line
	} else {
		dragged
	}
```

Ours is better here. In Luke's form, the `else` is buried about 75 columns in, so a quick reader takes the whole line for arithmetic. The stacked form shows the two outcomes as two outcomes.

## What I'd do

**Use the token count, as we did for stacking.** A short `if` stays on one line in Luke's form, and a long one takes braces. The threshold would come from real code, as it did for stacking, and I'd expect something like Example 1 to pass and Example 2 not to. Anything with a block, or a branch with more than one statement, takes braces as it must.

**What stays from our rule:** no parentheses around a whole body (`|x| (...)`), and no `else { if ... }`. Luke's guide doesn't ask for either, and neither is what `roc fmt` makes on its own.

**The cost:** the sweeps have already expanded these. `paren_if` rewrote 132 sites in roc-chat, and many more in safari. The recipe would need to rewrite both ways, as `stack` does, and one sweep per repo would bring the short ones back. Both are mechanical, and the line counts should fall.

**This reverses "an `if` takes braces, everywhere",** which you approved yesterday. It also means our recipes stop disagreeing with Luke's guide.

## The decision

- **A (my pick):** by length, as above.
- **B:** keep ours, braces always.
- **C:** adopt Luke's whole rule: one line whenever it fits.
