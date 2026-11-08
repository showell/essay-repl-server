# Open calls for Steve

**Answered.** Newer calls are in notes/open-calls-2.md.

**Steve, 2026-11-07:** "I agree with your leans except on Rider/RiderState/Motorcycle." So items 1 and 3-10 go as my leans say. Item 2 is reopened in notes/rider-boundaries.md.

Reviews today left these for you. None is urgent; the lanes work around each one. Answer any you like, in any order: a word each is enough. My lean is given after each.

## Types

1. **Read-heavy records: nominal or opaque?** The new rule is opaque by default, with nominal needing a reason. Segment, RideInstant, Tour, FrameView, RiderCamera, Scene, Truck and RiderEyes are records that other modules read field by field, with nothing to guard. Making them opaque means dozens of getters. Segment and Tour can already be built into states that break their rules: a segment's cat should stand by its trees, and a tour's history should run one step apart. The bends widget's 60 m cut and the frame widget's `past_instants: []` do exactly that. *My lean:* "a plain record read everywhere, with nothing to guard" counts as a reason for nominal; Segment and Tour, which do have invariants, go opaque with makers for the widgets.
2. **RiderState and Motorcycle:** they form a state machine whose transitions live in Rider, not in the types. Should the transitions move into the types (the style guide's rule), or should Rider stay the owner, with "with" makers? *My lean:* Rider stays the owner.
3. **`RoadAhead.SegmentInView`** stores both `index` and `segment`, which could disagree. Opaque would make it honest, at the cost of churn in about 30 readers. *My lean:* yes, but later.
4. **`Brush.Fill` opaque?** It would close the bypass where an app writes a `Glow` or an `Ellipse` that no painter can shade. It crosses the glue into JS, so every app's literal fills change. *My lean:* no; the new `Brush.ellipse` and `Brush.glow` makers are enough.

## Names

5. **HexColor's name.** The module is about shading RgbColor channels, not hex. A suggestion is `ColorShade`, with the channel readers moving into lib's RgbColor. *My lean:* yes.
6. **`ScrubWidget` becomes `WidgetPage`?** Four of the widgets scrub nothing, and its doc has to translate the name first. *My lean:* yes.

## Behavior

7. **One size rule for everything far away.** Today far animals on billboards are size-tested through the resting lens and trees through the camera's lens, and Billboard also cuts its own picture below 1 px. One rule, kept in Pipeline, would be honest, but **pixels move**: far animals would come and go at different distances when the view is wide. *My lean:* yes, with an eye test.

## Tests

8. **Does "no import only a test uses" bind widgets?** Widgets have no CrossModuleExpects of their own. Stills imports Font only to test that each name fits its cell, which is a real layout check. *My lean:* the rule binds widgets too, and their real checks move into gates/WidgetExpects.roc.
9. **The gaze widget's table** (speeds, gazes, the phase boundaries, gawk-then-brake). It tests Rider, Gaze and Gawking rather than the widget, and the parked book quotes its numbers. *My lean:* move it to the game's tests and keep the numbers there.

## Widgets that look like debugging tools

10. The review sorted these as inspectors rather than book pictures: **step** (Tour's history as readouts), **stills** (every still in a grid, with counts), **route** (a map with `Str.inspect` readouts), **bends** (three bends with sighting counts), **sky** (the Sun's and Sky's curves as charts), **rehearsal** (LeanSearch's 12 tries; also a book picture). These look like book pictures: beacon, cat, bird, tree, shapes, frame, gaze. You said debugging widgets are "rarely worth saving". *My lean:* keep them all until the book unparks, then decide chapter by chapter.
