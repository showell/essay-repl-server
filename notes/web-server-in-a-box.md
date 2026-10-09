# Web server in a box: what memory is for

*Written 2026-10-09, evening, following [our lexicon](our-lexicon.md),
whose roles of a copy (source, mirror, cache, derived, hint) this builds on.
"Web server in a box" means gopher-metal, with any site in it.
angry-gopher's chat is one possible consumer, and appears only as an
example.*

## The machine, reduced

Take away the details and the web server in a box is three things:

- **A disk**, which holds facts that are settled. Something was written,
  and its writing finished.
- **A network**, which brings questions in and takes answers out.
- **Memory**, in between.

Seen this way, the whole job is two sentences long. **Record durable facts
on the disk, and present them to the network as cheaply as possible.**
Memory is the tool for the second sentence, and the danger to the first.

We've been describing memory by what it holds: caches, derived values,
hints. That's accurate, but it describes the inventory, not the role. Here
is a sharper statement of the role.

## Memory holds nothing that has been promised

**Every byte in memory may be lost at any instant without the machine
having lied.**

A promise is anything the machine says that a client may rely on later: a
`303` after a form, a `200` on a save, "your key is revoked". A promise
may only be made about something whose source is the disk. So the line
between promised and not promised has to coincide exactly with the line
between disk and memory.

`durable.zig` is the guard on that line. A reply that announces a change
waits until the change has reached the disk, and only then crosses into
the network. With the write cache off, "reached" means "is on the media".

The rule says what memory may hold, by what its loss costs:

| kind | what it is | if it's lost | examples |
|---|---|---|---|
| **reconstructable** | a copy of something settled: a cache, a derived value, a hint | the next read, or the next boot, rebuilds it from the disk | the page cache, the folder cache, the held FAT, the free count |
| **retryable** | something in motion and not yet promised | the client never heard "done", so it asks again | a request half read, a write not yet committed, a reply held for its flush |
| **forgettable** | a fact whose source is memory, and whose protocol already allows losing it | the protocol recovers: a reset, a reconnect | TCP connections, the request heap, the log ring before it's kept |

Anything that fits none of the three is a bug, and you can hunt for it by
thought experiment. **Point at any byte of memory, pull the plug, and ask
two questions:**

1. **Did we just lie?** If yes, a promise escaped before its fact reached
   the disk.
2. **Will the next boot rebuild it, or will its loss go unnoticed?** If
   neither, it's a fact with no durable source, and memory was its only
   home.

This week's disk bugs fail one of these two questions:

- **The rotted FAT copy written over the good one**, and the tie that
  followed: a copy in memory was used as if it were the source.
- **The cache turned back on by a reset:** memory's belief "the cache is
  off" was a copy of the disk's mode page, and nothing re-read it after the
  disk changed. A stale cache of the device, used to decide when to promise.
- **The overwrite that deleted first:** between the delete and the new
  entry, the only copy of the file's new state was in memory, and the old
  one was already gone. Fixed today, so that the disk always holds a whole
  file.
- **A counter that restarts at 1 when its file is lost** (in the app, but
  the same shape): a derived value with a stored copy and no rule for
  rebuilding it from the source. It should be the highest id that exists.

## Memory is where facts change shape

If the first role is a constraint, the second is the reason memory exists.

The disk keeps facts in the shape that is **safest to write**:
- appends;
- one sector as the commit;
- chains of clusters;
- names folded to what FAT can hold.

The network asks for them in the shape that is **fastest to send**:
- a whole page;
- a whole file;
- a listing, in order.

**Memory is where one shape becomes the other.** Every such reshaping is a
derived value of the disk, so it can always be thrown away and done again.
Efficiency is the art of not doing it again needlessly.

That gives three rules for presenting facts cheaply, and the kernel
already follows each:

1. **Reshape once per change, not once per request.**
   - The page cache keeps whole files after their first read.
   - The folder cache keeps directory sectors; v20's version took a chat
     send from 466 disk requests to 88.
   - The held FAT keeps the allocation table in memory: 507,904 bytes,
     which spares a disk read on every allocation.
2. **Cache what can't change freely; cache what can only behind the one
   door every change goes through.**
   - The site's own files ship with the boot image, and nothing changes
     them while it runs. A cache of a source that can't change never needs
     invalidating, so it's the perfect cache.
   - The volume does change, so the page cache sits under `io.zig`, which
     sees every write, append, rename and removal. Its rule is **exact, or
     absent**: what it holds for a path is what the disk holds, or it holds
     nothing, and after a failed write it holds nothing.
3. **Bound everything, because everything in memory is disposable.**
   - The page cache has a budget, a slot count and a largest file.
   - The request heap shrinks back after each request, so a ten-megabyte
     upload doesn't leave ten megabytes reserved for the rest of the boot.
   - Memory never grows with the disk.

   Bounding is safe only because of the first role. You can only evict what
   you can rebuild.

## Memory is a function of the disk

Put the two roles together and the cleanest description of memory is this:

> **Memory is a function of the disk, plus whatever is in motion.**

**Boot computes that function.** It reads the disk, checks it, holds the
FAT, and fills caches as requests come. A reboot computes it again, and
that is why a reboot is the ultimate reconcile: whatever memory got wrong,
the next boot gets right, provided the disk is the source of everything
that matters.

This also explains a metal-vmm idea that is parked for now. A whole-machine
**snapshot** saves memory after boot so that runs can start from it. That
is valid only because memory is a function of the disk image and the boot,
which is deterministic. The snapshot is just a cache of that function's
result.

Read this way, a design question about memory becomes a question about
the function:
- Is this value *in* the function, so a boot rebuilds it?
- Or is it in motion, and unpromised?
- If it is neither, why is it in memory at all?

## A fact the client holds

One fact in the box has its source neither in memory nor on the disk.

**A session cookie is a fact whose durable source is the client.** The
server stores no session table. The cookie carries "this browser is user
p2", signed, and the signature is what makes a copy held by a stranger
trustworthy. It's an elegant answer to the first role: the session costs
memory nothing and the disk nothing, and a reboot loses no sessions.

It also shows that role's limit. A fact whose source is the client can't
be withdrawn by the server. Logging out clears the browser's copy, but any
other copy stays valid for its 365 days. That's why the cold agent's
"incarnation" proposal puts one small fact back on the disk: a value per
account that every cookie must match. That makes the disk the source of
"is this still valid?", while the client stays the source of "who am I?".

## Isolation, for free

ACID's I sits quietly in all this. **One handler at a time, run to
completion** (HOST.md) means memory has one writer at any instant. No
request sees another's half-done change, and no cache needs a lock. The
single-writer rule is part of why the page cache can be both simple and
exact.

It is worth knowing as a cost too. The day a second handler runs at once,
every "exact, or absent" claim needs re-proving, and so does every
reconstructable copy.

## What this gives us to work with

**Two questions for any byte of memory**, the ones from the pull-the-plug
experiment:
- If it vanished now, would we have lied?
- Would the next boot rebuild it, or would its loss go unnoticed?

**One rule for any reply:** answer from memory; promise only from the disk.

**One rule for any copy:** say its role, whether mirror, cache, derived or
hint, and give it that role's rule for a disagreement.

**One measure of efficiency:** how often a fact is reshaped, against how
often it changes. The ideal is once per change.

**One measure of correctness:** a reboot at any instant leaves the
machine exactly as truthful as before, and only less warm.

That last phrase, *only less warm*, may be the shortest description of
memory's role. **Memory makes the box fast; it must never be what makes
it right.**
