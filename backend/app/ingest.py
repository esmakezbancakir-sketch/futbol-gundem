import uuid
from datetime import datetime, timezone, timedelta

from . import config
from .database import get_conn
from .scraper import fetch_raw_entries
from .summarize import summarize_topics


def run_ingest_cycle() -> dict:
    """One full cycle: scrape RSS -> ask Claude for the top topics -> store.

    Safe to call repeatedly (e.g. every 6h via the scheduler, or manually
    for a one-off test) — dedup on source_url makes re-runs idempotent.
    """
    raw_entries = fetch_raw_entries()
    topics = summarize_topics(raw_entries)

    inserted = 0
    now = datetime.now(timezone.utc).isoformat()
    with get_conn() as conn:
        for t in topics:
            source_url = t.get("source_url")
            if not source_url:
                continue
            try:
                cursor = conn.execute(
                    "INSERT OR IGNORE INTO topics "
                    "(id, title, summary, source_url, source_name, competition, discovered_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        str(uuid.uuid4()),
                        t.get("title", ""),
                        t.get("summary", ""),
                        source_url,
                        t.get("source_name", ""),
                        t.get("competition", ""),
                        now,
                    ),
                )
                if cursor.rowcount:
                    inserted += 1
            except Exception:
                continue

        cutoff = (datetime.now(timezone.utc) - timedelta(days=config.RETENTION_DAYS)).isoformat()
        conn.execute("DELETE FROM topics WHERE discovered_at < ?", (cutoff,))

    return {"scraped": len(raw_entries), "candidates": len(topics), "inserted": inserted}
