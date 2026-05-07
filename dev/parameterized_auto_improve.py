#!/usr/bin/env python3
"""Parameterized Auto-Improvement script for COWORK.

Reads configuration from AUTO_IMPROVE_CONFIG.json and applies fixes.
Usage: python parameterized_auto_improve.py --once
"""
import json
import sys
import ast
import re
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent
CONFIG_PATH = BASE / "AUTO_IMPROVE_CONFIG.json"
DEV_PATH = BASE

def load_config():
    """Load configuration from JSON file."""
    default_config = {
        "enabled": True,
        "fix_types": {
            "syntax_errors": {"misplaced_imports": True, "indentation_fix": True},
            "docstrings": {"add_module_docstring": True},
            "argparse": {"add_if_missing": True},
            "main_block": {"add_if_missing": True}
        },
        "max_fixes_per_run": 10,
        "backup_before_fix": True
    }
    try:
        with open(CONFIG_PATH) as f:
            config = json.load(f)
        # Merge with defaults
        for key, val in default_config.items():
            if key not in config:
                config[key] = val
        return config
    except Exception as e:
        print(f"Warning: Could not load config, using defaults: {e}")
        return default_config

def fix_misplaced_imports(source):
    """Fix imports that are incorrectly placed outside function indentation."""
    lines = source.split('\n')
    fixed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Check for 'import' statements after a dedent (function end)
        if line.strip().startswith(('import ', 'from ')) and i > 0:
            # Look back to see if we're in a dedent situation
            prev_line = lines[i-1].strip()
            prev_prev = lines[i-2].strip() if i >= 2 else ""
            # If previous line ends function without newline before import
            if fixed_lines and fixed_lines[-1].strip() and not line.startswith((' ', '\t')):
                # This import might be misplaced - check context
                if prev_line in ['pass', 'return', '}'] or prev_line.startswith('return '):
                    # This import should be inside the function - skip it
                    pass
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
        i += 1
    return '\n'.join(fixed_lines)

def fix_syntax_errors(source):
    """Fix common syntax errors like misplaced imports after function definitions."""
    lines = source.split('\n')
    result = []
    in_function = False
    function_indent = 0
    skip_next_import = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Detect function definition
        if stripped.startswith('def ') and ':' in stripped:
            in_function = True
            function_indent = len(line) - len(line.lstrip())
            
        # Detect dedent (end of function)
        elif in_function and stripped and len(line) - len(line.lstrip()) <= function_indent:
            in_function = False
        
        # Check for misplaced import at module level inside function
        if in_function and stripped.startswith('import ') and skip_next_import:
            skip_next_import = False
            continue
        
        result.append(line)
    
    return '\n'.join(result)

def fix_indentation_issues(source):
    """Fix indentation issues by normalizing."""
    try:
        compile(source, '<string>', 'exec')
        return source
    except SyntaxError as e:
        if 'unexpected indent' in str(e):
            lines = source.split('\n')
            fixed = []
            for line in lines:
                # Remove leading spaces if line causes indent error
                fixed.append(line.lstrip(' \t'))
            return '\n'.join(fixed)
    return source

def add_docstring(source, script_name):
    """Add module docstring if missing."""
    try:
        tree = ast.parse(source)
        if ast.get_docstring(tree) is None:
            friendly = script_name.replace('_', ' ').title()
            docline = f'"""{friendly} — COWORK auto-generated docstring."""\n'
            lines = source.split('\n')
            insert_at = 0
            for idx, line in enumerate(lines):
                if line.startswith('#!') or line.startswith('# -*-') or line.startswith('# coding'):
                    insert_at = idx + 1
                else:
                    break
            lines.insert(insert_at, docline)
            return '\n'.join(lines)
    except SyntaxError:
        pass
    return source

def add_main_block(source):
    """Add if __name__ == '__main__' block if missing."""
    if 'if __name__' not in source:
        source = source.rstrip() + '\n\n\nif __name__ == "__main__":\n    pass\n'
    return source

def add_argparse(source):
    """Add argparse if missing but __main__ exists."""
    if 'argparse' not in source and 'if __name__' in source:
        lines = source.split('\n')
        import_idx = 0
        for idx, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith(('import ', 'from ')):
                import_idx = idx + 1
        if import_idx > 0:
            lines.insert(import_idx, 'import argparse')
            source = '\n'.join(lines)
        
        source = re.sub(
            r"(if __name__ == ['\"]__main__['\"]:\s*\n)\s*pass\n?",
            r'\1    parser = argparse.ArgumentParser(description=f"{Path(__file__).stem} — COWORK script")\n'
            r'    parser.add_argument("--help-ext", action="store_true", help="Show extended help")\n'
            r'    args = parser.parse_args()\n',
            source
        )
    return source

def main():
    if "--once" not in sys.argv:
        print("Usage: parameterized_auto_improve.py --once")
        sys.exit(1)
    
    config = load_config()
    if not config.get("enabled", True):
        print("Auto-improve is disabled in config")
        sys.exit(0)
    
    scripts = sorted([f for f in DEV_PATH.glob("*.py")])
    fixed_count = 0
    max_fixes = config.get("max_fixes_per_run", 10)
    
    print(f"Scanning {len(scripts)} scripts for auto-improvement...")
    
    for script_path in scripts:
        if fixed_count >= max_fixes:
            break
            
        name = script_path.stem
        
        # Apply excludes
        excludes = config.get("script_filters", {}).get("exclude_patterns", [])
        if any(ex in name for ex in excludes):
            continue
        
        try:
            with open(script_path) as f:
                original = f.read()
            source = original
            fixes = []
            
            # Apply fixes based on config
            fix_types = config.get("fix_types", {})
            
            if fix_types.get("syntax_errors", {}).get("misplaced_imports"):
                source = fix_syntax_errors(source)
                if source != original:
                    fixes.append("fixed_misplaced_imports")
            
            if fix_types.get("syntax_errors", {}).get("indentation_fix"):
                new_source = fix_indentation_issues(source)
                if new_source != source:
                    source = new_source
                    fixes.append("fixed_indentation")
            
            if fix_types.get("docstrings", {}).get("add_module_docstring"):
                source = add_docstring(source, name)
                if source != original:
                    fixes.append("added_docstring")
            
            if fix_types.get("main_block", {}).get("add_if_missing"):
                source = add_main_block(source)
                if source != original:
                    fixes.append("added_main_block")
            
            if fix_types.get("argparse", {}).get("add_if_missing"):
                source = add_argparse(source)
                if source != original:
                    fixes.append("added_argparse")
            
            if source != original:
                with open(script_path, 'w') as f:
                    f.write(source)
                fixed_count += 1
                print(f"  FIXED: {name} — {', '.join(fixes)}")
                
        except Exception as e:
            print(f"  ERROR: {name} — {e}")
    
    print(f"\nAuto-improvement complete: {fixed_count} scripts fixed")
    return {"fixed": fixed_count}

if __name__ == "__main__":
    main()