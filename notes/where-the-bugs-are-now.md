# Where the bugs are now

*Saturday 2026-10-10, written while the v22 plants run. A look at the
last ~40 commits in gopher-metal and the judge's last ~15 in metal-vmm:
what found what, and whether "hunt classes of bugs" still holds as the
main strategy.*

## The short answer

**Class hunts still work, but the class that pays most has shifted.** It
is no longer "a kind of mistake in the kernel". It is **"a fact nobody
checks exactly"**, and today most of those facts were in our own
instruments: tests, plants, floors, the judge, the mutation tools. The
kernel bugs that are left need two faults at once, and the things that
found them were an invariant and cold reviews, not seeds.

So I'd refine the strategy rather than replace it:
1. **Exact accounting** as the main class hunt: the kernel counts
   everything it leaves behind, and the judge holds the disk to those
   counts with no slack.
2. **Every check must be shown to fail**, as standing practice, not a
   one-off audit.

## What found what (the last day)

**Real served-code bugs, five:**

| bug | found by |
|---|---|
| giving clusters back walked into rot or another file's chain | the ledger (an invariant) |
| a rename whose new entry failed lost the file | the ledger |
| a refused delete marker that landed lost clusters | the ledger |
| a rename's undo wrote the boot sector | a cold review |
| TCP took a segment half the circle away as old (in CC's refactor, before merge) | a cold review |

The seeds found none of these directly. Every one of them needs a
*second* thing to go wrong: a lying read, then a refused write; a failed
write, then a failed cleanup.

**Breaks in how changes reach the kernel, two:** my `Mirrors` change and
CC's `Fin` change each broke a kernel that `zig build test` never
compiled. The gates caught one; the structural fix (`zig build check`)
caught nothing yet, because it's new.

**Problems in our own instruments: about twelve,** more than everything
else together:
- a test that could not fail on its own title, and one that asserted
  nothing about its premise;
- both mutation tools counting non-kills as kills;
- a plant on a path no seed reaches (it "worked" for weeks), and a plant
  whose five "catches" turned out to be the judge's false alarms;
- a floor line that held only because of a bug (the round-trip estimate
  before Karn's rule);
- a coverage check that silently skipped, and a stale port that made the
  test suite fail for reasons that had nothing to do with gopher-metal;
- 600 extra replay runs hiding inside the long tier's slowdown;
- **my own judge changes this morning**, which a cold review found would
  have let a deleted file pass as a "counted leak".

## The trends

**1. The kernel bugs left are compound.** Each needs a fault plus a second
fault on the recovery path. Random seeds rarely line those up: one seed
in eight touches the volume at all. The ledger found three of them on
its first run because it doesn't need a seed to line anything up. It
checks an accounting rule on *every* operation.

**2. Invariants beat sweeps for compound bugs.** The ledger is not a test
of any one scenario. It says "every cluster an operation takes ends in
one of four named ways", and any path that breaks that rule fails
wherever it runs. CC said the same in its overnight notes: the ledger
found more than the state-machine matrix did.

**3. Our instruments are now where most of the bugs are.** That makes
sense as the kernel gets cleaner: the checks were written against a
buggier kernel, and some only ever passed because of those bugs. A check
that passes against a clean kernel tells us nothing until we see it fail
against a broken one.

**4. Loosening a judge is the riskiest change we make.** Every excuse I
added this morning to get a green run was, at first, broader than the
fault it excused. The fix each time was the same: replace a blanket
excuse ("a stop may leave anything") with a count ("no more than the
kernel says it left"). The stricter judge then found a real gap within
an hour: the kernel was leaving a long-name part behind without counting
it.

**5. Cold reviews pay every time.** Five reviews in the last day, and
each found something real, two of them in served code. They are the
cheapest instrument we have: read-only, no CPU, minutes.

## The refined strategy

**Exact accounting, extended across the kernel/judge boundary.** The
ledger made the kernel's *internal* bookkeeping exact. Today's change
does the same for *what the kernel leaves on disk*: `leaked_clusters`
and `orphaned_parts` are printed at the end of every run, and the judge
compares them with what `fsck` finds. Every remaining excuse in the
judge should become a comparison like that:
- **"the kernel says it left K; fsck finds no more than K"**, not "a
  stop may leave things";
- **zero slack** as the goal. B41 is the open gap: an unknown write
  outcome is counted as a leak even if it landed, which is room for a
  real leak to hide in;
- the same idea for TCP is already in the lexicon: **custody and debt.**
  The question is whether the judge can hold the wire to the kernel's own
  account of what it owes and has sent.

**Every check is shown to fail, as a standing rule:**
- **each judge excuse ships with a plant it must *not* excuse.** The
  counted-leak excuse would come with a plant that leaks without
  counting;
- **plants live in the source** (B39), so they can't go stale, and a plant
  that never fires is its own failure;
- **the mutation tools check that the tree is green first,** and anything
  they can't classify is a failure, never a kill (147);
- **a floor line says why it can be reached,** and when a fix makes it
  unreachable, we say so rather than tuning seeds.

**Seeds keep their place, aimed rather than blind.** Compound bugs need
two faults in the right order. The explorer already steers toward rare
coverage. Pointed at "a cleanup path ran" and "a second fault hit a
recovery", it should find compound cases far faster than blind seeds.

## What I'd *not* change

- **The frenemy loop.** CC's overnight batch and the box's reviews found
  each other's mistakes all day, in both directions.
- **Red first.** Every real bug above has a test that failed before its
  fix.
- **Releases wait for a clean run.** v22 took three attempts, and each
  attempt found something real: a build break, a floor that witnessed a
  bug, and judge gaps. That's the gates working, at a cost of hours.
