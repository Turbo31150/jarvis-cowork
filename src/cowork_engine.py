#!/usr/bin/env python3
"""COWORK Engine — Continuous development, testing, anticipation, and self-improvement.

Integrates cowork scripts with JARVIS pattern agents for autonomous operation.
Runs multi-test cycles, identifies gaps, predicts needs, and generates improvements.

Usage:
    python cowork/cowork_engine.py --test-all       # Test all 329 scripts
    python cowork/cowork_engine.py --gaps            # Identify coverage gaps
    python cowork/cowork_engine.py --anticipate      # Predict next needs
    python cowork/cowork_engine.py --improve         # Auto-improve weak scripts
    python cowork/cowork_engine.py --cycle           # Full continuous cycle
    python cowork/cowork_engine.py --openclaw-sync   # Sync to OpenClaw workspace
"""

import sqlite3
import subprocess
import sys
import os
import json
import ast
import re
import time
from datetime import datetime
from collections import defaultdict, Counter
from pathlib import Path
from path_resolver import resolve_db_with_table, resolve_openclaw_dev_dir, resolve_project_root

BASE = Path(__file__).parent

# ── TELEGRAM ALERTING ─────────────────────────────────────────────────

def send_telegram_alert(message):
    """Send a Telegram alert via Bot API. Silently fails if not configured."""
    import urllib.request
    import urllib.parse
    token = os.environ.get("TELEGRAM_TOKEN", "")
    chat = os.environ.get("TELEGRAM_CHAT", "")
    if not token or not chat:
        env_file = Path("/home/turbo/jarvis-linux/.env")
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("TELEGRAM_TOKEN=") and not token:
                    token = line.split("=", 1)[1].strip()
                elif line.startswith("TELEGRAM_CHAT=") and not chat:
                    chat = line.split("=", 1)[1].strip()
    if not token or not chat:
        print("[telegram] No TELEGRAM_TOKEN/TELEGRAM_CHAT configured, skipping alert", file=sys.stderr)
        return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = urllib.parse.urlencode({
            "chat_id": chat,
            "text": message,
            "parse_mode": "HTML",
        }).encode()
        req = urllib.request.Request(url, data=data, method="POST")
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        print(f"[telegram] Alert failed: {e}", file=sys.stderr)
TURBO = resolve_project_root()
DB_PATH = resolve_db_with_table("etoile.db", "cowork_script_mapping")
DEV_PATH = BASE / "dev"
OPENCLAW_DEV = resolve_openclaw_dev_dir()
PYTHON = sys.executable


def _auto_migrate_db():
    """Auto-migrate cowork tables: add missing columns and tables for v12.6 compat."""
    db = sqlite3.connect(str(DB_PATH))
    # -- cowork_script_mapping: ensure pattern_id, script_name, status columns exist
    cols = {r[1] for r in db.execute("PRAGMA table_info(cowork_script_mapping)").fetchall()}
    if "pattern_id" not in cols and "pattern" in cols:
        db.execute("ALTER TABLE cowork_script_mapping ADD COLUMN pattern_id TEXT DEFAULT ''")
        db.execute("UPDATE cowork_script_mapping SET pattern_id = pattern WHERE pattern_id = ''")
        db.commit()
    elif "pattern_id" not in cols:
        db.execute("ALTER TABLE cowork_script_mapping ADD COLUMN pattern_id TEXT DEFAULT ''")
        db.commit()
    if "script_name" not in cols and "script" in cols:
        db.execute("ALTER TABLE cowork_script_mapping ADD COLUMN script_name TEXT DEFAULT ''")
        db.execute("UPDATE cowork_script_mapping SET script_name = script WHERE script_name = ''")
        db.commit()
    elif "script_name" not in cols:
        db.execute("ALTER TABLE cowork_script_mapping ADD COLUMN script_name TEXT DEFAULT ''")
        db.commit()
    if "status" not in cols:
        db.execute("ALTER TABLE cowork_script_mapping ADD COLUMN status TEXT DEFAULT 'active'")
        db.commit()
    if "total_calls" not in cols:
        db.execute("ALTER TABLE cowork_script_mapping ADD COLUMN total_calls INTEGER DEFAULT 0")
        db.commit()
    # -- agent_patterns table: create if missing
    tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    if "agent_patterns" not in tables:
        db.execute("""
            CREATE TABLE agent_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id TEXT NOT NULL,
                agent_id TEXT DEFAULT '',
                keywords TEXT DEFAULT '',
                description TEXT DEFAULT '',
                strategy TEXT DEFAULT 'round_robin',
                priority INTEGER DEFAULT 50,
                total_calls INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.commit()
    else:
        ap_cols = {r[1] for r in db.execute("PRAGMA table_info(agent_patterns)").fetchall()}
        if "total_calls" not in ap_cols:
            db.execute("ALTER TABLE agent_patterns ADD COLUMN total_calls INTEGER DEFAULT 0")
            db.commit()
    db.close()


# Run migration on import
try:
    _auto_migrate_db()
except Exception as _mig_err:
    print(f"[cowork_engine] Migration warning: {_mig_err}", file=sys.stderr)


# ── MULTI-TEST ENGINE ──────────────────────────────────────────────────

def test_script(script_name, timeout=30):
    """Test a single script: parse + --help + --once (if safe)."""
    script_path = DEV_PATH / f"{script_name}.py"
    if not script_path.exists():
        return {"script": script_name, "status": "missing", "errors": []}

    results = {"script": script_name, "errors": [], "warnings": [], "metrics": {}}

    # 1. Syntax check
    try:
        with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
            source = f.read()
        compile(source, str(script_path), 'exec')
        results["syntax"] = "OK"
    except SyntaxError as e:
        results["syntax"] = "FAIL"
        results["errors"].append(f"SyntaxError: {e}")
        results["status"] = "syntax_error"
        return results

    # 2. AST analysis — functions, classes, imports, docstring
    try:
        tree = ast.parse(source)
        results["metrics"]["functions"] = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
        results["metrics"]["classes"] = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
        results["metrics"]["lines"] = len(source.splitlines())
        results["metrics"]["has_docstring"] = ast.get_docstring(tree) is not None
        results["metrics"]["has_main"] = 'if __name__' in source
        results["metrics"]["has_argparse"] = 'argparse' in source
        results["metrics"]["imports"] = len([n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))])

        # Check for non-stdlib imports
        stdlib_safe = {'os', 'sys', 'json', 'sqlite3', 'subprocess', 'argparse', 'pathlib',
                       'datetime', 'time', 're', 'hashlib', 'shutil', 'tempfile', 'threading',
                       'http', 'urllib', 'socket', 'math', 'random', 'collections', 'functools',
                       'itertools', 'textwrap', 'csv', 'io', 'logging', 'ast', 'inspect',
                       'platform', 'ctypes', 'struct', 'uuid', 'base64', 'hmac', 'email',
                       'imaplib', 'smtplib', 'html', 'xml', 'configparser', 'getpass',
                       'glob', 'fnmatch', 'stat', 'signal', 'queue', 'concurrent',
                       'multiprocessing', 'traceback', 'string', 'operator', 'copy',
                       'pprint', 'enum', 'dataclasses', 'typing', 'abc', 'contextlib',
                       'weakref', 'gc', 'resource', 'winreg', 'msvcrt', 'winsound',
                       'mimetypes', 'webbrowser', 'http.server', 'http.client',
                       'urllib.request', 'urllib.parse', 'email.header', 'email.mime',
                       'email.mime.text', 'email.mime.multipart', 'email.mime.base'}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split('.')[0]
                    if root not in stdlib_safe:
                        results["warnings"].append(f"Non-stdlib import: {alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                root = node.module.split('.')[0]
                if root not in stdlib_safe:
                    results["warnings"].append(f"Non-stdlib import: {node.module}")

    except Exception as e:
        results["warnings"].append(f"AST analysis error: {e}")

    # 3. --help test (should not crash)
    if results["metrics"].get("has_argparse"):
        try:
            r = subprocess.run(
                [PYTHON, str(script_path), "--help"],
                capture_output=True, text=True, timeout=10, cwd=str(DEV_PATH)
            )
            results["help"] = "OK" if r.returncode == 0 else "FAIL"
            if r.returncode != 0:
                results["warnings"].append(f"--help exit code: {r.returncode}")
        except subprocess.TimeoutExpired:
            results["help"] = "TIMEOUT"
            results["warnings"].append("--help timed out")
        except Exception as e:
            results["help"] = "ERROR"
            results["warnings"].append(f"--help error: {e}")

    results["status"] = "OK" if not results["errors"] else "FAIL"
    return results


def test_all():
    """Run multi-test on all 329+ scripts."""
    scripts = sorted([f.stem for f in DEV_PATH.glob("*.py")])
    results = []
    stats = Counter()

    print(f"Testing {len(scripts)} scripts...\n")
    start = time.time()

    for i, name in enumerate(scripts):
        r = test_script(name)
        results.append(r)
        stats[r["status"]] += 1
        if r["errors"]:
            print(f"  FAIL: {name} — {r['errors'][0]}")
        elif r["warnings"]:
            print(f"  WARN: {name} — {len(r['warnings'])} warnings")

    elapsed = time.time() - start
    summary = {
        "total": len(scripts),
        "ok": stats["OK"],
        "fail": stats.get("FAIL", 0) + stats.get("syntax_error", 0),
        "missing": stats.get("missing", 0),
        "warnings_total": sum(len(r["warnings"]) for r in results),
        "avg_lines": sum(r.get("metrics", {}).get("lines", 0) for r in results) // max(1, len(results)),
        "avg_functions": sum(r.get("metrics", {}).get("functions", 0) for r in results) // max(1, len(results)),
        "with_docstring": sum(1 for r in results if r.get("metrics", {}).get("has_docstring")),
        "with_argparse": sum(1 for r in results if r.get("metrics", {}).get("has_argparse")),
        "with_main": sum(1 for r in results if r.get("metrics", {}).get("has_main")),
        "non_stdlib": [w for r in results for w in r["warnings"] if "Non-stdlib" in w],
        "elapsed_s": round(elapsed, 1),
        "timestamp": datetime.now().isoformat()
    }

    print(f"\n{'='*60}")
    print(f"Results: {summary['ok']}/{summary['total']} OK | "
          f"{summary['fail']} FAIL | {summary['warnings_total']} warnings")
    print(f"Coverage: {summary['with_docstring']} docstrings | "
          f"{summary['with_argparse']} argparse | {summary['with_main']} __main__")
    print(f"Avg: {summary['avg_lines']} lines/script | {summary['avg_functions']} functions/script")
    print(f"Time: {summary['elapsed_s']}s")

    # Save report
    report_path = TURBO / "data" / f"cowork_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump({"summary": summary, "results": results}, f, indent=2, ensure_ascii=False)
    print(f"Report: {report_path}")

    return summary, results


# ── GAP ANALYSIS ───────────────────────────────────────────────────────

def analyze_gaps():
    """Identify coverage gaps: patterns without enough scripts, weak areas."""
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row

    # 1. Patterns with few scripts
    mapping = db.execute("""
        SELECT pattern_id, COUNT(*) as cnt
        FROM cowork_script_mapping
        GROUP BY pattern_id
        ORDER BY cnt ASC
    """).fetchall()

    # 2. Patterns never dispatched
    unused = db.execute("""
        SELECT pattern_id, agent_id, description
        FROM agent_patterns
        WHERE pattern_id LIKE 'PAT_CW_%' AND total_calls = 0
    """).fetchall()

    # 3. Scripts without pattern
    all_scripts = {f.stem for f in DEV_PATH.glob("*.py")}
    mapped_scripts = {r[0] for r in db.execute("SELECT script_name FROM cowork_script_mapping").fetchall()}
    unmapped = all_scripts - mapped_scripts

    # 4. Category analysis — what's missing?
    categories = defaultdict(list)
    for f in DEV_PATH.glob("*.py"):
        prefix = f.stem.split('_')[0]
        categories[prefix].append(f.stem)

    # 5. Functional gaps
    existing_capabilities = set()
    for f in DEV_PATH.glob("*.py"):
        name = f.stem.lower()
        for cap in ["monitor", "optimizer", "analyzer", "manager", "guard", "scanner",
                     "tracker", "generator", "builder", "tester", "checker", "profiler",
                     "scheduler", "deployer", "router", "cache", "sync", "backup"]:
            if cap in name:
                existing_capabilities.add(cap)

    potential_gaps = []
    desired_capabilities = {
        "log_compressor": "Compress and archive old logs automatically",
        "api_rate_limiter": "Rate limiting for cluster API calls",
        "model_health_checker": "Deep health check of loaded models (not just ping)",
        "voice_command_fuzzer": "Fuzz test voice commands for edge cases",
        "config_drift_detector": "Detect config differences between nodes",
        "dependency_vulnerability_scanner": "Check Python stdlib usage for known issues",
        "performance_regression_detector": "Compare benchmarks over time",
        "auto_documentation_updater": "Keep COWORK_TASKS.md in sync with scripts",
        "script_deduplication": "Find and merge duplicate/overlapping scripts",
        "cross_script_integration_tester": "Test that scripts work together",
        "predictive_failure_detector": "Predict script failures from patterns",
        "resource_contention_monitor": "Detect GPU/CPU contention between scripts",
    }

    for name, desc in desired_capabilities.items():
        if not any(name.replace('_', '') in s.replace('_', '') for s in all_scripts):
            potential_gaps.append({"name": name, "description": desc})

    db.close()

    result = {
        "patterns_by_script_count": {r["pattern_id"]: r["cnt"] for r in mapping},
        "unused_patterns": [dict(r) for r in unused],
        "unmapped_scripts": sorted(unmapped),
        "category_distribution": {k: len(v) for k, v in sorted(categories.items())},
        "potential_gaps": potential_gaps,
        "total_capabilities": len(existing_capabilities),
        "timestamp": datetime.now().isoformat()
    }

    print(f"\n{'='*60}")
    print(f"GAP ANALYSIS — {len(all_scripts)} scripts")
    print(f"\nSmallest patterns:")
    for pat_id, cnt in sorted(result["patterns_by_script_count"].items(), key=lambda x: x[1])[:5]:
        print(f"  {pat_id}: {cnt} scripts")
    print(f"\nUnused patterns: {len(result['unused_patterns'])}")
    print(f"Unmapped scripts: {len(result['unmapped_scripts'])}")
    if result["unmapped_scripts"]:
        print(f"  {', '.join(result['unmapped_scripts'][:10])}")
    print(f"\nPotential gaps ({len(result['potential_gaps'])}):")
    for gap in result["potential_gaps"]:
        print(f"  - {gap['name']}: {gap['description']}")

    return result


# ── ANTICIPATION ENGINE ────────────────────────────────────────────────

def anticipate_needs():
    """Predict next needs based on dispatch patterns, error trends, and usage."""
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row

    # 1. Most used patterns → likely need more scripts
    hot_patterns = db.execute("""
        SELECT classified_type as pattern_type, COUNT(*) as cnt, AVG(latency_ms) as avg_lat,
               AVG(CASE WHEN success=1 THEN 1.0 ELSE 0.0 END) as success_rate
        FROM agent_dispatch_log
        GROUP BY classified_type
        ORDER BY cnt DESC
        LIMIT 10
    """).fetchall()

    # 2. Failing patterns → need fixing
    failing = db.execute("""
        SELECT classified_type as pattern_type, COUNT(*) as fails
        FROM agent_dispatch_log
        WHERE success = 0
        GROUP BY classified_type
        ORDER BY fails DESC
        LIMIT 5
    """).fetchall()

    # 3. Slow patterns → need optimization
    slow = db.execute("""
        SELECT classified_type as pattern_type, AVG(latency_ms) as avg_lat, COUNT(*) as cnt
        FROM agent_dispatch_log
        WHERE success = 1
        GROUP BY classified_type
        HAVING avg_lat > 20000
        ORDER BY avg_lat DESC
    """).fetchall()

    db.close()

    # 4. Script complexity analysis — find scripts that need refactoring
    complex_scripts = []
    for f in DEV_PATH.glob("*.py"):
        try:
            with open(f, 'r', encoding='utf-8', errors='ignore') as fh:
                source = fh.read()
            lines = len(source.splitlines())
            tree = ast.parse(source)
            funcs = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
            # Complexity indicators
            if lines > 400 or funcs > 20:
                complex_scripts.append({
                    "script": f.stem, "lines": lines, "functions": funcs,
                    "needs": "refactoring" if lines > 500 else "review"
                })
        except:
            pass

    # 5. Generate predictions
    predictions = []

    if hot_patterns:
        top = hot_patterns[0]
        predictions.append({
            "type": "high_demand",
            "pattern": top["pattern_type"],
            "calls": top["cnt"],
            "action": f"Add more scripts for '{top['pattern_type']}' pattern (most used: {top['cnt']} calls)"
        })

    if failing:
        for f in failing[:3]:
            predictions.append({
                "type": "reliability",
                "pattern": f["pattern_type"],
                "fails": f["fails"],
                "action": f"Fix reliability issues in '{f['pattern_type']}' ({f['fails']} failures)"
            })

    if slow:
        for s in slow[:3]:
            predictions.append({
                "type": "performance",
                "pattern": s["pattern_type"],
                "avg_latency": round(s["avg_lat"]),
                "action": f"Optimize '{s['pattern_type']}' (avg {round(s['avg_lat']/1000, 1)}s)"
            })

    if complex_scripts:
        for cs in complex_scripts[:5]:
            predictions.append({
                "type": "maintenance",
                "script": cs["script"],
                "lines": cs["lines"],
                "action": f"Refactor {cs['script']} ({cs['lines']} lines, {cs['functions']} functions)"
            })

    result = {
        "predictions": predictions,
        "hot_patterns": [dict(r) for r in hot_patterns],
        "failing_patterns": [dict(r) for r in failing],
        "slow_patterns": [dict(r) for r in slow],
        "complex_scripts": complex_scripts,
        "timestamp": datetime.now().isoformat()
    }

    print(f"\n{'='*60}")
    print(f"ANTICIPATION — {len(predictions)} predictions\n")
    for p in predictions:
        print(f"  [{p['type'].upper()}] {p['action']}")

    return result


# ── OPENCLAW SYNC ──────────────────────────────────────────────────────

def openclaw_sync():
    """Sync cowork scripts to OpenClaw workspace."""
    if not OPENCLAW_DEV.exists():
        print(f"OpenClaw workspace not found: {OPENCLAW_DEV}")
        return {"status": "error", "message": "workspace not found"}

    new_count = 0
    updated_count = 0
    unchanged = 0

    for f in sorted(DEV_PATH.glob("*.py")):
        target = OPENCLAW_DEV / f.name
        source_content = f.read_bytes()

        if not target.exists():
            target.write_bytes(source_content)
            new_count += 1
        elif target.read_bytes() != source_content:
            target.write_bytes(source_content)
            updated_count += 1
        else:
            unchanged += 1

    # Also sync key docs
    for doc in ["COWORK_TASKS.md", "INSTRUCTIONS.md", "TOOLS.md", "IDENTITY.md"]:
        src = BASE / doc
        tgt = OPENCLAW_DEV.parent / doc
        if src.exists():
            tgt.write_bytes(src.read_bytes())

    result = {
        "new": new_count,
        "updated": updated_count,
        "unchanged": unchanged,
        "total": new_count + updated_count + unchanged,
        "timestamp": datetime.now().isoformat()
    }

    print(f"\nOpenClaw Sync: {result['new']} new | {result['updated']} updated | "
          f"{result['unchanged']} unchanged | {result['total']} total")
    return result


# ── AUTO-IMPROVE ──────────────────────────────────────────────────

def auto_improve():
    """Auto-improve weak scripts: add docstrings, fix escape sequences, add __main__, add argparse."""
    fixed = 0
    skipped = 0
    details = []

    # Valid Python escape characters (after the backslash)
    valid_escapes = set('\\\'\"abfnrtvx01234567NuU\n\r')

    def _fix_escape_sequences(source):
        """Fix invalid escape sequences in non-raw string literals."""
        result = []
        i = 0
        in_string = None  # None, or the quote character(s)
        raw = False
        while i < len(source):
            ch = source[i]

            # Detect raw string prefix
            if in_string is None and ch in ('r', 'R') and i + 1 < len(source) and source[i + 1] in ('"', "'"):
                raw = True
                result.append(ch)
                i += 1
                continue

            # Detect string start
            if in_string is None and ch in ('"', "'"):
                raw_flag = raw
                raw = False
                # Check for triple quote
                if source[i:i+3] in ('"""', "'''"):
                    in_string = source[i:i+3]
                    result.append(in_string)
                    i += 3
                    # Scan triple-quoted string
                    while i < len(source):
                        if source[i:i+len(in_string)] == in_string:
                            result.append(in_string)
                            i += len(in_string)
                            break
                        elif source[i] == '\\' and not raw_flag:
                            if i + 1 < len(source) and source[i + 1] not in valid_escapes:
                                result.append('\\\\')
                                i += 1
                                continue
                        result.append(source[i])
                        i += 1
                    in_string = None
                    continue
                else:
                    in_string = ch
                    result.append(ch)
                    i += 1
                    # Scan single-quoted string
                    while i < len(source):
                        if source[i] == in_string and (i == 0 or source[i-1] != '\\'):
                            result.append(source[i])
                            i += 1
                            break
                        elif source[i] == '\\' and not raw_flag:
                            if i + 1 < len(source) and source[i + 1] not in valid_escapes:
                                result.append('\\\\')
                                i += 1
                                continue
                        result.append(source[i])
                        i += 1
                    in_string = None
                    continue

            raw = False
            result.append(ch)
            i += 1

        return ''.join(result)

    for f in sorted(DEV_PATH.glob("*.py")):
        try:
            with open(f, 'r', encoding='utf-8', errors='ignore') as fh:
                source = fh.read()
            original = source
            fixes_applied = []

            # Fix 1: Add missing module-level docstring
            try:
                tree = ast.parse(source)
                if ast.get_docstring(tree) is None:
                    friendly = f.stem.replace('_', ' ').title()
                    docline = f'"""{friendly} — COWORK auto-generated docstring."""\n'
                    lines = source.split('\n')
                    insert_at = 0
                    for idx, line in enumerate(lines):
                        if line.startswith('#!') or line.startswith('# -*-') or line.startswith('# coding'):
                            insert_at = idx + 1
                        else:
                            break
                    lines.insert(insert_at, docline)
                    source = '\n'.join(lines)
                    fixes_applied.append("added_docstring")
            except SyntaxError:
                pass

            # Fix 2: Fix invalid escape sequences (\B, \Z, etc.)
            new_source = _fix_escape_sequences(source)
            if new_source != source:
                source = new_source
                fixes_applied.append("fixed_escape_sequences")

            # Fix 3: Add missing if __name__ == "__main__" block
            if 'if __name__' not in source:
                source = source.rstrip() + '\n\n\nif __name__ == "__main__":\n    pass\n'
                fixes_applied.append("added_main_block")

            # Fix 4: Add missing argparse with --help for scripts that have __main__ but no argparse
            if 'argparse' not in source and 'if __name__' in source:
                # Add import argparse after last import line
                lines = source.split('\n')
                import_idx = 0
                for idx, line in enumerate(lines):
                    stripped = line.strip()
                    if stripped.startswith('import ') or stripped.startswith('from '):
                        import_idx = idx + 1
                if import_idx > 0:
                    lines.insert(import_idx, 'import argparse')
                    source = '\n'.join(lines)

                # Replace bare "pass" in __main__ with argparse setup
                source = re.sub(
                    r"(if __name__ == ['\"]__main__['\"]:\s*\n)\s*pass\n?",
                    r'\1'
                    '    parser = argparse.ArgumentParser(description=f"{Path(__file__).stem} — COWORK script")\n'
                    '    parser.add_argument("--help-ext", action="store_true", help="Show extended help")\n'
                    '    args = parser.parse_args()\n',
                    source
                )
                fixes_applied.append("added_argparse")

            if source != original:
                with open(f, 'w', encoding='utf-8') as fh:
                    fh.write(source)
                fixed += 1
                details.append({"script": f.stem, "fixes": fixes_applied})
                print(f"  FIXED: {f.stem} — {', '.join(fixes_applied)}")
            else:
                skipped += 1

        except Exception as e:
            skipped += 1
            details.append({"script": f.stem, "error": str(e)})

    result = {"fixed": fixed, "skipped": skipped, "details": details}

    print(f"\n{'='*60}")
    print(f"AUTO-IMPROVE: {fixed} fixed | {skipped} skipped")

    return result


# ── FULL CYCLE ─────────────────────────────────────────────────────────

def full_cycle():
    """Run complete continuous development cycle."""
    print(f"\n{'#'*60}")
    print(f"# COWORK ENGINE — Full Development Cycle")
    print(f"# {datetime.now().isoformat()}")
    print(f"{'#'*60}")

    # Phase 1: Test all
    print(f"\n{'='*60}\nPHASE 1: MULTI-TEST\n{'='*60}")
    test_summary, test_results = test_all()

    # Phase 2: Gap analysis
    print(f"\n{'='*60}\nPHASE 2: GAP ANALYSIS\n{'='*60}")
    gaps = analyze_gaps()

    # Phase 3: Anticipation
    print(f"\n{'='*60}\nPHASE 3: ANTICIPATION\n{'='*60}")
    predictions = anticipate_needs()

    # Phase 3.5: Auto-improve
    print(f"\n{'='*60}\nPHASE 3.5: AUTO-IMPROVE\n{'='*60}")
    improvements = auto_improve()

    # Phase 4: Sync
    print(f"\n{'='*60}\nPHASE 4: OPENCLAW SYNC\n{'='*60}")
    sync = openclaw_sync()

    # Phase 5: Summary
    print(f"\n{'#'*60}")
    print(f"# CYCLE COMPLETE")
    print(f"#")
    print(f"# Tests: {test_summary['ok']}/{test_summary['total']} OK")
    print(f"# Gaps: {len(gaps['potential_gaps'])} identified")
    print(f"# Predictions: {len(predictions['predictions'])} actions needed")
    print(f"# Improved: {improvements['fixed']} fixed | {improvements['skipped']} skipped")
    print(f"# Sync: {sync['new']} new + {sync['updated']} updated")
    print(f"{'#'*60}")

    # Save cycle report
    report = {
        "cycle": "full",
        "tests": test_summary,
        "gaps": gaps,
        "predictions": predictions,
        "improvements": improvements,
        "sync": sync,
        "timestamp": datetime.now().isoformat()
    }
    report_path = TURBO / "data" / f"cowork_cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nFull report: {report_path}")

    # Telegram alerts on failures/gaps
    fail_count = test_summary.get("fail", 0)
    total_count = test_summary.get("total", 0)
    gap_count = len(gaps.get("potential_gaps", []))
    if fail_count > 0:
        send_telegram_alert(f"<b>COWORK CYCLE FAIL</b>: {fail_count}/{total_count} scripts failed")
    if gap_count > 5:
        send_telegram_alert(f"<b>COWORK GAPS</b>: {gap_count} coverage gaps identified")

    return report


# ── CYCLE METRICS → DB ───────────────────────────────────────────────

def log_cycle_metrics(report):
    """Persist cycle metrics into etoile.db for dashboard/history."""
    db = sqlite3.connect(str(DB_PATH))
    db.execute("""
        CREATE TABLE IF NOT EXISTS cowork_cycle_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            total_scripts INTEGER DEFAULT 0,
            ok INTEGER DEFAULT 0,
            fail INTEGER DEFAULT 0,
            gaps INTEGER DEFAULT 0,
            predictions INTEGER DEFAULT 0,
            sync_new INTEGER DEFAULT 0,
            sync_updated INTEGER DEFAULT 0,
            elapsed_s REAL DEFAULT 0,
            report_json TEXT DEFAULT ''
        )
    """)
    tests = report.get("tests", {})
    gaps = report.get("gaps", {})
    preds = report.get("predictions", {})
    sync = report.get("sync", {})
    db.execute("""
        INSERT INTO cowork_cycle_log
        (timestamp, total_scripts, ok, fail, gaps, predictions, sync_new, sync_updated, elapsed_s, report_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        tests.get("total", 0),
        tests.get("ok", 0),
        tests.get("fail", 0),
        len(gaps.get("potential_gaps", [])),
        len(preds.get("predictions", [])),
        sync.get("new", 0),
        sync.get("updated", 0),
        tests.get("elapsed_s", 0),
        json.dumps(report, default=str, ensure_ascii=False)[:50000]
    ))
    db.commit()
    db.close()
    print("[metrics] Cycle logged to etoile.db:cowork_cycle_log")


# ── CONTINUOUS LOOP ──────────────────────────────────────────────────

def continuous_loop(interval=300):
    """Run full_cycle every `interval` seconds (default 5 min)."""
    import signal

    running = True
    def _stop(sig, frame):
        nonlocal running
        running = False
        print(f"\n[loop] Received signal {sig}, stopping after current cycle...")

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)

    cycle_num = 0
    pid = os.getpid()
    print(f"[loop] COWORK continuous loop started — interval={interval}s")
    print(f"[loop] PID={pid} | DB={DB_PATH}")
    send_telegram_alert(f"<b>COWORK Loop started</b> — PID={pid}, interval={interval}s")

    while running:
        cycle_num += 1
        print(f"\n{'='*60}")
        print(f"[loop] Cycle #{cycle_num} — {datetime.now().isoformat()}")
        print(f"{'='*60}")

        try:
            report = full_cycle()
            log_cycle_metrics(report)
        except Exception as e:
            print(f"[loop] Cycle #{cycle_num} FAILED: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            send_telegram_alert(f"<b>COWORK CYCLE ERROR</b> #{cycle_num}: <code>{e}</code>")

        if not running:
            break

        print(f"[loop] Next cycle in {interval}s...")
        # Sleep in small increments so we can respond to signals
        for _ in range(interval):
            if not running:
                break
            time.sleep(1)

    print(f"[loop] Stopped after {cycle_num} cycles")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="COWORK Engine — Continuous Development")
    parser.add_argument("--test-all", action="store_true", help="Test all scripts")
    parser.add_argument("--gaps", action="store_true", help="Gap analysis")
    parser.add_argument("--anticipate", action="store_true", help="Predict needs")
    parser.add_argument("--improve", action="store_true", help="Auto-improve scripts")
    parser.add_argument("--openclaw-sync", action="store_true", help="Sync to OpenClaw")
    parser.add_argument("--cycle", action="store_true", help="Full cycle (once)")
    parser.add_argument("--once", action="store_true", help="Alias for --cycle")
    parser.add_argument("--loop", action="store_true", help="Continuous loop (default 5min)")
    parser.add_argument("--interval", type=int, default=300, help="Loop interval in seconds")
    args = parser.parse_args()

    if args.test_all:
        test_all()
    elif args.gaps:
        analyze_gaps()
    elif args.anticipate:
        anticipate_needs()
    elif args.improve:
        auto_improve()
    elif args.openclaw_sync:
        openclaw_sync()
    elif args.loop:
        continuous_loop(interval=args.interval)
    elif args.cycle or args.once or len(sys.argv) == 1:
        full_cycle()
