# Batch YouTube Likes Processing Pipeline

Working pattern for processing YouTube liked videos in bulk (cron job compatible).

## Problem with Existing Infrastructure

The `yutu liked --today` command referenced in some prompts **does not exist**. The yutu CLI uses `playlistItem list` with a playlist ID instead. The existing Python pipeline in `~/claude-projects/scripts/youtube_intelligence/` has import errors (missing `get_async_llm_client`).

## Working Solution

Use yt-dlp directly with a Python processing script:

### 1. Delta File Format

Input from: `~/claude-projects/.feeds/youtube-likes-delta.json`
```json
{
  "generated": "2026-04-29T22:55:52.243509+00:00",
  "new_count": 20,
  "videos": [
    {
      "id": "VIDEO_ID",
      "title": "Video Title",
      "channel": "Channel Name",
      "published": "2026-04-29T07:44:11Z",
      "url": "https://youtube.com/watch?v=VIDEO_ID"
    }
  ]
}
```

### 2. Transcript Fetch with yt-dlp

```bash
yt-dlp \
  --write-auto-sub \
  --skip-download \
  --sub-langs en \
  --output "/tmp/yt_%(id)s.%(ext)s" \
  "https://youtube.com/watch?v=VIDEO_ID"
```

Reads: `/tmp/yt_VIDEO_ID.en.vtt`

### 3. VTT Parsing Pattern

```python
import re

def parse_vtt(vtt_content):
    lines = vtt_content.split('\n')
    text_parts = []
    
    for line in lines:
        line = line.strip()
        # Skip headers, timestamps, empty lines
        if not line or line.startswith('WEBVTT') or \
           line.startswith('Kind:') or \
           line.startswith('Language:') or \
           '-->' in line or \
           line.startswith('align:'):
            continue
        # Remove HTML-like tags
        line = re.sub(r'<[^>]+>', '', line)
        if line and not line.isdigit():
            text_parts.append(line)
    
    # Deduplicate while preserving order
    seen = set()
    unique_parts = []
    for part in text_parts:
        if part not in seen and len(part) > 5:
            seen.add(part)
            unique_parts.append(part)
    
    return ' '.join(unique_parts)[:8000]
```

### 4. Technical Scoring (0-10)

Score based on:
- Technical keyword density (AI, code, API, framework, etc.)
- High-value term presence (tutorial, guide, demo, analysis)
- Transcript quality (length > 1000 chars bonus)

### 5. Output Locations

- **Summaries:** `~/claude-vault/03-Knowledge/YouTube/{Channel-Name}/`
- **Archive:** `~/claude-projects/.feeds/youtube-likes-archived.jsonl`
- **Delta export:** `~/claude-projects/.feeds/youtube-likes-delta.json` (mark as "consumed")

### 6. Archive Log Format

```json
{"processed_at": "2026-04-29T16:18:18.422915", "id": "VIDEO_ID", "title": "...", "score": 9.5, "vault_path": "...", "transcript_length": 8000}
```

## Pitfalls

1. **yutu CLI limitation:** No `liked` command - use playlist/playlistItem with proper OAuth
2. **Import errors:** The existing youtube_intelligence pipeline has broken imports
3. **yt-dlp JS challenges:** May need `--remote-components` flag or encounter IP blocking
4. **Transcript limits:** Auto-subtitles may be truncated at 8000 chars for long videos

## Full Working Script

See: `templates/batch_likes_processor.py`
