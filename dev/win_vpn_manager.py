#!/usr/bin/env python3
"""win_vpn_manager.py — VPN Manager with nmcli (#278).

Manages VPN connections (OpenVPN, Wireguard) via NetworkManager.

Usage (Linux-Native):
    python dev/win_vpn_manager.py --list
    python dev/win_vpn_manager.py --up "VPN_NAME"
    python dev/win_vpn_manager.py --down "VPN_NAME"
    python dev/win_vpn_manager.py --status
"""
import argparse
import json
import subprocess
import sys


def list_vpns():
    """Lists all configured VPN connections."""
    try:
        output = subprocess.check_output(
            ['nmcli', '-t', '-f', 'NAME,TYPE', 'connection', 'show'], text=True)
        vpns = []
        for line in output.strip().split('\n'):
            name, conn_type = line.split(':')
            if 'vpn' in conn_type.lower() or 'wireguard' in conn_type.lower():
                vpns.append({"name": name, "type": conn_type})
        return vpns
    except Exception as e:
        return {"error": str(e)}


def vpn_action(name, action):
    """Brings VPN connection up or down."""
    cmd = ['nmcli', 'connection', action, name]
    try:
        subprocess.run(cmd, check=True)
        return True
    except Exception as e:
        print(f"VPN {action} Error: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="JARVIS VPN Manager (Linux Native)")
    parser.add_argument(
        "--list",
        action="store_true",
        help="List configured VPNs")
    parser.add_argument("--up", type=str, help="Bring VPN connection UP")
    parser.add_argument("--down", type=str, help="Bring VPN connection DOWN")
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show active VPN status")
    args = parser.parse_args()

    result = {"status": "success", "data": {}}

    if args.list:
        result["data"]["vpns"] = list_vpns()
    elif args.up:
        if vpn_action(args.up, "up"):
            result["data"]["message"] = f"VPN {args.up} is UP"
    elif args.down:
        if vpn_action(args.down, "down"):
            result["data"]["message"] = f"VPN {args.down} is DOWN"
    elif args.status:
        try:
            output = subprocess.check_output(
                ['nmcli', '-t', '-f', 'NAME,TYPE,STATE', 'connection', 'show', '--active'], text=True)
            result["data"]["active"] = [
                line.split(':') for line in output.strip().split('\n') if 'vpn' in line.lower()]
        except BaseException:
            result["data"]["active"] = []
    else:
        parser.print_help()
        return

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
