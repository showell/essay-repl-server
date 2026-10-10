# Searching all of chat

*2026-10-10, late night. How gopher chat's search works today, what
changes when it reaches across every topic a person can see, and the shape
I'd propose. A thinking document, not a plan yet.*

## How search works today

Search lives entirely in the browser (`chat/chat_search.js`). The server
plays no part in it.

- When you open a topic, the server streams the **whole transcript** to the
  page over SSE: every message, rendered to HTML. There is no window or
  paging; the page holds all of it in an array, `records`.
- Opening the search box builds a **token map** from `records`: words split
  on whitespace, edge punctuation trimmed, lowercased, two characters or
  more, each with a count and its most recent message.
- **Phase 1, autocomplete:** as you type, matching words are listed, prefix
  matches first, then by count.
- **Phase 2, results (Enter):** a linear scan of `records` for the chosen
  word as a substring (smart case), shown rendered and highlighted, oldest
  first; choosing one jumps to that message.

It's fast because the data is already in the page, and narrow for the same
reason: it sees one topic.

## What "all of chat" means on disk

- **A topic** is one file: `<conv>/sessions/<sid>.md`. A conv is a DM
  (`<a>_<b>`, one folder per pair) or a channel (`channels/<name>/`, with a
  members file). Messages are appended blocks of id, author, date and
  markdown.
- **What a person can see** is every DM they're half of, every channel
  they're a member of, and every topic in each. The server already walks
  exactly this list for the sidebar and for Recent.
- **Messages are only ever appended.** An edit is a new message ("Edit of
  MSG_…"). The only deletion is the admin's retire tool, which removes
  whole topics or whole DMs. Channel membership can change, which changes
  what a person may see.
- **Ids are unique only within a conv**, so a result must carry its conv.
- **Volume:** a handful of people, about 1,000 messages a week at the
  busiest pair. Over a year that's on the order of 10 MB of transcript text
  in total, tens of MB at most. Small for a computer, but not small for
  **one request**.

## The constraint that shapes everything

**gopher-metal runs one handler at a time.** A handler runs to its end
before any other request is served. HOST.md says it plainly: "a slow
handler is a bug on metal already."

A search that reads every transcript inside one request blocks every other
person for as long as it runs. Cold, 10 MB of transcripts on production's
volume is ~320 disk requests at ~5.8 ms each: **about 2 seconds of the site
frozen for everyone**, and longer as chat grows. That's the "squeezing out
other users" you named, and it's exactly what has to be designed out.

So, your two candidate mechanisms:

### (a) Searches that yield in the middle

There are two ways to yield.

1. **The browser drives the slices.** The search is many small requests:
   "search the next topics, at most ~256 KiB of reading", and the reply says
   where to resume. Each request is bounded, and between any two of them the
   kernel serves whatever else is waiting. **No change to either host.** It
   uses only what exists: a bounded handler, and `readAt` for positional
   reads (Recent's tail reads already work this way).
2. **The host yields.** A new kind of "kept job" that the host runs a slice
   at a time between handlers, as it serves kept SSE streams today. It's
   more elegant for the client, but it's **a new host contract on both
   hosts**: the scheduler, the judge and the simulations would all learn
   it. That's a lot of machinery for one feature.

I'd take (1). Fairness then comes for free from how the kernel already
works, and a slice's cost is a number we choose and can test.

### (b) Search keys on disk

An index saves re-reading. The question is **when it's written**.

- **On every send**, at the fan-out point where `images.md` and `code.md`
  are fed today: the index is always current, but every send gains disk
  writes. You just picked cuts to bring a send from 38 requests to 9, so I'd
  keep the send path out of it.
- **As a derived value, built by the search itself**, in the lexicon's
  terms a *cache* with a rule on disagreement: per topic, a small token file
  stamped with the transcript's size, as `.count` already is. A search
  reads a topic's token file if its stamp matches the transcript; if not, it
  rebuilds it from the transcript within its slice and writes it back. **A
  send writes nothing new**, and an appended topic just gets a stale stamp.
  The next search notices and redoes that one topic.

Because the transcripts only grow, a stale token file can even be extended
rather than rebuilt: tokenize from the old size to the new one.

## The shape I'd propose

1. **Autocomplete across everything, from the token files.** The search box
   opens with today's instant token map for the open topic. In the
   background, the browser pulls the token files topic by topic in bounded
   slices (building the stale ones as it goes) and merges them into the
   suggestions as they arrive: "142 topics searched" climbing in the status
   line. With warm token files, this is a few small reads per slice.
2. **Results, also in slices.** After Enter, the browser asks only for the
   topics whose token files contain the word, a few per request, and the
   server returns matching messages (id, conv, topic, author, date,
   markdown; rendering on demand, since HTML rendering is a cost we pay per
   message today). Results stream into the list as they come.
3. **Access is checked per slice, at read time**, against the same walk the
   sidebar does. Token files sit beside each topic, so a person who leaves a
   channel loses its topics the moment the walk stops listing them; nothing
   to invalidate. Retiring a topic removes its token file with its other
   sidecars.
4. **A slice's budget is a constant, and a test:** at most N disk requests
   (or bytes) per search request. The judge can hold that too: no search
   request may exceed its budget, measured like store-cost does.

## What I don't know yet (yours to decide)

- **What counts as a match:** words (today's tokens) or arbitrary
  substrings? Token files make words cheap and substrings expensive. Today's
  phase 2 is a substring scan after picking a word, which works if the
  autocomplete picks the word.
- **Scope and order of results:** newest first across all topics, or
  grouped by topic? Does a result open the topic and jump to the message,
  as today within one topic?
- **Whether DMs with people you've never messaged count:** today every user
  is a potential DM partner, so "all your DMs" walks one folder per pair
  that exists. That's fine at a handful of people.
- **How much autocomplete matters versus results.** If autocomplete must be
  global and instant, the token files have to be warm, which argues for
  building them at boot (`backfillAll` already walks every topic once) as
  well as lazily.

My suggestion for a first step, if this shape suits you: CC builds the
token-file format and its stale-stamp rule as a pure function with tests on
the host, and measures one full cold pass with store-cost's instrument, so
we know the real numbers before the UI changes.
