"""Path resolver for JARVIS Cowork — resolves database and project paths across environments."""

import sqlite3
from pathlib import Path


def resolve_project_root() -> Path:
    """Find the JARVIS project root directory."""
    candidates = [
        Path("/home/turbo/jarvis-cowork"),
        Path("/home/turbo/Workspaces/jarvis-linux"),
        Path("/home/turbo/jarvis-linux"),
        Path("/home/turbo/Workspaces/turbo"),
    ]
    for c in candidates:
        if c.exists():
            return c
    return Path("/home/turbo/jarvis-cowork")


def resolve_db_with_table(db_name: str, table_name: str) -> Path:
    """Find a SQLite database that contains the specified table."""
    search_dirs = [
        Path("/home/turbo/jarvis-cowork"),
        Path("/home/turbo/Workspaces/jarvis-linux/data/db"),
        Path("/home/turbo/Workspaces/jarvis-linux/src/jarvis/core/data/storage"),
        Path("/home/turbo/jarvis-cowork/dev"),
        Path("/home/turbo/data"),
    ]
    for d in search_dirs:
        db_path = d / db_name
        if db_path.exists():
            try:
                conn = sqlite3.connect(str(db_path))
                cursor = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                    (table_name,),
                )
                if cursor.fetchone():
                    conn.close()
                    return db_path
                conn.close()
            except Exception:
                continue
    # Fallback: return first existing db with that name
    for d in search_dirs:
        db_path = d / db_name
        if db_path.exists():
            return db_path
    return search_dirs[0] / db_name


def resolve_openclaw_dev_dir() -> Path:
    """Find the OpenClaw dev directory for cowork scripts."""
    candidates = [
        Path("/home/turbo/jarvis-cowork/dev"),
        Path("/home/turbo/Workspaces/turbo/cowork/dev"),
        Path("/home/turbo/.openclaw/dev"),
    ]
    for c in candidates:
        if c.exists():
            return c
    return candidates[0]
