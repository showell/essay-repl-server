# Request edges, and the Zig quirks worth tooling

*2026-10-17. Two questions from today: what are the "eleven number parses
no request reaches", and which parts of Zig's syntax deserve Shale tooling
of their own.*

## Part 1: the request-edges check

### What it guards

angry-gopher has a test called **request edges** (in `router.zig`, from
metal-vmm QUEUE 183). It sends edge numbers, as a signed-in member, to
every place a request carries a number: in a path, a query, a form field,
a cookie. The numbers include `0`, `-1`, `2147483648`,
`18446744073709551616`, `"+5"`, `" 5"`, `"007"` and `""`. It asserts no
request panics and every answer is an answer. This is the class hunt for
the bug "a number from outside parsed into a type too small for it".

### How it stays complete

A test like that rots quietly: someone adds a new `parseInt` behind a
new route, and the test never sends it anything. So the test **refuses to
pass on a parse site it doesn't know**. It reads the source, its own and
zig-webbox's (a request reaches library code too), finds every
`parseInt(` outside a test, and requires each one, by file and function,
to be in a list called `edge_sites`. Each entry is one of:

- **covered**: one of the test's requests reaches it (for example
  `signed.zig`'s `verify`, which parses a cookie's timestamp);
- **unreachable, with why**: no request can carry a number to it, and the
  entry says why.

A site in neither fails the test with "cover it with a request, or say
why none reaches it".

### The eleven, and why they moved

Eleven of the "unreachable" entries named **webbox's** files. Each is a
number webbox parses from something a request never supplies:

| file | function | what it parses, and why no request reaches it |
|---|---|---|
| `script_route.zig` | `lastSequence` | a sequence file the server wrote |
| `shale_sign.zig` | `main`, `lastFor` | the signer, a program run on the box, not the server |
| `shale_fixture.zig` | `main` | the program Shale's `run` tests spawn |
| `shale_jobs.zig` | `parseRecord` | a job's record its reaper wrote, read by the Linux CLI |
| `log_view.zig` | `requestAt` | the host's own log lines |
| `bus.zig` | `keepaliveSetting` | the host's start-up setting, an environment variable |
| `counter.zig` | `current` | a counter file the server wrote |
| `linux_host.zig` | `portFrom` | the environment |
| `linux_fetch.zig` | `parseHead` | the answer to the application's own fetch |
| `site_secret.zig` | `previous` | a secret file the server wrote |

They lived in angry-gopher's list, so **each time webbox added one,
angry-gopher's test broke**, in a repo that no webbox change tested. It
happened three times this week: CC's job records, the test fixture, and the
fetch's response parser. Each time the fix was a line in the wrong repo.

So today they moved. `zig-webbox/src/edge_sites.zig` lists them with the
same reasons. Its own test fails if a listed function is no longer there,
and red on a planted wrong name. angry-gopher's scan now accepts a library
site that webbox names. A webbox change that adds such a parse now says so
in webbox, next to the code. The five webbox sites a request *does* reach
(`sse.zig`'s `resumeAt`, `signed.zig`'s `verify` and `issuedOf`,
`log_view.zig`'s `parseFilter`, `script_route.zig`'s `parse`) stay in
angry-gopher's list. Covering them with requests is the application's job,
because it is the application's routes that reach them.

This is the third time today that the same shape of bug turned up: a
check in one repo that knows another repo's files. The other two were the
library-shape lint and the portable partition.

## Part 2: Zig quirks worth tooling

These are the places where Zig's own syntax trips up text tools. They
aren't problems with Zig, but a regular expression can't see them. I
hit most of them today.

### 1. `.name` means three things

A leading dot is one of:
- a field access (`x.watch`);
- a declaration access (`linux_reads.watch`);
- an **inferred enum literal** (`.watch`, with nothing on the left).

They look alike to text matching. Today's word-mode rename turned
`race.concurrent(.watch, watch, …)` into `.linux_reads.watch`. The
token-aware rename in QUEUE 234 skips anything right after a dot. A
*field* rename is the inverse problem, and harder: it must touch `.name`
in every struct literal `.{ .name = x }` whose type is that struct, which
only the compiler knows.

### 2. Declaration positions take a plain name

`pub const name`, `fn name(`, a parameter `name: T`, a field `name: T`,
a capture `|name|` and a label `name:` all take a bare identifier.
Renaming a *use* to a qualified name (`linux_writes.held_most`) is right
at the call site and invalid at the declaration. My first move script
produced `pub const linux_writes.kept_write_deadline_ms`, and the
compiler would have rejected it. 234's rename stops on a declaration
position when the new name is qualified.

### 3. Test names are strings, and `test decl {}` is not

`test "at most streams_most streams are held" { … }` names a test with a
string, and prose in it mentions identifiers. A text rename reached two
test names today, which is how test identity changes. The other form,
`test streams_most { … }`, names a *declaration* and should follow it
when it's renamed. Tooling has to tell the two forms apart.

### 4. Multiline strings start every line with `\\`

```zig
const usage =
    \\usage: shale [--write] FILE
    \\  --budget NAME=N
;
```

Each line is a separate string-literal token. A tool that treats `\\` as
an escape, which Python did to me earlier this week, corrupts them
silently. A tokenizer sees them as strings; text tools don't.

### 5. A file is a struct, and visibility is per file

Every `.zig` file is a struct. A declaration is private to its file
unless it's `pub`, and so are a struct's methods (`Progress.Ended` needed
its own `pub` today). Moving code between files therefore raises one
question every time: **which names must become `pub`**? I answered it
with a script that searched the remaining file for each moved name. The
compiler knows exactly.

### 6. No shadowing, even across nesting

A nested declaration can't reuse an outer name:
`pub const for_tests = struct { pub const sleepMs = sleepMs; }` is an
error. I aliased the file (`const host_file = @This();`) to get around it.
A rename that introduces a name already in scope fails to compile, so a
rename tool should check the scope first.

### 7. Lazy analysis: what isn't referenced isn't compiled

Zig compiles only what's referenced. Two consequences showed up today:
- **A test file nothing imports never runs**, and the suite stays green.
  That was the hole in the linux_host split; `library_test` guards it
  now.
- **A moved function with a type error compiles fine** until something
  calls it. `std.testing.refAllDecls` in a test block forces the
  question.

### 8. Unused locals and parameters are errors

Deleting the last use of a local means also writing `_ = x;` or removing
the local. Code moves that drop a use trip this. The compiler names the
line, so this one needs no tooling, only an expectation.

### 9. `@"name"` and labels

`@"error"` is an identifier spelled as a string (the tokenizer tags it
`.identifier`). Labels (`blk: { … break :blk x; }`) use the identifier
grammar too. A rename of `blk` should touch the label pair and nothing
else.

### 10. Imports are string paths

`@import("linux_reads.zig")` is a string, so moving or renaming a file is
a string edit in every importer. Today's `library_test` already parses
imports; the same parse gives an import graph for a move.

## What tooling this argues for, in order

The common answer is **Zig's own front end**, which the Linux host can
call: `std.zig.Tokenizer` (queued, 234) and **`std.zig.Ast`, the parser
`zig fmt` uses**. In the Linux prelude, as host builtins:

1. **`zig_rename`** (QUEUE 234): token-aware; covers quirks 1, 2, 3, 4
   and 9.
2. **`zig_decls(path)`**: every top-level declaration with its exact span,
   doc comments included, its visibility and kind. Today I found blocks
   by matching their first comment with a regular expression, which works
   only while the comments stay as they are. With exact spans, "move these
   declarations" becomes a function call.
3. **`zig_move(from, to, names)`**, built on `zig_decls`: move the named
   declarations, report which names now need `pub` and which the moved
   code needs from where it was (today's `sleepMs` find). That covers
   quirk 5, and it is most of what this afternoon's scripts did by hand.
4. **An import graph** from the same parse: for quirk 10, and for
   `library_test`'s rules.

Items 2 to 4 are a bigger piece than 234, and worth doing only after 234
proves the pattern. They would make a large Zig refactor a short, legible
Shale script, with the compiler's view of the code rather than text
matching.

Quirks 6 to 8 are the compiler's job. The tooling there is to compile and
test after every step, which `same_tests.shale` already does.
