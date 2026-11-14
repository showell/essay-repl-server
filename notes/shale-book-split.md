# Splitting the introduction: the big ideas, then Shale

You lost steam at "A language that changes", the introduction's last section. I see why: the introduction now carries two subjects. One is the ideas that reach past Shale: late-2026 agents, missions and standards, prompts, the essay surface, gates. The other is a tour of Shale itself. The tour comes last, after the bigger ideas, so it reads as an afterthought.

Here's the split I'd make.

## Chapter 1, Introduction: the ideas that last

- **Shale, in its first two paragraphs, as now.** A language written by agents for agents; you read it, your agent writes it. It's the book's central tool and new to every reader, so it stays at the top.
- **Who this book is for.**
- **Agents in late 2026.** Principles that last, requirements as the bottleneck, missions and standards instead of skills files.
- **The project, and sessions.**
- **We, and the prompts.** The first prompt sets the mission, follow-ups enforce standards, some improve the workflow.
- **Gates,** as the closing section. Gates are the book's thread, and they transcend Shale, so they make a strong last word. A two-sentence handoff follows: "Gates need a language to write them in. Next, a short tour of Shale."

That cuts the introduction to about 650 words, from 899, and it ends on its strongest idea.

## Chapter 2, a new interlude: Meet Shale

A shorter, lighter chapter, in interlude style, that re-introduces Shale and shows it:
- **It looks like Lua on purpose** and mostly works like any mainstream language. Show one short, real script from the project, quoted from its file, so the reader sees Shale before reading about it. `scripts/fast.shale` is a candidate: small, and it runs on every edit.
- **What Shale adds.** The five bullets move here from the introduction: budgets, a folder and its mounts, a reason for a risky program, one-line stops, the prelude. Each now points at a line in the script above.
- **Shale builds nothing itself.**
- **A language that changes.** Dialects, and Session 6's change, framed as what's to come. Here it's at home, beside the rest of Shale, instead of orphaned at the end of an introduction about bigger things.
- **The words the reader needs next.** `tail`, `want`, `whole` and `must` move here from One loop's glossary. The last cold reader flagged them as insider terms: One loop uses them before saying what they are.

About 500–700 words.

## Then One loop, and the sessions

One loop becomes chapter 3, unchanged except that its glossary loses the Shale terms the interlude now covers. The book's order becomes:

1. Introduction
2. Meet Shale
3. One loop
4. Sessions 1–7
5. How we work

## One question for you

**Does Meet Shale come before One loop or after it?** My recommendation is before. One loop is full of Shale, and the reader should meet the language before reading a real turn of the loop in it. After would put the workflow first and let the loop motivate the language, but then the reader hits `want` and `tail` cold, which is the insider problem again.
