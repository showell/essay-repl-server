# The cite resolvers: a lay of the land

*2026-09-13, at Update 60 (`9fff850c`). Groundwork for moving resolution into
the Rust compiler. The ledger this summarises is cobblestone-qemu
`FINDINGS.md` section 3.*

A **cite** (`cites Foreword chapter ListUtils`) names a chapter a program needs.
A **resolver** turns a program into a **unit**: the program plus every chapter
its cites reach, dependencies first, each once. Everything downstream (the seed,
our native tools, the Rust front end) compiles a unit, never a bare file.

Four pieces of code in our chain resolve cites, and they do not agree on one
question: *is this chapter already there?*

## Who calls which resolver

```dot
digraph {
  rankdir=LR; bgcolor="transparent";
  node [shape=box style="rounded,filled" fontname="Helvetica" fontsize=11];
  edge [color="#666666"];

  subgraph cluster_r {
    label="the resolvers"; fontname="Helvetica"; fontsize=12; color="#bbbbbb";
    R1 [label="Resolve-PlugForewords\nplug-build-lib.ps1" fillcolor="#e8eefc"];
    R2 [label="Resolve-CiteOrder\nquire-map.ps1" fillcolor="#fde9d9"];
    R4 [label="its own walk\nconcat-codex-self.ps1" fillcolor="#f2f2f2"];
    R3 [label="bundle::resolve / load\nrust-codex-compiler" fillcolor="#e6f4e6"];
  }

  subgraph cluster_up {
    label="upstream callers"; fontname="Helvetica"; fontsize=12; color="#bbbbbb";
    compile [label="build/compile.ps1\n(every seed compile)"];
    app [label="build/bundle-app.ps1"];
    btp [label="Build-TranspilerPlug\n(plug builds)"];
    self [label="compiler self-bundle"];
  }

  subgraph cluster_ours {
    label="our callers"; fontname="Helvetica"; fontsize=12; color="#bbbbbb";
    qb [label="cobblestone-qemu\nsubjects/bundle_*.ps1"];
    qa [label="cobblestone-qemu\nassemble_unit.ps1"];
    zb [label="codex-zig-transpiler\nsource/bundle_*.ps1"];
    zr [label="codex-zig-transpiler\nsource/resolve_unit.ps1"];
    wb [label="codex-wasm-transpiler\nbundle_codexwasm.ps1"];
    sx [label="safari export.py\n(bundle one)"];
    sr [label="safari run.sh\n(codexrun on a raw spec)"];
    arms [label="curated arms\n(codexrun, irdump on units)"];
  }

  btp -> R1; qb -> R1; zb -> R1; wb -> R1;
  compile -> R2; app -> R2; qa -> R2; zr -> R2;
  self -> R4;
  sx -> R3; sr -> R3; arms -> R3;
  btp -> compile [style=dashed label="then" fontsize=9];
  qb -> qa [style=dashed label="then" fontsize=9];
  zb -> zr [style=dashed label="then" fontsize=9];
}
```

Two things stand out. **Most units pass through two resolvers**: a bundler
(R1) assembles them, then the seed's compile step (R2) resolves them again. We
learned that the hard way: our transports skipped R2 until Update 59 broke them.
And **the Rust side is its own island** (R3). Nothing upstream calls it, and it
calls nothing upstream.

## When is a cited chapter "already there"?

```dot
digraph {
  rankdir=TB; bgcolor="transparent"; compound=true;
  node [shape=box style="rounded,filled" fillcolor="#ffffff" fontname="Helvetica" fontsize=10];
  edge [fontname="Helvetica" fontsize=9 color="#666666"];

  subgraph cluster_1 {
    label="R1  plug-build-lib"; fontname="Helvetica"; color="#8aa2d6";
    a1 [label="cite Q chapter N"];
    a2 [label="a chapter named N\nunder ANY prefix?" shape=diamond];
    a3 [label="skip" fillcolor="#e6f4e6"];
    a4 [label="add as Q--N"];
    a1 -> a2; a2 -> a3 [label="yes"]; a2 -> a4 [label="no"];
  }

  subgraph cluster_2 {
    label="R2  quire-map (per-directory quire, e.g. Foreword)"; fontname="Helvetica"; color="#d69a6a";
    b1 [label="cite Q chapter N"];
    b2 [label="a Q--N header\n(SeedSeen)?" shape=diamond];
    b3 [label="skip" fillcolor="#e6f4e6"];
    b4 [label="is Q/N.codex\na file?" shape=diamond];
    b5 [label="add as Q--N\neven if N is present\nunder another prefix" fillcolor="#fde9d9"];
    b6 [label="N present under\nany prefix?" shape=diamond];
    b7 [label="skip" fillcolor="#e6f4e6"];
    b1 -> b2; b2 -> b3 [label="yes"]; b2 -> b4 [label="no"];
    b4 -> b5 [label="yes"]; b4 -> b6 [label="no"]; b6 -> b7 [label="yes"];
  }

  subgraph cluster_3 {
    label="R3  Rust bundle.rs (the compiler's scoper rule)"; fontname="Helvetica"; color="#7fb27f";
    c1 [label="cite Q chapter N"];
    c2 [label="a Q--N header?" shape=diamond];
    c3 [label="skip" fillcolor="#e6f4e6"];
    c4 [label="chapters named N\nunder any prefix or none" shape=diamond];
    c5 [label="skip" fillcolor="#e6f4e6"];
    c6 [label="refuse:\nambiguous" fillcolor="#f4dede"];
    c7 [label="a checkout: the file's tree,\nor a quires.tsv line?" shape=diamond];
    c8 [label="refuse" fillcolor="#f4dede"];
    c9 [label="add as Q--N"];
    c1 -> c2; c2 -> c3 [label="yes"]; c2 -> c4 [label="no"];
    c4 -> c5 [label="one"]; c4 -> c6 [label="several"]; c4 -> c7 [label="none"];
    c7 -> c8 [label="no"]; c7 -> c9 [label="yes"];
  }
}
```

| | presence is keyed on | adds ListUtils and Tuple unasked | a chapter it cannot find |
|---|---|---|---|
| **R1** plug-build-lib | the bare chapter name, asked FIRST (our PR 69) | no | exit 3 |
| **R2** quire-map | `Quire--Name` first; the bare name only when the file is missing. The manifest quires `Codex`, `Emit` and `Semantics` ask the bare name first | yes, every unit (Update 36) | throws |
| **R3** Rust | `Quire--Name` first, then the ONE chapter of that name under any prefix or none; several is refused. The compiler's own rule (ChapterScoper `find-slug-for-cite-name`) | yes, every unit | refuses. The checkout is the file's tree or a `quires.tsv` line, never a variable |
| **R4** self-bundle | `Quire\|Name` in its own queue, Foreword and Math only | no, though R2 adds them at compile | skips silently |

## What the disagreement costs, so far

**3a. Double bundling (R1 against R2).** A foreword a bundler lists under
another prefix (`Parsmi--Maybe`) satisfies R1, and R2 adds it a second time. It
hit codex-zig-transpiler's subject once: five chapters, 2,749 lines, now fixed
on our side. Upstream's own callers cannot hit it. R4 prefixes forewords with
their own quire, and `bundle-app` starts from a bare source.

**3b. The implicit pair is in every unit, and it shows.** fib uses neither `for`
nor a tuple, yet its unit carries both:

```dot
digraph {
  rankdir=LR; bgcolor="transparent";
  node [shape=box style="rounded,filled" fontname="Helvetica" fontsize=10];
  edge [fontname="Helvetica" fontsize=9];
  src [label="fib.codex\n14 lines" fillcolor="#ffffff"];
  unit [label="the unit R2 builds\nListUtils + Tuple + fib\n(+3,731 bytes)" fillcolor="#fde9d9"];
  ir [label="IR  1,214 -> 1,863 bytes\n+6 section names, +4 MkTup ctors,\n+4 Tup type defs, row ids +454" fillcolor="#fff4e0"];
  zig [label="zig  +24 lines:\nfn Tup2 .. fn Tup5\n(nothing else changes)" fillcolor="#fff4e0"];
  out [label="output: unchanged\n55, 610" fillcolor="#e6f4e6"];
  src -> unit [label="compile.ps1"]; unit -> ir [label="seed"]; ir -> zig [label="plug"]; zig -> out;
}
```

The answers do not change, so this costs transparency rather than correctness.
Pruning keeps type definitions and constructor lists, and the ids the checker
mints move, so anything keyed on ids or chapter lists sees a difference. The
QEMU checker was fooled by it once.

**R3's fallback is gone.** It re-resolved a short unit against `CODEX_ROOT`,
which `~/.bashrc` exported at an unrelated tree. Both the fallback and the
export are deleted; see below.

**3c. The scoper's bare-name fallback counts definitions** (read from code, not
measured). `find-slug-by-bare-name` answers only when exactly one entry
matches, and its cache holds one entry per DEFINITION. On that reading, a cite
that reaches its chapter by bare name finds nothing when the chapter defines
two or more names. `cite-override-quire.codex`'s chapter defines one. A single
experiment settles it: add a second definition and compile.

## What Rust resolution settled

R3 is rewritten (rust-codex-compiler `16e88f3`), and the four decisions came out
this way:

1. **The presence key is the compiler's.** A `Quire--Name`-only rule came first
   and refused too much:
   - the self-host subject, where `Parsmi--Build Settings` answers
     `cites Codex chapter Build Settings`;
   - all 128 curated and safari units, which carry a plain
     `Chapter: ListUtils`;
   - `cite-override-quire.codex`, which upstream's battery requires to
     compile.

   The scoper already had a rule for all three.
2. **The implicit pair is always added**, as `compile.ps1` adds it, so our
   headers can match R2's.
3. **The checkout is the file's own tree**, or a `checkout` line in the nearest
   `quires.tsv` for a project outside one.
4. **Gone:** `CODEX_ROOT`, `CODEX_QUIRES`, `CODEXC_RAW`. A file missing nothing
   is a unit and is read as it is.

Measured at U60, R3 beside R2 (`tools/resolver_agree.py`):

    1,293 programs under codex/test, apps/ out
      1,291  the same headers, in the same order
          2  both refuse: errors/missing-cite, errors/unregistered-quire-cite
    every unit the Rust arms read     unchanged, byte for byte
    the Roc ladder, 1,032 programs    ledger unchanged, 496 pass

The one case where R3 and R2 must differ is a Foreword chapter carried under
another prefix, and `codex/test` holds none. The check would list one as
"different chapters".
