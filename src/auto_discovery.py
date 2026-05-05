#!/usr/bin/env python3
"""Auto-Discovery Module — Detects and registers new agent patterns from YAML configs."""

import os
import sqlite3
import yaml
from pathlib import Path
from datetime import datetime
from path_resolver import resolve_db_with_table, resolve_project_root

def discover_patterns():
    """Scan for YAML configs and update agent_patterns."""
    project_root = resolve_project_root()
    db_path = resolve_db_with_table("etoile.db", "agent_patterns")
    
    print(f"🔍 [Discovery] Scanning project root: {project_root}")
    
    # Find all yaml files in openclaw/ directories or root
    search_paths = [
        project_root,
        Path("/home/turbo/github-social-automation"),
        Path("/home/turbo/Workspaces/jarvis-linux"),
    ]
    
    yaml_files = []
    for sp in search_paths:
        if sp.exists():
            yaml_files.extend(list(sp.rglob("openclaw/*.yaml")))
            yaml_files.extend(list(sp.glob("*.yaml")))
    
    if not yaml_files:
        print("⚠️ [Discovery] No YAML configurations found.")
        return

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    for yf in yaml_files:
        try:
            with open(yf, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if not config or 'agents' not in config:
                continue
                
            app_name = config.get('name', yf.stem)
            print(f"📦 [Discovery] Found app: {app_name} ({yf.name})")
            
            for agent_id, agent_info in config['agents'].items():
                pattern_id = f"PAT_AUTO_{agent_id.upper()}"
                description = f"Auto-discovered agent from {app_name}"
                keywords = f"{app_name},{agent_id},{agent_info.get('type', '')}"
                
                # Check if exists
                cursor.execute("SELECT id FROM agent_patterns WHERE pattern_id=?", (pattern_id,))
                if cursor.fetchone():
                    print(f"  ⏭️ Agent {agent_id} already registered.")
                    continue
                
                # Insert new pattern
                cursor.execute("""
                    INSERT INTO agent_patterns (pattern_id, agent_id, keywords, description, status)
                    VALUES (?, ?, ?, ?, 'active')
                """, (pattern_id, agent_id, keywords, description))
                print(f"  ✅ Registered agent: {agent_id} -> {pattern_id}")
                
        except Exception as e:
            print(f"  ❌ Error parsing {yf}: {e}")

    conn.commit()
    conn.close()
    print("✨ [Discovery] Scan complete.")

if __name__ == "__main__":
    discover_patterns()
