---
title: "Social Media Thread Ingestion to Vault + Chroma"
description: "Pattern for ingesting Twitter/X thread links into the knowledge vault and vectorizing them in ChromaDB. Handles multi-part threads, external article links, and structured KB archiving."
date: "2026-05-28"
---

# Social Media Thread Ingestion to Vault + Chroma

**Use case:** User shares a Twitter/X thread link (e.g., `https://x.com/TheTuringPost/status/...`) and expects it ingested to the vault as structured KB articles, with all linked external articles extracted and archived.

## Workflow

### 1. Extract the Thread

Use `web_extract` on the Twitter/X URL:

```python
# Extracts thread posts, replies, and top-level comments
result = web_extract(["https://x.com/TheTuringPost/status/..."])
```

Output includes:
- Original post text
- Thread replies (numbered)
- Likes/retweets metadata
- Linked URLs within posts

### 2. Extract Linked Articles

If the thread contains links to external articles (e.g., `turingpost.com/p/...`), extract each:

```python
# Extract all linked articles
article_urls = extract_urls_from_thread(result)
article_contents = web_extract(article_urls)
```

### 3. Write to Vault

Create a directory per thread series:

```
claude-vault/03-Knowledge/Articles/<series-name>/
├── README.md              # Index + summary
├── 01-article-one.md      # First article
├── 02-article-two.md      # Second article
├── 03-article-three.md    # Third article
...
```

Each article gets YAML frontmatter:
```yaml
---
title: "Article Title"
source: "https://..."
author: "Name"
date: "2026-05-28"
type: "article"
tags: [tag1, tag2, tag3]
---
```

The README gets:
```yaml
---
title: "Series: Series Name"
source: "https://x.com/..."
author: "@handle"
date: "2026-05-28"
type: "knowledge-collection"
tags: [tag1, tag2, tag3]
---
```

### 4. Sync to ChromaDB

Use `knowledge_spine_upsert` to vectorize all articles:

```python
from scripts.lib.knowledge_spine_upsert import upsert_vault_note

for article in articles:
    upsert_vault_note(
        source="turing-post",
        item_id=f"llm-guide-{article['slug']}",
        source_path=article["path"],
        title=article["title"],
        body=article["content"],
        route="ai-fundamentals",
        extra_metadata={"series": "turing-post-llm-guides", "author": "Turing Post"},
    )
```

## Key Rules

1. **Always extract linked articles** — A Twitter thread is often just a teaser; the real content is in the linked articles. Extract ALL of them.
2. **Create a README index** — The series README links all articles and provides a high-level summary.
3. **Preserve attribution** — Include author, source URL, and date in every article's frontmatter.
4. **Vectorize the full content** — Don't just vectorize the thread summary; vectorize each extracted article so it's searchable.
5. **Use `route` tags** — Route the series to a relevant domain (e.g., `ai-fundamentals`, `trading-intel`, `creative-seeds`).

## Pitfalls

- **web_extract truncation** — Some articles may be truncated by `web_extract`. For premium content, use `browser_navigate` + `browser_console` with `document.body.innerText.slice()` to extract the full text.
- **Rate limits** — Extracting many articles in rapid succession may hit rate limits. Space requests 2-3 seconds apart.
- **Paywall detection** — If an article is behind a paywall, `web_extract` may return only the preview. Mark it in the README: `Paywall: partial content only`.
- **Duplicate ingestion** — Check if the article URL already exists in ChromaDB before upserting. Use `source_path` as the deduplication key.

## Session Reference

This pattern was validated during a 2026-05-28 session where the user shared a Turing Post thread (`https://x.com/TheTuringPost/status/2060054180379689074`) containing 6 guides to LLM internals. All 6 linked articles were extracted, written to `claude-vault/03-Knowledge/Articles/turing-post-llm-guides/`, and vectorized in ChromaDB `knowledge_spine` under `route: ai-fundamentals`.
