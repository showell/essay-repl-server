# What v23 carries

*Saturday 2026-10-10, evening. Everything on gopher-metal's master since
the `v22` tag (`bc459b3`), now at `0e737b8`, and the judge changes in
metal-vmm that decide whether a v23 run is clean. angry-gopher has not
moved since v22 (`51713cd6`), so the app is the same.*

## The short version

- **The one change a user would notice: uploads.** Writing a file now
  costs about a tenth of the disk writes it did (B42). On production's
  volume, where every disk request costs about 5.8 ms, a 1 MiB upload goes
  from ~143 writes (~0.8 s of disk time) to roughly 15–20.
- **Everything else in served code is about what happens when the disk
  fails.** A rename that hits one fault can no longer lose the file, and
  what a failure leaves behind is counted exactly instead of roughly.
- **Nothing changes for a disk that works**, apart from the uploads. The
  cold review of CC's 148 confirmed that its changes write exactly what
  v22 wrote to the disk; they add counting and some read-backs on failure
  paths only.
- **Not yet ready to cut.** CC's new plant is still running, the judge's
  newest check has not run on a guest, and there is one known false red in
  the judge (below). The release run itself takes about an hour.

## Served code, by what it changes for the site

### 1. Uploads: fewer disk writes (B42, `e4a7f3b`, `bdef1c2`)

v22 wrote the FAT (the disk's table of which clusters belong to which
file) once per cluster, and again for the second copy of the FAT. A
1 MiB file on 32 KiB clusters is 32 clusters, so ~128 of its 143 writes
were FAT bookkeeping.

Now a file's clusters are claimed a FAT sector at a time: every cluster
the file still needs from one sector is marked in memory, and the sector
is written once per FAT copy. One sector holds 128 entries, so a typical
upload touches one or two.

**What it risks:** this is the allocation path every write goes through.
It got a red-first test (8,207 FAT writes before, at most a few dozen
after), a cold review, whose one finding was fixed (`bdef1c2`: a refused
batch write is judged only on the batch's own entries), and a clean plants
run. **One behaviour changed:** in v22 a failed write to the second FAT
copy usually healed itself on the next cluster's write; now there's no
next write to heal it, so it's counted (`FAT copy writes failed`) and the
next mount repairs it from the first copy. The judge holds "FATs differ"
to that count.

**Deletes and overwrites still free one cluster per FAT write.** Batching
those is next on the box's list. It isn't in v23 unless we wait for it.

### 2. A rename that fails can't lose the file (CC's 147(g), `9c3190c`)

In v22, a rename removed the old name (a "tombstone" on the directory
entry) before it was sure the new name had landed. If the disk refused
that tombstone write but the write in fact landed, the undo didn't run,
and the file ended up under no name at all. Now both failure paths share
one undo (`undoUnlink`). It was red first: one fault at request 7 of 18
left the file nameless.

### 3. What a failure leaves on the disk is counted exactly (CC's 148)

This is the "exact accounting" strategy from
[where the bugs are now](where-the-bugs-are-now.md), applied to the disk.
When an operation fails half-way, the kernel now counts precisely what it
left behind, in three kinds:

- **leaked clusters**: claimed, but in no file;
- **orphaned long-name parts**: pieces of a long filename with no file
  under them;
- **chains past a size**: a file whose clusters run longer than its
  length says (new in v23).

Where the kernel can't know whether a write landed, it counts the
leftover apart, as **"may be live"**. The host test checks after every
faulted operation that these counts match what a full check of the
volume finds: exact as a floor, and exact plus may-be-live as a ceiling.
That check found 687 mismatches when it first ran. The biggest class: a
file freed after its new version was committed, where the free failed
part-way, so the rest of the old chain was counted as nothing.

**What users see:** nothing; the counts aren't fixed by this, only made
truthful. **What we see:** the run's end line (and the judge) now says
how much may be live, and how many clusters run past a size.
`/admin/host` still shows only the exact leaked count; QUEUE 152 adds
the rest.

### 4. Plants live in the source (B39, `c08dc9c`)

Our deliberate bugs ("plants", which prove the judge can catch a real
defect) used to be patch files that rotted as the code moved. Now each is
a few lines in the source behind a build option, `-Dplant=<name>`.
**Compiling a plant without the test instrumentation (`-Dcoverage`) is a
compile error,** so a release image can't contain one: in a release
build the plant code is compiled out. Three plants exist: a swallowed
disk write, a TCP resend with a wrong byte, and CC's new one, a leak
counted one short.

## Not served: tests and tools (in the release, but they never run on the site)

- **Mutation tools** (CC's 147, 148(g)): a mutant now counts as killed only
  when a test fails. Before, a compile error or an out-of-memory crash also
  counted, which overstated how good the tests are.
- **`lint_machine.py`** catches more ways to bypass a declared state machine.
- **The fault tests** assert their premises, and fail on their own titles.
- **`zig build check-plants`** type-checks every plant's build.

## The judge (metal-vmm): what decides "clean" for v23

These don't ship, but a v23 run is judged by them:

- **Exact accounting at the boundary.** When fsck finds leftovers, they
  pass only if the kernel's end line counted them: no more clusters than
  K, and (new tonight, `336c44f`) **no fewer than the part the kernel was
  sure of**. Without that floor, an over-count is room for a real leak to
  hide in. **This floor hasn't run on a guest yet.**
- **Read-backs for the two-client shapes** (CC's 149): a write that one
  client was told succeeded must be on the disk, for every client. Derived
  from the code, never yet run on a guest; a wrong one fails loudly, not
  silently.
- **A broken test I caused, now fixed.** My judge change this morning
  (`250cc5d`) left the judge's own test suite failing; I hadn't run it. The
  verdict was still right, just worded differently. It passes now, and the
  suite gained ten direct checks of the leak rule.

## Before cutting v23

| step | state | time |
|---|---|---|
| plants on the merge (`0e737b8`) | all pass: clean, swallowed write, TCP byte, and CC's leak plant (caught in all 3 runs it fired in) | done, 14 min |
| plants with the judge's new floor | not run | ~20 min |
| **known false red:** a chain past its size that the kernel counted still fails the judge (fsck's "Truncating" line isn't excused yet) | the box's next fix | small |
| QUEUE 152 (`orphaned_runs`, exact names) | CC, queued | — |
| release run: port, gates, long, image | — | ~45 min (v22's: gates 12, long 29) |

**The decision for you:** what goes into v23. Three choices:

1. **Now:** B42, the rename fix and 148, once a floor
   run are clean and the "Truncating" false red is fixed. Roughly 1.5 h of
   box time, most of it unattended.
2. **Wait for 152** as well, so `/admin/host` shows every count and the
   judge holds orphaned names exactly. That adds CC's turnaround plus a
   review.
3. **Wait for batched frees** too, so deletes and overwrites are as cheap
   as uploads.

My recommendation is option 1: the upload speed-up is the change you
asked for, and the rest are refinements that can be v24.
