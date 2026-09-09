# What desk-hover is, and why it was the wrong thing to chase

You asked what `desk-hover` even is. Fair question, because the name hides
almost everything about it. Here is the whole picture, in plain terms, and then
an honest account of why it came up, why it was a distraction, and whether it is
U55 or U57 work.

## First, what it is

`desk-hover` is one *unit* in our test corpus. A unit is a single `.codex` file
we feed to the checker. This one is 75,369 lines long.

But almost none of those lines are about hovering. The actual test is the last
sixty lines of the file, a chapter called `DeskHoverTest`. It does two small,
pure things:

- It checks **hover dwell**: you rest the pointer on a pill on the desktop, and
  after 400 milliseconds a preview bubble is allowed to appear. The test feeds
  in fake clock values (10000, 10399, 10400 ticks and so on) and asserts that
  the "held long enough" and "ready to show" answers flip at exactly the right
  tick. The clock is passed in as a parameter, which is the only reason the test
  can exist at all, since a real capture with a frozen clock could never satisfy
  a dwell.
- It checks **bubble placement**: given a pill near an edge of the screen, does
  the preview bubble get nudged back on-screen. A pill four pixels from the left
  would start at -15 and should be pushed to 0; one near the right would run off
  and should be pulled back.

That is it. It is a small, sensible unit test for a desktop hover interaction.

## So why is the file 75,369 lines?

Because the corpus stores each unit **fully resolved**. The sixty-line test
cites `GopDesk` and `BoxModel`, those cite more, and so on down through the
entire graphical stack: the desktop, the browser, the box model, layout,
fonts, the network stack, WebSocket, SHA, and about two hundred chapters more.
The resolver bundles the test together with every chapter it transitively needs
into one self-contained file, dependencies first, the test last.

So `desk-hover` is not really "a hover test." It is "a hover test plus the whole
operating system it runs on, flattened into one file." That distinction is the
whole point of what follows.

## Why it came up

We have a gate that checks four counters the type-checker keeps, ours against
the reference compiler, over every unit. After a couple of fixes this week that
gate went from disagreeing on everything to agreeing on all but a handful of
units. `desk-hover` was one of four related units, the `desk-*` family, still
disagreeing.

The disagreement was narrow and identical across all four: the reference
compiler minted exactly 32 more *row ids* than we did. Row ids are an internal
counter tied to how the checker tracks effects. Nothing else differed, not the
type variables, not the recorded expression types. A clean, small, shared
signature, which usually means one shared cause worth ten minutes.

## Why it was the wrong thing to chase

I bisected `desk-hover` by chapter to find where the count first parts, and it
pointed at the `WebSocket` chapter. That looked like a lead. It was not.

There is a 1,414-line unit, `encode-web-socket`, that contains the very same
`WebSocket` chapter with only its own real dependencies. I checked it directly.
It **agrees exactly** with the reference compiler, 4918 rows on both sides.

So `WebSocket` on its own is fine. The 32 extra rows appear only when
`WebSocket` is checked *inside* the giant `desk-hover` environment, alongside
two hundred other chapters. That makes this an *interaction*, not a bug in any
one chapter. The likeliest shape is a name that resolves to a slightly
different function, with a different number of arguments, once the larger
environment is in scope, which changes how many rows get minted at the call
site. That is the same class of thing as the chapter-scoped name collisions we
have seen before.

You called this exactly right in the moment: we were chasing a much larger
subject than we should. `desk-hover` only came up because it happened to be
first in the family. The real subject, if we ever want it, is a small
constructed reproducer, not a 75,000-line unit, and the bisection on the big
unit was actively misleading.

A method note for next time: bisecting at chapter boundaries is sound, because
dependencies always resolve backward, so a truncated prefix never breaks a
reference. Bisecting *inside* a chapter is not sound, because definitions in a
chapter freely reference each other in any order, and a truncated chapter makes
the reference compiler refuse. And a divergence that vanishes when you isolate
its supposed cause was never localized there in the first place.

## Is this U55 or U57 work?

Almost certainly leftover U55-era work, not anything U57 introduced.

The gap is in how we account for effect rows, which is one of the areas the Rust
front end has approximated from early on, back when it had several known gaps
against U55. Row and effect accounting was one of them. Nothing in U57's actual
changes touches how many rows a call site mints, and `WebSocket` is a stable
library chapter that did not meaningfully change between the updates. The reason
we are only seeing it now is not that it is new. It is that the counter gate
became readable for the first time this week, so its residual is finally worth
reading, and this is part of that residual.

## What we are doing about it: nothing, for now

This is corner-case coverage of the language, and that is deliberately not where
the effort goes yet. The order of business is validating U57 and refining the
U58 candidate branch first. We have not even run safari against this pin yet.

So the finding is parked, written down, and left alone: the `desk-*` four
diverge by 32 row ids through an environment interaction, not a local bug,
`WebSocket` is a red herring, and the fix, when it is worth making, starts from
a small reproducer rather than the desktop. It waits its turn behind the work
that actually gates the release.
