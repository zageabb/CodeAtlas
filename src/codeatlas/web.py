"""CodeAtlas web API and packaged architecture explorer.

Bind to loopback only until authentication and source access policies are added.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from urllib.parse import urlparse

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
            result = analyze(root)
            git = subprocess.run(
                ["git", "-C", str(root), "rev-parse", "--verify", "HEAD"],
                capture_output=True, text=True, timeout=10, check=False,
            )
            sha = git.stdout.strip() if git.returncode == 0 else None
            if sha and (len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha.lower())):
                sha = None
            parsed = urlparse(request.source)
            repo_url = (
                "https://github.com" + parsed.path.removesuffix(".git").rstrip("/")
                if parsed.scheme == "https" and parsed.hostname == "github.com"
                else None
            )
            result["provenance"] = {
                "source": repo_url or "local directory",
                "repository_url": repo_url,
                "commit_sha": sha,
                "immutable_source_links": bool(repo_url and sha),
            }
            return result
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
