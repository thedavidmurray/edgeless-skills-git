"""Agent Heartbeat Extractor - Extracts signals from agent heartbeat/cron outputs"""

import json
import sys
import re
from datetime import datetime
from typing import List, Optional
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))
from schema import Signal, SourceRef, generate_signal_id

class AgentHeartbeatExtractor:
    """Extracts signals from agent heartbeat and cron output logs"""
    
    CATEGORIES = {
        "finding": ["found", "discovered", "identified", "detected", "observed", "noticed"],
        "anomaly": ["anomaly", "unexpected", "unusual", "strange", "weird", "abnormal", "deviation"],
        "blocker": ["blocked", "stuck", "cannot proceed", "failing", "broken", "unavailable", "down"],
        "surprise": ["surprisingly", "unexpectedly", "did not expect", "strangely", "curiously"],
        "lesson-learned": ["lesson", "learned", "realized", "should have", "turns out"]
    }
    
    def __init__(self):
        self.extracted_by = "agent_heartbeat_extractor_v1"
        self.heartbeat_paths = [
            Path.home() / "claude-vault/13-Reports/agent-heartbeats",
            Path.home() / ".hermes/logs",
            Path.home() / "claude-projects/scripts/cron/logs"
        ]
    
    def _detect_category(self, text: str) -> Optional[str]:
        """Detect signal category from text using keyword patterns"""
        text_lower = text.lower()
        scores = {}
        for category, keywords in self.CATEGORIES.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[category] = score
        
        if scores:
            return max(scores, key=scores.get)
        return None
    
    def _extract_confidence(self, text: str) -> float:
        """Estimate confidence based on explicit markers"""
        text_lower = text.lower()
        if any(x in text_lower for x in ["confirmed", "verified", "certainly", "definitely"]):
            return 0.9
        if any(x in text_lower for x in ["likely", "probably", "appears"]):
            return 0.75
        if any(x in text_lower for x in ["maybe", "possibly", "suspect"]):
            return 0.6
        return 0.7
    
    def _find_heartbeat_files(self) -> List[Path]:
        """Find all heartbeat log files"""
        files = []
        for base_path in self.heartbeat_paths:
            if base_path.exists():
                # Look for JSONL, JSON, and .log files
                files.extend(base_path.glob("**/*.jsonl"))
                files.extend(base_path.glob("**/*.json"))
                files.extend(base_path.glob("**/*.log"))
                files.extend(base_path.glob("**/*heartbeat*"))
        return files
    
    def _parse_timestamp(self, text: str) -> Optional[str]:
        """Try to extract timestamp from log line"""
        # Common patterns: 2026-05-05, 2026/05/05, ISO timestamps
        patterns = [
            r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})',
            r'(\d{4}-\d{2}-\d{2})',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None
    
    def extract_from_file(self, filepath: Path) -> List[Signal]:
        """Extract signals from a single heartbeat log file"""
        signals = []
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            return signals
        
        # Try to parse as JSON/JSONL first
        lines = content.strip().split('\n')
        
        for idx, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Try JSON parsing
            try:
                data = json.loads(line)
                # Extract from structured log
                text = data.get('message', data.get('output', data.get('result', str(data))))
                timestamp = data.get('timestamp', self._parse_timestamp(line))
            except json.JSONDecodeError:
                # Treat as plain text log line
                text = line
                timestamp = self._parse_timestamp(line)
            
            # Skip short lines
            if len(text) < 40:
                continue
            
            # Detect category
            cat = self._detect_category(text)
            if cat:
                file_id = f"{filepath.stem}-{idx}"
                signals.append(Signal(
                    id=generate_signal_id("agent_heartbeat", file_id, cat, 0),
                    category=cat,
                    sub_tags=[filepath.stem[:20]],
                    quote=text[:500],
                    paraphrase=text[:150] + ('...' if len(text) > 150 else ''),
                    confidence=self._extract_confidence(text),
                    source=SourceRef(
                        kind="agent_heartbeat",
                        identifier=file_id,
                        path=str(filepath),
                        location_hint=f"line:{idx}" if timestamp is None else f"timestamp:{timestamp}"
                    ),
                    extracted_by=self.extracted_by,
                    metadata={
                        "file_size": filepath.stat().st_size if filepath.exists() else 0,
                        "timestamp": timestamp
                    }
                ))
        
        return signals
    
    def extract_batch(self, limit: int = 500) -> List[Signal]:
        """Extract signals from all heartbeat sources"""
        files = self._find_heartbeat_files()
        all_signals = []
        
        for filepath in files[:50]:  # Limit files processed
            try:
                signals = self.extract_from_file(filepath)
                all_signals.extend(signals)
                if len(all_signals) >= limit:
                    break
            except Exception as e:
                print(f"Error processing {filepath}: {e}", file=sys.stderr)
        
        return all_signals[:limit]

if __name__ == "__main__":
    extractor = AgentHeartbeatExtractor()
    signals = extractor.extract_batch(limit=200)
    
    # Output as JSONL
    for sig in signals:
        print(sig.model_dump_json())
    
    print(f"\nExtracted {len(signals)} signals from agent heartbeats", file=sys.stderr)
