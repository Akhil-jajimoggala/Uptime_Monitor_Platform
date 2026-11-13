from fastapi import FastAPI
from pydantic import BaseModel
from db import get_connection, init_db

app = FastAPI(title="Uptime Monitor Platform", description="A simple uptime monitoring platform", version="1.0.0")

init_db()

class MonitorCreate(BaseModel):
    url:str

@app.get("/healthz")
def healthz():
    return {"status" : "ok"}

@app.post("/monitors")
def add_monitor(monitor: MonitorCreate):
    with get_connection() as conn:
        row = conn.execute(
            "INSERT INTO monitors (url) VALUES (%s) RETURNING id, url",
            (monitor.url,),
        ).fetchone()
    return {"id": row[0], "url": row[1]}


@app.get("/monitors")
def list_monitors():
    with get_connection() as conn:
        rows = conn.execute("SELECT id, url FROM monitors ORDER BY id").fetchall()
    return [{"id": r[0], "url": r[1]} for r in rows]
