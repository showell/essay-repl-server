# What to borrow from K&R

Kernighan and Ritchie's *The C Programming Language* is the nearest classic to what we're writing: a short book that teaches a language to working programmers, through code. This note lays out its structure as I know it, then asks what Safari Ride's book should take from it.

A note on sources: the chapter list and the opening of Chapter 1 below are checked against current listings and the O'Reilly text. The section contents come from my memory of the second edition, which is reliable for the famous programs and looser for the order of the smaller ones.

## The structure

The second edition (1988, the ANSI one) runs to under three hundred pages:

- **Preface.**
- **Introduction**, a few pages of prose on the language's character: what C is, what it's good for, how it relates to the machine. It shows no programs to speak of.
- **Chapter 1, A Tutorial Introduction.** A fast pass over the whole language, through real programs.
- **Chapter 2, Types, Operators, and Expressions.**
- **Chapter 3, Control Flow.**
- **Chapter 4, Functions and Program Structure.**
- **Chapter 5, Pointers and Arrays.**
- **Chapter 6, Structures.**
- **Chapter 7, Input and Output.**
- **Chapter 8, The UNIX System Interface.**
- **Appendix A,** the reference manual. **Appendix B,** the standard library. **Appendix C,** what changed since the first edition.

Chapters 2 through 8 are the bottom-up order of a language reference: tokens and types, then statements, then functions, then the hard part (pointers), then aggregates, then the outside world. That order is unremarkable. Chapter 1 is what made the book famous.

## Chapter 1 is the whole trick

Chapter 1 opens like this:

> Let us begin with a quick introduction to C. Our aim is to show the essential elements of the language in real programs, but without getting bogged down in details, rules, and exceptions.

It then says plainly what it leaves out. Pointers and structures, the features you need for bigger programs, wait for later chapters. The chapter promises to be correct, and it doesn't promise to be complete.

Then it delivers, in about thirty pages:

- **hello, world**, on the first page of real content. It's the most copied program in history, and its job is tiny: prove the toolchain works and show the shape of a C program.
- **A Fahrenheit-to-Celsius table**, written several times over. The first version uses integers and a `while` loop. Then floating point, then a `for` loop, then symbolic constants. The same small program improves in front of the reader, one feature at a time.
- **Character input and output**, through a run of tiny Unix tools: copy input to output, count characters, count lines, count words. The last of these is essentially `wc`.
- **Arrays** (counting digits and white space), **functions** (`power`), **arguments passed by value**, **character arrays** (a program that prints the longest input line, built around a `getline` function) and **external variables**.

Each section ends with exercises, numbered 1-1, 1-2 and so on.

By the end of Chapter 1, the reader has written, or at least read, a dozen working programs and touched nearly every part of the language. Chapters 2 to 8 then come back over the same ground, slowly and precisely. The tutorial is a first pass; the rest of the book is the second.

## Is there an app theme?

You remembered right: there's no single app. There's something close to one, though, and it's worth noticing. Almost every program in the book is a small Unix tool, or a piece of one:
- a character counter and a word counter;
- the longest-line finder;
- a reverse Polish calculator in Chapter 4;
- a line sorter and a parser for C declarations in Chapter 5;
- a word-frequency counter on a binary tree and a hash table in Chapter 6;
- a `cat`, a directory lister and a storage allocator in Chapters 7 and 8.

The theme is a *world*, not an app: the Unix toolbox, where every program does one small job on a stream of text. The reader knows the world already, because they use it daily, so every example arrives with its purpose understood. Nobody has to explain why you'd want to count words.

Some functions also come back. `getline` appears in Chapter 1's longest-line program and returns in later chapters, improved. The reader meets an old friend, and the improvement shows what the new chapter added.

## What the structure does well

**It answers Aurélien's complaint on page 1.** "hello, world" is code on the first page of the first chapter, and the tutorial keeps the code coming for thirty pages. K&R never makes the reader wait for code. Its Introduction is short, and its Preface is shorter.

**It gets two orders at once.** A language reference wants bottom-up order, so nothing is used before it's defined. A learner wants top-down order: the whole thing first, the parts after. K&R does both, in sequence. Chapter 1 is a quick top-down pass, and Chapters 2 to 8 are a careful bottom-up one. The tutorial says up front that it's a first pass, so the reader forgives its gaps.

**It refines one program in front of the reader.** The temperature table, rewritten four times, teaches more than four separate programs would. Each rewrite isolates one new idea, and the reader sees exactly what the idea bought.

**It's dense, and density is respect.** K&R is famously terse. It trusts the reader to read every sentence, so it writes each sentence to be worth reading. That's the opposite of the "verbose at times" Aurélien felt and the "filler" notramo felt.

**Its examples come with their purpose built in.** The Unix world makes every example self-motivating.

## Where we differ, and should

**K&R teaches writing; we teach reading.** Its first section famously says the only way to learn a new language is by writing programs in it, and the exercises carry that out. Our reader reads one finished program, so the closer model for our *genre* is Lions' *Commentary on UNIX*, a line-by-line reading of a real operating system's source. K&R gives us the pacing, and Lions gives us the premise. Neither one gives us both. That's our book's own territory.

**K&R's chapters are about the language; ours are about the program.** K&R's table of contents is the language's: types, control flow, pointers. Ours is the ride's: things, shapes, a far tree, the pipeline. Our Roc ideas arrive where the ride needs them, which is our deliberate inversion of K&R. It's the right call for a book about how a real program is structured, and it's exactly the value Aurélien named. The cost is that a reader looking for "where does the book explain `where`?" has to know it's in "Asking a kind". Our appendices and glossary are the answer to that cost, as K&R's Appendix A is the answer to theirs.

**K&R has no pictures, and we have a ride.** A C program's output is text, and a text program's purpose is obvious. Ours is a moving picture, and the picture *is* the purpose. We have an advantage K&R never had: the reader can see whether the code is right.

## What to borrow

**1. A first chapter that says it's a first pass, and means it.** K&R's Chapter 1 earns the right to be incomplete by saying so in its first paragraph: essential elements, real programs, no details, rules or exceptions, with pointers and structures later. The new chapter 2, "One page", can take exactly that posture. It glances at one frame as a value, with `frame_view_at` as its line of Roc. It says plainly that the book holds this page still for its first half and comes back to every part of it. Then the gaps read as promises, not as omissions.

**2. Code on the first page of the first real chapter.** K&R's Introduction is prose, and Chapter 1 opens on code at once. Our Introduction is the ride and its description, and that's right, as you said. So the first chapter *after* the Introduction should open on Roc, not on prose about Roc. "One page" should show its line of Roc early, not after four paragraphs of setup.

**3. Refine one thing in front of the reader.** The temperature table is the model. We have a natural candidate: one frame, the same page, gaining a thing per chapter across the first half. That's riff 3 from this morning ("grow one scene"), which you called ambitious. K&R suggests a lighter version: the same frame shown again at a few milestones, with the reader seeing what each chapter added. The widgets already exist, so this is a matter of picking the frame and saying so, not a rebuild.

**4. Old friends come back improved.** `getline` returns in later chapters, and the return is a lesson. We already do this, more than we say: `scenery_sprite` in Things comes back in Asking a kind, and `tree_sprite` from A far tree is the center of The pipeline. The flip book's move to the motion half makes it our best `getline`: `next_or_restart` is glanced at early in The pieces as types, and then opens the second half as the main event.

**5. Density.** K&R says a thing once, precisely, and trusts the reader. Our D3 (Hemingway) and C13 (fix by subtraction) already say this. K&R is the proof that it works for a teaching book, and the standard to check a trim pass against: would K&R spend this sentence?

**6. A world the reader already knows.** We have one, and it may be our biggest asset. Everyone knows a country road, a cow, a sunset, a truck's headlights. Like the Unix toolbox, the ride's world explains its own examples: nobody needs to be told why a far tree looks small. A0 ("keep simple things simple") is the same insight. K&R suggests leaning on it harder in the front: let the world carry the motivation, and save the prose for the Roc.

## What not to borrow

- **Exercises.** They suit a book about writing. A reading book could have a few "try this" moments with the widgets, as the flip book's step-back experiment showed. A numbered list of exercises would change the genre.
- **The bottom-up second half.** Our program-shaped order is what makes the book about structure. Reordering by language feature would make it a reference with a ride attached.
- **hello, world.** You ruled it out, and K&R shows why it worked for them and wouldn't for us. Their hello world proves the toolchain. Our reader has no toolchain to prove, because the ride is already running on the page.

## The one-sentence lesson

K&R's structure is a fast, honest first pass that admits its gaps, followed by a slow second pass that fills them. Our front already wants that shape. "One page" can be our Chapter 1: a short, code-forward first pass at one frame, saying up front that the book is about to slow down.
