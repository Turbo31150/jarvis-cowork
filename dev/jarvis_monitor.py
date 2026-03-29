#!/usr/bin/env python3
"""JARVIS Service Monitor — checks health of all JARVIS services."""
import argparse, json, time, urllib.request
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from core.unified.services import get_service_registry
    _services = get_service_registry()
except Exception:
    _services = None

SERVICES = {
    "WS": _services.health_url("jarvis_ws") if _services else "http://127.0.0.1:9742/health",
    "M1-LMStudio": "http://127.0.0.1:1234/api/v1/models",
    "OL1-Ollama": _services.health_url("ollama") if _services else "http://127.0.0.1:11434/api/tags",
    "OpenClaw": _services.health_url("openclaw") if _services else "http://127.0.0.1:18789/health",
    "BrowserOS": _services.health_url("browseros") if _services else "http://127.0.0.1:9200/health",
    "Dashboard": "http://127.0.0.1:8080",
    "Gemini-Proxy": "http://127.0.0.1:18791/health",
    "Canvas-Proxy": "http://127.0.0.1:18800/health",
}

def check_service(name: str, url: str) -> dict:
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            return {"name": name, "status": "online", "code": resp.status}
    except Exception as e:
        return {"name": name, "status": "offline", "error": str(e)[:80]}

def main():
    parser = argparse.ArgumentParser(description="Monitor JARVIS services")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    results = [check_service(name, url) for name, url in SERVICES.items()]
    online = sum(1 for r in results if r["status"] == "online")

    if args.json:
        print(json.dumps({"services": results, "online": online, "total": len(SERVICES)}))
    else:
        for r in results:
            icon = "+" if r["status"] == "online" else "X"
            print(f"[{icon}] {r['name']}: {r['status']}")
        print(f"\n{online}/{len(SERVICES)} services online")

if __name__ == "__main__":
    main()
