# The shape of a run

*2026-09-18 — metal-vmm, nine milestones in: who talks to whom, and what makes
any of it move*

The last essay was about one problem — the clock — and how it was solved. This
one is a map. Nine milestones in, `metal-vmm` has enough moving parts that the
interesting thing is no longer any single one of them but **how they are wired
to each other**, so this is mostly pictures.

## Who owns what

```dot
digraph owns {
  rankdir=LR; bgcolor="transparent"; compound=true;
  node [shape=box, style="rounded,filled", fillcolor="#f6f6f6", color="#999", fontsize=11];
  edge [color="#666", fontsize=9];

  subgraph cluster_g {
    label="the guest — gopher-metal, unmodified"; color="#bbb"; fontsize=10;
    guest [label="a PVH kernel\npolls · one core · no interrupts", fillcolor="#e8f0fe"];
  }

  subgraph cluster_k {
    label="Linux"; color="#bbb"; fontsize=10;
    kvm [label="KVM_RUN\none vCPU", fillcolor="#fff3e0"];
  }

  subgraph cluster_v {
    label="metal-vmm"; color="#bbb"; fontsize=10;
    loop  [label="the exit loop\nmain.zig"];
    clock [label="the clock\nclock.zig", fillcolor="#e6f4ea"];
    dev   [label="the devices\nvirtio.zig"];
    ent   [label="entropy\nentropy.zig", fillcolor="#e6f4ea"];
    dsk   [label="the disk\ndisk.zig", fillcolor="#e6f4ea"];
    wire  [label="the wire\nfaults.zig", fillcolor="#fde8e8"];
    peer  [label="the peer\npeer.zig"];
  }

  file [label="an image file\n(read at the start,\nwritten at the end)", shape=note, fillcolor="#fafafa"];
  out  [label="stdout", shape=note, fillcolor="#fafafa"];

  guest -> kvm [label="runs"];
  kvm -> loop [label="exits"];
  loop -> clock [label="every exit\nis a tick"];
  loop -> dev;
  loop -> out [label="COM1"];
  dev -> dsk; dev -> ent; dev -> wire;
  wire -> peer;
  dsk -> file;
  clock -> dev [style=dashed, label="what time is it"];
}
```

**Everything in the middle box is ours, and that is the entire claim.** The
guest reads nothing this program did not hand it: not the disk, not the wire,
not the entropy, and — since the last essay — not the time.

## What makes anything happen

Nothing in that picture is driven by a thread, a timer, or the host's clock.
There is exactly one thing that moves the machine, and it is the guest asking
for something.

```dot
digraph beat {
  rankdir=LR; bgcolor="transparent";
  node [shape=box, style="rounded,filled", fillcolor="#f6f6f6", color="#999", fontsize=11];
  edge [color="#666", fontsize=9];

  run  [label="KVM_RUN", fillcolor="#fff3e0"];
  exit [label="an exit\na port, a register,\na clock read"];
  tick [label="the clock advances\n100 µs", fillcolor="#e6f4ea"];
  pump [label="the pump\nanything the wire\nhas finished carrying"];
  serve [label="serve the exit\nthe device answers"];

  run -> exit -> tick -> pump -> serve -> run [label="  resume  "];
}
```

That loop is the whole design. **Time is measured in questions**: the counter
moves 100 µs per exit and by nothing else, so the moment anything happens is a
function of what the guest did, not of what this box was busy with. The pump
runs at every exit because the guest polls memory and gives the program no
other moment to act.

Two consequences worth holding on to:

- **a guest that waits pays in questions, not seconds** — the `clock` probe
  waits for four real-time-clock seconds-edges and takes 1.3 s here against
  QEMU's 8.3;
- **a guest that waits without asking anything waits forever** — a spin on
  memory advances nothing. gopher-metal's DHCP does exactly that, which is why
  wire latency kills it.

## One request, end to end

```dot
digraph req {
  rankdir=TB; bgcolor="transparent"; nodesep=0.35; ranksep=0.32;
  node [shape=box, style="rounded,filled", fillcolor="#f6f6f6", color="#999", fontsize=10];
  edge [color="#666", fontsize=9];

  say   [label="the guest PRINTS \"listening on port 80\"", fillcolor="#e8f0fe"];
  trig  [label="the only moment the program knows it is ready\n(a polling guest signals no other way)", shape=plaintext, fillcolor="none"];
  open  [label="the peer opens a connection"];
  hold  [label="the wire carries it\n(or eats it, or holds it)", fillcolor="#fde8e8"];
  rx    [label="into a receive buffer the guest parked earlier"];
  work  [label="the guest's TCP, its HTTP,\nits FAT16, its disk reads", fillcolor="#e8f0fe"];
  tx    [label="a frame on the transmit queue\n→ the doorbell rings"];
  back  [label="the wire again", fillcolor="#fde8e8"];
  ans   [label="the peer collects status and body"];
  cmp   [label="printed as one line,\ncompared with what curl got\nfrom the same guest under QEMU", shape=note, fillcolor="#fafafa"];

  say -> open; trig -> say [style=invis];
  open -> hold -> rx -> work -> tx -> back -> ans -> cmp;
  work -> rx [label="  polls, sees it  ", style=dashed, constraint=false];
}
```

The trigger at the top is the part nobody would guess. A polling guest never
returns control to say "I am ready now", so the peer waits until the guest
**prints** that it is listening. gopher-metal's own judge waits for the same
line, arrived at independently for the same reason.

## Where a fault gets in

There are exactly two seams a fault can enter through, and they ask the same
question, so they ask it in the same place.

```dot
digraph faults {
  rankdir=LR; bgcolor="transparent";
  node [shape=box, style="rounded,filled", fillcolor="#f6f6f6", color="#999", fontsize=11];
  edge [color="#666", fontsize=9];

  sched [label="Schedule\n\"is this the nth,\nand was n named —\nor does the rate say so?\"", fillcolor="#fde8e8"];
  wire  [label="the wire\neats the guest's frame"];
  disk  [label="the disk\nrefuses the request"];
  gtcp  [label="the guest's OWN retransmission timer\nnotices, 200 ms later", fillcolor="#e8f0fe"];
  gfat  [label="the guest's OWN fat16.zig\nturns a status byte into ReadFailed", fillcolor="#e8f0fe"];

  sched -> wire [label="its own dice"];
  sched -> disk [label="its own dice"];
  wire -> gtcp; disk -> gfat;
}
```

**Picking the nth beats picking at random.** A rate explores by sampling; a
number explores exhaustively, and the table of "what happened when I took away
the nth" is a map rather than an anecdote. Refusing each of the `fat16` guest's
709 disk requests in turn took 1 minute 46 seconds, and every single run failed
cleanly naming the right layer.

Each seam gets its own generator, and a test holds them to it: turning the
wire's loss on must not change which disk requests fail. Two knobs that
interfere are two knobs you cannot reason about.

## Four questions, four instruments

```dot
digraph instruments {
  rankdir=TB; bgcolor="transparent"; nodesep=0.4;
  node [shape=box, style="rounded,filled", fillcolor="#f6f6f6", color="#999", fontsize=10];
  edge [style=invis];

  a [label="check.sh — is it RIGHT?\nQEMU runs the same guest on the same disk.\nSame words, same exit code, same disk afterwards.", fillcolor="#e8f0fe"];
  b [label="same.sh — does it REPEAT?\nThe same guest twice, here.\nQEMU cannot answer this about itself.", fillcolor="#e6f4ea"];
  c [label="lossy.sh — what can it survive losing?\nEat the guest's nth frame, one run per frame.", fillcolor="#fde8e8"];
  d [label="flaky.sh — what can it survive being refused?\nRefuse the guest's nth disk request, one run each.", fillcolor="#fde8e8"];
  a -> b -> c -> d;
}
```

The first two are oracles: they say whether the machine is trustworthy. The
second two are explorers: they only mean anything **because** the first two
pass. A sweep over a machine that does not repeat is a pile of anecdotes.

And the explorers have already earned it. `lossy.sh` found a real defect in the
guest on its first run: **gopher-metal's `dhcp.acquire` sends its DISCOVER once
and never retransmits.** Eat the first frame and the machine has no address.
Its TCP survives every other single-frame loss in the table, paying exactly the
200 ms its own `min_rto_ns` promises.

## What has been running on it so far

Probes. Small kernels that do one thing and print whether it worked — a disk
read, a lease, a fetch, a calibration. They were the right subject for building
a machine, because when a probe disagrees with QEMU the disagreement is three
lines long.

But a probe is a friendly guest. It asks for little, it holds no state, and its
error paths are shallow enough that refusing a disk request always ends the run.

**The next guest is `gopher.elf`**: angry-gopher's actual route table, compiled
from its own source, serving real HTTP over a FAT16 volume with the site's own
data on it — sessions, chat transcripts, images, a login. On Linux it is a web
application; here it is a 24 MB kernel with no operating system under it. It is
the thing all of this was built to be able to take apart.

That is the next run.
