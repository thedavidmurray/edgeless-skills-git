#!/usr/bin/env python3
"""
Hermes cron audit script — parses `hermes cron list` TUI output.
Detects stale jobs (>7d or never run), very stale jobs (>14d),
missing script files, and last-run errors.

Usage: python3 cron-audit.py
Output: JSON report to /tmp/cron_audit.json + human-readable stdout.
"""
import json, os, re, subprocess, sys
from datetime import datetime, timezone, timedelta

def main():
    result = subprocess.run(["hermes", "cron", "list"], capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        print(f"hermes cron list failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    text = result.stdout
    now = datetime.now(timezone(timedelta(hours=-7)))  # -07:00
    stale_threshold = timedelta(days=7)
    very_stale_threshold = timedelta(days=14)

    # Parse jobs by splitting on job-ID lines
    job_blocks = re.split(r'\n  [a-f0-9]+ \[', text)[1:]
    jobs = []
    for block in job_blocks:
        lines = block.strip().split('\n')
        job_id = lines[0].split()[0] if lines else "?"
        name_match = re.search(r'Name:\\s+(\\S+)', block)
        schedule_match = re.search(r'Schedule:\\s+(.+)', block)
        script_match = re.search(r'Script:\\s+(.+)', block)
        last_run_match = re.search(r'Last run:\\s+([0-9T:\\-\\.]+)\\s+(.+)', block)
        mode_match = re.search(r'Mode:\\s+(.+)', block)

        name = name_match.group(1) if name_match else "?"
        schedule = schedule_match.group(1).strip() if schedule_match else "?"
        script = script_match.group(1).strip() if script_match else None
        mode = mode_match.group(1).strip() if mode_match else None

        last_run = None
        last_status = None
        if last_run_match:
            last_run = last_run_match.group(1)
            last_status = last_run_match.group(2).strip()

        jobs.append({
            "id": job_id,
            "name": name,
            "schedule": schedule,
            "script": script,
            "mode": mode,
            "last_run": last_run,
            "last_status": last_status,
        })

    print(f"Total jobs: {len(jobs)}")

    stale = []
    very_stale = []
    for j in jobs:
        if j["last_run"] is None:
            stale.append(j)
            continue
        try:
            ts = datetime.fromisoformat(j["last_run"])
            age = now - ts
            if age > very_stale_threshold:
                very_stale.append((j, age))
            elif age > stale_threshold:
                stale.append((j, age))
        except Exception as e:
            print(f"Parse error for {j['name']}: {e}")

    print(f"\\n=== STALE JOBS (no run or >7 days) ===")
    for item in stale:
        if isinstance(item, tuple):
            j, age = item
            print(f"  {j['name']} | {j['last_run']} | {age.days}d ago | {j['last_status']}")
        else:
            print(f"  {item['name']} | NEVER RUN | script={item['script']}")

    print(f"\\n=== VERY STALE (>14 days) ===")
    for j, age in very_stale:
        print(f"  {j['name']} | {j['last_run']} | {age.days}d ago | {j['last_status']}")

    print(f"\\n=== MISSING SCRIPTS ===")
    missing = []
    for j in jobs:
        if j["script"] is None:
            continue
        script_path = j["script"]
        if not script_path.startswith("/"):
            candidates = [
                os.path.join("/Users/djm/.hermes/scripts", script_path),
                os.path.join("/Users/djm/claude-projects", script_path),
                os.path.join("/Users/djm/.hermes/scripts/cron", script_path),
            ]
            found = any(os.path.exists(c) for c in candidates)
            if not found:
                missing.append(j)
                print(f"  {j['name']} | script={script_path}")

    print(f"\\n=== JOBS WITH LAST ERROR ===")
    error_jobs = [j for j in jobs if j["last_status"] and "error" in j["last_status"].lower()]
    for j in error_jobs:
        print(f"  {j['name']} | {j['last_run']} | {j['last_status']}")

    print(f"\\n=== CRON AUDIT SUMMARY ===")
    print(f"Total jobs: {len(jobs)}")
    print(f"Stale (>7d or never): {len(stale)}")
    print(f"Very stale (>14d): {len(very_stale)}")
    print(f"Missing scripts: {len(missing)}")
    print(f"Last run error: {len(error_jobs)}")

    with open("/tmp/cron_audit.json", "w") as f:
        json.dump({
            "total": len(jobs),
            "stale": [{"name": (j[0]["name"] if isinstance(j, tuple) else j["name"]),
                       "last_run": (j[0]["last_run"] if isinstance(j, tuple) else None),
                       "days": (j[1].days if isinstance(j, tuple) else None),
                       "status": (j[0]["last_status"] if isinstance(j, tuple) else None)} for j in stale],
            "very_stale": [{"name": j["name"], "last_run": j["last_run"], "days": age.days, "status": j["last_status"]} for j, age in very_stale],
            "missing_scripts": [{"name": j["name"], "script": j["script"]} for j in missing],
            "error_jobs": [{"name": j["name"], "last_run": j["last_run"], "status": j["last_status"]} for j in error_jobs],
        }, f, indent=2)
    print("\\nReport saved to /tmp/cron_audit.json")

if __name__ == "__main__":
    main()
