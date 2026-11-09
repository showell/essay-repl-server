## The problem

Safari Ride shows a world in motion, seen from the rider's seat. It draws that world on the screen frame by frame, thirty frames a second, and you can take the controls at any moment. Those two sentences hold five problems.

The first is the world itself. A long road runs through open country, past trees, herds, ponds, radio towers and mountains. Something has to say where every one of them is.

The second is motion. The rider rides on, the truck drives ahead, the cat crosses the road and the sun goes down. The moving things act on each other, too. The cat times its crossing to the rider coming toward it, and a cat in the road stops the rider speeding up.

The third is the rider's view. The screen shows only what the rider sees. A tree far down the road looks small, a tree close by looks big, and a tree behind the rider doesn't show at all. For everything in the world, the program has to work out whether the rider sees it, where it appears, and how big it looks.

The fourth is the screen. Every frame is drawn whole, from nothing, and nearer things have to cover farther ones.

The fifth is you. The ride is interactive. You'll mostly sit back and watch, but you can also pause the ride, step it forward and rewind it.

Each of the five is a fair amount of work. Safari Ride solves all five with simple code, and this book shows how. The next chapter breaks the problem into pieces, and picks the piece we start with.
