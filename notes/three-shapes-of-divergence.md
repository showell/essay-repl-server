# Three shapes of divergence, and the one root under two of them

I ran the discovery loop against a batch of hand-built type-engine probes —
sums, pattern matching, orphans, polymorphism, plain type errors — each through
two oracles: our interpreter for the value, our IR through the zig plug for the
type, and upstream `codexzig` alongside to attribute every break. The programs
were small and the answers unarguable, which is what makes a disagreement mean
something. What came back sorts cleanly into three shapes, and the sorting is
the finding.

## Shape one: we are ahead

`is-some None`. The `Maybe a` is never observed at a type, so its element is an
orphan no context binds. Our zonk-and-default resolves it to int-default and our
IR compiles and runs — `False`. Upstream leaves the variable free and its zig
plug refuses the program: "type variable T11 is not declared at this site." This
is the inversion we decided to lean into, now visible on a shape we had not
tested: the empty-list defaulting generalizes, untouched, to a nullary sum
constructor, and to a nested one (`Some None`). I locked both as tests. This is
the reference relationship working exactly as the essays argued it would — where
we resolve a type upstream leaves open, our IR is the correct one, and the proof
is that ours builds where theirs will not.

## Shape two: a frontier we share

`make-empty : Integer -> List a; make-empty (n) = []`, used as `list-length
(make-empty 0)`. Here `a` is a genuine generic where `make-empty` is DEFINED —
its own zonk pass rightly protects it — and an orphan where it is USED. Both our
compiler and upstream carry the variable into the caller and both refuse it. The
mechanism is precise and worth naming: inlining recovers type variables only by
matching a helper's parameters against its arguments (`once_retype`), and `a`
lives in the return type, in no parameter, so there is nothing to match it
against. Worse, inlining runs in the pipeline, AFTER the checker's
zonk-and-default — so even the defaulting that would have caught a plain orphan
never sees the variable the inliner injected. Pinning it from outside
(`list-push (unwrap (make-empty 0)) 5`) does not help either: the constraint
sits in the caller, and the inlined body was already sealed.

This is not us being behind; it is a place the whole language stops. Which makes
it the most interesting kind of target — fixing it here would put us ahead the
way shape one already is, and the fix is legible: let the expected type flow
down into an inlined body (bidirectional, phase two), or run defaulting once
more after the pipeline for a true orphan (phase one, relocated). The frontier
is exactly where the curriculum said phases two and three would bite.

## Shape three: we are behind, and dishonestly

`n + "hello"`. Our checker emits IR; the interpreter catches it at runtime and
the plug at build time. Upstream rejects it at check with CDX2001. Same for a
monomorphic function handed the wrong type, and for an undeclared function used
at two incompatible types — in every case our checker waves the program through
and lets something downstream discover it is broken.

The cause is written plainly in our own source: "a `false` out of a partial
unifier is our ignorance and not the program's fault." That is a true and
reasonable thing to believe — as long as every program you ever check is
well-typed. And ours were: the checker grew byte-matched to the self-host
corpus, which is the compiler compiling itself, a body of code with no type
errors in it anywhere. So a unification failure could only ever mean the
unifier was incomplete, never that the program was wrong, and treating every
failure as our own ignorance was not a bug — it was correct for the only inputs
we had. The moment we feed it an ill-typed program, the assumption inverts and
the checker cannot tell a genuine conflict from its own gap.

## The root under two of the three

Shapes two and three look unrelated — one is about inlining a generic, the other
about adding two incompatible values — but they share a spine. In both, the
checker declines to commit. It will not commit a type error into a diagnostic;
it will not commit a resolved type into an inlined body. It computes the right
information — it KNOWS Integer and Text conflict, it KNOWS the inlined list's
element is unconstrained — and then files that knowledge as a gap instead of an
answer. The whole thesis of the reference work has been "carry earned knowledge
forward," and here are two places where the knowledge is earned and then
dropped on the floor.

The single most valuable change is small and precise: a unification failure
between two FULLY CONCRETE types is not ignorance — it is a CDX2001 the program
earned. Integer versus Text, with no variable on either side, cannot be the
unifier being incomplete; the types simply do not match. Separating that case
from the genuine "a variable I could not decide" is the difference between a
checker that counts its confusion and one that reports the program's errors —
which is the difference between a copy and a reference. A reference for
well-typed IR has to be able to say NO. Right now ours can only shrug.

## Reflection

The discovery loop earned its keep. Not one of these came from reading the code
and reasoning about it; each came from a three-line program whose answer I knew
and whose three arms then disagreed. Shape one told us the win generalizes.
Shape two handed us the exact call to make inlining type-aware, with the failing
line to prove it. Shape three found the assumption at the center of the checker
— reasonable, load-bearing, and quietly false the instant we left the corpus it
was built on. The next move is not more probes; it is to teach the checker the
one distinction it never needed before: between what it cannot decide and what
the program got wrong. Everything else — the phases, the frontier, the
reference — is downstream of that.
