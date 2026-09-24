# Fast Track in Roc

Fast Track is the marble race: four players, a deck of cards each, and pieces
that leave a pen, circle the board and come home to a base of four squares.
The first player with all four pieces home wins. This version runs in the
browser as Roc compiled to WebAssembly. You play red; the computer plays blue,
green and purple.

It was ported from Steve's Elm implementation,
[showell/elm-fasttrack](https://github.com/showell/elm-fasttrack). The rules
module by module, the undo, the page's geometry and Elm's random numbers came
across whole. The computer players are new.

The page: https://roc.lynrummy.com/fasttrack/ (the code:
[roc-apps/fasttrack](https://github.com/showell/roc-apps/tree/master/fasttrack)).

## The rules

Each Elm module has a Roc module of the same name and the same functions:
`Piece`, `LegalMove`, `Player`, `Move`, `Game`, `Setup`, `History`. Elm's
tests are Roc tests. Two libraries are ported rather than replaced, because
their behaviour reaches the game: elm/random, to the bit, so the random
numbers are Elm's, and assoc-list's ordered dictionary.

A few rules are this game's own:

- **Every player has a deck**, shuffled once from the game's seed and the
  player's seat. Nothing one player draws changes another's cards, so a seed
  deals every player the same cards whatever anyone plays.
- **Four discards bring a piece out** of the pen when a player cannot play.
- **Partnerships** follow pagat.com's rules, with a second style in which a
  partner's pieces become yours only once your own are home. The rules and the
  checks cover them; the page offers one game, red against three computers.

## The board is 89 numbers

A zone has 22 squares: four in the pen, four in the base, and fourteen of
track. Four zones and the bullseye make 89. Squares are numbered from red's
side, zone by zone, and the board is a list of 89 small numbers saying who
stands on each.

**The rules are written once, as red sees them.** Every color sees the same
board from its own zone, so a table turns any square into the number red
would give it, and back. The routes a piece can take -- round the track,
into its own base from its own DS square, across the fast track, into and out
of the bullseye -- are laid out once for red and precomputed: for every
square, every walk of one to ten steps. A move is a lookup in that table and
a check that the walk passes no piece of the mover's own color.

Names like `blue.R4` exist only at the edges: the page, the click codes and
the tests.

## The page

**Roc answers the whole page as data.** The board is 89 slots in a fixed
order, each a centre, a size, a fill and a piece; the page draws them once as
SVG and afterwards changes only the attributes that differ. The rest of the
page -- the hand, the instructions, a few buttons -- is a flat list of nodes,
rebuilt on every click. A click carries the number Roc gave the thing clicked,
and the page hands it straight back to Roc. The JavaScript knows no rule and
no color. The code that reads Roc's values out of WebAssembly memory is
generated from the platform's types by a glue script.

**The computer plays through the page's clock.** In a computer's seat the
view names a tick; the page sends it back after a pause, and each tick is one
click of the plan the computer made for its turn -- a card, a piece, a
square. Each click also carries its motions: the squares a piece walked, and
any piece it sent home. The page walks a marble along each path, square by
square, holds a captured piece in place until the mover lands on it, bursts
it, and shows it back in its pen.

## The computer player

**It plays the real rules.** A choice is a message the game already answers --
a card, a starting square, an end square, a card to discard -- and a line of
play is those messages applied to a real game. The search (`Search.roc`) tries
every line through the rest of the turn: every card that can be played, every
piece it can move, every way a seven splits, and on to the next card when the
card played lets the player go again. It never looks at a card it has not
drawn; when a line refills the hand, the line ends, and the computer searches
again with what it drew.

**The same position reached two ways is one line.** Positions are compared by
a key -- the board, the hand as a multiset, the discard credits, the stage of
the turn -- sorted rather than compared pair by pair. Ties between lines are
broken by the same key, so the choice never depends on the order the rules
list their moves in. A typical turn has a handful of lines; a hand of
move-again cards has hundreds; four jacks and a joker, each jack able to trade
places with a dozen pieces, pass the cap of 20,000 lines a level, and the
search keeps the first 20,000.

**The strategy is a value** (`Strategy.roc`). A position is worth:

- **the squares the player's pieces stand on**, from a table generated from
  Steve's ranking of the squares (a square that reaches home in fewer cards,
  and with more ways, ranks higher): 100 points a place, 6,100 for the deepest
  base square and 0 for the pen;
- **2,500 a step into the base**, so B4 counts four times;
- **the cards it holds back**: an A, a joker or a J in hand is worth 1,500
  with no piece home, then 1,000, 500 and nothing, so the computer keeps a way
  out of the pen and a trade early, and spends them late.

Opponents' pieces count for nothing. A capture happens when the best move for
the player's own pieces lands on someone.

## How it is tuned

**An experiment is a small program** that plays thousands of games. Red plays
the strategy under test, the other three seats play the champion, and a game
stops the moment someone wins. Experiments run as native programs; 200 games
take about twelve seconds.

**Luck is most of the game.** Winners draw more of the cards that let them go
again: over 200 games, an A, a 6, a joker or a J went to the eventual winner
31% of the time, a plain 2, 3, 5, 8, 9 or 10 about 24%, against 27% for cards
overall. The winner plays more cards, sits idle less and is captured less, and
a player that just takes the first legal move wins none of 80 games. Strategy
matters, but two reasonable strategies differ by a point or two of win rate.

**So comparisons are paired.** Every strategy plays red on the same deals, and
each seed is dealt four times with the decks turned a seat, so red plays every
player's deck. Measuring the difference deal by deal cuts its error two and a
half times against treating the games as unrelated: about 0.4 points of win
rate over 4,000 deals. Decks turned a seat add nothing over pairing for a
comparison; they balance the luck of the seat.

**What the experiments show**, in `TUNING.md`:

| change to the champion | red's win rate against it |
|---|---|
| playing against the leading opponent (own board less the leader's) | 21 wins of 80 → 17; and 27.6% → 27.2% over 8,652 deals when only a leader with three pieces home counts |
| hoarding 7s, worth less as pieces come home | no measurable change over 1,000 games |
| hoarding 7s, worth more as pieces come home | 25.0% → 23.3% over 1,000 games |
| no J hoard | -0.7 points over 4,000 deals (1.6 standard errors) |
| a base worth 2,500 a step instead of 1,000 | +1 point over 4,000 deals (1.9 standard errors); the champion's now |

Red, moving first, wins 27.2% of games in which every seat plays the same
strategy -- about two points of first-move advantage.

**A single decision can be measured directly.** From one position, each
candidate line is played out a thousand times with the undrawn cards shuffled
afresh and the same shuffles for every line. At one position of seed 69, the
champion of the time (a base worth 1,000 a step) left a piece on B1 and backed
a new piece to R0; tucking the piece to B3 instead wins 53.2% of the playouts
against 39.7%. Whole games cannot see a decision that clearly; the playouts
can, and they point at where the values are still wrong.

## The checks

Every build regenerates the square values and fails if they differ, runs
every test -- Elm's, the partnership rules, the routes, the motions, the
experiments' bookkeeping -- and builds the page twice, with LLVM and with the
dev backend, playing the two against each other click for click. A last check
plays the built page against a stand-in document for two hundred clicks, and
one more run paints the landing page's picture: four computers, 200 clicks
into a game. A change meant
not to alter the computer's play is checked by playing 200 games before and
after: every game must come out the same.
