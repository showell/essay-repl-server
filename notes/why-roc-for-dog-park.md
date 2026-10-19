# Why Dog Park is moving to Roc

*An open-ended essay, 2026-10-19. Steve's two reasons are a community of
people making games in Roc, and that Roc's constraints are useful at times.
What follows takes each seriously, and then asks what they imply for the
work, including where they pull against each other.*

## Where things stand

After about two days of porting, Dog Park's physics is split down the
middle:

- **Zig is the host.** It runs the server, the page's wasm, the unikernel,
  the wire format, the logs and the judge. It also keeps the bookkeeping:
  which poops are where, which critters stand in which cell, and the
  overlap check.
- **Roc is most of the behavior:**
  - the world's sizes and layout (`World.roc`);
  - what each critter does about the others (`Rules.roc`);
  - each critter's wish (`Wish.roc`);
  - and now the whole pixel-tick: the leashed dog's sweep, shove and slide,
    then everyone else's walk (`Walk.roc`).

Two things are queued for CC next. First the poop and the chickens (239).
Then a Zig that doesn't know what a dog or a cow is (240), so that a new
kind of critter can be written in Roc alone.

The cost so far: the Roc walk runs at about 1.4 times the old Zig walk's
instructions. You're willing to pay up to 15%. The rest of this essay is
about why that trade is worth making.

## Reason one: people

Roc has a community that makes games. People have built Roc *platforms*
for games: hosts that do the rendering, input and timing, and leave the
game logic to Roc. The two I know of target WASM-4 and raylib; I'm not
certain of the full list. The shape is always the same: a host language
does the I/O, and a pure Roc program decides what happens.

Dog Park now has exactly that shape, though nobody designed it to. Zig
lends Roc a few flat lists, Roc changes them in place and hands them back,
and neither side allocates. In a Roc game community's terms, Dog Park's
Zig is a platform and its physics is an app. Seen that way, the port isn't
a rewrite into an obscure language. It moves Dog Park's interesting part,
the behavior, into the one place a community of game makers could read
it, change it, and add to it.

That changes what 240 is for. Making the Zig "kind-blind", so that a new
critter needs only Roc, is good engineering. It's also the door a
contributor would walk through. Someone in that community shouldn't need
to read 1,600 lines of Zig to add a sheep. They should add a tag to
`World.roc`, fill in the rule table the compiler hands them, and play it.
If 240 lands as planned, the first thing a Roc person sees in Dog Park
is a game they can extend in their own language, with a compiler that
names everything they forgot.

**An open question here:** is Dog Park's host a platform someone else
could use? Today it's ours alone: one export, `roc_walk`, with arguments
shaped for this game. A small "board physics" platform (a torus of tiles,
critters as squares, integer positions, a step function) might be useful
to other games. That's speculative, and it shouldn't drive the design. But
it's a reason to keep the boundary clean and documented rather than
clever.

## Reason two: the constraints

Roc refuses things. It allows no mutation you can see, has no nulls, and
does no I/O inside the app. Its `match` must be exhaustive, its records
are typed structurally, and its tests (`expect`) sit right next to the
code. In two days, several of these refusals did real work.

**Exhaustive matching turned a silent bug class into compiler errors.**
In the Zig, and in the first Roc, a critter's kind was a number:
`kind == 0` meant a dog, `== 1` a cow, and anything else was a chicken in
one function and a dog in another. Once kinds became a tag
(`Dog | Cow | Chicken`) with every rule a `match`, adding a fourth kind
became a list of compile errors at exactly the places that need a
decision. That's the "make state honest" doctrine, enforced by a type
checker.

**Purity made the physics replayable for free.** The game depends on the
server re-running each report and reaching the same bytes. A Roc function
can't read the clock, can't touch a global, and can't do I/O. Every input
the walk depends on is an argument, so determinism is a property of the
language, not a discipline someone has to keep. The 14,800-line output
the port is judged by stays byte-identical because there's nowhere for a
difference to come from.

**The tests read as the rules.** Look at `Wish.roc`'s 22 `expect`s, or the
four I added for the leashed dog: "a chicken touching in front it shoves:
the chicken goes the step and a step across". They read like the design
doc. When I broke the leashed dog on purpose (letting it nudge its own
breed), one of those statements failed. In Zig the same check would sit in
a test file elsewhere, phrased in setup code.

**The boundary forced a clean contract.** Because Roc can't allocate into
the host's memory unless the host lends it room, every list crossing the
boundary is lent with a fixed capacity, and Roc has to hand it back
unique. That's annoying to set up. It also documents, in types, exactly
what the physics may touch and what it may not.

## Where the constraints cost

Your phrase was "useful *at times*", and that qualifier is earned.

**Mutation-heavy data structures stay in Zig.** The scene keeps critters
in cell bitsets and poops in linked lists by tile, and updates them in
place on every move. Roc can do in-place updates when a list is uniquely
held. But every `List.set` is a call, and every list the host can see has
its references counted atomically. CC measured this: atomic refcounts were
about a third of the first Roc walk's time. The fix was a style of its
own:
- one variable owns each list;
- a function that reads a list takes it and hands it back;
- no record carries a list through a loop.

That style is learnable. It's also a tax that Zig doesn't charge.

**Hot loops want numbers, not the nice types.** The walk's inner fold is
"numbers only", and the rules are flattened to numeric codes inside it.
Tags and records carried round a loop end up on the stack. So the code
that runs four million times a drag is less idiomatic than the code that
runs once. Roc's elegance is real where it runs often enough to matter,
and gets traded away exactly where it runs most.

**The toolchain is young.** The physics needs a nightly of Roc's new
compiler. CC's Roc and the box's produce different archive bytes for the
same source, and the compiled archives are checked in, so a stale one
could run unnoticed. These are the costs of being early: real, and
shrinking.

## How the two reasons fit together

They meet at the game's variations. The community reason says to put the
interesting part where game makers can change it. The constraints reason
says the compiler should catch what a changer forgets. Rules written as a
`match` over pairs of kinds, a level drawn as a string with `expect`s for
"nobody starts overlapping", and a new critter that touches no Zig: each
is easier to contribute and harder to get wrong. That's the same work
satisfying both reasons.

They pull apart only in the hot path. There, the community would benefit
from readable code, and the speed budget asks for flattened numbers. The
15% tolerance is your answer to that tension. Spend a little speed so that
more of the physics reads like rules. It probably also means the hot
walk's internals will always be the part of the Roc that a newcomer is
told not to start with.

## Questions I'd like your view on

1. **Who is the first outside contributor?** If it's someone from the Roc
   games world, the README's first screen should be about `World.roc` and
   `Rules.roc`, not the Zig build. When should that rewrite happen: after
   240, or now?
2. **Should Roc own the world's bookkeeping eventually,** with the poop
   lists and cell sets as Roc data structures? If the refcount tax comes
   down as the compiler matures, the case for keeping them in Zig weakens.
   Or is "Zig keeps the tables, Roc decides the moves" the right line for
   good?
3. **The independent check.** The overlap check stays in Zig on purpose,
   so the Roc physics is judged by code it doesn't share. As more moves to
   Roc, that check matters more. Should there be a second, deliberately
   naive Zig judge of the Roc walk (a slow reference that replays a tick
   and compares)? It would guard behavior the way the 14,800 lines guard
   bytes.
4. **Levels as pictures.** A level drawn as a string in Roc, checked at
   build time, is the most "Roc" feature on the list, and the most fun to
   contribute to. It needs the world to stop being compile-time constants
   in Zig. Is that worth queueing alongside 240?
