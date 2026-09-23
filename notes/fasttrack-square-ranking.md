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
   - without the 7;
   - without the 4;
   - without the J, Q and K, which also takes away the free face card.
     This comes late, so that face + 8 still counts as a cheaper play than
     face + 7;
   - last, without the 9 and 10, so a square reached with a 2 or 3 beats one
     reached with a 9 or 10.

Each cell below is `cards / routes` with that stage's deck. A `-` means the
square cannot reach B3 at all with that deck: the bullseye needs a J, Q or K
to leave.

## What still ties

- **Green's fast-track square and purple's L4,** and **blue's fast-track
  square and purple's L3:** identical at every stage.
- **The four pen squares,** which are the same square.

**How the last two stages split things:**

- **R4 beats R3.** At the "no 7" stage R3 loses its face + 7 route, and R4
  keeps face + 8.
- **DS, then purple's fast-track square, then R4.** Without the 9 and 10, DS
  is still one card, a 3. Purple's fast-track square needs 2 cards, with 3
  routes. R4 needs 2 cards, with 2 routes.

## The ranking

| square | no joker | no 6 | no 7 | no 4 | no J/Q/K | no 9/10 |
|---|---|---|---|---|---|---|
| rB3 | 0 / 1 | 0 / 1 | 0 / 1 | 0 / 1 | 0 / 1 | 0 / 1 |
| rB2 | 1 / 4 | 1 / 4 | 1 / 4 | 1 / 4 | 1 / 1 | 1 / 1 |
| rB1 | 1 / 5 | 1 / 5 | 1 / 5 | 1 / 5 | 1 / 1 | 1 / 1 |
| rDS | 1 / 2 | 1 / 2 | 1 / 2 | 1 / 2 | 1 / 1 | 1 / 1 |
| pFT | 1 / 2 | 1 / 2 | 1 / 2 | 1 / 2 | 1 / 1 | 2 / 3 |
| rR4 | 1 / 2 | 1 / 2 | 1 / 2 | 1 / 2 | 1 / 1 | 2 / 2 |
| rR3 | 1 / 2 | 1 / 2 | 1 / 1 | 1 / 1 | 1 / 1 | 1 / 1 |
| rR1 | 1 / 2 | 1 / 1 | 1 / 1 | 1 / 1 | 2 / 3 | 2 / 3 |
| rR2 | 1 / 2 | 1 / 1 | 2 / 25 | 2 / 22 | 2 / 2 | 2 / 2 |
| rR0 | 1 / 1 | 1 / 1 | 1 / 1 | 1 / 1 | 1 / 1 | 1 / 1 |
| gFT | 1 / 1 | 1 / 1 | 1 / 1 | 1 / 1 | 2 / 6 | 2 / 2 |
| pL4 | 1 / 1 | 1 / 1 | 1 / 1 | 1 / 1 | 2 / 6 | 2 / 2 |
| rBR | 1 / 1 | 1 / 1 | 1 / 1 | 1 / 1 | 2 / 3 | 2 / 3 |
| bullseye | 1 / 1 | 1 / 1 | 1 / 1 | 1 / 1 | - | - |
| bFT | 2 / 48 | 2 / 43 | 2 / 39 | 2 / 39 | 2 / 4 | 3 / 12 |
| pL3 | 2 / 48 | 2 / 43 | 2 / 39 | 2 / 39 | 2 / 4 | 3 / 12 |
| rFT | 2 / 44 | 2 / 38 | 2 / 34 | 2 / 34 | 2 / 4 | 2 / 2 |
| pL2 | 2 / 34 | 2 / 28 | 2 / 24 | 2 / 24 | 2 / 4 | 2 / 2 |
| gL4 | 2 / 31 | 2 / 29 | 2 / 27 | 2 / 27 | 3 / 12 | 3 / 2 |
| pL1 | 2 / 24 | 2 / 17 | 2 / 14 | 2 / 14 | 2 / 2 | 3 / 9 |
| pL0 | 2 / 22 | 2 / 14 | 2 / 10 | 2 / 10 | 2 / 2 | 3 / 7 |
| pHH | 2 / 22 | 2 / 14 | 2 / 7 | 2 / 7 | 2 / 1 | 2 / 1 |
| bL4 | 2 / 21 | 2 / 18 | 2 / 16 | 2 / 16 | 3 / 4 | 4 / 12 |
| pDS | 2 / 20 | 2 / 14 | 2 / 6 | 2 / 6 | 2 / 2 | 3 / 3 |
| rL4 | 2 / 18 | 2 / 15 | 2 / 13 | 2 / 13 | 3 / 4 | 3 / 2 |
| pBR | 2 / 16 | 2 / 14 | 2 / 8 | 2 / 8 | 2 / 3 | 3 / 6 |
| pR0 | 2 / 12 | 2 / 12 | 2 / 10 | 2 / 10 | 2 / 2 | 3 / 3 |
| pR1 | 2 / 9 | 2 / 9 | 2 / 9 | 2 / 8 | 2 / 1 | 4 / 31 |
| gL3 | 2 / 5 | 2 / 5 | 2 / 5 | 2 / 5 | 3 / 12 | 3 / 2 |
| pR2 | 2 / 5 | 2 / 5 | 2 / 5 | 2 / 4 | 3 / 21 | 3 / 3 |
| rHH | 2 / 5 | 2 / 3 | 2 / 2 | 3 / 60 | 4 / 16 | 4 / 6 |
| rL1 | 2 / 4 | 2 / 4 | 2 / 4 | 2 / 1 | 4 / 24 | 4 / 6 |
| rL0 | 2 / 4 | 2 / 3 | 2 / 3 | 2 / 1 | 3 / 4 | 3 / 2 |
| rL2 | 2 / 3 | 2 / 3 | 2 / 3 | 2 / 1 | 3 / 4 | 3 / 2 |
| gL2 | 2 / 2 | 2 / 2 | 2 / 2 | 2 / 2 | 3 / 13 | 3 / 2 |
| gR1 | 2 / 2 | 2 / 2 | 2 / 2 | 2 / 2 | 3 / 6 | 4 / 6 |
| gR0 | 2 / 2 | 2 / 2 | 2 / 2 | 2 / 2 | 3 / 6 | 4 / 4 |
| rL3 | 2 / 2 | 2 / 2 | 2 / 2 | 2 / 2 | 3 / 4 | 3 / 2 |
| gBR | 2 / 2 | 2 / 2 | 2 / 1 | 2 / 1 | 3 / 6 | 3 / 2 |
| gHH | 2 / 2 | 2 / 1 | 2 / 1 | 2 / 1 | 3 / 1 | 4 / 6 |
| gDS | 2 / 2 | 2 / 1 | 3 / 69 | 3 / 63 | 4 / 76 | 4 / 4 |
| pR3 | 2 / 1 | 2 / 1 | 2 / 1 | 2 / 1 | 3 / 15 | 4 / 18 |
| gL0 | 2 / 1 | 2 / 1 | 2 / 1 | 2 / 1 | 3 / 9 | 3 / 2 |
| gL1 | 2 / 1 | 2 / 1 | 2 / 1 | 2 / 1 | 3 / 6 | 4 / 6 |
| gR2 | 2 / 1 | 2 / 1 | 2 / 1 | 2 / 1 | 4 / 56 | 4 / 4 |
| pR4 | 3 / 374 | 3 / 269 | 3 / 203 | 3 / 189 | 3 / 12 | 4 / 16 |
| bL3 | 3 / 346 | 3 / 301 | 3 / 266 | 3 / 266 | 3 / 4 | 4 / 14 |
| bL2 | 3 / 221 | 3 / 190 | 3 / 164 | 3 / 164 | 3 / 4 | 4 / 12 |
| bR1 | 3 / 182 | 3 / 160 | 3 / 144 | 3 / 110 | 3 / 4 | 5 / 38 |
| bR2 | 3 / 152 | 3 / 132 | 3 / 118 | 3 / 71 | 4 / 24 | 5 / 24 |
| bDS | 3 / 142 | 3 / 65 | 3 / 20 | 3 / 20 | 4 / 8 | 5 / 30 |
| bBR | 3 / 139 | 3 / 105 | 3 / 40 | 3 / 40 | 3 / 4 | 4 / 12 |
| bR0 | 3 / 138 | 3 / 122 | 3 / 94 | 3 / 94 | 3 / 4 | 5 / 24 |
| bHH | 3 / 125 | 3 / 69 | 3 / 63 | 3 / 63 | 4 / 18 | 5 / 36 |
| bL1 | 3 / 106 | 3 / 93 | 3 / 79 | 3 / 79 | 4 / 30 | 5 / 48 |
| gR3 | 3 / 96 | 3 / 86 | 3 / 78 | 3 / 62 | 4 / 43 | 5 / 24 |
| bL0 | 3 / 81 | 3 / 73 | 3 / 65 | 3 / 65 | 3 / 4 | 4 / 12 |
| bR3 | 3 / 41 | 3 / 35 | 3 / 31 | 3 / 16 | 4 / 16 | 6 / 164 |
| gR4 | 3 / 34 | 3 / 28 | 3 / 24 | 3 / 24 | 4 / 40 | 4 / 4 |
| rHP1 | 3 / 8 | 3 / 3 | 3 / 3 | 3 / 1 | 4 / 4 | 4 / 2 |
| rHP2 | 3 / 8 | 3 / 3 | 3 / 3 | 3 / 1 | 4 / 4 | 4 / 2 |
| rHP3 | 3 / 8 | 3 / 3 | 3 / 3 | 3 / 1 | 4 / 4 | 4 / 2 |
| rHP4 | 3 / 8 | 3 / 3 | 3 / 3 | 3 / 1 | 4 / 4 | 4 / 2 |
| bR4 | 3 / 5 | 3 / 5 | 3 / 5 | 4 / 1610 | 4 / 16 | 5 / 24 |
