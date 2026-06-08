# Instagram Reel Ingestion via Browser Automation

**When to use:** When the user sends an Instagram reel URL (`https://www.instagram.com/reel/XXXX/`) and simple `urllib` or web scraping returns 403/empty results. Instagram's anti-bot protection blocks automated scrapers. The working method is **browser automation** (Playwright), not API calls.

## The Hive Pattern

Hive's `ig_reel_extract.py` (`~/.hermes/profiles/hive/scripts/ig_reel_extract.py`) is the canonical working implementation for the Edgeless swarm.

### What it does
1. Launches headless Chromium with `--disable-blink-features=AutomationControlled`
2. Loads the reel URL with `domcontentloaded` (not `networkidle` — faster, less bot-detection)
3. Dismisses the signup modal: Escape key → click `svg[aria-label='Close']` → Escape again
4. Extracts all visible text from `h1,h2,span,div,a` elements (deduplicated, preserving order)
5. Classifies into: caption, hashtags, comments, metadata
6. Takes a screenshot at `/tmp/ig_reel_{shortcode}.png` for optional vision analysis

### How to run it
```bash
python3 ~/.hermes/profiles/hive/scripts/ig_reel_extract.py \
  "https://www.instagram.com/reel/SHORTCODE/"
```

Output: JSON to stdout with `shortcode`, `url`, `screenshot`, `caption_candidates`, `hashtags`, `comments_top`, `meta`, `raw_texts_count`.

### Key parameters
- `headless=True` — runs in background (set to False for debugging)
- `wait_until="domcontentloaded"` — 15s timeout, doesn't wait for all network resources
- `wait_for_timeout(2500)` — 2.5s after load for JS hydration
- `viewport=1280x900` — desktop viewport avoids mobile-specific prompts
- `--disable-blink-features=AutomationControlled` — removes `navigator.webdriver` flag

### Why this works when APIs fail
- Instagram aggressively blocks headless scrapers via `navigator.webdriver`, TLS fingerprinting, and rate limiting
- Playwright with `--disable-blink-features=AutomationControlled` and real viewport + user agent passes most detection
- The signup modal is the primary blocker — dismissing it reveals the content
- No auth required for public reels

### Why not ScrapeCreators API?
The `scraping-intel` skill covers ScrapeCreators (100+ endpoints, 20+ platforms). For Instagram, it supports profile, posts, reels, comments, transcripts via API key. However:
- ScrapeCreators is pay-per-credit (100 free on signup, then per-request)
- The Instagram endpoints are v2 and require manual pagination
- For a single reel, the browser automation is faster, free, and requires no API key

**Rule of thumb:** Use browser automation for one-off reel ingestion. Use ScrapeCreators for batch profile analysis, ad library lookups, or TikTok/LinkedIn/Reddit where no browser script exists.

### Before trying to scrape
Always check if an existing agent script already handles the platform:
```bash
find ~/.hermes/profiles/*/scripts/ -name "*ig*" -o -name "*instagram*" -o -name "*reel*"
```
The swarm has specialized scripts per agent. Don't reinvent from scratch — discover and reuse.
