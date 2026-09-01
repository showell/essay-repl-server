# Why an interpreter needs no types, and what that buys us

You said you are biased toward a Zig worldview where types really do matter,
and I want to take that seriously rather than wave it away, because in Zig they
matter in a way that has no analogue here.

## Where the confusion comes from, and it is a good one

In Zig, a type is not a claim about a program — it is part of the program. It
decides how many bytes a struct occupies, which machine instruction an `+`
becomes, which version of a generic gets stamped out. Erase the types and there
is no code left to emit. That intuition is correct and it is why the zig arm of
safari cares so much about them.

The thing that intuition does not carry across is this: **types are needed to
compile a program and to reject a bad one. They are not needed to decide what a
good program does.**

An interpreter never asks "how wide is this integer" at compile time because it
is not compiling. It holds a value that already knows what it is — an integer,
a text, a list, a record — and when it meets `a + b` it looks at the two values
in its hands. The type checker's whole job is to prove ahead of time that those
hands will always hold the right things. If the program was going to typecheck,
running it produces the same answer whether or not anyone checked.

So `1 + 2` is 3 in an interpreter with no type system at all. The type system
exists so that `1 + "x"` never reaches that point.

## Why this is unusually true for Codex

There is one feature in Codex where types genuinely direct the *meaning* of a
program rather than just guarding it: type classes. `to-text x` has to become a
call through the right dictionary, and picking the dictionary is a type
question.

Here is the thing I learned building the desugarer today: **Codex resolves that
before the type checker runs.** The dictionary records are synthesised from the
class declarations, and the dictionary arguments are inserted at the call sites,
by the desugarer. By the time the checker sees the tree, the choice has already
been made syntactically.

That is a genuinely unusual design and it is what makes this idea work. The one
place where you would expect to need types to know what a program *means*, in
Codex you do not — the meaning is already in the tree. Everything else that
survives to the AST is ordinary: application, arithmetic, matching, let,
records, effects.

## The argument that actually matters

Here is the part I would want you to push back on if you disagree, because the
rest follows from it.

**A type checker cannot catch a shape error, because wrong shapes are almost
always well-typed.**

Consider the things I got wrong today and had to fix, or could plausibly still
have wrong in the desugarer:

- `a - b` where it should be `b - a`. Well-typed. Wrong answer.
- `+` and `*` given the same precedence. Well-typed. Wrong answer.
- `a |> f` desugaring to `a f` instead of `f a` — the operands swap, and
  nothing about the token says so. Well-typed if the arities happen to line up.
- `not x` becoming a negation instead of `x == False`. Well-typed.
- Match arms in the wrong order, or an alternation fanned out wrongly. Perfectly
  well-typed. Silently different behaviour.

Every one of those produces a program that a type checker will happily accept
and that computes something else. Reproducing Cobblestone's IR byte for byte
would catch them — but that is the thing we cannot check until *both* remaining
layers exist. Running the program catches them immediately, and catches them as
a wrong number on the screen rather than a structural diff nobody can read.

So the interpreter is not a cheaper substitute for the type checker. It tests a
failure class the type checker is structurally blind to. They are complementary,
and right now we have neither.

## Where types would matter to an interpreter — honestly

I do not want to oversell this. Three places where an interpreter would be
approximately right rather than exactly right:

- **Bounded integers.** `Integer between 0 and 255 wrapping` puts the wrapping
  behaviour in the type. An interpreter that treats everything as a 64-bit
  integer agrees everywhere except at the boundary. Fixable by carrying the
  bound on the value, but it is real work and real divergence until then.
- **Real width.** `Real approximate` is f32, `Real` is f64. Precision differs.
- **Effects.** The `[Console]` row is a static check, so it costs an
  interpreter nothing — but the interpreter does have to actually *do* the IO,
  and whatever else the program touches.

That third one is the open question I have not answered and should before
committing: I do not yet know what safari's programs emit. If they print text
and numbers, this is straightforward. If they render into a framebuffer and the
expected output is an image or a hash of one, the interpreter needs the drawing
primitives and the cost is different. That is a ten-minute check and I should do
it before spending a day.

## Against the four uses you named

You said you are not biased toward any one of Rust's possible purposes here —
your exposure to Rust, faster tooling, another arm, or R&D. What makes the
interpreter interesting to me is that it is the only item on our list that
scores on all four.

**Another arm.** Safari has four, and the note in my memory about them says the
`--both` mode "runs two different IR pipelines and cannot attribute a
difference" — the arms share too much. An interpreter shares *nothing* below
the AST: no IR, no emitter, no plug, no zig. When it disagrees, the
disagreement is attributable, which is the property the existing arms lack.

**Faster tooling.** Running a Codex program today means the native pipeline or
a guest. An interpreter runs one in milliseconds. Safari's own corpus sweep is
three minutes; the same sweep through an interpreter would be seconds. That
changes what it is comfortable to check, and things that are comfortable to
check get checked.

**R&D.** The linting goal wants to answer questions about programs — is this
branch dead, is this constant foldable, what does this expression evaluate to.
An evaluator is the substrate for all of that. It is also the natural back end
for a REPL, which is a thing this language does not have.

**Rust exposure.** A tree-walking interpreter is about the most idiomatic Rust
artifact there is — one big enum, exhaustive matching, recursion over boxed
nodes. It is a good thing to have read and edited if the goal is to become
comfortable with the language.

Cost: somewhere around a day, and it can be abandoned cheaply if the first
sample program shows it is the wrong shape.

## What I am not claiming

I am not claiming we can skip the type checker. We cannot — it is the thing
that decides whether a program is legal, it is half of what "works like Codex"
means, and the 222 refused programs in the gold bank are waiting to grade it.

I am claiming the order is wrong if we do the checker next. The checker's
oracle only lights up after the lowering as well; the interpreter's lights up on
the first program it runs. And the class of bug it catches — a tree that means
the wrong thing — is one that will otherwise sit undetected underneath
everything we build on top of it.
