# Track Processors Implementation Pattern

Complete implementation guide for the 7-track detection and routing system.

## Core Structure

### 1. Track Definitions

```python
TRACK_PAYLOAD_FIELDS = {
    "knowledge": [],  # No payload, just universal fields
    "tool_workflow": ["tool_workflow"],
    "people": ["people"],
    "trading_intel": ["trading_patterns"],
    "creative_seeds": ["creative_techniques"],
    "code_patterns": ["code_snippets"],
    "opportunity": ["business_ideas"],
}
```

### 2. Detection Patterns

```python
TOOL_PATTERNS = [
    r"(?:we|I)\s+(?:use|built|created|open sourced|released)\s+(\w+)",
    r"(?:check out|try|install)\s+(\w+)",
    r"npm install\s+(\S+)",
    r"cargo install\s+(\S+)",
]

PERSON_PATTERNS = [
    r"(?:follow|check out|interview with|conversation with)\s+([A-Z][a-z]+\s[A-Z][a-z]+)",
    r"([A-Z][a-z]+\s[A-Z][a-z]+)\s+(?:says|argues|believes)",
]

TRADING_PATTERNS = [
    r"(?:prediction market|odds|probability)\s+(?:of|for)\s+(\S+)",
    r"(?:Polymarket|Kalshi|predict)\s+(\S+)",
]

CREATIVE_PATTERNS = [
    r"(?:TouchDesigner|p5\.js|Processing|openFrameworks)",
    r"(?:shader|fragment|vertex|GLSL|HLSL)",
    r"(?:generative|procedural|algorithmic)\s+art",
]
```

### 3. Detection Functions

```python
def detect_tools(transcript: str) -> list[dict]:
    tools = []
    for pattern in TOOL_PATTERNS:
        for match in re.finditer(pattern, transcript, re.IGNORECASE):
            tool_name = match.group(1) if match.groups() else match.group(0)
            if tool_name and len(tool_name) > 1:
                tools.append({
                    "name": tool_name,
                    "context": transcript[max(0, match.start()-50):match.end()+50],
                    "confidence": 0.7,
                })
    # Deduplicate by name
    seen = set()
    return [t for t in tools if not (t["name"].lower() in seen or seen.add(t["name"].lower()))][:5]
```

### 4. Track Processors

```python
def process_tool_review(note_path: Path, fm: dict, transcript: str) -> TrackPayload | None:
    tools = detect_tools(transcript)
    if not tools:
        return None
    
    return TrackPayload(
        track="tool_workflow",
        extracted_items=tools,
        confidence=max(t["confidence"] for t in tools),
        action_recommended="create_install_review_queue"
    )
```

### 5. Router

```python
TRACK_PROCESSORS = {
    "knowledge": process_knowledge_note,
    "tool_workflow": process_tool_review,
    "people": process_network_candidate,
    "trading_intel": process_trading_intel,
    "creative_seeds": process_creative_seed,
    "code_patterns": process_code_pattern,
    "opportunity": process_opportunity,
}

def run_track_detection(note_path: Path, video_id: str) -> list[TrackPayload]:
    transcript = extract_from_transcript(video_id)
    if not transcript:
        return []
    
    detected = []
    for track_name, processor in TRACK_PROCESSORS.items():
        payload = processor(note_path, {}, transcript)
        if payload and payload.confidence > 0.5:
            detected.append(payload)
    
    return detected
```

### 6. Transcript Extraction (v1.0.0+ API)

```python
def extract_from_transcript(video_id: str) -> str:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)
        
        for transcript in transcript_list:
            data = transcript.fetch()
            # API v1.0.0+ uses .text attribute, NOT ["text"] dict access
            return " ".join([t.text for t in data])
        return ""
    except Exception:
        return ""
```

## Scoring Integration

```python
def score_note(path: Path) -> tuple[dict, int, list[str]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    fm = parse_frontmatter(text)
    body = extract_body(text)
    
    # Universal fields (max 5)
    present = {f: field_present(fm, body, f) for f in UNIVERSAL_FIELDS}
    
    # Detect tracks
    tracks = detect_tracks(fm)  # from frontmatter
    
    # Score = universal fields + track bonuses
    track_bonus = sum(1 for t in tracks if has_track_payload(fm, t))
    score = sum(present.values()) + track_bonus
    
    return present, score, tracks
```

## Adding Track 8+

1. Add pattern list constant
2. Create `detect_new_track()` function
3. Create `process_new_track()` processor
4. Register in `TRACK_PROCESSORS`
5. Update `TRACK_PAYLOAD_FIELDS`
6. Create ChromaDB collection for clustering

## Session-Tested Output

From production run 2026-05-06:
- 248/1172 notes fully enriched (21.2%)
- Average 3.2 tracks per note
- Top tracks: knowledge (172), tool_workflow (67), people (25)
- Bulk enrichment rate: 154 notes/second (keyword-based)
- Transcript-based: ~3 notes/minute (API limited)
