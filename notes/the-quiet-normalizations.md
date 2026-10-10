# The quiet normalizations

*2026-10-10, evening, written while the gates run. Open-ended: a pattern I
noticed in today's work, and what I think it says about where the remaining
bugs live.*

## Four things that looked unrelated

Today we fixed four things that didn't look alike at the time:

1. **`zig build check` said "NOT type-checked" and passed.** A stale port
   made it skip the kernel, it printed a line about it, and it exited 0. A
   kernel that didn't build reached a commit.
2. **The store tokenized paths.** `data//chat/x.md/` became `data/chat/x.md`,
   silently, in the store seam, in `io.zig`, and in the FAT driver's own path
   walk. Three layers, each politely fixing the same mistake for its caller.
3. **The judge's leak excuse had a ceiling and no floor.** "fsck finds no
   more than the kernel counted" let an over-count become room for an
   uncounted leak to hide in.
4. **`.lastauthor` went away, and with it a fallback** nobody had named as a
   feature. The Who cell would have gone blank for some sessions, quietly,
   instead of being wrong or being right.

What they share is that **each one took something that should have been a
decision and turned it into a default.** The check decided "a skipped kernel
is fine". The path walker decided "you probably meant one slash". The judge
decided "fewer than counted is fine". The `.lastauthor` cut decided "unknown
is fine", which might be right, but nobody had decided it.

I've started calling these **quiet normalizations**: code that receives
something slightly wrong and makes it slightly right without telling anyone.

## Why they're attractive

Every one of them was written with good intentions, and most were written by
people being careful.

- **They make the happy path work.** A tokenizer that skips empty parts never
  fails on `data//x`, so nothing upstream has to be careful about joining.
- **They look like robustness.** "Be liberal in what you accept" is real
  advice, for a protocol talking to strangers. Inside one program, it's
  something else: the caller and the callee are the same author, and
  liberality just moves a bug from where it was made to where it's
  noticed, which is usually much later, or never.
- **They're invisible in tests.** A test of the happy path passes either way.
  The only test that sees a normalization is one written to look for it,
  and nobody writes that test for a behaviour they don't know is there.

That last point is the important one. **A quiet normalization is a feature
nobody specified.** It has no test, no doc, no owner. It is load-bearing in
ways nobody can list. When the `.lastauthor` cut removed one, it removed a
behaviour (an author shown after a failed sidecar write) that no test named
and no person asked for, but that you'd notice was gone.

## The judge is the place this matters most

The kernel has quiet normalizations, and we found them today. But the judge
having them is worse, for a structural reason: **the judge is the thing that
is supposed to notice everything else's.**

When the leak excuse had a ceiling and no floor, it wasn't papering over one
bug. It was papering over a whole class: any kernel that over-counted
anything. And because the judge said "green", nobody would look. The day's
pattern, from the morning's blanket excuses to tonight's floors, has been the
same move every time: **replace an excuse with a comparison**, and then make
the comparison two-sided.

There's a deeper version of this I keep coming back to. The judge's
excuses exist because faults leave real mess, and the mess must be allowed.
But every excuse is a place where the judge stops looking. The kernel's
exact accounting (148, 152) is what lets the judge keep looking: the kernel
says "I left K", and the judge holds fsck to K. The excuse becomes a claim
the kernel makes and the judge checks. **That's the only kind of excuse
that doesn't decay**, because a kernel that lies about K fails.

## "Fail, never warn", and its limit

Your rule from today, fail over warn, is the general cure. A warning is a
quiet normalization with a printout: the system decided to continue, and it
told a log file nobody reads. I filtered the check's output for "error" and
missed the "NOT" line, which is exactly how warnings work in practice: they
are written for a reader who isn't there.

But there's a limit worth naming, because it's where the next bugs are: **a
failure is only as good as its trigger.** The check now fails on a stale
port, but only because someone thought to ask whether the port was stale.
The path walkers now refuse empty parts, but only the three we found.
`angry-gopher`'s `metalShape` still counts depth by tokenizing; there may be
others. The rule tells you what to do when you find a normalization. It
doesn't find them.

What finds them, today at least, was three things:

- **Writing a test of the oracle.** I was writing `store_model`'s bad-path
  list, put `a//b` in it, and the test said it was a fine path. Writing
  tests for the simplest component, the one you trust, is where you
  discover what you trusted without checking.
- **A second reader.** You read "`a//b` is actually valid" and asked why. I
  had treated it as a fact about the code; you treated it as a decision
  someone made. That reframing is most of the skill.
- **Cold reviews asked the right question.** "Is any excuse a blanket rather
  than a comparison?" found the judge's. A review prompted with "find
  quiet normalizations: inputs accepted and silently corrected" would
  probably find more. I'd like to run that one across the stack some
  evening: the store, `io.zig`, the router, the judge's scripts.

## On search, and patience

You mentioned CC is taking a while on search. I think the reason is related.
Search looks like one feature, but by the time the queue item was revised it
had four hard edges, and each one is a place where a quiet normalization
would be easy and wrong:

- **The tokenizer** is a pile of tiny decisions (edge punctuation, curly
  quotes, bytes past ASCII, what counts as a word), each of which a
  regex would "just handle" and a careful implementation has to name.
- **The boundary** (`visibleConvs`) is the leak-prevention guarantee, and it
  has to hold on every request, not most.
- **The oracle** (`/admin/search`) matches substrings while the index
  matches tokens, so "agrees with the baseline" needed restating before it
  could even be tested. CC has to build the restated comparison and then
  make it pass.
- **Mutation tests** are, by design, slow: each mutant is a rebuild and a
  test run. CC running them means it's checking that its tests can fail,
  which is exactly the "every check is shown to fail" rule.

So I'd read the time as CC doing the work the rule asks for, rather than
being stuck. If it's still quiet in an hour, a one-line FEEDBACK asking for
a progress note is cheap.

## A small proposal

Not a decision, just something I'd like to try:

**A "quiet normalization" hunt, as its own cold review**, once the current
batch settles. The prompt: find every place a function accepts an input it
would refuse if asked directly, and corrects it instead of refusing: path
joins, trims, case folding, defaults on missing config, `catch` into a
value, `orelse` with a plausible fallback. Each finding is either a
documented decision (with a test that names it) or a refusal. The store
lint (`lint_store_absence.py`) already does this for one shape, a read's
failure turned into a value; it found 67 sites when it was written.
The general version is broader and fuzzier, which is why it's a review and
not a lint.

The deeper hope is the one from this morning's essay, refined: **the bugs
left are where something is decided by default instead of on purpose.**
Exact accounting made the kernel's leftovers a decision. "Fail, never warn"
made the tools' skips a decision. The next step is making the inputs'
corrections a decision too.
