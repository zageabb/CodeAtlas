"""CodeAtlas web API and packaged architecture explorer.

Bind to loopback only until authentication and source access policies are added.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .analyzer import analyze
from .source import snapshot

app = FastAPI(title="CodeAtlas", version="0.2.0")


class ScanRequest(BaseModel):
    source: str


@app.post("/api/analyse")
def analyse(request: ScanRequest):
    try:
        with snapshot(request.source) as root:
            return analyze(root)
    except (ValueError, subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Analysis failed: {type(exc).__name__}",
        ) from exc


@app.get("/")
def home():
    """Serve the packaged, dependency-free architecture explorer."""
    return FileResponse(
        Path(__file__).parent / "static" / "index.html",
        media_type="text/html",
    )
