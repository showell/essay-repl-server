# What the safari port surfaced, and what it says about the instrument

*2026-08-30, written from the ladder while the arc-tangent PR is being measured.
Steve's read going in was that we are hitting pretty normal boundaries. Mostly
yes — but two of the eight are not the kind that heal with time, and the more
interesting question is what the port could see that the ladder structurally
cannot.*

## A number to start with

An hour ago the claim about our arc tangent was that it matched zig's to 1e-9
over eighteen values. That sentence lived in a README and a commit message.
Nothing in the repository contained the eighteen values, and no test compared
anything to zig.

Measured properly this afternoon — 41 arc tangents and 19 two-argument ones,
both arms generated from one input list so they cannot drift, compared as f64 bit
patterns rather than rendered decimals — the worst absolute error is **6.7e-16**,
four ULP. The prose was wrong by seven orders of magnitude, in the flattering
direction, and nobody could have known because the measurement was never written
down.

That is the whole essay in one artifact: not a defect, not a lie, just a claim
that was never made checkable, sitting in a document that reads as authoritative.
Hold onto the shape.

## Eight findings, one shape

The port produced eight write-ups. Read as a list they look unrelated: an
overflow mode, a trig library's accuracy, a name collision, an inlining rule, a
missing diagnostic stream, a literal parser, and two things in the game itself.
Read for shape they are one finding eight times.

**Something claims, and the claim is not carried.**

`IntegerTy i64-min i64-max OvError` declares a trapping multiply. Lowering has no
branch for the mode, so `OvError` and `OvWrapping` both become `IrMulInt`, and
`4e9 * 4e9` prints a negative number with exit 0. `RealTy (w) (m)` names a width
and a mode; the zig plug maps it to `f64`, discarding both. A source file says
`1000000000000000000.0`; the parser accumulates the digits into a wrapping i64
and the program receives `-844674407370955136`. Cordic's docstring claims 0.1%
error and delivers 0.45%, and its test prints `Math/Cordic OK` without calling
Cordic. A one-expression function over a record parameter is written as a
function and emitted as nothing. The seed reports ten real CDX3006 name
collisions and the zig arm reports silence.

In every case the failure is not that something computed wrongly. It is that a
promise made in one representation was dropped on the way to the next, and
nothing anywhere said so. The type system, the docstring, the test name, the
declaration — each is a claim, and the pipeline is full of places where claims go
to be quietly not enforced.

This is why I do not think the count is eight. It is one property — *claims are
not load-bearing across representation boundaries* — sampled eight times by
someone writing an ordinary program.

## Where I agree with "normal boundaries"

Six of the eight are exactly what a young self-hosted toolchain looks like. The
foreword's numeric tower is thin and integer-flavoured — the whole library has no
Real arc tangent anywhere across thirteen directories, and its two existing arc
tangents are milliradian integer routines. The plugs are incomplete; we have
personally filled four builtins in two PRs this month and thirteen more are still
refusing. Diagnostics are plumbed for the arm that was built first. Foreword
tests are one-cite compile smokes because that is what you write when the point
is that the chapter compiles at all.

None of that is pathological. It is a language that has been more concerned with
existing than with being complete, which is the correct order. A five-year-old
compiler with this much working would be doing fine.

## Where I would push back

Two of them are not youth.

**The overflow mode is a design fact, not an unfinished feature.** The IR has one
integer multiply. There is no opcode that could carry the trapping intent, so no
plug can honour it, and every plug's identical wrapping emission is not a shared
convention — it is the absence of anything to disagree about. This does not
improve as the compiler matures. Someone has to decide either to widen the IR or
to stop letting the type promise it. Waiting produces nothing.

**The literal parser is a bootstrap ratchet, and those tighten.** Cobblestone's
own comment says it outright: *"The bits land in IrNumLit, so they must match the
seed's exactly; a parser that rounds better is a parser that diverges."* That is
a beautiful and slightly chilling sentence. It means a **correctness fix is
indistinguishable from a regression**, because the seed's behaviour has become
the specification. The rounding half of that same function was already repaired
once, which shows it can be done — but the repair had to move both sides
together, and the cost of doing so goes up with every artifact pinned to the
current bits.

This is the classic self-hosting trap and it is not a boundary that time softens.
It is one that time hardens. Worth naming now while the tree is small.

## The part I think matters most: two instruments, one blind

Here is what I did not expect to find.

**The ladder's oracle is relative. The port's is absolute.** The ladder compiles
compiler chapters two ways and requires byte-identical agreement. That is an
extraordinarily sharp instrument for a whole class of defect, and it is
*structurally incapable* of seeing a defect both arms share.

Look at which findings the ladder could never have produced:

- The wide literal. Both arms print the same wrong constant — that is how we
  proved it was the front end. Perfect two-arm agreement, wrong answer. The
  ladder would have called it green forever.
- Cordic's accuracy. Both arms compute the same inaccurate cordic, byte for byte.
  Green.
- The missing arc tangent. An **absence**. No differential test can fail on a
  function nobody wrote.

Every one of those came from the port having an external standard: zig's libm,
and a gold file describing what the picture should look like. The ladder proves
the two arms agree. It cannot prove either is right.

I think that is the holistic gap. We have built a superb consistency instrument
and almost no correctness instrument. The corpus verdicts are banked from our own
runs. The tier set is two-arm. `codexzig`'s fixed point is self-referential by
construction — it re-emits its own bundle byte-identically, which is a beautiful
property and says nothing about whether the bundle is right. Even the bare-metal
oracle, which we lean on hardest and which settled the arc tangent's `.expected`
this afternoon, is only absolute relative to *the seed*. It answers "what does
Codex do", never "what is true".

The safari port improvised the missing half — for one program, in one domain, by
hand. That is the thing worth institutionalising.

## What I would actually do about it

Three things, in order of how cheap they are.

**Make the numeric oracle standing rather than improvised.** The rig built this
afternoon is forty lines: one input list, two generated programs, a comparison
that refuses if the two sides drift apart. It graded an arc tangent against zig's
libm to four ULP. The same rig grades Cordic against the docstring that has been
wrong for however long, and the next transcendental after that. The foreword's
docstrings are a specification nobody checks; they could become one that is
checked at the cost of a day.

**Notice that we have no instrument for absence.** Every finding we have is a
thing that behaved wrongly. The arc-tangent gap was found by a person wanting an
arc tangent. A cross-reference of the foreword's Real surface against, say, what
a C or zig math library exposes would take an afternoon and would enumerate the
gaps rather than waiting to trip over them. Absences do not fail tests.

**Take item 4 more seriously than its severity says.** The silently-not-emitted
function is the only finding whose sole witness is *outside* the language. It is
invisible from inside Codex and harmless there; it surfaces three steps
downstream when a zig shim calls something that no longer exists. That is a bad
shape — a defect class whose detector is "somebody was writing a foreign-function
boundary that week". We have no idea how large it is.

## The honest limits of the evidence

The port is one program. It is float-heavy graphics: it hammers Real arithmetic
and barely touches type classes, generics, or effects, which is exactly where the
ladder's findings 57 through 62 live. It is single-threaded and allocation-light.
So the two instruments are complementary rather than one being better, and
neither is general. Eight findings from one program is a striking yield, but it
is a *sample*, and the thing it samples most heavily is the numeric tower — which
is precisely where it found the most.

The right conclusion is probably not "the toolchain has eight problems". It is
"one ordinary program, written honestly, hit eight unenforced claims, and we
should expect the density to be similar wherever we point the next one."

*— Claude*
