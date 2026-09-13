# A Roc machine emulator: the design, in pictures

*The first step of the devices plan: a Roc machine with simulated devices,
shown in a browser, before any emitted Codex program depends on it. Short on
purpose. The pictures carry the design.*

## The layers

The machine is one Roc value. Everything that touches a device takes the
machine and hands it back. The browser only sees what the host copies out.

```dot
digraph layers {
  rankdir=TB; bgcolor="transparent";
  node [shape=box style="rounded,filled" fontname="Helvetica" fontsize=10 fillcolor="#ffffff"];
  edge [fontname="Helvetica" fontsize=9 color="#666666"];

  page [label="the page\nconsole · framebuffer · memory · PCI · disk · keys" fillcolor="#eef3fb"];
  host [label="wasm host (new)\nnew · step · key · view · drop" fillcolor="#fde9d9"];
  app  [label="the app (hand-written Roc)\nwhat runs on the machine" fillcolor="#fff8e6"];
  mach [label="Machine (one value)\nthe device models" fillcolor="#e6f4e6"];
  prog [label="a Codex program, emitted\n(later: fat16-list, pci-bridge-*)" fillcolor="#f4f4f4" style="rounded,dashed"];

  page -> host [label="calls exports"];
  host -> app [label="one boxed model"];
  app -> mach [label="Machine in, Machine out"];
  prog -> mach [label="the same threading" style=dashed];
}
```

**Borrowed from BASIC:**
- one boxed model behind the platform;
- `status` and `resume` for a machine that is waiting on its input;
- `view` as a flat byte list the page slices;
- the persistent structures (`Vec`, the `Mem` trie).

**Written fresh:** the host and the page, with an export per device door.

## The machine

One record, as BASIC's `Devices` is and as codex-vm is. Each door dispatches
on what it is given: an address, a port, a sector.

```dot
digraph machine {
  rankdir=LR; bgcolor="transparent"; compound=true;
  node [shape=box style="rounded,filled" fontname="Helvetica" fontsize=10 fillcolor="#ffffff"];
  edge [fontname="Helvetica" fontsize=9 color="#666666"];

  peek [label="peek · poke\nread-mmio-32" shape=plain];
  port [label="port-out-32\nport-in-32" shape=plain];
  blk  [label="block-read-sector\nblock-select" shape=plain];
  key  [label="key reads" shape=plain];
  prt  [label="print-line" shape=plain];

  subgraph cluster_m {
    label="Machine"; fontname="Helvetica"; fontsize=10; color="#bbbbbb";
    mem  [label="mem\nMem trie (sparse, 2 GB)" fillcolor="#fde8c8"];
    fb   [label="framebuffer window\n(an address range, as BASIC's hires)" fillcolor="#fde8c8"];
    pci  [label="pci\nlatched 0xCF8 + device table" fillcolor="#e6f4e6"];
    disk [label="drives\nimage bytes · selected drive" fillcolor="#e6f4e6"];
    keys [label="keys\nscancode queue" fillcolor="#e6f4e6"];
    con  [label="console\nunits written" fillcolor="#e6f4e6"];
    clk  [label="clock\nsteps, not wall time" fillcolor="#e6f4e6"];
  }

  peek -> mem; peek -> fb [label="in the window"];
  port -> pci [label="0xCF8 · 0xCFC"];
  blk -> disk; blk -> mem [label="512 bytes land here"];
  key -> keys; prt -> con;
}
```

**The clock counts steps, not wall time.** Then a run is reproducible, and
the verdicts that time things can be graded.

## Two ways to drive it

An emitted Codex program runs straight through, so it cannot stop halfway and
wait for a key. That gives two modes, and the demo needs both.

```dot
digraph modes {
  rankdir=LR; bgcolor="transparent";
  node [shape=box style="rounded,filled" fontname="Helvetica" fontsize=10 fillcolor="#ffffff"];
  edge [fontname="Helvetica" fontsize=9 color="#666666"];

  subgraph cluster_batch {
    label="batch: how a test runs"; fontname="Helvetica"; fontsize=10; color="#7fb27f";
    side [label="sidecars\n.disk · .keys · .vmargs" shape=note fillcolor="#fff8e6"];
    b1 [label="Machine.new(config)"];
    b2 [label="run the program\nto the end"];
    b3 [label="console units\n→ the verdict" fillcolor="#e6f4e6"];
    side -> b1 -> b2 -> b3;
  }

  subgraph cluster_live {
    label="interactive: how the page runs"; fontname="Helvetica"; fontsize=10; color="#d69a6a";
    l1 [label="Machine.new(config)"];
    l2 [label="step(machine, message)\n→ machine" fillcolor="#fde9d9"];
    l3 [label="view(machine)\n→ bytes for the panes"];
    l1 -> l2 -> l3;
    l3 -> l2 [label="next key, next frame" style=dashed];
  }
}
```

Batch mode is what the ladder needs: the keys are already in the queue, and
the disk is already attached.

Interactive mode is the games' shape (`step` is the only door, the model
holds the state). A program written that way can wait for a key without
stopping in the middle of itself.

## One frame of the page

```dot
digraph frame {
  rankdir=LR; bgcolor="transparent";
  node [shape=box style="rounded,filled" fontname="Helvetica" fontsize=10 fillcolor="#ffffff"];
  edge [fontname="Helvetica" fontsize=9 color="#666666"];

  js   [label="page\n(requestAnimationFrame)" fillcolor="#eef3fb"];
  step [label="roc_step(box, budget)\nrun until budget or waiting" fillcolor="#fde9d9"];
  key  [label="roc_key(box, scancode)" fillcolor="#fde9d9"];
  view [label="roc_view(box)\nflag · console · fb · mem page · pci · sector" fillcolor="#fde9d9"];
  draw [label="draw the panes;\nhighlight what the step touched" fillcolor="#e6f4e6"];

  js -> step -> view -> draw;
  js -> key [label="keydown" style=dashed];
  key -> step [style=dashed];
}
```

**Because the machine is a value, the step before is still in hand.** So the
memory pane can highlight exactly the bytes the last step wrote, and a "back"
button is a pop, as BASIC's is.

## A first demo, and what it proves

```dot
digraph demo {
  rankdir=TB; bgcolor="transparent";
  node [shape=box style="rounded,filled" fontname="Helvetica" fontsize=10 fillcolor="#ffffff"];
  edge [fontname="Helvetica" fontsize=9 color="#666666"];

  a [label="1. hand-written Roc app\nscans the PCI table, reads sector 0,\nechoes keys to the console" fillcolor="#fff8e6"];
  b [label="2. the same machine under an emitted\nCodex unit, batch: pci-bridge-cap\n(count=10 bus1=2 ... truncated=yes)" fillcolor="#e6f4e6"];
  c [label="3. fat16-list over its committed image\n(rootfile CODEX.CDX, bootfile BOOTX64.EFI)" fillcolor="#e6f4e6"];
  d [label="4. a real device behind the platform\n(a host file as the disk)" fillcolor="#f4f4f4" style="rounded,dashed"];
  a -> b [label="the machine is right"];
  b -> c [label="the disk is right"];
  c -> d [label="the seam holds" style=dashed];
}
```

- **Step 1 proves the machine and the page.** It needs no emitter change.
- **Steps 2 and 3 prove the models against upstream's verdicts.** They need
  step 0 of the devices plan: hardware builtins crash at run time instead of
  refusing the unit.
- **Step 4 is the "real device" half:** the same doors, answered by the host.

## Where it lives, and what I need from you

- **`roc-apps/machine/`**, beside `basic/`: `roc/Machine.roc` and one module
  per device, `wasm/platform/` (host.zig written fresh), `web/machine.html`.
  Preview on `:9203/machine/`.
- **The first subject.** The page in step 1: PCI table, sector 0 of a small
  image, a key echo. I think it is the smallest thing that shows every seam.
- **Config from the start:** `Machine.new` takes the sidecar files as they
  are (`.vmargs` text, `.disk` bytes, `.keys` text). Then step 2 needs no new
  plumbing.
