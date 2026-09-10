# The declaration's variable

The next pull request to Cobblestone is one definition in `IR/Lowering.codex`
and it closes the last red on the Roc corpus that was not already filed. This
is what it fixes, drawn.

## Two kinds of type variable

A polymorphic record declares a parameter. A polymorphic definition quantifies
a variable. They look the same on the wire, `(tvar N)`, and they are not the
same thing at all.

```dot
digraph {
  rankdir=LR; bgcolor="transparent"; pad=0.2; nodesep=0.4;
  node [shape=box style="rounded,filled" fillcolor="#f4f0e4" color="#c9bfa7" fontname="Helvetica" fontsize=12];
  edge [color="#b0a890" arrowsize=0.7 fontname="Helvetica" fontsize=10];
  subgraph cluster_d { label="the DECLARATION   Box (a) = record { get : Integer -> a }" fontname="Helvetica" fontsize=11 color="#c9bfa7" style="rounded";
    a2 [label="a  =  tvar 2\nbound by the record type;\nmeaningful only inside its declaration" fillcolor="#fbe9e0"]; }
  subgraph cluster_f { label="the DEFINITION   wrap : b -> Box b ;  wrap (x) = Box { get = \\\\i -> x }" fontname="Helvetica" fontsize=11 color="#c9bfa7" style="rounded";
    b3 [label="b  =  tvar 3\nquantified by wrap's signature;\nthe plug knows it as a comptime parameter" fillcolor="#e3efe0"]; }
}
```

Inside `wrap`, only `tvar 3` has a binder. A `tvar 2` appearing anywhere in
`wrap`'s wire is a variable nobody introduced, and a typed plug says so:

    zig plug: unresolved type variable T2 of __lam_0

## Where the declaration's variable got in

`lower-record` looks the constructor up and strips its arrows, which yields the
record in its declared form: name, parameters, and fields whose types name
those parameters. Then it lowers each field value with the field's declared
type as the expectation.

```dot
digraph {
  rankdir=TB; bgcolor="transparent"; pad=0.2; nodesep=0.3; ranksep=0.35;
  node [shape=box style="rounded,filled" fillcolor="#f4f0e4" color="#c9bfa7" fontname="Helvetica" fontsize=12];
  edge [color="#b0a890" arrowsize=0.7 fontname="Helvetica" fontsize=10];
  lr  [label="lower-record  Box { get = \\\\i -> x }\nexpected from context: Box (tvar 3)"];
  rt  [label="record-ty, from the constructor:\nRecordTy Box (tvar 2) { get : Integer -> tvar 2 }" fillcolor="#fbe9e0"];
  fe  [label="field-expected = lookup-record-field\n= Integer -> tvar 2" fillcolor="#fbe9e0"];
  ll  [label="lower-lambda  \\\\i -> x\nbody lowers to  (name x (tvar 3))"];
  lrt [label="lambda-recorded-ty declared-ret body-ty expected\n\nbody-ty has variables  ->  answer the EXPECTATION" fillcolor="#fbe9e0"];
  wire [label="on the wire:  (fn int-default (tvar 2))\n\nrefine-record-ty-from-fields fixes the RECORD's type afterwards,\nbut the lambda node already carries 2" fillcolor="#fbe9e0"];
  lr -> rt -> fe -> ll -> lrt -> wire;
}
```

The last box is the part that made this hard to see. `lower-record` does
know the applied arguments: after the fields are lowered it refines the
record's own type from them, and emits `(record-ty "Box" (args (tvar 3)))`
correctly. The repair runs one step too late for the field values, which were
lowered against the unrefined form and have already recorded what they were
handed.

Why a monomorphic use never showed it: with `wrap-int : Integer -> Box Integer`
the body's type is `int-default`, no variables, and `lambda-recorded-ty` takes
its third arm — substitute the declaration's parameter from the body — so the
lambda records `Integer -> int-default`. It is exactly the polymorphic body,
whose type is itself a variable, that trips the guard and keeps the
declaration's `a`.

## The fix

Compute the applied record type *before* the fields, and hand each field its
declared type with the declaration's parameters substituted by the applied
arguments.

```dot
digraph {
  rankdir=TB; bgcolor="transparent"; pad=0.2; nodesep=0.3; ranksep=0.35;
  node [shape=box style="rounded,filled" fillcolor="#f4f0e4" color="#c9bfa7" fontname="Helvetica" fontsize=12];
  edge [color="#b0a890" arrowsize=0.7 fontname="Helvetica" fontsize=10];
  lr  [label="lower-record  Box { get = \\\\i -> x }\nexpected from context: Box (tvar 3)"];
  rt  [label="record-ty:  RecordTy Box (tvar 2) { get : Integer -> tvar 2 }"];
  ap  [label="applied-ty = prefer-applied-record-ty expected record-ty\n= RecordTy Box (tvar 3) { .. }" fillcolor="#e3efe0"];
  fe  [label="field-expected = subst-type-vars-from-arg record-ty applied-ty (Integer -> tvar 2)\n= Integer -> tvar 3" fillcolor="#e3efe0"];
  ll  [label="lower-lambda  \\\\i -> x   against  Integer -> tvar 3"];
  wire [label="on the wire:  (fn int-default (tvar 3))\n\nthe definition's own b; the plug builds it" fillcolor="#e3efe0"];
  lr -> rt -> ap -> fe -> ll -> wire;
}
```

`prefer-applied-record-ty` already existed; it was used only for the emitted
record type. `subst-type-vars-from-arg` already existed; it learns a mapping
by matching a declared form against an applied one and applies it to a
target. Neither is new. When the context supplies no arguments, the applied
type *is* the declared one, the mapping is the identity, and every
monomorphic record literal lowers to the bytes it always did.

## What it looks like from our side

The Rust front end never had this bug, because it never used the declared
field type as an expectation: it lowers the field value with no expectation
and reads the record's type from what the checker recorded. So the three Roc
iterator programs were a place where the two front ends disagreed and ours
built. With the fix in upstream's tree, a rebuilt `codexir` emits, for all
three, IR that is byte-identical to what ours had emitted all along.

```dot
digraph {
  rankdir=LR; bgcolor="transparent"; pad=0.2; nodesep=0.5;
  node [shape=box style="rounded,filled" fillcolor="#f4f0e4" color="#c9bfa7" fontname="Helvetica" fontsize=12];
  edge [color="#b0a890" arrowsize=0.7 fontname="Helvetica" fontsize=10];
  src [label="roc-iter-map.codex" fillcolor="#e8e2d0"];
  ours [label="irdump (Rust)\n(fn int-default (ctd Step (tvar 45)))" fillcolor="#e3efe0"];
  up0 [label="codexir @ U57\n(fn int-default (ctd Step (tvar 16)))" fillcolor="#fbe9e0"];
  up1 [label="codexir + the fix\n(fn int-default (ctd Step (tvar 45)))" fillcolor="#e3efe0"];
  src -> ours; src -> up0; src -> up1;
  ours -> up1 [style=dashed label="byte-identical" dir=none];
}
```

The measurements that ride with the PR are the same shape as PR 139's: the
compiler self-hosts to convergence in one round, the QEMU fixed point holds,
and a census of all 1,269 corpus programs through a `codexir` carrying the fix
says exactly which programs change a byte and how. The pin is a test unit the
zig plug refuses before and prints after; the fidelity instrument cannot see
this shape, because a stale variable is legal-looking, and it says so in the
PR rather than pretending otherwise.

<style>
figure.ast { margin: 20px 0; text-align: center; }
figure.ast svg { max-width: 100%; height: auto; }
.dot-error { color: #a00; font-family: monospace; white-space: pre-wrap; }
</style>
<script src="/assets/viz-standalone.js"></script>
<script>
Viz.instance().then(function (viz) {
  document.querySelectorAll('code.language-dot').forEach(function (code) {
    var pre = code.closest('pre');
    try {
      var svg = viz.renderSVGElement(code.textContent);
      var fig = document.createElement('figure');
      fig.className = 'ast';
      fig.appendChild(svg);
      pre.replaceWith(fig);
    } catch (e) {
      var err = document.createElement('div');
      err.className = 'dot-error';
      err.textContent = 'graphviz: ' + e.message;
      pre.appendChild(err);
    }
  });
}).catch(function (e) { console.error('viz load failed', e); });
</script>
