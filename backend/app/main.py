from fastapi import FastAPI, Header, HTTPException
from apscheduler.schedulers.background import BackgroundScheduler

from . import config
from .database import init_db, get_conn
from .ingest import run_ingest_cycle

app = FastAPI(title="Futbol Gündem API")
scheduler = BackgroundScheduler()


def _check_token(x_token: str | None):
    if config.API_TOKEN and x_token != config.API_TOKEN:
        raise HTTPException(status_code=401, detail="invalid token")


@app.on_event("startup")
def on_startup():
    init_db()
    scheduler.add_job(
        run_ingest_cycle,
        "interval",
        hours=config.SCRAPE_INTERVAL_HOURS,
        id="ingest_cycle",
    )
    scheduler.start()


@app.on_event("shutdown")
def on_shutdown():
    scheduler.shutdown(wait=False)


@app.get("/api/topics")
def list_topics(limit: int = 50, competition: str | None = None):
    limit = max(1, min(limit, 200))
    query = "SELECT title, summary, source_url, source_name, competition, discovered_at FROM topics"
    params: list = []
    if competition:
        query += " WHERE competition = ?"
        params.append(competition)
    query += " ORDER BY discovered_at DESC LIMIT ?"
    params.append(limit)

    with get_conn() as conn:
        rows = conn.execute(query, params).fetchall()
    return {"topics": [dict(r) for r in rows]}


@app.post("/api/ingest/run")
def trigger_ingest(x_token: str | None = Header(default=None)):
    _check_token(x_token)
    return run_ingest_cycle()


@app.get("/api/health")
def health():
    return {"ok": True}
