# Shale programs, read whole

*2026-10-18. Two of the longer programs the box wrote in Shale today,
whole, as they ran; one small builtin of Shale's own, in Zig; and where
Shale could go next with a few more hours.*

Today the box split two large Zig files with Shale: metal-vmm's
`src/main.zig` (1,809 lines to 681) and the kernel's `probe/gopher.zig`
(2,653 to 1,731). Both splits were found and done by the two programs
below. Neither is clever. What they show is the shape Shale code takes
when it's doing real work: read something precisely, decide, act through
a few large builtins, and say what it did.

## A builtin, from the Zig side

First the bottom layer, because it explains what the programs above it
can lean on. This is `strip_suffix`, one of core Shale's 68 builtins
(the preludes and the Linux host add more), whole:

```zig
/// **`strip_suffix(s, t)`**: `s` without `t` at its end, or `s` as it is.
fn stripSuffix(run: *Run, pos: ast.Pos, args: []const Value) Error!Value {
    const str = try bi.stringArg(run, pos, .strip_suffix, args[0], "its first argument");
    const t = try bi.stringArg(run, pos, .strip_suffix, args[1], "its suffix");
    try run.charge(pos, t.len);
    run.tally(t.len);
    return .{ .string = if (std.mem.endsWith(u8, str, t)) str[0 .. str.len - t.len] else str };
}

```

That's the whole implementation. Four other places name it:

- **its name**, one line in `ast.zig`'s `Builtin` enum (`strip_suffix,`),
  so the parser knows it;
- **its arity**, `spec(.strip_suffix, 2, 2, stripSuffix)` in the topic's
  table: the interpreter refuses a call with the wrong number of
  arguments before the function runs;
- **its cost**, a line in `charge_test.zig`'s table. That table must name
  every builtin, checked at compile time, so none can skip having its
  charge tested;
- **its docs**, a row in SHALE.md's table, which people read. Nothing
  checks the table itself, but every code block in SHALE.md runs as a
  test.

Every builtin has the same few habits:
- **Arguments are checked by type through one helper** (`stringArg`),
  which writes the error message, so `strip_suffix(1, "x")` stops with "its
  first argument is an integer, not a string".
- **It charges for its work before doing it** (`run.charge`: a step a
  byte looked at). That's what makes every run bounded, and what made
  today's "the step budget ran out" stops honest.
- **It returns a slice of its input, not a copy**, when it can.
- It compiles the same on Linux and on metal.

The host builtins (`run`, `zig_decls`, `zig_move`, and so on) follow the
same pattern at a larger scale, in the Linux host behind `host(...)`.

## Program 1: `seams.shale`, where a file divides (235 lines)

**What it does.** It asks `zig_decls` for the file's top-level
declarations, each with `uses`, the top-level names it uses. With
`container=`, it asks for a struct's members instead, and counts what
each member reaches through a `.` (`self.slots`) as a use. Then it reads
the graph three ways:

1. **The hubs.** Some declarations are used by much of the file (a shared
   type: `Machine`, `Point`). Others use much of it (an orchestrator:
   `main`, `kmain`, `serve`). Both kinds glue everything to everything,
   so they're set aside.
2. **The cut profile in file order.** For each gap between consecutive
   declarations, it counts the references that cross it. A gap with few
   crossings and real code on both sides is a seam in the file's order.
   On metal-vmm's main.zig this found several clean gaps but said little,
   because the remaining helpers barely referenced each other.
3. **Who reaches it.** Each remaining declaration is grouped by the set
   of hubs whose uses reach it, through other non-hubs. This view is
   what found both splits. In main.zig it said: 28 declarations only
   `main` reaches, which all turned out to be the guest's boot; 10 only
   `serve` reaches, the run loop; the port constants only `Machine`
   reaches. In gopher.zig it found the configuration (only `readConfig`
   reaches it), the disks (a cluster inside the `kmain`-only group), the
   host facts, and the streams' turn.

**How to read it.** Most of the script is bookkeeping: maps of names to
counts, lists pushed and joined. The parts that carry the idea are
`used_by` and `uses_n` (fan-in and fan-out), `edges` (the graph without
the hubs), and the `reached` loop at the end, a depth-first walk from
each hub through declarations that aren't hubs. Some habits worth
noticing:
- Shale has no closures, so `find` and `union` are top-level functions.
- A missing key is a stop, so `get(m, k, 0)` appears wherever a count
  might be absent.
- Shale's `sort` takes no comparator, so the largest-first loop picks
  the maximum by hand.

```lua
-- **WHERE A ZIG FILE DIVIDES**: its top-level declarations as a graph
-- (zig_decls' `uses`), the hubs (what most of the file uses) set aside,
-- and the groups that are left, connected only through the hubs: each a
-- candidate seam, with its size, the hubs it needs, what outside it uses
-- it (each would need `pub`), and the tests that touch only it.
--
--   shale ~/shale-scripts/seams.shale path=src/x.zig [container=Name] [hub=N] [show=N]
--
-- `container=Name`: that container's members, not the file's, with what
-- each reaches through a `.` (`self.slots`) counted as a use.
--
-- `hub` is how many declarations must use a name for it to be a hub
-- (default: a fifth of the file's, at least 3).

const P = arg("path", "")
const SHOW = parse_int(arg("show", "10"))
const C = arg("container", "")
-- How many members each group lists (`names=N`).
const NAMES_SHOWN = parse_int(arg("names", "12"))

function lines_of(d)
  return d.last - d.first + 1
end

function find(parent, x)
  local r = x
  while parent[r] ~= r do r = parent[r] end
  return r
end

function union(parent, a, b)
  local ra = find(parent, a)
  local rb = find(parent, b)
  if ra ~= rb then parent[ra] = rb end
  return nil
end

function member(l, x)
  for y in l do
    if y == x then return true end
  end
  return false
end

if P == "" then fail("seams: give path=src/x.zig") end
local decls = nil
if C == "" then
  decls = zig_decls(P)
else
  decls = zig_decls(P, {container = C})
  -- A member's edges: the names it uses and the members it reaches.
  for d in decls do
    for r in d.reaches do
      if not member(d.uses, r) then push(d.uses, r) end
    end
  end
end
local imported = {}
for i in zig_imports(P) do
  if i.name ~= "" then imported[i.name] = true end
end
-- A const that only renames another (`const Io = std.Io;`) is an import too.
local prod = {}
local tests = {}
local by_name = {}
local total = 0
for d in decls do
  total = total + lines_of(d)
  if d.kind == "test" then
    push(tests, d)
  elseif d.name ~= "" and not has_key(imported, d.name) then
    local text = read(P, d.start, d.stop - d.start)
    local alias = re_find(text, "^(pub )?const [A-Za-z_][A-Za-z0-9_]* = [A-Za-z_][A-Za-z0-9_.]*;$") ~= nil
    if alias and lines_of(d) == 1 and #d.uses <= 1 then
      imported[d.name] = true
    else
      push(prod, d)
      by_name[d.name] = d
    end
  end
end

-- How many production declarations use each name (its fan-in), and how
-- many it uses (its fan-out).
local used_by = {}
local uses_n = {}
for d in prod do
  local n = 0
  for u in d.uses do
    if has_key(by_name, u) then
      used_by[u] = get(used_by, u, 0) + 1
      n = n + 1
    end
  end
  uses_n[d.name] = n
end
-- **TWO KINDS OF HUB**: what much of the file uses (a shared type or
-- helper), and what uses much of the file (an orchestrator: `main`,
-- `serve`). Either glues everything to everything; set aside, what is left
-- shows its parts.
local in_at = parse_int(arg("hub", tostring(max(4, #prod // 8))))
local out_at = parse_int(arg("out", tostring(max(6, #prod // 6))))
local hubs = {}
local hub_names = {}
for d in prod do
  local fin = get(used_by, d.name, 0)
  if fin >= in_at or uses_n[d.name] >= out_at then
    hubs[d.name] = true
    push(hub_names, d.name .. " (in " .. fin .. ", out " .. uses_n[d.name] .. ")")
  end
end

-- The rest, in file order, with the edges among them.
local rest = {}
local at = {}
for d in prod do
  if not has_key(hubs, d.name) then
    push(rest, d)
    at[d.name] = #rest
  end
end
local edges = {}
for d in rest do
  for u in d.uses do
    if has_key(at, u) then push(edges, {a = at[d.name], b = at[u], text = d.name .. "->" .. u}) end
  end
end
local before = {}
local sum = 0
for i = 1, #rest do
  sum = sum + lines_of(rest[i])
  before[i] = sum
end

print(P .. ": " .. #decls .. " declarations; " .. #prod .. " production, " .. #tests .. " tests; " .. #rest .. " left once " .. #hub_names .. " hubs are set aside, " .. #edges .. " edges among them")
local big = {}
for d in decls do
  if lines_of(d) >= 150 then push(big, d.name .. ":" .. d.first .. "(" .. lines_of(d) .. ")") end
end
if #big > 0 then print("largest (150+ lines; a seam inside one is below the top level): " .. join(big, ", ")) end
print("hubs: " .. join(hub_names, ", "))

-- **THE CUT PROFILE**: for each gap after the i-th, the edges that cross
-- it; a gap few cross, with code on both sides, is a seam in the file's
-- own order.
local most = parse_int(arg("min", "120"))
local gaps = {}
for i = 1, #rest - 1 do
  local left = before[i]
  local right = sum - left
  if left >= most and right >= most then
    local crossing = {}
    for e in edges do
      local lo = min(e.a, e.b)
      local hi = max(e.a, e.b)
      if lo <= i and hi > i then push(crossing, e.text) end
    end
    push(gaps, {i = i, n = #crossing, crossing = crossing, left = left, right = right})
  end
end
print("")
print("the gaps fewest edges cross (each side at least " .. most .. " lines):")
local shown = 0
local taken = {}
while shown < SHOW and count(taken) < #gaps do
  local best = 0
  for k = 1, #gaps do
    if not has_key(taken, tostring(k)) then
      if best == 0 or gaps[k].n < gaps[best].n then best = k end
    end
  end
  taken[tostring(best)] = true
  local g = gaps[best]
  -- Neighbours of a gap already shown say the same seam: shown once.
  local near = false
  for k in keys(taken) do
    local o = gaps[parse_int(k)]
    if o.i ~= g.i and o.i >= g.i - 2 and o.i <= g.i + 2 and get(o, "shown", false) then near = true end
  end
  if not near then
    g.shown = true
    shown = shown + 1
    local a = rest[g.i]
    local b = rest[g.i + 1]
    print("  after " .. a.name .. ":" .. a.last .. ", before " .. b.name .. ":" .. b.first .. ": " .. g.n .. " cross (" .. g.left .. " lines above, " .. g.right .. " below)" .. (g.n > 0 and (": " .. join(take(g.crossing, 6), ", ")) or ""))
  end
end

-- **WHO REACHES IT**: each declaration that is not a hub, grouped by the
-- hubs whose uses reach it (through other declarations, not through
-- hubs). A helper only `serve` reaches goes with `serve`; one `main` and
-- `serve` both reach is shared; one no hub reaches is the tests' or dead.
-- This is the file's structure by caller, whatever its order.
local reached = {}
for d in rest do reached[d.name] = {} end
for h in prod do
  if has_key(hubs, h.name) then
    local todo = {}
    for u in h.uses do
      if has_key(at, u) then push(todo, u) end
    end
    local seen = {}
    while #todo > 0 do
      local x = todo[#todo]
      todo = take(todo, #todo - 1)
      if not has_key(seen, x) then
        seen[x] = true
        push(reached[x], h.name)
        for u in rest[at[x]].uses do
          if has_key(at, u) and not has_key(seen, u) then push(todo, u) end
        end
      end
    end
  end
end
local by_sig = {}
local sigs = {}
for d in rest do
  local hs = reached[d.name]
  sort(hs)
  local sig = join(hs, " + ")
  if sig == "" then sig = "(no hub: tests' or unused)" end
  if not has_key(by_sig, sig) then
    by_sig[sig] = {lines = 0, names = {}}
    push(sigs, sig)
  end
  by_sig[sig].lines = by_sig[sig].lines + lines_of(d)
  push(by_sig[sig].names, d.name .. ":" .. d.first .. "(" .. lines_of(d) .. ")")
end
print("")
print("by the hubs that reach them:")
for s in sigs do
  local g = by_sig[s]
  print("  " .. s .. ": " .. #g.names .. " declarations, " .. g.lines .. " lines: " .. join(take(g.names, NAMES_SHOWN), ", ") .. (#g.names > NAMES_SHOWN and (", ... " .. (#g.names - NAMES_SHOWN) .. " more") or ""))
end
```

## Program 2: `zig_split.shale`, a move done whole (197 lines)

**What it does.** It moves named declarations from one Zig file to
another and leaves both files building. It is zig-webbox's move recipe
as one script:

1. `zig_move` the names, with their doc comments.
2. Put `pub` on what the old file still uses.
3. Give the new file a `//!` header and the imports its code needs.
4. Qualify or alias the old file's uses of what moved.
5. Import the new file into the old one.
6. With `from_as`, have `zig_move` reach what the moved code needs of the
   old file through it.
7. Name the new file in the old file's `test {}` block, so its tests run.

**Why it's shaped like this.** Every step is something today's moves
needed and the earlier version lacked:
- **Step 7 exists** because metal-vmm's serve.zig moved with two tests
  that then ran in no build.
- **The name-collision check near the top**, now exact by `zig_tokens`,
  exists because `machine` was already a name in 61 places.
- **The `var` rule in step 4** exists because `const x = m.x;` cannot
  alias a mutable global.
- **`into=yes`** exists because metal-vmm's pair code belonged in a file
  that already existed.
- **`from_as`** started here as a 40-line loop. Then the kernel's
  host_facts move needed 26 names and the loop ran out of steps and
  arena, so it became an option of `zig_move` itself (and
  `zig_renames`, a rename of many names in one pass).

The judge that ran after each move, `move_judge.shale`, isn't shown. It
compares the release binaries' symbols by name and size, and the tests
by name and by count. It deserves a mention because it caught the
silent-test problem, and because two kinds of build noise taught it
rules: Zig numbers its anonymous types, and the coverage SDK names its
sites by where they are. The kernel's new `-Dstamp=off` made the third
kind of noise, the commit stamp, go away entirely.

```lua
-- **DECLARATIONS MOVED TO A NEW FILE, AND THE OLD ONE MADE TO USE THEM**:
-- zig-webbox SHALE-AGENTS.md's recipe, as one script.
--
--   shale ~/shale-scripts/zig_split.shale from=src/main.zig to=src/boot.zig \
--     as=boot names=a|b|c doc="The guest's boot: ..." [after=pair]
--
-- `names` are separated by `|` (a test's name may hold a comma).
--
--   1. zig_move the names, each with its doc and the plain comment above;
--   2. `pub` on each the old file still uses (needs_pub);
--   3. the new file's `//!` (doc) and the imports the moved code uses;
--   4. each use left in the old file qualified, `as.name` (zig_rename);
--      or, with `uses=alias`, left as it is under `const name = as.name;`
--      beside the import (the old file's own idiom, where it has one);
--   5. `const as = @import("to's name");` in the old file, after the
--      import named `after` (or after its last top-level import);
--   6. what the moved code uses of the old file (needs_from_from) printed:
--      the script's caller decides, import or copy;
--   6b. with `from_as=X`, what the moved code uses of the old file is
--      reached through it (zig_move's own `from_as`: the uses qualified,
--      the import, `pub` in the old file);
--   7. the new file named in the old file's `test {}` block of
--      `_ = @import(...)` lines, where it has one: a test build never
--      analyses `main`, so a file only `main` reaches never runs its tests
--      (metal-vmm's serve.zig: the same names, two tests fewer run).
-- The compiler judges after (`zig build`), and a move judge.

const FROM = arg("from", "")
const TO = arg("to", "")
const AS = arg("as", "")
const NAMES = split(arg("names", ""), "|")
const DOC = arg("doc", "")
const AFTER = arg("after", "")
const USES = arg("uses", "qualify")
-- `into=yes`: TO is a file already there (the declarations join it): no
-- `//!` of its own, only the imports it lacks, and no test block to add it to.
const INTO = arg("into", "no") == "yes"
const FROM_AS = arg("from_as", "")
if USES ~= "qualify" and USES ~= "alias" then fail("zig_split: uses=qualify or uses=alias, not " .. USES) end

if FROM == "" or TO == "" or AS == "" or #NAMES == 0 or (DOC == "" and not INTO) then fail("zig_split: from, to, as, names and doc (or into=yes)") end
if INTO and not exists(TO) then fail("zig_split: into=yes, and " .. TO .. " is not there") end
if not INTO and exists(TO) then fail("zig_split: " .. TO .. " is there already: this makes a new file (into=yes joins one)") end
-- **THE IMPORT'S NAME MUST BE FREE**: Zig lets nothing shadow a top-level
-- name, so a parameter or a local already called `as` would stop the
-- build in every function that has one. Exact, by Zig's tokenizer: an
-- identifier `as` not right after a `.` (`x.as` is a field, not a name).
local toks = zig_tokens(FROM)
local taken = 0
for k = 1, #toks do
  if toks[k].tag == "identifier" and toks[k].text == AS and (k == 1 or toks[k - 1].tag ~= "period") then taken = taken + 1 end
end
-- Joining a file the old one imports already, under `as`, is the point.
local imported_as = false
for i in zig_imports(FROM) do
  local tb = split(TO, "/")
  if i.name == AS and i.target == tb[#tb] then imported_as = true end
end
if taken > 0 and not imported_as then fail("zig_split: `" .. AS .. "` is a name in " .. FROM .. " already (" .. taken .. " times, a parameter, a local or a declaration): choose another `as`") end

local move_opts = {comment = "doc_and_plain"}
if FROM_AS ~= "" then move_opts.from_as = FROM_AS end
local r = zig_move(FROM, TO, NAMES, move_opts)
print("moved " .. r.moved)
if FROM_AS ~= "" then print("reached through " .. FROM_AS .. ": " .. r.qualified .. " uses; made pub in " .. FROM .. ": " .. join(r.made_pub, ", ")) end

-- 2. pub, where the old file still uses one.
local made_pub = {}
for n in r.needs_pub do
  if not has_key(made_pub, n.name) then
    made_pub[n.name] = true
    local done = false
    for prefix in {"const ", "fn ", "var "} do
      if not done and count_in(TO, "\n" .. prefix .. n.name) + (starts_with(read(TO), prefix .. n.name) and 1 or 0) > 0 then
        local text = read(TO)
        if starts_with(text, prefix .. n.name) then
          replace(TO, "pub " .. text)
        else
          edit(TO, "\n" .. prefix .. n.name, "\npub " .. prefix .. n.name)
        end
        done = true
      end
    end
    if not done then print("needs pub, not made: " .. n.name .. " (a member or a method: by hand)") end
  end
end

-- 3. The new file's head: its doc and its imports; or, joining a file,
-- the imports it lacks, after its last.
if INTO then
  local have = {}
  for d in zig_decls(TO) do have[d.name] = true end
  local add = {}
  local seen = {}
  for i in r.needs_import do
    if not has_key(seen, i.name) and not has_key(have, i.name) then
      seen[i.name] = true
      push(add, "const " .. i.name .. " = " .. i.target .. ";")
    end
  end
  if #add > 0 then
    local its = {}
    for i in zig_imports(TO) do
      if i.name ~= "" then push(its, i) end
    end
    local at_text = lines(read(TO))[its[#its].line]
    edit(TO, at_text .. "\n", at_text .. "\n" .. join(add, "\n") .. "\n")
  end
  print("imports added to " .. TO .. ": " .. #add)
else
  local head = {}
  for l in split(DOC, "\\n") do push(head, "//! " .. l) end
  push(head, "")
  local seen = {}
  for i in r.needs_import do
    if not has_key(seen, i.name) then
      seen[i.name] = true
      push(head, "const " .. i.name .. " = " .. i.target .. ";")
    end
  end
  -- One blank line under the head, whatever it holds.
  while #head > 0 and head[#head] == "" do head = take(head, #head - 1) end
  local body = read(TO)
  while starts_with(body, "\n") do body = sub(body, 2) end
  replace(TO, join(head, "\n") .. "\n\n" .. body)
end

-- 4. The old file's uses, qualified, or aliased.
local moved = {}
for n in NAMES do moved[n] = true end
local renamed = 0
local qualified = {}
local aliases = {}
for u in r.uses_left do
  if has_key(moved, u.name) and not has_key(qualified, u.name) then
    qualified[u.name] = true
    -- A `var` cannot be aliased (`const x = m.x;` copies it, at comptime,
    -- which a var is not): its uses are qualified, in either mode.
    local is_var = false
    for d in zig_decls(TO) do
      if d.name == u.name and d.kind == "var" then is_var = true end
    end
    if USES == "alias" and not is_var then
      push(aliases, "const " .. u.name .. " = " .. AS .. "." .. u.name .. ";")
    else
      local z = zig_rename(FROM, u.name, AS .. "." .. u.name)
      renamed = renamed + z.renamed
    end
  end
end
if USES == "alias" then print("aliased " .. #aliases .. " names") else print("qualified " .. renamed .. " uses of " .. count(qualified) .. " names") end

-- 5. The import, in the old file.
local imports = {}
for i in zig_imports(FROM) do
  if i.name ~= "" then push(imports, i) end
end
local anchor = nil
for i in imports do
  if AFTER ~= "" and i.name == AFTER then anchor = i end
end
if anchor == nil then anchor = imports[#imports] end
local lines_of = lines(read(FROM))
local anchor_text = lines_of[anchor.line]
local base = split(TO, "/")
local added = "const " .. AS .. " = @import(\"" .. base[#base] .. "\");"
if imported_as then added = nil end
if #aliases > 0 then
  if added == nil then added = join(aliases, "\n") else added = added .. "\n" .. join(aliases, "\n") end
end
if added ~= nil then edit(FROM, anchor_text .. "\n", anchor_text .. "\n" .. added .. "\n") end

-- 7. The new file in the old file's test block, if it has one.
local text = read(FROM)
-- A plain find first: the pattern over a whole large file is costly.
local block = nil
local tb_at = find(text, "\ntest {\n")
if tb_at ~= nil then block = re_find(sub(text, tb_at, tb_at + 8000), "^\ntest \\{\n(    _ = @import\\(\"[^\"]+\"\\);\n)+\\}") end
if INTO then
  print(TO .. " was there: enrolled as it was")
  block = nil
end
if block ~= nil and contains(block.text, "@import(\"" .. base[#base] .. "\")") then
  print(base[#base] .. " is enrolled in " .. FROM .. "'s test block already")
elseif block ~= nil then
  local closing = sub(block.text, 1, #block.text - 1)
  edit(FROM, block.text, closing .. "    _ = @import(\"" .. base[#base] .. "\");\n}")
  print("enrolled " .. base[#base] .. " in " .. FROM .. "'s test block")
elseif not INTO then
  print("no `test {}` block of imports in " .. FROM .. ": name " .. TO .. " where its tests are enrolled")
end

-- 6. What the moved code uses of the old file.
if FROM_AS == "" then
  for n in r.needs_from_from do print("needs from " .. FROM .. ": " .. n.name .. " (" .. FROM .. ":" .. n.line .. "): import or copy it, or give from_as") end
end
for n in r.needs_pub do print("pub: " .. n.name) end
```

## Using it, and where to go next

**What today showed.** The programs above read like what they do, which
is the point of Shale. The pain points:
- **Budgets.** The defaults are sized for small scripts; a refactor of a
  2,600-line file needs `--budget steps=200000000 --budget
  arena_bytes=...`, and every time the box hit them it learned only by
  stopping. A script should be able to declare its own budgets at its
  top, within limits a launch sets, or the defaults should scale with
  the files a script names.
- **Scripts calling scripts.** zig_split, pub_loop, zig_tidy and
  move_judge call each other through `run({"shale", ...})` with a `want`.
  That works, but it's a process per call, an argument string per
  option, and no shared functions. A `use("mine:zig_split")` that loads
  another script's functions would let these become a library.
- **Gate friction.** A launch line can't hold a quoted argument, so a doc
  string or a name with a space goes through `run` inside a heredoc.
  Allowing one `doc="..."`-style quoted value would remove most of that.
- **Small gaps that cost minutes:** `parse_int` doesn't take hex, a
  regular expression over a whole large file is slow enough to exhaust a
  run, and `in` is a keyword, so it can't be a table key.

**Where it could go, with a few more hours.** My order, by value:

1. **Promote the refactor kit into zig-webbox, with tests.**
   `seams.shale`, `zig_split.shale`, `move_judge.shale`, `pub_loop.shale`
   and `zig_tidy.shale` have each had two real users today, which is the
   point where an abstraction earns its place. In `zig-webbox/tools/zig/`,
   with fixtures and the gate, CC can use them too, and their bugs get
   tests instead of my memory. About two hours.
2. **A seams picture.** The essay server renders Graphviz. A `dot=1`
   mode for seams.shale would draw the hubs and the groups. For a file
   like dog-park's physics.zig, dense with about 35 edges across its best
   gap, a picture may show what the lists can't. Half an hour.
3. **The first structural split: a container.** The kernel's `tcp.zig`
   `Table` (1,363 lines) and metal-vmm's `Scsi` now show their structure
   (`Scsi`'s fields grouped by which methods touch them: the command
   path, the line, synchronize, transfer). Acting on that is no longer a
   pure move: fields go into sub-structs, and `self.x` becomes
   `self.line.x`. The byte judge then no longer applies. The judge
   becomes the tests plus metal-vmm's sweeps, and Shale needs a field
   rename that knows which struct a `.x` belongs to, which tokens alone
   can't say. This is the frontier, and it's a CC-sized chunk once the
   design is agreed.
4. **Script libraries (`use`)**, after (1), since (1) shows exactly which
   functions want sharing.
5. **More Python and shell to replace.** The kernel's droplet and probe
   scripts (`judge_gopher.py` and its siblings) and angry-gopher's
   remaining Python lints. CC's 238 is the first of those. Each
   replacement is a second user of something, and each finds a want.

If I had to pick one thing for the next hour, it would be (1). Today's
scripts are the most-used Shale code in the repos, and they live outside
all of them.
