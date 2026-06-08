#!/usr/bin/env python3
"""
Nightly Skill Review & Establishment Pipeline
Analyzes agent activities, identifies skill gaps, recommends new skill creation
Posts digest to Discord #audit-log, creates Paperclip issues for skill gaps
"""

import json
import urllib.request
import subprocess
import os
import re
from datetime import datetime, timedelta
from collections import Counter, defaultdict

# Configuration
PAPERCLIP_URL = "http://127.0.0.1:3100"
COMPANY_ID = "c5ea22fb-99d2-46a1-87c6-e7fc1ab0d712"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1494511983326658620/_mv7NOacE7VgQRG30VDSCPmAycs8mG_Vezg8cF4cPVlZFhMXJNDvCZdmUcXh9Ns5uT8o"

def api_get(path):
    url = f"{PAPERCLIP_URL}/api/{path}"
    with urllib.request.urlopen(url, timeout=10) as resp:
        return json.loads(resp.read().decode())

def post_discord(content, embeds=None):
    payload = {
        "username": "Skill-Reviewer",
        "content": content,
        "embeds": embeds or []
    }
    # Use curl to avoid SSL issues in cron context
    result = subprocess.run(
        ['curl', '-s', '-X', 'POST', DISCORD_WEBHOOK,
         '-H', 'Content-Type: application/json',
         '-d', json.dumps(payload)],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        print(f"Discord post failed: {result.stderr}")

def create_issue(title, description, priority="medium", assignee=None):
    payload = {
        "title": title,
        "description": description,
        "priority": priority,
        "status": "todo",
        "companyId": COMPANY_ID
    }
    if assignee:
        payload["assigneeAgentId"] = assignee
    
    url = f"{PAPERCLIP_URL}/api/companies/{COMPANY_ID}/issues"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}

def main():
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    
    # Fetch data
    agents = api_get(f"companies/{COMPANY_ID}/agents")
    issues = api_get(f"companies/{COMPANY_ID}/issues")
    
    # Get recent runs for activity analysis
    recent_runs = []
    for agent in agents:
        try:
            runs = api_get(f"companies/{COMPANY_ID}/agents/{agent['id']}/runs")
            recent_runs.extend(runs[-5:] if runs else [])
        except:
            pass
    
    # Analyze activity patterns for skill gaps
    agent_skills_used = defaultdict(set)
    error_patterns = Counter()
    tool_failures = Counter()
    
    for run in recent_runs:
        agent_id = run.get('agentId')
        result = run.get('result', '')
        error = run.get('error', '')
        
        # Detect skill usage from result content
        if 'skill' in result.lower():
            skills_found = re.findall(r'[\w-]+-skill|skill/[\w-]+', result.lower())
            if agent_id:
                agent_skills_used[agent_id].update(skills_found)
        
        # Detect error patterns indicating skill gaps
        if error:
            if 'not found' in error.lower() or 'no such file' in error.lower():
                error_patterns['missing_tool/skill'] += 1
            if 'api' in error.lower() and 'key' in error.lower():
                error_patterns['api_auth_failure'] += 1
            if 'timeout' in error.lower():
                error_patterns['timeout_network'] += 1
            if 'parse' in error.lower() or 'json' in error.lower():
                error_patterns['parsing_failure'] += 1
    
    # Identify agents without skill diversity
    low_skill_diversity = []
    for agent in agents:
        skills = agent_skills_used.get(agent['id'], set())
        if len(skills) < 2 and agent['status'] == 'running':
            low_skill_diversity.append({
                'name': agent['name'],
                'skills': len(skills),
                'id': agent['id']
            })
    
    # Analyze backlog for skill gaps
    backlog = [i for i in issues if i.get('status') in ['backlog', 'todo']]
    backlog_skill_requests = Counter()
    
    for issue in backlog:
        title = issue.get('title', '').lower()
        desc = (issue.get('description') or '').lower()
        text = title + ' ' + desc
        
        if any(x in text for x in ['mcp', 'api', 'integration', 'webhook']):
            backlog_skill_requests['mcp_builder'] += 1
        if any(x in text for x in ['pine', 'tradingview', 'backtest']):
            backlog_skill_requests['trading_automation'] += 1
        if any(x in text for x in ['youtube', 'transcript', 'summarize']):
            backlog_skill_requests['youtube_pipeline'] += 1
        if any(x in text for x in ['plotter', 'art', 'generative', 'svg']):
            backlog_skill_requests['generative_art'] += 1
        if any(x in text for x in ['chroma', 'vector', 'embedding', 'rag']):
            backlog_skill_requests['vector_db'] += 1
        if any(x in text for x in ['discord', 'telegram', 'notify']):
            backlog_skill_requests['messaging'] += 1
    
    # Build recommendations
    skill_recommendations = []
    
    if backlog_skill_requests['mcp_builder'] >= 3:
        skill_recommendations.append({
            'skill': 'mcp-server-scaffold',
            'reason': f"{backlog_skill_requests['mcp_builder']} backlog items need MCP integrations",
            'priority': 'high' if backlog_skill_requests['mcp_builder'] >= 5 else 'medium'
        })
    
    if backlog_skill_requests['trading_automation'] >= 2:
        skill_recommendations.append({
            'skill': 'tradingview-pine-automation',
            'reason': f"{backlog_skill_requests['trading_automation']} trading tasks pending Pine Script automation",
            'priority': 'high'
        })
    
    if backlog_skill_requests['generative_art'] >= 2:
        skill_recommendations.append({
            'skill': 'pen-plotter-driver',
            'reason': f"{backlog_skill_requests['generative_art']} art/plotter tasks -- skill gap confirmed",
            'priority': 'medium'
        })
    
    if error_patterns['missing_tool/skill'] >= 3:
        skill_recommendations.append({
            'skill': 'tool-discovery-bridge',
            'reason': f"{error_patterns['missing_tool/skill']} 'not found' errors -- agents need tool discovery",
            'priority': 'high'
        })
    
    # Build Discord digest
    embeds = [{
        "title": f"Nightly Skill Review -- {now.strftime('%Y-%m-%d')}",
        "description": f"Activity Summary\n-- {len(agents)} agents checked\n-- {len(recent_runs)} recent runs analyzed\n-- {len(low_skill_diversity)} agents with low skill diversity",
        "color": 5763719,
        "fields": [
            {"name": "Skill Needs", "value": '\n'.join([f"{k}: {v}" for k, v in backlog_skill_requests.most_common(5)]) or "None detected", "inline": True},
            {"name": "Error Patterns", "value": '\n'.join([f"{k}: {v}" for k, v in error_patterns.most_common(4)]) or "No errors", "inline": True}
        ]
    }]
    
    if skill_recommendations:
        recs_text = '\n'.join([f"{r['priority'].upper()} -- {r['skill']}\n{r['reason']}" for r in skill_recommendations[:3]])
        embeds.append({
            "title": "Skill Establishment Recommendations",
            "description": recs_text,
            "color": 15548997 if any(r['priority'] == 'high' for r in skill_recommendations) else 3447003
        })
    
    post_discord(f"Nightly Skill Review Complete -- {now.strftime('%H:%M UTC')}", embeds)
    
    # Create Paperclip issues for high-priority skill gaps
    builder = next((a for a in agents if a['name'] == 'Builder'), None)
    assignee = builder['id'] if builder else None
    
    for rec in skill_recommendations:
        if rec['priority'] == 'high':
            issue = create_issue(
                f"Establish Skill: {rec['skill']}",
                f"Auto-generated from nightly skill review\n\n{rec['reason']}\n\nRecommended approach:\n1. Check skills hub for existing solutions\n2. Scaffold new skill if gap confirmed\n3. Test with 2-3 backlog tasks\n4. Document and register",
                priority="high",
                assignee=assignee
            )
            print(f"Created issue for {rec['skill']}: {issue.get('id', 'error')}")
    
    # Log completion
    with open('/tmp/nightly-skill-review.log', 'a') as f:
        f.write(f"{now.isoformat()}: Reviewed {len(agents)} agents, {len(recent_runs)} runs, {len(skill_recommendations)} recommendations\n")
    
    print(f"Review complete: {len(skill_recommendations)} skill recommendations")

if __name__ == '__main__':
    main()
