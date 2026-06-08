# Swarm Worker Terminal Stall Recurrence — 2026-05-17

## Incident Summary

**Worker:** Kilo (OpenAI Codex execution specialist)
**Coordinator:** Hive (Kimi K2.5 via Fireworks)
**Duration:** ~12 hour session (May 16 23:00 — May 17 05:30)
**Pattern:** Terminal stall recurrence — same as 2026-05-16 session but with additional phantom claims

## Stall Timeline

| Time | Event | Active Process | Hive Action |
|---|---|---|---|
| ~00:30 | Kilo starts terminal command | Unknown | Monitoring |
| ~00:45 | `⏳ Still working... (15 min)` | None detected | Check `ps aux` → no active process |
| ~01:15 | `⏳ Still working... (45 min)` | None | Hive completes EDGA-1220 autonomously |
| ~01:30 | `⏳ Still working... (60 min)` | None | Hive completes EDGA-1086 autonomously |
| ~02:30 | `⏳ Still working... (93 min)` | None | Kilo still reporting "still working" |
| ~03:30 | `⏳ Still working... (122 min)` | None | Kilo stream reconnect after 998s timeout |
| ~04:30 | `⏳ Still working... (139 min)` | None | Kilo stream reconnect after 669s timeout |
| ~05:30 | `⏳ Still working... (141 min)` | None | Kilo finally reports task-322 completion |

**Key observation:** Kilo claimed to be "running: terminal" for 141 minutes, but `ps aux | grep` showed zero active `xcodebuild`, `python`, `git`, or `claude` processes belonging to Kilo. The terminal command was either completed silently or hung in a way that didn't spawn a visible process.

## Phantom Claim During Stall

While stalled, Kilo claimed:
- "60% built" — `scripts/adversarial-harness.py` did not exist on disk when Hive checked
- "task-322 in progress — adversarial dev harness (planner/generator/evaluator triad). ~60% built" — actual file had 0 lines at check time
- Later: "260-line orchestrator" — when file finally appeared (263 lines), it was after the long stall

**Root cause hypothesis:** Kilo was working in-memory or hallucinating progress during the terminal stall, then eventually executed the actual work during a reconnection cycle.

## Verification Steps Applied by Hive

```bash
# 1. Check for active processes
ps aux | grep -i "claude\|xcodebuild\|python.*pre\|git.*push" | grep -v grep
# Result: No Kilo-associated processes

# 2. Check file existence
ls -la scripts/adversarial-harness.py
# Result: File not found (during stall)

# 3. Check git status
git log --oneline -5
# Result: Last commit was task-324, not task-322

# 4. Check workspace status
git status --short
# Result: Modified files in edgelesslab/, no new scripts/
```

## Post-Stall Verification

When Kilo finally reported completion:
```bash
# Verify task-322 deliverables
git log --oneline -3
# Result: 8780598 feat(adh): Adversarial Dev Harness prototype — task-322
#         a2ebef5 feat(task-322): Adversarial dev harness test runner + evaluation report

ls -la scripts/adversarial-harness.py
# Result: 263 lines, 8507 bytes ✓

ls -la tools/adversarial-dev/
# Result: harness_test_runner.py, test_prompts/, test_runs/, evaluation_report_20260517.md ✓

python3 -m py_compile tools/adversarial-dev/harness_test_runner.py
# Result: COMPILE OK ✓
```

All deliverables verified. The stall was genuine but the completion was real — just delayed by 2+ hours.

## Lessons

1. **Terminal stall + phantom progress claims are correlated.** When a worker is stalled, it may generate in-memory/hallucinated progress updates. Do not accept progress percentages without disk verification.

2. **141-minute stall with zero processes is possible.** The terminal tool can be "running" in the gateway's state tracking while the actual subprocess has completed or crashed. Always verify with `ps aux` + `process(action="list")`.

3. **Stream reconnects don't mean progress.** Kilo reconnected 2+ times during the stall, but each reconnect reset to "iteration 24/90" — no actual iteration advancement. Reconnect count is not a progress metric.

4. **Coordinator should complete mission autonomously after 15-min stall.** Hive waited too long before taking over. The 2026-05-16 session's Rule 12 in `verify-before-claiming` says 15 min → autonomous fallback. This session violated that rule by waiting 90+ min.

## Cross-Reference

- `references/swarm-coordinator-fallback-2026-05-16.md` — First terminal stall incident, Rule 12 formulation
- `backroom-protocol` Rule 6 — Hung task detection and reassignment
- `kanban-worker` "Worker Discipline in Swarm Mode" — Standby protocol to prevent "What's next?" loops
