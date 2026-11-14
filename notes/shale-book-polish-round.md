# The Shale book: the autonomous polish, done

**Read it here:** http://143.244.172.148:9210/shale-book/

While you were away, the book went through two review rounds and three edits. It's 11 chapters, every gate passes, and it's on dev at `54c8eb3`.

## How the rounds ran

- **Four cold reviewers in parallel,** each with its own brief:
  - **a newcomer** to agents;
  - **a fact-checker** against the journals and git history;
  - **a line editor;**
  - **an arc reader** for the story and its seams.
- **One editor** applied a triaged list of about 30 fixes, to keep one voice. It then read the whole book once more, to fix the seams its own edits made.
- **A fresh flow reader** read it at reading speed, looking only for broken seams, drift in voice, and terms used before they're defined. It found 17 seams, and an editor fixed them.
- **A second fresh flow reader** found only small things: one-sentence fixes, plus a tangle where Session 5 hands off to Session 6. A last editor fixed those. Its verdict: one voice, mostly, and the worst seam was the one now fixed. I stopped there, because the findings had shrunk to single sentences.

The reviewers' briefs live in `book/personas/`, next to `lessons.md`, so any later round can reuse them.

## What changed that you'll notice

- **Facts the record contradicted,** now fixed:
  - Session 4's plant had a stage name but no CPU budget, the reverse of what the book said.
  - Session 2's first simulation panicked; the next two timed out.
  - "Doubles" is now the measured 1.7 times.
  - A claim about seeded faults in Session 6 had no record, so it's cut.
- **The regex cost was wrong.** The book blamed the steps on the Shale loop; the true cause was the regex charge. Session 7 now pays this off: the move happened the same day, a second language change the work asked for.
- **Session 6's order is now plain.** The feature was built the afternoon before. Your "go ahead with the jobs feature" approved the merge, and the session is the merge and its gates.
- **Each term is defined where it first appears.** One loop's glossary is gone, since every term in it is now defined in the prose. `want` is defined once, in Meet Shale.
- **The setup, in a paragraph.** The agents run in Claude Code, its shell tool runs only Shale, and your replies reach the agent through the orchestrator.
- **The checks diagram moved to Session 5,** where the release becomes the third gate. Session 3 had shown the release two sessions before it existed.
- **Dialects are argued once, in Session 6,** with a pointer from Meet Shale.
- **How we work** collects the lessons of Sessions 5–7 and ends on a real last line.
- **Session 7 is now "links, the boring way",** so "a feature arrives" no longer blurs with Session 6.
- **Every quoted block now comes from a file.** I added Session 7's release output and One loop's stored reply to the essay-surface journal, after checking both against the session record.

## Two things for you

1. **Session 7's new title.** "Links, the boring way" was the arc reader's suggestion. Keep it?
2. **A "trying this yourself" section.** The newcomer asked how to get Shale, what a session costs, and what to do without Shale. I skipped it: the book has no record of costs, and whether to point readers at the repository is your call.

## A correction

Earlier I told you the regex change cut step counts "6–20×". The benchmark's real range was 5.7× to 24×, and the two cases Session 7 cites are about 20× and 24×.
