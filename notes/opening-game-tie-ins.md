# Five game tie-ins for the opening chapter

*Five short pitches, one paragraph each, each aimed at a different reader. They'd sit after the paragraph that describes the ride, and before "Safari Ride is written in Roc". Flow comes later. One of the five is a plant; you're blind to which.*

---

**1. For the programmer who has written a game loop**

Today Safari Ride is a screensaver: it plays itself, and the only keys it takes pause it and step it. But look at what's underneath. Each step carries a small state forward and works out everything else from it, which is exactly the loop at the heart of every game. The rider already has a throttle, and the ride's own code works it. Hand that throttle to the arrow keys, and the screensaver becomes a game. This book reads the loop you'd build it on.

**2. For a family watching together**

Right now the ride is something to watch, like a fish tank with a road in it. Most bends have an elephant, so the first giraffe gets a cheer. That's already half a game: spot the rare animal and count what you saw. The other half is easy to imagine, because the program knows exactly where every animal stands, at every step. A score is a few lines away, and the book shows the code that knows where they are.

**3. For anyone who has chased a bug that happens once in a thousand plays**

Safari Ride is a screensaver for now, and an unusually dependable one. It's completely deterministic: the same step always draws the same picture, down to the pixel, and the book's tests hold it to that. Games prize that property and rarely have it. It's what makes replays, speedrun verification and reproducible bug reports work. When Safari Ride becomes a game, it starts with the hardest part already done.

**4. For a game-jam weekend**

The ride runs itself today, but it's full of moments that want a button. The cat waits by the road for its chance to cross, and the rider has to react. Give the player that reaction, add one rule and a score, and you have a reflex game you could finish in a weekend. Until then it's a screensaver with good timing, and the book explains how each of those moments is planned.

**5. For two riders on one road**

Safari Ride is a screensaver with a single rider today. Because every step is worked out from a small state, two copies of the ride that see the same inputs stay in lockstep without sending each other a single picture. That's how many racing and strategy games keep players in sync across a network. Put two riders on the same road, one per player, and the ride becomes a race. The book reads the small state that would make it possible.
