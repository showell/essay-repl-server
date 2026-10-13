# Small signed programs on the unikernel

*2026-10-13. A thinking piece on Steve's question: upload a small signed
program, and the server runs it at once, in its turn. Examples: delete a
topic, look around the file system. The language should be nicer than
bash, far simpler than Python or Zig, Lua-like in spirit, and able to run
on Linux too.*

## My recommendation in one paragraph

Build our own small language with Lua's surface syntax, written in Zig
inside zig-webbox. A run allocates from one arena that is thrown away when
the run ends. There is no garbage collector, there are no floats, and the
only effects are through the store. The most important design choice is
not the syntax, though: **a script describes, and the host acts.** The
script reads the store and returns a list of the changes it wants. The
host shows that list (a dry run) or applies it. Sign with Ed25519, with a
sequence number and the target host inside the signed bytes. Every part of
this runs the same on Linux and on metal, because it touches nothing but
the store interface both hosts already share.

## Why not real Lua

Lua is small for a language: about 30,000 lines of C. Embedding it on
metal means:
- building C into the kernel, with the pieces of libc it needs (malloc,
  `setjmp`/`longjmp` for errors, `printf`-style formatting, floating-point
  maths);
- a garbage collector;
- removing the `io`, `os` and `debug` libraries to sandbox it.

Every one of those is surface we would then have to trust.

What we'd actually want from Lua is its feel: `local`, `if … then … end`,
`for name in list do … end`, strings that are easy to work with. We don't
need metatables, coroutines, floats or a garbage collector. A subset that
looks like Lua gets the feel without the machinery.

There is another reason the Lua shape matters: **Claude will write most of
these scripts.** Models write Lua fluently, and an unfamiliar syntax is
where a model makes mistakes. Familiar syntax with fewer features is the
safest place for a model to write code that deletes things.

## The language, sketched

```lua
-- Delete a topic: every message file under it, then the folder.
local topic = "chat/rooms/general/topics/old-test"
for name in ls(topic) do
  if ends_with(name, ".msg") then
    remove(topic .. "/" .. name)
  end
end
remove_dir(topic)
print("removed " .. count(ls(topic)) .. " messages")
```

**Values:**
- integers (64-bit, checked: overflow stops the script);
- strings;
- booleans;
- lists;
- maps;
- `none`.

No floats, so nothing differs between hosts.

**Statements:**
- `local`;
- assignment;
- `if/elseif/else`;
- `for x in list`;
- `for i = a, b`;
- `while` (budgeted);
- small functions, no closures over changing state.

**Built-ins:**
- **paths:** `ls`, `exists`, `is_dir`, `read`, `size`;
- **strings:** `split`, `join`, `lines`, `starts_with`, `ends_with`,
  `contains`, `trim`, `fmt`;
- **lists:** `count`, `sort`, `keys`;
- **output:** `print`.

**Effects:** `write`, `append`, `remove`, `remove_dir`. Under the
describe-then-act rule, these record a change rather than make one
(below).

**Errors stop the script.** Fail, never warn. There is no `pcall`; a
script that wants to tolerate a missing file asks `exists` first.

**Size:** a lexer, a parser to a tree, and an interpreter that walks the
tree with a step counter. I'd guess 1,500 to 2,500 lines of Zig with its
tests, in zig-webbox next to the store.

## The arena is the big simplification

A run lives inside one request. So every value it makes is allocated from
one arena, and the arena is freed when the run ends. There is no garbage
collector, no reference counting, and no leak possible beyond the run. A
memory budget is just the arena's size: hitting it stops the script with
"out of memory at line N".

## Describe, then act

This is the part I'd argue for hardest. If a script's `remove` really
removed files, then a script stopped halfway (by its step budget, a bug, or
a missing file on line 40) leaves the site half-changed, and nobody knows
which half.

Instead, the script runs against the store **read-only**. Every effect it
calls is recorded as a *planned change*. When the script finishes:
- **Dry run** (the default): the answer is the script's printout plus the
  plan, e.g. "remove 37 files under chat/rooms/general/topics/old-test,
  remove 1 folder". Nothing changes.
- **Apply:** the same script, signed with apply set, runs again from the
  same state and produces the same plan. The host checks the plan, then
  applies it in order, each change through the store's own checks. The
  answer lists what was done.

Why this is worth the constraint:
- **A script never half-runs.** Any error, budget or bug happens before the
  first change.
- **The dry run is free and exact.** It is the same evaluation, minus the
  apply step. Steve or an agent reads the plan before signing the apply.
- **The plan is the audit record.** The log keeps the script's hash, its
  signer and the plan applied: what changed, not just what code ran.
- **Its limit is mild:** a script cannot read back what it wrote earlier in
  the same run. Admin tasks rarely need to; a task that does becomes two
  scripts.

This is the "pull the pure decision away from the I/O" doctrine, applied
to a language: evaluation is pure and the host owns every effect.

## Running inside the turn

The unikernel serves one request at a time, so a script holds the whole
site while it runs. Bounds keep that short:
- a **step budget** (say a few million interpreter steps: tens of
  milliseconds);
- a **read budget** (files and bytes read);
- a **plan budget** (changes per run).

A big job, such as deleting ten thousand files, is done as several runs,
each one a script that does "the next 500". That is idempotent, because
each run sees the state the last one left.

There is no clock and no randomness, apart from a `now` the host hands in.
So a script run on a copy of the site volume gives the same plan as on
prod.

## Signing

- **Ed25519, not a shared secret.** `std.crypto` has it. The server holds
  only the public key, so even someone who reads the whole disk image
  cannot forge a script. The private key stays on the box or with Steve.
- **What is signed:**
  - the script's bytes;
  - dry-run or apply;
  - the **target** (`lynrummy.com`, or a test host), so a script signed for
    a test volume can't be replayed on prod;
  - a **sequence number** the server keeps on disk and requires to rise;
  - an **expiry**.

  Without the sequence number, anyone who saw a signed "delete topic X" on
  the wire could replay it later.
- **Two locks:** the endpoint also requires today's admin bearer key. A
  leaked signing key alone isn't enough, and neither is a leaked bearer key.
- **A tool on the box** signs a script: `sign.py script.lua --apply
  --target lynrummy.com`.

## Linux and metal

The interpreter needs only the store interface (`read`, `list`, `write`,
`replace`, `remove`), which zig-webbox already gives both hosts. So:
- angry-gopher on Linux runs the same scripts, and that's where they get
  developed and tested;
- **a script can be dry-run against a copy of prod's site volume on the
  box** before anyone signs it for prod;
- metal-vmm and the judges can include a script run in their stories, so
  the interpreter gets the same fault testing as everything else (a disk
  that fails mid-apply, for one).

## What to decide first

1. **The first three scripts.** "Abstraction earns its keep on the second
   user." Deleting a topic is one. What are the other two? If they are all
   "delete X" and "list X", a few signed admin commands would do the job
   with no language at all, and the language could wait until the list
   grows.
2. **Is describe-then-act acceptable?** That is, reads see only the state
   from before the run. I think yes for admin work.
3. **Lua-shaped or not?** I'd keep Lua's look (familiar to Steve and to
   models), with our own semantics where they're simpler, especially
   integers only and no nil surprises.
4. **Where the endpoint lives:** a route in zig-webbox, which both apps
   get, or in angry-gopher alone. I'd put the interpreter in zig-webbox and
   the route in each app that wants it, so Dog Park can have one too.

## Rough size of the work

- **The interpreter:** language, arena, budgets and plan, with thorough
  tests on Linux. About a long CC chunk: it needs no emulator, and it is
  exactly the kind of adversarial, pure work CC does well.
- **The endpoint:** signature, sequence number, dry run and apply,
  logging. The box's work, since it touches the host and the store.
- **The signing tool, plus a "dry-run on a copy of prod" recipe** on the
  box.
- **Judges and metal-vmm stories:** a script run with a fault mid-apply.
