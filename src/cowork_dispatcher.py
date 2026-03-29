#!/usr/bin/env python3
"""COWORK Dispatcher — Route tasks to cowork scripts via pattern matching.
Integrates with etoile.db pattern agents and executes scripts from dev/.
"""

import subprocess
import sys
import os
import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.unified import UnifiedMemoryStore

BASE = Path(__file__).resolve().parent
DB = UnifiedMemoryStore()
DB_PATH = str(DB.resolve("etoile").path)
DEV_PATH = BASE / "dev"
PYTHON = sys.executable


def get_cowork_patterns(db_path=DB_PATH):
    """Load all normalized COWORK patterns from the unified memory facade."""
    return DB.get_cowork_patterns()


def get_scripts_for_pattern(pattern_id, db_path=DB_PATH):
    """Get scripts mapped to a pattern via the unified memory facade."""
    return DB.get_scripts_for_pattern(pattern_id)


def match_pattern(query, patterns):
    """Match a query to the best COWORK pattern using keyword scoring."""
    query_lower = query.lower()
    query_words = set(re.findall(r'\w+', query_lower))
    scores = []

    for pat in patterns:
        keywords = set((pat.get('keywords') or '').split(','))
        # Score: keyword overlap + description match
        keyword_score = len(query_words & keywords)
        desc_words = set(re.findall(r'\w+', (pat.get('description') or '').lower()))
        desc_score = len(query_words & desc_words) * 0.5
        # Priority bonus:
        # - legacy patterns used 1..5
        # - current DB-backed patterns often use 0..100
        priority = int(pat.get('priority') or 50)
        if priority <= 10:
            priority_bonus = max(0, 10 - priority) * 0.1
        else:
            priority_bonus = max(0, 100 - priority) / 100
        total = keyword_score + desc_score + priority_bonus
        if total > 0:
            scores.append((total, pat))

    scores.sort(key=lambda x: -x[0])
    return scores


def execute_script(script_name, args=None, timeout=60):
    """Execute a cowork script and return output."""
    normalized = DB.normalize_script_name(script_name)
    script_path = DEV_PATH / f"{normalized}.py"
    if not script_path.exists():
        return {"error": f"Script not found: {script_path}"}

    cmd = [PYTHON, script_path]
    if args:
        cmd.extend(args)
    else:
        cmd.append("--once")

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, cwd=DEV_PATH
        )
        return {
            "script": normalized,
            "returncode": result.returncode,
            "stdout": result.stdout[-2000:] if result.stdout else "",
            "stderr": result.stderr[-500:] if result.stderr else "",
            "success": result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {"script": normalized, "error": "timeout", "success": False}
    except Exception as e:
        return {"script": normalized, "error": str(e), "success": False}


def dispatch(query, execute=False, top_n=3):
    """Dispatch a query: find matching patterns and optionally execute scripts."""
    patterns = get_cowork_patterns()
    matches = match_pattern(query, patterns)

    result = {
        "query": query,
        "matches": [],
        "timestamp": datetime.now().isoformat()
    }

    for score, pat in matches[:top_n]:
        scripts = get_scripts_for_pattern(pat['pattern_id'])
        match_entry = {
            "pattern_id": pat['pattern_id'],
            "agent_id": pat['agent_id'],
            "description": pat['description'],
            "score": round(score, 2),
            "scripts": [s['script_name'] for s in scripts],
            "script_count": len(scripts)
        }

        if execute and scripts:
            # Execute first matching script
            exec_result = execute_script(scripts[0]['script_name'])
            match_entry["execution"] = exec_result

        result["matches"].append(match_entry)

    return result


def list_all():
    """List all patterns and their scripts."""
    patterns = get_cowork_patterns()
    total_scripts = 0
    for pat in patterns:
        scripts = get_scripts_for_pattern(pat['pattern_id'])
        total_scripts += len(scripts)
        print(f"\n{pat['pattern_id']} ({pat['agent_id']})")
        print(f"  {pat['description']}")
        print(f"  Strategy: {pat['strategy']} | Priority: {pat['priority']}")
        print(f"  Scripts ({len(scripts)}): {', '.join(s['script_name'] for s in scripts[:5])}"
              + (f" +{len(scripts)-5} more" if len(scripts) > 5 else ""))

    print(f"\n--- Total: {len(patterns)} patterns, {total_scripts} scripts ---")


def health_check():
    """Check which scripts actually exist and are parseable."""
    with DB.connect("etoile") as db:
        cols = DB.table_columns(db, "cowork_script_mapping")
        script_col = "script_name" if "script_name" in cols else "script"
        rows = db.execute(f"SELECT {script_col} AS script_name FROM cowork_script_mapping").fetchall()

    ok = 0
    missing = 0
    errors = []

    for r in rows:
        script_name = DB.normalize_script_name(r[0])
        script_path = DEV_PATH / f"{script_name}.py"
        if script_path.exists():
            try:
                with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
                    compile(f.read(), script_path, 'exec')
                ok += 1
            except SyntaxError as e:
                errors.append({"script": script_name, "error": str(e)})
        else:
            missing += 1

    result = {
        "total": len(rows),
        "ok": ok,
        "missing": missing,
        "syntax_errors": len(errors),
        "errors": errors[:10]
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


# === CONFIGURATION JARVIS OS v12.4 COLOR ROUTING ===
def get_color_for_task(task_type: str) -> str:
    """Map task type to UI color queue."""
    if any(k in task_type.lower() for k in ["content", "video", "image", "gen", "dominance", "interaction"]):
        return "yellow"
    if any(k in task_type.lower() for k in ["social", "post", "linkedin", "twitter"]):
        return "red"
    if any(k in task_type.lower() for k in ["trade", "crypto", "stock", "price"]):
        return "blue"
    if any(k in task_type.lower() for k in ["email", "mail", "smtp", "imap", "bidding", "project"]):
        return "green"
    return "white"

def process_inbox():
    """Scan inbox for new missions, execute them, and move to outbox."""
    import time
    inbox_path = BASE / "inbox"
    outbox_path = BASE / "outbox"
    inbox_path.mkdir(exist_ok=True)
    outbox_path.mkdir(exist_ok=True)

    files = [f for f in os.listdir(inbox_path) if f.endswith('.json')]
    if not files: return 0

    processed_count = 0
    for filename in files:
        file_path = inbox_path / filename
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                mission = json.load(f)
            
            mission_id = mission.get("mission_id", filename)
            task_type = mission.get("classification", mission.get("type", "unknown"))
            query = f"{task_type} {mission.get('contexte', {}).get('analysis_goal', '')}"
            
            color = get_color_for_task(task_type)
            print(f"🌈 [JARVIS v12.4] Mission {mission_id} ({task_type}) -> QUEUE: {color.upper()}")
            
            result = dispatch(query, execute=True, top_n=1)
            result["mission_source"] = mission
            result["ui_color"] = color
            
            output_filename = f"result_{mission_id}_{int(time.time())}.json"
            with open(outbox_path / output_filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            os.remove(file_path)
            processed_count += 1
            print(f"✅ Mission {mission_id} processed. Result: {output_filename}")
        except Exception as e:
            print(f"❌ Error processing mission {filename}: {e}")
    return processed_count

def daemon_loop(interval=60):
    """Keep dispatcher alive, process inbox, and emit periodic health snapshots."""
    import time
    print(json.dumps({
        "status": "daemon_started",
        "patterns_db": DB_PATH,
        "mapping_db": DB_PATH,
        "interval": interval,
        "timestamp": datetime.now().isoformat(),
    }, ensure_ascii=False))
    
    while True:
        try:
            processed = process_inbox()
            if processed > 0:
                print(f"📊 [DAEMON] {processed} missions processed in this cycle.")
            if int(time.time()) % (interval * 5) < interval:
                health_check()
        except Exception as e:
            print(json.dumps({
                "status": "daemon_error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }, ensure_ascii=False))
        time.sleep(max(1, interval))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="COWORK Dispatcher")
    parser.add_argument("--dispatch", type=str, help="Query to dispatch")
    parser.add_argument("--execute", action="store_true", help="Execute matched scripts")
    parser.add_argument("--list", action="store_true", help="List all patterns")
    parser.add_argument("--health", action="store_true", help="Health check scripts")
    parser.add_argument("--once", action="store_true", help="Alias for --health")
    parser.add_argument("--daemon", action="store_true", help="Run in continuous inbox scanning mode")
    parser.add_argument("--interval", type=int, default=60, help="Scan interval in seconds")
    args = parser.parse_args()

    if args.dispatch:
        result = dispatch(args.dispatch, execute=args.execute)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.list:
        list_all()
    elif args.daemon:
        daemon_loop(interval=args.interval)
    elif args.health or args.once:
        health_check()
    else:
        parser.print_help()
