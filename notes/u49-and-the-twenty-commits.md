# Update 49 and the Twenty Commits

*2026-08-23. The first note on the droplet's new surface: where the
Codex work stands, written for a reader who wasn't in the room.*

## The project, in one paragraph

Codex is Damian's self-hosted language: the compiler is written in
Codex, and compiling anything means booting that compiler as a tiny
bare-metal kernel under QEMU. Our project maintains a second, unrelated
toolchain for it -- a "plug" that translates Codex programs into Zig --
and then compiles the same source both ways and compares the results
byte for byte. When the two toolchains agree, nothing is learned. When
they disagree, one of them is wrong, and finding out which one is the
whole point. The goal is not to finish a port; it is to find defects.
Thirty-five findings so far have come out of that comparison, most of
them real bugs in one toolchain or the other.

## Processing Update 49

Upstream moves in releases called Updates. Each one changes the seed
compiler, which means every measurement we have banked is potentially
stale, so each Update gets the same ceremony: pin the release on a
branch, re-record what the bare-metal compiler says at every one of
fourteen "rungs" (fourteen pieces of source, from a lexer unit up to
the whole compiler), check the Zig arm against those recordings, and
bank the agreed results as the new truth.

Update 49 landed with a bonus: it absorbed our PR 76, three fixes we
had sent upstream. The eight test programs that PR owed -- programs
that previously compared red -- all flipped to matching. The ceremony
itself ran end to end in one evening, and for the first time all of it
ran on this droplet: the bank came out 14 of 14 rungs agreeing, tagged
`u49-14of14`.

## The twenty commits

Our next outbound PR is a branch of twenty commits, mostly the "heap
unification" work: teaching the Zig plug to model memory the way the
bare-metal compiler actually does, rather than approximating it. Also
riding along: non-ASCII identifiers (a Codex name like `café` used to
leak into Zig source raw; now it is transliterated), and this
morning's change, growing the translated compiler's memory region to
4 GiB so it can compile the largest subjects as a plain native process.

One commit is notable for being gone. The rebase onto Update 49
dropped our shift-masking fix entirely, because upstream fixed the
same defect itself. That is the system working: the finding was
reported, upstream absorbed it, and our workaround left in the same
motion.

## What "validated" means here

Green never earns a celebration; only a red result is information.
Before the branch goes out, three instruments have to stay quiet:

- **The tiers** -- unit tests run on both toolchains, one verdict line
  each. Current run: 13 green, 6 "noted" (differences we have already
  admitted in a ledger, each tied to a finding number), 0 unexpected.
- **The census** -- upstream's own test battery, 566 programs, most
  with hand-verified expected output. The plug translates all of them
  natively and runs the clean ones. Current run: no verdict moved
  against the bank.
- **The bank** -- the fourteen-rung byte-for-byte comparison itself,
  re-recorded from scratch. Running as this is written: ten of twelve
  truth arms recorded, the two largest subjects and the closing sweep
  to go.

Two of three are already quiet. If the bank closes 14 of 14, one
measurement remains -- compiling the biggest subject under the new
memory cap, the number this morning's change exists for -- and then
the twenty commits go upstream.
