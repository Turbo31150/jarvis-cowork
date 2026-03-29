#!/usr/bin/env python3
"""win_bandwidth_monitor.py — Bandwidth monitoring by interface (#277).

Reads /proc/net/dev (kernel) to calculate throughput in KB/s.

Usage:
    python dev/win_bandwidth_monitor.py --once
    python dev/win_bandwidth_monitor.py --loop --interval 1
"""
import argparse
import json
import time
from datetime import datetime


def get_net_dev():
    """Reads /proc/net/dev and returns statistics."""
    with open('/proc/net/dev', 'r') as f:
        lines = f.readlines()[2:]

    stats = {}
    for line in lines:
        parts = line.split(':')
        if len(parts) < 2:
            continue
        interface = parts[0].strip()
        data = parts[1].split()
        # rx_bytes=data[0], tx_bytes=data[8]
        stats[interface] = {"rx": int(data[0]), "tx": int(data[8])}
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="JARVIS Bandwidth Monitor (Linux Native)")
    parser.add_argument(
        "--once",
        action="store_true",
        help="One-shot measurement")
    parser.add_argument(
        "--loop",
        action="store_true",
        help="Continuous monitoring")
    parser.add_argument(
        "--interval",
        type=int,
        default=1,
        help="Interval (seconds)")
    args = parser.parse_args()

    if args.once:
        t1 = get_net_dev()
        time.sleep(1)
        t2 = get_net_dev()

        diff = {}
        for iface in t2:
            if iface in t1:
                diff[iface] = {
                    "rx_kbps": (t2[iface]["rx"] - t1[iface]["rx"]) / 1024,
                    "tx_kbps": (t2[iface]["tx"] - t1[iface]["tx"]) / 1024
                }

        print(json.dumps(
            {"timestamp": datetime.now().isoformat(), "stats": diff}, indent=2))
    elif args.loop:
        print("Monitoring... (Ctrl+C to stop)")
        try:
            last = get_net_dev()
            while True:
                time.sleep(args.interval)
                current = get_net_dev()
                for iface in current:
                    if iface in last:
                        rx = (current[iface]["rx"] - last[iface]
                              ["rx"]) / (1024 * args.interval)
                        tx = (current[iface]["tx"] - last[iface]
                              ["tx"]) / (1024 * args.interval)
                        if rx > 0 or tx > 0:
                            print(
                                f"[{iface}] RX: {rx:.2f} KB/s, TX: {tx:.2f} KB/s")
                last = current
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
