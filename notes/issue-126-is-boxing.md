# Issue 126 is the boxing fix, and the gap has two faces

Issue 126: the hosted compiler types every comparison `error` where bare metal
says `boolean`. We filed it as a second site of the class PR 117 fixed — an
`address-of` that no hosted target can answer, so a type binds `ErrorTy`.
Today's question was whether our boxing fix (PR 135) resolves it. It does, and
chasing it down made the whole class legible.

## What we measured

The clean experiment is: build the compiler two ways whose only difference is
the three boxing commits, and read how each types a chapter of six comparisons.

- **Clean Update 57 (no boxing): the compiler does not build at all.** The zig
  plug refuses at `zig build-exe` time: `@compileError: no address-of for
  codexir.IRPat`, and the same for `codexir.IRActStmt`. There is no hosted
  compiler to ask.
- **Update 57 plus the boxing fix (the u58 candidate): it builds, and it types
  all six comparisons `boolean`.** The `error` symptom is gone.

Bare metal has always typed them `boolean`, because bare metal boxes every
variant value and `address-of` there is the identity.

## The gap has two faces, and boxing closes both

`address-of` on an unboxed, payload-carrying variant has two outcomes depending
on whether the site has an unsafe escape:

- **No escape → a compile-time refusal.** `IRPat` and `IRActStmt` are reached
  by `address-of` through the Update-55 lowering memo-copy, with no fallback, so
  the zig plug emits `@compileError` and the compiler will not build. This is
  the "it stops the zig build of the compiler itself" line in PR 135, now
  confirmed live at Update 57 and with the exact types named.
- **An unsafe escape → a runtime wrong answer.** The type-box that `check`
  validates is reached through `mcopy-type`, which has an unsafe escape rather
  than a refusal: it reads page fill and binds `ErrorTy`. Nothing crashes, the
  program still runs, and every comparison comes back typed `error`. This is
  issue 126.

Both are the same defect — `address-of` resting on a representation choice the
plug made for sizing rather than on the language's model — and the boxing fix
closes both by boxing *every* payload-carrying variant, so `address-of` is
total the way it is on bare metal.

## Why the attribution is sound without a matched failing run

The tidy proof would be a no-boxing hosted compiler typing `error` beside the
boxed one typing `boolean`. That proof cannot exist at Update 57, because the
no-boxing compiler does not build — the compile-time face of the same gap stops
it. So the attribution rests on three facts instead, and they are enough:

1. The class is `address-of`/`ErrorTy`, by the issue's own analysis and by PR
   117 before it.
2. The boxing fix addresses exactly that class, so completely that removing it
   breaks the build on the escape-less members of the very same set of types.
3. The only hosted compiler that builds at Update 57 is the boxed one, and it
   types every comparison `boolean`.

The `error` symptom in the issue belonged to an earlier, partially-boxed hosted
compiler that still built. The full fix — box every payload-carrying variant —
is what PR 135 sends.

## What this means for the two open items

PR 135 is not a convenience. At Update 57 there is no hosted compiler without
it. And COMPILER-56 (issue 126) is the runtime face of the gap PR 135 closes,
so it should close when PR 135 lands. Both are now one fix, not two.
