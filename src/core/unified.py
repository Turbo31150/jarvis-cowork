"""UnifiedMemoryStore stub — minimal implementation for cowork dispatcher."""

import sqlite3
from pathlib import Path


class UnifiedMemoryStore:
    """Lightweight memory store that resolves and connects to SQLite databases."""

    def __init__(self):
        self._db_dirs = [
            Path("/home/turbo/Workspaces/jarvis-linux/data/db"),
            Path("/home/turbo/Workspaces/jarvis-linux/src/jarvis/core/data/storage"),
            Path("/home/turbo/jarvis-cowork/dev"),
            Path("/home/turbo/data"),
        ]

    class _DBRef:
        def __init__(self, path: Path):
            self.path = path

    def resolve(self, db_name: str) -> "_DBRef":
        if not db_name.endswith(".db"):
            db_name += ".db"
        for d in self._db_dirs:
            p = d / db_name
            if p.exists():
                return self._DBRef(p)
        return self._DBRef(self._db_dirs[0] / db_name)

    def connect(self, db_name: str) -> sqlite3.Connection:
        ref = self.resolve(db_name)
        return sqlite3.connect(str(ref.path))

    def table_columns(self, conn: sqlite3.Connection, table: str) -> list[str]:
        try:
            cursor = conn.execute(f"PRAGMA table_info({table})")
            return [row[1] for row in cursor.fetchall()]
        except Exception:
            return []

    def get_cowork_patterns(self) -> list[dict]:
        try:
            conn = self.connect("etoile")
            cursor = conn.execute(
                "SELECT agent_id, pattern_type, description, keywords, priority, strategy FROM cowork_patterns"
            )
            rows = cursor.fetchall()
            conn.close()
            return [
                {
                    "agent_id": r[0],
                    "pattern_id": r[0],
                    "pattern_type": r[1],
                    "description": r[2],
                    "keywords": r[3] or "",
                    "priority": r[4] or 3,
                    "strategy": r[5] or "single",
                }
                for r in rows
            ]
        except Exception:
            return []

    def get_scripts_for_pattern(self, pattern_id: str) -> list[dict]:
        try:
            conn = self.connect("etoile")
            cursor = conn.execute(
                "SELECT script_name FROM cowork_script_mapping WHERE pattern_id=?",
                (pattern_id,),
            )
            rows = cursor.fetchall()
            conn.close()
            return [{"script_name": r[0]} for r in rows]
        except Exception:
            return []

    @staticmethod
    def normalize_script_name(name: str) -> str:
        return name.strip().replace(".py", "").replace("-", "_").lower()
