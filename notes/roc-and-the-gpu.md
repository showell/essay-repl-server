# What "Roc doesn't do GPU" means

*2026-09-12. For Steve, who asked what exactly that sentence meant, in plain
terms. It is the one fact that shaped the whole gpu port.*

## Two kinds of worker

A CPU is a handful of very capable workers. Each one can do anything a
program asks, one step after another, very fast. Your laptop has maybe eight
of them.

A GPU is thousands of much simpler workers who are only fast when they all
do the *same small job at the same time*, each on a different piece of the
data. A screen of 1024 by 768 has 786,432 pixels. "Work out the colour of
this pixel" is the same small job 786,432 times, and that is exactly the
shape a GPU is built for. It hands one pixel to each of thousands of workers,
they all finish together, and the whole screen is done in a fraction of a
millisecond.

The small job, written in the GPU's own language, is called a *shader*. On
the web that language is WGSL, and the browser's way of handing the GPU a
shader and some buffers and saying "run this on N workers" is called
WebGPU.

## What Cobblestone does

Damian's gpushow pages are built on that. Each demo has a Codex chapter,
written under the `Device` effect, whose main function says what one worker
does: read a few things from a buffer, do some arithmetic, write one packed
colour word. The wgsl plug translates that chapter into WGSL. The page hands
the WGSL to the GPU through WebGPU with a buffer of 786,432 words and says
"run it on 786,432 workers". Then a second, hand-written shader copies the
words to the screen. The kernel's author never thinks about parallelism; the
GPU does the "thousands at once" part for free.

## What a language has to have to "do GPU"

Two things, and Roc has neither.

The first is a compiler that can turn the language into a shader. Roc's
compiler produces programs for a CPU: a native binary, or a WebAssembly
module, which also runs on the CPU (inside the browser, but on the CPU).
Nobody has written a Roc-to-WGSL back end. So a function written in Roc can
never be handed to the GPU's thousands of workers; it can only be run by the
CPU's few.

The second is a way to talk to the GPU at all: a library that opens WebGPU,
makes buffers, and launches shaders. Roc's wasm modules do not have that,
and even if they did, the thing launched would be a WGSL shader, not Roc.
Roc would be the host, and the kernel would be in another language.

That is the whole meaning of the sentence. Roc can be the program that
decides what to draw, but it cannot be the program that runs on the GPU, and
it cannot even ask the GPU to run something else.

## So what did we port?

The kernel. A Codex kernel is, underneath, an ordinary function of the
worker's number: given "you are worker 4,711", it computes pixel 4,711. The
GPU calls that function 786,432 times in parallel. Roc calls it 786,432
times in a loop, on one core.

That is a real port and not a cheat, because the function is the whole
program. The `Device` effect, the loads and stores to buffers, became a
record the function takes and hands back; the "dispatch over N workers"
became a loop from 0 to N. Same arithmetic, same buffer, same pixels, and
"same" is checked: for plasma and the fountain, a Python evaluation of the
Codex source gives the same checksum as the Roc build, native and wasm.

The rocemit change that made this automatic is small in the end: a
definition typed `[Device]` takes the device as its first argument and
answers it back paired with its result, and an `act` threads it from one
statement to the next. Then the gallery script reads each page for its
buffers and passes, and all thirty-nine demos come out of the one machine.

## What it costs, and what it buys

It costs time. The GPU does plasma in well under a millisecond; Roc on one
CPU core does it in about 38 ms, and a kernel that reads many neighbours per
pixel, like bloom, takes six seconds a frame. The gallery page shows the
milliseconds next to the demo, and the slow ones are slow. There are ways to
claw some back on a CPU, splitting the pixels across web workers for a
handful of cores, but that is eight times faster, not a thousand.

It buys something too. WebGPU only works in a "secure context", which is why
the Cobblestone gallery has to be reached through an ssh tunnel to
`localhost`. The Roc version is a wasm module and a 2d canvas: any browser,
plain http, no tunnel. And every kernel Damian writes is now a Roc program
that runs anywhere Roc runs, GPU or not, with the plug's exact integer
semantics.

## The kitchen version

One chef who can cook anything, versus a thousand line cooks who can each
only make the one canapé on the card in front of them, all at once. The
Codex kernel is the card. The GPU is the thousand line cooks. Roc is the one
chef reading the same card 786,432 times. The canapés are identical; the
party just waits a bit longer.
