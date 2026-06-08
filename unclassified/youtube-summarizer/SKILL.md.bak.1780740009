---
name: youtube-summarizer
description: Automatically fetch YouTube video transcripts, generate structured summaries, and build knowledge corpora with multi-track enrichment. Detects YouTube URLs for one-off summaries or batch processing into vault-backed knowledge systems with agent routing.
version: 1.1.0
author: abe238
tags: [youtube, transcription, summarization, video, telegram, enrichment, knowledge-graph]
---

# YouTube Summarizer & Knowledge Builder

Fetch transcripts from YouTube videos — from quick summaries to full **knowledge corpus enrichment** with multi-track routing to specialist agents.

## When to Use

### One-Off Summarization
- User shares a YouTube URL
- Quick summary + key insights
- Send to messaging platform

### Knowledge Corpus Building
- Processing 50+ YouTube likes
- Building topic clusters
- Routing to specialist agents (Kilo/Scribe/Pamela)
- NotebookLM source preparation

**See:** `references/multi-track-enrichment-schema.md` for the full enrichment system.

## Dependencies

**Required:** MCP YouTube Transcript server:
`/root/clawd/mcp-server-youtube-transcript`

Install if missing:
```bash
cd /root/clawd
git clone https://github.com/kimtaeyoon83/mcp-server-youtube-transcript.git
cd mcp-server-youtube-transcript && npm install && npm run build
```

---

## Workflows

### A. Single Video Summary (MCP Server)
Quick one-off summarization.

### B. Batch Likes Processing (yt-dlp)
Cron-scheduled processing. See:
- `references/batch-likes-pipeline.md`
- `templates/batch_likes_processor.py`

Use for: 10+ videos, scheduled jobs, transcript caching.

### C. Multi-Track Enrichment (Knowledge Layer)
**See:** `references/multi-track-enrichment-schema.md`

Builds a **corpus** from YouTube likes with:
- 7 track types (tool_workflow, trading_intel, etc.)
- Hybrid detection (keyword + transcript + ChromaDB)
- Agent routing (Kilo → tools, Scribe → knowledge)
- NotebookLM integration (Tier-3 enrichment)

---

## Single Video Workflow

### 1. Detect YouTube URL
Extract video ID:
- `youtube.com/watch?v=VIDEO_ID`
- `youtu.be/VIDEO_ID`
- `youtube.com/shorts/VIDEO_ID`
- Direct ID: `VIDEO_ID` (11 chars)

### 2. Fetch Transcript
```bash
cd /root/clawd/mcp-server-youtube-transcript && node --input-type=module -e "
import { getSubtitles } from './dist/youtube-fetcher.js';
const result = await getSubtitles({ videoID: 'VIDEO_ID', lang: 'en' });
console.log(JSON.stringify(result, null, 2));
" > /tmp/yt-transcript.json
```

### 3. Process Data
Extract:
- `result.metadata.title`
- `result.metadata.author`
- `result.metadata.viewCount`
- `result.metadata.publishDate`
- `result.lines` → `result.lines.map(l => l.text).join(' ')`

### 4. Generate Summary

```markdown
📹 **Video:** [title]
👤 **Channel:** [author] | 👁️ **Views:** [views] | 📅 **Published:** [date]

**🎯 Main Thesis:**
[1-2 sentence core argument]

**💡 Key Insights:**
- [insight 1]
- [insight 2]
- [insight 3]
- [insight 4]
- [insight 5]

**📝 Notable Points:**
- [supporting point 1]
- [supporting point 2]

**🔑 Takeaway:**
[Actionable conclusion]
```

### 5. Save & Deliver
Save to `/root/clawd/transcripts/YYYY-MM-DD_VIDEO_ID.txt`

**Telegram:** Use `message --action send` with file attachment
**Other:** Reply with summary text

---

## Advanced: Multi-Track Enrichment

For building **knowledge systems** from YouTube, not just summaries.

### The 7 Tracks

| Track | Purpose | Routes To |
|-------|---------|-----------|
| **knowledge** | General curation | Scribe |
| **tool_workflow** | Tool install/review | Kilo/Beau |
| **people** | Network graph | Curator |
| **trading_intel** | Prediction signals | Pamela |
| **creative_seeds** | Generative art | Critic/Specimen |
| **code_patterns** | Snippet extraction | Kilo |
| **opportunity** | Business ideas | Builder |

### Schema

```yaml
---
title: "Video Title"
source: youtube
url: https://www.youtube.com/watch?v=VIDEO_ID
enrichment_tier: 2  # 0=raw, 1=basic, 2=structured, 3=deep
track_tags: [knowledge, tool_workflow]

# Universal fields
context: "Why this matters for your work"
one_liner: "Tweet-length summary"
vault_connections:
  - [[Related-Note-1]]
  - [[Related-Note-2]]
summary: "From transcript"

# Track payloads
tool_workflow:
  - name: "Effect-TS"
    context: "TypeScript functional programming"
    install_status: queued
---
```

### Detection Stack
1. **Keyword matching** — Fast pattern on channel/title
2. **Transcript analysis** — NLP on full text
3. **ChromaDB clustering** — Semantic similarity

See `references/multi-track-enrichment-schema.md` for:
- Full keyword patterns
- Scoring system (5 universal + track bonus)
- Weekly rhythm (assessment → batch → sync → handoff → learn)
- Implementation files

---

## Quality Guidelines

- **Concise:** Scannable in 30 seconds
- **Accurate:** No hallucinations beyond transcript
- **Structured:** Consistent formatting
- **Contextual:** Adjust for video length
  - <5 min: Brief
  - >30 min: Detailed breakdown

---

## Pitfalls

### youtube-transcript-api v1.0.0+ Breaking Change

**OLD (< v1.0.0):**
```python
from youtube_transcript_api import YouTubeTranscriptApi
transcript = YouTubeTranscriptApi.get_transcript(video_id)
text = " ".join([t["text"] for t in transcript])  # ❌ Broken
```

**NEW (v1.0.0+):**
```python
from youtube_transcript_api import YouTubeTranscriptApi
ytt_api = YouTubeTranscriptApi()
transcript_list = ytt_api.list(video_id)
for transcript in transcript_list:
    data = transcript.fetch()
    text = " ".join([t.text for t in data])  # ✅ Use .text attribute
```

**Key changes:**
- `get_transcript()` → `list()` + `fetch()`
- `snippet["text"]` → `snippet.text`
- Returns `FetchedTranscriptSnippet` objects

### Batch Processing Pitfalls

From `references/batch-likes-pipeline.md`:
- **yutu CLI:** No `liked` command exists; use `playlistItem` with OAuth
- **Import errors:** `youtube_intelligence` pipeline has broken `get_async_llm_client` imports
- **yt-dlp JS challenges:** May need `--remote-components` or encounter IP blocking
- **Truncation:** Long videos may hit 8000 char limits; chunk if needed

---

## Related Files

| File | Purpose |
|------|---------|
| `references/multi-track-enrichment-schema.md` | Full enrichment system |
| `references/batch-likes-pipeline.md` | Technical reference for cron jobs |
| `templates/batch_likes_processor.py` | Working Python script |
| `references/youtube-transcript-api-v1-migration.md` | API migration guide |
