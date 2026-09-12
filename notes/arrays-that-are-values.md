# Arrays that are values: Elm, Clojure, and Pages

BASIC arrays are mutable: `LET A(I)=X` changes one cell and nothing else.
A Roc machine is a value handed from statement to statement. The question
is how cheap one cell's change can be when the array is a value. Elm and
Clojure both answered it with the same structure. This note reads their
sources and holds `basic/roc/Pages.roc` up against them.

The short answer: Pages already has Elm's API, and in Roc it is faster
than Elm's structure wherever nothing else refers to the array. The two
part company in one place, a shared array, and BASIC has exactly one of
those: the page's history of machines. That case is unmeasured.

---

## Elm's Array, from its source

The files are `elm/core` 1.0.5, on this box under `~/.elm`:

| file | lines |
|---|---|
| `src/Array.elm` | 1,004 |
| `src/Elm/JsArray.elm` | 181 |
| `src/Elm/Kernel/JsArray.js` | 156 |

So 1,341 lines in all, most of them doc comments and the bulk operations
(`map`, `append`, `slice`). The part that answers our question is small.

An array is four things: its length, a starting shift, a tree, and a
tail.

```elm
set index value ((Array_elm_builtin len startShift tree tail) as array) =
```

The tree is made of nodes that are either a subtree or a leaf. Each node is
a `JsArray` of at most 32 entries (`branchFactor = 32`, so each level
takes 5 bits of the index, `shiftStep`). The tail holds the last 1 to 32
elements outside the tree, so `push` usually touches only the tail.

`set` walks down the index five bits at a time. On the way back up it
replaces each node it passed through:

```elm
setHelp shift index value tree =
    let pos = Bitwise.and bitMask <| Bitwise.shiftRightZfBy shift index
    in
    case JsArray.unsafeGet pos tree of
        SubTree subTree ->
            JsArray.unsafeSet pos (SubTree (setHelp (shift - shiftStep) index value subTree)) tree
        Leaf values ->
            JsArray.unsafeSet pos (Leaf (JsArray.unsafeSet (Bitwise.and bitMask index) value values)) tree
```

"Pure Elm" rests on the kernel, and the kernel's `unsafeSet` is a copy:

```js
var _JsArray_unsafeSet = F3(function(index, value, array)
{
    var length = array.length;
    var result = new Array(length);
    for (var i = 0; i < length; i++) { result[i] = array[i]; }
    result[index] = value;
    return result;
});
```

So one `set` copies one node per level on the path from the root to the
cell, each at most 32 slots. An array of 1,200 cells is a tail plus two
levels, so a write copies at most about 100 slots. The old array is
untouched and still valid, and it shares every node the write did not pass
through.

## Clojure's PersistentVector

`clojure/lang/PersistentVector.java` (about 850 lines) is the same tree:
32-slot nodes, 5 bits a level, a tail. Its update copies the path the same
way:

```java
private static Node doAssoc(int level, Node node, int i, Object val){
    Node ret = new Node(node.edit, node.array.clone());
    if(level == 0) ret.array[i & 0x01f] = val;
    else {
        int subidx = (i >>> level) & 0x01f;
        ret.array[subidx] = doAssoc(level - 5, (Node) node.array[subidx], i, val);
    }
    return ret;
}
```

Clojure adds one idea that matters for Roc: **transients**. Every node
carries an `edit` token. A transient vector owns a token, and a node whose
token is the transient's own is written in place instead of cloned:

```java
Node ensureEditable(Node node){
    if(node.edit == root.edit) return node;
    return new Node(root.edit, node.array.clone());
}
```

`persistent()` sets the token to null, and from then on every node is
shared again. A loop that builds a vector by a thousand writes goes
transient, writes in place, and comes back persistent. It pays for copies
only on nodes it did not already own.

## Roc has transients built in

This is where Roc differs from both. **A Roc list whose reference count is
one is a transient; a list with a count above one is persistent.** Nobody
asks for it. The ownership token is the reference count, checked on every
`List.set`, per list.

So in Roc the question is never "copy or mutate". Roc mutates whenever
nothing else refers to the list. The question is: **when something else
DOES refer to it, how much does one write copy?**

| structure | a write, nothing else refers to it | a write, shared |
|---|---|---|
| flat `List(F64)` | in place | the whole array |
| `Pages` (4,096-cell pages under a table) | in place | one page, plus the table if it is shared too |
| 32-way tree (Elm, Clojure) | in place, per node | one node per level, 32 slots each |

Elm and Clojure pay for the tree on every read, 2 to 4 levels of indexing,
because they have no in-place path. Roc gets the in-place path from its
reference counts. So where arrays are never shared, the flattest structure
is the fastest one, and Pages is nearly flat.

## Is a BASIC array ever shared?

**In the batch doors, no** — as long as the writes are spelled so nothing
else keeps a reference. That is the only thing that was wrong before Pages.
`set_arr` read the array's record out of the machine's list, so its cells
had two references and every store copied them all.
Now `Pages.set` takes the page out of the table before writing it, and
`set_arr` takes the array out of the machine's list the same way. Measured
on the nightly, compile included:

| program | wall |
|---|---|
| 200,000 stores into `DIM A(10)` | 19.7 s |
| 200,000 stores into `DIM A(4000)` | 18.9 s |

The same time for a 400× larger array means the stores are in place. P134,
which timed out at 120 s, now finishes and passes.

**On the page, yes, once per typed line.** The host keeps every state:

```zig
/// One line into a waiting machine, or a wake for a sleeping one.
pub export fn send(line_len: u32) void {
    const cur = top() orelse return;
    push(roc_resume(borrowed(cur), ...));
}
```

`send` borrows the current machine and pushes the next one, and `history`
holds both so that `back` can pop. After a typed line, the new machine and
the one in `history` share their arrays. The first write to a page copies
it:
- 4,096 numbers, 32 KB, for an array
- 4 KB for POKE memory, plus the 4,096-entry page table, another 32 KB

After that the new copy is referred to only once, and the rest of that
run writes in place. A tree would copy about three 32-slot nodes per cell
first touched. The difference is in how much each kept machine holds,
which is little for a program that touches a few cells per line. Nobody
has measured it. The page never calls `back` today, so it is also paying
for a history nobody uses.

## The second reason for a tree: mistakes

The first reason is sharing. The second is what happens when a later edit
breaks the take-out spelling, which we have done three times now:
- `?? l`
- `List.update`
- reading the record out of `m.arr`

With Pages, a broken spelling copies a 4,096-cell page per write. With a
tree, it copies the path. `Mem.roc`'s measurement, in
[memory as a value](memory-as-a-value.md), is the size of that difference:
with the fast path broken, the trie was about eleven times cheaper than
4 KB pages (12.25 s against 137.8 s).

A tree does not make a broken spelling free, and it does not make it
visible either. `tests/copycheck.sh` still has to be what notices.

## What this says to do

1. **Keep the API.** `Pages.new`, `Pages.get`, `Pages.set(cells, i, v,
   fill)` is Elm's `Array.initialize`/`get`/`set` without `push`. Arrays
   are sized at DIM, so the tail, the part of Elm's code that is about
   growing, has nothing to do here. Every caller would stay as it is if
   the representation behind it changed.
2. **The tree is small in Roc.** `copycheck.sh` already holds one, a
   32-way trie written with the take-out spelling, in about twenty lines:

   ```roc
   Node := [Empty, Leaf(List(U8)), Branch(List(Node))]
   ```

   Generic over the cell and with its depth taken from the size, it is
   what `Pages.roc` would become — in the range of a hundred lines, not
   Elm's thousand. Most of Elm's lines go to operations BASIC does not
   use.
3. **Measure the page's case before switching.** One program that types
   lines into an INPUT loop and writes an array cell per line, run with
   `history` kept and then with it dropped, while measuring the wasm
   heap. If the history's pages show up, switch Pages to the tree. If not,
   Pages is the Elm structure's fast path, and the tree is insurance
   against the next broken spelling.

The batch doors, the corpora and the merge do not depend on the answer.

---

Sources: elm/core 1.0.5 `src/Array.elm`, `src/Elm/JsArray.elm`,
`src/Elm/Kernel/JsArray.js` (read from `~/.elm/0.19.1/packages`);
[clojure/lang/PersistentVector.java](https://github.com/clojure/clojure/blob/master/src/jvm/clojure/lang/PersistentVector.java);
`roc-apps/tests/copycheck.sh`; `roc-apps/basic/wasm/platform/host.zig`;
[memory as a value](memory-as-a-value.md).
