# Where metal's extra 5 ms goes

*2026-10-01, evening. gopher-metal `43f6e75`.*

## The numbers

I fetched the same pages from lynrummy.com (Linux) and metal.lynrummy.com,
alternating between them. The times are to the first byte of the answer,
medians of 3 rounds (`droplet/race.py` in gopher-metal):

| page | from this box, through Caddy (lynrummy / metal) | on prod, server alone (Linux / metal) |
|---|---|---|
| home page | 3.0 / 7.9 ms | 0.50 / 6.0 ms |
| a picture | 2.6 / 8.8 ms | 0.25 / 6.5 ms |
| /delivery | 2.9 / 6.3 ms | 0.21 / 5.1 ms |
| /game (a redirect) | 2.4 / 11.0 ms | 0.22 / 5.2 ms |

Both are fast for a person, and you found metal zippy. But metal pays about
**5 ms more on every page**, even a redirect with no content.

## The server isn't the slow part

The console's own numbers for one of my requests:

    waited 2944 us, answered in 7 us

The server took **7 microseconds** to answer. Almost all the time was
"waited": the stretch between the connection opening and the whole request
arriving. The picture was slower to answer, at 1.1 ms, probably because metal
reads it from disk where Linux would have it in memory. That's real, but it's
the smaller cost.

## The likely cause: metal never rests

Linux, with nothing to do, tells the processor to **halt**: stop until
something happens, such as a network card saying a packet came in. It does
that with *interrupts*, which are how hardware taps the processor on the
shoulder.

gopher-metal has no interrupts at all. With nothing to do, it asks the network
card "anything yet?" over and over, millions of times a second, forever.

On our own test machines that's harmless. On a droplet, it probably isn't:

- A droplet's one processor is really a share of one of DigitalOcean's
  processors.
- When a packet arrives for the droplet, a helper program on DigitalOcean's
  machine has to run to hand it over. Another one sends our answers out.
- Those helpers need processor time on the same machine. A guest that never
  rests is always asking for its share. So the helpers can wait their turn,
  a millisecond or a few each time.

That fits what we see: a fast server, with milliseconds lost on every trip in
and out, and handshakes that sometimes take 0.6 ms and sometimes 2.7 ms.

**This is a strong guess, not yet a proof.** The proof is to fix it and
measure again.

## The fix

Teach gopher-metal to rest:

1. **Interrupts:** set up the table that says what to do when hardware taps
   the processor, and have the network card tap it when a packet arrives.
2. **Halt when idle,** the way Linux does, and wake on that tap. A timer tap
   also wakes it, so timeouts still happen on time.

This is real work, but the kind gopher-metal already does: talking to
hardware directly. It would also make metal a better guest. An idle droplet
would really be idle, instead of burning its share of a processor around the
clock.

## Still open

- **One fetch from metal failed outright** in 12 tries. It isn't explained
  yet. It may be the same cause, a packet held up long enough to be given up
  on, or it may not.
- **A proper 40-round run** for real statistics, best done after the fix.
