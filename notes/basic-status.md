# BASIC in Roc: where it stands

Branch `basic-machine` in roc-apps. Not merged.

## The suites

- **NBS: 195 pass, 0 fail, 13 unjudged** of 208, graded on the current
  interpreter after refetching the corpus. An unjudged program prints no
  verdict of its own.
- **Games: 55 of 99** match basic101's captured output byte for byte. The
  games now come from basic101's own tests, listings and captures together,
  and life2 passes because of that.
- **The fast path agrees with the full evaluator** on every program
  (`basic/check-fast.sh`).

## What runs, precisely

| program | built by, from | mode | target | used for |
|---|---|---|---|---|
| the Roc compiler | roc-lang's nightly binary, `nightly-2026-09-11-793f9d8` | as published; we do not build it | x86-64 | every build below |
| `basic-run` | the Roc compiler, from `BasicRun.roc` (`Machine.roc`) | `--opt=dev` | x86-64 | NBS and games, one process a program |
| `basic-check` | the Roc compiler, from `BasicCheck.roc` (`Machine.roc`) | `--opt=dev` | x86-64 | the fast-path check |
| `basic.wasm`, the page | the Roc compiler, from `BasicApp.roc` (`Machine.roc`) | `--opt=dev` | wasm32 | the browser, preview :9203 |

All three BASIC programs are the same new interpreter. **No LLVM until the
next major checkpoint.**

## Done today

- **The machine is split.** What never changes during a run is
  `Parse.Program`. What a statement changes is `Machine.M`. The devices
  (terminal, screen, memory, framebuffer) are `Devices.D`, behind one
  reference. **Every statement is about a quarter cheaper, and P134 went from
  7.3 s to 5.4 s.** Same transcripts, same fast-path agreement.
- **The page runs the new interpreter**, built with the dev backend in about
  5 seconds: http://143.244.172.148:9203/basic/basic.html

## Next

1. **Your look at the page.** I checked that it builds and is served, not
   that it runs in a browser.
2. **Delete the old interpreter** (`Basic.roc`, `Pages.roc`) and `gen.py`,
   once the page is right, and merge the branch.
3. **The ECMA-55 load checks**, 150 to 370 ms a program, the largest cost left
   in NBS.

## Open

- **INPUT allocates 5 times a statement, not 3,** since the devices moved.
  Nothing else did. Two tries did not find why. Chase it, or accept it?
- life, poetry, splat and superstartrek still differ from basic101: that is
  interpreter work, one game at a time.

Numbers: [basic-timings](basic-timings.md).
