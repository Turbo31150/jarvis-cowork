#!/usr/bin/env python3
"""COWORK MCP Bridge — FastMCP server for COWORK scripts.

Integrates with JARVIS to make all 332+ cowork scripts accessible via MCP.
"""

import sqlite3
import subprocess
import sys
import os
import json
import re
from datetime import datetime
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Setup paths
BASE = Path(__file__).parent
DEV_PATH = BASE / "dev"
# Use environment variable or default to etoile.db in the same directory
DB_PATH = Path(os.getenv("COWORK_DB", str(BASE.parent / "etoile.db")))
PYTHON = sys.executable

# Initialize FastMCP
mcp = FastMCP("jarvis-cowork")

def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db

@mcp.tool()
def cowork_dispatch(query: str) -> str:
    """Find COWORK scripts matching a natural language query."""
    if not query:
        return "Error: query parameter required"

    db = get_db()
    try:
        patterns = db.execute("""
            SELECT pattern_id, agent_id, keywords, description, strategy, priority
            FROM agent_patterns WHERE pattern_id LIKE 'PAT_CW_%'
        """).fetchall()

        query_words = set(re.findall(r'\w+', query.lower()))
        scores = []
        for pat in patterns:
            keywords = set((pat["keywords"] or "").split(","))
            desc_words = set(re.findall(r'\w+', (pat["description"] or "").lower()))
            score = len(query_words & keywords) + len(query_words & desc_words) * 0.5
            if score > 0:
                scripts = db.execute("""
                    SELECT script_name FROM cowork_script_mapping
                    WHERE pattern_id = ? AND status = 'active'
                """, (pat["pattern_id"],)).fetchall()
                scores.append({
                    "pattern_id": pat["pattern_id"],
                    "agent_id": pat["agent_id"],
                    "description": pat["description"],
                    "score": round(score, 2),
                    "scripts": [r["script_name"] for r in scripts]
                })

        scores.sort(key=lambda x: -x["score"])
        return json.dumps({"query": query, "matches": scores[:5]}, indent=2, ensure_ascii=False)
    finally:
        db.close()

@mcp.tool()
def cowork_execute(script: str, args: list = None, timeout: int = 60) -> str:
    """Execute a COWORK script by name."""
    if args is None:
        args = ["--once"]
    
    script_path = DEV_PATH / f"{script}.py"
    if not script_path.exists():
        return f"Error: Script not found: {script}"

    try:
        result = subprocess.run(
            [PYTHON, str(script_path)] + args,
            capture_output=True, text=True, timeout=timeout, cwd=str(DEV_PATH)
        )
        res = {
            "script": script,
            "success": result.returncode == 0,
            "stdout": result.stdout[-3000:] if result.stdout else "",
            "stderr": result.stderr[-500:] if result.stderr else "",
            "returncode": result.returncode
        }
        return json.dumps(res, indent=2, ensure_ascii=False)
    except subprocess.TimeoutExpired:
        return json.dumps({"script": script, "error": "timeout", "success": False}, indent=2)
    except Exception as e:
        return json.dumps({"script": script, "error": str(e), "success": False}, indent=2)

@mcp.tool()
def cowork_list(pattern: str = "") -> str:
    """List COWORK scripts, optionally filtered by pattern_id."""
    db = get_db()
    try:
        if pattern:
            rows = db.execute("""
                SELECT script_name, pattern_id FROM cowork_script_mapping
                WHERE pattern_id = ? AND status = 'active'
            """, (pattern,)).fetchall()
        else:
            rows = db.execute("""
                SELECT script_name, pattern_id FROM cowork_script_mapping
                WHERE status = 'active' ORDER BY pattern_id, script_name
            """).fetchall()

        return json.dumps({"scripts": [dict(r) for r in rows], "count": len(rows)}, indent=2)
    finally:
        db.close()

@mcp.tool()
def cowork_status() -> str:
    """Get current status of the COWORK system."""
    db = get_db()
    try:
        total_patterns = db.execute(
            "SELECT COUNT(*) FROM agent_patterns WHERE pattern_id LIKE 'PAT_CW_%'"
        ).fetchone()[0]
        total_scripts = db.execute(
            "SELECT COUNT(*) FROM cowork_script_mapping WHERE status = 'active'"
        ).fetchone()[0]
        
        # Check if table exists before querying
        tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        total_dispatches = 0
        if "agent_dispatch_log" in tables:
            total_dispatches = db.execute("SELECT COUNT(*) FROM agent_dispatch_log").fetchone()[0]

        script_files = len(list(DEV_PATH.glob("*.py")))
        
        res = {
            "cowork_patterns": total_patterns,
            "mapped_scripts": total_scripts,
            "script_files": script_files,
            "total_dispatches": total_dispatches,
            "db_path": str(DB_PATH),
            "status": "operational"
        }
        return json.dumps(res, indent=2)
    finally:
        db.close()

@mcp.tool()
def cowork_test(script: str) -> str:
    """Test a script (syntax check + --help)."""
    script_path = DEV_PATH / f"{script}.py"
    if not script_path.exists():
        return f"Error: Script not found: {script}"

    # Syntax check
    try:
        with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
            compile(f.read(), str(script_path), 'exec')
    except SyntaxError as e:
        return json.dumps({"script": script, "syntax": "FAIL", "error": str(e)}, indent=2)

    # --help test
    try:
        r = subprocess.run(
            [PYTHON, str(script_path), "--help"],
            capture_output=True, text=True, timeout=10, cwd=str(DEV_PATH)
        )
        return json.dumps({
            "script": script,
            "syntax": "OK",
            "help": "OK" if r.returncode == 0 else "FAIL",
            "help_output": r.stdout[:500] if r.stdout else ""
        }, indent=2)
    except Exception as e:
        return json.dumps({"script": script, "syntax": "OK", "help": "ERROR", "error": str(e)}, indent=2)

@mcp.tool()
def cowork_anticipate() -> str:
    """Predict next needs from dispatch logs."""
    db = get_db()
    try:
        tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        if "agent_dispatch_log" not in tables:
            return "Error: agent_dispatch_log table not found. Run migration first."

        hot = db.execute("""
            SELECT classified_type, COUNT(*) as cnt
            FROM agent_dispatch_log
            GROUP BY classified_type ORDER BY cnt DESC LIMIT 5
        """).fetchall()

        failing = db.execute("""
            SELECT classified_type, COUNT(*) as fails
            FROM agent_dispatch_log WHERE success = 0
            GROUP BY classified_type ORDER BY fails DESC LIMIT 3
        """).fetchall()

        return json.dumps({
            "hot_patterns": [dict(r) for r in hot],
            "failing_patterns": [dict(r) for r in failing]
        }, indent=2)
    finally:
        db.close()

if __name__ == "__main__":
    mcp.run()
