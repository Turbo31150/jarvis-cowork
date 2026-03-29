#!/usr/bin/env python3
"""trading_live_notifier.py — Watchdog Sniper avec Alertes Sonores et Telegram.

Surveille sniper_scan.db et declenche une alerte sonore + message TG
pour chaque nouveau signal detecte.
"""
import sqlite3
import time
import subprocess
import urllib.request
import urllib.parse
import json
import os
from datetime import datetime
from pathlib import Path
import argparse

# --- CONFIGURATION ---
DB_PATH = Path("/home/turbo/jarvis-linux/core/memory/sniper_scan.db")
TELEGRAM_TOKEN = "8369376863:AAF-7YGDbun8mXWwqYJFj-eX6P78DeIu9Aw"
TELEGRAM_CHAT = "2010747443"
# Son systeme par defaut
SOUND_FILE = "/usr/share/sounds/freedesktop/stereo/complete.oga"


def send_telegram(message):
    """Envoie une alerte Telegram."""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = urllib.parse.urlencode(
            {"chat_id": TELEGRAM_CHAT, "text": message, "parse_mode": "HTML"}).encode()
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return True
    except Exception as e:
        print(f"❌ Erreur Telegram: {e}")
        return False


def play_alert():
    """Declenche l'alerte sonore systeme."""
    try:
        # Tente paplay (PulseAudio) ou aplay (ALSA)
        subprocess.run(["paplay", SOUND_FILE], check=False)
    except BaseException:
        try:
            subprocess.run(["aplay", SOUND_FILE], check=False)
        except BaseException:
            print("⚠️ Impossible de jouer le son.")


def monitor_signals():
    """Boucle de surveillance de la base de donnees."""
    print(f"🕵️‍♂️ Surveillance Sniper active sur {DB_PATH}")
    print(f"🔔 Alertes: Telegram (OK) | Sonore (OK)")

    # Recuperer le dernier ID connu pour ne pas spammer au demarrage
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(id) FROM signal_tracker")
        last_id = cursor.fetchone()[0] or 0
        conn.close()
    except BaseException:
        last_id = 0

    while True:
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Chercher les nouveaux signaux
            cursor.execute(
                "SELECT * FROM signal_tracker WHERE id > ? ORDER BY id ASC", (last_id,))
            rows = cursor.fetchall()

            for row in rows:
                last_id = row['id']
                msg = (
                    f"🎯 <b>NOUVEAU SIGNAL SNIPER</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"💎 <b>Asset:</b> {row['symbol']}\n"
                    f"📈 <b>Direction:</b> {row['direction']}\n"
                    f"💰 <b>Prix Entrée:</b> {row['entry_price']}\n"
                    f"🚀 <b>TP1:</b> {row['tp1']}\n"
                    f"🛑 <b>SL:</b> {row['sl']}\n"
                    f"⭐ <b>Score:</b> {row['score']}/10\n"
                    f"⏰ <b>Heure:</b> {row['emitted_at']}"
                )

                print(f"🚀 Signal detecte: {row['symbol']} {row['direction']}")

                # Notifications
                send_telegram(msg)
                play_alert()

            conn.close()
        except Exception as e:
            print(f"❌ Erreur boucle: {e}")

        time.sleep(2)  # Scan toutes les 2 secondes


if __name__ == "__main__":
    # Test au demarrage
    send_telegram(
        "🔄 <b>Bot Trading JARVIS Activé</b>\nSystème d'alertes sonore et Telegram opérationnel.")
    monitor_signals()
