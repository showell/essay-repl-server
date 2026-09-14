# The machine demo, first cut: a batch run in the browser

The Roc machine runs Codex programs on the ladder, on the command line, and
now in the browser. This note is the plan for that first page, and where it
stands.

## Where it stands

**The page is built: `http://143.244.172.148:9203/machine/batch/`.**

- fat16-write, fat16-list and dhcp-acquire each build for WebAssembly and match
  their test's expected output (1 to 2 seconds a run).
- The panes are Console, Verdict, Disk and Network:
  - fat16-write shows the five sectors it wrote.
  - dhcp-acquire shows its four frames: DISCOVER, OFFER of 10.0.2.15, REQUEST,
    ACK.
- The page's script has run from Node against the built programs
  (`machine/batch/page.mjs`), but not yet in a browser.

**One Roc compiler bug had to be worked around.** The WebAssembly build fails
to link when a function copies a record holding nested records with lists in
several branches. The machine's command-line parser did exactly that. The
parser now carries the network card and the timer beside its record, and a
standalone program that shows the bug is kept in
`roc-apps/findings/wasm-reloc-order/`.

## What the page shows

You pick a program, press Run, and see what it did to the machine:

- **fat16-write** writes a file onto a FAT16 disk image, then reads it back.
- **fat16-list** lists the directories of a disk image.
- **dhcp-acquire** asks the network for an address and gets one.

Each run fills three panes:

- **Console**: the lines the program prints, which are the lines its test
  checks.
- **Disk**: the sectors the run wrote, with the bytes that changed marked.
- **Wire**: each network frame the program sent and each one the network
  answered with, one line each ("DHCP DISCOVER from 52:54:00:12:34:56" ...).

"Batch" means the program runs from start to finish in one go, as it does on
the ladder. Nothing waits for a key. An interactive machine is a later step.

## How Codex's pieces map to it

Cobblestone is an operating system written in Codex. Its bottom layer (boot,
interrupts, the scheduler) is x86 code that Codex's compiler generates, so it
is not Codex we can turn into Roc. The Roc machine stands in for that layer:
it starts in the state x86's boot leaves behind, and its doors do what the
kernel's helper routines do. Everything above it is ordinary Codex that
rocemit turns into Roc: the FAT16 and FAT32 file system code, the network
card driver and DHCP, the drawing code.

## The pieces to build

1. **A browser platform for emitted programs.** Today's browser platform only
   takes the hand-written app. The native platform (`machine/native`) already
   runs emitted programs: it gives them a console and answers the disk from
   files. The browser one has the same shape, answered by the page instead:
   the console goes to a buffer the page reads, and the disk is a buffer the
   page loaded the image into.
2. **A tap on the wire.** The network card and the network behind it are Roc
   code inside the machine, so the page cannot see the frames. A small module
   with one door, "a frame went by", is called where the card transmits and
   where an answer arrives. On the ladder it does nothing; in the browser it
   hands the frame to the page. It is the same seam as the disk's.
3. **The page.** A program picker, Run, and the three panes.
4. **The build.** Each featured program is emitted, wired to the browser
   platform the way `machine/native/run.sh` wires it to the native one, and
   built with `roc build --target=wasm32 --opt=dev` while we iterate (an LLVM
   build is for the finished page). It lands in the preview root,
   `~/build/roc-apps/next/machine/`, served on :9203.

## Risks, checked first

- **The wasm build of an emitted program.** The hand-written app builds for
  wasm; an emitted program is far larger and uses host-answered doors. The
  first step is to build fat16-write that way and see.
- **A crash inside the program.** In the browser a Roc crash stops the wasm
  instance. The host keeps the crash message so the page can show it.

## Later

- **Pixels.** The GOP units draw into memory, but each keeps its drawing
  surface at its own address. Showing them needs that address from each unit.
- **An interactive machine.** The desk (Cobblestone's desktop) is refused by
  rocemit today, and a program that waits for a real keypress cannot run
  straight through in the browser.
