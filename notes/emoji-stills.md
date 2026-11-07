# How a billboard finds its drawing

You said the closed set of emoji felt wrong. You're right, and here's why, with what I'd do instead. The code is on roc-apps master.

## What happens now

A billboard holds a number:

```roc
Billboard : { codepoint : U32, height : Distance, facing : Facing }
Species : { codepoint : U32, adult_height : Distance }
```

Each kind module writes its emoji's Unicode code point (`Pig.pig = { codepoint: 128022, ... }`). When the billboard is drawn, EmojiStills looks the number up:

```roc
emoji_polys_for = |cp|
	match cp {
		129414 => duck_polys
		...
		128022 => pig_polys
		_ => crash "EmojiStills.emoji_polys_for: a critter has a still"
	}
```

So each emoji is written three times: in the kind module, in that match, and in tests. A number with no still in EmojiStills type-checks fine and crashes at draw time. That's the wrong state the reviewer flagged.

## Why the closed set feels wrong

My proposal was `Still := [Duck, Elephant, Giraffe, Zebra, Rhino, Bull, Cow, Pig]`. It removes the crash, but it does it by building the list our smells warn against: one enum naming every animal, beside the modules that each own an animal. Adding a critter would then mean editing the enum, the match and the kind module. It's "a parallel hierarchy" with a better excuse. The match already being that list didn't make it right. It meant the match was the smell too.

## What I'd do instead

Make the still itself the value a kind names, and drop the lookup.

```roc
# EmojiStills: plain data, one value per emoji, no match, no crash
EmojiStill := { codepoint : U32, polygons : List(Stills.StillPolygon) }    # only EmojiStills builds one
pig : EmojiStill
cow : EmojiStill
...

# Billboard
Species : { still : EmojiStills.EmojiStill, adult_height : Distance }
Billboard : { still : EmojiStills.EmojiStill, height : Distance, facing : Facing }

# Pig
pig = { still: EmojiStills.pig, adult_height: Distance.metres(1.1) }
```

- **Kinds name their drawing directly.** A billboard can only hold a still that exists, because only EmojiStills can build one. There's no number to get wrong and nothing to crash.
- **Adding a critter** is one new value in EmojiStills, named once by its kind module.
- **It matches what the cat and bird just became.** Their stills modules are now plain data, and each kind owns the mapping to its own drawing. EmojiStills would match them.
- **The code point stays,** as the still's name for tests and debugging (`still.codepoint()`). It's an identity, not a key.

The cost: a billboard now carries a reference to its polygon list instead of a number. In Roc that's a reference-counted pointer, not a copy, so it's cheap. Comparing two billboards with `==` compares their stills too, which is fine for tests.

The reach is EmojiStills, Billboard and the four kind modules (CowHerd, Pond, Pig and Wildlife), plus the gates' hand-built billboards. Pixels hold.

## The other choice

Leave the number and keep the crash. The crash is loud, and today it's unreachable. That's defensible under "crash if it can't happen", but it leaves the three copies of each code point.

I recommend the still as the value.
