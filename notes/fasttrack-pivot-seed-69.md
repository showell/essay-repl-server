# Fast Track: where playing to win lost (seed 69)

The 80-game run of "own less the leader" against the champion had 9 games
that red won only as the champion. This note takes one of them, seed 69,
apart. A short table of the other eight is at the end.

**How it was run** (`fasttrack/exp_pivot.roc`):

- Red plays seed 69 twice: once as the **champion** (its own pieces only) and
  once as the **chaser**. The chaser scores its own pieces less the leading
  opponent's, at the end of its turn.
- Blue, green and purple play the champion in both games.
- Each player's deck is shuffled once from the seed, so both games deal the
  same cards in the same order.
- The two games are identical until red's two strategies first choose
  differently. That position is the **pivot**.

Board values are each player's own, as the champion values its pieces:
Steve's square ranking (100 points a place) plus the base bonus of 1000 a
step.

## Who won

| red plays as | winner | red home on |
|---|---|---|
| the champion | **red**, on turn 10 | turn 10 |
| the chaser | **blue**, on turn 17 | turn 18 |

## The pivot: red's turn 6

Red holds **7 2 9 6 6**. Board values before the turn:

| red | blue | green | purple |
|---|---|---|---|
| 15600 | 5500 | 5700 | **18400** (the leader) |

Both strategies play the same cards: a 6 brings a piece out of red's pen to
L0, and then the 7 is split. The only difference is **how the 7 splits**:

- **The champion splits it 5 + 2.** The piece on R0 goes 5 into base, to
  **B3**. The new piece goes 2, to L2.
- **The chaser splits it 2 + 5.** R0 goes 2, to **DS**. The new piece goes 5,
  to red's **fast-track square**, where purple's piece is standing, and
  purple's piece goes back to its pen.

For the two players in the capture, red and purple:

| | red | purple |
|---|---|---|
| before | 15600 | 18400 |
| champion's pick (B3, L2) | 21100 (**+5500**) | 18400 (0) |
| chaser's pick (DS, FT, capture) | 20300 (**+4700**) | 13000 (**−5400**) |

So the capture costs red 800 of its own value and takes 5400 off purple.

**How each strategy scores the two lines:**

- **The champion** scores red's own value (plus a hoarded hand, the same in
  both lines here): 21100 against 20300, so it tucks into B3.
- **The chaser** subtracts the leader's value. The capture puts purple at
  13000, still the leader, since blue and green are at 5500 and 5700. So it
  scores 21100 − 18400 = **2700** against 20300 − 13000 = **7300**, and
  captures.

### Every line red had

All 30 lines of red's turn 6, sorted by the champion's score. Each pair of
rows with the same squares is one position the search failed to merge;
that is a separate issue, covered at the end.

| line | pieces | red | purple (leader) | others | champion's score | chaser's score |
|---|---|---|---|---|---|---|
| **champion's pick** | red@red.R0 red@red.HP2 -> red@red.B3 red@red.L2 | +5500 | 0 |  | **21100** | 2700 |
|  | red@red.R0 red@red.HP2 -> red@red.L2 red@red.B3 | +5500 | 0 |  | 21100 | 2700 |
|  | red@red.R0 red@red.HP2 -> red@red.B1 red@red.L4 | +5200 | 0 |  | 20800 | 2400 |
|  | red@red.R0 red@red.HP2 -> red@red.L4 red@red.B1 | +5200 | 0 |  | 20800 | 2400 |
|  | red@red.R0 red@red.HP2 -> red@red.B2 red@red.L3 | +4700 | 0 |  | 20300 | 1900 |
|  | red@red.R0 red@red.HP2 -> red@red.L3 red@red.B2 | +4700 | 0 |  | 20300 | 1900 |
| **chaser's pick** | purple@red.FT red@red.R0 red@red.HP2 -> red@red.FT purple@purple.HP2 red@red.DS | +4700 | **−5400** |  | 20300 | **7300** |
|  | red@red.R0 red@red.HP2 -> red@red.B3 red@blue.R2 | +4700 | 0 |  | 20300 | 1900 |
|  | red@red.R0 red@red.HP2 -> red@blue.R2 red@red.B3 | +4700 | 0 |  | 20300 | 1900 |
|  | red@red.R0 red@red.HP2 -> red@red.B2 red@blue.R1 | +4600 | 0 |  | 20200 | 1800 |
|  | red@red.R0 red@red.HP2 -> red@blue.R1 red@red.B2 | +4600 | 0 |  | 20200 | 1800 |
|  | red@red.R0 red@red.HP2 -> red@bullseye red@red.BR | +4300 | 0 |  | 19900 | 1500 |
|  | red@red.R0 red@red.HP2 -> red@red.DS red@bullseye | +4200 | 0 |  | 19800 | 1400 |
|  | blue@blue.R0 red@red.R0 red@red.HP2 -> red@red.B1 red@blue.R0 blue@blue.HP4 | +3100 | 0 | blue −5500 | 18700 | 300 |
|  | blue@blue.R0 red@red.R0 red@red.HP2 -> red@blue.R0 blue@blue.HP4 red@red.B1 | +3100 | 0 | blue −5500 | 18700 | 300 |
|  | red@red.R0 red@red.HP2 -> red@red.DS red@red.L0 | +2900 | 0 |  | 18500 | 100 |
|  | red@red.HP2 -> red@blue.R1 | +2200 | 0 |  | 17800 | −600 |
|  | red@red.HP2 -> red@red.L2 | +2000 | 0 |  | 17600 | −800 |
|  | red@red.R0 red@red.HP2 -> red@red.DS red@blue.BR | +1700 | 0 |  | 17300 | −1100 |
|  | red@red.R0 red@red.HP2 -> red@blue.BR red@red.DS | +1700 | 0 |  | 17300 | −1100 |
|  | red@red.R0 red@red.HP2 -> red@red.BR red@blue.DS | +1500 | 0 |  | 17100 | −1300 |
|  | red@red.R0 red@red.HP2 -> red@blue.DS red@red.BR | +1500 | 0 |  | 17100 | −1300 |
|  | red@red.HP2 -> red@blue.R2 | +1200 | 0 |  | 16800 | −1600 |
|  | red@red.HP2 -> red@blue.HH | +1000 | 0 |  | 16600 | −1800 |
|  | red@red.HP2 -> red@blue.L1 | +700 | 0 |  | 16300 | −2100 |
|  | red@red.HP2 -> red@blue.R3 | +300 | 0 |  | 15900 | −2500 |
|  | red@red.R0 red@red.HP2 -> red@red.BR red@blue.R4 | +300 | 0 |  | 15900 | −2500 |
|  | red@red.R0 red@red.HP2 -> red@blue.R4 red@red.BR | +300 | 0 |  | 15900 | −2500 |
|  | red@red.R0 red@red.HP2 -> red@red.DS red@blue.R4 | +200 | 0 |  | 15800 | −2600 |
|  | red@red.R0 -> red@red.DS | +100 | 0 |  | 15700 | −2700 |

One line captures **blue** instead, costing blue 5500. The chaser scores it
only 300: blue is not the leader, so taking blue's piece is worth nothing to
it.

## What happened next

Board values at the start of each of red's turns, and every capture.

**Red as the champion:**

| red's turn | red | blue | green | purple | |
|---|---|---|---|---|---|
| 7 | 21100 | 15600 | 12900 | 19500 | |
| 8 | 26500 | 19100 | 16800 | 20100 | red captures purple |
| 9 | 28700 | 19100 | 19500 | 19100 | |
| 10 | 32500 | 19100 | 23000 | 19100 | **red home: red wins** |

**Red as the chaser:**

| red's turn | red | blue | green | purple | |
|---|---|---|---|---|---|
| 7 | 20300 | 15600 | 12900 | 12400 | |
| 8 | 24900 | 19100 | 16800 | 12000 | **purple captures red** |
| 9 | 21900 | 19100 | 19500 | 14200 | |
| 10 | 27400 | 19100 | 23000 | 18000 | |
| 11 | 28700 | 21900 | 23200 | 19100 | |
| 12 | 26500 | 24500 | 23200 | 19100 | |
| 13 | 29400 | 27000 | 25500 | 19100 | **green captures red** |
| 14 | 27000 | 29300 | 29200 | 21900 | |
| 15 | 27000 | 31600 | 31800 | 23700 | |
| 16 | 27000 | 32700 | 31600 | 27000 | |
| 17 | 29800 | 32200 | 32600 | 27000 | **blue home: blue wins** |
| 18 | 30900 | 33800 | 32400 | 31600 | red home |

## Reading it

1. **The capture came instead of a piece tucked into base.** The champion put
   a piece on B3, where no one can touch it. The chaser left red's pieces on DS
   and the fast-track square. Purple's pieces pass through red's zone on their
   way home.
2. **The capture was paid back almost at once.** Two turns later purple
   captured red. Red went from 24900 to 21900, and red's lead over the field
   was gone by turn 14. Green captured red again on turn 13, and red sat at
   27000 for three turns while blue and green went past.
3. **The champion took purple anyway, and for free.** On turn 8, as the
   champion, red captured purple in passing, as part of its own best play.
   The chaser paid for a capture the champion got two turns later at no cost.
4. **The capture did not stop the leader from winning, because the leader
   changed.** Purple was the leader at the pivot; it never threatened again.
   Blue, 5500 at the pivot and ignored by the chaser, won.

**A caveat on cause.** After the pivot the two games differ, and every later
move is the champion's best play in a different position. The cards come in
the same order, but they meet different boards. So the rest of each game is
not caused by the pivot alone. What the pivot shows cleanly is the trade: red
gave up a safe B3 for a capture that left two pieces exposed in an opponent's
path.

## The other eight games

The first point where red's two strategies part, and who won each game.

| seed | red's turn | champion's pick | chaser's pick (red / the leader) | winner, red as champion | winner, red as chaser |
|---|---|---|---|---|---|
| 74 | 3 | a piece to B1, keeping the A (+1400) | captures green's only piece out, at green's DS (+2800 / −5600), spending the hoarded A | red, turn 10 | green, turn 14 |
| 21 | 8 | a piece to B2 (+3700) | captures blue on blue's R0 (+1800 / −5500) | red, turn 12 | purple, turn 15 |
| 22 | 2 | B1 and a piece out (+8400) | captures blue at BR, and a J trade sends green back (+5100 / −5700) | red, turn 10 | purple, turn 18 |
| 43 | 3 | a piece to R3 (−300) | green's piece to its pen with no red piece moving (0 / −2800) | red, turn 16 | purple, turn 18 |
| 55 | 2 | out, to FT (+4600) | out, onto purple at the bullseye (+4100 / −4100) | red, turn 14 | green, turn 17 |
| 60 | 4 | out, to R0 (+5500) | captures blue on blue's FT (+3100 / −4600) | red, turn 10 | blue, turn 13 |
| 76 | 6 | B2, capturing purple on the way (+3800) | captures blue on blue's R0 (−1000 / −5500) | red, turn 14 | blue, turn 15 |
| 79 | 2 | a piece to R3 (−800) | J trade with green's piece at the bullseye (−1600 / −2600) | red, turn 12 | green, turn 15 |

The same pattern shows up in most of them: a base square or a safe advance
given up for a capture of the leader. The winner is usually a player the
chaser was not chasing at the pivot: in 5 of these 9 games someone other than
the pivot's leader won.

**Seed 43 looks wrong.** The chaser's line sends green's piece home while
every red piece ends where it started. With K J J 3 3 there might be a legal
sequence, a J trade and back, but I have not worked it out. It is worth
checking before trusting anything that involves the J.

**The search does not merge identical positions.** The seed 69 table lists
the same squares twice in reverse order: red to B3 and L2, then red to L2 and
B3. The search merges lines by comparing the whole game record, and these two
probably differ only in the order the pieces are listed. If so, it changes no
decision but multiplies the work. Seed 74 had 1,257 lines. This is the first
thing to measure for speed.
