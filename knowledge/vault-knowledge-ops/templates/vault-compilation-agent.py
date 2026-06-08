#!/usr/bin/env python3
"""
Vault Compilation Agent — Starter Template

Copy this file, customize DOMAIN_CONFIG, and run with DRY_RUN=1 first.

Usage:
    DRY_RUN=1 python scripts/{your-agent}.py      # preview
    APPLY=1 python scripts/{your-agent}.py        # write output
"""

import os
import re
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
from typing import Dict, List

# ---------------------------------------------------------------------------
# CONFIG — customize per use case
# ---------------------------------------------------------------------------
VAULT_ROOT = Path("/Users/djm/claude-projects/claude-vault")
OUTPUT_DIR = VAULT_ROOT / "03-Knowledge" / "Synthesis"
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8100"))

DOMAIN_CONFIG = {
    "example-domain": {
        "collections": ["knowledge", "research"],
        "vault_keywords": ["keyword1", "keyword2"],
        "max_files": 100,
    }
}

DRY_RUN = os.getenv("DRY_RUN", "1") == "1" if not os.getenv("APPLY") else False
if os.getenv("APPLY") == "1":
    DRY_RUN = False

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

def fingerprint(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

# ---------------------------------------------------------------------------
# CHROMADB
# ---------------------------------------------------------------------------

def get_chroma_client():
    try:
        import chromadb
        return chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    except Exception as e:
        print(f"[WARN] ChromaDB unavailable: {e}")
        return None

def query_chroma(domain: str, client) -> List[Dict]:
    results = []
    if client is None:
        return results
    cfg = DOMAIN_CONFIG.get(domain, {})
    for coll_name in cfg.get("collections", ["unified_knowledge"]):
        try:
            coll = client.get_collection(coll_name)
            peek = coll.peek(limit=20)
            docs = peek.get("documents", [])
            mets = peek.get("metadatas", [])
            ids = peek.get("ids", [])
            for i, doc in enumerate(docs):
                if doc:
                    results.append({
                        "source": f"chroma:{coll_name}",
                        "id": ids[i] if i < len(ids) else f"{coll_name}-{i}",
                        "content": doc[:800],
                        "metadata": mets[i] if i < len(mets) else {},
                    })
        except Exception as e:
            print(f"[WARN] Collection '{coll_name}' error: {e}")
    return results

# ---------------------------------------------------------------------------
# VAULT SCANNER
# ---------------------------------------------------------------------------

def scan_vault(domain: str) -> List[Dict]:
    files = []
    knowledge_dir = VAULT_ROOT / "03-Knowledge"
    if not knowledge_dir.exists():
        return files
    cfg = DOMAIN_CONFIG.get(domain, {})
    keywords = cfg.get("vault_keywords", [domain])
    max_files = cfg.get("max_files", 100)

    for subdir in knowledge_dir.iterdir():
        if not subdir.is_dir():
            continue
        name_lower = subdir.name.lower()
        if any(kw in name_lower for kw in keywords):
            for md_file in subdir.rglob("*.md"):
                if len(files) >= max_files:
                    break
                try:
                    content = md_file.read_text(encoding="utf-8", errors="ignore")
                    if any(kw in content.lower() or kw in md_file.name.lower() for kw in keywords):
                        files.append({"path": str(md_file.relative_to(VAULT_ROOT)), "content": content})
                except Exception:
                    continue
    return files

# ---------------------------------------------------------------------------
# CONTRADICTION DETECTION
# ---------------------------------------------------------------------------

def detect_duplicate_folders(vault_root: Path) -> List[Dict]:
    knowledge_dir = vault_root / "03-Knowledge"
    if not knowledge_dir.exists():
        return []
    folders = [d.name for d in knowledge_dir.iterdir() if d.is_dir()]
    normalized = {}
    dups = []
    for name in folders:
        key = re.sub(r"[^a-z0-9]+", "", name.lower())
        if key in normalized:
            dups.append({
                "type": "duplicate_folder",
                "canonical": normalized[key],
                "duplicate": name,
                "normalized": key,
                "suggestion": f"Merge '{name}' into '{normalized[key]}' or rename",
            })
        else:
            normalized[key] = name
    return dups

def detect_stale_refs(vault_files: List[Dict], vault_root: Path) -> List[Dict]:
    stale = []
    existing_paths = set()
    for root, _, ffiles in os.walk(vault_root):
        for f in ffiles:
            if f.endswith(".md"):
                rel = os.path.relpath(os.path.join(root, f), vault_root)
                existing_paths.add(rel)
                existing_paths.add(os.path.splitext(rel)[0])
    for vf in vault_files:
        links = re.findall(r"\[\[([^\]]+)\]\]", vf["content"])
        for link in links:
            link_clean = link.strip()
            link_slug = slugify(link_clean)
            candidates = [link_clean + ".md", link_slug + ".md", link_clean, link_slug]
            if not any(c in existing_paths or c.replace("-", " ") in existing_paths for c in candidates):
                stale.append({"type": "stale_ref", "source_file": vf["path"], "broken_link": link_clean})
    return stale

# ---------------------------------------------------------------------------
# MOC GENERATOR
# ---------------------------------------------------------------------------

def generate_moc(domain: str, chroma_docs: List[Dict], vault_files: List[Dict],
                 contradictions: List[Dict]) -> str:
    title = domain.replace("-", " ").title()
    all_text = " ".join(d.get("content", "") for d in chroma_docs + vault_files)
    all_text_lower = all_text.lower()

    # Topic counting (customize keywords per domain)
    topic_counts = defaultdict(int)
    topic_keywords = {
        "Topic A": ["keyword-a1", "keyword-a2"],
        "Topic B": ["keyword-b1", "keyword-b2"],
    }
    for topic, kws in topic_keywords.items():
        for kw in kws:
            topic_counts[topic] += all_text_lower.count(kw)
    top_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:6]

    # Vault links
    seen_paths = set()
    vault_links = []
    for vf in vault_files:
        path = vf["path"]
        if path in seen_paths:
            continue
        seen_paths.add(path)
        link_title = path.split("/")[-1].replace(".md", "").replace("-", " ")
        vault_links.append(f"- [[{path.replace('.md', '')}|{link_title}]]")

    # Chroma links
    seen_chroma = set()
    chroma_links = []
    for cd in chroma_docs:
        src = cd.get("source", "chroma:unknown")
        cid = cd.get("id", "?")
        key = f"{src}:{cid}"
        if key in seen_chroma:
            continue
        seen_chroma.add(key)
        preview = cd.get("content", "")[:60].replace("\n", " ")
        chroma_links.append(f"- `{src}` — {preview}...")

    # Contradictions
    contradiction_lines = []
    for c in contradictions:
        if c["type"] == "duplicate_folder":
            contradiction_lines.append(
                f"- **Duplicate folder**: '{c['duplicate']}' vs '{c['canonical']}' "
                f"(normalized: `{c['normalized']}`). {c['suggestion']}"
            )
        elif c["type"] == "stale_ref":
            contradiction_lines.append(
                f"- **Stale link**: `[[{c['broken_link']}]]` in `{c['source_file']}`"
            )

    moc = f"""---
title: "Synthesis: {title}"
domain: {domain}
generated_by: vault-compilation-agent
generated_at: {now_iso()}
total_sources: {len(chroma_docs) + len(vault_files)}
chroma_sources: {len(chroma_docs)}
vault_sources: {len(vault_files)}
contradictions_found: {len(contradictions)}
status: auto-synthesis
---

# Synthesis: {title}

> Auto-generated MOC from ChromaDB + vault cross-reference.

## Overview

| Metric | Value |
|--------|-------|
| Vault files scanned | {len(vault_files)} |
| ChromaDB docs pulled | {len(chroma_docs)} |
| Contradictions detected | {len(contradictions)} |
| Generation time | {now_iso()} |

## Top Topics

"""
    for topic, count in top_topics:
        moc += f"- **{topic}** — {count} mentions\n"

    moc += f"""
## Vault Sources

{chr(10).join(vault_links[:30]) if vault_links else "_No vault sources matched._"}

## ChromaDB Sources

{chr(10).join(chroma_links[:20]) if chroma_links else "_No ChromaDB sources available._"}

## Contradictions & Stale References

{chr(10).join(contradiction_lines) if contradiction_lines else "_No contradictions detected._"}

## Cross-Domain Links

- [[03-Knowledge/Synthesis/_index|Synthesis Index]]

---

*Last compiled. Hash: {fingerprint(domain + all_text[:500])}*
"""
    return moc

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    print(f"[vault-compilation-agent] DRY_RUN={DRY_RUN}")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    client = get_chroma_client()

    global_dups = detect_duplicate_folders(VAULT_ROOT)
    print(f"[agent] Found {len(global_dups)} duplicate folders")

    for domain in DOMAIN_CONFIG.keys():
        print(f"\n[domain: {domain}] ---")
        chroma_docs = query_chroma(domain, client)
        vault_files = scan_vault(domain)
        stale = detect_stale_refs(vault_files, VAULT_ROOT)
        contradictions = global_dups + stale

        moc_content = generate_moc(domain, chroma_docs, vault_files, contradictions)
        out_file = OUTPUT_DIR / f"{domain}--moc.md"

        if DRY_RUN:
            print(f"[DRY RUN] Would write {len(moc_content)} chars to {out_file}")
            preview = "\n".join(moc_content.split("\n")[:40])
            print(f"--- PREVIEW ---\n{preview}\n...")
        else:
            write_needed = True
            if out_file.exists():
                existing = out_file.read_text(encoding="utf-8")
                existing_hash = re.search(r"Hash: ([a-f0-9]{16})", existing)
                all_text_for_hash = " ".join(d.get("content", "") for d in chroma_docs + vault_files)
                new_hash = fingerprint(domain + all_text_for_hash[:500])
                if existing_hash and existing_hash.group(1) == new_hash:
                    write_needed = False
                    print("[IDEMPOTENT] Hash match — no write needed")
            if write_needed:
                out_file.write_text(moc_content, encoding="utf-8")
                print(f"[WRITTEN] {out_file} ({len(moc_content)} chars)")
            else:
                print("[SKIPPED] Content unchanged")

    print("\n[agent] Done.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
