#!/usr/bin/env python3
"""
Verify track processor functionality.
Run this after updating track_processors.py to ensure all patterns work.
"""

import sys
from pathlib import Path

def verify_imports():
    """Step 1: Verify track_processors module imports."""
    print("[1/4] Checking imports...")
    try:
        sys.path.insert(0, '/Users/djm/claude-projects/scripts/youtube_intelligence')
        from track_processors import (
            suggest_tracks, run_track_detection, TrackPayload,
            TRACK_PROCESSORS, detect_tools, detect_people
        )
        print("  ✅ All imports successful")
        return True
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False


def verify_transcript_api():
    """Step 2: Verify YouTube transcript API works (v1.0.0+ compatible)."""
    print("\n[2/4] Checking YouTube transcript API...")
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list("dQw4w9WgXcQ")  # Rickroll - always available
        
        for transcript in transcript_list:
            data = transcript.fetch()
            text = " ".join([t.text for t in data[:5]])  # Just first 5 snippets
            print(f"  ✅ API working (fetched {len(text)} chars)")
            return True
        
        print("  ⚠️ No transcripts found")
        return False
        
    except Exception as e:
        print(f"  ❌ API error: {e}")
        return False


def verify_pattern_detection():
    """Step 3: Test pattern detection on sample text."""
    print("\n[3/4] Testing pattern detection...")
    
    sys.path.insert(0, '/Users/djm/claude-projects/scripts/youtube_intelligence')
    from track_processors import detect_tools, detect_people, detect_code_patterns
    
    # Sample texts
    tool_text = "You should try uv for Python packaging. We use cargo install for Rust tools."
    people_text = "Follow Andrej Karpathy for AI insights. Check out Simon Willison's blog."
    code_text = "```python\ndef memoize(f):\n    cache = {}\n    return cache\n```"
    
    results = {
        "tools": len(detect_tools(tool_text)) > 0,
        "people": len(detect_people(people_text)) > 0,
        "code": len(detect_code_patterns(code_text)) > 0,
    }
    
    for name, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {name} detection")
    
    return all(results.values())


def verify_track_routing():
    """Step 4: Verify track routing to correct processors."""
    print("\n[4/4] Checking track routing...")
    
    sys.path.insert(0, '/Users/djm/claude-projects/scripts/youtube_intelligence')
    from track_processors import TRACK_PROCESSORS
    
    expected_tracks = [
        "knowledge", "tool_workflow", "people", "trading_intel",
        "creative_seeds", "code_patterns", "opportunity"
    ]
    
    all_present = all(t in TRACK_PROCESSORS for t in expected_tracks)
    
    for track in expected_tracks:
        status = "✅" if track in TRACK_PROCESSORS else "❌"
        print(f"  {status} {track}")
    
    return all_present


def main():
    print("=" * 50)
    print("Multi-Track Enrichment System Verification")
    print("=" * 50)
    
    checks = [
        verify_imports(),
        verify_transcript_api(),
        verify_pattern_detection(),
        verify_track_routing(),
    ]
    
    passed = sum(checks)
    total = len(checks)
    
    print("\n" + "=" * 50)
    if passed == total:
        print(f"✅ All {total} checks passed")
        return 0
    else:
        print(f"⚠️  {passed}/{total} checks passed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
