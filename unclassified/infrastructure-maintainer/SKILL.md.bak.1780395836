---
name: infrastructure-maintainer
description: System reliability, performance optimization, monitoring, alerting, and infrastructure automation. Maintains 99.9%+ uptime with comprehensive observability, cost optimization, and security hardening.
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [infrastructure, sre, monitoring, prometheus, alerting, reliability, performance]
    related_skills: [system-health, incident-response-commander, cron-scheduling]
    requires_toolsets: [terminal, web_search]
---

# Infrastructure Maintainer

System reliability specialist. Ensures infrastructure health through proactive monitoring, performance optimization, and automated maintenance. Builds the observability that prevents incidents before they happen.

## When to Use

- Setting up monitoring and alerting for new services
- Diagnosing performance bottlenecks or resource exhaustion
- Building backup and disaster recovery procedures
- Optimizing infrastructure costs
- Security hardening and compliance validation
- Capacity planning and scaling decisions

## Core Capabilities

### 1. System Health Monitoring (Hermes-Specific)

**Check all gateway processes:**

```bash
# List all running Hermes gateways
ps aux | grep -E "hermes_cli.main.*gateway" | grep -v grep | awk '{print $2, $11, $12}'

# Check each gateway's state
for profile in beau hive kilo scribe edgeless-cc jojo; do
    state_file="$HOME/.hermes/profiles/$profile/gateway_state.json"
    if [ -f "$state_file" ]; then
        state=$(python3 -c "import json; d=json.load(open('$state_file')); print(d.get('gateway_state','unknown'))")
        telegram=$(python3 -c "import json; d=json.load(open('$state_file')); p=d.get('platforms',{}).get('telegram',{}); print(p.get('state','unknown'))")
        echo "$profile: gateway=$state telegram=$telegram"
    fi
done
```

**System load tracking:**

```bash
# Current load
uptime

# Load history (if available)
cat ~/.hermes/cron/output/system-load-*.log 2>/dev/null | tail -20

# Memory pressure
vm_stat | head -10
# or
free -h 2>/dev/null || echo "free not available on macOS"
```

**Disk space:**

```bash
# Check all mounted filesystems
df -h

# Check Hermes-specific directories
du -sh ~/.hermes/profiles/*/logs/ 2>/dev/null
du -sh ~/.hermes/cron/output/ 2>/dev/null
du -sh ~/claude-projects/claude-vault/ 2>/dev/null
```

### 2. Prometheus-Style Alerting (Conceptual for Mac)

Since macOS doesn't run Prometheus natively, we use equivalent shell checks:

```bash
#!/bin/bash
# infrastructure-health-check.sh -- Run via cron every 5 minutes

ALERTS=()

# CPU check (macOS: use `top` or `ps`)
CPU_USAGE=$(top -l 1 -n 0 | grep "CPU usage" | awk '{print $3}' | sed 's/%//')
if (( $(echo "$CPU_USAGE > 80" | bc -l) )); then
    ALERTS+=("HIGH_CPU: ${CPU_USAGE}%")
fi

# Memory check
MEM_PRESSURE=$(memory_pressure 2>/dev/null | grep "System-wide memory free percentage" | awk '{print $5}' | sed 's/%//')
if [ -n "$MEM_PRESSURE" ] && (( $(echo "$MEM_PRESSURE < 10" | bc -l) )); then
    ALERTS+=("LOW_MEMORY: ${MEM_PRESSURE}% free")
fi

# Disk check
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
if (( DISK_USAGE > 85 )); then
    ALERTS+=("LOW_DISK: ${DISK_USAGE}% used")
fi

# Hermes gateway check
DEAD_GATEWAYS=()
for profile in beau hive kilo scribe edgeless-cc jojo; do
    state_file="$HOME/.hermes/profiles/$profile/gateway_state.json"
    if [ -f "$state_file" ]; then
        state=$(python3 -c "import json; d=json.load(open('$state_file')); print(d.get('gateway_state','unknown'))" 2>/dev/null)
        if [ "$state" != "running" ]; then
            DEAD_GATEWAYS+=("$profile:$state")
        fi
    fi
done

if [ ${#DEAD_GATEWAYS[@]} -gt 0 ]; then
    ALERTS+=("DEAD_GATEWAYS: ${DEAD_GATEWAYS[*]}")
fi

# Output alerts (empty = healthy)
if [ ${#ALERTS[@]} -gt 0 ]; then
    echo "ALERTS: ${ALERTS[*]}"
    exit 1
else
    echo "OK"
    exit 0
fi
```

### 3. Backup and Recovery

**Hermes state backup:**

```bash
#!/bin/bash
# backup-hermes-state.sh

BACKUP_DIR="$HOME/.hermes/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup gateway states
for profile in beau hive kilo scribe edgeless-cc jojo; do
    src="$HOME/.hermes/profiles/$profile/gateway_state.json"
    if [ -f "$src" ]; then
        cp "$src" "$BACKUP_DIR/${profile}_gateway_state.json"
    fi
done

# Backup Paperclip state (if accessible)
# Paperclip stores in its own DB; use API backup

# Backup cron jobs
cp ~/.hermes/profiles/beau/cron/jobs.json "$BACKUP_DIR/cron_jobs.json" 2>/dev/null

# Compress
tar -czf "${BACKUP_DIR}.tar.gz" -C "$(dirname "$BACKUP_DIR")" "$(basename "$BACKUP_DIR")"
rm -rf "$BACKUP_DIR"

echo "Backup: ${BACKUP_DIR}.tar.gz"
```

**ChromaDB backup:**

```bash
# If ChromaDB is running locally
CHROMA_DIR="$HOME/.chroma_data"  # or wherever Chroma stores data
tar -czf "$HOME/.hermes/backups/chroma_$(date +%Y%m%d).tar.gz" "$CHROMA_DIR"
```

### 4. Hermes Tool Integration

**Use `terminal` for system commands:**

```python
from hermes_tools import terminal

# Check system resources
result = terminal("uptime && df -h / && vm_stat | head -5")
print(result["output"])

# Check Hermes process count
result = terminal("ps aux | grep -c hermes")
print(f"Hermes processes: {result['output'].strip()}")
```

**Use `web_search` for vendor status pages:**

```python
from hermes_tools import web_search

# Check if external services are down
results = web_search("Fireworks AI status page down")
for r in results["data"]["web"]:
    print(f"  {r['title']}: {r['url']}")
```

**Use `execute_code` for complex analysis:**

```python
from hermes_tools import execute_code

# Analyze gateway restart patterns
code = """
import json
import glob
from collections import Counter

restart_counts = Counter()
for log in glob.glob('/Users/djm/.hermes/profiles/*/logs/gateway-exit-diag.log'):
    with open(log) as f:
        content = f.read()
    restarts = content.count('shutdown diagnostic')
    profile = log.split('/')[-3]
    restart_counts[profile] = restarts

for profile, count in restart_counts.most_common():
    print(f"{profile}: {count} restarts")
"""
result = execute_code(code=code)
print(result["output"])
```

### 5. Capacity Planning

**Monitor Hermes resource growth:**

```bash
# Vault size over time
ls -lt ~/claude-projects/claude-vault/ | head -5

# Session database growth
ls -lh ~/.hermes/profiles/beau/state.db

# Cron output accumulation
find ~/.hermes/cron/output -type f -mtime +7 | wc -l

# Log rotation check
find ~/.hermes/profiles/*/logs -name "*.log" -size +10M | wc -l
```

## Alert Thresholds (Recommended)

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Load avg (1m) | > 10 | > 20 | Scale or investigate |
| Memory free | < 20% | < 10% | Restart services or add RAM |
| Disk usage | > 80% | > 90% | Clean logs or expand storage |
| Gateway down | Any | > 2 simultaneously | Supervisor storm |
| Cron failures | > 2/day | > 5/day | Fix broken scripts |
| Paperclip API | Timeout > 5s | Connection refused | Restart Paperclip |

## Pitfalls

1. **Monitor before you change.** Never make infrastructure changes without baseline metrics.
2. **Untested backups are useless.** Verify restore procedures quarterly.
3. **Alert fatigue kills response quality.** >5 false alerts/week means the threshold is wrong.
4. **Disk fills from logs first.** Log rotation is infrastructure 101.
5. **Gateway restart loops look healthy from the outside.** Check `gateway_state.json` for exit reasons, not just running status.
6. **ChromaDB memory grows unbounded.** Restart periodically or implement embedding eviction.
7. **Cron output files accumulate forever.** Clean `~/.hermes/cron/output/` older than 30 days.
8. **Paperclip DB can corrupt on unclean shutdown.** Always graceful-stop Paperclip.
9. **macOS `launchd` kills idle processes.** The supervisor threshold must account for quiet bots with infrequent jobs.
10. **Do not monitor metrics you can't control.** User prefers digests over alerts for load/API rate limits.

## Verification Checklist

| Step | Command | Success Criteria |
|------|---------|-----------------|
| 1. Gateway health | Check all `gateway_state.json` | All running |
| 2. System resources | `uptime && df -h` | Load < 10, disk < 80% |
| 3. Backup integrity | Test restore from latest backup | Files recoverable |
| 4. Alert channels | Send test alert to Telegram/Discord | Delivered in < 10s |
| 5. Log rotation | `ls -lh ~/.hermes/profiles/*/logs/*.log` | No file > 50M |
| 6. Cron health | `hermes cron list` | All enabled jobs scheduled |
| 7. Paperclip API | `curl 127.0.0.1:3100/api/health` | Returns `{"status":"ok"}` |

## Example: Weekly Infrastructure Report

```markdown
# Infrastructure Report -- Week of 2026-05-19

## System Health
- **Uptime:** 99.97% (target: 99.9%)
- **Load Average:** Peak 8.4, average 3.2
- **Memory:** Peak usage 78%, no pressure events
- **Disk:** 67% used (stable)

## Gateway Status
| Bot | Status | Restarts (7d) | Notes |
|-----|--------|---------------|-------|
| Beau | Running | 0 | Healthy |
| Hive | Running | 2 | Supervisor storm on May 21 |
| Kilo | Running | 1 | Config reload |
| Scribe | Running | 2 | Supervisor storm on May 21 |
| Edgeless CC | Running | 1 | Healthy |
| Jojo | Running | 4 | Killed in storm, recovered |

## Cron Health
- Total jobs: 7
- Failed (7d): 3 (hermes-release-watcher, hn-frontpage-watcher, rss-intelligence-v2)
- Fixed: 2 (watchers re-deployed)
- New: 3 (rss-feedback-tracker, rss-quality-reconciler, cascading-recovery-fix)

## Alerts (7d)
- SEV2: 1 (supervisor storm)
- SEV3: 0
- SEV4: 2 (load spike warnings)

## Action Items
1. Fix remaining watcher cron scripts (P2)
2. Add log rotation for gateway logs > 50M (P2)
3. Test ChromaDB backup/restore (P3)
4. Review Paperclip blocked issue backlog (P2)
```

## Related Skills

- `system-health` -- Health checks and monitoring basics
- `incident-response-commander` -- When things go wrong
- `cron-scheduling` -- Cron job management and scheduling
- `postgresql` -- Database operations and maintenance
