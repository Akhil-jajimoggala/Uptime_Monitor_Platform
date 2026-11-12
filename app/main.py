from fastapi import FastAPI

app = FastAPI(title="Uptime Monitor Platform", description="A simple uptime monitoring platform", version="1.0.0")

@app.get("/healthz")
def healthz():
    return {"status" : "ok"}

