# The truck, shape first

*2026-11-08. Your point: to draw a truck I first need to know what it looks like, so show the cab, the windows, the tires and the trailer, say it's blue, and have something like `truck_picture : Sighting -> Picture`. Here's what the code does today, the design, and one choice it opens.*

---

## What's there today

`TruckBody` builds faces, not parts: `side`, `back`, `roof`, `windshield`, `nose`, `tire`. Every one of them takes a `TruckSetting` (the spot, the lens, the road), because each face places its own corners as it builds them. So shape and placement are tangled together, and nothing describes the truck on its own.

It is blue: dark navy sides (`0x152150`), a navy body (`0x1C2E66`) and a lighter blue roof (`0x3A52A8`), with near-black tires. The windshield is painted body-blue, though, so there's no glass. There are no side windows either. (I won't add any: no new features until the book is done.)

## The design: shape knows nothing about the road

```roc
## A face of the truck: a color and its corners, in the truck's own frame.
TruckFace : { color : RgbColor, corners : List(TruckPoint) }

trailer : List(TruckFace)     # its back, two sides and roof
cab : List(TruckFace)         # two sides, roof and nose
windshield : TruckFace
tires : List(TruckFace)       # one per wheel, on each axle

## The whole truck as it is built: the parts above, with no place in the world.
truck_shape : List(TruckFace)
```

None of these take a setting. They're plain values, which is what a shape should be, and they're the first thing the chapter shows: the colors with their names (`truck_blue`, `roof_blue`), then the trailer, the cab, the windshield and the tires. The widget at the top of the chapter already shows exactly this truck from three angles.

Then the one function a reader asks for, which is placement and projection together:

```roc
truck_picture : TruckSighting.Sighting -> Picture
```

## The choice: how the truck is placed

Today every corner is placed on the road separately, through `RoadAhead.rider_point_at`. So a truck standing across a bend bends with the road. A real truck doesn't bend: it's rigid.

- **A, rigid (lean):** the sighting works out the truck's foot (it already does) and its **heading** relative to the camera: the road's direction at the truck's spot. `truck_picture` turns each corner by that heading, adds the foot, lowers by the spot's `drop` (from the sightings redesign), and projects. So a `Sighting` of `{ spot, heading, lights }` plus the lens is all it needs, and `truck_picture` really is `Sighting -> Picture`, with the lens in the sighting or passed beside it. The truck no longer needs the road at all, and `TruckShape.TruckOnRoad` goes.
- **B, keep per-corner road placement:** the shape is still separate, but placement keeps asking the road for each corner, so the sighting must carry the road and the vantage. That's closer to today, with the same pixels.

**Lean: A.** It's how a rigid object is drawn in any 3D program, and it puts all the world knowledge in the sighting, which is where your sightings question was pointing. The pixels move slightly, only where the truck stands across a bend. They'd be re-pinned together with the sightings redesign's re-pin, which is in flight now.

## Order

The sightings redesign is changing the truck's lowering right now, so this goes straight after it, as one lane: the shape split (pixels hold), then rigid placement (pixels move, re-pinned with the frames looked at by eye). Then the truck chapter opens with the shape: "The truck is blue", the parts, then the one function that draws it from a sighting.

Rigid (A) or road-placed (B)?
