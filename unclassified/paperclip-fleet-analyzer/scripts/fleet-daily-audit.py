#!/usr/bin/env python3
"""
Paperclip Fleet Daily Audit Script

Run as: python3 fleet-daily-audit.py [--company-id UUID] [--paperclip-url URL]

Outputs structured JSON to stdout. In cron mode, pipe to a file or
consume via jq for Discord embed generation.

Handles None assigneeAgentId safely (Paperclip API returns null for
unassigned issues, not an empty string).
"""
import json
import sys
import urllib.request
from collections import Counter
from datetime import datetime

PAPERCLIP_URL = "http://127.0.0.1:3100"
COMPANY_ID = "c5ea22fb-99d2-46a1-87c6-e7fc1ab0d712"

BLOCKED_KEYWORDS = [
    'blocked', 'auth', 'authentication', 'login', 'credential',
    'ssh', 'vps', 'notebooklm', 'expired', 'token', 'api key',
    'discord', 'telegram', 'webhook', 'mcp', 'api', 'integration'
]

SKILL_KEYWORDS = {
    'mcp_builder': ['mcp', 'api', 'integration', 'webhook', 'server', 'bridge', 'adapter'],
    'trading_automation': ['pine', 'tradingview', 'backtest', 'strategy', 'indicator'],
    'youtube_pipeline': ['youtube', 'transcript', 'summarize', 'video', 'ingest'],
    'generative_art': ['plotter', 'art', 'generative', 'svg', 'creative', 'design', 'visual'],
    'vector_db': ['chroma', 'vector', 'embedding', 'rag', 'semantic', 'search', 'knowledge'],
    'messaging': ['discord', 'telegram', 'notify', 'bot', 'alert', 'messaging'],
    'cron_automation': ['cron', 'schedule', 'pipeline', 'automation', 'nightly', 'heartbeat'],
}


def api_get(path, timeout=15):
    url = f"{PAPERCLIP_URL}/api/{path}"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}


def safe_agent_id(issue, default='UNASSIGNED'):
    """Return first 8 chars of assigneeAgentId, or default if None/missing."""
    raw = issue.get('assigneeAgentId')
    return (raw[:8] if raw else default)


def run_analysis():
    agents = api_get(f"companies/{COMPANY_ID}/agents")
    if isinstance(agents, dict) and 'error' in agents:
        print(json.dumps({"error": f"agents fetch failed: {agents['error']}"}), file=sys.stderr)
        sys.exit(1)

    issues = api_get(f"companies/{COMPANY_ID}/issues?limit=300")
    if isinstance(issues, dict) and 'error' in issues:
        print(json.dumps({"error": f"issues fetch failed: {issues['error']}"}), file=sys.stderr)
        sys.exit(1)

    agent_map = {a['id'][:8]: a['name'] for a in agents}
    existing_ids = {a['id'][:8] for a in agents}

    # Status breakdown
    status_counts = Counter(i.get('status', 'unknown') for i in issues)
    active = [i for i in issues if i.get('status') not in ('done', 'cancelled')]

    # Workload per agent
    workload = Counter()
    for i in active:
        workload[safe_agent_id(i)] += 1

    # Orphaned issues
    orphaned = [
        i for i in active
        if i.get('assigneeAgentId')
        and i.get('assigneeAgentId')[:8] not in existing_ids
    ]

    # Blocked work
    blocked = []
    for i in active:
        text = (i.get('title', '') + ' ' + str(i.get('description', '') or '')).lower()
        matches = [k for k in BLOCKED_KEYWORDS if k in text]
        if matches:
            blocked.append({
                'id': i['identifier'],
                'title': i['title'][:50],
                'status': i['status'],
                'on': matches[0],
                'assignee': safe_agent_id(i)
            })

    blocker_types = Counter(b['on'] for b in blocked)

    # Skill gaps
    backlog_items = [i for i in issues if i.get('status') in ('backlog', 'todo')]
    skill_requests = Counter()
    for issue in backlog_items:
        title = issue.get('title', '').lower()
        desc = (issue.get('description') or '').lower()
        text = title + ' ' + desc
        for skill, keywords in SKILL_KEYWORDS.items():
            if any(k in text for k in keywords):
                skill_requests[skill] += 1

    # High-priority unassigned
    high_prio_unassigned = [
        i for i in backlog_items
        if not i.get('assigneeAgentId')
        and i.get('priority') in ('high', 'critical')
    ]

    # Recovery noise
    recovery = [i for i in issues if i.get('originKind') == 'stranded_issue_recovery']
    recovery_alive = [i for i in recovery if i.get('status') not in ('done', 'cancelled')]

    # Severity
    severity = 'GREEN'
    if high_prio_unassigned or len(orphaned) > 5 or not agents:
        severity = 'RED'
    elif orphaned or skill_requests or blocked:
        severity = 'YELLOW'

    result = {
        'run_at': datetime.now().isoformat(),
        'severity': severity,
        'agents': {
            'total': len(agents),
            'by_status': dict(Counter(a.get('status', 'unknown') for a in agents)),
        },
        'issues': {
            'total': len(issues),
            'by_status': dict(status_counts),
            'active': len(active),
        },
        'workload': {
            aid: {
                'name': agent_map.get(aid, 'UNASSIGNED' if aid == 'UNASSIGNED' else 'DEAD-AGENT'),
                'count': count
            }
            for aid, count in workload.items()
        },
        'orphaned': {
            'count': len(orphaned),
            'items': [
                {'id': o['identifier'], 'status': o['status'], 'title': o['title'][:50]}
                for o in orphaned[:20]
            ]
        },
        'blocked': {
            'count': len(blocked),
            'by_type': dict(blocker_types),
            'items': blocked[:20]
        },
        'skill_gaps': dict(skill_requests),
        'high_priority_unassigned': {
            'count': len(high_prio_unassigned),
            'items': [
                {'id': i['identifier'], 'priority': i['priority'], 'title': i['title'][:50]}
                for i in high_prio_unassigned[:10]
            ]
        },
        'recovery_noise': {
            'total': len(recovery),
            'alive': len(recovery_alive),
            'dead': len(recovery) - len(recovery_alive)
        }
    }

    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    run_analysis()
