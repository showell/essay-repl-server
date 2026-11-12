# Code in the first pages: four riffs

Aurélien wrote: "perhaps it would be more motivating to start almost right away by creating a tiny scene, then gradually extend and organize the project as the problems arise, rather than presenting the whole journey upfront."

Here is where the book stands. Chapter 1, the Introduction, holds the ride and four paragraphs, with no code. Chapter 2, The problem, holds a diagram and a table of five pieces, with no code. Chapter 3, Platforms, shows `web.roc`, the first code in the book, which is wiring. Chapter 4, The pieces as types, is a tour of about 140 lines. It covers all five pieces, down to `RideInstant` and `Tour`, and the book doesn't build those for another twenty chapters. Chapter 5, Things, has the first code a reader would call Safari code: the cow.

The constraint for every riff is your scope, a static image. And no hello world: the first code is real Safari code, on theme.

## Riff 1: the frame in five lines

The Introduction keeps the running ride. Right under it, a still picture: the cow and the bull on the grass by the road, the cow widget as it is today. Under that, the call that produces that picture, from the widget's real code:

```roc
picture_shapes = FrameView.painted_shapes({
	backdrop,
	ride_shape_lists: [road_shapes, bull_shapes, cow_shapes],
	space: upright_space,
})
```

One paragraph reads it: a picture is a backdrop with lists of shapes on top, far things first, and the platform paints the list. That's the book's first big idea, the frame as a value, in code on page 1. It reads nearly as English, so it needs no walkthrough.

- **Gains:** code on the first page, on theme, and the idea that drives the whole One frame half.
- **Costs:** `backdrop`, `road_shapes` and `upright_space` are names the reader can't open yet. C8 wants a function's details after the reader has seen it, and this snippet asks for some trust. The fix is to say so plainly: "Every name here gets its own chapter."
- **Disruption:** small. One snippet and one paragraph, and the rest of the book stands.

## Riff 2: the app is one record

The first code is the shape of the whole program, side by side twice. The cow picture's app:

```roc
canvas_app = {
	size: { width: canvas_width, height: canvas_height },
	frames_a_second: WidgetPage.fixed_picture_frames_a_second,
	init: {},
	model_at_next_step: |model, _input, _seconds| model,
	frame_shapes: |_model| picture_shapes,
	...
}
```

Then Safari Ride's:

```roc
canvas_app = {
	size: { width: Screen.width.to_f64(), height: Screen.height.to_f64() },
	frames_a_second: 30,
	init: initial_model,
	model_at_next_step: CanvasApp.untimed_model_at_next_step(model_at_next_step),
	frame_shapes: |m| FrameView.frame_view_at(m.tour.route(), m.tour.instant()).leaned_shapes(),
	...
}
```

A still picture is an app whose model is `{}` and whose step gives the model back unchanged. The ride is the same record, with a real model and a real step. The reader sees the book's theme, a small carried state with everything else derived from it, as two records on page 1. The rest of the book fills in the `frame_shapes` line and the `model_at_next_step` line.

- **Gains:** the theme in code before anything else, and a natural home for the Platforms chapter's content, which shrinks to a few sentences.
- **Costs:** the records are architecture, not scenery. A reader eager for a cow gets plumbing first, and `sounds` and `tones` are cruft for this page (H6). The widget's record would need trimming, or the snippet would need cutting at "...", which hides real code.
- **Disruption:** medium. Platforms folds into the opening, and The pieces as types loses its Person-watching stop.

## Riff 3: grow one scene

This is Aurélien's suggestion taken literally. The One frame half becomes one static scene that grows, chapter by chapter, and each chapter's widget is the scene so far:

1. sky and grass;
2. a cow;
3. the elephant and the other billboards at a bend (`match`);
4. a far tree (shapes, `map`, paint order);
5. the road, then rails and towers;
6. the pipeline, once the scene holds enough kinds to need one.

The Problem's five pieces and the types tour move to the end of that first act, as a map of what the reader has built: "here's what you've read, named." The structure appears as problems arise, which is his point exactly.

- **Gains:** the strongest answer to his critique. Each chapter has a reason that comes from the scene: "the scene now has four kinds of thing, so we need one way to render them all." The pipeline chapter earns itself.
- **Costs:** the biggest rewrite on the table. It reorders chapters 2 to 12, and most of those have passed your review. It also bends B (truth): the code is finished, so "we add a road" describes how the *book* grows the picture, never how the program was written. The widgets can honestly grow, since each one is a thin wrapper, but the prose must never pretend the code grew. And you told me Zulip feedback guides work forward, without overhauls. This riff is an overhaul.
- **Disruption:** large. It's a new structure for the first act.

## Riff 4 (pushback): he's asking for less upfront, not for more code early

I read his message differently from you. The clause that carries the weight is the last one: "rather than presenting the whole journey upfront, which might seem daunting and kind of spoil the fun." "Code in the first pages" is the cure he proposes. The disease he names is the upfront plan.

If that's right, adding a snippet to page 1 treats the symptom. A reader who meets the cow's code in chapter 1 still has to climb the five-piece table and a 140-line tour of `RideInstant`, `Tour` and `SafariApp.Model` before the book gets back to the cow. The daunting part is still there, now with a teaser in front of it.

The mission has a rule for this, C13: fix by subtraction first. Here's the subtractive version:

- **The problem shrinks to its first paragraph,** or folds into the Introduction. The five-piece table and diagram move to where the book first needs them: the start of Motion, where the reader has built the frame and needs the map for what's next.
- **The pieces as types splits.** Its first two stops, `Distance` and the things, stay up front, since a cow needs them. The world, the view, motion and the person watching each move to the act that builds them.
- **Platforms stays short,** as it is.

With that done, the first Safari code, the cow, lands in chapter 3 instead of chapter 5, and nothing new was written. A one-snippet opener from Riff 1 can still sit on top, if we want it.

There's a second, more practical pushback. A "tiny scene" is small on the screen, and large in code. The cow widget is 271 lines: a herd of one, a camera, a sighting, a backdrop, and a road. An honest tiny scene in the first pages shows its top call (Riff 1), never its build. A scene the reader builds from scratch in the opening would be hand-written code that Safari Ride doesn't run, which is the hello world you want to avoid.

- **Gains:** answers his real complaint, with deletion rather than addition, and it also answers notramo's "filler" and Aurélien's "verbose" at the front of the book.
- **Costs:** it moves passed material. The pieces as types is the chapter that teaches the reader to read types, and splitting it spreads that lesson thinner. Chapters 6 to 12 refer back to it in places, and those references would need checking.
- **Disruption:** medium, mostly moves, little new prose.

## Where I land

Riff 4's subtraction, with Riff 1's snippet on top. The subtraction answers what he named as the problem. The snippet answers what you read in his message, code in the first pages, at the cost of one paragraph. Riff 2 is a good idea for wherever Platforms ends up, and Riff 3 is too big a structural change to make in response to one message.
