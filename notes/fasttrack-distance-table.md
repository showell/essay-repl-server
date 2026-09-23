# Fast Track: the computer's distance table

These tables are what the computer thinks every square is worth, for a red
piece. They are printed by `roc-apps/fasttrack/distance_table.roc` straight
from `Agent.routes`, the same code the computer plays on. Nothing here is
worked out by hand, so a wrong number here is a wrong number in the player.

**How to read a row.** `steps` is the steps left to red's deepest base
square, B4. `formula` counts the edges on the shortest way there, by kind.
`route` is that way, square by square.

- **Squares** are a zone letter and an id: `r` red (the mover), `b` blue (the
  next zone), `g` green, `p` purple (the zone before red's). The ids are the
  Elm code's:
  - `HP1`–`HP4`: the holding pen (all four are worth the same; the table
    shows HP1).
  - `L0`–`L4`: the side a piece leaves the pen onto. `L0` is the square a
    piece lands on when it comes out of the pen.
  - `FT`: the zone's fast-track square, at the end of that side.
  - `R4`–`R0`: the other side, walked from `R4` down to `R0`.
  - `BR`, `DS`, `HH`: the three squares across the bottom. `DS` is the door:
    a piece of the zone's own color turns from `DS` into its base, and every
    other piece walks on to `HH` and `L0`.
  - `B1`–`B4`: the base. `B4` is the deepest square, and "home" in this
    table.
- **Kinds of edge:**
  - `->` a walk: 1 step.
  - `=>` a fast-track hop, or entering the bullseye: `hop` steps. Both need
    the move to end exactly on a fast-track square.
  - `~>` leaving the pen: `1 + pen` steps, the wait for an A, 6 or joker.
    Leaving the bullseye is also `~>`: `1 + 6` steps, the wait for a J, Q
    or K.
  - `<-` a 4 played backwards: `back4` steps. It only counts when it lands
    the piece in its own home stretch, R4 to DS.

The rows run in the order a lap visits them: red's pen, red's L0 to FT, then
blue's, green's and purple's zones from R4 round to FT, then red's home
stretch and base, and last the bullseye.

## Things to check

- **Your two squares.** Six past the pen without the bullseye is `bR4`:
  26 = 24 + 2·hop, which is 13 to blue's FT, then 13 home. Landing on the
  fast track instead is `bFT`: 13 = 11 + 2·hop.
- **The pen, in the first table: 24.** That is better than `bR4`'s 26, so a
  piece in the pen scores better than one out and stuck. That is the missing
  penalty you pointed out.
- **The 4 played backwards, in the second table.** `rL0` becomes 7 (back to
  `rR0`, then 6 home), `rL1` 6 and `rL2` 5, and the pen falls to 12. Then
  there is a cliff: `rL3` is 16, because from there a 4 back no longer
  reaches red's home stretch.
- **What `back4` should cost** is open. Here it is 1, the move alone, with no
  allowance for waiting for a 4 to turn up.

## The race so far

A bigger pen wait, on the first table (no 4 played backwards), has only made
the computer lose. Each value below was raced against pen 4, 200 games:
pen 7 won 50.0%, pen 11 48.0%, pen 15 43.0%, pen 23 39.0%.

The second table has not been raced yet.

## Table 1: the computer today

hop 1, pen 4, back4 off

| square | steps | formula | route |
|---|---|---|---|
| rHP1 | 24 | 16 + 3·hop + (1 + pen) | rHP1 ~> rL0 -> rL1 -> rL2 -> rL3 -> rL4 -> rFT => bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| rL0 | 19 | 16 + 3·hop | rL0 -> rL1 -> rL2 -> rL3 -> rL4 -> rFT => bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| rL1 | 18 | 15 + 3·hop | rL1 -> rL2 -> rL3 -> rL4 -> rFT => bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| rL2 | 17 | 14 + 3·hop | rL2 -> rL3 -> rL4 -> rFT => bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| rL3 | 16 | 13 + 3·hop | rL3 -> rL4 -> rFT => bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| rL4 | 15 | 12 + 3·hop | rL4 -> rFT => bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| rFT | 14 | 11 + 3·hop | rFT => bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| bR4 | 26 | 24 + 2·hop | bR4 -> bR3 -> bR2 -> bR1 -> bR0 -> bBR -> bDS -> bHH -> bL0 -> bL1 -> bL2 -> bL3 -> bL4 -> bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| bR3 | 25 | 23 + 2·hop | bR3 -> bR2 -> bR1 -> bR0 -> bBR -> bDS -> bHH -> bL0 -> bL1 -> bL2 -> bL3 -> bL4 -> bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| bR2 | 24 | 22 + 2·hop | bR2 -> bR1 -> bR0 -> bBR -> bDS -> bHH -> bL0 -> bL1 -> bL2 -> bL3 -> bL4 -> bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| bR1 | 23 | 21 + 2·hop | bR1 -> bR0 -> bBR -> bDS -> bHH -> bL0 -> bL1 -> bL2 -> bL3 -> bL4 -> bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| bR0 | 22 | 20 + 2·hop | bR0 -> bBR -> bDS -> bHH -> bL0 -> bL1 -> bL2 -> bL3 -> bL4 -> bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| bBR | 21 | 19 + 2·hop | bBR -> bDS -> bHH -> bL0 -> bL1 -> bL2 -> bL3 -> bL4 -> bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| bDS | 20 | 18 + 2·hop | bDS -> bHH -> bL0 -> bL1 -> bL2 -> bL3 -> bL4 -> bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| bHH | 19 | 17 + 2·hop | bHH -> bL0 -> bL1 -> bL2 -> bL3 -> bL4 -> bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| bL0 | 18 | 16 + 2·hop | bL0 -> bL1 -> bL2 -> bL3 -> bL4 -> bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| bL1 | 17 | 15 + 2·hop | bL1 -> bL2 -> bL3 -> bL4 -> bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| bL2 | 16 | 14 + 2·hop | bL2 -> bL3 -> bL4 -> bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| bL3 | 15 | 13 + 2·hop | bL3 -> bL4 -> bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| bL4 | 14 | 12 + 2·hop | bL4 -> bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| bFT | 13 | 11 + 2·hop | bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| gR4 | 25 | 24 + 1·hop | gR4 -> gR3 -> gR2 -> gR1 -> gR0 -> gBR -> gDS -> gHH -> gL0 -> gL1 -> gL2 -> gL3 -> gL4 -> gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| gR3 | 24 | 23 + 1·hop | gR3 -> gR2 -> gR1 -> gR0 -> gBR -> gDS -> gHH -> gL0 -> gL1 -> gL2 -> gL3 -> gL4 -> gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| gR2 | 23 | 22 + 1·hop | gR2 -> gR1 -> gR0 -> gBR -> gDS -> gHH -> gL0 -> gL1 -> gL2 -> gL3 -> gL4 -> gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| gR1 | 22 | 21 + 1·hop | gR1 -> gR0 -> gBR -> gDS -> gHH -> gL0 -> gL1 -> gL2 -> gL3 -> gL4 -> gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| gR0 | 21 | 20 + 1·hop | gR0 -> gBR -> gDS -> gHH -> gL0 -> gL1 -> gL2 -> gL3 -> gL4 -> gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| gBR | 20 | 19 + 1·hop | gBR -> gDS -> gHH -> gL0 -> gL1 -> gL2 -> gL3 -> gL4 -> gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| gDS | 19 | 18 + 1·hop | gDS -> gHH -> gL0 -> gL1 -> gL2 -> gL3 -> gL4 -> gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| gHH | 18 | 17 + 1·hop | gHH -> gL0 -> gL1 -> gL2 -> gL3 -> gL4 -> gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| gL0 | 17 | 16 + 1·hop | gL0 -> gL1 -> gL2 -> gL3 -> gL4 -> gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| gL1 | 16 | 15 + 1·hop | gL1 -> gL2 -> gL3 -> gL4 -> gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| gL2 | 15 | 14 + 1·hop | gL2 -> gL3 -> gL4 -> gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| gL3 | 14 | 13 + 1·hop | gL3 -> gL4 -> gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| gL4 | 13 | 12 + 1·hop | gL4 -> gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| gFT | 12 | 11 + 1·hop | gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| pR4 | 24 | 24 | pR4 -> pR3 -> pR2 -> pR1 -> pR0 -> pBR -> pDS -> pHH -> pL0 -> pL1 -> pL2 -> pL3 -> pL4 -> pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| pR3 | 23 | 23 | pR3 -> pR2 -> pR1 -> pR0 -> pBR -> pDS -> pHH -> pL0 -> pL1 -> pL2 -> pL3 -> pL4 -> pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| pR2 | 22 | 22 | pR2 -> pR1 -> pR0 -> pBR -> pDS -> pHH -> pL0 -> pL1 -> pL2 -> pL3 -> pL4 -> pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| pR1 | 21 | 21 | pR1 -> pR0 -> pBR -> pDS -> pHH -> pL0 -> pL1 -> pL2 -> pL3 -> pL4 -> pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| pR0 | 20 | 20 | pR0 -> pBR -> pDS -> pHH -> pL0 -> pL1 -> pL2 -> pL3 -> pL4 -> pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| pBR | 19 | 19 | pBR -> pDS -> pHH -> pL0 -> pL1 -> pL2 -> pL3 -> pL4 -> pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| pDS | 18 | 18 | pDS -> pHH -> pL0 -> pL1 -> pL2 -> pL3 -> pL4 -> pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| pHH | 17 | 17 | pHH -> pL0 -> pL1 -> pL2 -> pL3 -> pL4 -> pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| pL0 | 16 | 16 | pL0 -> pL1 -> pL2 -> pL3 -> pL4 -> pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| pL1 | 15 | 15 | pL1 -> pL2 -> pL3 -> pL4 -> pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| pL2 | 14 | 14 | pL2 -> pL3 -> pL4 -> pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| pL3 | 13 | 13 | pL3 -> pL4 -> pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| pL4 | 12 | 12 | pL4 -> pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| pFT | 11 | 11 | pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| rR4 | 10 | 10 | rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| rR3 | 9 | 9 | rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| rR2 | 8 | 8 | rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| rR1 | 7 | 7 | rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| rR0 | 6 | 6 | rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| rBR | 5 | 5 | rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| rDS | 4 | 4 | rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| rB1 | 3 | 3 | rB1 -> rB2 -> rB3 -> rB4 |
| rB2 | 2 | 2 | rB2 -> rB3 -> rB4 |
| rB3 | 1 | 1 | rB3 -> rB4 |
| rB4 | 0 | 0 | rB4 |
| bullseye | 18 | 11 + (1 + 6) | bullseye ~> pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |## With the 4 played backwards (Steve)

hop 1, pen 4, back4 1

| square | steps | formula | route |
|---|---|---|---|
| rHP1 | 12 | 6 + (1 + pen) + 1·back4 | rHP1 ~> rL0 <- rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| rL0 | 7 | 6 + 1·back4 | rL0 <- rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| rL1 | 6 | 5 + 1·back4 | rL1 <- rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| rL2 | 5 | 4 + 1·back4 | rL2 <- rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| rL3 | 16 | 13 + 3·hop | rL3 -> rL4 -> rFT => bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| rL4 | 15 | 12 + 3·hop | rL4 -> rFT => bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| rFT | 14 | 11 + 3·hop | rFT => bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| bR4 | 26 | 24 + 2·hop | bR4 -> bR3 -> bR2 -> bR1 -> bR0 -> bBR -> bDS -> bHH -> bL0 -> bL1 -> bL2 -> bL3 -> bL4 -> bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| bR3 | 25 | 23 + 2·hop | bR3 -> bR2 -> bR1 -> bR0 -> bBR -> bDS -> bHH -> bL0 -> bL1 -> bL2 -> bL3 -> bL4 -> bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| bR2 | 24 | 22 + 2·hop | bR2 -> bR1 -> bR0 -> bBR -> bDS -> bHH -> bL0 -> bL1 -> bL2 -> bL3 -> bL4 -> bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| bR1 | 23 | 21 + 2·hop | bR1 -> bR0 -> bBR -> bDS -> bHH -> bL0 -> bL1 -> bL2 -> bL3 -> bL4 -> bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| bR0 | 22 | 20 + 2·hop | bR0 -> bBR -> bDS -> bHH -> bL0 -> bL1 -> bL2 -> bL3 -> bL4 -> bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| bBR | 21 | 19 + 2·hop | bBR -> bDS -> bHH -> bL0 -> bL1 -> bL2 -> bL3 -> bL4 -> bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| bDS | 20 | 18 + 2·hop | bDS -> bHH -> bL0 -> bL1 -> bL2 -> bL3 -> bL4 -> bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| bHH | 19 | 17 + 2·hop | bHH -> bL0 -> bL1 -> bL2 -> bL3 -> bL4 -> bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| bL0 | 18 | 16 + 2·hop | bL0 -> bL1 -> bL2 -> bL3 -> bL4 -> bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| bL1 | 17 | 15 + 2·hop | bL1 -> bL2 -> bL3 -> bL4 -> bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| bL2 | 16 | 14 + 2·hop | bL2 -> bL3 -> bL4 -> bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| bL3 | 15 | 13 + 2·hop | bL3 -> bL4 -> bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| bL4 | 14 | 12 + 2·hop | bL4 -> bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| bFT | 13 | 11 + 2·hop | bFT => gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| gR4 | 25 | 24 + 1·hop | gR4 -> gR3 -> gR2 -> gR1 -> gR0 -> gBR -> gDS -> gHH -> gL0 -> gL1 -> gL2 -> gL3 -> gL4 -> gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| gR3 | 24 | 23 + 1·hop | gR3 -> gR2 -> gR1 -> gR0 -> gBR -> gDS -> gHH -> gL0 -> gL1 -> gL2 -> gL3 -> gL4 -> gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| gR2 | 23 | 22 + 1·hop | gR2 -> gR1 -> gR0 -> gBR -> gDS -> gHH -> gL0 -> gL1 -> gL2 -> gL3 -> gL4 -> gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| gR1 | 22 | 21 + 1·hop | gR1 -> gR0 -> gBR -> gDS -> gHH -> gL0 -> gL1 -> gL2 -> gL3 -> gL4 -> gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| gR0 | 21 | 20 + 1·hop | gR0 -> gBR -> gDS -> gHH -> gL0 -> gL1 -> gL2 -> gL3 -> gL4 -> gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| gBR | 20 | 19 + 1·hop | gBR -> gDS -> gHH -> gL0 -> gL1 -> gL2 -> gL3 -> gL4 -> gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| gDS | 19 | 18 + 1·hop | gDS -> gHH -> gL0 -> gL1 -> gL2 -> gL3 -> gL4 -> gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| gHH | 18 | 17 + 1·hop | gHH -> gL0 -> gL1 -> gL2 -> gL3 -> gL4 -> gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| gL0 | 17 | 16 + 1·hop | gL0 -> gL1 -> gL2 -> gL3 -> gL4 -> gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| gL1 | 16 | 15 + 1·hop | gL1 -> gL2 -> gL3 -> gL4 -> gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| gL2 | 15 | 14 + 1·hop | gL2 -> gL3 -> gL4 -> gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| gL3 | 14 | 13 + 1·hop | gL3 -> gL4 -> gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| gL4 | 13 | 12 + 1·hop | gL4 -> gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| gFT | 12 | 11 + 1·hop | gFT => pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| pR4 | 24 | 24 | pR4 -> pR3 -> pR2 -> pR1 -> pR0 -> pBR -> pDS -> pHH -> pL0 -> pL1 -> pL2 -> pL3 -> pL4 -> pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| pR3 | 23 | 23 | pR3 -> pR2 -> pR1 -> pR0 -> pBR -> pDS -> pHH -> pL0 -> pL1 -> pL2 -> pL3 -> pL4 -> pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| pR2 | 22 | 22 | pR2 -> pR1 -> pR0 -> pBR -> pDS -> pHH -> pL0 -> pL1 -> pL2 -> pL3 -> pL4 -> pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| pR1 | 21 | 21 | pR1 -> pR0 -> pBR -> pDS -> pHH -> pL0 -> pL1 -> pL2 -> pL3 -> pL4 -> pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| pR0 | 20 | 20 | pR0 -> pBR -> pDS -> pHH -> pL0 -> pL1 -> pL2 -> pL3 -> pL4 -> pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| pBR | 19 | 19 | pBR -> pDS -> pHH -> pL0 -> pL1 -> pL2 -> pL3 -> pL4 -> pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| pDS | 18 | 18 | pDS -> pHH -> pL0 -> pL1 -> pL2 -> pL3 -> pL4 -> pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| pHH | 17 | 17 | pHH -> pL0 -> pL1 -> pL2 -> pL3 -> pL4 -> pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| pL0 | 16 | 16 | pL0 -> pL1 -> pL2 -> pL3 -> pL4 -> pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| pL1 | 15 | 15 | pL1 -> pL2 -> pL3 -> pL4 -> pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| pL2 | 14 | 14 | pL2 -> pL3 -> pL4 -> pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| pL3 | 13 | 13 | pL3 -> pL4 -> pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| pL4 | 12 | 12 | pL4 -> pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| pFT | 11 | 11 | pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| rR4 | 10 | 10 | rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| rR3 | 9 | 9 | rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| rR2 | 8 | 8 | rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| rR1 | 7 | 7 | rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| rR0 | 6 | 6 | rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| rBR | 5 | 5 | rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| rDS | 4 | 4 | rDS -> rB1 -> rB2 -> rB3 -> rB4 |
| rB1 | 3 | 3 | rB1 -> rB2 -> rB3 -> rB4 |
| rB2 | 2 | 2 | rB2 -> rB3 -> rB4 |
| rB3 | 1 | 1 | rB3 -> rB4 |
| rB4 | 0 | 0 | rB4 |
| bullseye | 18 | 11 + (1 + 6) | bullseye ~> pFT -> rR4 -> rR3 -> rR2 -> rR1 -> rR0 -> rBR -> rDS -> rB1 -> rB2 -> rB3 -> rB4 |