#!/usr/bin/env python3
"""One-shot scanner for new Wechatsync Markdown ZIP exports.

Designed to be called by macOS launchd every 30 seconds. It only processes ZIPs that
contain article.md, remembers successful archive hashes, and delegates the real work
to publish_wechatsync_zip.py.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = Path.home() / "Downloads"
STATE_DIR = Path.home() / "Library" / "Application Support" / "DupontMaster"
STATE_FILE = STATE_DIR / "wechatsync-publisher-state.json"
PUBLISHER = ROOT / "scripts" / "publish_wechatsync_zip.py"


def archive_hash(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def is_wechatsync_zip(path: Path) -> bool:
    try:
        with zipfile.ZipFile(path) as zf:
            names = {name.lstrip("./") for name in zf.namelist()}
            return "article.md" in names or any(name.endswith("/article.md") for name in names)
    except (zipfile.BadZipFile, OSError):
        return False


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {"processed": {}}
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("processed"), dict):
            return data
    except Exception:
        pass
    return {"processed": {}}


def save_state(state: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    # Keep state bounded; newest successful archives are enough for duplicate prevention.
    processed = state.get("processed", {})
    if len(processed) > 200:
        processed = dict(list(processed.items())[-200:])
        state["processed"] = processed
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(STATE_FILE)


def main() -> int:
    if not DOWNLOADS.exists() or not PUBLISHER.exists():
        return 0

    state = load_state()
    processed: dict[str, dict] = state.setdefault("processed", {})

    # Only inspect reasonably recent files. launchd runs frequently, so this stays cheap.
    candidates = sorted(
        (p for p in DOWNLOADS.glob("*.zip") if p.is_file()),
        key=lambda p: p.stat().st_mtime,
    )[-40:]

    for path in candidates:
        if not is_wechatsync_zip(path):
            continue
        digest = archive_hash(path)
        if digest in processed:
            continue

        print(f"发现文章同步助手压缩包：{path.name}", flush=True)
        result = subprocess.run(
            [sys.executable, str(PUBLISHER), str(path)],
            cwd=ROOT,
            text=True,
        )
        if result.returncode == 0:
            processed[digest] = {
                "filename": path.name,
                "mtime": path.stat().st_mtime,
            }
            save_state(state)
            print(f"官网发布完成：{path.name}", flush=True)
        else:
            # Do not mark failed packages as processed. A later run can retry after the
            # user fixes OSS/Git/Vercel prerequisites.
            print(f"官网发布失败，将保留待重试：{path.name}", flush=True)
            return result.returncode

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
