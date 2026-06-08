# YouTube Transcript API v1.0.0+ Migration Guide

## Breaking Changes (v0.x to v1.0.0)

The youtube-transcript-api library changed its API significantly in v1.0.0. The old dict-style access patterns are broken.

### Key Changes

| Old (< v1.0.0) | New (v1.0.0+) |
|----------------|---------------|
| `YouTubeTranscriptApi.get_transcript(id)` | `YouTubeTranscriptApi().list(id)` + `fetch()` |
| `snippet["text"]` | `snippet.text` (attribute access) |
| `snippet["start"]` | `snippet.start` |
| `snippet["duration"]` | `snippet.duration` |
| Returns list of dicts | Returns `FetchedTranscript` of `FetchedTranscriptSnippet` objects |

## Migration Examples

### Basic Transcript Fetch

```python
# OLD (< v1.0.0)
from youtube_transcript_api import YouTubeTranscriptApi

transcript = YouTubeTranscriptApi.get_transcript(video_id)
full_text = " ".join([t["text"] for t in transcript])

# NEW (v1.0.0+)
from youtube_transcript_api import YouTubeTranscriptApi

ytt_api = YouTubeTranscriptApi()
transcript_list = ytt_api.list(video_id)

for transcript in transcript_list:
    data = transcript.fetch()
    full_text = " ".join([t.text for t in data])  # Note: .text not ["text"]
    break
```

### With Language Selection

```python
# OLD
transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])

# NEW
transcript_list = ytt_api.list(video_id)
transcript = transcript_list.find_transcript(['en'])
data = transcript.fetch()
```

### Error Handling

```python
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable
)

try:
    ytt_api = YouTubeTranscriptApi()
    transcript_list = ytt_api.list(video_id)
    
    for transcript in transcript_list:
        data = transcript.fetch()
        return " ".join([t.text for t in data])
        
except TranscriptsDisabled:
    return "Transcripts disabled for this video"
except NoTranscriptFound:
    return "No transcript found"
except VideoUnavailable:
    return "Video unavailable"
```

## Object Reference

### FetchedTranscriptSnippet

```python
@dataclass
class FetchedTranscriptSnippet:
    text: str      # Transcript text
    start: float   # Start time in seconds
    duration: float  # Duration in seconds
```

### TranscriptList

```python
transcript_list = ytt_api.list(video_id)

# Available methods:
transcript_list.find_transcript(language_codes=['en'])  # Find by language
transcript_list.find_generated_transcript(language_codes=['en'])
transcript_list.find_manually_created_transcript(language_codes=['en'])

# Iteration:
for transcript in transcript_list:
    print(transcript.language)  # Language name
    print(transcript.language_code)  # e.g., 'en'
    print(transcript.is_generated)  # bool
    data = transcript.fetch()  # Get FetchedTranscript
```

## Version Detection

```python
import youtube_transcript_api

# Check if v1.0.0+
if hasattr(youtube_transcript_api, 'FetchedTranscriptSnippet'):
    print("v1.0.0+ API")
    # Use new API
else:
    print("Legacy v0.x API")
    # Use old API
```

## Common Errors After Upgrade

| Error | Cause | Fix |
|-------|-------|-----|
| `type object has no attribute 'get_transcript'` | Using old API on new version | Use `YouTubeTranscriptApi().list()` |
| `FetchedTranscriptSnippet is not subscriptable` | Using `["text"]` instead of `.text` | Change to `snippet.text` |
| `list_transcripts` not found | Method renamed | Use `list()` method |
| `find_transcript` not found | Moved to TranscriptList object | Call on `transcript_list.find_transcript()` |

## Session Context

**Discovered:** 2026-05-06 during YouTube enrichment campaign
**Impact:** All transcript-dependent skills (youtube-summarizer, multi-track-content-enrichment)  
**Resolution:** Updated to object-attribute access pattern  
**Tested on:** 200+ videos during batch enrichment to 21.2% target
