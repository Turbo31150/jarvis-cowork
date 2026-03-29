#!/usr/bin/env python3
"""jarvis_portfolio_tracker.py — Portfolio & PnL Tracker (#272).

Tracks open positions from signal_tracker and calculates global PnL.

Usage:
    python dev/jarvis_portfolio_tracker.py --report
    python dev/jarvis_portfolio_tracker.py --json
"""
import argparse
import json
import sqlite3
from datetime import datetime
from pathlib import Path

# Paths
DB_PATH = Path("/home/turbo/jarvis-linux/core/memory/sniper_scan.db")


def get_portfolio_summary():
    """Calculates global PnL from open and closed signals."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Summary metrics
        cursor.execute(
            "SELECT status, count(*), sum(pnl_pct) FROM signal_tracker GROUP BY status")
        rows = cursor.fetchall()

        stats = {}
        total_pnl = 0
        for row in rows:
            stats[row[0]] = {"count": row[1], "pnl": row[2] or 0}
            total_pnl += row[2] or 0

        # Top 5 best trades
        cursor.execute(
            "SELECT symbol, direction, pnl_pct, status FROM signal_tracker ORDER BY pnl_pct DESC LIMIT 5")
        top_trades = cursor.fetchall()

        conn.close()
        return {
            "total_pnl": total_pnl,
            "stats": stats,
            "top_trades": top_trades
        }
    except Exception as e:
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="JARVIS Portfolio Tracker")
    parser.add_argument(
        "--report",
        action="store_true",
        help="Display human-readable report")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON metrics")
    args = parser.parse_args()

    data = get_portfolio_summary()

    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print(
            f"--- JARVIS PORTFOLIO REPORT ({datetime.now().strftime('%Y-%m-%d %H:%M')}) ---")
        if "error" in data:
            print(f"ERROR: {data['error']}")
        else:
            print(f"Total PnL: {data['total_pnl']:.2f}%")
            for status, s in data["stats"].items():
                print(f"[{status}] Count: {s['count']}, PnL: {s['pnl']:.2f}%")
            print("\nTop Trades:")
            for t in data["top_trades"]:
                print(f" - {t[0]} ({t[1]}): {t[2]:.2f}% [{t[3]}]")


if __name__ == "__main__":
    main()
