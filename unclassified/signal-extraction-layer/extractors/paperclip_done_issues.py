"""Paperclip Done Issues Extractor - Extracts signals from completed issues"""

import json
import sys
import subprocess
from datetime import datetime
from typing import List, Optional
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))
from schema import Signal, SourceRef, generate_signal_id

class PaperclipDoneExtractor:
    """Extracts signals from Paperclip done/completed issues"""
    
    CATEGORIES = {
        "decision": ["decided", "chose", "selected", "opted for", "went with"],
        "lesson-learned": ["learned", "realized", "discovered", "understood that", "turns out"],
        "gotcha": ["gotcha", "pitfall", "watch out", "beware", "careful", "caution", "avoid"],
        "reusable-pattern": ["pattern", "works well", "best practice", "standard approach", "template"]
    }
    
    def __init__(self, base_url: str = "http://127.0.0.1:3100/api"):
        self.base_url = base_url
        self.extracted_by = "paperclip_done_extractor_v1"
    
    def _api_call(self, endpoint: str) -> dict:
        """Make API call to Paperclip"""
        result = subprocess.run(
            ['curl', '-s', f'{self.base_url}/{endpoint}'],
            capture_output=True, text=True
        )
        return json.loads(result.stdout) if result.stdout else {}
    
    def _detect_category(self, text: str) -> Optional[str]:
        """Detect signal category from text using keyword patterns"""
        text_lower = text.lower()
        for category, keywords in self.CATEGORIES.items():
            for kw in keywords:
                if kw in text_lower:
                    return category
        return None
    
    def _extract_confidence(self, text: str) -> float:
        """Estimate confidence based on explicit markers"""
        text_lower = text.lower()
        if any(x in text_lower for x in ["definitely", "certainly", "confirmed"]):
            return 0.95
        if any(x in text_lower for x in ["probably", "likely", "seems"]):
            return 0.75
        if any(x in text_lower for x in ["maybe", "unclear", "unsure"]):
            return 0.55
        return 0.80
    
    def extract_from_issue(self, issue: dict) -> List[Signal]:
        """Extract signals from a single done issue"""
        signals = []
        
        issue_id = issue.get('identifier', issue.get('id', 'unknown'))
        title = issue.get('title', '')
        description = issue.get('description', '')
        comments = self._api_call(f'issues/{issue.get("id")}/comments') if issue.get('id') else []
        
        # Extract from title
        if title:
            cat = self._detect_category(title)
            if cat:
                signals.append(Signal(
                    id=generate_signal_id("paperclip", issue_id, cat, 0),
                    category=cat,
                    quote=title,
                    paraphrase=title[:200],
                    confidence=self._extract_confidence(title),
                    source=SourceRef(
                        kind="paperclip",
                        identifier=issue_id,
                        url=f"{self.base_url}/issues/{issue.get('id')}",
                        location_hint="title"
                    ),
                    extracted_by=self.extracted_by,
                    metadata={
                        "issue_status": issue.get('status'),
                        "priority": issue.get('priority'),
                        "completed_at": issue.get('completedAt')
                    }
                ))
        
        # Extract from description sections
        if description:
            sections = self._parse_sections(description)
            for idx, (section_name, content) in enumerate(sections.items()):
                cat = self._detect_category(content)
                if cat and len(content) > 50:
                    signals.append(Signal(
                        id=generate_signal_id("paperclip", issue_id, cat, idx+1),
                        category=cat,
                        sub_tags=[section_name.lower().replace(' ', '-')],
                        quote=content[:500],
                        paraphrase=self._paraphrase(content),
                        confidence=self._extract_confidence(content) * 0.9,
                        source=SourceRef(
                            kind="paperclip",
                            identifier=issue_id,
                            url=f"{self.base_url}/issues/{issue.get('id')}",
                            location_hint=f"section:{section_name}"
                        ),
                        extracted_by=self.extracted_by
                    ))
        
        # Extract from completion comments
        for cidx, comment in enumerate(comments):
            body = comment.get('body', '')
            cat = self._detect_category(body)
            if cat and len(body) > 30:
                signals.append(Signal(
                    id=generate_signal_id("paperclip", issue_id, cat, f"c{cidx}"),
                    category=cat,
                    quote=body[:500],
                    paraphrase=self._paraphrase(body),
                    confidence=self._extract_confidence(body) * 0.85,
                    source=SourceRef(
                        kind="paperclip",
                        identifier=issue_id,
                        url=f"{self.base_url}/issues/{issue.get('id')}/comments",
                        location_hint=f"comment:{cidx}"
                    ),
                    extracted_by=self.extracted_by
                ))
        
        return signals
    
    def _parse_sections(self, markdown: str) -> dict:
        """Parse markdown into sections by header"""
        sections = {"general": ""}
        current_section = "general"
        
        for line in markdown.split('\n'):
            if line.startswith('## ') or line.startswith('### '):
                current_section = line.strip('# ').strip()
                sections[current_section] = ""
            else:
                sections[current_section] += line + '\n'
        
        return {k: v.strip() for k, v in sections.items() if v.strip()}
    
    def _paraphrase(self, text: str) -> str:
        """Simple paraphrase - first sentence or first 150 chars"""
        sentences = text.split('. ')
        if sentences:
            first = sentences[0][:150]
            return first + ('...' if len(first) == 150 else '')
        return text[:150] + ('...' if len(text) > 150 else '')
    
    def extract_batch(self, days_back: int = 30, limit: int = 100) -> List[Signal]:
        """Extract signals from recent done issues"""
        # Get done issues
        company_id = "c5ea22fb-99d2-46a1-87c6-e7fc1ab0d712"
        issues = self._api_call(f'companies/{company_id}/issues?status=done&limit={limit}')
        
        all_signals = []
        if isinstance(issues, list):
            for issue in issues:
                try:
                    signals = self.extract_from_issue(issue)
                    all_signals.extend(signals)
                except Exception as e:
                    print(f"Error extracting from {issue.get('identifier')}: {e}", file=sys.stderr)
        
        return all_signals

if __name__ == "__main__":
    extractor = PaperclipDoneExtractor()
    signals = extractor.extract_batch(days_back=30, limit=50)
    
    # Output as JSONL
    for sig in signals:
        print(sig.model_dump_json())
    
    print(f"\nExtracted {len(signals)} signals", file=sys.stderr)
