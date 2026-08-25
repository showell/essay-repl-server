# What run.ps1 actually does on this box

*2026-08-25*

The ergonomics queue carried a warning about the Codex tree's own plug
scripts: that `codex/plugs/*/run.ps1` starts a 3 GB guest without asking
our compute lock, and could therefore land on top of a running sweep and
turn it into thrash. This is the note that checks it. Most of the warning
was wrong, one part of it is worse than advertised, and there is a real
defect underneath that belongs upstream rather than in our queue.

Everything below was run, not read.

## What run.ps1 is

Upstream's way to run one plug over one source file. Two legs:

    run.ps1  ->  build/compile.ps1     .codex source  ->  IR-CCE
             ->  build/plug-run.ps1    IR  ->  the plug's output

Both legs need a virtual machine, because the Codex compiler and every
plug are Codex programs that boot as a kernel. 38 of the 56 plugs go
through `plug-run.ps1`, every one of them asking for `-MemMB 3072`. The
zig plug is one of the 38.

There are two VM hosts. `codex-vm.exe` is the primary and is
Windows-only. QEMU is the other, and `build/vm-config.ps1:14-19` says
plainly what it is for: "QEMU is the fallback and the only host on
Linux/WSL. Both paths are live."

This box is Linux.

## Leg one: it works, and it is a 3 GB guest

`build/compile.ps1` hardcodes `tools\codex-vm.exe` at line 209, but when
that fails it calls `Invoke-VmCompileFallback` (line 239), which is the
QEMU path in `vm-config.ps1:821`. So the compile leg is honest about
running on Linux, and it does:

    build/compile.ps1 -Src codex/plugs/test-input/record.codex \
        -Kernel seed/Codex.cdx -IrCce -Passes text-plug
    -> IR written, 4 seconds

Caught mid-run, the guest is exactly what the warning claimed:

    /usr/bin/qemu-system-x86_64 -accel tcg ... -m 3072 -kernel seed/Codex.cdx

Three gigabytes on an eight gigabyte box, started by something that
never asked our lock. That half of the warning is true, and it is the
half that matters, because this leg is the one that WORKS.

While it was up I asked our side what it could see:

    COMPUTE JOB RUNNING WITHOUT THE LOCK -- refusing beside:
      /usr/bin/qemu-system-x86_64 -accel tcg ...

So the protection is one-directional, and now precisely so. A ladder job
starting beside that guest refuses, because a `qemu-system` is a compute
job under any rule. A `compile.ps1` starting beside a live sweep is
refused by nothing, because it asks nothing. Two 3 GB guests here do not
fail — they thrash at 2% CPU each, which reads as mysterious slowness
rather than as the refused launch it should have been. An hour-long
sweep would not go red. Its timings would just quietly stop meaning
anything.

## Leg two: it cannot run here at all

`build/plug-run.ps1` hardcodes the same binary at line 49 and, unlike
`compile.ps1`, has no fallback. The word `qemu` does not appear in the
file. It dot-sources `vm-config.ps1` — the file that knows how to find a
QEMU, and that carries a ready-made error for having no host at all
("no VM host: ...", line 56) — and then ignores all of it and launches
`tools\codex-vm.exe` directly.

    build/plug-run.ps1 -IrInput hello.ir -PlugCdx zig-plug.cdx -MemMB 3072
    [plug-run] IR input: 1481 bytes
    [plug-run] Listening on TCP 9145
    plug-run.ps1: The variable '$proc' cannot be retrieved because it
                  has not been set.
    -> exit 1, one second

That is the failure a Linux user gets: not "no VM host", but a
PowerShell strict-mode complaint about an unset variable, because
`Start-Process` on a file that does not exist left `$proc` unset and the
next line read it. The diagnosis it needs is sitting in the file it
already sourced.

So on Linux, the 38 plugs that route through `plug-run.ps1` cannot be
run. Not slowly, not partially — at all.

## And the warning's own premise was stale

The version of this in our queue said `run.ps1` starts a 3 GB guest. In
this tree it does not, because it dies before it gets near one:

    codex/plugs/zig/run.ps1 -Src hello.codex -Out hello.zig
    FAIL: IR compile failed
    -> exit 4, one second

`run.ps1` calls `compile.ps1` without `-Kernel`, so `compile.ps1` looks
for `build-output/bare-metal/Codex.cdx` — the self-hosted compiler that
`build.ps1` produces — and this checkout has never run `build.ps1`. It
exits in a second having started nothing. I had to pass `-Kernel
seed/Codex.cdx` by hand to get leg one to run at all.

So the live hazard is not the one the queue named. `run.ps1` is inert
here. `build/compile.ps1`, reachable directly and by anything that
passes a kernel, is the thing that will put three gigabytes beside your
sweep, and it takes four seconds to do it.

## What is actually actionable

Not much, for us. We cannot teach `plug-run.ps1` about our lock even if
we wanted to: it opens with "GENERATED FROM THE CODEX SHELL DSL. Do not
edit by hand" — the source is `codex/build/plugrunScript.codex`, and
`build/check-generated-scripts.ps1` reports a hand edit as drift. A lock
that only our tree knows about does not belong in their generator
either. So our side of it is discipline, and it is one line: nothing in
the codex tree gets run by hand while a sweep is up.

The missing VM host is a different matter, and it is theirs. It is a
clean gap with a clean consequence — a whole platform, which their own
comment calls the only host on that platform, cannot run 38 plugs — and
it fails with a message that names the wrong thing. We also have the
working recipe, because the ladder has been doing this exact transport
daily for weeks: `plug_run.py` listens on 9145 and lets the guest dial
out, and `codex_vm.py:43-51` boots the guest with user-mode networking
(`-netdev user,id=net0 -device ne2k_isa,netdev=net0,irq=9,iobase=0x300`).
That goes over the fence with the recipe attached and the hedge stated —
we have not tried it on Windows, and the change belongs in the
generator, not in the generated file.

## The lesson, which is the same one as last week

The queue item said "starts a 3072 MB guest" and cited two line numbers.
Both line numbers were real. The sentence was still wrong, because
nobody had run the thing: the script it named exits in one second on
this box, and the script that really does start the guest was not the
one being warned about. This is the third time in three days that a cost
claim in a queue survived only because it was written from reading.

Reading tells you what a script would do. It does not tell you what it
does.
