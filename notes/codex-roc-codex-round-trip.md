# Codex to Roc and back

A Codex program from Cobblestone's test suite goes through two translators and
two interpreters and comes out the other side printing exactly what it printed
before:

    codex/test/X.codex
      -> rocemit (rust-codex-compiler)      Codex to Roc
      -> rocflight's parser and checker     the Roc, typed
      -> roc2codex (our rocflight fork)     Roc back to Codex
      -> codexrun (rust-codex-compiler)     runs it
      == the output Cobblestone captured for X

The subjects are roc-apps' ported tests: 525 Codex programs that rocemit writes
as Roc, each with the exact bytes the original prints. **515 of them make the
whole trip and print those bytes.** None prints anything else. The other 10 are
refused by design: a program that pokes raw memory is written over rocemit's
simulated machine memory, threaded through every function, and undoing that is
a whole-program rewrite rather than a translation.

The output is not the original Codex. `sum-pair (p) = when p is (x, y) -> x + y`
comes back as itself, but a text built by a fold comes back as the fold rocemit
wrote, and a program's own chapters sit in a unit beside a small `Roc--Wrap`
chapter of helpers. What matches is what the program does, judged the only way
that is not circular: the Cobblestone verdict, captured long before any of this
existed.

## The pieces

**rocflight** is Brian Teague's Roc interpreter in Rust: a parser, a
bidirectional type checker and a register VM. It is not ours. We fork it
(showell/rocflight), send fixes back as pull requests, and keep the Codex work on
a branch of our own, `codex-emit`. The emitter reads the tree rocflight's parser
builds and the types its checker infers; the one thing it asks of rocflight is
a record of every node's type, which the checker now keeps on request and
otherwise does not.

**roc2codex** is about 1,000 lines in `src/codex/`. It writes each Roc module
as a Codex chapter and `main!` as the chapter's `opening`, and it writes one
resolved unit: the Foreword chapters every Codex program carries, then the
program's. `codexrun` runs a resolved unit from anywhere.

**codexrun** is rust-codex-compiler's Codex interpreter. It was the oracle's
weak point three times: it did not match `Nil` and `Cons` against a real list,
it read a negative exponent as a huge unsigned one, and a tail view of a list
read the whole list (the same list-pattern bug). It passed those programs'
originals no more than their round trips. Those are fixed, and each fix moved
exactly the verdicts it should over the 275 U61 programs that reach them.

## What made it work: the types have to survive

The first version passed 296 of 526, and most of what separated 296 from 515
was not cleverness in roc2codex. It was making the Roc say what the Codex
meant.

rocemit had been lossy in ways nobody noticed while Roc was the destination:

- **A Codex `Text` was a bare `List(U8)`.** Its units are CCE codes,
  Cobblestone's own alphabet. Written as a list of bytes, the Roc could not say
  which lists were text. It is now `CceText :: List(U8)`, an opaque type of its
  own, and a text literal is a Roc string literal, which `from_quote` turns into
  CCE units.
- **A Codex `Char` was a bare `I64`**, and `char-code` and `code-to-char`
  disappeared, since a Char was its code. So `ch == 15` compared a Char with an
  Integer on the way back, and Codex says that is simply false. Four round
  trips printed wrong answers from that, beside the ones that failed loudly. It is now
  `CceChar :: I64`, with `code` and `of_code` as the two conversions.
- **A Codex record type was a structural alias.** `Byte = record { val :
  Integer between 0 and 255 }` and `Wide`, the same with 65535, were one Roc
  type, `{ val : I64 }`, and a literal `{ val: 0 }` could have been either. Every
  record type without type parameters is now a nominal, `Byte := { val : I64 }`,
  built `Byte.{ val: 0 }`.

The names are Steve's call: `CceText` and `CceChar` say whose text and whose
characters they are. Another Roc program's `Text` means its own thing, and a
CCE code is a position in Cobblestone's alphabet, where `'a'` is 15.

Each change went through rocemit's own ladder of 1,036 Cobblestone programs
first, and the ledger never moved: 767 pass, 26 set aside as slow.

## What made it work: idioms read back

rocemit writes a Codex builtin as a Roc idiom, and roc2codex reads each idiom
back as the builtin it came from: `U64.to_i64_wrap(List.len(xs))` is
`list-length xs`, and `List.get(xs, I64.to_u64_wrap(i)) ?? crash(..)`, which
rocflight's parser has already desugared into a `match`, is `list-at xs i`. The
table is rocemit's builtin table run backwards. That is "cheating" in Steve's
sense: roc2codex is tuned to rocemit's Roc, not to Roc in general.

The price of cheating is ambiguity, and the rule for ambiguity is to refuse and
say why. Some of the refusals it gave on the way: a record literal that "could
be any of Byte, Wide"; a Char pattern nested inside another pattern, which
would need a literal conversion rocflight cannot do; a call into one of Roc's
own modules with no idiom behind it. It never guesses. The one place it gets
close is Codex's single string type: every Roc string literal is written as a
Codex `Text`, because a `Str` that behaves differently from a `Text` has to do
it through a `Str` builtin, and those are refused.

A few things have no Roc form at all and come back as scaffolding. rocemit
writes wrapping arithmetic on a Codex `Integer wrapping` as `I64.plus_wrap`,
and the Roc no longer says which integers wrapped. So the unit carries a
`Roc--Wrap` chapter whose helpers take an `Integer wrapping`: a plain Integer
passes for one, and arithmetic on it wraps where plain arithmetic traps.

## What it found

The round trip is a test of four programs at once, and it found bugs in all of
them.

- **In rocflight**, which runs the same 525 Roc programs: at first 476 matched
  `roc`'s output, now 518. The fixes went to Brian as PRs: loading a module's own
  imports and local packages; a module namespace hiding a type of its own name;
  typing `Name.(x)` patterns as the backing (an `is_eq` that recursed forever);
  a string pattern matching a nominal through `from_quote`; a nested type's
  methods seeing the enclosing module; a lambda whose body is a record; a
  nominal over a list or a scalar claiming records in `==`; and updating a
  nominal record three levels deep. Four are issues instead, because they need
  decisions only Brian can make; the largest is that a parameterised alias
  from another module loses its arguments.
- **In Roc itself**: a constant made of `from_quote` literals checks in time
  that grows faster than quadratically, 20 seconds at 800 literals
  (roc-lang/roc#11666), which surfaced when rocemit started writing text
  literals as strings.
- **In codexrun**: the three interpreter bugs above.
- **In rocemit**: every type it erased.

## The next target

A round trip proves something a one-way translator cannot: that the typed Roc
tree carries enough to rebuild the program. That tree is now the interesting
thing. A second emitter reading it, beside roc2codex, gets the same subjects,
the same verdicts and the same discipline for free: 525 programs, each with the
exact bytes it must print.

**Zig** is the ecosystem's own language: Roc's compiler is written in it, its
platforms' hosts are, and Cobblestone already emits Zig from Codex (the zig
plug; our own codex-zig-transpiler, `codexzig`, is another). What makes it hard from Roc is
what Roc takes for granted. Zig has no closures, so every lambda that captures
becomes a struct of its captures and a function taking it; rocemit's programs
pass functions around freely (`apply add 20 22`, a record field holding a
function). Memory is the program's to manage. A pure program that allocates and
never frees fits an arena allocated once and dropped at exit, which is honest
for these tests and wrong for a long-running one. Generics are `comptime`
functions returning types, which a generic `Maybe(a)` or `ListUtils` fold would
need.

**Rust** is closer than it looks. The borrow checker is mostly about who may
change what, and in a pure program nobody changes anything: a value is either
moved into its one consumer or shared. `Rc` makes sharing cheap where the
emitter cannot prove a value has one consumer; closures are `Rc<dyn Fn(..)>`;
recursive unions are enums with a `Box` or `Rc` in the recursive position;
records are structs deriving `Clone` and `PartialEq`, which is what the nominal
records' field-by-field `is_eq` already is. The places Rust pushes back are
known ones:

- **Recursion depth.** Rust does no tail-call elimination. rocemit already
  rewrites the folds it recognises into accumulator loops, and roc2codex reads
  them back as written, so the same shapes would arrive as loops. A general tail
  call still needs a loop the emitter writes.
- **Integer arithmetic.** Codex traps on overflow and has a wrapping type; Rust
  has `checked_*` and `wrapping_*` and panics in debug. Each Codex operation
  says which one it means, once the types say so.
- **Lists.** Roc lists are values that are written in place when uniquely
  held. `Rc<Vec<T>>` with `Rc::make_mut` gives the same: in place when unique,
  a copy otherwise. That is exactly the discipline rocflight's VM and Roc's
  runtime already follow.

So my read agrees with Steve's hunch: Rust is the easier of the two. Almost
every Roc construct in these programs has a direct Rust counterpart, and the
two that don't (tail calls, in-place list writes) have well-worn answers.
Zig needs closure conversion and a memory story before the first test passes.

The practical plan would mirror roc2codex: a `src/rust/` beside `src/codex/`
on the same branch, the same checker types, a `roundtrip.sh` twin that
compiles each program with `rustc` and diffs its output against the same 525
verdicts, and a refusal for everything it does not yet write. Starting from the
cheapest tests, as roc2codex did with `arithmetic`, it would show within a day
how much of the Rust story is true.
