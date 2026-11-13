# The promise hunt

Four cold hunters read the whole book, about ten chapters each. Each one listed every promise its chapters make: a forward pointer, a teaser, an opening that says what's ahead, a claim about what the book holds, and each appendix row's chapter. For each promise, the hunter said where the book pays it. They checked 353 promises, and 311 were paid where they should be.

| Verdict | Count | What happened |
|---|---|---|
| Paid | 311 | Nothing to do |
| Paid later, unsaid | 13 | A pointer where a reader would hunt; plain facts left alone |
| Unpaid, easy | 9 | Paid in a sentence or two, or cut where cutting was shorter |
| Unpaid, out of scope | 1 | Cut: a code comment naming a benchmark the book never mentions |
| False | 19 | Corrected against the code |

Every false sentence and every unpaid promise is fixed. Three forks of me phrased most of the fixes, and I did one group myself.

## The false ones worth knowing

- **The problem** said motion "carries" the cat and the bird. They're derived from the clock and the carried plan. The verb is fixed in both places.
- **The book's early lists** promised towers a dozen chapters before Radio towers. They now name the cow and the tree, and the towers come with the world.
- **Types** gave the three reasons for `OutOfSight` wrong. They now match the errors chapter: behind the camera, under the horizon, and too small.
- **Three chapters** said the beacons follow "the clock alone". A beacon follows the clock and its tower.
- **Radio towers** said every tower gets a beacon disc. A dim or small beacon gets none.
- **The beacons** credited the disc to the tower's sighting. It's `Tower.tower_shapes`.
- **The appendices** credited two rows to the wrong chapter. The list-functions table claimed to be complete, and it now says "main".
- **The glossary** said anything crossing the near plane is cut. Only rods, faces and patches are cut. A thing whose foot is short of the plane is refused.
- **The book's last sentence** claimed the appendices gather the patterns. You caught that one, and it's gone. The book now ends on "Get the types right, and everything else follows."

## Easy promises, now paid

- The sun's "one piece of spherical trigonometry": the sky turns about its pole at 45° latitude on the winter solstice, so the sun sinks into the southwest.
- How the rider stops at the road's end: `exit_speed` is rest on the last segment, so the bend limit brakes the bike to a stop.
- Mountains' "turn that comes from the lens" is now named: `Lens.turn_at_x`.
- The throttle's "the cat's has its own chapter" now names that chapter: What a cat does to the rider.

The rebuilt book is at http://143.244.172.148:9210/tutorial.fresh/
