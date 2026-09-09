# WGSL/naga: what landed, when, and the one kernel still red

You thought the WGSL work might have been too late for Update 57. It was not. Here is the timeline, retraced from the commits and the GitHub thread, and the state of the kernels at the U58 candidate today.

## The timeline

- **2026-09-05** we opened **PR 129**, "wgsl plug: emit shaders Firefox accepts, all three causes." It carried three commits and the regenerated kernels; the PR comment records eye-testing `reflect.html` and `ssao.html` in a real browser over the tunnel.
- **2026-09-07** Damian landed it, with credit, ingesting it into Perforce (blu 22421, main 22423). His words: "Your `WgslEmitter.codex` was taken exactly." So the emitter change is upstream verbatim, not a paraphrase.
- **2026-09-08** he confirmed it **shipped in Update 56** (`6cd2ca1b`).

The thing that makes this confusing is the Update 56 abort. But "aborted" was about the release label and seed, not the commits: **Update 57 (`49fa9f27`) is built on top of Update 56**, so it carries U56's landings. I verified the cause-1 fix marker `wgsl-zero-text` is present in U57's `WgslEmitter.codex`. So the WGSL fix is in U57, and in our u58-candidate. It made the boat.

## The state at the U58 candidate

naga is Firefox's validator, run offline. Over every kernel in the u58 checkout:

- **U55, before any of this: 19 of 44 pass.**
- **u58 candidate today: 43 of 44 pass.**

The three causes PR 129 addressed:

- **Cause 1, a tail-call loop with no terminator.** Fixed and live. This was the big one, 25 files.
- **Cause 3, `bitcast` in a const expression.** Fixed and live.
- **Cause 2, a `ptr<storage>` as a function parameter.** Fixed for every file except one.

## The one still red: GlobeKernels

`GlobeKernels.wgsl` is the sole remaining naga failure at u58. Its `earth_shade_pixel` still takes `framebuf` and `tex` as `ptr<storage, array<i32>, read_write>` parameters, and naga refuses a storage pointer as a user-function parameter:

```
error: Function 'earth_shade_pixel' is invalid
  = Argument 'framebuf' at index 0 is a pointer of space Storage, which can't be passed
```

WGSL restricts pointer parameters to the function, private and workgroup address spaces; storage needs the `unrestricted_pointer_parameters` extension, which Tint (Chrome) implements and naga (Firefox) does not. So globe renders in Chrome and fails in Firefox, which is exactly the direction naga exists to catch.

This is the case the original diagnosis flagged as "real work, not a small fix": the emitter has to pass indices instead of pointers, or inline those helpers, rather than emit a storage-pointer parameter. PR 129's "all three causes" closed cause 2 for the other six files but left this one. It is the natural WGSL follow-up, and it is ours: the wgsl plug is ours to fix, the same way the zig plug is.

## The adjacent zig-plug owe, since it is the same shape

While retracing this I checked the sibling case. `a77ed493` on u58-candidate, "box every payload-carrying variant," fixes a zig-plug defect we own outright: we filed it as issue #121, then withdrew the issue saying it is ours to fix in the plug, not Damian's to guard in the compiler. It is not upstream, the one plug commit missing from both U56 and U57, and it is more serious than a shader that only Firefox rejects: at Update 56 it stops the zig build of the compiler itself. That fix is finished on u58-candidate and prepared for ingest; it is owed as a PR, and it is the strongest item in the outbound queue.

## Eye-testing

The u58 checkout is served on 9202 (loopback only). WebGPU needs a secure context, so it has to be reached over the tunnel, not the droplet IP:

```
ssh -N -L 9202:localhost:9202 steve@143.244.172.148
```

Then, in Firefox on Windows:

- the gallery: `http://localhost:9202/apps/gpushow/web/index.html`
- the globe, the one expected to fail: `http://localhost:9202/apps/globe/web/globe-codex.html`
- two that PR 129 fixed and should now render: `http://localhost:9202/apps/gpushow/web/reflect.html` and `.../ssao.html`

naga already says 43 of 44 pass, so the eye test is confirmation rather than discovery, and the globe is the one to watch fail.
