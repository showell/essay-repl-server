# Five small calls about the kinds

Each has my recommendation. A word per item is enough.

**1. The truck kind's name.** "TruckAhead" says where the truck is, and a kind's name shouldn't carry location. The kind now holds only the truck's lights (`{ headlights, brake_lights }`). I recommend `LitTruck`, to sit beside `PosedCat` and `PosedBird`.

**2. `BigGreen` isn't big.** At 6.4 m it's shorter than `Red` (9.8 m) and `Gold` (14.7 m), and "big" holds only against `SmallGreen` (4.9 m). I recommend `Green` and `SmallGreen`. It reaches Trees, CowHerd, SceneShapes, BirdFlight and the gates.

**3. A closed set of emoji.** `Billboard.codepoint` is a bare `U32`, and EmojiStills crashes on anything but its eight values. I recommend `EmojiStills.Still := [Duck, Elephant, Giraffe, Zebra, Rhino, Bull, Cow, Pig]` in place of the number. It looks like a parallel list beside the kind modules. But EmojiStills' match already is that list, so this only names it, and the crash goes away.

**4. The truck's `pace : [Slowing, NotSlowing]`.** It's a stored flag, set wherever the new speed is below the old, so it could disagree with the speeds. The other choice is to store the previous speed and work "slowing" out from the two. I recommend keeping the flag: the step function sets it in one place, and two speeds make the state bigger for little gain.

**5. Which way the bird faces.** It always draws as drawn, which is right only because every bird starts on a left-hand tree. The choice is to put the facing in the pose, or to call it more than we need today. I recommend more than we need today, with a comment saying why it holds.
