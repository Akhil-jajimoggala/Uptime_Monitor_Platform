from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Uptime Monitor Platform", description="A simple uptime monitoring platform", version="1.0.0")

monitors = []

class MonitorCreate(BaseModel):
    url:str

@app.get("/healthz")
def healthz():
    return {"status" : "ok"}

@app.post("/monitors")
def add_monitor(monitor: MonitorCreate):
    new_monitor = {"id": len(monitors) + 1, "url": monitor.url}
    monitors.append(new_monitor)
    return new_monitor


@app.get("/monitors")
def list_monitors():
    return monitors

