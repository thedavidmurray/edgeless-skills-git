# CLI Output vs Filesystem Verification — RSS Triage Case

## Pattern
The `rss_triage_cli.py` prints "enrich notes written: 10" and "archived: 0" in its stdout summary. These are routing decisions, not filesystem confirmations.

## Risk
An agent may claim "10 vault notes created" based solely on CLI stdout, without verifying the actual filesystem state.

## Verification
After the CLI exits 0:
1. `wc -l .feeds/rss-archived.jsonl` — check archive growth
2. `jq -r '.items[].id' .feeds/rss-delta.json | while read id; do grep -q "$id" .feeds/rss-archived.jsonl && echo OK || echo MISSING; done` — per-item coverage
3. `find claude-vault/00-Inbox/rss -type f -mmin -30` — inbox notes
4. `find claude-vault/03-Knowledge/RSS -type f -mmin -30` — KB notes
5. `grep -ri "title fragment" claude-vault/00-Inbox claude-vault/03-Knowledge` — keyword cross-check

## Lesson
Always verify filesystem state independently of CLI stdout. The CLI's summary counts are display decisions, not proof of I/O success.
