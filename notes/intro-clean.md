# Introduction, a clean draft

The first chapter under the new rule: a clean draft every time, with no regurgitating and no editing yet. I closed the old draft and kept only its facts. I dropped two of its numbers, "about ninety modules" and "about four minutes", because no expect pins them (B2). Reply on any paragraph.

---

# Safari Ride: a tour of a real Roc program

This book reads one whole Roc program with you, from the top down and back up.

## Introduction

You are about to read a complete program. It's called Safari Ride, and it's running in the page below. Give it a moment to load, and the ride starts by itself.

*[the ride widget] The ride, running as you read. Click it to give it the keyboard: Space pauses it, and the arrow keys step it.*

A rider on a motorcycle follows a long road through open country. Trees line the road. Cows and pigs graze beside it. A truck drives on ahead. Radio towers blink on the horizon. A bird takes off as the rider comes near, and a cat crosses the road. The sun sets behind the mountains, the truck turns on its headlights, and night falls. At the end of the road the rider stops, and the ride starts over.

Nobody steers and nothing keeps score, so Safari Ride isn't a game. It has a game's hard parts, though: terrain, a camera, physics, and things that react to the rider.

The program handles all of that with one simple design. Each step of the ride carries four things: the rider, the truck, the clock and the plan for the encounter ahead. Everything else is derived from those four. The sky's color, the sun's height, the trees in view and the cat's pose are all calculated fresh, every frame. The same four things always give the same picture.

This book shows how that design keeps a busy program simple, and how Roc makes it natural. Most of the code is plain Roc: records, tags and functions. That's a feature.

A safari is a guided tour, so this book is a tour of a tour. We start with the whole program. Then we hold one frame still and build everything in it, from a single triangle up to a herd of cows. Then we let the clock run, and the rider, the truck and the cat start to move. At the end we zoom back out.

You should be able to read a little Roc. If you can't yet, start with the official Roc tutorial. This book explains each Roc idea where it first comes up.
