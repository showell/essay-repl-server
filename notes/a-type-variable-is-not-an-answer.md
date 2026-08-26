# A type variable is not an answer

*2026-08-26*

Update 50's ceremony stopped at the gate. `codexzig_build.sh` — the
crown-jewel artifact that compiles the compiler's own chapter set through
the zig plug and then tries to *build* the result — emitted 47 copies of
the same zig error:

    error: use of undeclared identifier 'T38'

`T38` was declared, 73 times, as `comptime T38: type`. The 47 failures used
it somewhere else entirely, in functions that take no comptime parameters
at all. A type variable was escaping the definition that quantified it and
landing in a scope that had never heard of it.

This note is what it turned out to be, and the answer to the question worth
asking about any defect a new instrument finds on its first outing:
**did we just break this, or did we just look?**

The short answer is *we just looked*, and the evidence is unusually clean.
The longer answer has a sting in it, which is the part I'd keep.

---

## What the wire actually says

The whole defect fits in five lines of intermediate representation. Here is
a thirty-line Codex program whose two rows differ in exactly one thing —
whether the mapped function has a name — compiled by the seed:

    map-list      : (tvar 23 -> tvar 24) -> (List (tvar 23) -> List (tvar 24))
    mapped-named  : apply (apply map-list bump)    xs      -- bump : int -> int
    mapped-lambda : apply (apply map-list __lam_0) xs      -- xs   : List int
    __lam_0       : (params (param "x" (tvar 23))) (fn (tvar 23) int-default)

Read `__lam_0`'s signature. Its parameter type is `tvar 23` — which is
`map-list`'s **own** type variable `a`, unresolved. That looks like a
compiler bug and it is not one. A lambda written inline gets *lifted* into
a top-level definition, and the driver runs that lift **after** the resolve
pass. So a lifted lambda carries the types it was *handed* at the call
site, not the types resolution later worked out.

This is not folklore. The C# plug states it outright, in prose, above the
function that handles it:

> A lifted lambda reaches this plug with UNRESOLVED type variables in its
> signature: the compiler's IR-CCE lift runs after the resolve pass, so a
> `__lam_N` def carries the expected types its lambda was handed, not the
> resolved ones.

C# answers `dynamic` and moves on. Zig has no `dynamic`, so the zig plug
has to actually recover the type — and it has machinery for exactly that.
It walks each of the callee's declared parameter types against the type
actually supplied, in step, and answers with whatever sits where the
variable sits. Declared `List a` against actual `List Integer` answers
`a = Integer`. If a pair doesn't mention the variable, it tries the next
argument.

## The bug is the sentinel

"This pair doesn't mention it" was signalled by returning the empty string.

Now match `map-list`'s declared first parameter, `(a -> b)`, against
`__lam_0`'s actual type, `(tvar 23 -> Integer)`.

The walk finds `a` in the declared position. It reads what is sitting in
the corresponding actual position. That is `tvar 23`. It renders it, gets
the string `"T23"`, and returns it — **and `"T23"` is not the empty
string.** So the scan stops, satisfied, believing it has resolved `a`.

It never reaches argument two, `xs`, whose declared `List a` against actual
`List Integer` is the answer that was wanted and was sitting right there.

The emitted zig puts the two rows side by side, and I don't think the
defect has ever been easier to see than this:

    fn mapped_named(xs: *CxList(i64)) *CxList(i64) {
        return map_list(i64, i64, ... p0: i64 ... return bump(p0);    ...);
    }
    fn mapped_lambda(xs: *CxList(i64)) *CxList(i64) {
        return map_list(T23, i64, ... p0: T23 ... return __lam_0(p0); ...);
    }

Same function, same list, same element type. One of them names a type that
does not exist.

**A recovered answer that is itself a variable is not a resolution.** That
sentence is the entire fix. Concrete beats variable; variable beats
nothing. A variable answer is *kept* as a last resort rather than refused,
because inside a generic definition it is the correct answer — `map-list`'s
own body calls `map-list-loop`, and there `T23` really is a comptime
parameter in scope.

## The detector that a plausible answer walked past

The part I find most instructive is that this plug had already built a
detector for this exact gap, and the detector could not fire.

The recovery function ends in a deliberate `@compileError("zig plug:
unresolved type variable T<id> of <callee>")`, and there is a paragraph
above it explaining, at length, why a named marker is better than the
`anyopaque` it replaced — that ten silent failures read as one mystery
rather than ten facts.

That marker sits on the "no answer" path. A variable answer looked like
success, so the code that reaches the marker was never executed. **A gap
detector that a plausible wrong answer walks past is not a detector.** The
failure isn't that nobody thought about this; someone thought about it
carefully enough to write a good error message for it.

There were also *two* copies of the walk — one answering text for the type
argument list, one answering a type for substitution — with two different
sentinels, `""` and `VoidTy`. The prose above them claimed "the walk is
shared and only the answer differs." It wasn't shared. It was copied. I
wrote the fix twice before collapsing them into the one thing the comment
already claimed they were.

And there was a second half from the same root. With `a` recovered, the
closure the plug builds around a function value still carried the variable,
because it read the lambda's type without passing it through the enclosing
call's own bindings. And since `__lam_0` really is emitted generic —
`fn __lam_0(comptime T23: type, x: T23) i64` — it was being *called* as
`__lam_0(p0)`: one argument against two. The trampoline is a call site like
any other and had never learned to apply a generic callee.

The plug's own notes predicted this, six sites ago: *"A GENERIC NAME MUST
BE APPLIED, and nothing enforces it centrally — six sites had to learn
independently... Expect a seventh."* This was the seventh.

---

## So: introduced, or latent?

**Latent, and the evidence is not circumstantial.**

**The defective code is byte-identical to what shipped in Update 44.** The
recovery walk and the comptime-parameter machinery both entered the tree at
`ff1d299b`, six Updates ago, when the zig plug first landed. Here is the
line as it was written then, and as it still was this morning:

    is TypeVar (vid) -> if vid == id then emit-zig-type actual else ""

Unchanged. The accept rule beneath it — `if text-length found > 0 then
found` — likewise unchanged. Nothing in Update 50 touched it, and neither
did any of the eight PRs we landed into Update 50.

**The trigger is unchanged too.** The whole of `codex/compiler/IR/` is
byte-identical between the Update 49 pin and the Update 50 pin — an empty
diff, not a small one. `ListUtils.codex`, which defines `map-list`, is
byte-identical. The five comprehension sites in `Lowering.codex` whose
lifted lambdas produce the failing calls exist, unchanged, at both pins. So
neither the defect nor the shape that trips it is new.

What changed is that something finally looked. Two of them, both ours, both
in the twenty-four hours before the gate fired:

- **`codexzig` was built and wired into the ceremony.** It is the first
  artifact that takes the compiler's own chapter set through the plug and
  then attempts to *build* the emitted zig. Transpiling had always
  succeeded; nobody had been compiling the result of this particular path.
- **A stale `ir-emit-roots` list was corrected the same morning** — we had
  copied four roots where upstream has six, in both harnesses, so no oracle
  on either side could see the drift. Fixing it widens what gets emitted at
  all.

There is one honest gap in this account and it should stay visible. I have
established that the *code* and the *trigger source* predate Update 50. I
have **not** re-run the Update 49 pin through the same gate to watch it
fail, because that costs a QEMU chain and the box is busy verifying the
fix. The claim "Update 49 would have failed here too" is inference from two
identical trees, not a measurement. It is a cheap measurement and it is
worth taking.

## The sting

While writing this I went looking for whether the corpus had ever shown the
same symptom, and it had: two programs, `typeclass-poly` and
`typeclass-smoke`, refusing on `use of undeclared identifier 'T16'`.

That entry is in our own priority queue, with a parenthetical:

> `use of undeclared identifier 'T16'` (a 16-element tuple; `Tuple` defines
> Tup2..Tup5 only)

`T16` is not a 16-element tuple. `T` followed by an integer is precisely
how this emitter renders a type variable; it is the same string as the
`T38` that stopped the release. Somebody read a plausible meaning into it,
wrote the plausible meaning down, and the queue has carried that reading
ever since — filed as a missing tuple arity, which is a boring gap nobody
would prioritise, rather than as an escaping type variable, which is the
defect that later stopped an Update.

I rebuilt the natives with my fix and re-ran both programs. **They fail
exactly as before**, same errors, same count. So it is the same *symptom
class* by a *different route* — those come from typeclass dictionary
construction, not from a call to a generic definition — and it is still
open. My fix does not touch them and I am not going to claim it does.

But it means the class had been visible in our own corpus, in our own
queue, for weeks. It didn't need Update 50 to surface. It needed someone to
read `T16` as what it says instead of what it looks like.

---

**What is fixed, and what it was measured against.** The reproducer goes
red to green and matches bare metal. `native_build.sh` builds `codexir`
again: 47 errors to zero. The IR feeding that build is 8,669,320 bytes —
byte-for-byte the size it was in the failing run, which is how you know
nothing above the emitter moved.

A six-leg verification chain is running as I write this: the gate itself,
the full sweep any emitter change owes, the tier set, and the corpus
census. The census is *expected* to move, because the unresolved-type-
variable marker now fires where a variable answer used to pass silently.
That is the detector working for the first time, and it should be read as a
measurement rather than as a regression.

**And one blind spot worth more than the fix.** `lift-lambdas` belongs to
the driver, not to the IR pipeline. So `native/codexir` — the fast native
front end everything cheap is built on — never produces a `__lam_N` at all.
`corpus_run.py`, `tier_run.py --zig`, and with them the entire tier set are
structurally incapable of posing this question, and all of them stayed
green through the whole failure. The tiers were not wrong. They were
answering a question that could not contain the defect.

That is the thing to keep. Not the sentinel bug — sentinel bugs are
forever. The lesson is that a green suite is a statement about the
questions the instrument can ask, and it is worth knowing, in advance and
in writing, which questions each instrument cannot.
