# Dog Park in Roc: what is easy to change, and what is not yet

*CC's branch `claude/great-wright-i7aste` of dog-park, read 2026-10-18 (its
newest commit, e7ac200, "The walk in Roc"). CC is working on performance
now. Nothing here is merged into `main`.*

## What has moved to Roc

In about four hours CC has moved Dog Park's description, and much of its
behaviour, into Roc:

| file | lines | what it is |
|---|---|---|
| `roc/World.roc` | 49 | the world's numbers: tile size, world and park size, the critters' sizes, breeds |
| `roc/world.roc` | 204 | the park laid out, checked, and printed for Zig (`world.zon`) and the page (`world.js`) |
| `roc/Rules.roc` | 106 | what each critter does about each moving critter it sees; paces; chickens; poop |
| `roc/Wish.roc` | 251 | **behaviour**: a critter's wish from the critters near it, with 22 `expect`s |
| `roc/Walk.roc` | 939 | **behaviour**: one pixel-tick's walk, every critter's move after the leashed dog's |

The first three are configuration, run at build time to print files the
Zig reads. The last two are physics. They're compiled to `.a` libraries
for wasm, the Linux server and the kernel, linked into the Zig, and called
every tick. Roc is no longer just configuration.

## Three excerpts

### The rules, as data

This is the part that reads best. `Rules.roc` gives each critter a record
of how it answers each kind of critter it sees, written in the game's own
terms:

```roc
Rule : [
    Ignore,
    Keep(I64),                            ## keep this far away
    Herd({ inner : I64, outer : I64 }),   ## stay in a band around the nearest kin
    Close(I64),                           ## close in to touching, from within this
]

Sees : { gathers : Gathers, kin : Rule, dog : Rule, cow : Rule, chicken : Rule, pace : Share }

dog : Sees
dog = {
    gathers: Each,
    kin: Herd({ inner: 42, outer: 70 }),
    dog: Keep(wary),
    cow: Keep(63),
    chicken: Ignore,
    pace: { num: 1, den: 1 },
}

cow : Sees
cow = {
    gathers: Nearest,
    kin: Keep(wary),
    dog: Keep(wary),
    cow: Close(245),
    chicken: Ignore,
    pace: { num: 1, den: 2 },
}
```

You could read that aloud to someone who has never seen code. A dog
herds with its own breed in a band 42 to 70 px from its nearest, keeps
`wary` from other dogs and 63 px from cows, ignores chickens, and walks at
the leashed dog's pace. A cow listens only to its nearest moving critter,
and walks at half pace.

### The world, as a function of a tile

```roc
tile_spots : I64, I64 -> List(Spot)
tile_spots = |col, row| {
    far = tile_px - corner_in
    mid = tile_px // 2
    dogs = [
        { kind: Dog, x: corner_in, y: corner_in },
        { kind: Dog, x: far, y: corner_in },
        { kind: Dog, x: corner_in, y: far },
        { kind: Dog, x: far, y: far },
    ]
    if (col + row) % 2 == 0 {
        dogs.concat([{ kind: Cow, x: mid, y: mid }])
    } else {
        dogs.concat([
            { kind: Chicken, x: mid - chicken_off, y: mid },
            { kind: Chicken, x: mid + chicken_off, y: mid },
        ])
    }
}

expect no_overlap(park)
```

Each tile holds a dog of each breed in its corners, plus either a cow (on
a white tile) or two chickens (on a blue one). The `expect` under it
checks that no two critters overlap where they start. That rule used to
be the physics' problem at load time; now a bad layout fails at build
time.

### The behaviour, with its tests beside it

`Wish.roc` turns the rules into a step. Its tests are written as the
story they check:

```roc
## A dog of another breed 100 px east: room `wary` (158 px) from it, so 58 px west.
expect Wish.wish(dog_me, [nb(0, Bool.False, 3, 100 * 256, 0)]) == { anchor: -1, x: -58 * 256, y: 0 }

## A cow heeds only its nearest: a cow 100 px east (within 245) draws it
## toward touching (42 px apart), though a dog 150 px west would scare it.
expect Wish.wish(cow_me, [nb(1, Bool.False, 2, 100 * 256, 0), nb(0, Bool.False, 7, -150 * 256, 0)]) == { anchor: -1, x: 58 * 256, y: 0 }
```

## How easy are the natural variations?

### Tuning: trivial, and guarded

Changing how wary a dog is, a cow's pull, a critter's size, how often the
herd poops, or how far chickens see is **one number in `Rules.roc` or
`World.roc`, then `zig build roc`**. The `expect`s guard what has to
stay true. Poop slots must be a power of two (the physics counts them in
32 bits). The park must sit centred in the world. Nobody may start
overlapping. This is where Roc already pays off: the knobs are named, in
one place, in the game's own words.

### A new critter: hard; the critter set is closed in many places

Say you want sheep. Here's what has to change, today:

- **`world.roc`:** `Kind : [Dog, Cow, Chicken]` gains `Sheep`; `half`
  gains a size; `tile_spots` places them; the `zon` and `js` printers gain
  a list of sheep.
- **`Rules.roc`:** `Sees` gains a `sheep : Rule` field. Every existing
  critter's record gains a line saying what it does about sheep, and
  sheep get a `Sees` of their own. **N kinds make an N×N table, kept as
  fields.** A new kind touches every row.
- **`Wish.roc`:** a kind is a number here, not the tag: `kind : U8`, "0 a
  dog, 1 a cow, 2 a chicken". `rule_for` decides by `n.kind == 0 ... == 1
  ... else`, and `sees` by `if (me.kind == 1) Rules.cow else Rules.dog`.
  A sheep, kind 3, would silently be taken for a chicken by `rule_for`,
  and for a dog by `sees`.
- **`Walk.roc`:** "dogs and cows only" walk, and kinship is encoded in
  numbers: a dog's kin is its breed, a cow's "the breeds' count", a
  chicken's 255.
- **The Zig and the page:**
  - `physics.zig`'s `Kind`;
  - `world.zig`'s `World` struct, with its `dogs`, `cows` and `chickens` lists;
  - the wire format;
  - the page's drawing.

So the readable rules sit inside a critter set that is closed, and closed
twice. In `Rules.roc` it's closed by record fields, where at least the
compiler would make you fill in every new one. In `Wish.roc` and
`Walk.roc` it's closed by numeric codes, where it wouldn't; that's where
mistakes would hide.

**What would make a new critter one change, guided by the compiler:**

1. **Keep `Kind` a tag inside Roc.** Turn the Zig's number into the tag
   once, at the boundary where the physics hands over the critters, and
   use `match` everywhere after. Roc's exhaustive `match` then refuses to
   compile any rule, size or pace that forgot the sheep.
2. **Make the rules a function of a pair:**

   ```roc
   rule : Kind, Kind -> Rule
   rule = |who, sees| match (who, sees) {
       (Dog, Dog) => Keep(wary)        ## kin handled apart
       (Dog, Cow) => Keep(63)
       (Cow, Cow) => Close(245)
       (Sheep, Dog) => Keep(200)
       ...
       _ => Ignore
   }
   ```

   This is the N×N table written once. It would be better without the
   `_` fallback, so that the compiler lists every pair a new kind leaves
   unsaid; a deliberate `Ignore` would then be written out.
3. **Make the Zig's `World` hold critters as one list of `{kind, x, y}`**,
   not one list per kind.

With those, a sheep is a tag, a size, a place in the layout and a row and
column of the rule table. The compiler points at everything else.

### A new level: easy to change the one level; no support for several yet

Today a level means `World.roc` (sizes) plus `tile_spots` (the layout
rule). Changing *the* level is easy: edit the function and rebuild. But
there is no notion of *levels*. The world is compiled into the physics
(`world.zig` imports `world.zon` at compile time), so picking a level at
runtime would need the Zig to hold the world as data rather than
constants. That's a Zig change, not a Roc one. CC's commit "retire the
configuration's pins: any world and rules that fit their types play"
started down this road.

Where Roc would shine for levels is **a level as a picture**:

```roc
level_one =
    \\D . D . D
    \\. C . c c
    \\D . D . D
```

That's a string per level, parsed in Roc into spots, with `expect`s that
each one is well formed (no overlap, every critter inside the park, a
breed in each corner). Writing a level would then be drawing it, and a
bad one would fail the build.

## The verdict, briefly

- **Tuning:** already excellent. Named, in one place, guarded by `expect`s.
- **Behaviour in Roc:** readable, and tested in its own terms. Twenty-two
  `expect`s in `Wish.roc` read like the design doc.
- **New critters:** the weakest point. Kinds are tags in the layout, then
  record fields in the rules, then bare numbers in the wish and the walk.
  Making `Kind` a tag through and through, with the rules a `match` on
  pairs, would put Roc's exhaustiveness to work, and make adding a critter
  a compiler-guided chore instead of a hunt.
- **Levels:** easy for one, not built for many. The main blocker is the
  Zig holding the world as compile-time constants. Levels drawn as
  strings would suit Roc well.

## A side note on the `.a` files

The Roc physics is checked in compiled (`roc/lib/physics-*.a`, about 400 KB
in all), so builds don't need the Roc compiler. That's reasonable. But
nothing ties an archive to the `.roc` source it came from: edit `Walk.roc`,
forget `zig build roc`, and the old physics runs. A hash of the Roc
sources written beside the archives, checked by every build, would turn
that into a refusal. That's for CC and Steve to decide; I've only
suggested it.
