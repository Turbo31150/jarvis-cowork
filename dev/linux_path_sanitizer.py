#!/usr/bin/env python3
"""linux_path_sanitizer.py — #600 Mass-replace Windows hardcoded paths with _paths dynamic constants.

Searches for 'F:/BUREAU/turbo' and variants in all dev/*.py files and replaces them.
"""
import os
import re
from pathlib import Path

DEV_DIR = Path(__file__).resolve().parent
REPO_ROOT = DEV_DIR.parent

PATTERNS = [
    (re.compile(r'["\']F:/BUREAU/turbo/(.*?)["\']'), r'str(TURBO_DIR / "\1")'),
    (re.compile(r'["\']F:\\\\BUREAU\\\\turbo\\\\(.*?)["\']'), r'str(TURBO_DIR / "\1")'),
    (re.compile(r'["\']F:/BUREAU/turbo["\']'), r'str(TURBO_DIR)'),
    (re.compile(r'["\']F:\\\\BUREAU\\\\turbo["\']'), r'str(TURBO_DIR)'),
]

def sanitize_file(file_path: Path):
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    original = content
    
    # Ensure _paths is imported if we are making changes
    has_changes = False
    for pattern, replacement in PATTERNS:
        if pattern.search(content):
            content = pattern.sub(replacement, content)
            has_changes = True
            
    if has_changes:
        # Check if TURBO_DIR is imported
        if "from _paths import" not in content and "import _paths" not in content:
            # Insert import after docstring or at top
            if '"""' in content:
                end_doc = content.find('"""', content.find('"""') + 3) + 3
                content = content[:end_doc] + "\nfrom _paths import TURBO_DIR" + content[end_doc:]
            else:
                content = "from _paths import TURBO_DIR\n" + content
        
        file_path.write_text(content, encoding="utf-8")
        return True
    return False

def main():
    count = 0
    for script in DEV_DIR.glob("*.py"):
        if script.name == "_paths.py" or script.name == Path(__file__).name:
            continue
        if sanitize_file(script):
            print(f"✅ Sanitized: {script.name}")
            count += 1
    
    print(f"\nTotal scripts sanitized: {count}")

if __name__ == "__main__":
    main()
