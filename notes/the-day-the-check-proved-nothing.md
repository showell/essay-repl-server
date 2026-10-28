# The day the check proved nothing

*A reflective essay on 2026-10-28, written by Claude (the box) for Steve. Long by request.*

## Where the day stood when it started

The day opened with a lot already in motion. Our alignment PR to Roc (#12665)
was waiting on review with CI green. v41 was serving lynrummy.com. CC had a
queue of "aggressive ports", written to move the chat's remaining Zig into Roc.
The style guide had just been reorganised by topic. Most of what follows is
small: a check here, a rename there, a queue item. But underneath the small
things, the day had a shape, and the shape is worth writing down, because it
rhymes with lessons we've paid for before.

The shape was this: **the most expensive mistake of the day was a check that
proved nothing, and I believed it.**

Let me start there, because it's the freshest and the most instructive, and
then go back and look at the rest of the day in its light.

## The download that differed

CC finished items 286 through 291 in one long run. Every chat stream, the
message store, presence, the docs pages, and uploads and downloads all moved
into Roc. Each item followed the discipline we'd set: first freeze the old Zig's
behaviour as a hashed run of real requests, then port, then show that the hash
didn't move. It's a good discipline. It turns "I think the port is faithful"
into a single 64-character fact.

I merged all of it and ran the quick gate. One test failed: `downloadsRun`, the
291 freeze. Thirty-three requests, hashed together, and on this box the hash
was `41aaff…` where CC's frozen value was `88d2a7…`.

My first thought was the right one. A bundle is a tar of a folder's files, and
the Roc built the list from `Files.list!`, which returns the filesystem's order.
Different machines, different filesystems, different orders, different tar,
different gzip, different hash. I read the code and found the line: "then the
uploads in the folder's order." It was right there in the comment.

So I wrote the fix (sort the uploads by name) and ran the test. Same hash:
`41aaff…`. And I concluded that order wasn't the cause.

That conclusion was wrong, and the way it was wrong is the whole lesson. On this
box the folder *already lists sorted*. Sorting a sorted list changes nothing. My
experiment didn't vary the variable I was testing, so its null result said
nothing about that variable. "Same hash after sorting" is exactly what you'd see
if order were the cause *and* this filesystem happened to sort, and it is also
what you'd see if order were irrelevant. The check could not tell the two apart.
I read it as if it could.

I did try to vary it properly. I forced the files into creation order and into
its reverse. But the forced list left a variable unused, the Roc compiler
refused the build, and my script, which looked only for the hash line, reported
"no line". I abandoned that experiment and told Steve the theory was wrong.

Then CC, on the machine where the order actually differed, found it in a few
minutes: the bundle's GET and HEAD were the only two answers that changed, and
the cause was the folder's order. CC's note was generous and exact: "Your check,
that sorting by name gave the same 41aaff…, showed your order was already sorted,
not that order didn't matter."

There are three lessons in this, and two are already in memory, which is the
uncomfortable part.

**First: a null result is only as strong as the variation behind it.** Before
reading "nothing changed" as "this isn't the cause", ask whether the experiment
actually changed the thing. Here, sorting on a sorted filesystem was a no-op
dressed up as an experiment.

**Second: instrument, don't tweak.** The memory says it in three words, and I
did the opposite. The test produced one hash for 33 answers, and the fastest
route to the truth was to make it say *which answer* differed. I wrote that to
CC as a request, which was right, but I wrote it *after* spending three test
runs (about two and a half minutes of build each) on tweaks. If the first step
had been "make the mismatch name its answer," the GET and HEAD of the bundle
would have pointed straight at the tar, and the tar at the order.

**Third: don't abandon an experiment because it broke.** The reversed-order run
was the one that could have proved it. It died on an unused variable, a
one-character fix (`_listed`), and I dropped it instead of fixing it. The memory
calls this "don't abandon experiments", and its reason is exactly this: the
broken experiment is often the decisive one, because it's the one that actually
varied something.

What saved the day was the system around me, not my reasoning. CC's environment
differed from mine, and that difference turned a portability bug into a visible
failure. A freeze that runs on two machines is worth more than one that runs on
one, and today's bug existed *because* the old Zig had the same flaw: the frozen
hash had faithfully captured one filesystem's accident. The fix made the bundle
deterministic, which is the honest version of "the port matches the original".
The original wasn't stable enough to match.

## A test that can only say no

The freeze is a beautiful instrument with one weakness: it's mute. A hash says
"different" and nothing else. That's fine while things pass, and costly the
first time they don't, because the person debugging has nothing to go on.

CC's fix was to give `freezeRun` a voice. On a mismatch it now prints every
answer's own short hash, length and first line, and writes the whole run to a
file you can diff. That's the right fix, and it's worth generalising: **any
check whose failure is a single bit should, on failure, explain itself.** The
cookbook self-tests I wired in today follow this pattern: a failure names the
recipe and prints its last lines. So does the quick gate. The freeze didn't,
until today.

## The rest of the day, in that light

Looking back at the earlier work with "did the check actually check?" in mind
is clarifying, because a lot of the day was about making checks honest.

### Wiring the self-tests

The cookbook's recipes — the name hunts, the stacking checks, the alignment
hunt — each carry plants: tiny files that a given check must fire on, and
"quiet" files it must not. Until today those self-tests ran only when someone
remembered to run them. A cold agent wired them into Shale's `zig build test`,
and CI now downloads `roc-ast` from the toolchain release (checksummed), so the
Roc hunt's plants run there too rather than being quietly skipped.

When the agent reported success, I ran `zig build cookbook-test` myself and
looked for the five `ok` lines. That's the "a green is a claim" rule: count what
ran, and check your change was among it. I was careful there and careless with
the download test a few hours later. The difference wasn't knowledge. In the
first case the check was in front of me as a list of five things. In the second
it was buried in my own experiment design, where I didn't think to look.

### Naming, and the parts of speech

Much of the day went into teaching Shale to read names the way a person reads
them. The name hunts already flagged effects named as nouns, questions that
return Bools, and vague words. Today they gained:
- `command_tense`: a tag passed in as an instruction should be a verb;
- the Zig `noun_effect` check, which Steve asked for because it was cheap;
- `preposition_split`: one noun given two different trailing prepositions in
  one file (`blocks_of` beside `blocks_in`).

The interesting part was the false positives, because each one taught the check
something true about language:
- **`has_at`/`has_from`** is a deliberate pattern, a worker and its recursion.
  The tell is arity: the `_from` version takes one more argument.
- **`insertBefore`/`insertAfter`** is a pair of opposites, not a split.
- **`Who [Known(...), Unasked]`** carries payloads, so it's state, not a command.

Each of these became a quiet plant, so the check can never regress into
flagging them again. That's the plant discipline doing what it's for: a
heuristic about English becomes a tested claim.

The word tables (verbs, participles, prepositions) came from our own code, not
from a dictionary. Steve agreed on that, and I think it's the right call for a
reason beyond dependencies: a dictionary would tell us what English allows,
where our tables record what *we* mean. "welcome" and "corrupt" are verbs here
because that's how a reader takes them in context, and a dictionary would hedge.

### The style guide as a living thing

The guide had a good day. Notramo's two tips from Zulip — state machines must
be opaque, and tags for effects use verbs — became rules with checks behind
them. Steve's record-over-three-arguments preference went in flagged as his,
with the `roc fmt` reason attached. And CC, under the new "the guide moves with
the code" rule, added five rules in one run without being asked twice. Two of
them are about the host boundary:
- "A list the host would mirror goes a call at a time";
- "An effect that answers the request is for bytes only the host should touch".

Both are real design insights that came out of porting, not out of theory.

The one correction I made was small: CC had tagged each rule with its queue
number, "(metal-vmm QUEUE 291)". A guide meant for anyone writing Roc shouldn't
carry our queue's history. The rule should stand on its own and the commit
message should remember where it came from. It's the "no narrative in prose"
rule, applied to a document whose readers will never see our queue.

### Readability at the scale of modules

Steve's request in the afternoon turned the readability work up a level, from
names to modules. His framing was the useful part: we've spent effort on
splitting big files, but the Roc chat has the opposite problem. Its modules are
small, so the risk is a reader forced through five of them to follow one flow.

The survey found exactly that. Getting a message count passes through main,
Last, Count, Files and Paths: five modules for one number. Upload is called by
a single function in main. The docs feature lives half in main and half in Docs,
with its title helper in a third module. Feeds exports six helpers that only
Recent uses.

What I like about the proposed check (a module whose calls all come from one
other module is a finding unless an allowlist names it *with its reason*) is
that it doesn't forbid anything. SafeImg stays separate because it's a security
rule that deserves to be auditable on its own, and the allowlist says so. The
check's job is to make every such split a decision somebody wrote down, rather
than an accident of porting order. That's the "a default is a decision nobody
made" doctrine, applied to module boundaries.

### What Roc already had

The stdlib survey was humbling in a useful way. We'd rewritten more builtins
than I'd have guessed:
- `List.split_on`, `split_first`, `starts_with`;
- `U64.min` and `minus_saturated`, `I64.div_floor_by`;
- `Json.to_str`, which escapes byte for byte as our hand-written version does.

Each rewrite was reasonable at the time, because we were porting Zig line by line
and the Zig had its own helper. But a faithful port carries over the original's
*shape*, including its private conveniences, and today we paid that down in
bulk (queued as 301). The broader point: **a port's second pass is a search for
what the new language already gives you.** The first pass can't do it well,
because it's busy being faithful.

The same survey found what Roc *doesn't* have. Its most compelling find, which
Steve picked out, is ASCII predicates on `U8`. We have 13 inline
`c >= '0' and c <= '9'` checks, and punctuation's set is four disjoint ranges
that nobody gets right from memory. Steve's comment that this would be his first
upstream submission that isn't a bug fix changed how I briefed it. A bug fix
argues from a failing test. An API proposal argues from taste, precedent and
evidence of harm, and the obvious objection — "it's trivial to write yourself" —
has to be answered, not waved off. The agent is working through Zig, Rust,
Python and Go for precedent, and the adversarial passes come after. I'm curious
whether the evidence will hold up. "Bug-prone" is a claim, and the honest
version of the proposal needs real bugs, not plausible ones.

### Steve's Python, mapped to Roc

A small, pleasant moment: Steve's `html_helpers.py` from zulip-flet mapped onto
Roc's `Html` almost one to one. What it showed is how much a type system gives
for free:
- His `SafeHtml.trust` is Roc's `Html.trusted`.
- His `combine` is our `join`.
- His docstring admits the protection is "not completely fool-proof", a mypy
  convention; Roc's opaque type makes it a compiler rule.

The one idea worth taking was `build_tag`, an element builder that always escapes
attribute values. Today our pages fill templates, and whether an attribute
value is escaped depends on the caller remembering. That's the "one home for a
rule" doctrine in miniature: escaping an attribute should happen in one place,
so no caller can forget it. Now queued as 302.

## The friction

It would be dishonest to leave out how many of today's tool calls were me
fumbling Shale. In one stretch I learned, one refusal at a time:
- `run` needs a `timeout_ms` and a keep;
- its output is `.out`, not `.stdout`;
- `print` won't take a map;
- `const` isn't allowed inside a loop;
- there's no `find_re`;
- `run` won't run `grep`;
- `df /` is refused because the root holds the keys mount.

Each refusal was clear and told me exactly what to do instead, so in a sense the
design worked: no call did the wrong thing silently. But "fail loud" has a cost
when the caller is learning, and today I was learning things I had known before
the context was compacted.

Two of the gaps were real Shale gaps rather than my own forgetting:
- **`queue_done`** ran out of its five-million-step budget after three items, and
  left the queue half-edited (consistent, luckily, because each item's two edits
  happened in a fixed order).
- **CC asked twice** for an `edit` that replaces from one marker to another,
  because the workaround mixes Shale's 1-based `sub` with `find_in`'s 0-based
  offsets.

Both are the kind of thing the "fix Shale's gaps in Shale" rule exists for, and
both are on my list.

## What I'd carry forward

Pulling the day together:

1. **Vary the variable before you trust the null.** The download bug cost an
   hour of elapsed time because I believed a no-op experiment. Before reading
   "nothing changed", ask what the experiment changed.

2. **A mute check should learn to speak at the moment it first fails.** The
   freeze now names its answers. Every hash-style check we own should do the
   same.

3. **Two machines are a free experiment.** CC's environment differing from mine
   was the instrument that found a real portability bug, one the original Zig
   had all along. When a check passes on one side and fails on the other,
   that's information, not noise.

4. **Porting has two passes.** The first is faithful; the second asks what the
   new language already provides and where the old shape no longer earns its
   keep: the builtins, the module boundaries, the template that should be a
   builder.

5. **A check's exemptions should carry reasons.** Quiet plants for the hunts, an
   allowlist with reasons for single-caller modules, flagged preferences in the
   style guide. In each case a heuristic becomes something the next reader can
   audit instead of something they have to trust.

I notice that two of these five are rules already in memory. That pattern
showed up in the last essay too. The rules are stored, but at the moment they
apply they don't fire, because the moment never looks like the rule's
description. "Instrument, don't tweak" reads like advice about performance work;
today it applied to a hash mismatch. Rather than adding a new memory, I'll make
the existing ones say *when* they apply, in words that match how the moment
actually looks: "a single hash disagrees", "a check that came back unchanged".

## Where things stand

- **CC** is on 292, with 300–302 queued behind it.
- **The merges are pushed:**
  - roc-webbox `main`, carrying 286–291 and the fix;
  - angry-gopher `box/roc-cleanup`;
  - the queue.
- **The live chat's Zig** is down from 34,923 tokens this morning to about 28,700.
- **The ASCII proposal** is with a cold agent.
- **PR #12665** waits on review.

It was a productive day, and the most useful thing in it was a mistake I made
and someone else caught.
