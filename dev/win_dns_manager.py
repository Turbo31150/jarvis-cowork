#!/usr/bin/env python3
"""win_dns_manager.py — DNS Manager & Cache Analytics (#276).

Usage (Linux-Native):
    python dev/win_dns_manager.py --status
    python dev/win_dns_manager.py --set-dns "8.8.8.8 8.8.4.4"
    python dev/win_dns_manager.py --flush
"""
import argparse
import json
import subprocess
import sys


def get_dns_status():
    """Gets DNS status using resolvectl."""
    try:
        output = subprocess.check_output(['resolvectl', 'status'], text=True)
        return output.strip()
    except Exception as e:
        return f"Error: {e}"


def flush_cache():
    """Flushes DNS cache using resolvectl."""
    try:
        subprocess.run(['resolvectl', 'flush-caches'], check=True)
        return True
    except Exception as e:
        print(f"Flush Error: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="JARVIS DNS Manager (Linux Native)")
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show DNS status")
    parser.add_argument("--flush", action="store_true", help="Flush DNS cache")
    args = parser.parse_args()

    result = {"status": "success", "data": {}}
    if args.status:
        result["data"]["dns"] = get_dns_status()
    elif args.flush:
        if flush_cache():
            result["data"]["message"] = "DNS cache flushed"
    else:
        parser.print_help()
        return

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
