# The second copy

*2026-09-20 — a day that produced six programs and one bug, over and over*

Six small Roc programs now run on roc.lynrummy.com and as native binaries: three
arcade games, a world you fly around, a paint program, and a movie you can
scrub. Each is one set of files. That is the visible outcome, and it is not the
interesting part.

The interesting part is that nearly every defect found today was the same
defect, and nearly every fix was a deletion.

## One bug, seven costumes

Here they are, in the order they turned up.

**A packer and a reader.** `ShapeWire.pack` in Roc turned a frame into 32-bit
words; `shapewire.js` turned them back. One format, written twice, kept in step
by attention. Adding a camera meant editing both. Adding an image meant editing
both.

**A pointer and a length.** `computeFrame()` answered how many bytes; `frameAt()`
answered where they started. Two calls, and the second is only valid after the
first. This one caught a reviewer, and then caught me within the hour, and then
— after I "fixed" it by collapsing the two into one call — caught me a *third*
time in a new shape: `read(new DataView(memory.buffer), computeFrame())`.
JavaScript evaluates left to right, asking for a frame can grow wasm memory,
and growing it detaches every view over the old buffer. The hazard was never
"two calls." It was any expression that captures a view of memory before an
effect that can move it.

**A widget and a width.** The page drew one pip per tone and believed there
were three. Breakout has five. Breaking a brick — the point of the game — lit a
speaker with no sound in it, and nothing failed.

**A model and a texture.** The paint program upstream keeps its canvas in the
model *and* on the GPU, and every branch that changes one must remember to emit
the upload that changes the other. Its own comment says so: returning both
together "is what keeps the two from drifting apart."

**A check and the thing it checks.** `page_check` gated on `fills === 0`. But
the runner clears the canvas with a counted `fillRect`, so a page that painted
no shape at all reported 29 fills over 31 frames and passed. Our automated eye
certified a black screen. And when I wrote the replacement, my first attempt
compared a hash that folds over the *whole session* — it can never repeat, so it
reported "changed" every frame. A fake check, written while fixing a fake check.

**A README and the code.** I wrote a careful architecture README in the
afternoon, describing code I had written that morning, and a reviewer found a
dozen false claims in it. Not stale ones — *born* wrong. The frame had seven
shape variants and I wrote six. `Image` doesn't carry a fill and I said it did.
I claimed every app answers `release` when exactly one file does, for all of
them. I wrote "the one path that must be true rather than checked" about a path
that is checked twice, with an error message naming the file.

**A name and its meaning.** `Mouse.wheel_delta` existed on both sides and meant
different things — one axis here, two in roc-ray.

## The fixes were deletions

Look at what actually resolved each one. Almost none of them was "check harder."

| | |
|---|---|
| packer and reader | the compiler generates the reader; **`ShapeWire.roc` is gone** |
| pointer and length | one call, and the view built after it on its own line |
| widget and width | `tones` on the seam, so a runner cannot guess |
| model and texture | the frame carries its own pixels; the upload type stops existing |
| README and code | five lines pointing at the per-file docstrings, which sit next to what they describe |
| two meanings | one name deleted |

The generated frame reader is the clearest case. We had been treating "tag
unions in the glue generator" as the blocker for years-in-dog-time — about a
day. It wasn't. The platform declared `frame : Box(model) -> List(U32)`, so the
compiler's type table saw *a list of integers* and could not have generated
anything useful however clever the generator got. The fix was to stop lying to
the compiler: declare `List(Frame.Shape)` and the table carries the whole
vocabulary. Then 158 lines of Roc packer and 96 lines of JavaScript decoder
both went away, the apps needed **no change at all** because a structural union
unifies by shape, and it ran 5.4× faster.

Deleting the duplicate is also faster than maintaining it. That is not always
true, and it is pleasant when it is.

## When you cannot delete the second copy, build the check

The exception is instructive. The canvas's transform matrix and
`Camera.roc`'s `world_to_screen` genuinely must both exist: one is arithmetic
the app needs to convert a pointer position, the other is six numbers in an
order a browser defines. Neither can be derived from the other.

So that one gets a check — `camera_check.mjs` feeds four cameras through the
painter and compares the matrix against the same map written the geometric way.
It agrees to 5.7e-14 px.

The rule that falls out: **a check is what you build when you have failed to
remove the duplication, not what you build instead of trying.**

## Names lag the design by about a day

Six renames today: `Game` → `CanvasApp`, `game_runner.js` →
`canvas_app_runner.js`, `arcade/` → `canvas_apps/`, `Lens` → `Space`,
`GameRunner` → `CanvasAppRunner`, `wheel_delta` deleted.

Every one was late, and late by the same interval: the thing had become
something else, and the name recorded what it used to be. `Game` stopped being
right the moment a camera demo joined; `arcade` stopped being right when a
movie did. `Lens` was fine until you remembered the audience is functional
programmers, to whom a lens is a getter and a setter in a trenchcoat.

The tell is a name that needs a disclaimer. The README had a sentence
apologising for `game` still being in the local names — "older than that and
not yet honest." A sentence like that is not documentation, it is a rename
someone has decided not to do yet.

## Being wrong, and finding out

Three of today's errors were mine in a way worth recording.

**I reported a spike as working when it was not integrated.** I had run a
generated reader in a throwaway script, compared a word count, and called it
proof. The correction was blunt and correct: a non-integrated glue is not a
spike of anything. What I had demonstrated — reading a list of integers — was
*guaranteed* to work and therefore carried no information. I proved the easy
part and reported it as the thing.

Doing the integration properly found three problems no script would have: the
host cannot free a rich value without knowing the tag layout (answered, in the
end, by a one-line Roc function that hands the frame back to Roc); a generated
type id is a *position* that moves when the platform gains a function, so a
page bound to `read_t32` dies; and —

**I published a measurement that was backwards.** I reported the typed frame as
26% slower to read. It was measured while the experiment deliberately leaked
135 MB, which poisoned it. Measured without the leak, it is *faster*, because
generated straight-line readers beat a hand-written decoder that returns a
two-element array from every call. I had decided the leak was a known,
acceptable flaw of the experiment and then measured through it anyway.

**I wrote confident prose about code I had written hours earlier and got a
dozen facts wrong.** This is the one I find hardest to file. It isn't rot —
rot takes time. It's that writing a summary of code is a different act from
reading it, and the summary comes out of memory, and memory is confident.

## On the cold reader

Three cold reviews today, deliberately given little context.

The first found that the JavaScript layer's names undersold it and its data
shape oversold it. The second was asked to propose a decomposition of two files
into small modules and **refused** — and argued it, against the history: every
content change to the decoder had straddled the obvious seam, so a cut there
would produce two files that always change together. The third checked a README
against the code and found the dozen errors above.

The refusal matters most. An instrument that only ever confirms is not an
instrument. It also produced the best sentence of the day, about the file that
checks one matrix while another goes unchecked: *you wrote a whole file because
the other matrix in this layer is easy to transpose; the one with more
arithmetic and no users has no check.*

What the cold reads are good for is narrow and real: **checking claims against
the code**, and saying what a reader will not know. What they are not good for
is judgement about where the project should go — none of the three found the
thing that actually limits this design, which came from the person who owns it.

## Where it stops

That limit: a value-frame wins in proportion to how much smaller the model is
than the picture. A screensaver is a few hundred bytes of state fanning out to
every pixel, so recomputing the whole picture each frame is free and the design
sings. A paint program's model *is* its picture. There is no smaller
description of it, so "the frame is a value" degenerates into "send the state,"
and the state is a framebuffer.

Which means the texture the paint program upstream keeps on the GPU was not
accidental complexity after all. It was the right architecture for a program in
that regime, and we flattened it into the wrong one and called the flattening a
win. The upload list did not stop existing; it moved into the wire, where it is
paid every frame instead of once per stroke. At sixteen by sixteen that is
free. It would not be at five hundred.

So the honest summary of the day is that one idea — a frame is a value —
carried five programs comfortably, carried the sixth while visibly straining,
and pointed clearly at what it would take to carry a seventh. That seems like a
good place to stop and look at it for a while.
