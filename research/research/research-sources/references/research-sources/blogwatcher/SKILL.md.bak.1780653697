---
name: blogwatcher
description: >
  Monitor blogs and RSS/Atom feeds for updates using the blogwatcher-cli tool.
  Add blogs, scan for new articles, track read status, filter by category. RSS feed
  discovery, HTML scraping fallback, OPML import, read/unread article management.
  Blog tracking, content monitoring, feed aggregation, article triage.
version: 2.0.0
author: JulienTant (fork of Hyaxia/blogwatcher)
license: MIT
metadata:
  tags: [RSS, Blogs, Feed-Reader, Monitoring, news, aggregation, OPML]
  tier: task-specific
  domain: research
  color: green
  homepage: https://github.com/JulienTant/blogwatcher-cli
prerequisites:
  commands: [blogwatcher-cli]
  env_vars: [BLOGWATCHER_DB, BLOGWATCHER_WORKERS]
---

# Blogwatcher

## Identity (Who This Agent Is)

A content monitoring specialist focused on blog and RSS/Atom feed tracking.
Provides automated discovery, scraping fallback, and structured article management
with categorization and read-state tracking.

## When to Use

- User mentions "blog", "RSS", "feed", "news", "articles"
- Tracking website updates without APIs
- Monitoring multiple content sources
- Importing OPML subscriptions from other readers
- Filtering content by category or source
- Managing read/unread article states

## When NOT to Use

- Real-time streaming data → use WebSocket or event-based tools
- API-first data sources → use direct API calls
- Social media monitoring → use `scrapping` skill for social platforms
- Email newsletters → use `himalaya` email skill

## Core Mission

Enable automated blog and RSS feed monitoring with intelligent feed discovery,
fallback scraping, and structured article management for content tracking workflows.

## Critical Rules

1. **ALWAYS use --yes flag for automated operations** - prevents interactive prompts
2. **Database path must be explicit in Docker** - use BLOGWATCHER_DB env var or volume mount
3. **Feed discovery may fail** - have fallback scrape-selector ready

## Instructions

### Phase 1: Installation & Setup

Pick installation method:

```bash
# Go (recommended)
go install github.com/JulienTant/blogwatcher-cli/cmd/blogwatcher-cli@latest

# macOS Apple Silicon
curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_darwin_arm64.tar.gz | tar xz -C /usr/local/bin blogwatcher-cli

# Linux AMD64
curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_linux_amd64.tar.gz | tar xz -C /usr/local/bin blogwatcher-cli
```

Docker alternative:
```bash
docker run --rm -v blogwatcher-cli:/data -e BLOGWATCHER_DB=/data/blogwatcher-cli.db ghcr.io/julientant/blogwatcher-cli scan
```

Validation checkpoint: Verify `blogwatcher-cli blogs` runs without error.

### Phase 2: Adding Blogs

Auto-discover feed:
```bash
blogwatcher-cli add "Blog Name" https://example.com
```

Explicit feed URL:
```bash
blogwatcher-cli add "Blog Name" https://example.com --feed-url https://example.com/feed.xml
```

HTML scraping fallback:
```bash
blogwatcher-cli add "Blog Name" https://example.com --scrape-selector "article h2 a"
```

Bulk import from OPML:
```bash
blogwatcher-cli import subscriptions.opml
```

Validation checkpoint: Run `blogwatcher-cli blogs` to confirm addition.

### Phase 3: Scanning & Reading

Scan all blogs:
```bash
blogwatcher-cli scan
```

List unread articles:
```bash
blogwatcher-cli articles
```

Filter by category:
```bash
blogwatcher-cli articles --category "Engineering"
```

Mark articles read:
```bash
blogwatcher-cli read 1 2 3  # Mark article IDs 1, 2, 3 as read
blogwatcher-cli read-all     # Mark all as read (requires --yes)
```

## Deliverables

| Output | Format | Storage |
|--------|--------|---------|
| Tracked blogs list | Text table | SQLite DB |
| New articles | Indexed list | SQLite DB |
| Scan summary | Terminal output | Ephemeral |
| OPML export | XML file | Filesystem |

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Feed discovery rate | >90% | Successful / attempted |
| Scan completion | 100% | No errors |
| Article categorization | >80% | With category / total |

## Cross-References

- For social media data → `scrapping` skill
- For academic papers → `arxiv` skill
- For email content → `himalaya` skill
- For YouTube content → `youtube-content` skill

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `BLOGWATCHER_DB` | SQLite database path | `~/.blogwatcher-cli/blogwatcher-cli.db` |
| `BLOGWATCHER_WORKERS` | Concurrent scan workers | 8 |
| `BLOGWATCHER_SILENT` | Minimal scan output | false |
| `BLOGWATCHER_YES` | Auto-confirm prompts | false |
| `BLOGWATCHER_CATEGORY` | Default article filter | none |

## Learning & Memory

- Feed discovery works on most WordPress, Substack, Ghost blogs
- HTML scraping requires CSS selector knowledge
- OPML import preserves categories from source readers
- Database location varies: local vs Docker

## Changelog

- v2.0.0: Unified template adoption
- v1.0.0: Initial Hermes skill
