#!/usr/bin/env python3
"""
Instagram Reel Extractor — Browser automation fallback.
Loads reel URL, dismisses signup modal, captures:
1. Caption + hashtags from page text
2. Creator handle, metrics, comments
3. Screenshot for optional vision analysis

Usage: python ig_reel_extract.py <reel_url>
Output: JSON to stdout
"""
import json, re, sys
from playwright.sync_api import sync_playwright

IG_REEL_RE = re.compile(r"instagram\.com/reel/([A-Za-z0-9_-]+)")


def extract(shortcode, url):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars",
                "--window-size=1280,900",
            ],
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 900},
        )
        page = context.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(2500)

            # Dismiss signup modal
            page.keyboard.press("Escape")
            page.wait_for_timeout(500)
            try:
                close_btn = page.query_selector("svg[aria-label='Close']")
                if close_btn:
                    close_btn.click()
                    page.wait_for_timeout(500)
            except Exception:
                pass
            page.keyboard.press("Escape")
            page.wait_for_timeout(500)

            # Extract all visible text from body
            texts = page.evaluate("""
                () => {
                    const all = document.body.querySelectorAll('h1,h2,span,div,a');
                    const out = [];
                    for (const el of all) {
                        if (el.offsetParent === null) continue;
                        const t = el.textContent?.trim();
                        if (t && t.length > 2 && t.length < 3000) out.push(t);
                    }
                    return out;
                }
            """)

            # Deduplicate preserving order
            seen = set()
            deduped = []
            for t in texts:
                if t not in seen:
                    seen.add(t)
                    deduped.append(t)

            # Screenshot
            shot_path = f"/tmp/ig_reel_{shortcode}.png"
            page.screenshot(path=shot_path, full_page=False)

            # Classify
            caption = []
            hashtags = []
            comments = []
            meta = []
            for t in deduped:
                if t.startswith('#'):
                    hashtags.append(t)
                elif any(k in t.lower() for k in ('likes','follow','reply','hours ago','days ago','original audio')):
                    meta.append(t)
                elif len(t) > 10 and not t.startswith('Log In') and not t.startswith('Sign Up'):
                    caption.append(t)
                else:
                    comments.append(t)

            return {
                "shortcode": shortcode,
                "url": url,
                "screenshot": shot_path,
                "caption_candidates": caption[:8],
                "hashtags": hashtags,
                "comments_top": comments[:10],
                "meta": meta[:8],
                "raw_texts_count": len(deduped),
            }
        finally:
            browser.close()


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else ""
    if not url:
        print("Usage: python ig_reel_extract.py <reel_url>", file=sys.stderr)
        sys.exit(1)
    m = IG_REEL_RE.search(url)
    shortcode = m.group(1) if m else url.rstrip('/').split('/')[-1]
    result = extract(shortcode, url)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
