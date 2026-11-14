# The Shale book in sessions, with Session 7

**Read it here:** http://143.244.172.148:9210/shale-book/

The book is now ten chapters, numbered by session instead of by weekday, and every build gate passes. I'd like your reply on one question: does the sessions framing read better than the week did?

## The chapters

1. **Introduction**
2. **One loop:** one real turn of the loop, with its diagram.
3. **Session 1: a server and a number**
4. **Session 2: replies that stay put:** with the anchoring diagram (same text, else same neighbors, else most similar, else orphaned).
5. **Session 3: a check for each moment:** with the fast, full and release diagram.
6. **Session 4: making the checks fail:** fixtures and fault seeding.
7. **Session 5: shipping should be boring**
8. **Session 6: the language gets better:** the jobs feature, and the release as parent and child, with its diagram.
9. **Session 7: a feature arrives:** bare URLs become links. This is new.
10. **How we work**

## What changed with sessions

- **The honesty line.** The introduction says once, plainly, that the sessions aren't days: the build took an afternoon of agent time, and the links feature came the next morning.
- **The journals keep their names.** `journal/monday.md` is the record, so the includes still name it. One sentence explains why; a gate holds every other weekday in prose to zero.
- **No cap at a week.** Session 7 fits naturally, and so would Session 8.

## Session 7, the links feature

The prompt asked for the minimal, safe thing: only bare `http://` and `https://` in prose, nothing in code, sentence punctuation stays outside the link, and the URL escaped like everything else. The chapter shows the fixture cases and the one seeded fault that proved the escaping test catches it.

It's live on your surface now, so the link at the top of this note should be clickable there.

## Still running

A cold agent is moving Shale's regex helpers into builtins. When it reports, I'll review it and run the three gates before merging.
