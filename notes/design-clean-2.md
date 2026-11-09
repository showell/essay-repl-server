## A small story, a rich picture

The last chapter looked at Safari Ride from the seat of the person watching it. They see a world, the rider's view of it, things in motion, a frame on the screen, and a few controls. Now we take the programmer's seat. Each of those five problems has an answer, and each answer has a home in the code.

Start with what changes. Not much happens in Safari Ride. A rider rides down a road. Now and then a cat or a bird crosses the rider's path. The beacons blink on the radio towers, and the sun goes down. Four small things tell that whole story at any moment: where the rider is, where the truck is, the time on the clock, and when the cat or the bird ahead starts to move.

The picture is another matter. At step 1,529 of the ride, the frame paints 2,121 shapes over its backdrop of sky and grass. While the ride plays, it takes thirty steps a second. One step later the rider has moved on, and the road, the trees and the cows all shift on the screen. So Safari Ride keeps the small story, and describes the rich picture fresh, every frame.

Most of Safari Ride's Roc code lives in modules. A module is one file, named for what it holds: `World.roc` holds the module `World`. A name like `World.route` means `route`, from the module `World`.

### The world

The world is a value in the Roc code. `World` holds a short list of segment plans, one for each stretch of road. Each plan is a record of this type:

```roc World.roc
## One segment of the route as planned: its length and scenery, and what
## lives along it.
SegmentPlan : {
	length : Distance,
	scheme : Trees.Scheme,
	encounter : Segment.PlannedEncounter,
	pigs : World.PigPresence,
	bull : CowHerd.Bull,
}
```

Each field's type comes from the module that owns it, so `Trees.Scheme` comes from `Trees`. Even inside `World`, its own types carry the prefix, as `World.PigPresence` does. The first plan fills in 500 metres of road, `AllGreen` trees and a bird to meet (`BirdHere`). The list wraps each plan with its bend: this one turns 50° into the next segment, and an elephant and its baby stand at the bend.

The plan never says where a single tree stands. `World.route` builds the whole route from the plans, once, before the ride starts, and the trees, the herds and the towers all follow from them. The plans are Roc code, so the compiler checks them: a plan that leaves out its length doesn't compile.

### The rider's view

Every frame, `RiderCamera` places a camera where the rider is, facing where the rider looks. The trees, the animals, the towers and the truck then go through the same three forms: placed on the road, sighted by the camera, and turned into shapes. `Pipeline` writes the steps between those forms once, for all of them.

One rule gives both where a thing lands on the screen and how big it looks there. It's the rule a pinhole camera follows: twice as far away looks half as big. A thing the rider can't see is refused, with a tag that says why. `BehindCamera` means it's behind the rider, and `BelowHorizon` means the curve of the earth hides it.

### Motion

One function moves the ride on. `RideInstant.next_or_restart` takes the world and one moment of the ride, and gives the next moment. It moves only the four small things, in a fixed order. The rider reads where the cat or the bird ahead has got to, then moves, and the clock ticks. Then the truck and the encounter plan answer the rider's new place. That order is how a cat in the road stops the rider speeding up, and how the cat times its crossing to where the rider has just arrived.

Everything else that seems to move is worked out from those four things. The sun goes down because the clock says so. No code moves a sun.

### The screen

The Roc code never draws. `FrameView` describes each frame as a list of shapes, in the order they're painted: the mountains, then the ground, then the things beside the road, sorted far to near. Each shape is painted over the ones before it, so near things cover far ones. Seeing works this way in the real world, too. The world doesn't paint itself onto your eyes: light brings you information, and your mind makes the picture.

The painting belongs to the platform. A Roc program runs on a platform, the layer underneath it that talks to the outside world: here, the screen and the keyboard. Safari Ride gives its platform one value, `SafariApp.canvas_app`, and two of its fields do the work:

```roc SafariApp.roc, in canvas_app
# ...
model_at_next_step: CanvasApp.untimed_model_at_next_step(model_at_next_step),
frame_shapes: |m| FrameView.frame_view_at(m.tour.route(), m.tour.instant()).leaned_shapes(),
# ...
```

`model_at_next_step` gives the ride's next state, from the keys that were pressed. `frame_shapes` is a function, written `|m| …`, of the model `m`. It asks `FrameView` for the frame at the tour's current moment, and gives the frame's list of shapes. In this page, the ride runs as WebAssembly, and JavaScript paints each list on a canvas. The same Roc code also runs as a native program on a platform called roc-ray. Safari Ride is the top layer, and it's the same on both.

### The person watching

The controls are a handful of keys, named beside the ride, and `SafariApp` answers them. The ride itself never knows it's paused. Stepping back has to be as quick as stepping forward, so `Tour` keeps every moment since the ride last started. To step back, it takes the moment before, and the next frame is described from it like any other.

### Where we start

So what are those 2,121 shapes? All but eight of them are polygons. A far tree is one rectangle of trunk under eight triangles. We start there, with one triangle.

