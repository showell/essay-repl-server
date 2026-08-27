# A day of being wrong, productively

*For Steve. 2026-08-27, near midnight. Reflective, and not entirely serious.*

---

## The scoreboard nobody keeps

If you graded today by findings opened, it was a triumph: 57 through 65, plus
sub-findings, plus two instrument repairs. If you graded it by findings that
survived contact with a compiler, it was a more modest day: three went in a PR,
one was withdrawn after being built, one is parked, one is "works except when it
doesn't", and one turned out to be two other findings wearing a trench coat.

The number I actually find interesting is a third one. **Three times today I
wrote a confident mechanism into a document, and three times a five-minute
measurement said otherwise.** Finding 64's diagnosis. Finding 63's diagnosis.
Finding 65's falsifier. In two of those cases the wrong version had already been
sent to another human being.

That is a 100% failure rate on "reason from one error message to a mechanism,
then write it down as fact." It is such a clean result that if I were grading it
as an experiment I would call it well-powered.

## The shape of the mistake, which is funnier than it sounds

Every one of these had the same anatomy. I would see an error message. The error
message would suggest a mechanism. The mechanism would be *plausible* — that is
the load-bearing word — and I would write several hundred words of confident
prose explaining it, complete with file:line citations that were all individually
correct and collectively pointing at the wrong thing.

Finding 64 is the connoisseur's example. I found a lambda whose parameter said
`tvar 16` while its own body said `boolean`. I had just spent the morning
proving that exact disagreement was caused by a missing span. There was a
missing span *right there* in `synth-instance-fields`. I wrote it up, fixed it,
told Damian, and put it in a PR he then reserved a register row for.

Then I built it. The parameters didn't move. Because a method lambda is a record
*field value*, so it has an expectation from the field's declared type, so the
arm that needs a span never fires, so the span could not possibly have been the
blocker. **The evidence was consistent with my story and also with the truth,
and I never checked which.**

The corrective is not "be smarter." It is embarrassingly mechanical: when a
diagnosis matters, make the suspect path answer a value it could not produce any
other way, *before* writing the prose. We invented that this morning. It's called
the canary. It took ninety seconds and settled a question two careful readings
had failed at. I then proceeded to not use it, four times, over twelve hours.

## In praise of the pre-registration, which kept saving me from myself

The thing that actually worked — consistently, boringly, without any cleverness
— was writing down what a build must show before running it.

It caught the finding 60 disaster (a rule that shipped a *wrong answer*). It
caught finding 64 being inert. It caught finding 65's fix breaking a superclass
chain. In every case the useful half was **the prediction that failed**, not the
one that held.

And the moment I'm proudest of is a small one: this evening I wrote a
pre-registration saying `typeclass-smoke` must stay red because a compound-head
instance would leave a free dictionary behind — then took the baseline, found
there *was* no such dictionary, and amended the pre-registration *before* the
build rather than reinterpreting it after. That is the whole discipline in one
move. It cost four minutes and it is the difference between a measurement and a
horoscope.

## The blast radius, or: how the machine caught what I didn't

My favourite catch of the day wasn't mine.

I made a small emitter change, predicted a handful of files would move, and the
diff came back with **56**, dominated by e1000 network drivers and DHCP tests
that have nothing to do with unused `let` bindings. I nearly filed that under
"huh, weird" and moved on to celebrate the four green targets.

Running all 56 found `deck-bracket-contract` going `match → differ` — a silently
wrong deck-bracket count, shipped into a build, from a rule I'd written twice.
The wins were all green. The wrong answer was in the files nobody predicted.

**An unexplained blast radius outranks the wins it arrives packaged with.** I've
written that into the register in those words, because I want the next person
who is pleased with themselves to trip over it.

## The compiler has a shape, and we found it by accident

The genuinely good news is architectural and it emerged sideways.

We now have four instances of one thing: **a CST node too weak to carry what the
source plainly says.** `LambdaExpr` with no span. `InstanceDef.type-name` as a
single `Token`, so `instance Showable (List Integer)` arrives as the bare word
`List` — the parser literally calls `skip-to-close-paren` on the rest, which is
at least honest about it. `ErrorTy` meaning two different things. And the IR
carrying instantiations at call sites but not definitions.

None of these was found by looking for them. They were found by porting somebody
else's test suite, in file order, including the boring cases. Case 10 of Roc's
aliasing cluster — `x = [1,2,3]; _y = x; read x` — is about as unpromising a
program as exists, and it found a defect. Its twin case 13 bounded the fix. Case
20 found the *next* defect and proved the fix incomplete.

There's a lesson in there about the value of porting the tedious half of a test
suite, and I suspect it generalises well beyond compilers.

## Where the tooling actually hurt

Three things cost real time today, and none of them were hard problems:

**A stale file nobody deleted.** A `run.jsonl` from the previous day produced 94
phantom regressions and sent me hunting a compiler bug that didn't exist. You
asked "why are we keeping it if it's stale?" — and the answer was that I'd
written a careful warning about not using it instead of typing `rm`. Deleting it
took four seconds and immediately answered a question I'd queued a whole
measurement for.

**A branch that had quietly become a fork.** Every headline number I quoted for
hours described a tree with 29 untracked files, which no git ref described and
which cannot be rebuilt. The MANIFEST faithfully recorded the *checkout* and was
perfectly useless, because the population and the checkout are different facts.

**`git rebase` leaving HEAD somewhere surprising**, twice, which put compiler
fixes on the ports branch. I fixed that with a pre-commit hook rather than a
resolution to be careful, which is the only reason I believe it won't be three.

The pattern: **every one was a place where the tool could have told me and
didn't.** All three now do.

## For the codexzig repo, since you're about to start it

You didn't ask for advice, so treat this as thinking out loud rather than a
recommendation.

The ladder is a *comparison* machine — everything in it exists to make two
things disagree loudly. That's why it's 1300 lines of PRIORITIES and 2200 lines
of register: comparison generates findings, findings generate prose, prose
accumulates.

`codexzig` is a different animal. It's one program, source in, zig out, and its
central property is a fixed point: it re-emits its own bundle byte-identically.
That's not a comparison, it's an *invariant* — and invariants are cheap to state
and cheap to check. A repo built around one invariant might stay small in a way
the ladder structurally cannot.

The two things I'd carry over: **say what population you measured** (the
provenance line is eight lines of code and would have saved me hours today), and
**pre-register anything that costs a guest**. The thing I would *not* carry over
is the register-as-narrative habit. Today I deleted 1100 lines of documentation
that had gone stale, most of it written by me, most of it written in the same
confident voice as the three diagnoses that turned out to be wrong.

## The line I keep coming back to

Damian closed PR 93 with *"this one changed how the compiler talks to every
backend we will ever have."*

It's a generous sentence, and the thing it's generous about is a **missing span
field on one AST node**. Somebody, at some point, wrote `synthetic-span` there
because the node didn't have one to give, and moved on, and it was fine for
years — until a backend arrived that couldn't erase and couldn't guess.

That's the whole project in one image, really. Not heroic debugging. Just being
the first thing pedantic enough to notice.
