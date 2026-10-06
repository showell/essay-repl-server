# Three long tasks for Cloud Claude

*2026-10-06, after v18 shipped. For Steve, choosing what CC works through
while he is away.*

The constraint isn't skill. CC is the same model; what it lacks is the box.
It has zig 0.16 and python, but no KVM, no QEMU, no droplet, and no prod. So
the right task lives where `zig build test` and the simulators are the whole
truth: pure layers, host-side tests, docs. Each line below stays there, has a
clear finish line, and has more surface than CC can exhaust in one sitting.

I'd judge each by four things:

- **Will it get blocked?** Does it need the box, a decision from Steve, or
  anything that could trip CC's permission checks? Item 65 taught us that last
  one is real.
- **Is the mission clear?** Could CC tell, at any point, whether it's done?
- **Does it pay off?** Does what it finds matter to lynrummy.com, or to where
  the stack is going?
- **Is the risk shallow?** A wrong turn should cost a commit, not a week.

---

## 1. The Store: the first floor of a web server in a box

*The outside-the-box one.*

[A web server in a box](a-web-server-in-a-box.md) said the platform should
hand an application a narrow **Store** instead of zig's whole directory API:
read whole, write whole, append, list, remove, replace. It also said the
**Linux twin must be as strict as metal**: it refuses, on your laptop, the
name FAT would fold into another one, for exactly the reason the droplet
would fail later. Nothing of that exists yet. All of it can be built and
proven without the box.

**The work, in order:**

1. **The interface, as a zig type** in gopher-metal: the six operations, the
   errors they can answer, and what "replace" promises (the old file or the
   new one, never half of each, even across a power cut).
2. **A model**, in memory, as plain as possible. It's the oracle.
3. **The FAT store**, over `fat16.zig`, on the in-memory disk the tests
   already use (`test_disk.zig`), with its power cuts and torn writes.
4. **The strict Linux store**, over `std.Io`'s filesystem in a temp
   directory. It enforces FAT's rules (case folding, name length, forbidden
   characters, `max_tree_depth`) *before* touching the disk.
5. **`store_sim`**: seeded sequences of operations, with crashes, run against
   all three. Every answer must match the model. FAT and Linux must refuse
   the same names for the same reasons. After any crash, every replaced file
   is wholly old or wholly new. These become properties in the catalog, with
   a floor.
6. **The census**: angry-gopher's ~104 disk call sites, each mapped to a
   Store operation in a table (a doc, no angry-gopher code change). The calls
   that don't fit are the real finding: each one is a question about the
   seam, for Steve.

**Why it's a good long task:** it has lots of surface (three backends, a
simulator, a census) and one design decision, the interface, which the
earlier essay already drafted. The differential between FAT and strict Linux
is the judge in miniature, and it will find real things. The case-folding
class of bug that bit chat on 2026-10-01 is exactly what step 5 checks for.

**Where it could stall:** in the census, if CC tries to *migrate*
angry-gopher rather than describe it. The item says describe. Second risk:
the interface can grow. The rule is six operations, and anything else goes
under Questions.

**What it buys:** the floor that a second tenant (a Roc app, a Cobblestone
app, a guestbook) would stand on, proven before anyone builds a door. It's
also a cheaper chat: today the 104 calls run through a wide seam, and a narrow
one is less to keep honest.

---

## 2. Every refusal named: coverage across the rest of the kernel

*The safe one.*

Today the SDK's properties live almost entirely in two modules: `tcp.zig`
(20 sites) and `fat16.zig` (47), plus the simulators. The other ~40 modules
of gopher-metal have none: `proto`, `arp`, `scsi`, `virtio`'s ring
bookkeeping, `stream` and `Spill`, `io.durable`, `page_cache`, `kept_log`,
`log_ring`, `gpt`, the `pvh` memory map, `civil` and `wallclock`,
`request_heap`, `restart`. Each of them refuses things (a short frame, a bad
partition table, a memory map with holes), and today no report says which
refusals any run has ever exercised.

**The work, module by module:**

1. For each refusal (an early return, an error answer), add a `reachable`
   naming it, the way "tcp: a damaged segment is dropped" already does.
2. For each invariant a module keeps, add an `always`, and use the numeric
   comparisons from item 61 where there's a limit. This includes B15: the
   TCP table's `check` and FAT's `check` as `always` in a `-Dcoverage`
   kernel.
3. For each module, reach its properties from a simulator or host test.
   Extend `pure_sim` with structured inputs (a frame built field by field,
   then one field made wrong) rather than random bytes.
4. Raise the floor in `coverage/floor-sim.txt` as each module is reached,
   and keep a table in `COVERAGE.md`: module, properties, how many reached,
   by what.

**Why it's a good long task:** it's methodical and needs no design. It has a
visible finish line (every module in the table), and it's one property at a
time, so a wrong turn costs one property. It also makes every metal-vmm
sweep on the box more informative, because a sweep's coverage report then
says *which* refusals each fault reached, not just that the page held.

**Where it could stall:** on DHCP. Lies in DHCP replies are the box's now
(B18), so DHCP stays out of this line. Second risk: a property in kernel code
must not change behavior. That's item 36's rule, and the gates on the box
check it.

**What it buys:** knowing what's tested. When a guest gate on the box fails,
or a prod log shows a refusal, the catalog says whether any simulator ever
went there.

---

## 3. The seed explorer: guidance, the Antithesis way

*The highest-leverage one, with the most design.*

Our simulators draw seeds 1 to N and hope. Antithesis's real advantage isn't
its properties. It's that it **steers**: it keeps the runs that reached
something new and varies them, instead of rolling fresh dice each time. We
have everything that requires except the steering. The properties say what
was reached, and since item 61 the numeric comparisons say how close a run
came to a limit.

**The work:**

1. **Choices, not seeds.** A `Choices` source in zig-coverage-sdk: each draw
   a simulator makes comes either from a seed (as now) or from a recorded
   tape that can be replayed, cut short or changed at one point. Hypothesis
   works this way, and it's what makes "vary a good run" possible.
2. **Convert the simulators** (`tcp_sim`, `fat_sim`, `page_sim`, `ready_sim`)
   to draw from `Choices`. A seed's run must be byte for byte what it is
   today, and the tests prove that.
3. **The explorer**: a loop in the SDK that runs a simulator, keeps every tape
   that reached a new property or a new extreme, and spends its budget
   mutating those tapes.
4. **The measurement**: at the same number of runs, how many MISSes do blind
   seeds leave against the explorer? Which properties only the explorer
   reached? A failure it finds shrinks to its shortest tape, which becomes a
   regression test, as seed 23953 did.

**Why it's a good long task:** it's real infrastructure with a measurable
result. Either the explorer beats blind seeds at equal budget, or it doesn't,
and we learn which. Every simulator added later inherits it.

**Where it could stall:** step 2 touches every simulator, and step 1 is a
design: what a tape is, and how a mutation is chosen. It's the line most
likely to produce a question that waits for Steve. It's also the least
likely to find a prod bug quickly, since its payoff is compound.

**What it buys:** the simulators stop being "N seeds and hope", and the
gap between our tooling and Antithesis narrows where it matters most.

---

## How I'd queue it

**Line 1 first, with line 2 queued behind it as the fallback.** Line 1 is the
one that moves the stack somewhere new, and its shape is already drafted. If
CC hits a Store design question, it writes the question down and takes the
next module of line 2, so it never blocks. Line 2 can absorb any amount of
time, and every hour of it pays off on the box's next sweep.

Line 3 is the one I'd want *with* you here: its first two steps are design
decisions you'd want to see before they spread through every simulator.

All three stay inside what CC's environment can prove: `zig build test`, the
simulators, python, and docs. None of them needs the box, a release, or prod.
