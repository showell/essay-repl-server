# Our lexicon

*Written 2026-10-09, evening. The list behind it comes from
`tools/lexicon.py` (output in `tools/lexicon-output.txt`). The program
compares each word's rate in metal-vmm's QUEUE.md, QUEUE-ARCHIVE.md and
FEEDBACK.md (about 24,000 words of prose) with its rate in the box's man
pages (6.7 million words of technical English). Words like "file", "error"
and "write" cancel out, and what's left is ours. It leaves out the names of
repos, tools and people.*

*A cold agent was asked to write this. The API's content filter stopped it
before it had written anything, so the box wrote it instead. Treat it as
less cold than the essays before it.*

## What the list says

**The top of the list, by how much more we use each word than the man
pages do:**

| word | here | in the man pages |
|---|---|---|
| sweep | 53 | 0 |
| unhurt | 15 | 0 |
| judged / judge | 40 | 7 |
| explorer | 43 | 3 |
| excuse | 41 | 3 |
| refusal / refuse | 70 | 397 |
| blind | 24 | 3 |
| knob | 46 | 15 |
| floor | 53 | 33 |
| seed | 141 | 469 |
| red | 81 | 361 |

**And the phrases.** Several that never appear in the man pages:
- *red test*
- *red first*
- *unhurt run*
- *power cut*
- *cold review*
- *blind run*
- *real kernel*
- *read back*

Read as a whole, the vocabulary falls into four groups:

- **The experiment:** sweep, seed, knob, draw, fire, cut, lie, flood, rot.
  The words of someone running trials and turning dials.
- **The verdict:** judge, unhurt, excuse, oracle, gate, floor, red, green.
  Who decides whether a trial passed.
- **The roles:** box, cloud, cold, review, finding, proposal, question.
  Who said what, and how much it should be believed.
- **Behaviour, in plain verbs:** answer, say, refuse, hold, keep, reach,
  lose. These are the most surprising, and I come back to them below.

Almost nothing on the list names a *claim*:
- "fact" appears 7 times;
- "promise" 12;
- "invariant" 5;
- "forbidden" twice;
- "owner" never.

We have a rich language for *running* things and *judging* runs, and a thin
one for *what must be true*. The postmortem came to the same conclusion
from another direction: the judge was asking the wrong question. That
question, "is it the same as unhurt, unless excused?", is built from the
words we had. The better question, "did anything forbidden happen?", needs
words we mostly didn't use.

## The load-bearing words

**Unhurt.** It's the best coinage on the list, and it's ours. "The baseline
run" would have said *when* it ran, but "unhurt" says *what was done to it*:
nothing. One word carries the whole comparison method. Its weakness is the
one the cold agent's question #4 found: "unhurt" quietly suggests "right",
and it isn't. An unhurt run is only the run nobody hurt. If the kernel is
wrong with no faults at all, every comparison with it certifies the bug.
Keep the word, and stop letting it mean "correct".

**Excuse.** 41 uses, and it did real work for a week. It also encodes a
stance: a difference is guilty until a fault excuses it. That stance is why
the list of excuses only grew. Each new one needed a review, and each
review narrowed it. Keep the word for what it is, a reason a difference is
allowed, but stop treating excuses as the judge's main vocabulary. The new
judge's words are **rule** and **forbidden**. "Forbidden" appears twice,
which shows how far we have to go.

**Refuse.** Used more than any word but the roles, and it carries a
doctrine: when the kernel can't be sure, it says no loudly rather than
guess. A name past ASCII is refused. A write onto a folder is refused. A
cluster size no volume has is refused. "Failure is never absence" is the
same doctrine in the app's words. It's a good word because it makes the
kernel the actor, which matches how we want the kernel to behave.

**Answer and say.** We wrote "answer" 95 times and "say" 105 times. "The
guest answered 500", "the boot says so", "a knob that never fired is said".
That's unusual for systems prose, which usually says "returns" or "logs".
The reason, I think, is that both words name something *a person outside
the machine can see*. An error that's returned but never said is invisible.
These two words quietly hold our rule that the kernel must speak about what
went wrong, and they're the reason "silence" became a bug class (123).

**Red.** "Red test" appears 32 times and "red first" 9. "Red first" is a
whole working agreement in two words: a finding arrives as a test that
fails on the old code. It's the most successful bit of shared vocabulary
on the list. Nobody ever has to explain it.

**Cold.** "Cold review" and "cold agent": a reader with no context and no
stake. It works because it names the property that makes the reader
useful, which is knowing nothing, rather than their job.

**Seed, knob, draw, fire.** The fault machinery's words, settled and
precise. "Fire" became important today: 124(e) is "an excuse needs its
fault to have *fired*, not only been *drawn*". It's a good example of a
distinction that only became sayable once we had two words.

## Words doing two jobs

- **Tier.** "The long tier" (a gate: `long.sh`) appears 7 times. Today's
  plan adds "fault tiers" (ordinary and rare). Two meanings, one word, both
  in the judge's neighbourhood. Rename one: **class of fault** for the plan,
  or keep "tier" there and say "the long gate".
- **Door.** The exit door, the coverage door and the request door are
  three ports with three jobs. That works only because the qualifier is
  never dropped. "The door" alone appears three times, and each time a
  reader has to guess.
- **Seed.** FAULT_SEED, the explorer's seeds and a simulator's seeds are
  three different generators. Context has saved us so far.
- **Shape.** Production's shape (PCI with a volume) and request shapes
  (`requests/shapes/`). The first is older and rarer; "production's
  machine" would free the word.
- **Floor.** Coverage floors (`floor-sim.txt`), and also a "floor" for
  limits. In practice "floor" means a ratchet: a list that may only grow.
  That is a fine meaning; say it.

## Words to add

The brief was at least one noun and one verb that don't appear in the
docs. I checked each one against all three documents.

### Noun: **owner** (0 uses)

*The one place a fact lives; every other copy is a cache of it.*

> "The FAT's owner is the first copy on disk; the held FAT and the second
> copy are caches, and the mirror weighing is a cache that disagreed with
> its owner."

Today's best idea was "one fact, one place, one atomic step", and it needs
this word. Without "owner" we say "which copy is authoritative" every time,
and we said it badly four times about the FAT copies. With it, a design
question gets short: **who owns this fact?** A copy with no owner is a bug
waiting for its first disagreement, like the kept free count, the two
cache flags or `.lastauthor`.

### Verb: **falsify** (0 uses)

*To try to show a stated claim false, by a test, a seed or a reading.*

> "CC falsifies the box's overwrite fix: the claim is 'old or new, never
> gone'; the attempt is a cut at every write."

We call the frenemy loop "attack" and "review". Both name the activity
without naming the target. "Falsify" forces the claim to be written down
first: you can't falsify "the fix", only "the fix makes `write` old or
new". That's the scientific-method framing you raised. A claim nobody can
falsify isn't a claim, and the habit would have caught 125's
recipes earlier: their claim, "this is the status the guest gives", was
falsifiable on a guest and never tried.

### Two more worth having

- **witness** (noun, 0 uses). *The smallest thing that lets someone else
  check a claim: a seed and its knob line, an image, a red test.* "A finding
  without a witness is a phenomenon" puts your old rule in one sentence. A
  queue item would then carry its witness, as most of the good ones already
  do.
- **reconcile** (verb, 0 uses). *To bring every copy of a fact back to its
  owner.* Mirror repair, the folder cache dropping a failed sector, boot
  re-deriving the free count, and the plan's "reconciliation at boot is
  normal operation" all do this. Today they have no common name, so they
  get designed one at a time.

## Words to retire or sharpen

- **"Excuse" as the judge's centre:** keep the word, but move the weight
  to **rule** and **forbidden**.
- **"Unhurt" as "right":** sharpen it to "the run nobody hurt".
- **"Today"** (40 uses, up from the man pages' 54 in 6.7 million). A
  QUEUE item that says "today" is wrong tomorrow. Dates, always.
- **"Lie"** (22) is vivid, and right for a disk that claims write-through
  and caches. Keep it narrow: a fault, never a description of a bug.

## A glossary, as we use the words

| term | what we mean |
|---|---|
| sweep | many seeded runs of the real kernel, each judged |
| seed | one number that names a run's whole fault schedule |
| knob | one fault setting; drawn by a seed, or set by hand |
| fire | a drawn knob's moment came, and it took effect |
| unhurt run | the same request with no knob turned: the run nobody hurt, not the right one |
| judge | what decides a run passed: rules first, the page comparison second |
| excuse | a reason a difference from the unhurt run is allowed; needs its fault to have fired |
| rule / forbidden | something that must never happen, checked on every run, which no fault excuses |
| refuse | the kernel saying no, out loud, rather than guessing |
| answer / say | what someone outside the machine can see; the kernel must say what went wrong |
| red first | a finding arrives as a test failing on the old code |
| cold | a reader with no context and no stake |
| plant | a deliberate bug, never merged, that the judge must catch |
| floor | a ratchet: a list that may only grow |
| class | a kind of mistake, hunted across all the code |
| fact | one thing the system holds true about itself |
| owner | the one place a fact lives; the rest are caches |
| reconcile | bring every copy of a fact back to its owner |
| witness | the smallest thing that lets someone else check a claim |
| falsify | try to show a stated claim false |
