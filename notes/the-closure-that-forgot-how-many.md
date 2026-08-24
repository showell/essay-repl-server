# The closure that forgot how many

*2026-08-24*

We went looking for why one small program crashed. We found a defect that
can make a correct program return a wrong number, and whether it does
depends on code somewhere else that never runs.

Here is the whole thing in plain terms.

## A function waiting for the rest of its arguments

`add3` takes three numbers and adds them.

    add3 : Integer, Integer, Integer -> Integer
    add3 (x) (y) (z) = x + y + z

You can hand it just one and hold onto the result:

    add3 5

That is not a number yet. It is a function still waiting for two more.
The compiler builds a small object on the heap to represent it, with two
parts:

- a **stub**: a few instructions
- the **arguments collected so far**: here, just `5`

When the missing arguments finally show up, the stub puts `5` back in
front of them and jumps to the real `add3`.

## The convention nobody wrote down

The stub is built on an assumption: **every remaining argument arrives at
once.** `add3 5` is waiting for exactly two more, and the stub is
hardcoded to slide two arguments over and drop `5` into the gap.

The object does not record that it wants two. There is no count stored
anywhere in it. The stub simply assumes the caller knows.

That assumption is fine as long as every caller obeys it. Three places in
the compiler call one of these objects. Two of them hand over all the
remaining arguments in one go. **The third hands them over one at a
time.**

## What one-at-a-time does

That third path passes `20`, takes whatever comes back, treats it as a
new object still waiting for arguments, and passes `22` to that.

But `add3 5` handed only `20` does not come back with a new object. Its
stub does what it was built to do: it assumes both arguments are present,
slides them over, drops `5` in front, and jumps straight into `add3`.
`add3` adds three things — `5`, `20`, and **whatever was left in the
register the third argument should have been in.**

So it returns a number. Some number. Then the compiler takes that number,
treats it as the address of the next object, and follows it.

Everything after that depends on what the leftover junk happened to be.

## Three outcomes from one expression

Three things can happen, and we measured all three from the same source
expression:

**The junk happens to be right.** If the register still held `22` from
something earlier, `add3` computes `5 + 20 + 22 = 47`. The correct
answer, by luck.

**The junk makes a plausible address.** The number gets followed, garbage
comes back, and the program prints something like `6291544`. That is not
a number the program computed. It is a memory address, printed where an
answer belongs. **No crash. No warning. Just a wrong number.**

**The junk makes an impossible address.** In one case the intermediate
number was `45`. The program followed address 45, which lands in ancient
BIOS memory near the bottom of RAM, read what was there, and jumped to
it. Crash, with a register dump and no diagnostic.

## The part that should worry you

The same expression, in the same file, gives different answers depending
on what else is nearby.

| what is in the file | `((make-adder 5) 20) 22` |
|---|---|
| just that one line | **47** |
| one more line after it | **47** |
| two more lines after it | **crashes, printing nothing** |

A line added *after* an expression changes what that expression does. In
another test, adding a function that is **defined and never called**
turned a correct `47` into a heap address.

None of this is exotic code. It is a function that returns a function —
ordinary in any language that has them.

## Why the tests never saw it

The compiler has a test for partial application. It uses the two callers
that obey the convention. The one that breaks it has no test anywhere in
the tree.

That is the honest reason this survived: not that the case is rare, but
that the fixture happened to be written in the shape that works.

## What is actually wrong

The object has no arity — no record of how many arguments it still wants.
Because it cannot say, no caller can ask, and one caller guesses wrong.

You could patch the one bad caller and the crashes would stop. But the
real gap is the missing number. As long as the object cannot state what
it needs, correctness depends on every call site independently
remembering an unwritten rule, and one of them already forgot.

## What we know and what we do not

**Measured, on real hardware, twenty programs:** the three outcomes, the
instability table, and that a never-called definition can change a
working one. Also that this only touches functions returning functions —
`add3` itself, which returns a plain number, is correct everywhere it
appears.

**Read from the compiler's source, not measured:** the stub's convention,
the three calling paths, and which one breaks. The citations are specific
and checkable, but we did not instrument the compiler to watch it happen.

**Not established:** we cannot yet fully account for why one particular
correct result is correct. The leftover-register story explains it, and
fits every dump we have, but "it worked by luck" is a claim we have
inferred rather than proven.

That distinction matters more than finishing the story. A maintainer
needs to know which sentences to trust.
