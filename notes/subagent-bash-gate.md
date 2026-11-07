# Subagents and the Bash gate

**One yes/no question at the end.**

## What's happening

Your Bash hook (`shale-gate`) refuses every command except the Shale launch, and it does refuse mine. But today several cold agents ran plain `ls`, `cat` and `mkdir` without being refused. A probe agent confirmed it: all three ran, with no hook message.

It isn't Claude Code. The hook fires for subagents, and their tool calls carry an `agent_id` (documented in the hooks docs). The gate itself lets them through, on purpose:

- `shale/tools/shale_gate.zig:14-15`, in its header: "a subagent's call (its input carries an `agent_id`): local cold agents are exempt".
- Lines 170-171 set `subagent = true` when `agent_id` is present, and line 230 is `if (h.subagent) return 0;`.
- `tools/shale_gate_test.zig:189` asserts that a subagent's `ls -la` passes.

The exemption dates from at least 2026-10-18, when Shale moved out of zig-webbox, so it was a deliberate choice back then. The brief now tells agents "only Shale runs", but nothing enforces that for them.

## What it means today

Agents mostly follow the brief, and the slips were read-only (`cat`, `ls`, `mkdir`, and one `sed -i` that an agent used for bulk renames). Nothing harmful happened. But the Shale-only rule binds the agents only by their reading of the brief, not by the gate.

## The fix, if you want it

Remove the exemption: delete `if (h.subagent) return 0;`, update the header comment, and flip the test at `shale_gate_test.zig:189` so a subagent's `ls -la` is refused. Then `zig build` in the shale checkout, which you'd run, since it rebuilds the gate itself. Agents would then get the same refusal I do, with the same escape (`# want: <tag>: <text>`) for a real need. That logs to `wants.tsv`, so you'd see what they reach for.

One thing to know first: a few agent tasks have leaned on plain tools Shale refuses as "text tools" (`sed -i` for bulk renames, `wc`, `grep`), mostly by passing `want =`. With the gate on, they'd go through Shale's `run` with a `want`, as mine do. That's workable, and their "what tripped you up" lists would tell us if it hurts.

## The question

**Should cold agents be held to the Shale-only gate too (remove the subagent exemption)? Yes or no.**
