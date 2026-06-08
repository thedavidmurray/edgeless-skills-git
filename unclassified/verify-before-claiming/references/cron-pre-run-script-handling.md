# Cron Pre-Run Script Output — Trust, Don't Re-Execute

## The Pattern

When operating as a scheduled cron job, the execution context often includes **pre-run script output** collected before the agent loop starts. Example format:

```
[20260516-124931] Swarm Health: GREEN | 7 up, 0 down, 1 disabled | 0.22s
```

This output is the result of a lightweight probe script that ran *before* the agent was invoked. It is **already verified data** from the actual system state at that moment.

## Common Failure Mode

The agent receives pre-run output, then wastes the entire turn:

1. Searching for the script that produced the output (may be a wrapper, inline shell, or ephemeral probe — not a named file)
2. Trying to match the exact output format against known scripts
3. Re-running a different script that produces *different* results
4. Reporting contradictory or confusing findings

**This is a form of confabulation-by-overwork** — the agent produces uncertainty where there was clarity, because it refused to trust the provided data.

## Correct Handling

**Step 1: Report the pre-run output as primary data**
- Quote it verbatim with its timestamp
- State it comes from the pre-run script

**Step 2: (Optional) Cross-check with a known script if ADDITIONAL detail is needed**
- Only if the user explicitly asked for deeper diagnostics
- State that the cross-check is supplementary, not a replacement
- When results differ, explain why (different check interval, different bot set, etc.)

**Step 3: Never claim the pre-run output is "wrong" without evidence**
- A discrepancy between pre-run (7 bots) and agent-run (8 bots) usually means one bot started between the two checks
- Report both, explain the likely time-drift cause

## Example — Good vs. Bad

**❌ BAD:**
```
User: Run swarm health check and report.
Pre-run output: [GREEN | 7 up, 0 down, 1 disabled]

Agent: *spends 10+ tool calls searching for scripts*
      *runs a different script*
      *reports conflicting 8/8 results*
      *confuses the user*
```

**✅ GOOD:**
```
Agent: Pre-run health probe (12:49:31 UTC): GREEN — 7 up, 0 down, 1 disabled.
      Cross-check with unified-health-snapshot.py: 8/8 bots currently up.
      Likely the disabled bot recovered between the two checks.
      Status: healthy.
```

## When This Applies

| Context | Pre-run output type | Action |
|---------|---------------------|--------|
| Cron health check | `GREEN | N up, M down` | Report directly, cross-check only if asked |
| Cron system status | Load avg, disk %, memory | Report as-is, flag if critical |
| Cron bot roster | Bot names + PIDs | Report directly |
| Any cron with `[IMPORTANT: pre-run script]` header | Agent output block | **Do not re-run the script. Analyze the block.** |

## Integration with Verify-Before-Claiming

This does NOT contradict the verify-before-claiming protocol. The pre-run script **is** the verification step. The agent's job is to **synthesize and report**, not to independently reproduce.

Verify when:
- The pre-run output is missing or empty
- The user explicitly asks for a different/more detailed check
- The output contains anomalies that warrant deeper inspection

Trust when:
- Clean, structured output is provided with timestamp
- The output matches the expected format for the task
- No user signal suggests doubt or requests additional verification
