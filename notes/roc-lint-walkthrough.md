# One Roc lint, end to end

*2026-11-01. LC. A four-line Roc module, the lint it fails, and every step between: what roc-ast writes, what Shale reads, and the Shale that decides. Everything below is real output from tonight's tools.*

## The program

```roc
module [shout]

shout : Str -> Str
shout = |s| Str.concat(Str.trim(Str.with_ascii_uppercased(s)), "!")
```

**The lint is `nest_depth`** ([cookbook/roc/nest_depth.shale](https://github.com/showell/shale/blob/master/cookbook/roc/nest_depth.shale)). A call whose argument is a call whose argument is a call, `f(g(h(x)))`, has to be read inside out. roc-apps' style guide says to write it left to right: a method chain, a pipe, or a named middle step.

What the lint says:

```
Shout.roc:4: nested: depth 3: shout = |s| Str.concat(Str.trim(Str.with_ascii_uppercased(s)), "!")
nest_depth (Roc): 1 files; nested 1 (min 3, strict); depth 3 1
```

## Step 1: Roc's own parser

**roc-ast** ([tools/roc_ast/main.zig](https://github.com/showell/shale/blob/master/tools/roc_ast/main.zig), in Shale) links the Roc compiler's `parse` module at roc-chat's pin, so the tree is exactly what the compiler sees. It can write that tree two ways.

**Its default is Roc's own debug printer,** the format the compiler's snapshot tests use, made for a person to read:

```
(file @1.1-4.68
	(module @1.1-1.15
		(exposes @1.8-1.15
			(exposed-lower-ident @1.9-1.14
				(text "shout"))))
	(statements
		(s-type-anno @3.1-3.19 (name "shout")
			(ty-fn @3.9-3.19
				(ty @3.9-3.12 (name "Str"))
				(ty @3.16-3.19 (name "Str"))))
		(s-decl @4.1-4.68
			(p-ident @4.1-4.6 (raw "shout"))
			(e-lambda @4.9-4.68
				(args
					(p-ident @4.10-4.11 (raw "s")))
				(e-apply @4.13-4.68
					(e-ident @4.13-4.23 (raw "Str.concat"))
					(e-apply @4.24-4.62
						(e-ident @4.24-4.32 (raw "Str.trim"))
						(e-apply @4.33-4.61
							(e-ident @4.33-4.58 (raw "Str.with_ascii_uppercased"))
							(e-ident @4.59-4.60 (raw "s"))))
					(e-string @4.64-4.67
						(e-string-part @4.65-4.66 (raw "!"))))))))
```

The nesting is visible at a glance: three `e-apply` nodes, each inside the one before. But the layout carries the structure (tabs, which things share a line), and strings are written unescaped. Until tonight Shale guessed the tree back out of this text, and that guessing is where the three reader bugs and the unescaped-string stop came from.

**`roc-ast --tree` writes the same tree for a program:** one fact a line, tab-separated, every value escaped. `n parent kind line col end_line end_col` is a node; `a node name value` is an attribute on the node it names.

```
n	0	file	1	1	4	68
n	1	module	1	1	1	15
n	2	exposes	1	8	1	15
n	3	exposed-lower-ident	1	9	1	14
n	4	text	0	0	0	0
a	5	value	shout
n	1	statements	0	0	0	0
n	6	s-type-anno	3	1	3	19
a	7	name	shout
n	7	ty-fn	3	9	3	19
n	8	ty	3	9	3	12
a	9	name	Str
n	8	ty	3	16	3	19
a	10	name	Str
n	6	s-decl	4	1	4	68
n	11	p-ident	4	1	4	6
a	12	raw	shout
n	11	e-lambda	4	9	4	68
n	13	args	0	0	0	0
n	14	p-ident	4	10	4	11
a	15	raw	s
n	13	e-apply	4	13	4	68
n	16	e-ident	4	13	4	23
a	17	raw	Str.concat
n	16	e-apply	4	24	4	62
n	18	e-ident	4	24	4	32
a	19	raw	Str.trim
n	18	e-apply	4	33	4	61
n	20	e-ident	4	33	4	58
a	21	raw	Str.with_ascii_uppercased
n	20	e-ident	4	59	4	60
a	22	raw	s
n	16	e-string	4	64	4	67
n	23	e-string-part	4	65	4	66
a	24	raw	!
```

Nodes are numbered from 1 in the order they come, so `n 16 e-apply` is a child of node 16. A `0 0 0 0` span is a grouping node with no source of its own (`statements`, `args`).

## Step 2: Shale's `roc_tree`

`roc_tree(paths)` (Shale's Linux prelude) runs `roc-ast --tree` and hands the lines to the host. The host turns them into a list of nodes, each a table `{kind, depth, parent, kids, line, col, end_line, end_col}` plus its attributes. For this file:

```
1 file (parent 0)
2   module (parent 1)
3     exposes (parent 2)
4       exposed-lower-ident (parent 3)
5         text (parent 4)
6   statements (parent 1)
7     s-type-anno (parent 6) name=shout
8       ty-fn (parent 7)
9         ty (parent 8) name=Str
10         ty (parent 8) name=Str
11     s-decl (parent 6)
12       p-ident (parent 11) raw=shout
13       e-lambda (parent 11)
14         args (parent 13)
15           p-ident (parent 14) raw=s
16         e-apply (parent 13)
17           e-ident (parent 16) raw=Str.concat
18           e-apply (parent 16)
19             e-ident (parent 18) raw=Str.trim
20             e-apply (parent 18)
21               e-ident (parent 20) raw=Str.with_ascii_uppercased
22               e-ident (parent 20) raw=s
23           e-string (parent 16)
24             e-string-part (parent 23) raw=!
```

A recipe never sees text from here on, only these tables.

## Step 3: the Shale that decides

**A call's depth is 1 plus the deepest call among its arguments.** The first kid of an `e-apply` is the function, and the rest are the arguments. This is the heart of `nest_depth.shale`, slightly trimmed:

```lua
function is_call(n)
  return n.kind == "e-apply" or n.kind == "e-method-call"
end

-- The call depth at node `i` of `ns`, kept in `memo` (-1 not yet known).
function cd(ns, memo, i, loose)
  if memo[i] >= 0 then return memo[i] end
  local n = ns[i]
  local k = n.kind
  local v = 0
  if k == "e-apply" then
    local best = 0
    for a in drop(n.kids, 1) do
      local x = cd(ns, memo, a, loose)
      if x > best then best = x end
    end
    -- A tag's payload (`Ok(...)`) is no call.
    if ns[n.kids[1]].kind == "e-tag" then v = best else v = 1 + best end
  elseif k == "e-method-call" then
    -- a method's receiver carries its depth through: a.f().g() reads left to right
    local recv = 0
    local best = 0
    for c in n.kids do
      if ns[c].kind == "receiver" then recv = cd(ns, memo, ns[c].kids[1], loose) end
      if ns[c].kind == "args" then
        for a in ns[c].kids do
          local x = cd(ns, memo, a, loose)
          if x > best then best = x end
        end
      end
    end
    v = 1 + best
    if recv > v then v = recv end
  elseif passes(k, loose) then
    -- `?`, a pipe, a nominal wrapper: no level of their own
    for c in n.kids do
      local x = cd(ns, memo, c, loose)
      if x > v then v = x end
    end
  end
  memo[i] = v
  return v
end
```

**Worked through on this file:**
- **Node 20,** `Str.with_ascii_uppercased(s)`: its one argument is node 22, an `e-ident`, which is depth 0. So node 20 is depth **1**.
- **Node 18,** `Str.trim(...)`: its argument is node 20. So **2**.
- **Node 16,** `Str.concat(..., "!")`: its arguments are node 18 (depth 2) and node 23, a string (depth 0). So **3**.

**Only the outermost call of a nest is reported,** so one long chain is one finding, not three. `outermost` climbs from node 16 to its parent, node 13, an `e-lambda`. That isn't a call, and nothing above passes depth on, so node 16 is outermost. The main loop then prints it:

```lua
for f in roc_tree(paths) do
  local ns = f.nodes
  local memo = {}
  for n in ns do push(memo, -1) end
  for i = 1, #ns do
    if is_call(ns[i]) and cd(ns, memo, i, LOOSE) >= MIN and outermost(ns, memo, i, LOOSE) then
      -- path:line: nested: depth N: <the line>
    end
  end
end
```

## The fix, and why it's quiet

```roc
shout = |s| s.with_ascii_uppercased().trim().concat("!")
```

`nest_depth (Roc): 1 files; nested 0 (min 3, strict)`.

**The tree shows why.** The calls are now `e-method-call` nodes, each one's `receiver` holding the call before it:

```
n	13	e-method-call	4	13	4	57
a	16	method	.concat
n	16	receiver	0	0	0	0
n	17	e-method-call	4	13	4	45
a	18	method	.trim
n	18	receiver	0	0	0	0
n	19	e-method-call	4	13	4	38
a	20	method	.with_ascii_uppercased
n	20	receiver	0	0	0	0
n	21	e-ident	4	13	4	14
a	22	raw	s
n	20	args	0	0	0	0
n	18	args	0	0	0	0
n	16	args	0	0	0	0
n	25	e-string	4	53	4	56
...
```

A receiver carries its depth through rather than adding a level, because a chain reads left to right. Each call's own arguments are depth 0, so the whole chain is depth 1.

## Where this goes next

**Every step a recipe takes past `roc_tree` is ordinary Shale over a list of tables,** about 160 lines for this one. A native-Roc version of the same lint, as notramo suggested on Zulip, would replace steps 1 and 2 with the compiler's parser in-process, and could keep step 3's logic nearly line for line.
