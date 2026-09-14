# How rocemit threads the device, memory and machine: a cold review

A fresh agent with no history in this work read `rust-codex-compiler` at
5ede0f4 (2026-09-14) to answer Steve's question: how many places does the
emitter thread a value like `Machine` through every Codex function that
reaches it, is that one pattern or several, and is there a better
generalization? It was read-only: it ran rocemit on single units and nothing
else. This is its report, lightly edited. Line numbers are in
`src/roc_emit.rs` unless a file is named.

## Summary

1. **One pattern, three settings.** Device (the GPU kernels, `f943473`,
   2026-09-12) came first; Mem followed the same day (`37a5abb`, "threaded like
   a device"); Machine on 09-13 (`b756062`). All three run through one code path,
   switched by a `state` string. They differ only in the trigger (a type, or a
   scan of who calls whom) and in their door table. Safari threads nothing in
   the emitter.
2. **Roc's own effects are genuinely different.** `=>` arrows and `!` names
   answer the same question ("this property must reach every caller"), but the
   Codex checker has already written the effect label onto every caller's type,
   and Roc does the plumbing itself. The emitter only picks the spelling.
3. **The ten "a function value carries no state" refusals are one missing
   feature**, a function value that is generic over whether it touches the
   outside world. The fix would copy each higher-order definition for the kind
   of function it is handed: roughly 300 to 500 lines. It would unlock none of
   the ten, because every one of those units also hands a lambda to
   `process-spawn`, which has no door.
4. **Sign-off on the technique**, with four tidy-ups worth doing: one door
   table (door facts live in four places today, and every door commit edits
   them), a state enum, one "bind the pair" helper, and reconciling three "does
   this touch the state" tests that disagree about heap marks.
5. **One small change might move the ledger:** a constant with an effect
   (`x : [Console] T`) as a `{} => T` function, which the state mechanism
   already does for a constant `[Device] T`. Six units hit that refusal; how
   many would then pass is not checked.

## 1. Inventory

### A. The threaded value: Device, Mem, Machine

**Which one a unit uses** is the field `state` (687), chosen when the
emitter's context is built (778-851). There are two triggers:

- **Device, from the type.** `has_device` (1207-1222) looks for the `Device`
  label on any arrow, or on a constant's effectful type. The doors are the
  operations the chapter declares under `effect Device` (789-803). A kernel
  unit is also written in 32-bit integers and floats (804).
- **Mem and Machine, from a closure over calls.** A definition joins if its
  body names a builtin in `MEMORY_OPS` (44) or `MACHINE_OPS` (58), or names a
  definition that already joined, repeated until nothing new joins (809-851).
  The state is Machine if any machine builtin appears (828, 843). The opening
  is left out (846) and builds the state itself: `Mem.new(...)` or
  `Machine.boot!(args, effects)` (1573-1579).
- **Why a closure is needed at all:** Codex types the memory builtins as pure.
  `peek-byte` and `poke-byte` carry no effect (`builtins.rs:367-368`), while
  the port, block and MMIO builtins carry `Device.Port`, `Device.Block` and
  `Device.Mmio` (`builtins.rs:365, 369, 373, 397`). One closure covers both.

**What all three emit:**

- A threaded definition takes the state first and answers `(State, T)`
  (`def` 1450-1464, `device_signature` 1077-1085).
- The body is threaded statement by statement (`eff_expr` 1767, `eff_match`
  1879, `eff_let` 1911).
- Doors go through `eff_call` (1949-2123): Device operations at 2100-2122,
  memory at 2034-2098, machine doors (arity and `!`) at 2007-2033.
- The state's successive names are `dev`/`mem`/`machine` plus a number (1698,
  1722), and the last one is marked unused (719).

**Only for Mem and Machine**, because Codex lets a poke sit inside an
expression:

- The call is lifted into a binding ahead of the expression (`hoist`, 702,
  1755).
- The expression emitter switches on `by_closure() && dev.is_some()` for
  short-circuit `and`/`or` (2157), `if` (2214), `match` (2237), `let` (2254), a
  name (2347) and a call (2538).
- A heap mark is the bump pointer when memory is threaded (`heap_live` 695,
  1427, 1564; `Mem.mark`/`release` 1992-1999), and 0 otherwise (2375, 2680).

**Nine places branch on the `state` string:** 495-499, 1081, 1158, 1170-1174,
1548, 1573, 1699-1703, 1710, 1968-1972.

**Refusals it produces:**

- "a function value ... carries no state" (1962-1977): 10 units.
- "an effectful argument", Device only (1955): 0 units.
- "a match guard that touches memory" (1895).
- A name spelled like the state (1713).
- "an opening scoped to ..." under Machine (1548-1553): 4 units.

### B. Roc's native effects: `=>` and `!`

**Trigger:** the effect labels on Codex types. The checker has already carried
them up to every caller, so no closure is needed.

- `effect_left` (1129-1146) keeps the labels the state does not answer.
- What the state answers is `threads` (1169-1175): `Device` for kernels;
  `Device.*`, `Capability` and `Network.*` for Machine; nothing for Mem.
- `takes_bang` (1156-1162) feeds the set of `!` names (906), which `def` (1429)
  and `def_ref` (925) read.
- `signature` (1062) and `fun_parts` (1042-1059, for function types inside
  annotations) choose `=>`.

**Emission:** a Console act is a plain block (2397), `print-line` becomes
`line!` (2921), and the opening becomes `main!` (1539).

**Where A and B meet:**

- Under Machine every threaded definition is `=>` (1081, 1158).
- Some doors are both threaded and a Roc effect, by a hand-written name test
  (2021-2031) that repeats the `!` already on the signatures in roc-apps
  `machine/roc/Machine.roc`.

**Refusals:**

- An effectful function handed to a pure parameter (2568-2597): 1 unit,
  `effect-map-effctx`.
- A constant with an effect (`arrows` 1120-1122 unwraps it only when the state
  carries the label; otherwise `ty()` fails at 1036): 6 units, `cce-tier1`,
  `mask-ops`, `vec-select`, `effect-value-poly`, `handler-smoke`,
  `location-sensors-stub`.

### C. Related, but not this pattern

- `effect_scope.rs` is the checker's capability-scope check. Its only link to
  the emitter is `opening_effects` (1510), which becomes `Machine.boot!`'s
  capability list.
- Hand-written threading in roc-apps, which is likely what "something similar
  with safari" remembers:
  - `safari/roc/SafariApp.roc`, the gallery and the games keep a boxed model
    in the platform.
  - `basic/roc/Machine.roc` threads a BASIC machine by hand.
  - safari-codex's RiderState is threaded by the Codex source itself.

  None of these is emitter machinery.

### Duplication

- **D1. Three "touches the state" tests disagree:**
  - the closure's builtin set (810-812) has no heap marks;
  - `is_effectful` (1667-1684) is shallow and includes heap marks when memory
    is threaded;
  - `has_effect` (1741-1751) looks inside the whole expression and excludes
    them.

  **By reading, not reproduced on a unit:** with memory threaded, `let r =
  __heap-restore h in <pure>` in a pure position skips the `let` switch (2254,
  because `has_effect` is false). It goes through the plain let path to
  `builtin` (2680) and becomes `0`, so the rewind is dropped. Likewise, a
  definition whose only state use is a heap mark never joins the closure.
- **D2. "Bind the pair, move to the next state name"** is written six times on
  the expression side (2171-2174, 2225-2228, 2243-2246, 2256-2259, 2350-2353,
  2543-2546) and three times on the statement side (1800-1802, 1815-1819,
  1925-1929). The `by_closure() && dev.is_some()` gate repeats six times.
- **D3. Door facts live in four places:**
  - the builtin names (44-88);
  - the arity table (2007-2018) plus the `want()` checks (2054-2098);
  - the `!` name test (2021-2031);
  - the Codex-to-Roc name rule, `replace('-', "_")` (2032).

  Machine.roc has its own `!` signatures besides. The door commits `4718fd7`,
  `b886af1`, `4d4e3aa` and `1b41722` each edited the builtin lists and two to
  four places in the emitter.
- **D4.** The nine string branches listed under A.
- **D5. "Is this row an effect" is computed five ways:** `fun_parts` (1049,
  which ignores `threads`), `effect_left` (1137), `has_device` (1213), `apply`
  (2580-2586) and `opening_effects` (1519).

## 2. One pattern or several?

| | lowered to a threaded value | lowered to a Roc effect |
|---|---|---|
| **trigger: a label on the Codex type** | Device | Console and every other label |
| **trigger: a closure over builtins** | Mem, Machine | (none) |

**Device, Mem and Machine are one pattern.** Each is a set of doors plus every
definition that reaches them, taking the state first and answering it back,
with the body as blocks that answer a pair.

- The trigger differs only because Codex types memory access as pure.
- Mem and Machine add the lifting only because Codex lets a poke sit where a
  Device operation may not.
- Machine is Mem with a bigger record and a few doors that are also host
  effects.

It is implemented once already; "threaded like a device" is literally true in
the code.

**Roc effects are a different pattern.** The question is the same, but none of
the machinery is: Codex already labels every caller, Roc threads the world
itself, and there is no state name, pair or lifting. The emitter decides one
`!` and one arrow. The two meet only where `effect_left` subtracts what the
state answers, and where Machine's host doors are both.

## 3. Generalizations

### G1. Let a function value carry the state (or an effect): not now

**The idea:**

- A partial application of a threaded definition becomes a closure `|s, x|
  f(s, captured..., x)`.
- A higher-order definition that receives one is copied with that parameter
  threaded. The copies are keyed by definition and threaded positions, and a
  copy calls the parameter with the state.
- The same copying would handle an effectful function handed to `list-map`.

**Types cannot drive it for memory.** `web-mux-feed`'s `obs : Text -> Integer`
(`codex/os/net/WebServer.codex:333`) is pure in Codex, and GopWeb hands it a
lambda that pokes (`apps/works/GopWeb.codex:177`, `gopweb-log` at 87-95). So
the pass would follow where each function value goes. A function value stored
in a record or a list, or returned, would still be refused.

**Size and risk:**

- A new pass of about 300-500 lines, plus changes to `apply`, `partial`,
  `eff_call` and definition naming. Medium to high risk: it touches every
  threaded path.
- A chapter's text would grow copies that exist only in some units. That goes
  further than the rule that a module's text must not depend on which spec is
  attached (975; `rocemit.rs:60-62`).

**It unlocks none of the ten:**

- `spawn-reuse`, `nested-spawn`, `proc-state-running` and `spawn-memo-table`
  call `process-spawn`.
- The six desk units cite GopDesk, which cites GopWeb, whose `gopweb-start`
  (189) is `process-spawn (\x -> gopweb-service blk x)`.
- `process-spawn` has no case in `builtin()` (2635-2927), and its type carries
  `[Concurrent]` (`builtins.rs:408`), which the Machine does not thread.
- **The desk tests refuse on GopWeb definitions they never call.** None of the
  six mentions `gopweb`, and GopDesk never calls `gopweb-start`. They refuse
  because whole chapters are emitted, and `emit_modules` returns the first
  refusal (529) before it prunes unreached modules (576).

At most G1 would unlock `effect-map-effctx`. The levers for the ten are a
process model in the Machine and, for the desk six, a separate decision about
whether an unreached definition may refuse without refusing the unit. That
cuts against "refuse what is not built", so it is Steve's call.

### G2. One door table (recommended)

**The change:**

- Replace `MEMORY_OPS`, `MACHINE_OPS`, the arity match, the width table, the
  `!` test and the Device operation match with rows: Codex name, state, Roc
  function, arity, fixed extras such as a width, host effect or not.
- `eff_call`'s memory and machine block (1988-2098, about 110 lines) becomes a
  lookup plus a few irregular cases (heap marks, the argument order of
  `atomic-*`), and the closure's builtin set comes from the same rows.

**Size and risk:** about 80 fewer lines, low risk; a spelling slip fails the
ladder or the gpu gate.

**What it gets:** no behaviour change. A new door becomes one row instead of
three or four edits (eight door commits in two days).

**One side effect:** if heap marks become rows, a definition whose only state
use is a heap mark starts being threaded. That fixes half of D1 and moves
output, so it needs a ladder run.

### G3. A state enum instead of a string

`enum State { Device, Mem, Machine }`, with the base name, the module,
`threads`, whether definitions are always `=>`, and the opening's constructor.

- It gathers the nine branches into one place, and a fourth state becomes a
  compile error.
- About 40 lines moved, trivial risk. Worth doing only with G2.

### G4. One bind-the-pair helper, and drop the `by_closure()` gate

- A helper replaces the six expression-side copies, and a sibling covers the
  three statement-side ones.
- Dropping the gate lets kernels use lifting too, which deletes the Device-only
  "an effectful argument" refusal (0 ledger hits; kernels are not in the
  ledger). The gpu gate must be rerun.
- About 30 fewer lines, low risk.
- Fold `is_effectful` and `has_effect` into one test with a shallow/deep
  parameter, which is where D1 gets settled.

### G5. A constant with an effect as a `{} => T` function (small)

- `test-lt : [Console] Nothing = act ...` (`mask-ops.codex:5`) refuses today.
- The fix is to emit `test_lt! : {} => {}` and call `test_lt!({})` at each
  reference: about 30 lines, low risk.
- It is worth one ladder run, but later refusals hide behind this one: for
  example, `mask-ops` also calls `vec-splat`, and `handler-smoke` probably
  needs `handle`.

### Sign-off

The core technique is sound and already generalized where the code allows.

- State-passing is the standard lowering for a pure target, and here it is one
  path for all three states.
- The closure is the only trigger available without re-inferring effects Codex
  does not write down.
- Handing Roc effects to Roc is right, and it is correct to keep that apart.
- The refusals are honest limits: Roc has no effect polymorphism, and the one
  generalization that removes them (G1) pays off only after `process-spawn`
  has a model.

The work worth doing is housekeeping (G2 with G3, G4 including D1) and the G5
experiment.

## 4. Blind spots

- **Nothing was run** but rocemit on single units: spawn-reuse,
  effect-map-effctx, scope-console, fat16-list, cap-heap-poke-pure, mask-ops,
  handler-smoke, desk-span, one kernel. A unit shows only its first refusal, so
  every "unlocks" count is an upper bound.
- **D1 is from reading the code**, not from a unit that shows it.
- **Not confirmed:** whether Roc accepts a `->` function where `=>` is
  expected. If it does, the `list-map` refusal might dissolve by writing
  higher-order parameters as `=>`, at the cost of `!` spreading to callers.
- **The GPU kernels are not in the ledger**; one kernel's output was seen, not
  the 46-kernel gate.
- **Not read closely:** 1240-1420 (type definitions and methods) and 2989-3056
  (the fold rewrite). A grep found no state references in either.
- **Other emitters** (the zig and wasm transpilers, upstream's C# ZigEmitter)
  were not examined beyond git logs.
