# Units in safari: no bare F64

*Decided by Steve in Q&A, 2026-11-05. The rule: F64 lives inside the unit types and the trigonometry, and almost nowhere else.*

| Meaning | Type | Notes |
|---|---|---|
| The ride's step number | `Clock`, a U32 | Whole, and only ever counted |
| A simulated duration | `Steps` | Whole. Subtracting two `Clock`s gives one |
| A position along an animation | `Beats` | Fractional, and tied to no clock: "the cat freezes at beat 10" |
| A ratio from 0 to 1 | `Fraction`, opaque | Progress, dusk, easing. Anything that can pass 1, like `scale`, gets its own name |
| How strongly something holds the rider's eye | `Attention`, opaque | From 0 upward: the cat reaches 1.8 |
| A length in metres | `Distance` | |
| A position on the road | `Along`, `Across` | Mirrors `Bearing` and `Turn`: two `Along`s subtract to a `Distance`, and neither can be passed as the other |
| A length on screen | `Pixels` | Stops at the edge of `lib.Shapes` |
| Real time | none in safari | `dt` is removed from safari's path, so real time can't reach it |

A simulated step is always whole. The fractional "steps" of the old timelines were never moments in time: they were positions along an animation, which is why they become `Beats`.

## How it lands

One stage at a time, because every stage touches the same modules. Each must leave every frame hash and the page's drawn hash unchanged, and code must stay identical where `same_code` can check it.

1. Time: `Clock`, `Steps`, `Beats`, and `dt` out of safari's path.
2. `Fraction`.
3. `Distance`, then `Along` and `Across`.
4. `Pixels`.
5. A lint holding bare `F64` in safari's signatures at zero, with named exceptions, and the rule in `docs/roc-style.md`.
