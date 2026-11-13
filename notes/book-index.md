# The book's index, and what it shows

The index is built from the book itself. `tutorial/index_terms.txt` holds 73 terms, each with a category and the patterns that find it. `tutorial/book_index.shale` reads the built book's prose and records which chapters mention each term, which chapter mentions it most, and which mentions it first. So the index stays true as the chapters change.

This is the second pass. The first one showed where English collides with the book's words ("still", "kind", "limits"), and those patterns are now tighter.

## Categories

I settled on three:
- **Roc concepts**: 36 terms, from modules to `Box`.
- **Animation concepts**: 26 terms, from shapes to the flip book.
- **Safari Ride's design**: 12 terms, in place of "Other". Every term that didn't fit the first two turned out to be one of the ride's own design ideas: carried and derived, the sighting, the kind, the chain of limits, rehearsal, the five pieces. Naming them as a category says something true about the book.

## What the index shows about the structure

These are the findings I'd act on, strongest first. Most of the "mentioned early" list is the opening chapters previewing the book on purpose, and I've left those out.

1. **The camera has no home before chapter 36.** Eighteen chapters mention it. The one that dwells on it is The math layer, near the end. The rider's view is one of the five pieces, and the pipeline chapters solve it without ever settling what the camera is. A short paragraph in The pipeline, saying what the camera holds, would give it a home where it first bites.
2. **"Spot" is a glossary word with no chapter.** It's in six chapters, never more than three times in one. The pipeline is where a spot is made (place, then sighting, then spot), so that chapter should own it.
3. **"Project" lives in The truck, not The math layer.** Projecting onto the screen is the math layer's subject, but only The truck uses the word. The math layer says "divide by `forward`" and never names the step. One word in the math layer fixes it, and so does F1: one word for one thing.
4. **The sighting's home is the errors chapter, not The pipeline.** The pipeline makes sightings, and Errors as tag unions refuses them. The errors chapter mentions sightings nine times and the pipeline only twice. That's mild, and it may be honest.
5. **Record update is used before its interlude.** Rails (17) explains it in place, then Records (21) teaches it. Rails' one-line gloss is fine under C4. Moving Records earlier would cost the world chapters their run. I'd leave it.
6. **Types and Functions each first mention ten terms.** They're the two Roc chapters that open the book, so that's expected. Still, the counts show they're the heaviest pages for a new reader.
7. **Six terms live in a single chapter:** closure, cone, `var` and `while`, `Box`, the frame hash, and projection. A one-chapter term is fine when the chapter owns it. Closure and `var` are Roc ideas the book never reuses, so they're candidates to drop from the index.

## How it goes into the book

I propose an "Appendix: index" with one table per category. Each table has three columns:
- **the term**;
- **its main chapter**, linked: the chapter that mentions it most;
- **every other chapter** it appears in, by number.

A term spread across fifteen chapters or more shows its main chapter and "throughout", rather than a long run of numbers. That covers frame, step, module and record.

The appendix would come from a `{{index}}` include, which the book's builder expands at build time from `index_terms.txt`. That keeps the index out of `tutorial.md` as generated text, so it can never go stale.

## The current index

Run `shale canvas_apps/safari/tutorial/book_index.shale` in the lane, after a tutorial gate, for the full tables with every chapter number. The main chapters:

| Roc concept | Main chapter |
|---|---|
| Module | 5. Types |
| Package | 4. Platforms, packages and modules |
| Platform | 38. The platform |
| Type annotation | 6. Functions |
| Record, record update | 21. Records |
| Tag union, tag, `match` | 8. Tag unions: billboard critters |
| Type variable, `where` clause, method | 12. Where clauses: asking a kind |
| Opaque type, nominal type | 5. Types |
| Static dispatch, functions as values, anonymous functions, blocks, constants, doc comments, `if` | 6. Functions |
| Closure | 16. The road |
| `Try`, `?`, `crash`, invariant | 13. Errors as tag unions |
| `??` | 34. The bird |
| `expect` | 37. Proving it |
| `var` and `while` | 29. Variables and loops: rehearsal |
| Pure functions, effects and `!`, the arrows | 22. Pure functions and effects |
| `..` in a pattern | 15. Mountains |
| List functions | 10. Lists and map: a far tree |
| `Box` | 38. The platform |

| Animation concept | Main chapter |
|---|---|
| Shape | 38. The platform |
| Triangle and rectangle | 9. Shapes |
| Cone | 10. Lists and map: a far tree |
| Lights and glow, projection, clipping | 31. The truck |
| Frame, step, timeline and stage | 33. The cat |
| Picture | 26. The setting sun |
| Sprite | 5. Types |
| Rendering, depth and paint order | 11. The pipeline |
| Camera, lens and focal length, perspective, near plane | 36. The math layer |
| Horizon, blend | 14. The sky and the grass |
| Billboard | 7. Things |
| Still | 8. Tag unions: billboard critters |
| Polygon and quad | 17. Rails |
| Lean and roll | 27. The rider |
| Yaw and bearing | 15. Mountains |
| Easing | 25. The beacons |
| Flip book | 20. Immutable values: a flip book |

| Safari Ride's design | Main chapter |
|---|---|
| Carried and derived, encounter and encounter plan | 39. Zooming back out |
| Segment and route | 16. The road |
| Bend | 8. Tag unions: billboard critters |
| Sighting | 13. Errors as tag unions |
| Spot | 31. The truck |
| Kind | 12. Where clauses: asking a kind |
| Solid, card, far scenery | 15. Mountains |
| Chain of limits | 28. The throttle |
| Rehearsal | 29. Variables and loops: rehearsal |
| Frame hash | 37. Proving it |
| The five pieces | 3. The problem |

Some main chapters show what "mentions most" really measures. Shape lands in The platform, frame and step in The cat, and carried and derived in Zooming back out. For the book, I'd let `index_terms.txt` name a term's main chapter where the count picks the wrong one, and have the script check that the named chapter mentions the term at all.
