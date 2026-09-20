# Two frontends, one core

*2026-09-20 — what porting three of roc-ray's games to the browser taught us
about the shape of a Roc program that runs in two places*

A week ago the question was how to make a screensaver run on a web page and on
a desktop from the same Roc. Today three of roc-ray's own example games —
snake, pong, breakout — do the same, and the surprising part is how little it
took. This is an attempt to say what the reusable part is, because it does not
seem to be specific to games, or to us.

## The premise was wrong in a useful way

We kept saying "one app, two platforms". There is no such app. Roc requires an
application to name exactly one platform, so `snake_web.roc` and
`snake_native.roc` are two different programs. What runs in both places is a
**value**: `SnakeGame.game`, of type `Game(Model)`. The game's own modules
import no platform at all — the rules, the board and the drawing depend on
nothing but arithmetic.

So the honest description is **one core, two frontends**, which is not a
metaphor we invented. It is libretro's architecture: a core exports `run` and
`get_system_av_info` — width, height and frame rate — and a frontend owns the
window, the loop, the input and the audio. It is also WASM-4's: a cartridge
exports `update`, the console owns a gamepad byte and a framebuffer. And in
WebAssembly's own vocabulary our wasm module is a *reactor* — instantiated
once, its exports called repeatedly, keeping state between calls — rather than
a *command* that runs to completion.

Seeing it that way answers a question we had been circling. roc-ray feels like
a platform in every sense: it provides effects, it owns the loop, it calls your
`init!`/`update!`/`render!`. Our web platform declares the same three functions
and provides no effects at all — no `hosted` block, nothing the app may reach
out through. It is a platform in Roc's technical sense and a **doorway** in the
ordinary one. Neither word is wrong; they are describing different axes.

## The one change that makes the inversion possible

Both platforms ask for the same triple. Every difference is in the arrows:

```roc
# roc-ray asks for                      # ours asks for
update! : model, Input, Io => model     advance : model, Keys, F32 -> model
render! : model, Draw.Frame => {}       frame   : model -> List(Shape)
```

`render!` is *handed a surface and returns nothing*. `frame` is *handed nothing
and returns a description*.

That is the whole of it. A function of the form `model, Frame => {}` can only
be called by something that can make a `Frame` — so the caller must be a
platform, underneath you, owning the loop. A function of the form
`model -> List(Shape)` can be called by anyone, from anywhere, including a
language that has never heard of Roc.

**Making the output data is what lets control live outside.** Everything else
followed from that one decision.

## Input is the same trick, and roc-ray had already done it

We expected input to be the hard direction. It was free, because Luke had
already made a snapshot a *value*: `Devices.none.with_key_down(KeyW)` is how
roc-ray's own tests drive a game. A snapshot is data, so a browser's event loop
can build one, and a test can write one down.

That is why a ported game's `read_controls` — the single function in each of
these games that touches the keyboard — compiles on both ends with its import
line changed and nothing else. We built `Keys`, `Mouse`, `Math`, `Color` and
`Random` to mirror roc-ray's surface *under roc-ray's own names*, and the ports
cost almost nothing: snake's `Snake.roc` is verbatim; breakout's `Ball`,
`Bricks` and `Paddle` changed one line each. Only the drawing was rewritten,
because upstream draws imperatively and here a frame is a value.

Adding the mouse later was the test of whether that was luck. It was not: one
more argument, no new mechanism, and breakout is now played by pointing at it.

## Where the idioms are

If there is something here for other people, it is these, and none of them is
about games.

**A frame is a value, not a sequence of calls.** This is the load-bearing one.

**Input is a value too, and the same value on both ends.** Then the function
that interprets it is written once.

**Mirror the host's names when you are shadowing its concepts** — module name,
type name, method name. A port then costs its import lines. But only where it
is unambiguous: we had to call ours `Input` rather than `Devices`, because two
nominal types with the same qualified name are ambiguous to the *compiler*, and
aliasing the module does not help.

**Let the thing declare its own rate.** A movie paced by the display runs at
one speed on a 60 Hz monitor and another on a 144 Hz one; the same movie on
roc-ray's default ran four times faster again. `fps` belongs to the program,
and both runners pace to it.

**Put the width of a channel in the channel.** Our sound indicator counted
three tones by hand. Breakout has five, so breaking a brick — the point of the
game — lit a speaker with no sound in it, and nothing failed.

That last one is the recurring failure, and it is worth naming on its own.

## Silent decoders

Three bugs this week had the same shape: two halves of one format kept in step
by attention, and nothing between them.

The sound widget guessed a width. The JavaScript frame reader, handed a brush
mode it did not know, computed an undefined span, made its cursor `NaN`,
compared `NaN < length`, got `false`, and **dropped the rest of the frame in
silence**. And the check we wrote to catch such things could not see colour at
all, because a canvas fill colour is a property assignment rather than a call,
and a gradient's stops went to a stub — so a colour regression was invisible to
the only automated eye we had.

Each was a decoder that disagreed with its encoder. Each passed every check
that existed when it was written.

Which points at the real gap. `ShapeWire.pack` in Roc and `shapewire.js` in
JavaScript are an encoder and a decoder for one format, written twice by hand.
Roc has a name for what should be doing that: `roc glue` generates host
bindings from the compiler's own type table, and its README argues the case
better than we would —

> platform code should consume generated glue instead of hand-rolling Roc ABI
> bindings

— and ships `ZigGlue.roc`, `RustGlue.roc` and `CGlue.roc`. There is no
JavaScript one. So we started `JsGlue.roc`: it reads the type table and emits
readers, and for our platform it already generates the list walk that decodes a
frame — ptr at 0, length at 4, stride 4 — which reads the same 3,820 words our
hand-written decoder does. Tag unions are the gap that matters, since a `Shape`
is one, and the compiler already hands over the discriminant offset and each
variant's payload layout.

We did not need the ABI to get this far, because we flattened everything to a
list of 32-bit words and dodged it. That is why 174 lines of JavaScript suffice
— and it is also exactly why nothing could check us.

## How far this goes

The browser side is small, and the smallness is not about games. In the same
repository: 43 lines of JavaScript run 46 GPU compute kernels, 110 run a UEFI
framebuffer with a keyboard controller, 221 run any of these games. Safari is
about 120 Roc modules and adds **zero** JavaScript.

So the size law is roughly: **the host code is proportional to the vocabulary
of the wire and the surface of the devices, and independent of the complexity
of the program.** A narrow waist, in the sense the IP hourglass is one.

Which also says where it ends. Sprites and real audio fit — they are still
descriptions, wanting a handle to something the runner loaded. Mouse fits; it
is input. **The wall is asynchrony**: anything the browser will only give you
as a promise, wanted in the middle of a step. A pure `advance` cannot await.
Our own survey of roc-ray's two dozen examples says the same thing from the
other side — every one we could not port needed `Task`, `Http`, `Sqlite` or
`Udp`, and none of them was blocked by graphics.

There are two ways through that wall and the repository has already priced
both. One is hosted effects, which in a browser means a Web Worker, a
synchronous XHR, a `SharedArrayBuffer` and cross-origin isolation headers. The
other is Elm's: the program answers a list of requests and receives results as
data on a later tick. roc-ray has already built that and named it —
`App.Input.messages`, filled by `Task.spawn!`. It keeps the frame pure, it
keeps the determinism that `fps` exists to protect, and it is the only one of
the two that both runners could implement.

That is the next interesting question, and it is a long way past screensavers.
