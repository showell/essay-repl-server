# The voice pass

You caught "Everyone knows what a clock does. The news is what this one refuses to do." The blind nitpicker had missed it. This pass hunts that kind of line across the whole book.

## The reader

The brief names MISSION's voice and tone rules (axes D and E) and gives no example sentences. On The clock it caught your sentence on its own, as D2, D11 and D7, along with seventeen siblings such as "the module leaves adding two clocks out" and "the clock stops the program".

## The rewrite of The clock

The clock got a clean draft rather than a sentence pass. It opens on what a clock counts, then splits a moment from a length, then shows the compiler rejecting `Clock.start + 7`. The table now includes `next`. `<` calling `is_lt` sits beside `+` calling `plus`. Two of `Clock.roc`'s doc comments now say when the code crashes, in place of what a clock "is no count of".

## The rest of the book

Six voice readers covered the other 36 chapters, six chapters each, and found about 290 sentences. Six forks of me then phrased the fixes, one group of six chapters each, with one rule for what counts as borderline. About 210 sentences changed. About 80 borderline ones stayed: "gives back", short glosses on a code name, and passives that use the glossary's word.

These are the worst sentences each reader found:
- "It names the page's parts in the code, and it skips how each part is made." (One page)
- "So a still is free of pixels and metres, and the same numbers draw a cow in the distance and a cow by the road." (Billboard Critters)
- "A thing behind the camera, a thing the horizon hides and a thing too small to see all stay out of the frame." (Refused)
- "Everything else in a frame is derived from them and the road, worked out again each time." (The ride instant, D1's own banned phrase)
- "It reads like a list of rules because that's what it is." (The throttle)
- "…`EncounterReaction`, which knows which encounters ask anything of the rider." (What a cat does to the rider)

Five chapters in a row ended on a pointer to the next one (E5). Three now end on what the reader has, and two on what's still open.

## The lint

`book_negatives.shale words=voice` flags the disguised negatives ("refuses", "leaves out", "stays out", "skips", "free of") and the verbs that give code a will ("knows", "decides", "wants", "trusts", "forgets"). The gate holds it at zero, like the negatives lint. Ten sentences are kept in `book_voice.txt` as real refusals, such as a sighting that returns `Err` or the compiler rejecting a program. A link to a chapter, such as `{{chapter Refused}}`, is no longer a hit, for either lint.

The rebuilt book is at http://143.244.172.148:9210/tutorial.fresh/
