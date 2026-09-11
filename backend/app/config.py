import os

DATA_DIR = os.environ.get("DATA_DIR", "/data")
DB_PATH = os.path.join(DATA_DIR, "topics.db")

API_TOKEN = os.environ.get("API_TOKEN", "")
RETENTION_DAYS = int(os.environ.get("RETENTION_DAYS", "30"))
SCRAPE_INTERVAL_HOURS = int(os.environ.get("SCRAPE_INTERVAL_HOURS", "6"))
MAX_TOPICS_PER_RUN = int(os.environ.get("MAX_TOPICS_PER_RUN", "10"))

CLAUDE_BIN = os.environ.get("CLAUDE_BIN", "claude")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5")
