#!/usr/bin/env python3
"""Auto-repair: analyse errors from orchestrator runs and attempts fixes."""
import argparse
from _paths import TELEGRAM_TOKEN, TELEGRAM_CHAT
import sys
import json
import os
import sqlite3
import subprocess
import time
import urllib.parse
import urllib.request
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

SCRIPT_DIR = Path(__file__).resolve().parent
DB_PATH = SCRIPT_DIR / "data" / "cowork_gaps.db"


def send_telegram(text):
    data = urllib.parse.urlencode(
        {"chat_id": TELEGRAM_CHAT, "text": text[:4000]}).encode()
    try:
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data)
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass


def get_recent_failures(hours=2):
    """Get recent task failures from orchestrator_runs."""
    if not DB_PATH.exists():
        return []
    conn = sqlite3.connect(str(DB_PATH), timeout=10)
    conn.row_factory = sqlite3.Row
    cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
    rows = conn.execute("""
        SELECT task_name, timestamp, output_summary
        FROM orchestrator_runs
        WHERE success = 0 AND timestamp > ?
        ORDER BY timestamp DESC LIMIT 20
    """, (cutoff,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def check_cluster_health():
    """Quick health check of cluster nodes."""
    import urllib.request


if __name__ == "__main__":
    pass
