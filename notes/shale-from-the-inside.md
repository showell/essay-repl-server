# Shale from the inside

*2026-10-17. The first afternoon under the ban: what I wrote in Shale, and
what it felt like. The pain points are meant to steer what we do next.*

## What happened

The gate went in at about 19:40 UTC. Since then every top-level command I
ran was a `shale` launch. In that time I:

- found every `.zig` file over 1,000 lines across seven repos;
- mapped `linux_host.zig` and measured which of its names cross each seam;
- split `linux_host.zig` from 2,963 lines into five files (the host is now
  885 lines), in four commits;
- built and ran the test suite, the formatter and `zig build consumers`
  through `run`;
- did every commit and push through the git prelude.

**The escape hatch was used zero times.** `~/.local/state/shale/wants.tsv`
is empty. Everything I needed, Shale could do. The question is how pleasant
it was.

## The code

### The long files, across the repos

This is the cookbook's own recipe with a loop over repos. It ran first try.

```shale
local repos = {"zig-metal-unikernel", "zig-webbox", "metal-vmm", "dog-park",
               "observatory", "angry-gopher", "zig-coverage-sdk"}
local rows = {}
local files = 0
for r in repos do
  for p in glob(r .. "/**/*.zig") do
    files = files + 1
    local n = count_lines(p)
    if n > arg("over", 1000) then push(rows, {lines = n, path = p}) end
  end
end
sort(rows, "lines", "desc")
print(table(rows, {"lines", "path"}))
print(#rows .. " of " .. files .. " .zig files are over " .. arg("over", 1000) .. " lines")
```

It reported 26 of 442. `glob` skipping `.zig-cache` on its own is the kind
of default that saves a careless agent from a wrong answer.

### The safety net: the same tests, by name

This script made the refactor safe. It runs the suite with the timing
runner, then compares every test's name against a baseline taken before the
first move. The module part of a name is left out, because a moved test's
module changes. It fails on any test missing, any test new, or any failure.

```shale
function short(name)
  local m = re_find(name, "\\.test\\.(.*)$")
  if m == nil then return name end
  return m.group
end

function names_of(text)
  local got = {}
  for l in lines(text) do
    local m = re_find(l, "^ *[0-9]+\\.[0-9]+ s  (.*)$")
    if m ~= nil and re_find(m.group, "^total, ") == nil then push(got, short(m.group)) end
  end
  sort(got)
  return got
end

local r = run({"zig", "build", "test", "-Dtest-timing"}, {timeout_ms = 110000, whole = 4000000})
if r.code ~= 0 then
  for l in last(lines(r.out), 40) do print(l) end
  fail("zig build test exited " .. r.code)
end
local now = names_of(r.out)
local was = {}
for n in lines(read("zig-out/refactor-baseline.txt")) do if n ~= "" then push(was, short(n)) end end
sort(was)

local seen = {}
for n in now do
  if has_key(seen, n) then seen[n] = seen[n] + 1 else seen[n] = 1 end
end
local missing = 0
for n in was do
  if not has_key(seen, n) or seen[n] == 0 then print("missing: " .. n) missing = missing + 1 else seen[n] = seen[n] - 1 end
end
local extra = 0
for n in keys(seen) do
  if seen[n] > 0 then print("new: " .. n) extra = extra + seen[n] end
end
if missing > 0 or extra > 0 then fail(missing .. " missing, " .. extra .. " new, of " .. #was) end
print("same tests: " .. #now .. " of " .. #was .. ", all passing")
```

It earned its keep. Each move ended with `same tests: 473 of 473, all
passing`. Once it reported a rename that had reached a test's name. At the
end it reported exactly one new test: the `test { _ = @import(...) }` block
that now pulls in the moved tests.

### A move, and the plant that proves the check

Each move was a script: find the block by the comments it starts and ends
at, write it to the new file, and rename the host's uses with `edit`'s word
mode. The third move picked declarations from four ranges and worked out by
itself which names had to become `pub`:

```shale
-- Which of the moved names the host still uses (a test's name aside).
local used = {}
for name in declared do
  local hit = false
  for l in kept do
    if not hit and find(l, name) ~= nil and re_find(l, "^test \"") == nil
       and re_find(l, "\\b" .. name .. "\\b") ~= nil then hit = true end
  end
  if hit then push(used, name) end
end
```

Each move then planted its failure and committed in the same script:

```shale
edit("src/webbox_linux.zig", "    _ = linux_streams;\n", "")
local r = run({"zig", "build", "test", "-Dtest-filter=library:"}, {timeout_ms = 110000, whole = 400000})
edit("src/webbox_linux.zig", "    _ = linux_writes;\n", "    _ = linux_writes;\n    _ = linux_streams;\n")
if r.code == 0 or find(r.out, "webbox_linux.zig names linux_streams but its test block does not") == nil then
  fail("the plant was not caught: exit " .. r.code)
end
print("plant caught; restored")
local head = git_commit("", [=[linux_streams.zig: the streams held at once, out of linux_host.zig (51 lines)
...]=], {add = {"src/linux_streams.zig", "src/linux_host.zig", "src/webbox_linux.zig"}})
```

The plant script, the restore and the commit sit in one file, and the
commit message is a long string with no escaping at all. That last part is
232's `[=[ … ]=]` doing exactly what it was for.

One plant found a real hole. With the host's single
`test { _ = @import("linux_host_test.zig"); }` removed, `zig build test`
**passed and ran none of the 1,500 lines of tests**. `library_test` now
requires every `*_test.zig` to be imported by some file, and it went red on
that plant.

## Where it hurt

In order of how much each cost me, in time and in tokens.

### 1. Every `edit` prints its diff, and I can't filter it

The gate refuses pipes and redirects, by design. But Shale's own output is
then all I get, and `edit` prints a full diff for every call. The reads
move did 22 word-mode renames, and its output was about 300 lines of diff,
all of which landed in my context. A refactor is exactly the case where I
want "22 renames, 94 lines changed" and nothing more unless I ask. The
budget design argues the same way: output is a cost, so a call shouldn't
spend it unasked.

**Want:** `edit(..., {quiet = true})`, or a run-level `--quiet-effects`,
with the diff behind `--verbose` as the dry run's list is.

### 2. A word rename doesn't know Zig

`edit(p, name, new, {all = true, word = true})` matches a word anywhere.
In this refactor it reached:
- the enum literal `.watch` in `race.concurrent(.watch, …)`, which became
  `.linux_reads.watch`;
- the verb "asks" in three comments (I had a variable named `asks`);
- two test names, which are strings.

Each was caught (by the compiler, by reading the diff, or by the
same-tests check), and each cost a round trip. Renaming an identifier is
the commonest refactor there is, and doing it with text matching is the
`sed` problem all over again.

**Want:** a rename that sees tokens: identifiers only, never inside a
string or a comment, never after a `.`. It could be a Zig builtin in the
Linux prelude (Zig tokenizes Zig in its standard library: `std.zig.Tokenizer`),
`zig_rename(path, from, to)`. This is Shale-shaped and worth a QUEUE item:
it would have saved half of this afternoon's corrections.

### 3. A dry run can't preview a script whose later calls depend on earlier ones

My first move script did `replace(host, …)`, then `edit(host, …)` for the
renames. The dry run didn't make the `replace`, so the `edit`s ran against
the old file and previewed renames inside the very block being moved,
including `pub const linux_writes.kept_write_deadline_ms`. The real run was
right. But the dry run is the safety step, and here it misled me.

**Want:** a dry run that keeps its own changes in an overlay, so a later
read sees them. That's the honest version of the CLI's default mode.

### 4. Small vocabulary gaps, each one a stop and a retry

None of these is a bug: each stop was clear and named the problem. Each
still cost a launch:

- **no `drop`**: a slice of a list is `last(take(l, j), j - i)`;
- **`whole` takes a byte cap**, not a boolean;
- **`take` refuses a string**; the string version is `sub`;
- **a missing map key is a stop**, not nil (`has_key` asks first). I like
  it, but I wrote `(seen[n] or 0)` from habit;
- **no `write`**: it's `replace`;
- **one capture group, no `(?:`**. My pattern
  `^(?:pub )?(?:fn|const|var) ` had to become
  `^(pub fn|pub const|pub var|fn|const|var) `;
- **`grep` is plain text.** I wrote `grep(p, "edit%(")` (a Lua habit) and
  got no matches with no complaint, which looks exactly like "there are
  none". That's the one I'd fix: a pattern character in a plain-text
  `grep` could warn, or there could be `grep_re`.

These belong in SHALE-AGENTS.md's "where Shale is worse", or get small
fixes. `drop` (or `slice`) and the `grep` confusion are the two I'd do.

### 5. The root, and files outside it

Shale's paths are relative to its root. I couldn't `grep` zig's own
`std/Io/Dir.zig` without a mount, so I used the Read tool. My scratch
scripts live outside every repo, so Shale's `edit` couldn't touch them and
I fixed them with the Edit tool. Neither was a ban violation, but both
were seams. **Want:** a default mount for the zig install (read-only),
and the CLI letting a script's own folder be readable.

### 6. Step budgets on Shale loops

A regex per line, per name, over 2,900 lines blew through 50 million steps.
I rewrote it to filter with `find` first (cheap) and run the regex only on
lines that matched. That's the right lesson ("loop in builtins, not in
Shale"), and the stop said exactly which budget ran out. It still means
a straightforward script needs a performance thought earlier than Python
would.

## What was good

- **`run` plus `must`** made the build and test loop feel native. The
  runner's refusal of `-e` and the gate's refusal of pipes pushed me into
  writing real script files. Those files are now reusable (`same_tests.shale`
  ran eight times).
- **`edit`'s list form and long strings** made multi-line Zig edits
  exact. A failed match is a stop, never a silent no-op.
- **The git prelude** removed the commit-message quoting problem entirely.
- **Every stop was a single, accurate line.** I never had to guess what
  went wrong.
- **The default dry run** meant I never wrote by accident.

## On coupling

You said our refactors are riskier because the repos are coupled. This one
showed exactly how. The four moves were invisible to every application:
`linux_host` exports the same two names it did. Still, the last step broke
angry-gopher, which kept a hand list naming one of webbox's test helpers
by file (`linux_host.zig`'s `countAnswers`) in its request-edges check.
`zig build consumers` caught it before the push. That step is three hours
old.

The pattern from this morning's essay holds: the coupling that bites is
never the API. It's a check in one repo that knows another repo's file
layout. Two of today's three such checks are now fixed at the root (the
partition pin, and the request-edges scan, which skips test files now).
The third kind, `edge_sites` naming webbox's non-test parse sites by file
and function, is still a hand list across a repo boundary. I'd move webbox's
parse sites into a list webbox owns, checked by webbox, so angry-gopher
lists only its own.

## Next steps, by value

1. **A quiet `edit`** (or quiet effects): the biggest cost, and small.
2. **A token-aware rename for Zig**, as a Linux-prelude builtin.
3. **A dry run that overlays its own changes.**
4. **`drop`/`slice`, and a plain-text `grep` that warns on a pattern
   character.**
5. **Default mounts:** the zig install read-only, and the script's own
   folder.
6. **webbox owns its request-reachable parse sites**, so angry-gopher's
   `edge_sites` stops naming webbox files.

Items 1–5 are CC-sized Shale work, one queue item. Item 6 is mine.
