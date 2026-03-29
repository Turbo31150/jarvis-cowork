#!/usr/bin/env python3
"""win_accessibility_helper.py — Accessibility assistant (#269).

Usage:
    python dev/win_accessibility_helper.py --say "TEXT"
    python dev/win_accessibility_helper.py --high-contrast on|off
"""
import argparse
import subprocess
import sys

def say(text):
    """Speaks text using spd-say."""
    try:
        subprocess.run(['spd-say', text], check=True)
        return True
    except Exception:
        # Fallback to espeak
        try:
            subprocess.run(['espeak', text], check=True)
            return True
        except Exception as e:
            print(f"TTS Error: {e}", file=sys.stderr)
            return False

def set_high_contrast(state):
    """Toggles high contrast theme via gsettings (Gnome)."""
    theme = "HighContrast" if state == "on" else "Yaru" # Default Ubuntu theme
    try:
        # Enable accessibility features
        subprocess.run(['gsettings', 'set', 'org.gnome.desktop.interface', 'toolkit-accessibility', 'true' if state == 'on' else 'false'])
        # Change theme
        subprocess.run(['gsettings', 'set', 'org.gnome.desktop.interface', 'gtk-theme', theme])
        return True
    except Exception as e:
        print(f"Gsettings Error: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="JARVIS Accessibility Helper (Linux Native)")
    parser.add_argument("--say", type=str, help="Speak text")
    parser.add_argument("--high-contrast", type=str, choices=["on", "off"], help="Toggle high contrast")
    args = parser.parse_args()

    if args.say:
        say(args.say)
    elif args.high_contrast:
        set_high_contrast(args.high_contrast)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
