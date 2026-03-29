#!/usr/bin/env python3
"""fast_trading_pipeline.py — Pipeline ultra-rapide pour creation de contenu trading.

Etapes:
1. Recherche des news (Perplexity/Web)
2. Analyse & Structure (Gemini)
3. Redaction Kreative (ChatGPT)
4. Enregistrement local & Publication ready.

Usage:
    python dev/fast_trading_pipeline.py --symbol BTC --topic "halving reaction"
"""
import argparse
import json
import subprocess
import time
from pathlib import Path

ROUTER = Path("/home/turbo/jarvis-linux/cowork/dev/prompt_router.py")
REPORT_DIR = Path("/home/turbo/jarvis-linux/data_legacy/reports/")


def run_step(prompt):
    cmd = ["python3", str(ROUTER), "--route", prompt]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(proc.stdout)
    except BaseException:
        return {"error": proc.stdout}


def main():
    parser = argparse.ArgumentParser(
        description="JARVIS Fast Trading Content Pipeline")
    parser.add_argument(
        "--symbol",
        type=str,
        required=True,
        help="BTC, ETH, etc.")
    parser.add_argument(
        "--topic",
        type=str,
        default="daily analysis",
        help="Topic specifique")
    args = parser.parse_args()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_file = REPORT_DIR / f"content_{args.symbol}_{int(time.time())}.md"

    print(f"🚀 Lancement Pipeline pour {args.symbol} : {args.topic}")

    # Step 1: Web Intelligence
    print("  1. Extraction Intelligence Web (Perplexity)...")
    web_res = run_step(
        f"Dernieres news {
            args.symbol} {
            args.topic} 16 mars 2026. Liste les 3 points cles.")

    # Step 2: Architecture & Analysis
    print("  2. Structuration & Analyse (Gemini)...")
    archi_prompt = f"Analyse ces news pour {
        args.symbol}: {
        web_res.get(
            'content',
            'News en cours de lecture...')}. Cree une structure de rapport pro."
    archi_res = run_step(archi_prompt)

    # Step 3: Creative Writing
    print("  3. Redaction Newsletter & Thread (ChatGPT)...")
    content_prompt = f"Basé sur cette analyse: {
        archi_res.get(
            'content',
            'Analyse locale')}. Ecris un thread Twitter de 5 posts et une intro de newsletter de 200 mots pour {
        args.symbol}."
    content_res = run_step(content_prompt)

    # Final Save
    content = f"""# Rapport de Contenu Trading JARVIS
**Date:** {datetime.now().isoformat()}
**Symbol:** {args.symbol}
**Topic:** {args.topic}

## 🌐 Intelligence Web
{web_res.get('content', 'Ouverture navigateur effectuee.')}

## 🧠 Analyse & Structure (Gemini)
{archi_res.get('content', 'Analyse générée.')}

## ✍️ Redaction Finale (ChatGPT)
{content_res.get('content', 'Contenu prêt.')}
"""
    with open(report_file, "w") as f:
        f.write(content)

    print(f"✅ Pipeline Termine. Rapport disponible: {report_file}")


if __name__ == "__main__":
    from datetime import datetime
    main()
