# The negative-words lint: the change set

*Built by one agent in its own lane, then edited by me. It's merged to master (ea99565a) so later chapters inherit the lint. Every change is a plain revert if you dislike it.*

## The tool

`canvas_apps/safari/gates/book_negatives.shale` runs as `part=book_negatives` in the Safari gates, in about 30 ms. Here's what it does:
- It reads the prose of the new chapters, down to the heading "The modules". That stopping point moves down as chapters pass the loop.
- It skips code: fences, includes and backticks.
- It flags every sentence that holds a negative word: not, no, never, nothing, nobody, nowhere, neither, nor, without, unless, "rather than", lack, hardly and barely, plus all the n't contractions.
- A flagged sentence fails the gate, unless the table `canvas_apps/safari/book_negatives.txt` keeps it under a named kind.

## The kinds

| Kind | Fate | Example |
|---|---|---|
| extraneous | fix | "and a tree behind the rider doesn't show at all", after "The screen shows only what the rider sees" |
| contrast | fix | "Every function in this chapter has a `->` arrow, not `=>`." |
| hidden-positive | fix | "`flip` needs no annotation" for "the compiler works out its type" |
| presumed-worry | fix | "There's no event handler here." |
| hedge | fix | "there isn't much else to ask" |
| double-negative | fix | "The test needs nothing the module doesn't" |
| refusal | keep | "a rod with both ends behind it isn't drawn" (the MISSION D2 exception) |
| cautionary | keep, if it names a real trap | "Float addition isn't associative, so a sum's order is part of its meaning here." |
| authoritative | keep, if the code or compiler enforces it | "Roc forbids import cycles, so no path of arrows loops back." |

## What it found

The new chapters had only **4 negative sentences** in 337. We'd been enforcing D2 by hand, and it shows. All four were fixed, none were kept, and the table holds 0:

| Chapter | Before | Kind | After |
|---|---|---|---|
| The problem | "…a tree close by looks big, and a tree behind the rider doesn't show at all." | extraneous | "…and a tree close by looks big." |
| The pieces as types | "The world doesn't paint itself onto your eyes: light brings you information, and your mind makes the picture." | hidden-positive | "Light brings your eyes information, and your mind makes the picture." |
| Billboard Critters | "`flip` needs no annotation: the compiler works out its type from where it's used." | hidden-positive | "The compiler works out the type of `flip` from where it's used." |
| Billboard Critters | "A bend has room for one thing at most: an animal and its baby, a pond of ducks, or nothing." | contrast | "A bend is quiet, or it holds one thing: an animal and its baby, or a pond of ducks." |

For scale, the old draft below "The modules" has 288 negatives in 2,924 sentences, so each chapter will meet the lint as it passes the loop.

## My edit

The four rewrites read well, and I kept them. The real catch was elsewhere. Today's quads made one sentence in "The pieces as types" false: "Nearly every shape is a polygon." It now reads "Nearly every shape has straight edges."
