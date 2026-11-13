from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl, field_validator
from db import get_connection, init_db
from checker import check_url

import re
from urllib.parse import urlsplit, urlunsplit

app = FastAPI(title="Uptime Monitor Platform", description="A simple uptime monitoring platform", version="1.0.0")

init_db()

class MonitorCreate(BaseModel):
    url:HttpUrl

@app.get("/healthz")
def healthz():
    return {"status" : "ok"}

def normalize_url(raw: str) -> str:
    url = raw.strip()
    if not url or re.search(r"\s", url):
        raise ValueError("Enter a valid website address, e.g. google.com")

    # fix typos like "https:www.google.com" or "https:/www.google.com"
    url = re.sub(r"^(https?):/{0,2}(?=[^/])", r"\1://", url, flags=re.IGNORECASE)

    # no scheme at all, e.g. "google.com" or "www.google.com"
    if not re.match(r"^https?://", url, flags=re.IGNORECASE):
        url = "https://" + url

    parts = urlsplit(url)
    host = parts.hostname
    if not host or ("." not in host and host != "localhost"):
        raise ValueError("Enter a valid website address, e.g. google.com")

    path = "" if parts.path == "/" else parts.path
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, parts.query, ""))


class MonitorCreate(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def clean_url(cls, value):
        return normalize_url(value)

@app.post("/monitors")
def add_monitor(monitor: MonitorCreate):
    with get_connection() as conn:
        row = conn.execute(
            "INSERT INTO monitors (url) VALUES (%s) RETURNING id, url",
            (str(monitor.url),)
        ).fetchone()
    return {"id": row[0], "url": row[1]}

@app.delete("/monitors/{monitor_id}", status_code=204)
def delete_monitor(monitor_id: int):
    with get_connection() as conn:
        deleted = conn.execute(
            "DELETE FROM monitors WHERE id = %s RETURNING id", (monitor_id,)
        ).fetchone()
    if deleted is None:
        raise HTTPException(status_code=404, detail="Monitor not found")

@app.post("/monitors/{monitor_id}/check")
def run_check(monitor_id: int):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT url FROM monitors WHERE id = %s", (monitor_id,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Monitor not found")

    is_up, result, seconds = check_url(row[0])

    with get_connection() as conn:
        conn.execute(
            "INSERT INTO checks (monitor_id, is_up, result, response_time) "
            "VALUES (%s, %s, %s, %s)",
            (monitor_id, is_up, str(result), seconds),
        )
    return {"is_up": is_up, "result": str(result), "response_time": seconds}


@app.get("/monitors/{monitor_id}/history")
def monitor_history(monitor_id: int, limit: int = 20):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT is_up, result, response_time, checked_at FROM checks "
            "WHERE monitor_id = %s ORDER BY checked_at DESC LIMIT %s",
            (monitor_id, limit),
        ).fetchall()
    return [
        {
            "is_up": r[0],
            "result": r[1],
            "response_time": r[2],
            "checked_at": r[3].isoformat(),
        }
        for r in rows
    ]

@app.get("/monitors")
def list_monitors():
    with get_connection() as conn:
        rows = conn.execute("SELECT id, url FROM monitors ORDER BY id").fetchall()
    return [{"id": r[0], "url": r[1]} for r in rows]
