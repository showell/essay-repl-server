# Static dispatch in rocflight's checker: the design

*2026-09-26. The plan for making rocflight type a method call on a type variable the way roc does. Written before implementation, so it can be picked up after a break.*

## Why this is next

rocflight's checker gives a method call on a value of *unknown* type a result guessed from the method's name. Take `double_all = |it| it.map(|x| x * 2)`:

- **The result is always a list.** `map` is guessed to return a `List`, whatever `it` turns out to be.
- **The lambda's `x` never learns its type.** So the `2` in `x * 2` defaults to `Dec`, and `double_all([1.I64, 2])` prints `[2.0, 4.0]` where roc prints `[2, 4]`.
- **Over an iterator it is now refused.** Since "an iterator is its own type" (commit `0cbef22` on branch `iter-type-wip`), `double_all([1.I64, 2].iter())` is a type error where roc prints `[2, 4]`.

A `for` loop over an unannotated parameter has the same problem. It guesses `List`, so `total([1.I64, 2].iter())` is refused, and roc prints `3`.

All of these are one gap: rocflight has no static dispatch. The Iter commit stays unpushed until this closes it, so PR #25 never carries a known regression.

## What roc does

Researched from roc's source (`~/showell_repos/roc` @ d6312ed7) and confirmed with the 09-07 nightly. The memory file `reference_roc_static_dispatch.md` has the file:line citations.

- **A method call on an unknown receiver is a constraint, not a guess.** `it.map(f)` attaches `map : it, (c -> d) -> r` to `it`'s type variable. The lambda is checked once, with a fresh `c`, which the constraint's function type ties to `it`.
- **A constraint is checked when the variable becomes concrete.**
  - Two variables unified together pool their constraints. A method name on both sides unifies the two signatures.
  - A variable bound to a real type queues its constraints. A queue drain then looks up that type's method, instantiates it, and unifies it with the constraint. That one step types the lambda's argument and the result.
  - A type without the method gives "missing method".
- **Operators are constraints too.** `x * 2` is `times`, returning the receiver's type. That's why `double_all([1.I64, 2])` gets `I64` literals.
- **`for x in xs` is `xs.iter()`.** Over a `Str`, roc reports "missing method `iter`".
- **A generic function's constraints are its inferred `where` clause:** `a -> b where [a.map : a, (c -> c) -> b, c.times : …]`. Each call site gets its own copy.
- **A constraint that is never resolved is an error.** Only literals default (to `Dec`/`Str`); method constraints never do.
- **roc resolves every call site at compile time** (it monomorphizes). rocflight dispatches on the running value, so it needs only the *types* right, not new code generation.

## Where it goes in rocflight

The checker already has three per-variable side tables that travel through unification and instantiation: numerals (`numeral_vars`), string literals (`quote_vars`) and tag-union rows (`row_vars`). Constraints are a fourth, richer table: variable id → a list of `(method, function type)`.

| Step | Where | What |
|---|---|---|
| record | `synth`, the `Expr::Dispatch` arm: the receiver is a `TypeVar` | Replaces the name-table fallback (`builtin_result`). Synthesize the arguments; a lambda's parameters stay fresh. Build `receiver -> arg1 -> … -> result` in curried form, attach it to the variable, and return `result`. |
| record | `synth`, the `Expr::For` arm: the iterable is a `TypeVar` | Replaces "unify with `List(elem)`". Attach `iter : xs -> Iter(elem)`; the loop binds `elem`. |
| merge | `unify`, the variable–variable case, next to the numeral and row propagation | The bound variable's constraints move to the other one. A method name both have unifies the two function types, queued, not recursive. |
| resolve | `unify`, a variable bound to a concrete type | Queue `(constraints, type)`, and drain the queue when the outermost `unify` returns. For a type with a method block (a builtin module via `module_named`, or a nominal of the program's own), instantiate `declared(module, method)` and unify it with the constraint. If there is no such method, the error is "missing method", in roc's words. |
| generalize | `check_let` | Generalize the variables reachable *through* constraints too (`double_all`'s `c` and `d` appear in no part of `a -> b`). |
| instantiate | `instantiate` | Copy each generalized variable's constraints onto its fresh copy, through the same mapping. |

**Literals need nothing new.** Once the constraint resolves, the `x` in `x * 2` becomes `I64`, and the `2` comes with it through the numeral-copy machinery `instantiate` already has. That machinery decides a generic body's literal from what all its uses settled on.

## Three commits, stacked on PR #25

1. **Constraints on variables:** the table above. Records and tag unions stay lenient: a method on one is not checked. roc allows only derived methods there (`is_eq`, hashing, codecs, `map` on a tag union), and pinning that down is a later refinement.
   - **Failing test first**, every expectation from roc:
     - `double_all` over a list and over an iterator: `[2, 4]` both ways.
     - `keep_big = |xs| xs.keep_if(|n| n > 1)`: a list gives `[2, 3]`, and an iterator gives `<opaque>`.
     - `total` over a list and over an iterator: `3`.
     - `double_all("hello")` is rejected (missing `map`).
   - **This commit also closes the Iter commit's gaps,** so the two land on #25 together.
2. **Annotated `where` clauses become per-variable constraints.** Today they're one flat, program-wide list of method *names* (`where_methods`) with no signatures, and a promised method on a variable returns an unconstrained type. After this commit:
   - A body may call only what its `where` declares, typed by the declared signature.
   - A call site's argument must satisfy the constraint, as roc checks it: `describe(Bad)`, where `to_str : Bad -> I64`, is rejected when `Str` is required.
3. **Strictness to match roc:** a constraint that is never resolved, or a method on an unknown type outside any lambda, becomes an error. This goes last, and it is gated by the 581-program ported corpus, because it is the one step that can make rocflight refuse programs it runs today.

**Operators stay as rocflight types them today,** by unifying the two operands, unless the tests force the issue. roc's refusal to unify them only matters for user types such as `Duration * I64`.

## Gates, every commit

- `cargo test` in debug and release.
- The branch gates, about 6 minutes: `check_roc` 97/2, `check_examples` 19/0, `check_artifact`.
- The all-prs gates, about 7 minutes: the ported corpus 581/581, plus Fast Track on the interpreter with its times and peak memory appended to `~/build/rocflight/ft_timings.tsv`.
- The codex-emit gates, about 8 minutes: roc2rust 581/581, its own tests, and the round trip at 551/29/1.
- **A before-and-after of roc2rust's Fast Track translations.** Byte-identical Rust means the performance comparison with roc stands. Any difference means rerunning the 10-game roc-against-Rust comparison.
- **A cold review.**
