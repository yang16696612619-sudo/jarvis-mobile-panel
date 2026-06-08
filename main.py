"""Jarvis Mobile Web — read-only status panel."""

from __future__ import annotations

import json
import os
import re
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

# Privacy: scrub local paths from pushed data
_PATH_PATTERN = re.compile(r"[A-Za-z]:\\(?:[^\\\s]+\\)*[^\\\s]*")


def sanitize(data: dict) -> dict:
    d = json.loads(json.dumps(data))
    if "key" in d:
        d["key"].pop("source", None)
        d["key"].pop("mimo_source", None)
    for w in d.get("workers", {}).values():
        if "summary" in w and w["summary"]:
            w["summary"] = _PATH_PATTERN.sub("[路径]", w["summary"])
    if "reports" in d:
        for r in d["reports"]:
            r.pop("preview", None)
    return d


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
    sanitized = sanitize(body)
    latest.clear()
    latest.update(sanitized)
    return {"ok": True, "received_at": now}


@app.get("/api/status")
async def get_status():
    return latest


@app.get("/")
async def index():
    html = (HERE / "templates" / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(html)


@app.get("/voice-test")
async def voice_test():
    html = (HERE / "templates" / "voice_test.html").read_text(encoding="utf-8")
    return HTMLResponse(html)
