
#!/usr/bin/env python3
"""jarvis_market_analyzer.py — Market signal aggregator (#270).

Usage:
    python dev/jarvis_market_analyzer.py --once
    python dev/jarvis_market_analyzer.py --list-signals
"""
import argparse
import json
import sqlite3
from datetime import datetime
from pathlib import Path

# Paths
SNIPER_DB = Path("/home/turbo/jarvis-linux/core/memory/sniper.db")
SCAN_DB = Path("/home/turbo/jarvis-linux/core/memory/sniper_scan.db")


def get_latest_signals():
    """Aggregates signals from both sniper and scan databases."""
    signals = []
    try:
        # From sniper_scan.db (signal_tracker)
        if SCAN_DB.exists():
            conn = sqlite3.connect(SCAN_DB)
            cursor = conn.cursor()
            # On suppose des colonnes symbol, side, score (à confirmer par le
            # schema)
            cursor.execute(
                "SELECT * FROM signal_tracker ORDER BY id DESC LIMIT 10")
            rows = cursor.fetchall()
            signals.extend([{"source": "tracker", "data": r} for r in rows])
            conn.close()

        # From sniper.db (signals)
        if SNIPER_DB.exists():
            conn = sqlite3.connect(SNIPER_DB)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM signals ORDER BY id DESC LIMIT 10")
            rows = cursor.fetchall()
            signals.extend([{"source": "sniper", "data": r} for r in rows])
            conn.close()

        return signals
    except Exception as e:
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(
        description="JARVIS Market Analyzer (Batch 118)")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run aggregation once")
    args = parser.parse_args()

    result = {
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "data": {"signals": get_latest_signals()}
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
