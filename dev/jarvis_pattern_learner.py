#!/usr/bin/env python3
"""jarvis_pattern_learner.py — Apprentissage de patterns JARVIS.

Detecte et apprend les habitudes utilisateur.

Usage:
    python dev/jarvis_pattern_learner.py --once
    python dev/jarvis_pattern_learner.py --learn
    python dev/jarvis_pattern_learner.py --patterns
    python dev/jarvis_pattern_learner.py --predict
"""
import argparse
import json
import os
import sqlite3
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

DEV = Path(__file__).parent
DB_PATH = DEV / "data" / "pattern_learner.db"
ETOILE_DB = Path("/home/turbo/data/etoile.db")
ROUTER_DB = DEV / "data" / "router.db"
LEARNER_DB = DEV / "data" / "learner.db"
BASH_HISTORY = Path.home() / ".bash_history"


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(DB_PATH))
    db.execute("""CREATE TABLE IF NOT EXISTS patterns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts REAL, pattern_type TEXT, description TEXT,
        frequency INTEGER, confidence REAL)""")
    db.commit()
    return db


def _parse_ts(raw):
    """Parse a timestamp that may be epoch float or ISO string."""
    if isinstance(raw, (int, float)) and raw > 1000000000:
        return raw
    if isinstance(raw, str):
        try:
            return datetime.fromisoformat(raw).timestamp()
        except Exception:
            pass
    return 0


def collect_history():
    actions = []
    week_ago = time.time() - 604800

    # --- Source 1: etoile.db (uses 'timestamp' col, ISO format) ---
    if ETOILE_DB.exists():
        try:
            db = sqlite3.connect(str(ETOILE_DB))
            for t in [t[0] for t in db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'").fetchall()]:
                cols = [c[1] for c in db.execute(
                    f"PRAGMA table_info([{t}])").fetchall()]
                ts_col = next((c for c in cols if c in ("ts", "timestamp")), None)
                action_col = next(
                    (c for c in cols if c in (
                        "action", "command", "tool", "node", "category")), None)
                if ts_col and action_col:
                    try:
                        for r in db.execute(
                                f"SELECT [{ts_col}], [{action_col}] FROM [{t}] ORDER BY [{ts_col}]").fetchall():
                            if r[1]:
                                ts = _parse_ts(r[0])
                                if ts > week_ago:
                                    hour = datetime.fromtimestamp(ts).hour
                                    weekday = datetime.fromtimestamp(ts).weekday()
                                    actions.append(
                                        {"ts": ts, "action": r[1], "hour": hour, "weekday": weekday,
                                         "source": "etoile"})
                    except Exception:
                        pass
            db.close()
        except Exception:
            pass

    # --- Source 2: router.db (routes table with ts, category, node) ---
    if ROUTER_DB.exists():
        try:
            db = sqlite3.connect(str(ROUTER_DB))
            for r in db.execute(
                    "SELECT ts, category, node FROM routes WHERE ts > ? ORDER BY ts",
                    (week_ago,)).fetchall():
                if r[1]:
                    ts = r[0] if r[0] > 1000000000 else 0
                    if ts > 0:
                        actions.append({
                            "ts": ts, "action": f"{r[1]}@{r[2]}",
                            "hour": datetime.fromtimestamp(ts).hour,
                            "weekday": datetime.fromtimestamp(ts).weekday(),
                            "source": "router"})
            db.close()
        except Exception:
            pass

    # --- Source 3: bash_history (shell commands, no timestamps but gives frequency) ---
    if BASH_HISTORY.exists():
        try:
            lines = BASH_HISTORY.read_text(errors="ignore").strip().split("\n")
            recent = lines[-500:]  # last 500 commands
            now = time.time()
            for i, line in enumerate(recent):
                cmd = line.strip().split()[0] if line.strip() else ""
                if cmd and not cmd.startswith("#"):
                    fake_ts = now - (len(recent) - i) * 60
                    actions.append({
                        "ts": fake_ts, "action": f"shell:{cmd}",
                        "hour": datetime.fromtimestamp(fake_ts).hour,
                        "weekday": datetime.fromtimestamp(fake_ts).weekday(),
                        "source": "bash_history"})
        except Exception:
            pass

    # --- Source 4: scan all dev/data/*.db for tables with ts + action cols ---
    data_dir = DEV / "data"
    if data_dir.exists():
        for db_file in data_dir.glob("*.db"):
            if db_file.name in ("pattern_learner.db", "router.db"):
                continue
            try:
                db = sqlite3.connect(str(db_file))
                for t in [t[0] for t in db.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'").fetchall()]:
                    cols = [c[1] for c in db.execute(
                        f"PRAGMA table_info([{t}])").fetchall()]
                    ts_col = next((c for c in cols if c in ("ts", "timestamp")), None)
                    action_col = next(
                        (c for c in cols if c in (
                            "action", "command", "tool", "node", "event")), None)
                    if ts_col and action_col:
                        try:
                            for r in db.execute(
                                    f"SELECT [{ts_col}], [{action_col}] FROM [{t}] ORDER BY [{ts_col}]").fetchall():
                                if r[1]:
                                    ts = _parse_ts(r[0])
                                    if ts > week_ago:
                                        actions.append({
                                            "ts": ts, "action": r[1],
                                            "hour": datetime.fromtimestamp(ts).hour,
                                            "weekday": datetime.fromtimestamp(ts).weekday(),
                                            "source": db_file.stem})
                        except Exception:
                            pass
                db.close()
            except Exception:
                pass

    return actions


def detect_patterns(actions):
    patterns = []
    if not actions:
        return patterns

    # Hourly patterns
    by_hour = defaultdict(Counter)
    for a in actions:
        by_hour[a["hour"]][a["action"]] += 1

    for hour, counter in sorted(by_hour.items()):
        top = counter.most_common(3)
        for action, count in top:
            if count >= 3:
                patterns.append({
                    "type": "hourly",
                    "description": f"At {hour:02d}h, '{action}' done {count}x this week",
                    "hour": hour,
                    "action": action,
                    "frequency": count,
                    "confidence": min(count / 7, 0.95),
                })

    # Day-of-week patterns
    by_day = defaultdict(Counter)
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for a in actions:
        by_day[a["weekday"]][a["action"]] += 1

    for day, counter in sorted(by_day.items()):
        top = counter.most_common(2)
        for action, count in top:
            if count >= 3:
                patterns.append({
                    "type": "weekly",
                    "description": f"On {days[day]}, '{action}' done {count}x",
                    "day": days[day],
                    "action": action,
                    "frequency": count,
                    "confidence": min(count / 4, 0.9),
                })

    # Sequence patterns (A -> B)
    sorted_actions = sorted(actions, key=lambda x: x["ts"])
    sequences = Counter()
    for i in range(len(sorted_actions) - 1):
        a, b = sorted_actions[i]["action"], sorted_actions[i + 1]["action"]
        if a != b:
            sequences[(a, b)] += 1

    for (a, b), count in sequences.most_common(5):
        if count >= 3:
            patterns.append({
                "type": "sequence",
                "description": f"'{a}' often followed by '{b}' ({count}x)",
                "from": a, "to": b,
                "frequency": count,
                "confidence": min(count / 5, 0.85),
            })

    return patterns


def do_learn():
    db = init_db()
    actions = collect_history()
    patterns = detect_patterns(actions)

    for p in patterns:
        db.execute(
            "INSERT INTO patterns (ts, pattern_type, description, frequency, confidence) VALUES (?,?,?,?,?)",
            (time.time(),
             p["type"],
                p["description"],
                p["frequency"],
                p["confidence"]))
    db.commit()
    db.close()

    return {
        "ts": datetime.now().isoformat(),
        "actions_analyzed": len(actions),
        "patterns_found": len(patterns),
        "by_type": {
            "hourly": sum(
                1 for p in patterns if p["type"] == "hourly"),
            "weekly": sum(
                1 for p in patterns if p["type"] == "weekly"),
            "sequence": sum(
                1 for p in patterns if p["type"] == "sequence"),
        },
        "top_patterns": sorted(
            patterns,
            key=lambda x: x["confidence"],
            reverse=True)[
            :10],
    }


def do_show_patterns():
    """Show stored patterns from DB."""
    db = init_db()
    rows = db.execute(
        "SELECT pattern_type, description, frequency, confidence FROM patterns ORDER BY confidence DESC LIMIT 30"
    ).fetchall()
    db.close()
    if not rows:
        return {"message": "No patterns stored yet. Run --learn first.", "patterns": []}
    patterns = []
    for r in rows:
        patterns.append({
            "type": r[0], "description": r[1],
            "frequency": r[2], "confidence": round(r[3], 3)
        })
    return {"total_stored": len(rows), "patterns": patterns}


def do_predict():
    """Predict next likely actions based on current hour/day."""
    now = datetime.now()
    hour = now.hour
    weekday = now.weekday()
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    db = init_db()
    # Find patterns matching current hour
    hourly = db.execute(
        "SELECT description, confidence FROM patterns WHERE pattern_type='hourly' AND description LIKE ? ORDER BY confidence DESC LIMIT 5",
        (f"At {hour:02d}h%",)
    ).fetchall()
    # Find patterns matching current day
    weekly = db.execute(
        "SELECT description, confidence FROM patterns WHERE pattern_type='weekly' AND description LIKE ? ORDER BY confidence DESC LIMIT 5",
        (f"On {days[weekday]}%",)
    ).fetchall()
    # Find sequence patterns (top)
    sequences = db.execute(
        "SELECT description, confidence FROM patterns WHERE pattern_type='sequence' ORDER BY confidence DESC LIMIT 5"
    ).fetchall()
    db.close()

    predictions = []
    for desc, conf in hourly:
        predictions.append({"basis": "hourly", "prediction": desc, "confidence": round(conf, 3)})
    for desc, conf in weekly:
        predictions.append({"basis": "weekly", "prediction": desc, "confidence": round(conf, 3)})
    for desc, conf in sequences:
        predictions.append({"basis": "sequence", "prediction": desc, "confidence": round(conf, 3)})

    return {
        "current_time": now.strftime("%Y-%m-%d %H:%M"),
        "current_hour": hour,
        "current_day": days[weekday],
        "predictions": predictions if predictions else [{"message": "No predictions yet. Run --learn first."}]
    }


def main():
    parser = argparse.ArgumentParser(description="JARVIS Pattern Learner")
    parser.add_argument("--once", "--learn", action="store_true", dest="learn", help="Learn patterns")
    parser.add_argument("--patterns", action="store_true", help="Show patterns")
    parser.add_argument("--predict", action="store_true", help="Predict next")
    parser.add_argument("--report", action="store_true", help="Report")
    args = parser.parse_args()

    if args.patterns:
        print(json.dumps(do_show_patterns(), ensure_ascii=False, indent=2))
    elif args.predict:
        print(json.dumps(do_predict(), ensure_ascii=False, indent=2))
    else:
        print(json.dumps(do_learn(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
