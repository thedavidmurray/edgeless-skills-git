#!/usr/bin/env python3
"""
skill_frontmatter.py

Migrate existing SKILL.md / skill.md files to standard YAML frontmatter.
Scans ~/.hermes/skills/ and ~/.Codex/skills/ (and any extra paths)
and ensures every skill file has the required frontmatter block.

Usage:
    python skill_frontmatter.py [--dry-run] [--source PATH ...]

Standard frontmatter fields:
    name: str (required)
    version: str (default "1.0.0")
    description: str (default "Edgeless skill")
    author: str (default "Edgeless")
    license: str (default "MIT")
    domain: str (inferred from path or tags)
    platforms: list[str] (optional)
    metadata:
        tags: list[str]
        related_skills: list[str]
        requires_toolsets: list[str]
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
DEFAULT_SOURCES = [
    Path.home() / ".hermes" / "skills",
    Path.home() / ".Codex" / "skills",
]

REQUIRED_FIELDS = {"name", "description", "version", "author", "license"}
OPTIONAL_FIELDS = {"platforms", "domain", "metadata"}

# Domain inference from directory names or tags
DOMAIN_HINTS = {
    "creative": ["creative", "writing", "design", "media", "art", "music"],
    "devops": ["devops", "deploy", "ci", "cd", "docker", "k8s", "kubernetes", "infra"],
    "research": ["research", "investigation", "analysis", "market", "paper"],
    "product": ["product", "ux", "strategy", "roadmap", "feature"],
    "tooling": ["tool", "cli", "script", "automation", "build"],
    "observability": ["observability", "monitor", "alert", "log", "metric", "sre"],
    "ingestion": ["ingestion", "etl", "pipeline", "rss", "youtube", "feed"],
    "knowledge": ["knowledge", "memory", "chroma", "vault", "retrieval", "rag"],
    "security": ["security", "threat", "compliance", "audit", "pentest"],
    "system": ["system", "gateway", "platform", "core", "meta"],
    "external": ["external", "integration", "api", "bridge", "webhook"],
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_frontmatter(text: str) -> tuple[dict[str, Any] | None, str]:
    """Extract YAML frontmatter from markdown text.

    Returns (frontmatter_dict, body) or (None, text) if no frontmatter.
    """
    if not text.startswith("---"):
        return None, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, text
    try:
        fm = yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return None, text
    return fm, parts[2].lstrip("\n")


def build_frontmatter(existing: dict[str, Any] | None, skill_name: str, skill_dir: Path) -> str:
    """Build a complete frontmatter dict, merging existing values with defaults."""
    if existing is None:
        existing = {}

    fm: dict[str, Any] = {}
    fm["name"] = existing.get("name", skill_name)
    fm["description"] = existing.get("description", existing.get("title", f"Edgeless skill: {skill_name}"))
    fm["version"] = str(existing.get("version", "1.0.0"))
    fm["author"] = existing.get("author", "Edgeless")
    fm["license"] = existing.get("license", "MIT")

    # Infer domain
    domain = existing.get("domain", "")
    if not domain:
        domain = infer_domain(skill_name, existing.get("metadata", {}))
    if domain:
        fm["domain"] = domain

    platforms = existing.get("platforms")
    if platforms:
        fm["platforms"] = platforms

    metadata = existing.get("metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}

    # Ensure tags exist
    tags = metadata.get("tags", [])
    if not tags:
        tags = [domain] if domain else []
    if skill_name not in tags:
        tags.append(skill_name)
    metadata["tags"] = sorted(set(t for t in tags if t))

    related = metadata.get("related_skills", [])
    if related:
        metadata["related_skills"] = related
    requires = metadata.get("requires_toolsets", existing.get("requires_toolsets"))
    if requires:
        metadata["requires_toolsets"] = requires

    if metadata:
        fm["metadata"] = metadata

    return fm


def infer_domain(skill_name: str, metadata: dict) -> str:
    """Infer domain from skill name or tags."""
    tags = [t.lower() for t in metadata.get("tags", [])]
    combined = f"{skill_name} {' '.join(tags)}".lower()
    for domain, hints in DOMAIN_HINTS.items():
        for hint in hints:
            if hint in combined:
                return domain
    return "unclassified"


def format_frontmatter(fm: dict) -> str:
    """Serialize frontmatter dict to YAML string."""
    yaml_text = yaml.dump(fm, default_flow_style=False, sort_keys=False, allow_unicode=True)
    return f"---\n{yaml_text}---\n"


def migrate_file(path: Path, dry_run: bool = False) -> dict[str, Any]:
    """Migrate a single SKILL.md file. Returns report dict."""
    text = path.read_text(encoding="utf-8")
    existing, body = parse_frontmatter(text)
    skill_name = path.parent.name

    new_fm = build_frontmatter(existing, skill_name, path.parent)
    new_text = format_frontmatter(new_fm) + body

    changed = text.strip() != new_text.strip()
    action = "unchanged"
    if changed:
        if dry_run:
            action = "would_update"
        else:
            path.write_text(new_text, encoding="utf-8")
            action = "updated"

    return {
        "path": str(path),
        "skill": skill_name,
        "action": action,
        "had_frontmatter": existing is not None,
        "domain": new_fm.get("domain", "unclassified"),
    }


def discover_skills(source_dirs: list[Path]) -> list[Path]:
    """Find all SKILL.md / skill.md files under the given directories."""
    skills: list[Path] = []
    for d in source_dirs:
        if not d.exists():
            continue
        for candidate in ("SKILL.md", "skill.md"):
            for path in d.rglob(candidate):
                # Skip hidden/archive dirs
                if any(part.startswith(".") for part in path.relative_to(d).parts[:-1]):
                    continue
                skills.append(path)
    return skills


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate skill frontmatter to standard format")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing")
    parser.add_argument("--source", action="append", type=Path, help="Extra source directories")
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    parser.add_argument("--summary", action="store_true", help="Print summary")
    args = parser.parse_args()

    sources = list(DEFAULT_SOURCES)
    if args.source:
        sources.extend(args.source)

    skills = discover_skills(sources)
    reports = []
    for path in skills:
        reports.append(migrate_file(path, dry_run=args.dry_run))

    if args.json:
        print(json.dumps(reports, indent=2))
    else:
        for r in reports:
            status = r["action"]
            if status == "unchanged":
                continue
            icon = {"would_update": "👀", "updated": "✅"}.get(status, "⚠️")
            print(f"{icon} {r['path']} [{status}]")

    if args.summary or not args.json:
        updated = sum(1 for r in reports if r["action"].endswith("update"))
        unchanged = sum(1 for r in reports if r["action"] == "unchanged")
        print(f"\n📊 Skills scanned: {len(reports)}")
        print(f"   Updated/would_update: {updated}")
        print(f"   Unchanged: {unchanged}")
        domain_counts: dict[str, int] = {}
        for r in reports:
            domain_counts[r["domain"]] = domain_counts.get(r["domain"], 0) + 1
        print("   Domain distribution:")
        for d, c in sorted(domain_counts.items(), key=lambda x: -x[1]):
            print(f"      {d}: {c}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
