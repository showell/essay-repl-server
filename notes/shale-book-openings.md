# Five ways to open the Shale book

Five candidate opening paragraphs. Each takes a different angle on the same premise: the reader learns a language they read every day and almost never write. Under each is a line on what it bets on. None of these is a draft of the book; they're probes for the goals and the voice.

## 1. The reader's job

> This book teaches a language you will read every day and almost never write. Your agent writes it. Each time the agent wants to search your files, run your tests or change your code, it writes a short Shale script, runs it, and reads what comes back. The script stays behind, and you can read it too: what the agent looked at, what it ran, what it changed, and how far it was allowed to go. Here we learn to read those scripts quickly, to judge them, and to steer the agent that wrote them.

**Bets on:** the premise, stated plainly in the first sentence. The reader knows the deal before the paragraph ends.

## 2. The scrollback

> Scroll back through a long session with a coding agent and you find hundreds of commands: a grep here, a sed there, a test run piped through tail, a Python one-liner that rewrote twelve files. Each one did something to your machine, and most went by too fast to read. Shale turns that scroll into something you can read. Every action is a small script with its limits written into it: how long a program may run, how much of its output comes back, which folders the script may touch. Learn to read those scripts, and the scroll becomes a record.

**Bets on:** a pain the reader has already felt. The language arrives as the answer to it.

## 3. A reading knowledge

> Scholars used to speak of a "reading knowledge" of a language: enough Latin to follow Cicero, with no plan to write a letter in it. That is the knowledge this book aims for, in Shale. Your agents write Shale, and you read it. A reading knowledge comes faster than a writing one, because recognizing a form takes far less than producing it. By the end of the book, a glance at a script will tell you what it reads, what it runs, what it changes, and where it stops.

**Bets on:** an old, respectable frame for an odd premise. It also sets the scope: recognition, with production left to the agent.

## 4. Something for trust to hold

> Letting an agent run commands on your machine is an act of trust, and a shell gives that trust nothing to hold. A bash line can hang, flood the screen, wander out of the project or delete it, and it looks the same either way. Shale gives trust something to hold. Every program runs with a timeout. Every script stays inside the folders it names. Every risky step is spelled out by name, with the agent's reason written beside it. Here we learn to read those guarantees, and to weigh the reasons an agent gives when it steps past one.

**Bets on:** safety as the reason to care. The reader's question is "can I let this thing loose?", and the book answers it.

## 5. The machine this book was written on

> On the machine where this book was written, agents run no bash. A hook stops every shell command before it starts and lets exactly one form through: a Shale script. Every build, test run, search, merge and deploy passes through that gate, along with the checks on this book's own prose. Each script is short enough to read and plain about what it does. This book is a guide to reading them: what to look for first, what a healthy script looks like, and what a script tells you about the agent that wrote it.

**Bets on:** a true story from a working setup. The book's authority comes from use, and the reader sees that the idea scales past a toy.

## What the five already disagree on

Picking among these settles a few goals before any prose:

- **Who the reader is.** Openings 1 and 3 speak to anyone curious; 2 and 4 speak to someone already running agents, a little nervously.
- **What the book promises.** Reading speed (1, 3), a record of what happened (2), safety (4), or a practice someone already lives in (5).
- **How much bash is in the book.** Openings 2 and 4 define Shale against the shell, so bash would recur as a foil. Openings 1 and 3 barely mention it.
- **Who "we" is.** Opening 5 implies an author with a machine; the others leave the voice impersonal.
