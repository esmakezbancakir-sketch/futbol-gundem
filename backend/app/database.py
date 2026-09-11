import sqlite3
import os
from contextlib import contextmanager

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS topics (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    source_url TEXT NOT NULL UNIQUE,
    source_name TEXT,
    competition TEXT,
    discovered_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_topics_discovered_at ON topics(discovered_at DESC);
"""


def init_db():
    os.makedirs(config.DATA_DIR, exist_ok=True)
    with get_conn() as conn:
        conn.executescript(SCHEMA)


@contextmanager
def get_conn():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
