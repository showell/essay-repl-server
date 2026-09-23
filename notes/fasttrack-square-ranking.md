# Fast Track: ranking the squares

Every square a red piece can stand on, ranked best first. The squares count
the way to B3, as once B4 is taken, with a free face card allowed first. The
table is printed by `roc-apps/fasttrack/rank_board.roc` from
`Reach.routes_with`.

**The rules, in order:**

1. **Fewer cards to B3,** with every card but the joker.
2. **Among equals, a base square first,** the deeper first.
3. **More routes.** A route is every shortest sequence of moves, where a move
   is a card, or a face card then a card. For a square one card out, that is
   just its ways in: R1's two are F+5 and 6.
4. **While still tied,** rules 1 and 3 again (fewer cards, then more routes)
   with a smaller deck at each stage:
   - without the 6;
   - without the J, Q and K, which also takes away the free face card;
   - without the 7;
   - without the 4.

Each cell below is `cards / routes` with that stage's deck. A `-` means the
square cannot reach B3 at all with that deck: the bullseye needs a J, Q or K
to leave.

## What still ties

- **`rDS`, `rR3`, `rR4` and purple's fast-track square, at every stage.**
  - With all the cards, each has two one-card routes, and none of them uses
    a 6: F+2 or 3, F+7 or 8, F+8 or 9, F+9 or 10.
  - Without J, Q and K, each keeps exactly one route: 3, 8, 9 and 10.
  - Dropping the 7 and the 4 then touches none of them.
- **Green's fast-track square and purple's L4,** blue's fast-track square
  and purple's L3, and green's BR and green's R0: identical at every stage.
- **The four pen squares,** which are the same square.

**R3 against R4.** You ranked R4 above R3, because R3's second way is face +
7 and R4's is face + 8. The cascade removes the J, Q and K before the 7, and
that takes both face routes out at once. With the 7 removed before the
J/Q/K, R3 would lose its face + 7 route first, and R4 would come out ahead.
The rest of the group would still tie.

**R1 against R3,** the pair that tied before, now splits at the first stage.
Without the 6, R1 keeps only F+5, while R3 keeps both of its routes.

## The ranking

| square | no joker | no 6 | no J/Q/K | no 7 | no 4 |
|---|---|---|---|---|---|
| rB3 | 0 / 1 | 0 / 1 | 0 / 1 | 0 / 1 | 0 / 1 |
| rB2 | 1 / 4 | 1 / 4 | 1 / 1 | 1 / 1 | 1 / 1 |
| rB1 | 1 / 5 | 1 / 5 | 1 / 1 | 1 / 1 | 1 / 1 |
| rDS | 1 / 2 | 1 / 2 | 1 / 1 | 1 / 1 | 1 / 1 |
| rR3 | 1 / 2 | 1 / 2 | 1 / 1 | 1 / 1 | 1 / 1 |
| rR4 | 1 / 2 | 1 / 2 | 1 / 1 | 1 / 1 | 1 / 1 |
| pFT | 1 / 2 | 1 / 2 | 1 / 1 | 1 / 1 | 1 / 1 |
| rR2 | 1 / 2 | 1 / 1 | 1 / 1 | 2 / 2 | 2 / 2 |
| rR1 | 1 / 2 | 1 / 1 | 2 / 4 | 2 / 4 | 2 / 3 |
| rR0 | 1 / 1 | 1 / 1 | 1 / 1 | 1 / 1 | 1 / 1 |
| gFT | 1 / 1 | 1 / 1 | 2 / 6 | 2 / 6 | 2 / 6 |
| pL4 | 1 / 1 | 1 / 1 | 2 / 6 | 2 / 6 | 2 / 6 |
| rBR | 1 / 1 | 1 / 1 | 2 / 4 | 2 / 4 | 2 / 3 |
| bullseye | 1 / 1 | 1 / 1 | - | - | - |
| bFT | 2 / 48 | 2 / 43 | 2 / 6 | 2 / 4 | 2 / 4 |
| pL3 | 2 / 48 | 2 / 43 | 2 / 6 | 2 / 4 | 2 / 4 |
| rFT | 2 / 44 | 2 / 38 | 2 / 4 | 2 / 4 | 2 / 4 |
| pL2 | 2 / 34 | 2 / 28 | 2 / 4 | 2 / 4 | 2 / 4 |
| gL4 | 2 / 31 | 2 / 29 | 3 / 21 | 3 / 12 | 3 / 12 |
| pL1 | 2 / 24 | 2 / 17 | 2 / 3 | 2 / 2 | 2 / 2 |
| pL0 | 2 / 22 | 2 / 14 | 2 / 4 | 2 / 2 | 2 / 2 |
| pHH | 2 / 22 | 2 / 14 | 2 / 3 | 2 / 1 | 2 / 1 |
| bL4 | 2 / 21 | 2 / 18 | 3 / 6 | 3 / 4 | 3 / 4 |
| pDS | 2 / 20 | 2 / 14 | 2 / 4 | 2 / 2 | 2 / 2 |
| rL4 | 2 / 18 | 2 / 15 | 3 / 5 | 3 / 5 | 3 / 4 |
| pBR | 2 / 16 | 2 / 14 | 2 / 3 | 2 / 3 | 2 / 3 |
| pR0 | 2 / 12 | 2 / 12 | 2 / 2 | 2 / 2 | 2 / 2 |
| pR1 | 2 / 9 | 2 / 9 | 2 / 1 | 2 / 1 | 2 / 1 |
| pR2 | 2 / 5 | 2 / 5 | 3 / 28 | 3 / 21 | 3 / 21 |
| gL3 | 2 / 5 | 2 / 5 | 3 / 18 | 3 / 12 | 3 / 12 |
| rHH | 2 / 5 | 2 / 3 | 3 / 6 | 3 / 6 | 4 / 16 |
| rL1 | 2 / 4 | 2 / 4 | 3 / 5 | 3 / 5 | 4 / 24 |
| rL0 | 2 / 4 | 2 / 3 | 2 / 1 | 2 / 1 | 3 / 4 |
| rL2 | 2 / 3 | 2 / 3 | 2 / 1 | 2 / 1 | 3 / 4 |
| gL2 | 2 / 2 | 2 / 2 | 3 / 16 | 3 / 13 | 3 / 13 |
| gR1 | 2 / 2 | 2 / 2 | 3 / 12 | 3 / 10 | 3 / 6 |
| gBR | 2 / 2 | 2 / 2 | 3 / 6 | 3 / 6 | 3 / 6 |
| gR0 | 2 / 2 | 2 / 2 | 3 / 6 | 3 / 6 | 3 / 6 |
| rL3 | 2 / 2 | 2 / 2 | 3 / 4 | 3 / 4 | 3 / 4 |
| gDS | 2 / 2 | 2 / 1 | 3 / 6 | 4 / 76 | 4 / 76 |
| gHH | 2 / 2 | 2 / 1 | 3 / 1 | 3 / 1 | 3 / 1 |
| pR3 | 2 / 1 | 2 / 1 | 3 / 24 | 3 / 15 | 3 / 15 |
| gL0 | 2 / 1 | 2 / 1 | 3 / 9 | 3 / 9 | 3 / 9 |
| gL1 | 2 / 1 | 2 / 1 | 3 / 6 | 3 / 6 | 3 / 6 |
| gR2 | 2 / 1 | 2 / 1 | 4 / 92 | 4 / 64 | 4 / 56 |
| pR4 | 3 / 374 | 3 / 269 | 3 / 18 | 3 / 12 | 3 / 12 |
| bL3 | 3 / 346 | 3 / 301 | 3 / 6 | 3 / 4 | 3 / 4 |
| bL2 | 3 / 221 | 3 / 190 | 3 / 6 | 3 / 4 | 3 / 4 |
| bR1 | 3 / 182 | 3 / 160 | 3 / 10 | 3 / 8 | 3 / 4 |
| bR2 | 3 / 152 | 3 / 132 | 4 / 45 | 4 / 33 | 4 / 24 |
| bDS | 3 / 142 | 3 / 65 | 3 / 6 | 4 / 8 | 4 / 8 |
| bBR | 3 / 139 | 3 / 105 | 3 / 6 | 3 / 4 | 3 / 4 |
| bR0 | 3 / 138 | 3 / 122 | 3 / 6 | 3 / 4 | 3 / 4 |
| bHH | 3 / 125 | 3 / 69 | 4 / 40 | 4 / 30 | 4 / 18 |
| bL1 | 3 / 106 | 3 / 93 | 4 / 48 | 4 / 38 | 4 / 30 |
| gR3 | 3 / 96 | 3 / 86 | 4 / 79 | 4 / 51 | 4 / 43 |
| bL0 | 3 / 81 | 3 / 73 | 3 / 6 | 3 / 4 | 3 / 4 |
| bR3 | 3 / 41 | 3 / 35 | 4 / 44 | 4 / 24 | 4 / 16 |
| gR4 | 3 / 34 | 3 / 28 | 4 / 56 | 4 / 48 | 4 / 40 |
| rHP1 | 3 / 8 | 3 / 3 | 3 / 1 | 3 / 1 | 4 / 4 |
| rHP2 | 3 / 8 | 3 / 3 | 3 / 1 | 3 / 1 | 4 / 4 |
| rHP3 | 3 / 8 | 3 / 3 | 3 / 1 | 3 / 1 | 4 / 4 |
| rHP4 | 3 / 8 | 3 / 3 | 3 / 1 | 3 / 1 | 4 / 4 |
| bR4 | 3 / 5 | 3 / 5 | 3 / 1 | 3 / 1 | 4 / 16 |
