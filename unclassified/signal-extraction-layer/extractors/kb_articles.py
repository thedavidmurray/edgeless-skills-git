"""KB Articles Extractor - Extracts signals from vault knowledge base articles"""

import json
import sys
import re
from datetime import datetime
from typing import List, Optional
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))
from schema import Signal, SourceRef, generate_signal_id

class KBArticleExtractor:
    """Extracts signals from KB articles in the vault"""
    
    CATEGORIES = {
        "framework": ["framework", "architecture", "pattern", "structure", "design"],
        "formula": ["formula", "equation", "calculation", "algorithm", "computation"],
        "claim": ["claim", "assertion", "proposition", "hypothesis", "theory"],
        "methodology": ["methodology", "method", "process", "procedure", "workflow", "systematic"]
    }
    
    def __init__(self):
        self.extracted_by = "kb_article_extractor_v1"
        self.vault_paths = [
            Path.home() / "claude-projects/claude-vault/03-Knowledge"
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
        if any(x in text_lower for x in ["proven", "validated", "tested", "evidence"]):
            return 0.92
        if any(x in text_lower for x in ["research suggests", "studies show", "data indicates"]):
            return 0.85
        if any(x in text_lower for x in ["may", "might", "could", "possibly"]):
            return 0.65
        return 0.75
    
    def _find_kb_files(self) -> List[Path]:
        """Find all KB article files"""
        files = []
        for base_path in self.vault_paths:
            if base_path.exists():
                files.extend(base_path.glob("**/*.md"))
                files.extend(base_path.glob("**/*.json"))
        return files
    
    def _parse_sections(self, markdown: str) -> dict:
        """Parse markdown into sections by header"""
        sections = {"general": ""}
        current_section = "general"
        
        for line in markdown.split('\n'):
            if line.startswith('## ') or line.startswith('### ') or line.startswith('# '):
                current_section = line.strip('# ').strip()
                sections[current_section] = ""
            else:
                sections[current_section] += line + '\n'
        
        return {k: v.strip() for k, v in sections.items() if v.strip()}
    
    def extract_from_file(self, filepath: Path) -> List[Signal]:
        """Extract signals from a single KB article"""
        signals = []
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            return signals
        
        # Parse sections
        sections = self._parse_sections(content)
        
        # Extract from each section
        for section_name, section_content in sections.items():
            # Split into paragraphs
            paragraphs = [p.strip() for p in section_content.split('\n\n') if len(p.strip()) > 100]
            
            for pidx, para in enumerate(paragraphs[:5]):  # Limit paragraphs per section
                cat = self._detect_category(para)
                if cat:
                    file_id = f"{filepath.parent.name}/{filepath.stem}"
                    signals.append(Signal(
                        id=generate_signal_id("kb", file_id, cat, pidx),
                        category=cat,
                        sub_tags=[section_name.lower().replace(' ', '-')[:30]],
                        quote=para[:500],
                        paraphrase=para[:150] + ('...' if len(para) > 150 else ''),
                        confidence=self._extract_confidence(para),
                        source=SourceRef(
                            kind="kb",
                            identifier=file_id,
                            path=str(filepath),
                            location_hint=f"section:{section_name},para:{pidx}"
                        ),
                        extracted_by=self.extracted_by,
                        metadata={
                            "file_size": filepath.stat().st_size,
                            "word_count": len(content.split())
                        }
                    ))
        
        return signals
    
    def extract_batch(self, limit: int = 500) -> List[Signal]:
        """Extract signals from KB articles"""
        files = self._find_kb_files()
        all_signals = []
        
        for filepath in files[:100]:  # Limit files processed
            try:
                signals = self.extract_from_file(filepath)
                all_signals.extend(signals)
                if len(all_signals) >= limit:
                    break
            except Exception as e:
                print(f"Error processing {filepath}: {e}", file=sys.stderr)
        
        return all_signals[:limit]

if __name__ == "__main__":
    extractor = KBArticleExtractor()
    signals = extractor.extract_batch(limit=200)
    
    # Output as JSONL
    for sig in signals:
        print(sig.model_dump_json())
    
    print(f"\nExtracted {len(signals)} signals from KB articles", file=sys.stderr)
