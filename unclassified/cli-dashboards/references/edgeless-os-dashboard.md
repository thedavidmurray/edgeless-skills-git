# Reference: Edgeless OS — Swarm Infrastructure Dashboard

Date: 2026-06-04
Context: Edgeless swarm — 20 agents, 207 skills, Paperclip, ChromaDB, vault, cron, git
File: `scripts/edgeless-os-dashboard.py`

## What this instance does

Unified terminal dashboard for the Edgeless agent swarm. Surfaces all active workstreams in one view: Paperclip agents, backlog status, cron health, vault stats, system health, and active projects.

## Data sources

| Source | Method | Fallback |
|--------|--------|----------|
| Paperclip agents | `curl /api/companies/{cid}/agents` | None (fast) |
| Paperclip backlog | `curl /api/companies/{cid}/issues?limit=200` | Fleet-daily markdown report (`claude-vault/13-Reports/daily-alignment/YYYY-MM-DD-fleet-daily.md`) |
| Hermes cron | `~/.hermes/cron/jobs.json` direct read | None |
| Vault metrics | `find` + `du` on `claude-vault/` | None |
| ChromaDB | `curl --max-time 2 localhost:8100/api/v1/heartbeat` | None |
| Git status | `git status --short` | None |
| Active projects | Hardcoded list with status strings | None |

## Rendered panels

```
SWARM AGENTS         Status | Count | Bar
running              11      | ████████
paused                5      | ████
idle                  4      | ███

SYSTEM HEALTH        Service  | Status | Detail
Paperclip            UP       | 20 agents
ChromaDB             DOWN     | localhost:8100
Vault                OK       | 23,427 md | 4900.5 MB
Git                  DIRTY    | 1874 uncommitted
Crons                RUNNING  | 59 active | 13 paused | 22 err

PAPERCLIP BACKLOG    Metric   | Count | Bar
Alive                142      | ████████
Blocked              7        | █
Source: fleet-daily (API slow)

ACTIVE PROJECTS
RUNE/CAIRO         | Paper trading | PMCC validation
The Clapper v2     | iOS certs | TestFlight
Edgeless Blog      | Weekly posts + social threads
Skill Library      | 207 skills | 18 underutilized
Vault KB           | 23.4K files | Wiki sparse
Discord Swarm      | 8 bots | 11 running
YouTube Pipeline   | Likes → Chroma → NotebookLM
Creative / fxhash  | Generative art pipeline
```

## Key code patterns

### Fleet-daily fallback parser

```python
import re, glob, pathlib

reports = sorted(glob.glob("claude-vault/13-Reports/daily-alignment/*-fleet-daily.md"))
if reports:
    text = pathlib.Path(reports[-1]).read_text()
    alive = int(re.search(r"(\d+)\s+active\s+issues", text).group(1))
    blocked = int(re.search(r"(\d+)\s+blocked", text).group(1))
    source = "fleet-daily"
else:
    alive = blocked = 0
    source = "N/A"
```

### Cron metrics from jobs.json

```python
import json, pathlib

jobs = json.loads(pathlib.Path("~/.hermes/cron/jobs.json").expanduser().read_text())
active = sum(1 for j in jobs["jobs"] if j.get("enabled") and not j.get("paused_at"))
paused = sum(1 for j in jobs["jobs"] if j.get("paused_at"))
errors = sum(1 for j in jobs["jobs"] if j.get("last_status") == "error")
```

### Vault metrics

```python
import subprocess

files = subprocess.run(
    ["find", "claude-vault", "-name", "*.md"],
    capture_output=True, text=True
)
file_count = len(files.stdout.strip().split("\n")) if files.stdout else 0

size = subprocess.run(
    ["du", "-sm", "claude-vault"],
    capture_output=True, text=True
)
size_mb = float(size.stdout.split()[0]) if size.stdout else 0
```

## Anti-patterns learned

- **Do not block render on slow API.** Paperclip `/issues` can take 20s+. Always fetch with `--max-time 2` or skip to fallback.
- **Label fallback data.** Append `Source: fleet-daily` to the table so the user knows the data is cached.
- **Initialize counters.** `alive_count` and `blocked_count` must be initialized to 0 before the try/fetch block to avoid `UnboundLocalError` when the API fails.
- **Separate fetch from render.** Build a `data = {}` dict first, then construct `rich.Table` objects. Never mix I/O and table construction.

## Files

- `scripts/edgeless-os-dashboard.py` — 280 lines, rich + subprocess + json
- `claude-vault/13-Reports/daily-alignment/` — fleet-daily markdown reports
- `~/.hermes/cron/jobs.json` — cron job state

## Deployment

Run manually: `python3 scripts/edgeless-os-dashboard.py`

Wire into daily cron (e.g., 8 AM) for morning stand-up view.
