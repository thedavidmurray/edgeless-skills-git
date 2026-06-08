#!/usr/bin/env python3
"""YouTube Intelligence Agent - Batch Likes Pipeline

Processes YouTube liked videos from delta file:
- Fetches transcripts via yt-dlp
- Scores technical value (0-10)
- Generates markdown summaries
- Archives to vault and JSONL

Usage: python3 batch_likes_processor.py
"""

import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path

# Configuration
DELTA_PATH = Path.home() / "claude-projects" / ".feeds" / "youtube-likes-delta.json"
VAULT_PATH = Path.home() / "claude-vault" / "03-Knowledge" / "YouTube"
ARCHIVE_LOG = Path.home() / "claude-projects" / ".feeds" / "youtube-likes-archived.jsonl"

def extract_transcript(video_id):
    """Fetch transcript using yt-dlp."""
    url = f"https://youtube.com/watch?v={video_id}"
    cmd = [
        "yt-dlp",
        "--write-auto-sub",
        "--skip-download",
        "--sub-langs", "en",
        "--output", f"/tmp/yt_{video_id}.%(ext)s",
        url
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            return None, f"yt-dlp error: {result.stderr[:200]}"
        
        vtt_path = f"/tmp/yt_{video_id}.en.vtt"
        if os.path.exists(vtt_path):
            with open(vtt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            os.remove(vtt_path)
            return parse_vtt(content), None
        return None, "No transcript available"
    except subprocess.TimeoutExpired:
        return None, "Timeout"
    except Exception as e:
        return None, str(e)

def parse_vtt(vtt_content):
    """Parse VTT and extract clean text."""
    lines = vtt_content.split('\n')
    text_parts = []
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('WEBVTT') or \
           line.startswith('Kind:') or line.startswith('Language:') or \
           '-->' in line or line.startswith('align:'):
            continue
        line = re.sub(r'<[^>]+>', '', line)
        if line and not line.isdigit():
            text_parts.append(line)
    
    seen = set()
    unique_parts = []
    for part in text_parts:
        if part not in seen and len(part) > 5:
            seen.add(part)
            unique_parts.append(part)
    
    return ' '.join(unique_parts)[:8000]

def score_technical_value(title, transcript):
    """Score video technical value 0-10."""
    score = 5
    tech_terms = [
        'ai', 'agent', 'code', 'programming', 'api', 'framework', 'database',
        'claude', 'cursor', 'github', 'python', 'javascript', 'llm',
        'architecture', 'system', 'automation', 'workflow', 'docker',
        'kubernetes', 'cloud', 'server', 'microservice', 'devops',
        'machine learning', 'ml', 'neural', 'model', 'training',
        'frontend', 'backend', 'fullstack', 'web', 'app', 'mobile'
    ]
    content = (title + ' ' + (transcript or '')).lower()
    matches = sum(1 for term in tech_terms if term in content)
    score += min(matches * 0.5, 3)
    
    high_value = ['tutorial', 'explained', 'how to', 'guide', 'demo', 'review', 'analysis']
    score += sum(0.5 for term in high_value if term in content)
    
    if transcript and len(transcript) > 1000:
        score += 1
    
    return min(10, max(0, round(score, 1)))

def generate_summary(title, channel, transcript, score):
    """Generate markdown summary for vault storage."""
    summary = f"""---
title: "{title}"
channel: "{channel}"
processed: "{datetime.now().isoformat()}"
score: {score}
type: youtube-summary
tags: [youtube, intelligence]
---

# {title}

**Channel:** {channel}  
**Technical Score:** {score}/10

## Summary
"""
    
    if transcript:
        preview = transcript[:2000].replace('\n', ' ')
        summary += f"\n{preview}...\n\n"
        
        summary += "## Key Insights\n\n"
        sentences = transcript.split('. ')
        insights = []
        tech_keywords = ['AI', 'code', 'agent', 'API', 'system', 'build', 'create']
        for sent in sentences[:20]:
            for kw in tech_keywords:
                if kw.lower() in sent.lower() and 30 < len(sent) < 300:
                    insights.append(sent.strip())
                    break
        
        for insight in insights[:5]:
            summary += f"- {insight}\n"
    else:
        summary += "\n*Transcript unavailable*\n"
    
    summary += f"\n---\n*Processed {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n"
    return summary

def process_videos():
    """Main processing loop."""
    if not DELTA_PATH.exists():
        print(f"No delta file: {DELTA_PATH}")
        return 0, []
    
    with open(DELTA_PATH) as f:
        delta = json.load(f)
    
    videos = delta.get('videos', [])
    print(f"Processing {len(videos)} videos")
    
    processed = []
    errors = []
    VAULT_PATH.mkdir(parents=True, exist_ok=True)
    
    for i, video in enumerate(videos[:20], 1):
        vid = video['id']
        title = video['title']
        channel = video.get('channel', 'Unknown')
        
        print(f"[{i}/{len(videos)}] {title[:50]}...")
        
        transcript, error = extract_transcript(vid)
        if error:
            print(f"  ⚠️  {error}")
            errors.append({'id': vid, 'title': title, 'error': error})
        else:
            print(f"  ✓ {len(transcript)} chars")
        
        score = score_technical_value(title, transcript)
        summary = generate_summary(title, channel, transcript, score)
        
        safe_title = ''.join(c for c in title if c.isalnum() or c in ' -_').replace(' ', '_')[:50]
        channel_dir = VAULT_PATH / channel.replace(' ', '-')
        channel_dir.mkdir(exist_ok=True)
        
        vault_file = channel_dir / f"{vid}_{safe_title}.md"
        with open(vault_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        processed.append({
            'id': vid,
            'title': title,
            'score': score,
            'vault_path': str(vault_file.relative_to(Path.home())),
            'transcript_length': len(transcript) if transcript else 0
        })
    
    with open(ARCHIVE_LOG, 'a') as f:
        for item in processed:
            f.write(json.dumps({'processed_at': datetime.now().isoformat(), **item}) + '\n')
    
    print(f"Done: {len(processed)} processed, {len(errors)} errors")
    return len(processed), errors

if __name__ == '__main__':
    count, errors = process_videos()
