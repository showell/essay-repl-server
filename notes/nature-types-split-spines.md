# Nature types, split in two: the spines

*Your call: chapter 9 stays short and snappy, and `where` gets a chapter of its own with room to breathe. Both follow the new D5: prose before the code motivates the Roc feature, the code speaks for itself, and prose after it only clarifies syntax.*

## Chapter 9: Nature types (short)

**Picture:** the four conifers, as now.

1. **A thing beside the road takes three forms, placed, sighted and rendered, with its kind inside, so this chapter looks at one kind.** (A restatement of "The pieces as types", framed as one.)
2. **A tree needs a height and a color, and nothing about where it stands, so `Conifer` holds just that: four tags, one for each sort of tree.** (The motivation, then `{{module Conifer}}`.)
3. **The code reads plainly, so the prose after it clarifies only syntax.** (`:=` against `Billboard`'s `::`, `Green | SmallGreen`, and `is_eq` on tags.)
4. **Two of its functions sit inside the type's braces, and the rest outside, and the next chapter shows why.** (One forward pointer, named and framed as later, C3 and C12.)
5. **So a kind describes a thing, and the pipeline does the rest: but the pipeline knows no kinds, so how does it get a height and a sprite out of one?** (The close leaves the question for chapter 10.)

## Chapter 10: Asking a kind (room to breathe)

**Picture, for variety:** five different kinds side by side, all drawn by the same function: a tree, a cow, a radio tower, the cat and the bird. Chapter 9's picture varies the tags of one kind, and this one varies the kinds.

1. **One function, `rendering_of`, draws every kind in the picture, so it must call a `scenery_sprite` that belongs to a type it can't name.** (The problem, stated before any code.)
2. **A type variable says "any type", but any type might have no sprite at all, so `rendering_of` needs a way to say "any type that has one".** (Still motivation: why a plain type variable isn't enough.)
3. **So Roc lets an annotation ask, with `where`: any type that has a `scenery_sprite` of this type, inside its braces.** (`Pipeline.rendering_of`, then the syntax after it: the brackets, `kind.scenery_sprite :`, and a requirement's own type.)
4. **The compiler checks the requirement at every call: when the ride renders a `Sighted(Conifer)`, it looks inside `Conifer`'s braces and finds the sprite.** (One call site from `Scene`, quoted.)
5. **But a type without the function is a compile error, so here's a kind that forgot its sprite, and what the compiler says.** (A new `{{fails}}` program, like the ones in earlier chapters: the compiler's own words.)
6. **The compiler knows, at each call, which type fills `kind`, so it knows which `scenery_sprite` runs, and nothing is looked up while the ride runs.** (Under the hood, in plain words. I'll check the exact claim with the compiler before writing it.)
7. **Sighting asks for a height the same way, so `scenery_sighting_of` carries a second `where`, and it answers with a `Try`.** (`Try`, the three reasons, and `TooSmall` as new; towers in one sentence.)
8. **Roc matches a `where` by name and type alone, so the names say what they're for: `scenery_height` and `scenery_sprite`.** (What an accidental match would do, then why the prefix.)
9. **So a kind meets the pipeline by having two functions inside its braces, and five kinds do.** (The close, in sync with paragraph 1.)

## For you

- **Chapter 10's title.** "Asking a kind" is my suggestion; it says what `where` does in the ride's own words.
- **Paragraph 5's failing program** is the most concrete teacher of `where`. It means a small new file under `tutorial/fails/`, which the build already checks really fails.
