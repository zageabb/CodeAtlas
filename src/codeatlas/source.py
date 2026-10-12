"""Acquire source snapshots without running repository code."""
from __future__ import annotations

import re
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlparse

GITHUB = re.compile(r"^/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?/?$")


@contextmanager
def snapshot(location: str):
    if location.startswith("https://"):
        parsed = urlparse(location)
        if parsed.hostname != "github.com" or parsed.port is not None or not GITHUB.fullmatch(parsed.path) or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("Only canonical GitHub HTTPS repository URLs are supported")
        with tempfile.TemporaryDirectory(prefix="codeatlas-") as directory:
            subprocess.run(
                ["git", "-c", "protocol.file.allow=never", "clone", "--depth", "1",
                 "--single-branch", "--", location, directory],
                check=True, timeout=120, capture_output=True, text=True,
                env={"PATH": "/usr/bin:/bin", "GIT_TERMINAL_PROMPT": "0", "GIT_CONFIG_NOSYSTEM": "1"},
            )
            yield Path(directory)
    else:
        path = Path(location).expanduser().resolve()
        if not path.is_dir():
            raise ValueError("Source directory not found")
        yield path
