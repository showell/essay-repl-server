# Drawing without a screen

*2026-09-15. Safari moved onto roc-ray today and shipped for Windows, macOS and
Linux. The box it was built on has no display, no GPU, no Windows and no Mac.
This is about how the pictures were known to be right anyway, and about what a
platform is for.*

## A smaller question

[Five days of Roc](five-days-of-roc.md) ended on a question about fit: was Roc
the right target for everything we pointed it at? Today's question was smaller
and more practical. Safari was already Roc and already correct in a browser. The
job was to make it a native program on Luke Boswell's raylib platform, for
machines this box cannot be.

Nothing here opens a window. There is no Windows SDK to link against, no Mac to
run a binary on, no GPU to run a shader. By evening there were three releases on
GitHub, the last with a Windows executable, two Mac binaries and a Linux one,
drawing through a fragment shader with anti-aliasing. Every claim in their notes
had been checked by something. None of those somethings was a look at a screen
on this box.

## The seam was data

The quick part was the part Roc is built for. Safari's emitted chapters already
answered "what does this frame show" as a list of draw commands. One
hand-written module, `SafariRide`, gathered the ride and that list, and the web
app shrank to boxing a model and packing words. Everything below `SafariRide` is
shared; everything above it is an edge.

The roc-ray edge stayed thin because the next two layers were data too. `Brush`
says what a command's paint means. `Shapes` says how a frame breaks into things
a GPU fills: convex polygons, triangles cut from the concave ones, discs,
rectangles, each carrying its brush. The roc-ray app is one file that turns each
shape into a draw call. When Steve asked what the second step cost in
portability, the answer was a table rather than an argument: no shared module
imports a platform, and each platform owns one small file.

That is the shape Steve named at the end of the day as Roc's sweet spot. The
platform does the heavy lifting, the application is plain functional code, and
the line between them is a value that crosses it.

## Proxies for eyes

The more interesting part was knowing the picture was right.

**The first proxy was a hash.** Before `SafariRide` existed, the web build drew
sixty frames and a step back, and hashed them all into one digest; the refactor
had to reproduce it, and did: `8fc5691b` before and after. A hash cannot say a
frame is good. It can say nothing moved, which is all a refactor promises.

**The second was a twin.** The first iteration painted every pixel in Roc, which
was slow, and as a product beside the point. But it followed the canvas's rules
closely enough to be an oracle, so it stayed in the app behind a key. `Shapes`
could then be checked with no GPU at all: fill its pieces through that painter
and compare with the painter's own frame. Not one of 576,000 pixels differed on
the frames tried, gradients included. The painter nobody would ship became the
reference.

**The third was a borrowed machine.** GitHub's Windows runner has no GPU either,
but Mesa's software OpenGL gives raylib what it asks for, and roc-ray's host can
press keys on a schedule. So a workflow drove the app to four places on the
route and saved each frame three ways: the GPU painter, the same without
anti-aliasing, and the Roc twin. A small PNG decoder counted the disagreements. At most 41 pixels a frame differed by more than 8 in 255, all on
the edges of thin shapes; the rest was rounding in gradients. The world tilted
the same way in both, which settled a sign that had been derived by reading
roc-ray's camera code rather than by watching.

**The last proxy was a person.** Steve ran each Windows build from WSL, and his
were the judgments the instruments could not make: that the pixel painter was
sluggish, that the shader build looked right, that anti-aliasing was clearly
better with A pressed. The instruments decided whether two things were the same.
He decided whether they were good.

## What could not be claimed

The Mac binaries were built and run on Apple Silicon and Intel runners, which
also have no GPU. They link, load and step through frames, and they have drawn
nothing anyone has seen. The Linux binary has never opened a window either. The
release notes say so in bold, and Apoorva's Mac is where the first picture will
come from.

All day there was a pull toward saying more than was known. A Mac binary
cross-linked on this Linux box came out signed and well formed, and has never
run. A draft of the notes said the two painters "agree to within 41 pixels",
which hides thousands of pixels that differ a little. Another said the painting
layers were shared with the web, which they are not. Each release went out after
a cold read took those sentences out. When nobody can look, the wording is part
of the measurement.

## Small frictions, fixed where they lived

Some of the day's problems had nothing to do with pictures.

- Roc's Windows link looks for an installed SDK, so the Windows build moved to a
  runner rather than to a workaround.
- Git on that runner wrote carriage returns, and a shell `read` kept one. The fix
  was a `.gitattributes`, not a strip in the script.
- roc-ray's plain `zig build` makes a debug host, whose checks cost a third of
  every frame until the host was built for release.
- The one compiler warning was a divide guard on a constant in Safari's Codex,
  and removing it forked Safari's copy from Cobblestone's.

## What a platform owes

roc-ray does not target the browser. Its maintainer closed that request: a
second host is a second asset path and a second test matrix. After a day spent on
the web and native at once, that reads as right about the cost, and the day also
shows what a web host would inherit: nothing in `Shapes` or `Brush` knows it runs
on raylib. Whether that is worth a conversation is Steve's to decide, after
Luke's first response.

Luke's own reply on Zulip to a profiling question was that he gives his wasm
platforms a native test host, full of instrumentation, so the standard tools
work. That is today's move from the other side. When the thing you ship cannot
be watched where it runs, build a place where it can be measured, and keep that
place next to the code.

## Open

- What does Apoorva's Mac show?
- Would the web draw from `Shapes` as well as the blitter does, and would a second
  web edge earn its keep?
- Where does a frame's time go now? `perf` names Roc functions only by number;
  roc-ray's Observatory could name the phases.
- Is "shared data, thin edges, a twin painter as the oracle" a pattern for the
  other apps, or a property of a screensaver?

| repo | revision | role |
|---|---|---|
| roc-apps | `a1e4146` | the app, the build script, the workflows; tag `safari-roc-ray-2026-09-15c` |
| roc-ray | `e100c95` | the platform |
| roc-lang/nightlies | `nightly-2026-09-07-14d9829` | the compiler roc-ray pins |
| safari-codex | `d1508f3` | the Codex source, forked from Cobblestone's copy |
