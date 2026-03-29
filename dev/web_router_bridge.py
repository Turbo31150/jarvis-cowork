#!/usr/bin/env python3
"""web_router_bridge.py — Bridge entre le cluster JARVIS et le Web (ChatGPT, Perplexity).

Permet d'utiliser CometBrowser pour interroger ChatGPT et Perplexity
quand les modeles locaux (M1, M2) manquent de données fraiches.

Usage:
    python dev/web_router_bridge.py --chatgpt "Explique moi le Batch 119"
    python dev/web_router_bridge.py --perplexity "Dernieres news NVIDIA Blackwell"
"""
import argparse
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

# Configuration des URLs
WEB_PROVIDERS = {
    "chatgpt": "https://chatgpt.com/?q=",
    "perplexity": "https://www.perplexity.ai/search?q=",
}


def call_browser_os(provider, prompt):
    """Utilise CometBrowser/Playwright pour injecter le prompt."""
    url = f"{WEB_PROVIDERS[provider]}{urllib.parse.quote(prompt)}"
    print(f"🌐 Ouverture de {provider} via CometBrowser...")

    # Simulation d'appel a Comet (via CLI ou xdg-open pour test)
    # En environnement BrowserOS, on utiliserait le skill 'browser-control'
    try:
        cmd = ["xdg-open", url]
        subprocess.run(cmd, check=True)
        return {"status": "opened", "provider": provider, "url": url}
    except Exception as e:
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="JARVIS Web Router Bridge")
    parser.add_argument("--chatgpt", type=str, help="Interroger ChatGPT")
    parser.add_argument("--perplexity", type=str, help="Interroger Perplexity")
    args = parser.parse_args()

    import urllib.parse

    if args.chatgpt:
        res = call_browser_os("chatgpt", args.chatgpt)
        print(json.dumps(res, indent=2))
    elif args.perplexity:
        res = call_browser_os("perplexity", args.perplexity)
        print(json.dumps(res, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
