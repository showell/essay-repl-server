# Saved, in simple terms

*2026-11-01. LC, for Steve: what roc-chat's Saved feature is, how it works,
and whether it got more complex than the Zig chat's.*

## What it does

You're reading a topic and want to come back to a message later.
1. **Press `s`** (or click "save" on the message). A small popup asks for
   a note, prefilled with "read later". Press Enter.
2. **The strip says** "MSG_Orchard.Banana_12 saved to reading list"; the
   last two words link to the list.
3. **The message shows "✓ saved"** in green from then on, for you only.
4. **Your reading list is at `/chat/saved`,** with a "Saved" link in the
   top bar. Newest first, each entry shows:
   - your note as a heading;
   - who wrote the message, and when;
   - "↩ open in chat", which goes back to the message in its topic;
   - a copy of the message's text, as it was when you saved it.

   Each entry has a box to change the note and a Remove button.

That's the whole feature, the same one the Zig chat had.

## How it works

- **One file per person** on the server holds your list. Each save is one
  line: an id, when you saved it, where the message lives (topic and
  number), who wrote it, your note, and a copy of the text. The server
  reads the whole file, changes it, and writes it back in one go.
- **Saving** is a form post from the popup. The server checks that you
  can read that topic, copies the message's text from its own store (never
  from your browser), adds the line, and answers with the strip's HTML.
- **"✓ saved"** is drawn by the server when it draws the page, because it
  knows which numbers you've saved in that topic.
- **The list page** is plain HTML from the server. Changing a note or
  removing an entry is an ordinary form that reloads the page.

## Did it get more complex? Yes, and here's why

The numbers, old against new:

| | the Zig chat | roc-chat |
|---|---|---|
| popup | 113 lines (JS) | 155 lines (`save.js`) |
| storage and list | 565 lines (`reading_list.zig`) **plus the Docs system** | 989 lines (codec, rules, page) |
| tests | (fewer) | 274 lines (`save_test.js` plus an e2e step), and expects inside the Roc |

**About 40% of the new lines are tests.** The rest is bigger mainly for
one reason.

**The old reading list borrowed a whole subsystem.** In the Zig chat the
list was a *document in Docs*: one markdown block per save. Docs already
knew how to store a document, show it, let you edit it, and let you delete
a block by editing the text. The reading list got all of that for free.
roc-chat has no Docs, so the parts Docs used to do had to be built:
- **a file format,** `SavedCodec.roc`, where a Docs document was just
  markdown;
- **a page,** `SavedPage.roc`, where Docs had its own page;
- **edit-note and remove forms,** where in Docs you just edited the text.

So most of the growth isn't Roc being wordier. It's the reading list now
owning work Docs used to do.

## Where the review added weight

Some complexity came from the cold review. Each piece below answers a real
failure; whether it's worth its weight is your call:

| piece | why it's there | could drop? |
|---|---|---|
| **ids never reused** (a `next=N` mark in the file) | without it, a stale tab's Remove could delete a different save | only by keying forms on something else |
| **an unreadable list doesn't break topic pages** | the old app made that call explicitly; otherwise one bad file takes every topic page down | no, it's the old behaviour |
| **a re-save moves the entry to the top** | closest to the old "append another block" | yes: updating the note in place is simpler |
| **the author's name frozen in the copy** | the old block froze it as text | yes, if a current name is fine |
| **the 1 MiB cap checked on note edits too** | the cap only held on save | it's a small check |
| **the copy outlives losing access** | a save is your own copy, as the old doc was | this is a design choice, not code |

## What I'd simplify, if you want it leaner

1. **A re-save just updates the note in place.** The entry doesn't move.
   That's one less rule and one less test.
2. **Merge `ReadingList.roc` into the codec or the page,** if it stays this
   small. Three modules for one feature is a split by layer, not by
   volatility.
3. **Leave the rest.** The stale-tab and unreadable-file guards are cheap
   insurance against real bugs, and the server-drawn "✓ saved" and strip
   made the JS *smaller*, not bigger.

## The short version

Saved does what it always did. It's bigger because the Zig chat leaned on
Docs, and roc-chat has to own its list. The review added a few safety
rules, mostly worth keeping. Two small simplifications are available if
you want them: a re-save updating in place, and merging one module.
