# Fast Track: ranking the squares

Every square a red piece can stand on, ranked best first, from the table on
the board at `?show=b3`. That table counts cards to B3, as once B4 is taken,
and lets a free face card go first. Printed by
`roc-apps/fasttrack/rank_board.roc`.

**The rules, in order:**

1. **Fewer cards to B3.**
2. **Among equals, a base square first, the deeper first.** Rule 3 alone
   would put B1 above B2: B1 has six ways into B3, a 2 or a face card then
   any one-step card, and B2 has five.
3. **More ways in.** A way is a distinct first card on a shortest route.
   "F+5" (a face card, then a 5) is a different way from "6".
4. **More ways on an expendable card:** 2, 3, 5, 8, 9 or 10, counting the card
   played after any face card. These don't leave the pen, go backwards,
   split, or let you play again.

## The ties left after all four rules

- **The purest pair: `rR1` and `rR3`.** Both are 1 card, with 2 ways and 1 of
  them expendable. R1 is F+5 or 6 (the 5 is expendable); R3 is F+7 or 8 (the
  8 is).
- **`rDS`, `rR4` and purple's fast-track square:** 1 card, 2 ways, both
  expendable (F+2 or 3; F+8 or 9; F+9 or 10).
- **`rBR`, `rR0`, green's fast-track square, purple's L4 and the bullseye:**
  1 card, a single expendable way (F+3; 5; F+10; F+10; F+10).
- **Two-card squares:** `rFT`, `bFT` and `pL3` (26 ways, 12 expendable);
  `rL3`, `gL2`, `gR0` and `gR1` (2 ways, 2 expendable); `rL2`, `gHH` and
  `gBR`; `gL0`, `gL1`, `gR2` and `pR3`.
- **The four pen squares,** which really are the same square.

Your two cases come out as you said: **R1 beats R0**, on 2 ways against 1,
and **R4 beats R3**, on 2 expendable ways against 1.

**One caution.** For squares two or more cards out, rule 3 counts only the
*first* card of a shortest way. The face-card pairs inflate those counts:
`rFT` has 26. Whether that tells two squares apart usefully is open.

## The ranking

| square | cards | ways | expendable | ways in |
|---|---|---|---|---|
| rB3 | 0 | 0 | 0 |  |
| rB2 | 1 | 5 | 0 | A, J, Q, K, Jo |
| rB1 | 1 | 6 | 1 | F+A, 2, F+J, F+Q, F+K, F+Jo |
| rDS | 1 | 2 | 2 | F+2, 3 |
| rR4 | 1 | 2 | 2 | F+8, 9 |
| pFT | 1 | 2 | 2 | F+9, 10 |
| rR1 | 1 | 2 | 1 | F+5, 6 |
| rR3 | 1 | 2 | 1 | F+7, 8 |
| rR2 | 1 | 2 | 0 | F+6, 7 |
| rBR | 1 | 1 | 1 | F+3 |
| rR0 | 1 | 1 | 1 | 5 |
| gFT | 1 | 1 | 1 | F+10 |
| pL4 | 1 | 1 | 1 | F+10 |
| bullseye | 1 | 1 | 1 | F+10 |
| rFT | 2 | 26 | 12 | F+8, 9, F+9, 10, F+10, A, F+A, 2, F+2, 3, F+3, 5, F+5, 6, F+6, 7, F+7, 8, J, F+J, Q, F+Q, K, F+K, Jo, F+Jo |
| bFT | 2 | 26 | 12 | F+2, 3, F+3, 5, F+5, 6, F+6, 7, F+7, 8, F+8, 9, F+9, 10, F+10, A, F+A, 2, J, F+J, Q, F+Q, K, F+K, Jo, F+Jo |
| pL3 | 2 | 26 | 12 | F+2, 3, F+3, 5, F+5, 6, F+6, 7, F+7, 8, F+8, 9, F+9, 10, F+10, A, F+A, 2, J, F+J, Q, F+Q, K, F+K, Jo, F+Jo |
| pL2 | 2 | 21 | 12 | F+3, 5, F+5, 6, F+6, 7, F+7, 8, F+8, 9, F+9, 10, F+10, F+A, 2, F+2, 3, F+J, F+Q, F+K, F+Jo |
| gL4 | 2 | 18 | 6 | F+2, F+3, F+5, F+6, F+7, F+8, F+9, F+10, A, F+A, J, F+J, Q, F+Q, K, F+K, Jo, F+Jo |
| pL1 | 2 | 15 | 11 | 5, F+5, 6, F+6, 7, F+7, 8, F+8, 9, F+9, 10, F+10, F+2, 3, F+3 |
| rL4 | 2 | 14 | 7 | F+9, F+10, F+A, 2, F+2, F+3, F+5, F+6, F+7, F+8, F+J, F+Q, F+K, F+Jo |
| pL0 | 2 | 13 | 9 | F+5, 6, F+6, 7, F+7, 8, F+8, 9, F+9, 10, F+10, F+3, 5 |
| bL4 | 2 | 13 | 6 | F+3, F+5, F+6, F+7, F+8, F+9, F+10, F+A, F+2, F+J, F+Q, F+K, F+Jo |
| pHH | 2 | 12 | 8 | F+6, 7, F+7, 8, F+8, 9, F+9, 10, F+10, 5, F+5, 6 |
| pDS | 2 | 11 | 7 | F+7, 8, F+8, 9, F+9, 10, F+10, F+5, 6, F+6, 7 |
| pBR | 2 | 9 | 6 | F+8, 9, F+9, 10, F+10, F+6, 7, F+7, 8 |
| pR0 | 2 | 7 | 6 | F+7, 8, F+8, 9, F+9, 10, F+10 |
| pR1 | 2 | 6 | 5 | 4 back, F+8, 9, F+9, 10, F+10 |
| gL3 | 2 | 6 | 1 | F+A, 2, F+J, F+Q, F+K, F+Jo |
| pR2 | 2 | 4 | 3 | F+4 back, F+9, 10, F+10 |
| rL0 | 2 | 4 | 1 | F+4 back, 4 back, F+5, 6 |
| rHH | 2 | 4 | 0 | 4 back, F+4 back, F+6, 7 |
| rL1 | 2 | 3 | 1 | 4 back, F+4 back, 5 |
| rL3 | 2 | 2 | 2 | F+2, 3 |
| gL2 | 2 | 2 | 2 | F+2, 3 |
| gR0 | 2 | 2 | 2 | F+8, 9 |
| gR1 | 2 | 2 | 2 | F+9, 10 |
| rL2 | 2 | 2 | 1 | 4 back, F+3 |
| gHH | 2 | 2 | 1 | F+5, 6 |
| gBR | 2 | 2 | 1 | F+7, 8 |
| gDS | 2 | 2 | 0 | F+6, 7 |
| gL0 | 2 | 1 | 1 | 5 |
| gL1 | 2 | 1 | 1 | F+3 |
| gR2 | 2 | 1 | 1 | F+10 |
| pR3 | 2 | 1 | 1 | F+10 |
| pR4 | 3 | 28 | 12 | A, F+A, 2, F+2, 3, F+3, 5, F+5, 6, F+6, 7, F+7, 8, F+8, 9, F+9, 10, F+10, J, F+J, Q, F+Q, K, F+K, Jo, F+Jo, 4 back, F+4 back |
| gR3 | 3 | 27 | 12 | A, F+A, 2, F+2, 3, F+4 back, F+10, J, F+J, Q, F+Q, K, F+K, Jo, F+Jo, F+3, 5, F+5, 6, F+6, 7, F+7, 8, F+8, 9, F+9, 10 |
| bL3 | 3 | 23 | 9 | A, F+A, 2, 5, F+5, 6, F+6, 7, J, F+J, Q, F+Q, K, F+K, Jo, F+Jo, F+7, 8, F+8, 9, F+9, 10, F+10 |
| gR4 | 3 | 21 | 12 | F+A, 2, F+2, 3, F+3, F+J, F+Q, F+K, F+Jo, 5, F+5, 6, F+6, 7, F+7, 8, F+8, 9, F+9, 10, F+10 |
| bL2 | 3 | 19 | 10 | F+A, 2, F+2, 3, F+5, 6, F+6, 7, F+7, 8, F+J, F+Q, F+K, F+Jo, F+8, 9, F+9, 10, F+10 |
| bL1 | 3 | 12 | 9 | F+2, 3, F+3, F+6, 7, F+7, 8, F+8, 9, F+9, 10, F+10 |
| bL0 | 3 | 9 | 8 | F+3, 5, F+7, 8, F+8, 9, F+9, 10, F+10 |
| bHH | 3 | 8 | 7 | 5, F+5, 6, F+8, 9, F+9, 10, F+10 |
| bDS | 3 | 7 | 4 | F+5, 6, F+6, 7, F+9, 10, F+10 |
| bR1 | 3 | 5 | 4 | 4 back, F+8, 9, F+9, 10 |
| bR2 | 3 | 5 | 3 | 4 back, F+4 back, F+9, 10, F+10 |
| bBR | 3 | 5 | 2 | F+6, 7, F+7, 8, F+10 |
| bR0 | 3 | 4 | 3 | F+7, 8, F+8, 9 |
| bR3 | 3 | 3 | 1 | F+4 back, F+10, 4 back |
| rHP1 | 3 | 3 | 0 | A, 6, Jo |
| rHP2 | 3 | 3 | 0 | A, 6, Jo |
| rHP3 | 3 | 3 | 0 | A, 6, Jo |
| rHP4 | 3 | 3 | 0 | A, 6, Jo |
| bR4 | 3 | 2 | 0 | 4 back, F+4 back |
