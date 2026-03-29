#!/usr/bin/env python3
"""win_screen_reader.py — Screen reader and visual analyzer (#267).

Usage:
    python dev/win_screen_reader.py --once
    python dev/win_screen_reader.py --ocr
    python dev/win_screen_reader.py --analyze
"""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Paths
TEMP_SCREEN = "/tmp/jarvis_screen.png"
TEMP_OCR = "/tmp/jarvis_ocr"


def capture():
    """Captures the screen using scrot."""
    try:
        subprocess.run(['scrot', '-o', TEMP_SCREEN],
                       check=True, capture_output=True)
        return True
    except Exception as e:
        print(f"Error capturing screen: {e}", file=sys.stderr)
        return False


def ocr():
    """Performs OCR using tesseract."""
    try:
        subprocess.run(['tesseract', TEMP_SCREEN, TEMP_OCR, '-l',
                       'fra+eng'], check=True, capture_output=True)
        with open(f"{TEMP_OCR}.txt", 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        return f"OCR Error: {e}"


def main():
    parser = argparse.ArgumentParser(
        description="JARVIS Screen Reader (Linux Native)")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Execute once (capture + OCR)")
    parser.add_argument(
        "--ocr",
        action="store_true",
        help="Perform only OCR on last capture")
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Visual analysis using Cluster M1 (placeholder)")
    args = parser.parse_args()

    result = {
        "timestamp": datetime.now().isoformat(),
        "status": "error",
        "data": {}
    }

    if args.once:
        if capture():
            text = ocr()
            result["status"] = "success"
            result["data"] = {"text": text, "path": TEMP_SCREEN}

    elif args.ocr:
        if os.path.exists(TEMP_SCREEN):
            text = ocr()
            result["status"] = "success"
            result["data"] = {"text": text}
        else:
            result["data"] = {
                "error": "No screen capture found. Run with --once first."}

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
