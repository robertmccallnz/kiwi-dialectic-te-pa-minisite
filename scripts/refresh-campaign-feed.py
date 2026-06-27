#!/usr/bin/env python3
"""
Refresh /data/campaign-categories.json with current Indigenous-news headlines.

Run weekly via cron. Reads the curated baseline, fetches a small set of trusted
Indigenous-led news RSS feeds, classifies each headline into one of the existing
category IDs by keyword match, and writes back enriched JSON. The curated
`slogans`, `attribution`, and `sources` fields are NEVER touched. Only
`current_headlines`, `feed_last_refreshed`, and `feed_sources` are updated.

If a feed is unreachable or malformed, the script logs and skips it — the
curated baseline always remains the source of truth.

Usage:
    python3 scripts/refresh-campaign-feed.py
    python3 scripts/refresh-campaign-feed.py --dry-run     # don't write
    python3 scripts/refresh-campaign-feed.py --verbose
"""

from __future__ import annotations
import argparse
import datetime as dt
import json
import re
import sys
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = REPO_ROOT / "data" / "campaign-categories.json"

# Indigenous-led or Indigenous-focused news sources. RSS only — no JS scraping.
FEED_SOURCES = [
    {"id": "ictnews",            "name": "ICT News (Indian Country Today)",  "url": "https://ictnews.org/feed"},
    {"id": "cultural-survival",  "name": "Cultural Survival",                "url": "https://www.culturalsurvival.org/rss.xml"},
    {"id": "survival",           "name": "Survival International",           "url": "https://www.survivalinternational.org/news.rss"},
    {"id": "waatea",             "name": "Waatea News (Māori)",              "url": "https://waateanews.com/feed/"},
    {"id": "first-nations-tg",   "name": "The Guardian — First Nations AU",  "url": "https://www.theguardian.com/australia-news/indigenous-australians/rss"},
]

# Keyword routing — headlines go to the first category whose keywords match.
# All matching is case-insensitive on the title+description string.
ROUTING = [
    ("mauna-kea",                ["mauna kea", "tmt", "mauna a wakea", "puuhonua"]),
    ("west-papua",               ["west papua", "papua merdeka", "papuan", "ulmwp"]),
    ("mmiw",                     ["mmiw", "mmiwg", "missing and murdered", "stolen sisters"]),
    ("land-back",                ["land back", "landback", "land return", "rematriation"]),
    ("ihumatao",                 ["ihumatao", "ihumātao", "soul protectors"]),
    ("palestine-indigenous-solidarity", ["palestine", "gaza", "from aotearoa to palestine", "settler colonialism"]),
    ("language-revitalisation",  ["language revitalisation", "language revitalization", "reo māori", "te reo", "endangered language", "first languages"]),
    ("climate-frontlines",       ["climate", "pacific climate", "rising seas", "just transition", "fossil fuel"]),
    ("ai-sovereignty",           ["ai ", "artificial intelligence", "algorithm", "data sovereignty", "indigenous data"]),
    ("data-sovereignty",         ["data sovereignty", "care principles", "te mana raraunga", "maiam nayri wingara", "ocap"]),
    ("anti-extraction",          ["pipeline", "mine", "dam ", "extraction", "wet'suwet'en", "standing rock", "line 3"]),
    ("treaty-aotearoa",          ["treaty", "te tiriti", "waitangi", "toitū te tiriti", "treaty principles bill"]),
    ("anti-racism-policing",     ["deaths in custody", "police", "blak lives", "black lives matter", "racism", "racial"]),
]

MAX_HEADLINES_PER_CATEGORY = 4
MAX_HEADLINE_AGE_DAYS = 60

REQUEST_HEADERS = {
    "User-Agent": "te-pa.org/campaign-feed-refresh (https://te-pa.org)",
    "Accept": "application/rss+xml, application/xml, text/xml",
}


def log(msg: str, *, verbose: bool, force: bool = False) -> None:
    if verbose or force:
        print(msg, file=sys.stderr)


def fetch_feed(url: str, *, verbose: bool, timeout: int = 20) -> list[dict]:
    """Fetch and parse an RSS or Atom feed. Returns a list of {title, link, summary, pubdate}."""
    req = urllib.request.Request(url, headers=REQUEST_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
    except (urllib.error.URLError, TimeoutError) as e:
        log(f"  feed unreachable ({url}): {e}", verbose=verbose, force=True)
        return []

    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        log(f"  feed malformed ({url}): {e}", verbose=verbose, force=True)
        return []

    items: list[dict] = []
    # RSS 2.0
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        summary = (item.findtext("description") or "").strip()
        pubdate = (item.findtext("pubDate") or "").strip()
        if title and link:
            items.append({"title": title, "link": link, "summary": summary[:300], "pubdate": pubdate})
    # Atom
    atom_ns = "{http://www.w3.org/2005/Atom}"
    for entry in root.iter(f"{atom_ns}entry"):
        title = (entry.findtext(f"{atom_ns}title") or "").strip()
        link_el = entry.find(f"{atom_ns}link")
        link = (link_el.get("href") if link_el is not None else "") or ""
        summary = (entry.findtext(f"{atom_ns}summary") or entry.findtext(f"{atom_ns}content") or "").strip()
        pubdate = (entry.findtext(f"{atom_ns}updated") or entry.findtext(f"{atom_ns}published") or "").strip()
        if title and link:
            items.append({"title": title, "link": link, "summary": summary[:300], "pubdate": pubdate})
    return items


def parse_pubdate(s: str) -> dt.datetime | None:
    if not s:
        return None
    # RSS RFC 2822-ish
    for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return dt.datetime.strptime(s, fmt).astimezone(dt.timezone.utc)
        except ValueError:
            continue
    return None


def route_headline(title: str, summary: str) -> str | None:
    text = (title + " " + summary).lower()
    text = re.sub(r"<[^>]+>", " ", text)
    for cat_id, keywords in ROUTING:
        for kw in keywords:
            if kw in text:
                return cat_id
    return None


def strip_html(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    if not DATA_FILE.exists():
        print(f"ERROR: {DATA_FILE} not found", file=sys.stderr)
        return 2

    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    log(f"Loaded {len(data['categories'])} curated categories.", verbose=args.verbose, force=True)

    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=MAX_HEADLINE_AGE_DAYS)
    per_category: dict[str, list[dict]] = {c["id"]: [] for c in data["categories"]}
    feeds_ok: list[dict] = []
    feeds_failed: list[dict] = []

    for src in FEED_SOURCES:
        log(f"Fetching {src['name']} …", verbose=args.verbose, force=True)
        items = fetch_feed(src["url"], verbose=args.verbose)
        if not items:
            feeds_failed.append({"id": src["id"], "name": src["name"], "url": src["url"]})
            continue
        feeds_ok.append({"id": src["id"], "name": src["name"], "url": src["url"], "items_seen": len(items)})

        for item in items:
            pub = parse_pubdate(item["pubdate"])
            if pub and pub < cutoff:
                continue
            cat = route_headline(item["title"], item["summary"])
            if not cat:
                continue
            bucket = per_category.get(cat)
            if bucket is None or len(bucket) >= MAX_HEADLINES_PER_CATEGORY:
                continue
            bucket.append({
                "title": strip_html(item["title"])[:240],
                "link": item["link"],
                "source": src["name"],
                "source_id": src["id"],
                "published": pub.isoformat() if pub else None,
            })

    headlines_flat = []
    for cat_id, items in per_category.items():
        for it in items:
            headlines_flat.append({**it, "category": cat_id})

    log(f"Matched {len(headlines_flat)} headlines across {sum(1 for v in per_category.values() if v)} categories.", verbose=args.verbose, force=True)

    data["current_headlines"] = headlines_flat
    data["feed_last_refreshed"] = dt.datetime.now(dt.timezone.utc).isoformat()
    data["feed_sources"] = {"ok": feeds_ok, "failed": feeds_failed}

    if args.dry_run:
        log("--dry-run: not writing.", verbose=args.verbose, force=True)
        print(json.dumps({"matched": len(headlines_flat), "categories_active": sum(1 for v in per_category.values() if v), "feeds_ok": len(feeds_ok), "feeds_failed": len(feeds_failed)}, indent=2))
        return 0

    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log(f"Wrote {DATA_FILE}", verbose=args.verbose, force=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
