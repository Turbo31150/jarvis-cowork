#!/usr/bin/env python3
"""JARVIS cowork — System health: combined scan + diagnostic + VRAM."""
from __future__ import annotations
import argparse
import json
import sys
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from core.unified.services import get_service_registry
    _services = get_service_registry()
except Exception:
    _services = None

WS_URL = _services.base_url("jarvis_ws") if _services else "http://127.0.0.1:9742"


def _get(url, timeout=15):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def main():
    p = argparse.ArgumentParser(description="System health check")
    p.add_argument("--once", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    results = {}
    results["diagnostic"] = _get(f"{WS_URL}/api/diagnostic/run")
    results["vram"] = _get(f"{WS_URL}/api/vram/status")
    results["rollback"] = _get(f"{WS_URL}/api/rollback/history")
    if args.json:
        json.dump(results, sys.stdout, indent=2, default=str)
    else:
        diag = results.get("diagnostic") or {}
        vram = results.get("vram") or {}
        rb = (results.get("rollback") or {}).get("stats", {})
        print(
            f"Health: {
                diag.get(
                    'health_score',
                    '?')}/100 | VRAM: {
                vram.get(
                    'gpu',
                    {}).get(
                        'vram_pct',
                    '?')}%")
        print(
            f"Issues: {
                len(
                    diag.get(
                        'issues',
                        []))} | Fixes: {
                rb.get(
                    'total_fixes',
                    0)} (rollbacks: {
                            rb.get(
                                'rolled_back',
                                0)})")
        for rec in diag.get("recommendations", [])[:3]:
            print(f"  REC: {rec}")


if __name__ == "__main__":
    main()
