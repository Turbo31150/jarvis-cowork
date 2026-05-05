#!/usr/bin/env python3
"""Cowork wrapper: cleanup_zombies — invoque le script principal."""
from _paths import TURBO_DIR
import subprocess, sys, json
from pathlib import Path
import argparse

SCRIPT = Path(str(TURBO_DIR / "scripts/cleanup_zombies.py"))

def main():
    if not SCRIPT.exists():
        print(json.dumps({"success": False, "error": "cleanup_zombies.py not found"}))
        return
    r = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True, text=True, timeout=30,
        encoding="utf-8", errors="replace"
    )
    print(json.dumps({"success": r.returncode == 0, "output": r.stdout[:500]}))

if __name__ == "__main__":
    main()
