# What the truck carries into its drawing

A review of the truck's drawing (TruckBody, TruckLights) found seven things. I decided six; this one is a question of form, so it's yours.

## The facts

Every kind is drawn from a `Picture.Setting(context)`, which is `{ spot, cam_focal, context }`. The `spot` says where the thing stands, and the `context` is whatever else the kind needs.

The truck's context is the road. On the way in, `LitTruck.scenery_picture` repacks the setting:

```roc
TruckInView : { view : { road, cam_focal }, spot, box : TruckBox }
box = TruckShape.truck_box(spot.road_point())
```

That trips two smells from the guide:
- **One input packed several ways.** `road` and `cam_focal` get a third wrapper.
- **A stored value restates another.** `box` comes from `spot`, so the record could hold a box that disagrees with its spot.

The tower has the same shape, by your earlier call: its setting's context is a `Tower.Footprint`, worked out from its spot and the road once at sighting, then carried.

## The options

**(a) Like the tower.** `Picture.Setting({ road, box })`. The repacking goes, and the box is worked out once and carried, as the tower's footprint is. The kinds stay one family.

**(b) No stored box.** Pass `Picture.Setting(RoadView)` straight through, and call `TruckShape.truck_box(setting.spot.road_point())` where it's needed: once each in the faces, the headlight beams and the brake lights. Nothing derived is stored, but the truck no longer matches the tower.

Pixels hold either way.

## My recommendation

**(a).** The box is the truck's footprint on the road, the same idea as the tower's. Working it out three times to avoid storing it trades one smell for a repeat. If you'd rather have (b), the tower should follow it too, so we'd stay one family.

## Decided without you, for the record

- The four strip faces (back, roof, windshield, nose) and the brake lamp come from one `TruckShape.strip_corners`, so about 130 lines become five short calls.
- `TruckFace` goes. A face is a `Camera.FlatPolygon`, sorted by the mean of its corners' depth.
- The helpers move out of TruckLights' and TruckBody's blocks. `Screen.distance` gets its second user in `Tower.screen_rod`.
- The beam's middle is `at_lamp(headlight_height)`, so `midpoint` goes.
- `ArgbColor.from_rgb(color, { alpha })` replaces reading an RGB number as an ARGB one. The sun glow is its second user, and it waits for the lib lane.
- The tests that restate constants go.

## Steve's answer (2026-11-07)

Agreed: (a), like the tower. `Picture.Setting({ road, box })`, with the box worked out once at sighting.
