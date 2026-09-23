# Fast Track: the fewest cards home

For a red piece on an empty board: how few cards take it from each square to
red's B4, and which cards start such a way. It is worked back from B4 over
every card's landing squares, as the rules compute them
(`roc-apps/fasttrack/Reach.roc`). This page is printed by
`fasttrack/reach_board.roc`.

**What it assumes.**

- **No opponents,** so nothing blocks a piece and nothing sends one home.
- **One card is one card.** Cards that let you play again are not credited
  yet.
- **Each card moves the way the rules allow,** and a 7 is only ever played
  whole:

| card | what it does here |
|---|---|
| A, J, Q, K, joker | move 1 |
| 4 | backwards only ("4 back") |
| 6 from the pen | one square, onto L0 |
| 7 | seven squares (a split needs a second piece) |
| A, 6, joker | the only cards that leave the pen |
| J, Q, K | the only cards that leave the bullseye |

- **The fast track and the bullseye need exact moves.** A fast-track hop happens only
  on a move that starts on a fast-track square. The bullseye is entered only
  from red's own fast-track square.

**How to read a square.** `L2 3 · 3, 4 back` means that from L2 the fewest
cards home is 3, and a 3 or a 4 played backwards starts a 3-card way. Each zone is
drawn upright, the way the page draws its panel, with the pen at the left and
the base up the middle. The other zones' pens and bases are left blank,
because a red piece never stands on them.

## Things to check

- **DS is 2, not 1.** It is 4 steps from B4, and no card moves 4 forward.
  Any of A, 2, 3, J, Q, K, joker or a 4 back starts a 2-card way.
- **So L2 is 3.** A 4 back from L2 lands on DS. L0 (to R0) and L1 (to BR)
  are 2, as you expected, and so is red's HH (to R1).
- **Red's fast-track square is 2:** any card from 5 to 9, hopping to purple's
  fast-track square and on into red's home stretch.
- **The pen is 3** (A, 6 or joker to L0, then 2), and so is the bullseye
  (J, Q or K to purple's fast-track square, then 2).
- **The worst squares on the board are 4 cards from home:** blue's R2–R4
  and L1, and green's R2–R4. The rest of enemy territory is 3, except
  purple's zone, the last before red's: its L side, bottom row and
  fast-track square are 2, and only its R side is 3.

### Red's zone (the mover's own)

| | | | | | |
|---|---|---|---|---|---|
|  | **FT** 2 · 5, 6, 7, 8, 9 |  |  |  |  |
|  | **L4** 3 · A, 4 back, J, Q, K, Jo |  | **B4** 0 |  | **R4** 1 · 10 |
|  | **L3** 3 · 2, 4 back |  | **B3** 1 · A, J, Q, K, Jo |  | **R3** 1 · 9 |
|  | **L2** 3 · 3, 4 back |  | **B2** 1 · 2 |  | **R2** 1 · 8 |
| **pen** 3 · A, 6, Jo | **L1** 2 · 4 back |  | **B1** 1 · 3 |  | **R1** 1 · 7 |
|  | **L0** 2 · 4 back | **HH** 2 · 4 back | **DS** 2 · A, 2, 3, 4 back, J, Q, K, Jo | **BR** 1 · 5 | **R0** 1 · 6 |

### Blue's zone (next after red's)

| | | | | | |
|---|---|---|---|---|---|
|  | **FT** 2 · 3, 5, 6, 7, 8, 10 |  |  |  |  |
|  | **L4** 3 · A, J, Q, K, Jo |  |  |  | **R4** 4 · 3, 4 back, 5, 6, 7, 8, 10 |
|  | **L3** 3 · 2 |  |  |  | **R3** 4 · 2, 3, 4 back, 5, 6, 7, 9, 10 |
|  | **L2** 3 · 3 |  |  |  | **R2** 4 · A, 2, 3, 4 back, 5, 6, 8, 9, 10, J, Q, K, Jo |
|  | **L1** 4 · A, 2, 3, 4 back, 8, 9, 10, J, Q, K, Jo |  |  |  | **R1** 3 · 4 back, 10 |
|  | **L0** 3 · 5 | **HH** 3 · 6 | **DS** 3 · 7 | **BR** 3 · 8 | **R0** 3 · 9 |

### Green's zone

| | | | | | |
|---|---|---|---|---|---|
|  | **FT** 2 · 2, 3, 5, 6, 7, 9, 10 |  |  |  |  |
|  | **L4** 3 · A, 6, 7, 8, 9, 10, J, Q, K, Jo |  |  |  | **R4** 4 · 3, 4 back, 5, 6, 7, 8, 9, 10 |
|  | **L3** 3 · 2, 7, 8, 9, 10 |  |  |  | **R3** 4 · 2, 3, 4 back, 5, 6, 7, 8, 9, 10 |
|  | **L2** 3 · 3, 8, 9, 10 |  |  |  | **R2** 4 · A, 2, 3, 4 back, 5, 6, 7, 8, 9, 10, J, Q, K, Jo |
|  | **L1** 3 · 9, 10 |  |  |  | **R1** 3 · 4 back, 10 |
|  | **L0** 3 · 5, 10 | **HH** 3 · 6 | **DS** 3 · 7 | **BR** 3 · 8 | **R0** 3 · 9 |

### Purple's zone (the one before red's)

| | | | | | |
|---|---|---|---|---|---|
|  | **FT** 2 · A, 2, 3, 5, 6, 8, 9, 10, J, Q, K, Jo |  |  |  |  |
|  | **L4** 2 · 2, 3, 5, 6, 7, 9, 10 |  |  |  | **R4** 3 · 5, 6, 7, 8, 9, 10 |
|  | **L3** 2 · 3, 5, 6, 7, 8, 10 |  |  |  | **R3** 3 · 3, 5, 6, 7, 8, 9, 10 |
|  | **L2** 2 · 5, 6, 7, 8, 9 |  |  |  | **R2** 3 · 2, 3, 5, 6, 7, 8, 9, 10 |
|  | **L1** 2 · 5, 6, 7, 8, 9, 10 |  |  |  | **R1** 3 · A, 2, 3, 4 back, 5, 6, 7, 8, 9, 10, J, Q, K, Jo |
|  | **L0** 2 · 6, 7, 8, 9, 10 | **HH** 2 · 7, 8, 9, 10 | **DS** 2 · 8, 9, 10 | **BR** 2 · 9, 10 | **R0** 2 · 10 |

### The bullseye

**bullseye** 3 · J, Q, K
