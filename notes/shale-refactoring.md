# Refactoring Zig with Shale: what the tools found, and what the code was hiding

*Written 2026-10-19, after two days of cleanup across angry-gopher, the
kernel, zig-webbox and metal-vmm. Every analysis and every edit went
through Shale. This is an essay, not a report: some of it is settled, and
some is a question I don't know the answer to yet.*

## The suite, as it ended up

Nobody designed the suite. It grew a recipe at a time, each written when
a job needed it, and only afterwards did it turn out to have a shape. There are
three kinds of tool, and the split between them turned out to be the most
useful idea of the lot.

**Finders** read a tree and make lists. They never decide anything.

- `seams` and `file_map` show a file's structure. `long_zig` lists the
  files over a thousand lines.
- `smells` covers long functions, long parameter lists, `bool` parameters,
  swallowed errors, and numbered steps in comments.
- `bool_calls` finds the calls that pass a bare `true` or `false`.
- `param_runs` (new yesterday) finds the same run of parameter names in
  several functions.
- `clones` finds the same code in two places.
- `dead` finds declarations nothing uses.

**Movers** change code, and refuse whatever they can't change whole:

- `zig_split` moves declarations into a new file.
- `call_args` rewrites every call of a function by a template.
- The `zig_renames` builtin qualifies names over a range of lines, using
  Zig's own tokenizer.
- `pub_loop` and `zig_tidy` are smaller.

All of them run under `--undo-on-stop`, so a stop leaves the tree as it
was.

**Judges** say whether a change did what it claimed:

- `move_judge` compares symbols and test names before and after a move.
- `const_judge` compares a constant's bytes against a git revision.
- `same_tests` checks that the same tests still run, wherever they moved.
- `flip_bools` (new yesterday) judges the test suite rather than the code.

The finders work from tokens, not types. That sounds like a weakness, and
it's mostly a strength. A recipe doesn't need to understand Zig's
semantics if the compiler judges right afterwards, so the work divides
cleanly. Shale proposes and moves, Zig type-checks, the tests judge
behavior. Each one catches what the others can't.

## What the long programs were hiding

### The struct was usually already there

I expected long parameter lists to need new types. Mostly they didn't.
Again and again, the right type was already defined a few lines away, and
the signature just didn't use it:

- `reading_list.save` took `conv, sid, id` loose. The same file defines
  `Ref{conv, sid, id}`, and the reading list's own parser returns one.
- `chat_sse.emitWire` took the six fields of `BusMsg`, the struct declared
  right above it. Its live caller had a `BusMsg` in hand, and took it apart
  to make the call.
- `scsi.FakeDriver.rw` took `writing: bool` and turned it straight into a
  `Dir` enum the file already had.
- recent.zig threaded `dm: bool` through two functions, while
  `chat_store.ConvKind{dm, channel}` existed and was imported.

I think this is how code grows. A function is written first and its
arguments are whatever the caller has. Later someone names the concept,
for the parser or the wire, and the older signatures never catch up.
The type exists; it just never reached the functions already passing its
pieces. A long parameter list isn't really a missing abstraction. It's a
seam nobody went back to stitch.

That's why `param_runs` turned out to be a better finder than `smells`.
"This function takes nine parameters" is only a question. "These three
parameters appear, in this order, in 21 functions" means the struct
already has users. As the doctrine puts it, an abstraction earns its keep
on the second user.

### Most bools were modes

`bool_calls` lists the calls that pass a bare `true` or `false`, and each
one tends to tell a story. `plan(apply: bool)` was really a dry run against
a real run. `admit(new_session: bool)` meant "this write makes a session".
`walk(root: bool)` was a failure policy: at a root a failure fails the
backup, and inside one it's a named skip. In every case the bool stood for
a choice with two names, and the names only lived in the comments.

`bool_calls` also turned up a few that should stay bools. The DHCP and
drain code has `upload` and `charged` flags that look like one fact stored
twice. One constructor sets them independently, so they're two facts. The
finder asked; reading the code answered. I came to trust that division of
labor more than any heuristic.

### The tests were thick where the code was, and thin where code met code

This was the real discovery, and it came sideways. After every signature
change I planted a swapped or flipped argument at the production caller,
expecting the tests to fail, so I'd know the refactor had a judge. Over
and over they passed:

| The flip that passed every test | What it would have meant |
|---|---|
| a message's author name and uid swapped | the wrong person credited |
| DHCP's source and destination ports swapped | a machine that never gets an address |
| a saved message's `sid` and `id` swapped | a reading list that links nowhere |
| the retire screen's preview and confirm swapped | **a preview that deletes** |
| Recent's DM and channel swapped | "(DM)" on the wrong rows |
| pin and unpin swapped | pinning unpins |
| a backup root walked as "inside" | a failed backup that looks whole |

These aren't badly tested programs. angry-gopher has about 2,760 unit
tests, and the functions behind every row above are tested. What wasn't
tested was the wiring: the one line where a route hands its arguments to
the function. Unit tests cluster around functions because that's where
it's easy to write them. The decisions that slip through sit at the joins,
in lines that look too simple to test.

`flip_bools` automates the plant. It flips each bare `true`/`false` passed
at a call outside the tests, one at a time, and runs the suite. On
angry-gopher 17 of 24 flips survived:

- 8 were real gaps, now held by 4 tests;
- 4 were checked by the separate markdown corpus;
- 2 were in a benchmark binary the tests never build;
- 3 changed nothing that mattered.

That's a noisy list, but every real gap was a real one, and the noise took
minutes to sort.

It's mutation testing narrowed to one mutation. I picked that mutation
because a bool literal at a call is a decision the code makes in plain
sight, and the cheapest one to flip. A wider version, which swapped any
two arguments of the same type, would have found the author, port and
location swaps by itself. I did those by hand.

### Lazy analysis hides dead weight

Zig only analyzes what's reachable, so it never complains about an unused
private function or import. `dead` found 120 unused imports across five
repos, and one dead function. None of it was harmful. All of it was
reading cost. The recipe also taught me that removing a declaration
leaves blank lines behind, which zig fmt then refused at the gate. A small
thing, but every mover has to leave the file in the state the formatter
expects.

### Workhorse functions are fine; their seams are what matter

The longest functions are routers and dispatchers: `routed`, `handle`,
`kmain`, `serveOne`. I left them long. The improvements were around them:

- `serveOne` took eleven parameters, eight of them the parts of one
  connection, so they became one `Wire` value.
- The request body's state became `Body`, and three scattered `defer`s
  became one `deinit`. I planted each `deinit` step out in turn; each
  failed a test.

That fits Steve's workhorse pattern: one long function doing dispatch is
honest, and the cleanup belongs in what it hands around.

### Repetition is sometimes an interface

The first run of `param_runs` was full of noise:

- zig-webbox's `drain(w, data, splat)`, in five files;
- metal-vmm's snapshot functions, all named `f`;
- vtable `read` and `write` methods.

These share a shape because an interface demands it, and they aren't
structs waiting to be named. Counting distinct function names instead of
functions removed almost all of it.

## What Shale learned about itself

Using Shale on real code found Shale's bugs faster than its own tests did:

- **The walk through a mount:** `glob("repos:...")` stopped on its first
  file, because `walk` built each entry's path from the working directory
  instead of the mount. Every earlier glob had happened to run from inside
  the repo it read.
- **job_start:** a missing log folder came back as "the reaper ended
  without writing a record", which is true and useless. It now names the
  folder.

There were lessons in how to use it, too:

- **A reinvented tool:** I hand-wrote a whole-name replacement inside one
  function, then found that the `zig_renames` builtin already does it with
  a line range, and does it better: it uses tokens, skips comments and
  strings, and stops at a declaration. The cookbook README now points
  there. A recipe library is only as good as the index you read before
  writing.
- **Order of work:** `call_args` refuses the whole job if any call has the
  wrong argument count. I edited a function's body (including its own
  recursive call) before running it on the other call sites, and it
  refused, correctly. Rewrite calls first, then edit bodies.
- **Budgets are part of a recipe's contract:** `smells` ran out of memory
  on a 70-file repo. Its header now says what a large tree needs, as
  `move_judge`'s already did.

What didn't happen is worth saying too. Quoting never got in the way
after `--args-stdin` existed. Partial edits never survived a stop after
`--undo-on-stop` existed. Sorting by several keys made every finder's
report one line. The language stayed small, and the recipes stayed short
enough to read before running them.

## Open questions

**When is a refactor churn?** `(conv_dir, sid)` appears in 21 functions.
`param_runs` says it's a struct with users. Steve and I left it, because
swapping two paths fails loudly in the tests, and the change would touch
every chat file for readability alone. So "a struct with users" is
necessary but not sufficient; the other half is what a mistake costs and
whether anything would catch it. Could a finder know that? Perhaps by
running the flip itself: swap the pair at one call and see if the tests
notice. If they do, the struct is optional. If they don't, it's a test
first and then maybe a struct.

**Should the judges of the tests become routine?** Every planted flip took
a test run, and `flip_bools` costs half a minute a flip. That's fine as a
hunt and wrong as a gate. But each gap it found was in code that had been
"green" for weeks. Maybe the right rhythm is a hunt after each refactor,
on just the files it touched. That's cheap, and it targets exactly the
call sites that just changed.

**How far should token-level analysis go?** Every finder here reads
tokens. A real type-aware query ("every call passing two values of the
same type side by side") needs Zig's semantic analysis, which Shale
doesn't have, and building it would be a large project. So far tokens plus
the compiler have been enough. My guess is they'll keep being enough for
finding. Moving is where types would help: a mover that knew types could
refuse a swap the tokens can't see.

**Does any of this carry to Roc?** CC's Dog Park Roc has the same smells
in a different form: critter kinds as `U8` codes where a tag union exists,
just as angry-gopher had `dm: bool` where `ConvKind` existed. The finders
would need a Roc tokenizer. The judge idea (plant at the caller, see if
the tests notice) carries over as is, and Roc's `expect`s would make a
fast judge.

**Is the cookbook the right shape?** Eighteen recipes, each a file you
read, copy and change. That suited a niche language and one heavy user.
If a second agent uses it, the README becomes the interface, and its
first paragraph should probably be the find / move / judge split, since
that's what tells you which recipe you want.

## A closing thought

These programs were written carefully, reviewed, and tested heavily. Still,
in two days the tools found the same thing in every repo: a type, enum or
test that didn't reach the place it was needed. `Ref` and `BusMsg` existed
but weren't in the signatures. `ConvKind` existed but wasn't passed. The
tests existed but not at the call. None of it was wrong code. It was
knowledge the code had already earned, not yet carried to the line where
it would matter.

That might be the best use for a tool like Shale. Not finding bugs, but
finding where the code already knows better than it says.
