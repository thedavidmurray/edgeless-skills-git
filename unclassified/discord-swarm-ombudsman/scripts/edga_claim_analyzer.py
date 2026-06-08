#!/usr/bin/env python3
"""
EDGA Claim Analyzer — Ombudsman Pattern Detection
Parses Discord messages from audit-log to detect coordination patterns:
- Duplicate claims (multiple agents claiming same EDGA-XXX)
- Silent claims (claimed but no updates >3h)
- Delivered awaiting approval
- Infrastructure failures

Usage: python3 edga_claim_analyzer.py /tmp/audit_log.json
Output: JSON report to /tmp/edga_analysis.json
"""

import json
import re
import sys
from datetime import datetime, timezone
from collections import Counter

# Thresholds
SILENT_CLAIM_HOURS = 3
DELIVERED_APPROVAL_HOURS = 2


def extract_edga_id(content):
    """Extract EDGA-XXX reference from message content."""
    match = re.search(r'EDGA-(\d{3,4})', content, re.IGNORECASE)
    return f"EDGA-{match.group(1)}" if match else None


def extract_claim_agent(content):
    """Extract claiming agent from claim patterns."""
    patterns = [
        r'claimed.*?by\s+(\w+)',
        r'(\w+)\s+claimed',
        r'\*\*(\w+)\*\*\s+claimed',
        r'🔖.*?Claimed.*?by\s+(\w+)',
        r'🎯.*?Claimed.*?by\s+(\w+)',
        r'🔧.*?claimed.*?by\s+(\w+)',
        r'🔒.*?CLAIMED.*?by\s+(\w+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def extract_complete_status(content):
    """Detect completion patterns in message content."""
    complete_patterns = [
        r'complete[\s\*]*edga-\d+',
        r'deliverable.*complete',
        r'✅.*complete',
        r'✅.*edga-\d+',
        r'stand down',
        r'releasing claim',
    ]
    for pattern in complete_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return True
    return False


def analyze_claims(messages, current_time):
    """Build EDGA claim state from message history."""
    # Sort chronologically
    sorted_msgs = sorted(
        messages,
        key=lambda x: datetime.fromisoformat(
            x.get('timestamp', current_time.isoformat()).replace('Z', '+00:00')
        )
    )
    
    edga_claims = {}
    
    for msg in sorted_msgs:
        content = msg.get('content', '')
        author = msg.get('author', {}).get('username', 'unknown')
        ts_str = msg.get('timestamp', current_time.isoformat())
        
        try:
            timestamp = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
        except:
            timestamp = current_time
            
        edga_id = extract_edga_id(content)
        if not edga_id:
            continue
        
        if edga_id not in edga_claims:
            edga_claims[edga_id] = {
                'claims': [],
                'updates': [],
                'completed': False,
                'complete_time': None
            }
        
        claim_agent = extract_claim_agent(content)
        is_complete = extract_complete_status(content)
        age_hours = (current_time - timestamp).total_seconds() / 3600
        
        if claim_agent:
            edga_claims[edga_id]['claims'].append({
                'agent': claim_agent,
                'time': timestamp.isoformat(),
                'author': author,
            })
        
        if is_complete:
            edga_claims[edga_id]['completed'] = True
            edga_claims[edga_id]['complete_time'] = timestamp.isoformat()
        
        edga_claims[edga_id]['updates'].append({
            'time': timestamp.isoformat(),
            'author': author,
            'is_claim': bool(claim_agent),
            'is_complete': is_complete,
            'age_hours': age_hours
        })
    
    return edga_claims


def detect_stale_patterns(edga_claims, current_time):
    """Identify stale coordination patterns from claim state."""
    stale_issues = []
    
    for edga_id, data in edga_claims.items():
        claims = data['claims']
        updates = data['updates']
        
        if not updates:
            continue
        
        latest_update = max(updates, key=lambda x: x['time'])
        latest_age = latest_update['age_hours']
        
        # Pattern 1: Duplicate claims
        if len(claims) > 1:
            agents = list(set(c['agent'] for c in claims))
            stale_issues.append({
                'type': 'duplicate_claims',
                'severity': 'critical',
                'edga_id': edga_id,
                'agents': agents,
                'claim_count': len(claims),
                'age_hours': latest_age,
                'blocker': f'{len(claims)} agents claiming same task',
                'action': f'Clarify ownership: {agents[0]} leads, others assist or release'
            })
        
        # Pattern 2: Silent claim (>3h with no updates)
        elif len(claims) == 1 and not data['completed'] and latest_age > SILENT_CLAIM_HOURS:
            agent = claims[0]['agent'] if claims else 'unknown'
            stale_issues.append({
                'type': 'silent_claim',
                'severity': 'medium',
                'edga_id': edga_id,
                'agents': [agent],
                'age_hours': latest_age,
                'blocker': f'No status updates since claim {latest_age:.1f}h ago',
                'action': f'Status update from {agent} or release claim'
            })
        
        # Pattern 3: Delivered awaiting approval (>2h since complete)
        elif data['completed'] and latest_age > DELIVERED_APPROVAL_HOURS:
            stale_issues.append({
                'type': 'awaiting_approval',
                'severity': 'low',
                'edga_id': edga_id,
                'agents': [claims[0]['agent']] if claims else ['unknown'],
                'age_hours': latest_age,
                'blocker': 'Deliverable complete, human decision pending',
                'action': 'Review deliverable and approve/decline'
            })
    
    return stale_issues


def format_triage_report(stale_issues, total_tracked):
    """Generate condensed triage report for Discord (under 2000 chars)."""
    critical = [i for i in stale_issues if i['severity'] == 'critical']
    medium = [i for i in stale_issues if i['severity'] == 'medium']
    low = [i for i in stale_issues if i['severity'] == 'low']
    
    lines = [
        f"[FROM:Ombudsman][TO:Hive][TYPE:TRIAGE][REF:OMBU-{datetime.now(timezone.utc).strftime('%Y-%m-%d-%H%M')}]",
        "",
        f"**Stale Scan** ({datetime.now(timezone.utc).strftime('%H:%M')} UTC)",
        ""
    ]
    
    if critical:
        lines.append("🔴 **CRITICAL: Duplicate Claims**")
        for c in critical:
            lines.append(f"• **{c['edga_id']}**: {', '.join(c['agents'])} ({c['age_hours']:.1f}h)")
            lines.append(f"  → {c['action']}")
        lines.append("")
    
    if medium:
        lines.append("🟡 **SILENT CLAIM (>3h)**")
        for m in medium:
            lines.append(f"• **{m['edga_id']}**: {m['agents'][0]} ({m['age_hours']:.1f}h silent)")
            lines.append(f"  → {m['action']}")
        lines.append("")
    
    if low:
        edga_list = ', '.join(i['edga_id'] for i in low[:5])
        if len(low) > 5:
            edga_list += f" (+{len(low)-5} more)"
        lines.append(f"🟢 **AWAITING APPROVAL ({len(low)}):**")
        lines.append(edga_list)
        lines.append("")
    
    # Summary line
    most_urgent = critical[0]['edga_id'] if critical else (medium[0]['edga_id'] if medium else 'none')
    lines.append(f"**Summary**: {len(stale_issues)} flagged ({len(critical)} critical, {len(medium)} medium, {len(low)} low)")
    lines.append(f"Most urgent: {most_urgent}")
    lines.append("[STATUS:COMPLETE]")
    
    return '\n'.join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 edga_claim_analyzer.py <audit_log.json> [backroom.json]", file=sys.stderr)
        sys.exit(1)
    
    with open(sys.argv[1]) as f:
        audit_messages = json.load(f)
    
    backroom_messages = []
    if len(sys.argv) > 2:
        with open(sys.argv[2]) as f:
            backroom_messages = json.load(f)
    
    current_time = datetime.now(timezone.utc)
    all_messages = audit_messages + backroom_messages
    
    # Analyze
    edga_claims = analyze_claims(all_messages, current_time)
    stale_issues = detect_stale_patterns(edga_claims, current_time)
    
    # Sort by severity
    severity_order = {'critical': 0, 'medium': 1, 'low': 2}
    stale_issues.sort(key=lambda x: severity_order.get(x['severity'], 99))
    
    # Output summary
    print(f"=== EDGA CLAIM ANALYSIS ===")
    print(f"Current time: {current_time.isoformat()}")
    print(f"Total messages: {len(all_messages)} (audit:{len(audit_messages)}, backroom:{len(backroom_messages)})")
    print(f"EDGA tasks tracked: {len(edga_claims)}")
    print(f"Issues flagged: {len(stale_issues)}")
    print()
    
    for issue in stale_issues:
        print(f"[{issue['severity'].upper()}] {issue['edga_id']}")
        print(f"  Agents: {', '.join(issue['agents'])}")
        print(f"  Age: {issue['age_hours']:.1f}h | Blocker: {issue['blocker']}")
        print(f"  Action: {issue['action']}")
        print()
    
    # Generate triage report
    report = format_triage_report(stale_issues, len(edga_claims))
    print("=== TRIAGE REPORT (Discord format) ===")
    print(report)
    print()
    print(f"Character count: {len(report)}")
    
    # Save outputs
    output = {
        'scan_time': current_time.isoformat(),
        'total_messages': len(all_messages),
        'edga_tasks_tracked': len(edga_claims),
        'issues_flagged': len(stale_issues),
        'stale_issues': stale_issues,
        'triage_report': report
    }
    
    with open('/tmp/edga_analysis.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    with open('/tmp/triage_report.txt', 'w') as f:
        f.write(report)
    
    print(f"\nSaved to: /tmp/edga_analysis.json, /tmp/triage_report.txt")


if __name__ == "__main__":
    main()
