#!/usr/bin/env python3
"""
Paperclip Dispatch Router — Automated issue routing with WIP-aware assignment.

Usage:
    python dispatch-router.py --dry-run    # Preview only
    python dispatch-router.py --execute  # Actually PATCH assignments
    python dispatch-router.py --clear-zombies  # Unassign all issues from dead agents

Features:
1. Zombie clearing — Unassign issues from deleted/dead agents
2. Domain routing — Match issue text to agent domains via keyword rules
3. WIP limit enforcement — Max 5 active issues per agent (adjustable)
4. Recovery noise exclusion — Skip originKind=stranded_issue_recovery issues
5. Verified against Paperclip API (2026-05-13)

API verification:
- PATCH /api/issues/{id} {status, assigneeAgentId} → HTTP 200
- PATCH /api/agents/{id} {adapterConfig, status} → HTTP 200
"""

import requests, time, sys, argparse
from collections import defaultdict, Counter

# Configuration
BASE = "http://127.0.0.1:3100/api"
COMPANY = "c5ea22fb-99d2-46a1-87c6-e7fc1ab0d712"
WIP_LIMIT = 5
RATE_DELAY = 0.3  # Seconds between PATCH calls

# Domain routing rules: keyword list → agent name
ROUTING_RULES = [
    (['discord', 'gateway', 'bot', 'swarm', 'server', 'telegram', 'alert'], 'Beau'),
    (['website', 'ios', 'app', 'swift', 'skill', 'testflight', 'storekit', 'xcode', 'build'], 'Edgeless CC'),
    (['implement', 'build', 'code', 'script', 'execute', 'fast-track', 'protocol', 'deploy', 'ship'], 'Kilo'),
    (['audit', 'review', 'qc', 'verify', 'ombuds', 'process', 'mediat', 'health check'], 'Ombudsman'),
    (['oauth', 'auth', 'security', 'token', 'credential', 'login', 'encrypt', 'cipher'], 'Cypher'),
    (['knowledge', 'kb', 'research', 'vault', 'enrich', 'chroma', 'obsidian', 'notebooklm', 'scribe'], 'Scribe'),
    (['trading', 'pine', 'strategy', 'backtest', 'indicator', 'portfolio', 'risk', 'position'], 'Trader'),
    (['email', 'cron', 'rss', 'pipeline', 'dispatch', 'triage', 'notification', 'health'], 'Hive'),
    (['creative', 'art', 'plotter', 'generative', 'visual', 'design', 'svg', 'flora', 'render'], 'Critic'),
]

def fetch_all(url_path, limit=250):
    resp = requests.get(f"{BASE}{url_path}", params={"limit": limit}, timeout=30)
    data = resp.json()
    return data if isinstance(data, list) else data.get('issues', data.get('agents', []))

def route_issue(issue):
    """Return (agent_name, matched_keywords) or (None, None)"""
    text = (issue.get('title', '') + ' ' + str(issue.get('description', ''))).lower()
    for keywords, agent_name in ROUTING_RULES:
        matches = [k for k in keywords if k in text]
        if matches:
            return agent_name, matches
    return None, None

def clear_zombies(issues, agents, dry_run=True):
    """Unassign issues from dead agents"""
    live_ids = {a['id'] for a in agents}
    zombies = [i for i in issues
               if i.get('assigneeAgentId')
               and i['assigneeAgentId'] not in live_ids
               and i.get('status') not in ('done', 'cancelled')]

    print(f"Zombies to clear: {len(zombies)}")
    cleared = 0
    for i in zombies:
        if dry_run:
            print(f"  [DRY] Would unassign {i['identifier']}: {i['title'][:50]}")
            cleared += 1
            continue
        r = requests.patch(f"{BASE}/issues/{i['id']}",
                           json={"assigneeAgentId": ""},
                           headers={"Content-Type": "application/json"})
        if r.status_code == 200:
            cleared += 1
            print(f"  ✅ {i['identifier']}")
        else:
            print(f"  ❌ {i['identifier']}: HTTP {r.status_code}")
        time.sleep(RATE_DELAY)
    print(f"Cleared: {cleared} | Failed: {len(zombies) - cleared}")
    return cleared

def dispatch(issues, agents, dry_run=True):
    """Route unassigned alive issues to agents by domain, respecting WIP limits"""
    agent_map = {a['name']: a for a in agents}
    alive = [i for i in issues
             if i.get('status') not in ('done', 'cancelled')
             and i.get('originKind') != 'stranded_issue_recovery']

    # Count current WIP per agent
    wip = Counter()
    for i in alive:
        if i.get('assigneeAgentId'):
            name = next((a['name'] for a in agents if a['id'] == i['assigneeAgentId']), 'UNKNOWN')
            wip[name] += 1

    assigned = 0
    for issue in alive:
        if issue.get('assigneeAgentId'):
            continue  # Already assigned

        agent_name, matches = route_issue(issue)
        if not agent_name:
            print(f"  ⚠️  No route: {issue['identifier']} | {issue['title'][:50]}")
            continue

        if wip[agent_name] >= WIP_LIMIT:
            print(f"  😴 WIP full ({wip[agent_name]}/{WIP_LIMIT}): {agent_name} → skip {issue['identifier']}")
            continue

        agent = agent_map.get(agent_name)
        if not agent:
            print(f"  ❌ Agent not found: {agent_name}")
            continue

        if dry_run:
            print(f"  [DRY] Would assign {issue['identifier']} → {agent_name} (keywords: {matches})")
            wip[agent_name] += 1
            assigned += 1
            continue

        r = requests.patch(f"{BASE}/issues/{issue['id']}",
                           json={"assigneeAgentId": agent['id']},
                           headers={"Content-Type": "application/json"})
        if r.status_code == 200:
            wip[agent_name] += 1
            assigned += 1
            print(f"  ✅ {issue['identifier']} → {agent_name}")
        else:
            print(f"  ❌ {issue['identifier']} → {agent_name}: HTTP {r.status_code}")
        time.sleep(RATE_DELAY)

    print(f"\nDispatch complete: {assigned} assigned")
    print("Agent loads:")
    for name, count in sorted(wip.items(), key=lambda x: -x[1]):
        if count > 0:
            print(f"  {name}: {count}")
    return assigned

def main():
    parser = argparse.ArgumentParser(description="Paperclip Dispatch Router")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--execute", action="store_true", help="Actually PATCH")
    parser.add_argument("--clear-zombies", action="store_true", help="Only clear zombie assignments")
    parser.add_argument("--wip-limit", type=int, default=WIP_LIMIT, help=f"Max issues per agent (default {WIP_LIMIT})")
    args = parser.parse_args()

    if not args.dry_run and not args.execute and not args.clear_zombies:
        print("Usage: python dispatch-router.py --dry-run | --execute | --clear-zombies")
        sys.exit(1)

    dry_run = not args.execute and not args.clear_zombies
    global WIP_LIMIT
    WIP_LIMIT = args.wip_limit

    print("Fetching fleet state...")
    agents = fetch_all(f"/companies/{COMPANY}/agents")
    issues = fetch_all(f"/companies/{COMPANY}/issues")
    print(f"Agents: {len(agents)} | Issues: {len(issues)}")

    if args.clear_zombies or args.execute:
        clear_zombies(issues, agents, dry_run=False)
        # Re-fetch after clearing
        if args.execute:
            issues = fetch_all(f"/companies/{COMPANY}/issues")

    if args.execute or (not args.clear_zombies and dry_run):
        dispatch(issues, agents, dry_run=dry_run)

if __name__ == "__main__":
    main()
