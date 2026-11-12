"""Temporary download links for generated files (Excel / HTML naqsha / PDF).

Files live in a temp folder for 24 hours and are served at
/files/<random token>/<file name>. The token is long and random, so only someone
holding the link can open the file.
"""
from __future__ import annotations

import os
import re
import secrets
import tempfile
import time
from pathlib import Path

TTL_SECONDS = 24 * 3600
ROOT = Path(os.environ.get("FARAID_FILES_DIR") or Path(tempfile.gettempdir()) / "faraid_files")
TOKEN_RE = re.compile(r"^[A-Za-z0-9_-]{20,64}$")
NAME_RE = re.compile(r"^[\w.\-]{1,120}$", re.UNICODE)

MEDIA = {
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".pdf": "application/pdf",
    ".html": "text/html; charset=utf-8",
}


def base_url() -> str:
    return (os.environ.get("PUBLIC_BASE_URL") or os.environ.get("RENDER_EXTERNAL_URL")
            or f"http://localhost:{os.environ.get('PORT', '8000')}").rstrip("/")


def cleanup() -> None:
    if not ROOT.exists():
        return
    now = time.time()
    for d in ROOT.iterdir():
        try:
            if d.is_dir() and now - d.stat().st_mtime > TTL_SECONDS:
                for f in d.iterdir():
                    f.unlink()
                d.rmdir()
        except OSError:
            pass


def new_bundle():
    """A fresh private folder for one result; returns (folder, url_for(file_name))."""
    cleanup()
    token = secrets.token_urlsafe(24)
    folder = ROOT / token
    folder.mkdir(parents=True, exist_ok=True)
    return folder, lambda name: f"{base_url()}/files/{token}/{name}"


def find(token: str, name: str) -> Path | None:
    if not TOKEN_RE.match(token) or not NAME_RE.match(name):
        return None
    p = ROOT / token / name
    if p.is_file() and time.time() - p.stat().st_mtime <= TTL_SECONDS:
        return p
    return None
