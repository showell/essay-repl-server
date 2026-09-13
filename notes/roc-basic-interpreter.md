# A BASIC interpreter in Roc

We wrote a BASIC interpreter in pure Roc. It runs two dialects: ECMA-55
Minimal BASIC, and the microcomputer BASIC of the 1978 Creative Computing
games. It runs as a command on the desktop and as a web REPL in the browser,
where a program draws on a memory-mapped screen and waits for typed input.

## What it is

- **A listing is parsed once** into statements, and every variable name
  becomes a slot before the program runs.
- **The evaluator only reads the machine.** An expression answers its value
  and its effects (a report, a stop, a random number drawn), and the
  statement that asked applies them.
- **The machine is three structures.** What never changes during a run is
  the program. What a statement changes is the machine: the program counter,
  variables, arrays, loops, return points. The devices sit behind one
  reference: the terminal, the screen, the address space and the
  framebuffer.
- **The run loop is one pure function**, `machine_state_at_next_effect`. It
  runs statements until the program needs the world: a line of input, a
  sleep, the end. The web page resumes it from there.

It is a fairly complete implementation:

- all of ECMA-55, with the standard's load-time checks and its exceptions
  reported as it requires;
- the games' extensions: string functions, DEF FN, ON GOTO and GOSUB, POKE
  and PEEK into screen and colour memory, a plotting framebuffer, SLEEP, and
  RND drawn as basic101 draws it, so a game that uses random numbers can be
  graded byte for byte.

**It passes the NBS conformance suite: 195 programs pass, none fail, and 13
print no verdict a script can judge. 55 of the 99 games match their captured
output exactly.** The rest of the games are ordinary interpreter work, one
game at a time.

## What Roc made hard

**Roc is not an ideal platform for interpreting a mutable language like
BASIC, unless you are content with memory allocations that are hard to
predict.**

A BASIC program is a long series of small writes: a variable here, an array
cell there, a character onto the screen. In Roc every value is immutable, and
the compiler writes a structure in place only when it can see that nothing
else refers to it. When it cannot see that, it copies silently. The language
has no way to say "this must be written in place", and no warning when it is
not.

On Roc's default platform every heap allocation is a system call, which gave
us an honest instrument. We counted allocations per statement on a ladder of
tiny programs, each adding one feature, and held each to zero. What the
ladder showed was a set of rules no one would guess from reading the code.
Each of these made a write copy:

- a fallback value that names the list being written;
- a value passed down a recursion and handed back;
- a helper function given a record together with something read from that
  record;
- a `match` whose arms carry their bodies inline rather than calling a
  function;
- a field taken out of a record in one statement and put back in the next.

None of these changes what the program computes; each changes whether a
write copies. Two versions of the same statement that look equally harmless
can differ by a copy per execution. One corner is still unexplained: INPUT
makes two allocations more than it should.

**Well-chosen data structures remedied the worst of it:**

- **persistent vectors** of 32-way nodes for variables, arrays and memory, so
  a copy that does happen is a short path of small nodes, never a whole table;
- **stacks as a list and a depth**, so a return or a loop exit reuses a cell
  instead of shrinking the list;
- **a read-only evaluator**, so the machine is never threaded through a
  recursion;
- **the devices behind one reference.** A record update in Roc touches every
  list in the record, so the width of the machine record was a cost on every
  statement. Moving the rarely written parts behind one reference made every
  statement about a quarter cheaper.

Roc still makes odd decisions about when to copy. The data structures bound
the damage, but they do not make the behaviour predictable.

**For the web REPL the performance is more than sufficient.** A statement
costs a few microseconds, and the page already sleeps a millisecond after
every PRINT on purpose. The cost shows in the longest NBS runs, and in
loading, where the standard's checks allocate heavily.

## What we stood on

The project leaned on resources other people put on the web:

- **The NBS Minimal BASIC test programs**, as compiled by John Gatewood Ham
  and published in [sehugg/nbs-ecma55-test](https://github.com/sehugg/nbs-ecma55-test),
  with the ECMA-55 standard itself.
- **David Ahl's *BASIC Computer Games***, the listings from
  [coding-horror/basic-computer-games](https://github.com/coding-horror/basic-computer-games).
- **[basic101](https://github.com/wconrad/basic101)**, a Ruby BASIC-80
  interpreter. Its test captures are the expected output for the games. It
  settled dozens of questions of dialect: how a number prints, what STOP
  says, and how RND draws from Ruby's Mersenne Twister.
- **The Mersenne Twister reference algorithm**, and **Elm's Array**, the
  shape of our persistent vector.

**The NBS suite served us well.** It grades itself and it is thorough, and
passing it means something. It leans toward statistical programs, though: its
longest runs sort arrays and test the distribution of random numbers. That is
not the kind of program we demo. The games and the screen are what the web
REPL is for, and there the captures from basic101 were the better judge.

## Where it could go

There is more here than we have time for. Deeper into this project: the last
44 games, the load checks' allocations, and whether the INPUT puzzle and the
other copying rules reduce to something worth reporting to the Roc
maintainers. Beside it: other languages from the same era, or BASIC's own
relatives, on the same machine shape. Or the same interpreter in another
functional language, to see whether the copying surprises are Roc's own or
come with the territory. Any of those would make a good side project, and
this one leaves a working interpreter, a test ladder and a set of hard-won
rules to start from.
