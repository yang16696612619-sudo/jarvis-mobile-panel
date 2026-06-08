"""Jarvis Mobile Web — Railway read-only status panel."""

from __future__ import annotations

import os
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse

HERE = Path(__file__).resolve().parent

app = FastAPI(title="Jarvis Mobile Web")

PUSH_TOKEN = os.environ.get("PUSH_TOKEN", "")
if not PUSH_TOKEN:
    raise RuntimeError("PUSH_TOKEN environment variable is required")

latest: dict = {"status": "waiting", "updated_at": None, "_received_at": 0}


@app.post("/api/push")
async def push_status(req: Request):
    auth = req.headers.get("Authorization", "")
    token = auth.replace("Bearer ", "")
    if token != PUSH_TOKEN:
        raise HTTPException(401, "invalid token")
    body = await req.json()
    now = time.time()
    body["_received_at"] = now
    body["status"] = "ok"
    latest.clear()
    latest.update(body)
    return {"ok": True, "received_at": now}


@app.get("/api/status")
async def get_status():
    return latest


@app.get("/")
async def index():
    html = (HERE / "templates" / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(html)
