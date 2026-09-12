# Damian's games, as a Roc port: the analysis

*2026-09-12. Steve's axis is the app, not the language: safari and the
shaders made obvious demos. This is the same look at `apps/games`, with the
emitter census run and the missing pieces added along the way.*

## What is there

Two halves. The classic suite is thirty-four board and card games, each an
engine chapter of pure functions (TicTacToe at 109 lines, HexWar at 1,380)
plus a `<Game>Wasm` shell chapter that is the export surface. A shared
`Rng`, a shared `Minimax`, the foreword's `List` and `Tuple`. No effect, no
`act`, no handler anywhere in the 73 chapters: the games are the purest
Codex in the tree, which is the emitter's sweet spot and safari's shape
exactly. CodexMagic is the other half, seventy chapters of card engine,
economy, clans and a bare-metal HTTP server under `[Console]` and
`[Network]`; a server, not a browser demo, and out of scope here.

## How the games are hosted, and why it matters

The landing site's arcade page loads `<id>.wasm` per game with only two
WASI stubs as imports, and `arcade.js` holds one descriptor per game, with
`boot`, `step`, `view`, `move` and `status` written against the module's
exports by name: `ot_new()`, `ot_ai(h)`, `ot_place(h, m)`, `ot_cell(h, i)`.
The 618 export names over 35 games come from one table in
`build-wasm.ps1`, so adding a game there is a row.

Two state contracts. TicTacToe threads its whole game through one 24-bit
integer, so the page holds the state. Every other game is too wide, so the
page holds a *handle*: the i32 IS the address of the board record in the
module's heap, the module bump-allocates and frees nothing, and the heap is
reset only at a new game. That is why the arcade bounds its autoplay steps
and prefers a `runs` export that plays a whole game in one call.

A Roc module with the same export names drops into that page unchanged,
the way the Roc safari drove `blitter.js`. The shell chapters' functions
take the board *record* (`ot-wasm-place : OthelloBoard, Integer ->
OthelloBoard`); it is the plug's wrapper that narrows a pointer to it. So
the Roc host keeps a table of boxed boards and hands out indexes: `ot_new`
appends and answers its index, `ot_place(h, m)` reads slot `h`, calls the
emitted function, appends the result. Old handles stay valid, as the
arcade assumes. And because Roc's memory is counted, there is no heap to
reset and nothing leaks across a long autoplay; the `steps` bound becomes
unnecessary rather than violated. TicTacToe's flat contract is just pure
functions of an integer.

## The oracles are already written

Every game has a grader: `ot-verify.mjs [path/to/othello.wasm]` implements
Othello's rules a second time in JavaScript and plays whole games in
lockstep with the module, comparing all sixty-four cells after every ply.
Thirty-five of these take a module path, and `ar-verify.mjs` grades the
descriptors for progress. A Roc module with the export contract is graded
by the same files, no harness to write. That is a stronger oracle than
safari's frozen verdicts, because it is rules against rules.

## The census, before and after

Before today rocemit emitted one of the 73 chapters, and that one against
the wrong tree: the emitter resolves cites through the box's `CODEX_ROOT`,
which names Damian's Sep 8 checkout, and u58's `Rng` and `DeviceMath`
differ from it. (The gallery had been built on the old `DeviceMath`,
139 lines behind, and is republished on the right one.) Resolving from
u58, everything refused on one type form.

Five additions later, 72 of 73 emit and pass `roc check`; the one out is a
console demo with a value opening. Each addition is the language's, not a
game's:

- **`Integer between lo and hi wrapping`** as a type, and `+ - *` spelled
  as the wrapping operations on every node the checker types that way.
  Rng's LCG state is declared so, and Roc's plain `+` would crash on it.
- **`list-set-at`**, the mutating set, as `List.set`. They agree wherever
  the program uses the answer, which every typed use does; a program that
  sets and then reads the old name would diverge silently, and only a
  grader would catch it. Fifty-six chapters were waiting on this one.
- **Instance names.** `==` on a list is lowered as upstream's x86 emitter
  spells it, `__eq_ConsList@<keys>`, one name per element type; the
  derived definition is one function whose `where` clause dispatches the
  elements' equality, so the name is looked up without its suffix.
- **Record update** by a literal field name, as Roc's `{ ..r, f: v }`.
- **The heap checkpoint** Chess takes around every search step is nothing
  under counted memory.

None of it is games-specific, and the wrapping-by-type and the instance
names are things any larger Codex program would have hit next.

## What the port would be

A `games/` track shaped like the gallery's: a generator reads the export
table and each shell chapter's signatures and writes, per game, a Roc app
over the emitted chapters and a platform whose host is the handle table
with that game's export names. The arcade page and `arcade.js` are copied
as they are, as `blitter.js` was. The graders run against each module. I
would estimate the generator and the host at a day, and then the graders
decide, which is the point: they will find every place where "the answer
is used" was an assumption.

## The honest comparison with the other candidates

Against the gallery: the games teach the emitter more, because they are
real programs with records, sums, matches and recursion, and they come
with rules-level oracles. Against a handler subject: the games exercise no
effects at all, so `handle` and text stay untested; but they are thirty-four
demos people click on, and a handle table is the host pattern every
interactive app needs. Against safari: same shape, more of it, and a
harness that argues back.

So, yes: the games are the better next port on your axis, and a good one
on mine. Start with Othello, since its grader is the strictest and it is
the handle contract; TicTacToe as the flat one; then the generator does
the other thirty-two.
