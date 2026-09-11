"""
Step 1: Content ingestion for RAG pipeline.

Fetches a sitemap.xml, crawls every URL in it, strips nav/header/footer/script
boilerplate, and saves clean page text + metadata as one JSON file per page.

Usage:
    pip install requests beautifulsoup4 lxml
    python ingest.py
"""

import json
import re
import time
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
from backend.config import SITE_ROOT, SITEMAP_URL, ROBOTS_URL, OUTPUT_DIR, ALL_PAGES_JSON
import requests
from bs4 import BeautifulSoup

REQUEST_DELAY_SECONDS = 1.0  # be polite, don't hammer the server
USER_AGENT = "Mozilla/5.0 (compatible; MyRAGBot/1.0; +https://www.webenza.com/)"

# Skip URLs matching these patterns (adjust to taste — e.g. legal boilerplate
# pages that add noise but little value to a support chatbot)
SKIP_PATTERNS = [
    r"/privacy-policy/",
]

# CSS selectors to remove before extracting text — nav, footer, forms, etc.
# Inspect your site's actual HTML and adjust these to match your theme.


#REMOVE_SELECTORS = [
#    "header", "nav", "footer", "script", "style", "noscript",
#    "form", "aside", ".cookie-banner", ".related-posts", ".comments",
#]


REMOVE_SELECTORS = [
    "header",
    "nav",
    "footer",
    "script",
    "style",
    "noscript",
    "form",
    "aside",
    "iframe",

    # Webenza global footer
    "#footer-sec-webenza",
    "#privacy-policy-footer-webenza",

    # Webenza Specialisation section
    "section.footer-what",

    # Other common noise
    ".cookie-banner",
    ".related-posts",
    ".comments",
]

def get_sitemap_urls(sitemap_url: str) -> list[str]:
    """Fetch and parse a sitemap.xml. Handles both a plain urlset and a
    sitemap index (a sitemap of sitemaps) by recursing if needed."""
    resp = requests.get(sitemap_url, headers={"User-Agent": USER_AGENT}, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.content, "xml")

    # Sitemap index case: <sitemapindex><sitemap><loc>...
    sub_sitemaps = soup.find_all("sitemap")
    if sub_sitemaps:
        urls = []
        for sm in sub_sitemaps:
            loc = sm.find("loc")
            if loc:
                urls.extend(get_sitemap_urls(loc.text.strip()))
        return urls

    # Plain urlset case: <urlset><url><loc>...
    return [loc.text.strip() for loc in soup.find_all("loc")]


def load_robots_parser() -> RobotFileParser:
    rp = RobotFileParser()
    rp.set_url(ROBOTS_URL)
    rp.read()
    return rp


def should_skip(url: str, robots: RobotFileParser) -> bool:
    if not robots.can_fetch(USER_AGENT, url):
        return True
    return any(re.search(pattern, url) for pattern in SKIP_PATTERNS)


def extract_clean_text(html: str) -> tuple[str, str]:
    """Returns (title, clean_body_text)."""
    soup = BeautifulSoup(html, "lxml")

    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""

    # Prefer a <main> or <article> tag if the theme has one — usually the
    # cleanest signal for "this is the actual content". Fall back to <body>.
    main = soup.find("main") or soup.find("article") or soup.find("body")
    if main is None:
        return title, ""

    for selector in REMOVE_SELECTORS:
        for tag in main.select(selector):
            tag.decompose()

    # Collapse whitespace, keep paragraph breaks
    text = main.get_text(separator="\n", strip=True)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return title, text


def url_to_filename(url: str) -> str:
    path = urlparse(url).path.strip("/")
    slug = path.replace("/", "_") or "home"
    return f"{slug}.json"


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    print(f"Reading robots.txt: {ROBOTS_URL}")
    robots = load_robots_parser()

    print(f"Fetching sitemap: {SITEMAP_URL}")
    urls = get_sitemap_urls(SITEMAP_URL)
    urls = sorted(set(urls))  # dedupe
    print(f"Found {len(urls)} URLs")

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    results = []
    for i, url in enumerate(urls, 1):
        if should_skip(url, robots):
            print(f"[{i}/{len(urls)}] SKIP  {url}")
            continue

        try:
            resp = session.get(url, timeout=20)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"[{i}/{len(urls)}] ERROR {url} -> {e}")
            continue

        title, text = extract_clean_text(resp.text)

        if len(text) < 100:
            # Likely JS-rendered content that didn't come through in raw HTML,
            # or a genuinely thin page. Flag it so you can investigate —
            # you may need Playwright/Selenium for pages like this.
            print(f"[{i}/{len(urls)}] THIN  {url} ({len(text)} chars) — check if JS-rendered")

        page_data = {
            "url": url,
            "title": title,
            "text": text,
            "char_count": len(text),
        }
        results.append(page_data)

        out_path = OUTPUT_DIR / url_to_filename(url)
        out_path.write_text(json.dumps(page_data, ensure_ascii=False, indent=2), encoding="utf-8")

        print(f"[{i}/{len(urls)}] OK    {url} ({len(text)} chars)")
        time.sleep(REQUEST_DELAY_SECONDS)

    # Also write one combined file — handy for the next (chunking) step
    combined_path = ALL_PAGES_JSON
    combined_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nDone. {len(results)} pages saved to {OUTPUT_DIR}/")
    print(f"Combined file: {combined_path}")


if __name__ == "__main__":
    main()