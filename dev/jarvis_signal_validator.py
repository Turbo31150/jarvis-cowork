#!/usr/bin/env python3
"""jarvis_signal_validator.py — AI Consensus Signal Validator (#271).

Validates market signals by querying multiple AI nodes (M1, M2, OL1).
Consensus requires at least 2 identical votes.

Usage:
    python dev/jarvis_signal_validator.py --validate
    python dev/jarvis_signal_validator.py --consensus-check SYMBOL
"""
import argparse
import json
import sqlite3
import urllib.request
from datetime import datetime
from pathlib import Path

# Config
NODES = {
    "M1": "http://127.0.0.1:1234/v1/chat/completions",
    "M2": "http://192.168.1.26:1234/v1/chat/completions",
    "OL1": "http://127.0.0.1:11434/v1/chat/completions"
}
DB_PATH = Path("/home/turbo/jarvis-linux/core/memory/sniper_scan.db")


def query_llm(url, model, prompt):
    """Queries a model via OpenAI-compatible API using stdlib."""
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1
    }
    try:
        req = urllib.request.Request(
            url, data=json.dumps(data).encode('utf-8'))
        req.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req, timeout=10) as response:
            res = json.loads(response.read().decode('utf-8'))
            return res['choices'][0]['message']['content'].upper()
    except Exception as e:
        return f"ERROR: {e}"


def validate_signal(symbol, direction, price):
    """Asks M1, M2, and OL1 for validation."""
    prompt = f"Analyze {symbol} {direction} at {price}. Reply only VALID or REJECT."
    votes = []

    # M1 - Qwen3-8b (Local Champion)
    votes.append(query_llm(NODES["M1"], "qwen/qwen3-8b", prompt))

    # M2 - Deepseek-R1-8b (Reasoning)
    votes.append(query_llm(NODES["M2"], "deepseek-r1-0528-qwen3-8b", prompt))

    # OL1 - Deepseek-R1-7b (Ollama)
    votes.append(query_llm(NODES["OL1"], "deepseek-r1:7b", prompt))

    valid_votes = [v for v in votes if "VALID" in v]
    consensus = len(valid_votes) >= 2

    return {
        "symbol": symbol,
        "votes": votes,
        "consensus": consensus,
        "score": len(valid_votes) / 3 * 100
    }


def main():
    parser = argparse.ArgumentParser(description="JARVIS AI Signal Validator")
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate pending signals")
    parser.add_argument("--check", type=str, help="Check specific symbol")
    args = parser.parse_args()

    if args.check:
        # Mock check for testing
        print(json.dumps(validate_signal(args.check, "LONG", 50000), indent=2))
    elif args.validate:
        # Fetch pending signals from DB
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT symbol, direction, entry_price FROM signal_tracker WHERE status='OPEN' AND validations < 3")
            rows = cursor.fetchall()
            for row in rows:
                v = validate_signal(row[0], row[1], row[2])
                print(
                    f"Validated {
                        row[0]}: Consensus={
                        v['consensus']} ({
                        v['score']}%)")
                # Update validations here if needed
            conn.close()
        except Exception as e:
            print(f"DB Error: {e}")


if __name__ == "__main__":
    main()
