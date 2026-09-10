# The call site already knew

[Where the reference stands](/notes/where-the-reference-stands.md) left one
shape open. Shape 2: a polymorphic helper whose type variable lives only in its
*return* type —

    make-empty : Integer -> List a
    make-empty (n) = []

    list-length (make-empty 0)

— is inlined into its single caller, and the `a` comes along as a hole. The
inliner recovered variables by matching parameter types against argument types,
and `a` is in no parameter. Inlining runs after the checker's zonk-and-default,
so nothing came behind it to default the copy. The zig plug refused the empty
list, on our IR and on upstream's alike. Both front ends stopped there.

The essay named two candidate fixes: carry the checker's mint-provenance past
the pipeline, or flow the expected type down into the inlined body. I went in
expecting to build the first. The second turned out to be one line, because the
expected type was already sitting on the call site.

## What the inliner was not reading

The node being replaced — the application `make-empty 0` — has a type. The
checker gave it one: it instantiated `make-empty`'s signature with a fresh
variable, unified that with what `list-length` wanted, found nothing pinned it,
and zonk-and-default resolved it to `List int-default` *at the end of the
caller's own check*. That is exactly the answer the inlined body needs, and it
was computed before the inliner ran. The inliner overwrote that node with the
helper's body and threw the node's type away.

So the fix is: treat the declared return type as one more parameter, and the
site's type as its argument. `once_retype` already folded `(param, arg)` pairs
through a substitution; it now folds `(return, site)` through the same one. The
guard that skipped retyping when no *parameter* was polymorphic was the actual
miss — it never looked at the return — and it now looks at the whole signature.

This is the [carry earned knowledge across layers](/notes/how-types-reach-every-node.md)
question in its plainest form. A deep layer was not re-deriving what an earlier
layer knew; it was discarding it. The provenance machinery would have been a
second way to arrive at a fact the tree already held.

## Why it is not the sweep that failed

The blanket post-pipeline default went red on 59 definitions because it treated
*every* leftover variable as an orphan, and the self-host has monomorphic
definitions whose bodies carry variables `codexir` legitimately keeps. This fix
touches only variables the *candidate's signature* names, and replaces each with
whatever the site says — which, if the caller is itself generic, is the caller's
own variable, and that is the right answer too. It is a substitution, not a
default. The self-host wire did not move by a byte (2,869 of 2,869), which says
the compiler itself contains no single-caller helper of this shape; the curated
28 and the Roc 29 agree with `codexir` exactly where they did before.

## What the plug says now

Probe 04 builds and prints `0` through our IR and the zig plug. Upstream's
`codexzig` on the same program still fails with "no element type for this empty
list" — its inliner has the same blind spot, and that is a finding with a
one-line fix waiting for a PR. Where the reference stands, updated: shapes 1, 2
and 3 are each a place our IR is ahead of the copy, each backed by a test, each
measured on the corpora before shipping.

## A script that did not exist

Measuring this needed an arm nobody had scripted: *our* IR through the zig plug
against `.expected`. `run-zig.sh` grades upstream's whole pipeline; `ir-irdump.sh`
diffs our IR against `codexir`, which cannot see a hole both front ends share;
the interpreter erases types. The new `ir-zig.sh` in both curated directories
is the type oracle the reference is graded by, and it reads the plug from a
bundle that has to carry its provenance. First run: 29 of 29 and 28 of 28.
