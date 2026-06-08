#!/usr/bin/env python3
"""Signals CLI - Query the Signal Extraction Layer"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))

def query_signals(query: str = None, source: str = None, category: str = None, limit: int = 10):
    """Query signals collection from vault storage"""
    
    vault_path = Path.home() / "claude-projects/claude-vault/03-Knowledge/Signals"
    
    signals = []
    if vault_path.exists():
        for source_dir in vault_path.iterdir():
            if source_dir.is_dir():
                for cat_dir in source_dir.iterdir():
                    if cat_dir.is_dir():
                        for sig_file in cat_dir.glob("*.json"):
                            try:
                                with open(sig_file) as f:
                                    signals.append(json.load(f))
                            except:
                                pass
    
    # Filter by source
    filtered = signals
    if source:
        filtered = [s for s in filtered if s.get('source', {}).get('kind') == source]
    
    # Filter by category
    if category:
        filtered = [s for s in filtered if s.get('category') == category]
    
    # Text search on query
    if query and query.strip():
        query_lower = query.lower()
        filtered = [
            s for s in filtered 
            if query_lower in s.get('quote', '').lower() 
            or query_lower in s.get('paraphrase', '').lower()
            or any(query_lower in t.lower() for t in s.get('sub_tags', []))
        ]
    
    # Sort by confidence descending
    filtered.sort(key=lambda s: s.get('confidence', 0), reverse=True)
    
    return filtered[:limit]

def main():
    parser = argparse.ArgumentParser(description="Query Signal Extraction Layer")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--source", "-s", help="Filter by source (youtube, paperclip, rss, etc)")
    parser.add_argument("--category", "-c", help="Filter by category (decision, lesson-learned, etc)")
    parser.add_argument("--limit", "-n", type=int, default=10, help="Limit results")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    results = query_signals(args.query, args.source, args.category, args.limit)
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"Found {len(results)} signals:\n")
        for i, sig in enumerate(results, 1):
            print(f"[{i}] {sig.get('category', 'unknown')} | {sig.get('source', {}).get('kind', 'unknown')}")
            print(f"    {sig.get('paraphrase', sig.get('quote', 'N/A'))[:100]}...")
            print(f"    ID: {sig.get('id', 'N/A')}")
            print(f"    Confidence: {sig.get('confidence', 'N/A')}")
            print()

if __name__ == "__main__":
    main()
