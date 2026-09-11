import feedparser

# Global football RSS sources. Kept small and reputable so parsing stays
# reliable without needing per-site HTML scraping.
FEEDS = [
    {"name": "BBC Sport Football", "url": "https://feeds.bbci.co.uk/sport/football/rss.xml"},
    {"name": "Sky Sports Football", "url": "https://www.skysports.com/rss/12040"},
    {"name": "ESPN Soccer", "url": "https://www.espn.com/espn/rss/soccer/news"},
    {"name": "The Guardian Football", "url": "https://www.theguardian.com/football/rss"},
]


def fetch_raw_entries(max_per_feed: int = 8):
    """Pull recent entries from each configured RSS feed.

    Returns a flat list of dicts: {title, link, source_name, published}.
    Network/parse errors on one feed never take down the others.
    """
    entries = []
    for feed in FEEDS:
        try:
            parsed = feedparser.parse(feed["url"])
        except Exception:
            continue
        for e in parsed.entries[:max_per_feed]:
            link = getattr(e, "link", None)
            title = getattr(e, "title", None)
            if not link or not title:
                continue
            entries.append({
                "title": title,
                "link": link,
                "source_name": feed["name"],
                "published": getattr(e, "published", None),
                "summary_raw": getattr(e, "summary", ""),
            })
    return entries
