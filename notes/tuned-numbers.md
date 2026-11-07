# What these numbers stand for

Reviews turned up numbers that are right only because they were nudged until they looked right. Your smell list says "if a constant is right only because it was nudged until the eye agreed, ask what it stands for." Here they are, grouped. For each group, tell me one of three things:
- **eye:** it's the eye's choice. We document it as one ("chosen by eye") and stop asking.
- **rule:** it stands for something. Tell me what, and we'll write it that way.
- **derive:** it should come from other numbers. We'll work out the formula.

My guess and recommendation follow each group.

## 1. The trees' heights

```
small_height = 4.896 m
big tree = small × 1.3      red tree = small × 2      gold tree = small × 3
```

4.896 is exactly 136 × 0.036: the tree drawing is 136 parts tall, so a small tree is 36 mm a part. The ×1.3, ×2 and ×3 are a family of sizes. *Guess: eye for the factors. And 4.896 is really "36 mm a part", which is a rule worth writing that way: `small_height = tree_parts × 36 mm`.*

## 2. The herds' scatter

```
cows:  along += jitter × sin(i × 2.7)    across += jitter × cos(i × 1.9)
pigs:  along += jitter × sin(i × 2.3)    across += jitter × cos(i × 1.7)
```

These are a cheap, repeatable "random" scatter: each animal's index runs through a sine, so the herd doesn't stand in a grid. The phases only need to be unrelated enough to look scattered. *Recommend: rule. Name it once as a scatter function both herds call, such as `Scatter.offset(i, { along_phase, across_phase })`, documented as a repeatable stand-in for randomness. Each herd keeps its own phases, by eye.*

## 3. Where things stand on a segment

- **The cow herd:** 24 m from the segment's start.
- **The pig herd:** 60 m before the segment's end.
- **The cat:** looks for its tree from 105 m.

*Guess: eye. These are staging choices about where on a segment the rider meets each thing. Document them as such, beside each other in World, once World is split.*

## 4. The truck's lights

- **The glow:** it reaches 3.2 times as far as its lamp's farthest corner.
- **The brake lamp:** 0.1, 0.36, 0.2 and 0.5 shape it.
- **The cab's roof:** it reaches 0.3 of the cab's length.

*Guess: eye for all of them. They're the drawing of a truck, like the stills are the drawing of a cow. Document them as the truck's proportions.*

## 5. The rider's brake fade

The brake fades as `e^(-n/20)`, so `brake_decay` is 20 steps. *Guess: eye, unless the Motion chapter wants a physical braking curve. Keep it and document it, and revisit it with the Motion chapter's derivations (turn speeds, firmest brake).*

## 6. The mountains' shapes

`land_height`'s 18, 12, 0.9 and 1.9, and `range_height`'s 0.24, 0.16, 0.6 and +1.0, are already documented as tuned by eye in the backdrop cleanup. One of them has a known consequence: 0.9 waves per turn leaves a seam at due south. It's on the eye-test list, since a whole number of waves moves the land.

## A separate question: a perched bird and its tree

A perched bird sits exactly where its tree stands, so the two are the same depth from the camera, and the tie order paints the bird first. The tree's crown then covers the bird's feet. While landing, the bird is a little nearer, so it paints over the tree, then it drops behind the moment it perches. *Recommend: a perched bird sorts in front of its tree, as a named rule: "a critter perched on a tree is drawn over it". Today's look is a coincidence of the tie order. This moves the perched bird's pixels, so it's an eye test.*

A word per group is enough.

## Steve's answer (2026-11-07)

Agreed to every recommendation. "All the tuning numbers are just a fact of life in the app, and there's no perfect solution... we want to avoid silly things like the bird not actually being perched on top of the tree due to coincidences, but to use the truck as an example, all those dimensions are things that we got right with eye tests, so they're not likely to change too much."
