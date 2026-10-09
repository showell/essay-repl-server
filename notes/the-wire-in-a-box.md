# The wire in a box: custody, belief and debt

*Written 2026-10-09, evening, as the network layer's counterpart to
[web server in a box](web-server-in-a-box.md). The vocabulary comes from
`tools/lexicon.py`, run on the comments of gopher-metal's `tcp.zig`,
`stream.zig`, `proto.zig`, `arp.zig`, `net.zig`, `netcore.zig`, `dhcp.zig`
and `tcp_check.zig`, plus `docs/tcp.md`. The output is in
`tools/lexicon-tcp-output.txt`. TCP should be faithful to its RFCs. This
essay is about the words we use to show how ours is built, and which tasks
it has to get right.*

## What the comments already say

Measured against the man pages, the network code's comments lean hard on a
small set of words:
- **acknowledged** (35, against 6 in 6.7 million words of man pages)
- **room** (27)
- **shut** (17)
- **behind** (17)
- **carry** (19)
- **queued** (25)
- **bounded** (20)
- **said / answer / say** (88 between them)
- **wait** (66)
- **turn** (44)

The phrases "next turn", "half open", "send queue" and "peer last [said]"
also stand out.

The code names point the same way:
- `transmit`, `pump`, `handle`;
- `una`, `rcv_nxt`, `wnd`;
- `window_news`, `update_at`, `rto_at`, `fin_wait_ns`;
- `recycle`, `reclaim`.

Two things stand out:

- **The comments talk about TCP as a conversation.** The peer "says" it has
  room, we "answer" with a reset, a window that reopens is "said again",
  and a FIN "goes last". That's no accident. A connection really is two
  parties keeping one conversation straight over a wire that loses, delays
  and duplicates what they say.
- **They are obsessed with waiting, and rightly.** `tcp.zig` and
  `stream.zig` each open with a section titled "what waits, and what bounds
  the wait". `tcp_check.zig` holds the same list as a liveness table. No
  other part of the kernel documents itself this way.

## The network has no source

The disk essay rested on one rule: **the disk is the source of every
durable fact.** Every copy in memory is a cache, a derived value or a hint,
and a disagreement is settled by going back to the source.

**The network breaks that rule.** A connection's facts live in two
machines, and neither one is authoritative:
- How many of our bytes has the peer received? The truth is in the peer's
  memory. We know only what its last acknowledgement said.
- How much room does the peer have? The truth is in its buffer. We know
  only its last window.
- How long is the path? Nobody knows. We estimate from samples.

So the network's version of the disk essay's question is not "what is the
source?" but **"what did the other side last say, and how much is that
worth?"** Its answer needs three ideas the disk didn't: **custody**,
**belief** and **debt**.

## Three duties

### Custody: hold every byte until it is receipted

An acknowledgement is a **receipt**: "I hold every byte before this
number." The rule follows directly:

- **A byte we sent stays in our custody until the peer receipts it.** `tx`
  holds `tx[tx_start..tx_end]`, every byte not yet acknowledged; a timeout
  sends from `una` again. A byte may leave custody in only two ways: by a
  receipt, or by giving the whole connection up.
- **A byte we receipted is in our custody until the reader takes it.**
  `rx[start..end]`. We told the peer we have it, so we have it.

Custody is where the disk essay's "memory holds nothing promised" meets its
one honest exception. **Every ACK we send is a promise, and it lives only
in memory.** That is allowed because TCP lets a connection be lost, but
only *whole* and only *out loud*. The rule that makes it honest is already
in `tcp.zig`: **a segment for no connection we hold is answered with a
reset.** A machine that rebooted and forgot a connection says so the first
time the peer speaks. Forgetting without a reset would be a lie by
silence: the peer would wait on receipts that will never come.

In the triage's terms:
- **A connection is forgotten as a whole, never in part.** One reset ends
  it.
- **Bytes inside it are retried:** sent again until receipted.
- **What we measured is reconstructed:** measured again.

What must never happen is a connection that carries on after losing part of
what it holds.

### Belief: know the peer only by what it last said, in order

What we hold about the peer is **belief**, and each belief has a rule for
when to change it:

| belief | what set it | its rule |
|---|---|---|
| `una` (what it has received) | its latest receipt | moves forward only; an old ACK is no news |
| `wnd` (its room) | the segment numbered `wl1`/`wl2` | a late, older segment doesn't overrule a newer one (RFC 9293's SND.WL1/WL2) |
| `mss` (its largest segment) | its SYN | said once; 536 if it said nothing |
| `peer_done` (it has finished) | its FIN | final |
| `told_wnd` (what it believes about *us*) | our last segment | our belief about its belief; when we reopen, we owe it news |

**Belief is never source, and it is never refreshed by asking.** It moves
only when the peer speaks, and only forward in sequence space. Most of
TCP's careful rules (WL1/WL2, Karn's rule for which sample to trust,
duplicate ACKs) are about *which* message is allowed to change a belief.

### Debt: everything owed has a clock and a give-up

The third word the comments circle without naming. Each side owes the
other things:

| debt | owed by | its clock | its give-up |
|---|---|---|---|
| bytes on the wire, unreceipted | us | `rto_at`, doubling | reset after `max_retries` |
| our SYN-ACK, unanswered | us | `rto_at` | `max_retries`; a newer SYN may take its slot |
| our FIN | us | after the last byte | as bytes |
| news of a reopened window | us | `window_news`, `update_at` | lapses after `max_retries` |
| a probe into a shut window | us | `rto_at` | reset after `max_retries` |
| the peer's FIN, after ours | the peer | `fin_wait_until` | reset after `fin_wait_ns` |
| the peer's request bytes | the peer | `idle_ns` (the host's) | let go |

`tcp.zig`'s "what waits, and what bounds the wait" is exactly this ledger,
written as prose. **Calling it debt makes the rule plain: no debt without
a clock, and no clock without a give-up.** A debt with no give-up is a slot
held forever, and in a table of 256 slots, a door slowly closing.

## The turn

The comments' second-favourite word is **turn**. Time in this TCP moves
only inside `transmit`, which `pump` runs once per turn of the loop. So
every clock in the debt ledger is really "the deadline, plus however long
until the next turn". `stream.zig` says it plainly: the host owns that
second part, and while a handler is reading the disk or rendering a page,
no turn happens at all.

That's the network's Isolation. There is one turn at a time, a turn runs to
completion, and no frame is handled half-way while a handler runs. It's
also the network's one shared risk with the disk: **a slow handler stops
every clock.** The debts don't expire; they just aren't looked at.

## A vocabulary for a connection's fields

FAT's held state split naturally into geometry, held and buffers. A `Conn`
splits by the three duties, plus two plain groups:

| group | what it is | fields today |
|---|---|---|
| **identity** | fixed for the connection's life | `peer_ip`, `peer_mac`, `peer_port`, `serial`, `opened_at` |
| **custody** | bytes held for someone | `rx`, `start`, `end` (for the reader); `tx`, `tx_start`, `tx_end` (for the peer) |
| **progress** | where each direction stands in sequence space | `rcv_nxt`, `una`, `sent`, `high`, `state`, `fin`, `fin_ever_sent`, `peer_done` |
| **belief** | what the peer last said | `wnd`, `wl1`, `wl2`, `mss`, `told_wnd` |
| **measure** | estimates: hints, re-measured | `srtt_ns`, `rttvar_ns`, `timed_at`, `timed_seq`, `dupacks` |
| **debts** | what is owed, and its clock | `rto_at`, `rto_ns`, `retries`, `resent_early`, `window_news`, `update_at`, `updates`, `fin_wait_until` |
| **host's** | the host's marks, not TCP's | `claimed`, `heard_at` |

**Two things show up at once:**

- **`progress` holds one fact in several places.** `state`, `fin`,
  `fin_ever_sent`, `peer_done` and `fin_wait_until` together say "how far
  the close has gone". `tcp_check.zig` keeps them in agreement with rules
  like `closing_disagrees_with_fin`. The kernel-facts note flagged this
  (#12): a tagged union per direction would make disagreement
  impossible rather than checked.
- **`debts` is the largest group, and it has no structure.** Each debt is
  two or three loose fields, and its give-up is a shared `retries` counter
  in some cases and its own counter (`updates`) in another. A `Debt` type
  (a deadline, a backoff and a give-up) would make "no debt without a
  clock" true by construction.

## Faithful to the spec: a second vocabulary

TCP has a source after all. It's not a disk but **RFC 9293** (and 6298 for
the clock, 5681 for the duplicate ACKs). Our names and the RFC's should map
one to one, in a table where a reader can check it:

| ours | RFC 9293 |
|---|---|
| `una` | SND.UNA |
| `una + sent` | SND.NXT |
| `wnd` | SND.WND |
| `wl1`, `wl2` | SND.WL1, SND.WL2 |
| `rcv_nxt` | RCV.NXT |
| free room in `rx` | RCV.WND |
| `srtt_ns`, `rttvar_ns`, `rto_ns` | SRTT, RTTVAR, RTO (RFC 6298) |

Our names stay. They're shorter, and `sent` as a count past `una` is
easier to reason about than an absolute SND.NXT. But each field's comment
should name its RFC twin, so "faithful to spec" can be checked line by line
rather than taken on trust. The comments already do this for WL1/WL2 and
SRTT, and not yet for the rest.

## The tasks to get right

Reduced to rules, in the order they'd hurt to break:

1. **Custody:** never drop a byte that isn't receipted, and never receipt
   one we don't hold.
2. **Forget whole, and out loud:** a connection is lost only entirely, and
   a segment for a connection we don't hold is answered with a reset.
3. **Belief moves forward only, on the peer's word:** no older message
   overrules a newer one.
4. **Every debt has a clock and a give-up**, and every clock is looked at
   on the next turn.
5. **Room is respected both ways:** never send past the peer's window, and
   never advertise room we don't have.
6. **The spec is the source of behaviour:** each field names its RFC twin.

**The lexicon to add:**
- **custody** (and **receipt** for an ACK);
- **belief**;
- **debt** (with **clock** and **give-up**);
- **turn**, already ours.

The fields grouped as identity, custody, progress, belief, measure, debts
and host's are the network's counterpart to geometry, held and buffers.

*Next, after you've read this: a cold agent revises the network code's
comments in these terms, in the same worktree as the FAT pass, and
proposes one refactoring for clarity. The `Debt` type and a per-direction
close are the obvious candidates.*
