# Where the deck bracket goes missing

## The question

`opening.codex:798` says this:

    let (ir-raw, lower-keep-end) = deck-record (lower-chapter ...)

and the emitted zig says this:

    switch (lower_chapter(ch_1, bound, cst, ...)) { .MkTup2 => ...

The `deck-record` is gone. Not mis-emitted -- **gone**. There is no
`cx_deck_enter`, no `cx_deck_exit`, and no call to the identity `deck_record`
function that the same file also defines and never calls.

That matters because `lower-chapter` opens with a deliberate unmatched
`__deck-exit`: it exits an extent its caller opened. With no extent, `cx_nest`
goes to -1, `cx_deck_enter` stops swapping the cursors, and every copy the
lowering compact makes lands in the bivy that `__heap-restore` is about to
reclaim. One missing bracket disables the deck for the rest of the run.

The interception works 1,267 times in the same file. It misses once. The
question is which layer loses it.

## Do we need each layer to print something?

No. **Every layer already prints, and in ASCII.** The instinct to add
instrumentation is the instinct that cost the most time this week, and it is
not needed here:

| layer | ASCII we already have |
|---|---|
| source | the `.codex` file |
| AST | rust arm: `parsedump`, `desugardump` |
| checked | rust arm: `checkdump` |
| IR | the seed's own `IR-UNI` mode; rust arm's `irdump` |
| IR after passes | `IR-UNI` again, with the pipeline flag varied |
| zig | the emitted `.zig` |

`opening.codex`'s dispatch names the modes outright: CDX, TEXT, IR-UNI,
IR-CCE, MEASURE, DISK, RESOLVE. We have been feeding ourselves IR-CCE all
along because that is what the transport wants, and IR-CCE is a wire format --
which is why `grep deck-record` on a 10 MB `.ir` returns zero and tells us
nothing. IR-UNI is the same content in text.

So the strategy is not "make each layer emit something". It is **stop reading
the compressed one**.

## The real lever is the subject, not the loop

Tonight's win was shrinking the loop from seven minutes to under two seconds.
The next win is shrinking the *subject* from 2.6 MB of compiler to about ten
lines of Codex.

The shape under suspicion is narrow:

    let (a, b) = deck-record (f x)

A tuple destructuring whose scrutinee is a `deck-record` application. Both
sites that lose the bracket -- `opening.codex:798` and `:861` -- have exactly
this shape. Every one of the 1,267 sites that keeps it is, as far as we have
looked, an ordinary single-value binding.

If a ten-line chapter with that destructuring loses its bracket, the entire
question collapses to one file you can read end to end, with its IR-UNI beside
its zig, both short enough to eyeball. If it does *not* lose the bracket, then
the shape is not the trigger and we have eliminated the leading theory for the
price of one second.

That experiment costs less than reading the emitter does. It goes first.

## What `usedfor` can answer before we run anything

`usedfor deck-record codex/` classifies every call site by what consumes it --
the tool exists, it reads the whole checkout in about three seconds, and this
is precisely the question it was built for. It answers:

- how many `deck-record` calls sit in a destructuring position at all
- whether those two `opening.codex` sites are alone or the tip of a class
- whether any *other* consumer shape is unique enough to be suspect

If the destructuring bucket has exactly two members and they are the two known
sites, that is close to a proof by itself, and it arrives before any compile.

## Then, and only then, read code

There is one question worth reading for, and it is small and named:

> Does `emit-zig-apply` ever see this application, and if it does, why does
> `n == "deck-record" & list-length args == 1` fail?

Three candidate answers, in the order I would test them:

1. **The emitter never sees it as an application.** A destructuring lowers to a
   match, and the scrutinee may be emitted through a path that does not route
   apply chains through `emit-zig-apply`. Read the match/scrutinee emitter.
2. **An IR pass removed it.** The diagnostics say
   `PIPELINE fold-constants,inline-leaf-calls,inline-single-caller` on every
   build. `deck-record` *is* the identity function in source -- a perfect
   inline-leaf candidate. If a pass inlines it away, the name is gone before
   codegen and the intercept cannot fire. Test by varying the pipeline flag,
   not by reading: two IR-UNI dumps, diffed.
3. **The root is not `IrName "deck-record"`.** Renaming, cite resolution, or
   the bundler's `subj-` prefix could make the root a different name in this
   position. `subj-deck-record` already exists as a separate emitter rule that
   emits the argument alone -- identity, no bracket -- which is the exact
   failure we observe. That rule deserves a hard look regardless of what else
   is true.

Candidate 3 is the one I would bet on, because the identity behaviour it
implements is byte-for-byte the behaviour we are seeing, and because the
`zig-skip-def` comment says the intercept is *obliged* by skipping the def --
an obligation stated in prose is an obligation nothing checks.

## The fix that should land regardless

    fn cx_deck_exit() void {
        cx_nest -= 1;                       // unconditional
        if (cx_nest == 0) { ... }
    }

A negative nest silently disables the deck. Nothing complains, nothing fails,
and the damage surfaces thousands of allocations later as a corrupt switch in
a constant folder. Refusing at `nest == 0` -- panicking, loudly, naming the
caller -- converts that into a one-second failure that points at
`lower_chapter`. I know it does, because that is exactly what happened the
moment I added it by hand.

This is the fail-loud floor and it is worth having whether or not it is our
bug, whether or not the bracket is ever restored, and whether or not anyone
ever reads this paragraph. A cursor discipline that cannot detect its own
violation is not a discipline.

## Order of operations

1. `usedfor deck-record` -- three seconds, may localise it outright.
2. The ten-line destructuring subject through the fast loop -- two seconds.
3. IR-UNI of that subject, with and without the pipeline -- two dumps, diffed.
4. Read the one emitter path the first three have implicated.
5. Land the `cx_deck_exit` refusal independently of all of it.

Steps 1 through 3 cost under a minute together and will almost certainly make
step 4 a five-minute read instead of a spelunk. That ordering is the whole
lesson of the last two days: the measurement was always cheaper than the
theory, and I kept reaching for the theory first.
