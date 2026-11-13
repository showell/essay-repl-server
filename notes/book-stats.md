# The book in numbers

These counts come from `canvas_apps/safari/tutorial/book_stats.shale`, run on the built book of 2026-11-13. That build includes the promise-hunt fixes and the trims to 900 words.

- **Roc lines** are the non-blank lines inside Roc code blocks.
- **Prose words** are the words outside every code block, headings and table cells included.
- **An image** is a picture the Roc code draws that the reader only looks at.
- **A widget** is one the reader works: with the VCR controls, by clicking, or, for the ride itself, with the keys.

`tutorial/book_check.mjs` already records which widget is which, so the count reads its table.

A chapter now holds at most 900 words of prose (MISSION A7). The tutorial gate runs this script and fails a chapter that goes over.

| Chapter | Roc lines | Prose words | Diagrams | Widgets | Images |
|---|---|---|---|---|---|
| 1. Introduction | 0 | 294 | 0 | 1 | 0 |
| 2. One page | 18 | 346 | 0 | 0 | 1 |
| 3. The problem | 0 | 527 | 1 | 0 | 0 |
| 4. Platforms, packages and modules | 7 | 309 | 0 | 0 | 0 |
| 5. Types | 99 | 871 | 0 | 0 | 2 |
| 6. Functions | 20 | 658 | 0 | 0 | 0 |
| 7. Things | 24 | 699 | 0 | 0 | 2 |
| 8. Tag unions: billboard critters | 45 | 882 | 1 | 0 | 1 |
| 9. Shapes | 69 | 495 | 0 | 0 | 2 |
| 10. Lists and map: a far tree | 79 | 890 | 0 | 0 | 1 |
| 11. The pipeline | 50 | 700 | 1 | 0 | 1 |
| 12. Where clauses: asking a kind | 69 | 885 | 0 | 0 | 1 |
| 13. Errors as tag unions | 63 | 888 | 1 | 0 | 0 |
| 14. The sky and the grass | 64 | 720 | 0 | 0 | 1 |
| 15. Mountains | 120 | 668 | 0 | 0 | 1 |
| 16. The road | 52 | 736 | 0 | 0 | 2 |
| 17. Rails | 62 | 454 | 1 | 0 | 1 |
| 18. Radio towers | 56 | 693 | 0 | 0 | 1 |
| 19. Herds | 53 | 390 | 0 | 0 | 1 |
| 20. Immutable values: a flip book | 20 | 496 | 0 | 1 | 0 |
| 21. Records | 10 | 182 | 0 | 0 | 0 |
| 22. Pure functions and effects | 0 | 282 | 0 | 0 | 0 |
| 23. Opaque types: the clock | 62 | 476 | 0 | 0 | 0 |
| 24. The ride instant | 33 | 455 | 0 | 0 | 0 |
| 25. The beacons | 48 | 757 | 0 | 1 | 0 |
| 26. The setting sun | 54 | 722 | 0 | 3 | 0 |
| 27. The rider | 95 | 789 | 1 | 0 | 0 |
| 28. The throttle | 44 | 452 | 2 | 0 | 0 |
| 29. Variables and loops: rehearsal | 69 | 748 | 0 | 1 | 0 |
| 30. The rider's gaze | 102 | 889 | 1 | 1 | 0 |
| 31. The truck | 97 | 764 | 0 | 0 | 1 |
| 32. The truck's motion | 101 | 748 | 1 | 0 | 0 |
| 33. The cat | 155 | 872 | 1 | 1 | 0 |
| 34. The bird | 95 | 846 | 0 | 1 | 0 |
| 35. What a cat does to the rider | 38 | 407 | 1 | 0 | 0 |
| 36. The math layer | 78 | 884 | 1 | 0 | 0 |
| 37. Proving it | 30 | 882 | 0 | 0 | 0 |
| 38. The platform | 68 | 872 | 1 | 0 | 0 |
| 39. Zooming back out | 8 | 474 | 1 | 0 | 0 |
| Appendix: the patterns | 0 | 247 | 0 | 0 | 0 |
| Appendix: list functions | 0 | 240 | 0 | 0 | 0 |
| Appendix: what catches you out | 0 | 252 | 0 | 0 | 0 |
| Appendix: glossary | 0 | 470 | 0 | 0 | 0 |
| Credits | 0 | 60 | 0 | 0 | 0 |
| **The 39 chapters** | 2157 | 25102 | 15 | 10 | 19 |
| **The appendices** | 0 | 1269 | 0 | 0 | 0 |
| **The whole book** | 2157 | 26399 | 15 | 10 | 19 |

The trims took about 2,100 words out of nine chapters, which were 901 to 1,458 words long. Every one of them is now between 871 and 890.

To run it again, after a tutorial gate in the lane:

```
shale canvas_apps/safari/tutorial/book_stats.shale
```
