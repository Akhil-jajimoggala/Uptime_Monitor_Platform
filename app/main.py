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

@app.post("/monitors")
def add_monitor(monitor: MonitorCreate):
    with get_connection() as conn:
        row = conn.execute(
            "INSERT INTO monitors (url) VALUES (%s) RETURNING id, url",
            (str(monitor.url),)
        ).fetchone()
    return {"id": row[0], "url": row[1]}


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
