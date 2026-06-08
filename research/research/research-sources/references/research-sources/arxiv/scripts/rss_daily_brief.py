#!/usr/bin/env python3
"""
Complete implementation: Daily arXiv RSS Brief Pipeline.

Fetches latest papers from cs.AI, cs.CL, cs.LG RSS feeds, scores them by
intrinsic interest + Semantic Scholar citations, writes enriched briefs to
the vault, and reports ENRICH-ticket candidates.

No dependencies beyond Python stdlib.

Usage:
  python3 rss_daily_brief.py --vault /path/to/claude-vault/03-Knowledge/ArXiv
  python3 rss_daily_brief.py --vault /path/to/claude-vault/03-Knowledge/ArXiv --top 5 --min 3
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime

# --- Config ---
FEEDS = [
    ("cs.AI", "https://rss.arxiv.org/rss/cs.AI"),
    ("cs.CL", "https://rss.arxiv.org/rss/cs.CL"),
    ("cs.LG", "https://rss.arxiv.org/rss/cs.LG"),
]

# Interest keywords for scoring
INTEREST_KEYWORDS = {
    "new_method": [
        "new method", "new approach", "novel architecture", "novel framework",
        "novel algorithm", "propose a", "we propose", "propose", "introduce",
    ],
    "benchmark": [
        "benchmark", "dataset", "new benchmark", "corpus",
    ],
    "empirical": [
        "strong empirical", "state-of-the-art", "sota", "outperforms",
        "significant improvement", "superior", "substantial",
    ],
    "agentic": [
        "agent", "agents", "agentic", "multi-agent", "reasoning",
        "chain of thought", "cot", "rl", "reinforcement learning",
        "grpo", "ppo", "planning", "eval", "evaluation",
    ],
}

# Cross-link filename hints for existing vault briefs
FILENAME_TOPIC_MAP = {
    "consilium": "agentic-systems",
    "deliberative-curation": "data-curation",
    "mindgames": "rl",
    "interactive-reasoning": "reasoning",
    "abaqus": "agentic-systems",
    "thinking-past-the-answer": "reasoning",
    "toolgate": "compression",
    "diversity-collapse": "robustness",
    "decoupling-subword": "llm",
    "hana-hierarchical": "agentic-systems",
    "autoreason": "reasoning",
    "legal-triage": "agentic-systems",
}

# --- Step 1: Discover ---

def fetch_feeds(tmp_dir="/tmp"):
    """Fetch RSS feeds and save to tmp_dir."""
    for cat, url in FEEDS:
        path = os.path.join(tmp_dir, f"{cat.replace('.', '_')}.xml")
        try:
            subprocess.run(["curl", "-sS", "-o", path, url], check=True, timeout=30)
            print(f"Fetched {cat} -> {path}")
        except subprocess.TimeoutExpired:
            print(f"Timeout fetching {cat}")
        except subprocess.CalledProcessError as e:
            print(f"Error fetching {cat}: {e}")
        time.sleep(3)


def parse_feeds(tmp_dir):
    """Parse fetched XML feeds and return deduped candidate list."""
    papers = {}
    for cat, _ in FEEDS:
        path = os.path.join(tmp_dir, f"{cat.replace('.', '_')}.xml")
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            continue
        try:
            tree = ET.parse(path)
        except ET.ParseError:
            print(f"Parse error for {cat}")
            continue
        root = tree.getroot()
        for item in root.findall(".//item"):
            title_elem = item.find("title")
            link_elem = item.find("link")
            desc_elem = item.find("description")
            if title_elem is None or link_elem is None:
                continue
            title = title_elem.text or ""
            link = link_elem.text or ""
            desc = desc_elem.text or "" if desc_elem is not None else ""
            creators = item.findall("{http://purl.org/dc/elements/1.1/}creator")
            authors = [c.text for c in creators if c.text]
            # Handle single comma-separated author string
            if len(authors) == 1 and ", " in authors[0]:
                authors = [a.strip() for a in authors[0].split(",")]

            m = re.search(r"arxiv\.org/abs/(\d+\.\d+)", link)
            if not m:
                continue
            arxiv_id = m.group(1)
            abstract = ""
            if "Abstract: " in desc:
                abstract = desc.split("Abstract: ", 1)[1].strip()
            clean_title = re.sub(r"\s+\([^)]+\)$", "", title).strip()

            if arxiv_id in papers:
                if cat not in papers[arxiv_id]["categories"]:
                    papers[arxiv_id]["categories"].append(cat)
                continue

            papers[arxiv_id] = {
                "id": arxiv_id,
                "title": clean_title,
                "authors": authors,
                "abstract": abstract,
                "categories": [cat],
            }
    return list(papers.values())


# --- Step 2: Rank ---

def score_interest(paper):
    text = (paper["title"] + " " + paper["abstract"]).lower()
    score = 0
    if any(k in text for k in INTEREST_KEYWORDS["new_method"]):
        score += 3
    if any(k in text for k in INTEREST_KEYWORDS["benchmark"]):
        score += 2
    if any(k in text for k in INTEREST_KEYWORDS["empirical"]):
        score += 2
    if any(k in text for k in INTEREST_KEYWORDS["agentic"]):
        score += 1
    return score


def enrich_semantic_scholar(papers, max_candidates=25, sleep_seconds=1.2):
    """Query Semantic Scholar for citation signals. Top candidates only."""
    sorted_papers = sorted(papers, key=lambda x: score_interest(x), reverse=True)
    for p in sorted_papers[:max_candidates]:
        arxiv_id = p["id"]
        url = (
            f"https://api.semanticscholar.org/graph/v1/paper/arXiv:{arxiv_id}"
            f"?fields=title,citationCount,influentialCitationCount,year,fieldsOfStudy"
        )
        data = None
        for attempt in range(3):
            try:
                result = subprocess.run(
                    ["curl", "-sS", "--max-time", "15", url],
                    capture_output=True, text=True, check=True,
                )
                data = json.loads(result.stdout)
                break
            except subprocess.CalledProcessError as e:
                if e.returncode == 22:  # HTTP 429 often maps to exit 22
                    print(f"  429 for {arxiv_id}, attempt {attempt+1}")
                    time.sleep(2 ** attempt)
                else:
                    print(f"  HTTP error for {arxiv_id}: {e.returncode}")
                    break
            except Exception as e:
                print(f"  Error for {arxiv_id}: {e}")
                break

        if data:
            p["citation_count"] = data.get("citationCount", 0) or 0
            p["influential_citations"] = data.get("influentialCitationCount", 0) or 0
            p["year"] = data.get("year", "")
            p["fieldsOfStudy"] = data.get("fieldsOfStudy", [])
        else:
            # Likely not indexed yet (404) or rate-limited
            p["citation_count"] = 0
            p["influential_citations"] = 0
            p["year"] = ""
            p["fieldsOfStudy"] = []
        time.sleep(sleep_seconds)
    return papers


def compute_kb_score(paper):
    cc = min(paper.get("citation_count", 0), 10)
    ic = min(paper.get("influential_citations", 0) * 2, 6)
    interest = score_interest(paper)
    return cc + ic + interest


# --- Step 3: Fetch arXiv abs HTML ---

def fetch_abs_html(arxiv_id, tmp_dir="/tmp"):
    path = os.path.join(tmp_dir, f"{arxiv_id}.html")
    try:
        subprocess.run(
            ["curl", "-sS", "-o", path, f"https://arxiv.org/abs/{arxiv_id}"],
            check=True, timeout=30,
        )
        with open(path) as f:
            return f.read()
    except Exception as e:
        print(f"  Failed to fetch abs for {arxiv_id}: {e}")
        return ""


def parse_abs_html(html, paper):
    """Parse arXiv abs HTML for metadata. Returns updated paper dict."""
    # Abstract
    m = re.search(
        r'<blockquote class="abstract mathjax">\s*<span class="descriptor">Abstract:</span>\s*(.*?)</blockquote>',
        html, re.DOTALL,
    )
    if m:
        abstract = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        abstract = re.sub(r'\s+', ' ', abstract)
        paper["abstract"] = abstract
    # Title
    tm = re.search(
        r'<h1 class="title mathjax">\s*<span class="descriptor">Title:</span>\s*(.*?)</h1>',
        html, re.DOTALL,
    )
    if tm:
        title = re.sub(r'<[^>]+>', '', tm.group(1)).strip()
        paper["title"] = title
    # Authors
    authors = re.findall(
        r'<a href="/search/\?searchtype=author[^"]*">([^<]+)</a>', html,
    )
    if authors:
        paper["authors"] = authors
    # Date
    dm = re.search(r'<div class="dateline">[^\d]*(\d{1,2}\s+\w+\s+\d{4})', html)
    if dm:
        try:
            dt = datetime.strptime(dm.group(1), "%d %b %Y")
            paper["published"] = dt.strftime("%Y-%m-%d")
        except ValueError:
            pass
    # Categories
    cats = re.findall(r'<span class="primary-subject">([^<]+)</span>', html)
    if cats:
        paper["categories"] = cats
    return paper


def generate_tags(paper):
    text = (paper["title"] + " " + paper["abstract"]).lower()
    tags = []
    if "agent" in text or "multi-agent" in text:
        tags.append("agentic-systems")
    if "reinforcement" in text or "rl" in text or "reward" in text or "policy gradient" in text:
        tags.append("rl")
    if "reasoning" in text or "chain-of-thought" in text or "cot" in text or "faithful" in text:
        tags.append("reasoning")
    if "eval" in text or "benchmark" in text or "dataset" in text:
        tags.append("evaluation")
    if "llm" in text or "language model" in text:
        tags.append("llm")
    if "retrieval" in text or "rag" in text:
        tags.append("rag")
    if "distillation" in text or "pruning" in text or "quantiz" in text:
        tags.append("compression")
    if "out-of-distribution" in text or "ood" in text or "distribution shift" in text:
        tags.append("robustness")
    if "sensor" in text or "iot" in text or "edge" in text or "lightweight" in text or "wearable" in text:
        tags.append("edge-ai")
    if "medical" in text or "clinical" in text or "ecg" in text or "health" in text:
        tags.append("healthcare")
    if "time series" in text or "timeseries" in text:
        tags.append("time-series")
    if "information extraction" in text or "ner" in text or "relation extraction" in text:
        tags.append("information-extraction")
    if "zero-shot" in text:
        tags.append("zero-shot")
    if "data curation" in text or "curation" in text:
        tags.append("data-curation")
    if "fine-tuning" in text or "finetuning" in text:
        tags.append("fine-tuning")
    for cat in paper.get("categories", []):
        cat_clean = cat.split("(")[-1].replace(")", "").strip()
        if cat_clean not in tags:
            tags.append(cat_clean)
    return tags


def get_related(arxiv_id, tags, all_selected_ids, output_dir):
    """Build cross-link list for Related section."""
    related = []
    # Links among today's selected papers
    for other_id in all_selected_ids:
        if other_id == arxiv_id:
            continue
        related.append(f"- [[{other_id}-brief]]")
    # Links to existing vault briefs
    if os.path.isdir(output_dir):
        for fname in os.listdir(output_dir):
            if not fname.endswith(".md"):
                continue
            if arxiv_id in fname:
                continue
            for hint, topic in FILENAME_TOPIC_MAP.items():
                if hint in fname.lower() and topic in tags:
                    related.append(f"- [[{fname}]]")
                    break
    return related


# --- Step 4: Write Briefs ---

def clean_latex(text):
    """Remove LaTeX commands like \ours, \method from text."""
    text = re.sub(r'\\[A-Za-z]+\b', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def split_sentences(text):
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]


def classify_sentences(sentences):
    """Classify sentences into problem, method, results, or general."""
    problem, method, results, general = [], [], [], []
    for s in sentences:
        s_lower = s.lower()
        is_prob = any(w in s_lower for w in [
            "however", "challenge", "issue", "problem", "suffer", "degrade",
            "limited", "difficult", "struggle", "overlook", "gap", "lack",
            "shortcoming", "weakness", "failure mode",
        ])
        is_meth = any(w in s_lower for w in [
            "propose", "introduce", "design", "framework", "method", "approach",
            "present", "develop", "build", "construct", "architecture",
            "mechanism", "algorithm", "strategy",
        ])
        is_res = any(w in s_lower for w in [
            "result", "experiment", "show", "achieve", "outperform",
            "accuracy", "f1", "precision", "recall", "performance",
            "improve", "demonstrate", "evaluate", "test", "find", "observe",
            "significant",
        ])
        if is_prob:
            problem.append(s)
        elif is_meth:
            method.append(s)
        elif is_res:
            results.append(s)
        else:
            general.append(s)
    return problem, method, results, general


def write_brief(paper, output_dir, today, all_selected_ids):
    arxiv_id = paper["id"]
    title = paper["title"]
    authors = paper.get("authors", [])
    abstract = clean_latex(paper.get("abstract", ""))
    categories = paper.get("categories", [])
    published = paper.get("published", today)
    cc = paper.get("citation_count", 0)
    ic = paper.get("influential_citations", 0)
    kb = paper.get("kb_score", 0)
    tags = paper.get("tags", [])

    sentences = split_sentences(abstract)
    prob, meth, res, gen = classify_sentences(sentences)

    # TL;DR
    tldr = ". ".join(sentences[:2])
    if not tldr.endswith("."):
        tldr += "."
    if len(tldr) > 300:
        tldr = tldr[:297] + "..."

    # Sections
    problem = ". ".join(prob if prob else sentences[:3])
    if not problem.endswith("."):
        problem += "."

    method = ". ".join(meth if meth else sentences[3:5] if len(sentences) > 3 else sentences[2:4])
    if not method.endswith("."):
        method += "."

    results_text = ". ".join(res if res else sentences[-2:])
    if not results_text.endswith("."):
        results_text += "."

    why_tags = ", ".join(tags[:3]) if tags else "relevant research"
    related = get_related(arxiv_id, tags, all_selected_ids, output_dir)

    md = f"""---
arxiv_id: {arxiv_id}
title: "{title}"
authors: {authors}
categories: {categories}
published: {published}
citation_count: {cc}
influential_citations: {ic}
kb_score: {kb}
source: arxiv
tags: {tags}
generated: {today}
url: https://arxiv.org/abs/{arxiv_id}
---

## TL;DR

{tldr}

## Problem & Motivation

{problem}

## Method / Contribution

{method}

## Key Results

{results_text}

## Why It Matters (KB relevance)

KB-score breakdown: citation component={min(cc, 10)}, influential component={min(ic*2, 6)}, intrinsic interest={score_interest(paper)}. This work aligns with active research areas in the Edgeless knowledge base, particularly around {why_tags}.

## Limitations / Open Questions

As with most preliminary arXiv submissions, this work may not yet include full ablation studies, reproducibility artifacts, or peer review. The practical deployment of the proposed method remains an open question.

## Links

- Abstract: https://arxiv.org/abs/{arxiv_id}
- PDF: https://arxiv.org/pdf/{arxiv_id}
"""

    if related:
        md += "\n## Related\n\n"
        md += "\n".join(related) + "\n"

    out_path = os.path.join(output_dir, f"{arxiv_id}-brief.md")
    os.makedirs(output_dir, exist_ok=True)
    with open(out_path, "w") as f:
        f.write(md)
    print(f"  Wrote {out_path}")
    return out_path


# --- Main ---

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--vault", default="/Users/djm/claude-projects/claude-vault/03-Knowledge/ArXiv"
    )
    parser.add_argument("--top", type=int, default=5)
    parser.add_argument("--min", type=int, default=3)
    args = parser.parse_args()

    today = datetime.now().strftime("%Y-%m-%d")
    tmp_dir = "/tmp"
    output_dir = args.vault

    print("Step 1: Fetching RSS feeds...")
    fetch_feeds(tmp_dir)

    print("Step 2: Parsing feeds...")
    papers = parse_feeds(tmp_dir)
    print(f"  {len(papers)} unique papers")

    if not papers:
        print("arxiv feeds unavailable")
        sys.exit(1)

    print("Step 3: Enriching with Semantic Scholar...")
    papers = enrich_semantic_scholar(papers)

    for p in papers:
        p["kb_score"] = compute_kb_score(p)

    papers.sort(key=lambda x: x["kb_score"], reverse=True)
    selected = papers[:args.top]
    if len(selected) < args.min:
        selected = papers[:args.min]

    print(f"\nSelected {len(selected)} papers:")
    for p in selected:
        print(f"  {p['id']} | kb={p['kb_score']} | {p['title'][:80]}")

    print("\nStep 4: Fetching abs pages and writing briefs...")
    all_selected_ids = [p["id"] for p in selected]
    for p in selected:
        html = fetch_abs_html(p["id"], tmp_dir)
        if html:
            p = parse_abs_html(html, p)
        p["tags"] = generate_tags(p)
        write_brief(p, output_dir, today, all_selected_ids)

    print(f"\nDone. Wrote {len(selected)} briefs to {output_dir}")
    high_score = [p for p in selected if p.get("kb_score", 0) >= 12]
    print(f"Papers eligible for ENRICH tickets: {len(high_score)}")
    for p in high_score:
        print(f"  {p['id']} | {p['title'][:80]}")


if __name__ == "__main__":
    main()
