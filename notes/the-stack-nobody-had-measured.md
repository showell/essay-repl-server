# The Stack Nobody Had Measured

*2026-08-24. A day's work, in plain terms: one bug, four answers deep,
and the small instrument that kept the chain going.*

## The setting, in one paragraph

We maintain a second, independent toolchain for Damian's Codex compiler.
Codex is written in itself, so compiling anything normally means booting
the compiler as a tiny operating system inside an emulator. Our "plug"
translates Codex into Zig instead, which lets the same compiler run as an
ordinary Linux program. Then we compile the same source both ways and
demand the two results agree byte for byte. Where they disagree, someone
is wrong, and finding out who is the entire point of the project.

## The bug we started with

One of our tools crashed. `zigemit` — the compiler's own code generator,
translated to Zig and compiled to a native binary — was handed a large
input and ran out of stack.

The stack is the scratch space a program uses for function calls. Every
time a function calls another, a little block of memory is set aside for
it, and released when the call returns. Call deeply enough without
returning and you run out.

The input had 3.2 million tokens, and the function that died advanced
exactly one token per call. So: 3.2 million nested calls, each holding a
few hundred bytes. That is roughly a gigabyte of scratch space to do
something that needs almost none.

## Why the real compiler doesn't have this problem

The function looked like this, in spirit:

```
  count (n) (acc) =
   if n == 0 then acc
   else count (n - 1) (acc + 1)
```

Notice the last thing it does is call itself, and it does nothing with
the answer — it just hands it back to whoever asked. That is called a
*tail call*, and it has a nice property: the caller has no work left, so
its scratch space is dead the moment the call is made. A compiler that
notices this can reuse the same block instead of stacking a new one,
turning the recursion into a plain loop. Depth stays flat forever.

Damian's compiler has done this since Update 30, over a year ago. Our
plug never learned to. Every one of those calls was a real call, and the
compiler is full of loops written this way.

Interestingly, the *same commit* that taught the real compiler this trick
also taught the Python plug. Ours was simply missed. It had been latent
ever since.

## Why it took this long to notice

Two reasons, and the second is the interesting one.

First, nothing we ran was ever big enough. Our test programs are small —
the deepest one lexes about five thousand tokens, where the ceiling is
around 1.8 million. A 350x margin. The problem simply could not appear.

Second — and this is the part I did not expect — **it had already
appeared, and been papered over.** Nine days ago someone hit a stack
overflow in an emitted program and fixed it by giving every emitted
program a 512 MB stack. That bought about 1.8 million calls of headroom,
which was enough for everything we ran until the day we pointed the tool
at the biggest input we had.

So "why are we only seeing this now" has an uncomfortable answer: we
weren't seeing it now. We saw it a week ago, made the symptom go away,
and wrote a comment explaining why the big stack was necessary.

## The fix, and the three things that made it awkward

The change itself is old and well understood: turn the self-call into a
loop. Parameters become variables, the tail call assigns their new values
and jumps back to the top.

Three details did the actual work.

**The new values must be computed before any of them are stored.** If a
loop's next arguments read the very variables it is about to overwrite,
storing them one at a time means the second argument is built from the
first one's *new* value. This does not crash. It returns a plausible
number. That is much worse.

**Zig will not let you shadow a function's parameters**, so the loop
variables need different names, and every mention of the parameter in the
body has to be rewritten to point at them. We already had machinery for
that and my first attempt bypassed it, which produced a loop referring to
a variable that did not exist.

**Zig is strict about unused things**, and it is strict in both
directions: a parameter nobody reads is an error, and so is explicitly
discarding one that *is* read. My first two attempts each landed on one
of those. It took three tries to state the rule correctly.

The result: that tool now processes the same large input in 27 seconds on
the *standard* stack, where before it died with four times as much. More
importantly, the program it produces is still correct — it compiles, runs,
and its output matches our recorded reference byte for byte.

## The comment that turned out to be wrong

The 512 MB workaround came with a note explaining itself. It said the
thing that really needs the deep stack is a particular back-and-forth
between two functions in the lexer, and that fixing self-calls would not
help.

That note is the reason nobody looked further. So I measured it.

I fed the compiler a file with 100,000 consecutive lines of prose — the
exact shape the note describes — and gave it a 256 KB stack, two thousand
times smaller than the real one. It ran fine. So did 100 lines. Identical.
The cycle the comment blames is flat: it goes three calls deep and then
unwinds, every time, because of a detail in how the scanner stops at the
end of a line.

A wrong explanation is worse than no explanation. Nobody re-checks a
question that appears to be answered.

## The instrument

At this point I stopped fixing things and built a measuring tool, which
in hindsight should have come first.

It takes the emitted program, rebuilds it with progressively smaller
stacks, and finds the smallest one that still works. That part is
obvious. The part that mattered is what it does when a size *fails*: it
reads the crash report and counts which functions appear most often.

So it answers two questions rather than one. Not just "how much stack do
we need", but "what is on the stack when we run out".

That second column is what makes the tool worth having, and I can prove
it, because of what happened next.

## What it found, and the twist

The tool pointed straight at the parser. Two separate three-function
loops, each going around once per definition in the file, each stacking
frames the whole way. On our largest real document — 4,511 definitions —
that is several thousand nested calls. Both of those loops are made
entirely of tail calls, so none of the frames are doing anything.

Nobody flattens them, though, because every implementation in the
project, Damian's included, only handles a function calling *itself*.
Two functions calling each other in a circle is a different case.

But it does not need to be that case. If the helper functions *return*
what they found instead of calling onward, the loop calls itself and the
existing optimisation handles it. That is a small, self-contained change
to the compiler's source that would pay off on every one of the 44 plugs
at once. I made it.

Then I measured, and the number did not move at all.

The *cycle* column, however, had completely changed. Both parser loops
were gone — the fix worked. What had surfaced underneath was a third
thing entirely: the compiler's sorting routine, recursing ten thousand
deep.

And that one was our own fault. Sorting takes a comparison function as an
argument, and my tail-call change refused to touch any function with a
function-shaped argument, because Zig will not store one in a variable.
Too blunt. That parameter never *changes* — every recursive call passes
the same comparator through. A parameter that never changes does not need
a variable at all; it can stay exactly what it is.

Had the tool only reported pass/fail, I would have concluded the parser
change did nothing and moved on.

## Where it stands tonight

The tail-call work is done and verified. The parser change is written and
its first measurement is honest but incomplete — it cleared its own two
obstacles and revealed a third. The refinement to our optimiser is
written and rebuilding now. I have also written a small unit-test file
that pins the properties this transformation must not break, including
the argument-ordering hazard, since a future version could regress it and
still produce believable answers.

Three things are recorded and none has been sent to Damian yet, which is
its own loose end and now written down as one.

## The bit I would keep

Every step today was a *why* question whose answer contained the next
one. The tool ran out of stack — why? No tail calls. Why did nobody
notice? A workaround hid it. Why did the workaround exist? A reason that
turned out to be false. What is the real reason? The parser. Did fixing
the parser help? Yes, and it exposed a mistake of my own two layers up.

What kept that chain moving was not persistence. It was that one
measurement produced a *description* rather than a verdict. A tool that
says "fails at 24 MB" ends the conversation. A tool that says "fails at
24 MB, and here is what was on the stack" starts the next one.
