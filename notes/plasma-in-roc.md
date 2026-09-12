# A Codex GPU kernel in Roc: plasma

*2026-09-12. The first of Cobblestone's WGSL programs ported to Roc by hand,
and what the port says about the other forty-five.*

Eye test, preview only: <http://143.244.172.148:9203/gpu/plasma.html>. Any
browser, plain http. The WGSL original needs a WebGPU secure context and a
tunnel; this one does not, and that is the first thing the port says.

## The question

Cobblestone's `apps/gpushow` is forty-six Codex chapters written under the
`Device` effect. The wgsl plug lowers each to a WebGPU compute shader, the
page dispatches it over one GPU thread per pixel, and a render pass reads the
storage buffer back onto the canvas. Roc has no GPU target. So the question
Steve put first, can this even be done in Roc, has a short answer: the kernel
can, the GPU cannot, and the kernel is the program.

A Codex kernel is a function of the thread id:

    plasma-step : Integer, Integer, Integer -> [Device] Integer
    plasma-step (outb) (frame) (gid) = act
      device-store outb gid (pl-color gid frame)
    end

The GPU calls it 786,432 times a frame, in parallel. Roc calls it 786,432
times a frame, in a loop. Same function, same pixels, and "same" is a
checksum, not a feeling: frames 0 and 9 of the Roc port equal a Python
evaluation of the Codex source, to the integer.

| | |
|---|---|
| frame 0, Roc native and wasm | 6293600626746 |
| frame 0, Python over the Codex semantics | 6293600626746 |
| frame 9, Roc native | 6241870578001 |
| frame 9, Python | 6241870578001 |
| native, one 1024x768 frame | 29 ms |
| wasm in Node, one frame | 57 ms |

## How: the effect is state

`[Device]` gives a kernel four things: loads and stores on buffers, the
thread's index, and (in two chapters) block indices. On the GPU a buffer is a
binding and a store is a memory write. In Roc the whole device is a record
the kernel takes and returns:

    Device :: [].{
        Device : { bufs : List(List(I64)) }

        load : Device.Device, I64, I64 -> (Device.Device, I64)
        load = |dev, buf, i| {
            b = List.get(dev.bufs, I64.to_u64_wrap(buf)) ?? []
            (dev, List.get(b, I64.to_u64_wrap(i)) ?? 0)
        }

        store : Device.Device, I64, I64, I64 -> (Device.Device, I64)
        store = |dev, buf, i, v| {
            bufs = List.update(dev.bufs, I64.to_u64_wrap(buf), |b| List.set(b, I64.to_u64_wrap(i), v) ?? b) ?? dev.bufs
            ({ bufs: bufs }, v)
        }

        dispatch : Device.Device, I64, (Device.Device, I64 -> (Device.Device, I64)) -> Device.Device
        dispatch = |dev, n, kernel| dispatch_from(dev, 0, n, kernel)

        dispatch_from : Device.Device, I64, I64, (Device.Device, I64 -> (Device.Device, I64)) -> Device.Device
        dispatch_from = |dev, gid, n, kernel|
            if gid >= n { dev } else {
                (dev1, _) = kernel(dev, gid)
                dispatch_from(dev1, gid + 1, n, kernel)
            }
    }

A buffer handle is an integer because the Codex source passes buffers as
Integers; the plug turns each such parameter into a binding, this turns it
into an index. Out of bounds reads zero and writes nothing, as a WGSL
storage access does. The kernel becomes

    plasma_step : Device.Device, I64, I64, I64 -> (Device.Device, I64)
    plasma_step = |dev, outb, frame, gid|
        Device.store(dev, outb, gid, pl_color(gid, frame))

and the app is one function from the frame number to the pixels, which the
page copies into an ImageData:

    render : I64 -> List(U32)
    render = |frame| {
        dev = Device.new([List.repeat(0, I64.to_u64_wrap(w * h))])
        out = Device.dispatch(dev, w * h, |d, gid| PlasmaKernel.plasma_step(d, 0, frame, gid))
        List.map(Device.buffer(out, 0), |v| I64.to_u32_wrap(v))
    }

Two things had to be true of Roc for this to be a port and not a stunt, and
both are. `List.set` on a list nobody else holds writes in place, so a store
is a store and not a copy of 786,432 words; had it copied, a frame would be
minutes, not milliseconds. And the compiler turns `dispatch_from` into a
loop: it recurses 786,432 deep per frame and the stack does not notice.

The rest of the chapter, the fixed-point sine and the colour field, is
transcribed in the shape rocemit already writes for safari: one type module
per chapter, every definition annotated, Codex's `/` as `I64.div_trunc_by`.
Nothing in it is new.

## What the other forty-five need

A survey of the kernels and the pages, so the emitter's job is sized before
it is started.

- **All forty-six are compute.** The plug emits no vertex or fragment stage;
  each page's render shader is hand-written and, on thirty-four of the
  thirty-nine demo pages, is the same fullscreen triangle reading a packed
  `0xRRGGBB` word per pixel. Those thirty-four are the plasma shape exactly:
  the kernel writes pixels, the page shows the buffer. One platform, one
  page template, one `render` per kernel.
- **Forty-two take `frame` as their only uniform.** The page writes
  `[frame, 0, 0, 0]` and dispatches `ceil(N / 64)` workgroups; on the CPU
  that is `dispatch(dev, N, kernel(frame))`.
- **Seventeen use `device-load`.** The double-buffered simulations
  (particles, cpuparticles, nbody, swarm, fireworks) read last frame's
  positions and write this frame's; the page keeps the buffers across
  frames and draws points or quads from them. Five pages, and each wants a
  small hand-written canvas draw of what its render shader does. That is
  the same division Cobblestone has: the kernel is generated, the host
  wiring is not.
- **Thirty use `Real`.** They cite `DeviceMath`, which is square root, sine,
  cosine and arc tangent by polynomial, a chapter like any of safari's, and
  emits like one. Reals cross the buffer boundary as bits; no kernel uses the
  f64 loads and stores.
- **Three read `thread-idx`, two read `block-idx` and `block-dim`.** The
  CPU dispatch can answer those from `gid` and the workgroup size of 64.
  None uses `sync-threads`, so there is no barrier to emulate.
- **Two chapters have two entry points** (`FireworksKernel`,
  `GlobeKernels`), each a dispatch of its own.

So for the emitter, three pieces:

1. **A library mode.** `rocemit` today refuses a unit with no opening. A
   kernel chapter has none; its modules are the output.
2. **The act lowering.** An `act` in a `[Device]` function becomes
   state-threading: `x <- device-load b i` is `(dev1, x) = Device.load(dev,
   b, i)`, the last statement's pair is the result, and every function whose
   type carries `[Device]` takes and returns the device. The compiler already
   lowers `act` blocks to IR; the emitter has only ever met one, in safari's
   opening.
3. **The demo plan per kernel**: its entry, its buffers and their sizes, its
   uniform, and which page template. That is the page's knowledge, not the
   kernel's, and it can be a table.

## Open

- **Speed.** 57 ms a frame is seventeen frames a second, against safari's
  fifteen milliseconds. The per-frame `List.repeat` and the map to `U32` are
  the first suspects, then the closure in the loop. A model that keeps its
  buffer across frames removes the first.
- **Integer width.** The plug computes in `i32` with wrapping; this port
  computes in `I64`. The kernels are written to stay in 32-bit range (the
  Mandelbrot chapter says so in its own prose), so the two agree wherever
  the GPU result was meant. Roc has `I32`; the emitter could pick it for
  device chapters and match the plug bit for bit, wrap included.
- **The five simulations** need their page-side draws before they can be
  eye-tested; the pixel kernels do not.
