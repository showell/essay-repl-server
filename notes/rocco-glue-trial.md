# roc-odin-glue on the Safari spike: a trial

*2026-11-06. roc-odin-glue 08190ba (Rocco 6a436bf pins 12b321d, which has the same files), Roc nightly-2026-11-03-34bd006, Odin dev-2026-11a, roc-apps master 7bd34b3, headless Chromium 1140 on SwiftShader. Sources are in `~/showell_repos/odin-wasm-trial/`, branch `rocco-glue`, no remote.*

## Verdict

**It works, and the wasm32 mode really is mechanical.** With a patch of 32 added and 30 removed lines, the glue runs on our pin and our platform, and its generated Odin replaces the spike's hand-copied reader and refcount code. Hand-written host code goes from 1,020 lines to 859, which is 161 fewer.

Safari's result didn't change at all. All 119 sampled frames agree with the generated JS reader, and every digest, vertex count and live-block count equals the old host's. All 18 PNGs from the judge are byte-identical to the old host's.

**The patch itself isn't one Braeden could take.** It flips the glue to 32-bit rather than adding a mode, and Rocco needs 64-bit. The finding is worth having; the diff would need redoing first. Nothing was sent or drafted.

## What ran, and what it does

`glue/` in Rocco's tree is an empty submodule, so the code is in a separate repo, https://github.com/Pixelsprout/roc-odin-glue. I cloned that one repo and no other submodule.

The only file I ran is `OdinGlue.roc`, 1,039 lines, and I read all of it first. Its SHA-256 starts c1876196.

- It reads the type table the compiler hands it. Its nine imports are all from the compiler's built-in `glue` platform.
- It writes nothing itself. It is one pure function that returns one file, `roc_platform_abi.odin`, and the compiler writes that into the folder I named.
- It spawns nothing. It has no effects at all, and its only non-ASCII characters are two em dashes in comments.

So it does nothing outside generating source. It ran through our own pinned `roc glue`. I didn't read the compiler's code that runs a spec; it is the same path `JsGlue.roc` takes on every page build.

I ran no build script, engine, install step or example. `example/check.sh` is in that group, so the glue's own tests did not run. `build.sh` on the branch refuses any `OdinGlue.roc` but the one I read, and I checked that it does.

## Question 1: our pin, our types, wasm32

Unpatched, it compiled on our pin, 23 days newer than the one it was verified on, and needed no change for that. Then it stopped at its own deliberate crash:

    OdinGlue: no Odin spelling for unit (type id 33)

That is the `{}` argument of `init`. Its README says `{}` is supported only as a return type. It has nothing to do with pointer width.

| Part of the patch | Removed | Added |
|---|---|---|
| Layout reads, `size64` to `size32` and the like, by `sed` | 23 | 23 |
| Header comment and `size_of(uintptr)` assert | 3 | 3 |
| `odin_package`, which its README says to edit anyway | 1 | 1 |
| Skip `{}` arguments in the foreign block, not a width matter | 3 | 5 |
| **Total** | **30** | **32** |

The width change needed no logic. The rules in the generated helpers are written with `size_of(uint)` and `size_of(int)`, so they follow the target. I checked them against `list.zig` and `utils.zig` at our pin: the low-bit slice tag, the `n << 1` capacity, header sizes, allocation alignment, and 0 for static data all match.

The output is 763 lines: 185 asserts, 153 aliases, 76 blank, and 28 types among the rest. It runs in 2.2 s. All 185 asserts hold on `js_wasm32`, and it passes `-vet -strict-style`.

I expected one more bug that wasn't there. The glue's helper `roc_release` has the same name as our platform's foreign `roc_release`, but the helper is `@(private="file")`, and Odin keeps those in a separate scope. The compiler accepted it, and I confirmed that check could fail by planting a wrong assert.

## Question 2: does Safari still run?

Yes. The old numbers are from rerunning the unchanged spike today, and they match the spike's note.

| Check | Old host | Generated |
|---|---|---|
| Frames agreeing with the JS reader, across 12,000 steps | 119 of 119 | 119 of 119 |
| Shapes in those frames | 233,048 | 233,048 |
| Live blocks, lowest and highest | 102, 2,948 | 102, 2,948 |
| Pages at the end | 191 | 191 |
| PSNR against canvas, six steps, MSAA | 43.48 to 47.26 dB | the same at each step |
| PSNR, six steps, no AA | 36.51 to 39.81 dB | the same at each step |
| WebGL and canvas PNGs | | 18 of 18 byte-identical |
| Space, right arrow, J on the live page | pass | pass |
| Wasm size | 761,505 B | 761,831 B (+326) |

Three further checks, since agreement alone proves little:

1. **The digest can still fail.** I swapped the numbers of `Flat` and `Glow` in the generated file, once. All 185 asserts passed, as its README warns they would. The digest disagreed on every frame tried, 0 of 10, with 1957223531 against 3998923035 at step 3000, and PSNR fell to 9.35 dB. The plant is gone.
2. **The generated decref works on wasm32.** The branch only uses `roc_incref_box`, because Roc still frees each frame. So I built a variant where `roc_list_decref` frees it instead. Live blocks, digests and all PNGs matched the old host exactly, in all three apps. It costs another 1,329 bytes of wasm in Safari.
3. **`Blend` and `Image` are covered.** Safari sends neither. On Breakout and the Workshop, 15 of 15 frames agreed, digests and live blocks matched the old host, and 9 of 9 PNGs were byte-identical, in both the normal build and the decref variant. Breakout's frames carried `Blend` at 3 draw calls, and the Workshop's carried `Image`.

I kept Roc's `roc_release` on the branch. Replacing it would add wasm and save no lines.

### Lines

| File | Before | After |
|---|---|---|
| `host/frame.odin` | 154 | 17 |
| `host/roc_abi.odin` | 144 | 117 |
| `host/digest.odin` | 98 | 101 |
| `host/painter.odin` | 419 | 419 (19 edited) |
| `host/gl.odin` | 205 | 205 |
| **Total** | **1,020** | **859** |

`digest.odin` grew because `Pieces` now has its own case: the old reader read it as `Poly`, while the generated one spells out `tris`. `build.sh` gained 11 lines, and the patch file is 168 lines of diff.

### What happened to the note's list of silent risks

| Copied by hand in the spike | Now |
|---|---|
| The list header | Generated |
| The refcount word, 0 meaning static | Generated |
| The plain add for incref | Generated, also not atomic |
| All of `frame.odin`: field order, tag numbers, tag place | Generated on every build |
| Masking a data pointer's low two bits | **Lost.** See below |
| The size prefix for `roc_dealloc` | Stays. It is our allocator's, not a Roc layout |

The generated file is rebuilt on every build, so it can't go stale the way the glue's README warns. A renamed field or a new tag now stops the build, because the painter's and digest's switches must cover every tag. `bench.js` still has its own hand-written tag numbers.

## What's worse

- **The tag mask.** Roc's `increfDataPtr` strips the low bits of a data pointer, and the spike did too. The generated `roc_incref_box` doesn't. Fact: nothing went wrong in any run. Guess: this is safe, because Roc's comment says those bits are for recursive tag unions and a model is a plain box.
- **Names.** The generator defines a shape under the first path that reaches it, so `Rgba` is `Roc_Frame_Disc_Fill_Ellipse_C0`. Each host alias in `frame.odin` goes through another generated path, such as `Roc_Frame_Poly_Fill_Flat`, so a new tag won't move it. It reads worse, and it needs that convention.
- **Extra steps in the reader.** It is now `shape.payload.poly`, not `shape.poly`, which is where the 19 painter edits went.
- **Context.** The generated helpers use Odin's calling convention, so `borrowed` builds a context on every call. I didn't measure the cost. Each judge round here was 1, so this trial says nothing about speed.

## Not tested

- Any real GPU, as before.
- Whether the 64-bit output still works. I never ran it after the unit fix.
- `roc_list_from_slice` and everything else that passes a value into Roc. This host never does.
- Strings. The platform has no `Str`, so none of that code was emitted.
- Whether any frame contained a seamless slice, so that branch of the decref may never have run.
- Breakout and the Workshop with input. They ran with none, and the Workshop's results were the same at every step, so that frame looks static.
- Any Roc pin other than ours, including Rocco's 10-11.

## Question 3: would Braeden want it?

**Facts.** His glue README says 32-bit support "is additive work, not a redesign", so he expected this. `docs/RESEARCH-SCALING.md` says web is out of scope "while the glue is 64-bit only and sokol and Odin have no shared web path". That is two conditions, and this meets one. His roadmap's out-of-scope list names only the second: "Web builds until Odin and sokol have a shared web path." He wrote both pull requests in the glue repo, and it has 1 star and no forks.

**My judgment.** I think he might want the capability and wouldn't want this diff.

- It replaces 64-bit, so as it stands it would break Rocco.
- A real version needs a width setting, a constant like `odin_package`, since `roc glue` passes no arguments. `AbiLayout` and `AbiFieldLayout` have width accessors and `AbiTagLayout` doesn't, so a few helpers are needed. My guess is a patch of about the same size.
- It would need a test that fits his `check.sh`. `odin check -target:js_wasm32` on the examples would pin the asserts, but the digest evidence here lives in our harness.
- It unblocks nothing for him yet, because sokol's web path is the larger piece. So I'd expect it to be welcome but not urgent. That is a guess about him.

The unit-argument fix is separate and smaller, and he could take it alone, though his README documents that limit as a choice, so it may be deliberate. The missing tag mask is a short question rather than a patch.

## Where this leaves the spike

Item 2 of the spike's "what a real engine needs next", a generated reader, is done on this branch, with Roc's layout now read from the compiler. The branch needs a clone of roc-odin-glue at 08190ba, as its README says. The clone from this trial was in a scratch folder.
