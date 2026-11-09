## A small story, a rich picture

Not much happens in Safari Ride. A rider rides down a road. Now and then a cat or a bird crosses the rider's path. The beacons blink on the radio towers, and the sun goes down. Four small things tell that whole story at any moment: where the rider is, where the truck is, the time on the clock, and when the cat or the bird ahead starts to move.

The picture is another matter. At step 1,529 of the ride, the frame paints 2,121 shapes over its backdrop of sky and grass. While the ride plays, each frame shows the story one step on. The rider moves a little, and the road, the trees and the cows all shift on the screen. The story barely changes from one step to the next. The picture changes all over.

Safari Ride's design falls out of that difference. It has three pieces.

The stage is the world: the road, the trees, the herds and the towers, and the places where a cat or a bird waits. The stage never changes. The rider moves through it. So we build the world once, before the ride starts, and from then on we only read it. The stage answers the first problem.

The story is the four small things, and we carry it from each step to the next. A step reads the stage and the story, and gives the story's next moment. The story is small enough to keep every moment of it, back to the start of the ride. That's how rewinding works: to go back a step, we take the moment before. The story answers the second problem, and the fifth.

The picture is everything on the screen, and we never keep it. For every frame, the Roc code describes the whole picture fresh from the stage and the story, as a list of shapes. Then the page paints the list. The Roc code never draws. Seeing works this way in the real world, too. The world doesn't paint itself onto your eyes: light brings you information, and your mind makes the picture. To describe the picture, the Roc code works out what the rider sees, and lists far things before near ones, so the near ones are painted over them. The picture answers the third problem and the fourth.

Because each picture comes fresh from its moment, pausing, stepping and rewinding need no drawing code of their own. We describe whichever moment you've asked for.

*The three pieces of the design (a diagram in the book):*

```
the stage (the world, laid out once)  --is read by each step-->      the story (four small things)
the story                             --steps to its next moment-->  the story
the stage                             --is read for every frame-->   the picture (a list of shapes)
the story                             --gives, fresh every frame-->  the picture
the picture                           --is painted by-->             the page
```

The first half of the book holds one frame still, and builds the stage and the picture for it. The second half lets the story move. We start with the picture, and a picture is a list of shapes. The simplest shape is a triangle.
