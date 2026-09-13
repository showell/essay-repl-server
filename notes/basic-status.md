# BASIC in Roc: where it stands

roc-apps `master`, at 5a6f199. **Parked.** The summary is
[the essay](roc-basic-interpreter.md).

## The suites

- **NBS: 195 pass, 0 fail, 13 unjudged** of 208. An unjudged program prints
  no verdict of its own.
- **Games: 55 of 99** match basic101's captured output byte for byte. The
  games come from basic101's own tests, listings and captures together.
- **The fast path agrees with the full evaluator** on every program
  (`basic/check-fast.sh`).

## What runs, precisely

| program | built by, from | mode | target | used for |
|---|---|---|---|---|
| the Roc compiler | roc-lang's nightly binary, `nightly-2026-09-11-793f9d8` | as published; we do not build it | x86-64 | every build below |
| `basic-run` | the Roc compiler, from `BasicRun.roc` (`Machine.roc`) | `--opt=dev` | x86-64 | NBS and games, one process a program |
| `basic-check` | the Roc compiler, from `BasicCheck.roc` (`Machine.roc`) | `--opt=dev` | x86-64 | the fast-path check |
| `basic.wasm`, the page | the Roc compiler, from `BasicApp.roc` (`Machine.roc`) | `--opt=dev` | wasm32 | the browser, preview :9203 |

All three are the same interpreter. The old one (`Basic.roc`, `Pages.roc`) is
deleted. **No LLVM until the next major checkpoint.**

## The machine

What never changes during a run is `Parse.Program`. What a statement changes
is `Machine.M`. The devices (terminal, screen, memory, framebuffer) are
`Devices.D`, behind one reference. INPUT allocates 5 times a statement; the
ladder holds it there.

## When we return

1. **Better coverage on the games.** life, poetry, splat and superstartrek are
   among the 44 that still differ: interpreter work, one game at a time.
2. **The ECMA-55 load checks**, 150 to 370 ms a program, the largest cost left
   in NBS.

Numbers: [basic-timings](basic-timings.md).
