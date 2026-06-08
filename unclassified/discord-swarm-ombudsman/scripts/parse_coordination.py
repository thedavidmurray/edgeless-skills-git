#!/usr/bin/env python3
"""
Ombudsman Coordination Parser
Parses Discord messages from bot-backroom to identify stale coordination threads.
Usage: python3 parse_coordination.py /tmp/backroom.json
"""

import json
import re
import sys
from datetime import datetime, timezone

# Time thresholds (hours)
STALE_ASSIGNMENT_HOURS = 2
STALE_ONBOARDING_HOURS = 2
STALE_ESCALATION_HOURS = 2
CRITICAL_HUMAN_WAIT_HOURS = 4

ACTIONABLE_TYPES = ["ASSIGNED", "EXECUTE", "ARCH", "ENRICH", "VPS", "TRIAGE", "WELCOME"]

def parse_timestamp(ts_str):
    """Parse ISO8601 timestamp."""
    return datetime.fromisoformat(ts_str.replace('Z', '+00:00'))

def extract_tag(content, tag_name):
    """Extract value from [TAG:value] pattern."""
    match = re.search(rf'\[{tag_name}:([^\]]+)\]', content)
    return match.group(1) if match else None

def has_any_type(content, types):
    """Check if content contains any of the given TYPE values."""
    return any(f"[TYPE:{t}]" in content for t in types)

def analyze_message(msg, current_time):
    """Analyze a single message for stale coordination patterns."""
    content = msg.get("content", "")
    timestamp = parse_timestamp(msg.get("timestamp", current_time.isoformat()))
    age_hours = (current_time - timestamp).total_seconds() / 3600
    
    result = {
        "id": msg.get("id"),
        "timestamp": timestamp.isoformat(),
        "age_hours": round(age_hours, 1),
        "content_preview": content[:100] + "..." if len(content) > 100 else content,
        "from": extract_tag(content, "FROM"),
        "to": extract_tag(content, "TO"),
        "ref": extract_tag(content, "REF"),
        "msg_type": extract_tag(content, "TYPE"),
        "has_ack": "[TYPE:ACK]" in content,
        "has_complete": "[TYPE:COMPLETE]" in content,
        "is_actionable": has_any_type(content, ACTIONABLE_TYPES),
    }
    
    # Determine staleness
    result["is_stale"] = False
    result["stale_reason"] = None
    
    # Work assignment without ACK
    if result["is_actionable"] and not result["has_ack"] and not result["has_complete"]:
        if age_hours > STALE_ASSIGNMENT_HOURS:
            result["is_stale"] = True
            result["stale_reason"] = f"Assignment >{STALE_ASSIGNMENT_HOURS}h, no ACK"
            result["action_required"] = f"ACK from {result['to'] or 'target'}"
    
    # Onboarding without confirmation
    if "[TYPE:WELCOME]" in content and not "[DEPTH:1]" in content:
        if age_hours > STALE_ONBOARDING_HOURS:
            result["is_stale"] = True
            result["stale_reason"] = f"Onboarding >{STALE_ONBOARDING_HOURS}h, no confirmation"
            result["action_required"] = f"[TYPE:ACK][DEPTH:1] from {result['to'] or 'target'}"
    
    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 parse_coordination.py <messages.json>", file=sys.stderr)
        sys.exit(1)
    
    with open(sys.argv[1]) as f:
        messages = json.load(f)
    
    current_time = datetime.now(timezone.utc)
    
    # Sort by timestamp (newest first)
    messages.sort(key=lambda m: m.get("timestamp", ""), reverse=True)
    
    stale_threads = []
    recent_active = []
    
    for msg in messages:
        analysis = analyze_message(msg, current_time)
        
        if analysis["is_stale"]:
            stale_threads.append(analysis)
        elif analysis["is_actionable"] and analysis["age_hours"] < STALE_ASSIGNMENT_HOURS:
            recent_active.append(analysis)
    
    # Output summary
    print(f"📋 Ombudsman Scan Results")
    print(f"Current time: {current_time.isoformat()}")
    print(f"Messages analyzed: {len(messages)}")
    print(f"Stale threads: {len(stale_threads)}")
    print(f"Recent active (<{STALE_ASSIGNMENT_HOURS}h): {len(recent_active)}")
    print()
    
    if stale_threads:
        print("🔴 STALE THREADS:")
        for thread in stale_threads:
            print(f"  • [{thread['ref'] or 'NO-REF'}] → {thread['to'] or 'unknown'}")
            print(f"    Type: [{thread['msg_type']}] | Age: {thread['age_hours']}h")
            print(f"    Action: {thread['action_required']}")
            print()
    
    # Output JSON for downstream processing
    output = {
        "scan_time": current_time.isoformat(),
        "stale_threads": stale_threads,
        "recent_active": recent_active,
        "total_messages": len(messages)
    }
    
    with open("/tmp/ombudsman_results.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"Full results written to: /tmp/ombudsman_results.json")

if __name__ == "__main__":
    main()
