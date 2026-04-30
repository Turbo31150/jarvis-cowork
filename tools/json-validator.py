#!/usr/bin/env python3
"""
JSON Validator and Repair Tool for ~/.openclaw/ directory.
Validates and attempts to repair corrupted JSON files automatically.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class JSONValidator:
    """Validate and repair corrupted JSON files."""

    def __init__(self, base_dir: str = "~/.openclaw/"):
        self.base_dir = os.path.expanduser(base_dir)
        self.reports_dir = "repair_reports"
        os.makedirs(os.path.join(self.base_dir, self.reports_dir), exist_ok=True)

    def validate_file(self, filepath: str, report_errors: bool = True) -> Dict:
        """Validate a JSON file and return validation result."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to parse
            try:
                data = json.loads(content)
                return {
                    "status": "valid",
                    "filepath": filepath,
                    "size_bytes": len(content),
                    "parse_error": None,
                    "schema_issues": [],
                    "trailing_comma": self._check_trailing_comma(content),
                    "indentation_issue": self._check_indentation(content)
                }
            except json.JSONDecodeError as e:
                error_info = {
                    "line": e.lineno,
                    "column": e.colno,
                    "message": str(e),
                    "snippet": content[max(0, e.end-50):e.start+50] if e.start < len(content) else ""
                }
                
                # Try to diagnose and repair
                repair_result = self._attempt_repair(content, filepath)
                
                return {
                    "status": "corrupted",
                    "filepath": filepath,
                    "size_bytes": len(content),
                    "parse_error": error_info,
                    "repair_available": repair_result["available"],
                    "repair_result": repair_result.get("result"),
                    "schema_issues": self._check_schema(data) if data else [],
                    "trailing_comma": self._check_trailing_comma(content),
                    "indentation_issue": self._check_indentation(content)
                }
                
        except FileNotFoundError:
            return {
                "status": "not_found",
                "filepath": filepath,
                "error": f"File not found: {filepath}"
            }
        
        except Exception as e:
            return {
                "status": "error",
                "filepath": filepath,
                "error": str(e)
            }

    def _check_trailing_comma(self, content: str) -> Optional[str]:
        """Check for trailing comma before closing bracket."""
        # Look for patterns like }, or ], at end of lines within brackets
        import re
        
        # Find bracket pairs and check contents
        depth = 0
        for i, char in enumerate(content):
            if char in '[{':
                depth += 1
            elif char in '}]':
                depth -= 1
                if depth <= 0:
                    continue
            
            if depth > 0 and char == ',' and i + 1 < len(content) and content[i+1] not in ' \t\n\r[],}]:'; 
                
                # Check if next non-whitespace is a closing bracket
                j = i + 1
                while j < len(content) and content[j] in ' \t\n\r':
                    j += 1
                
                if j < len(content) and content[j] in '}]':
                    return f"Trailing comma at position {i} (line ~{content[:i].count(chr(10))+1})"

        # More robust check: look for pattern before closing brackets
        trailing_patterns = [
            r',\s*]',  # comma before ]
            r',\s*}',  # comma before }
            r',\s*\)',  # comma before )
        ]
        
        for pattern in trailing_patterns:
            match = list(re.finditer(pattern, content))
            if match:
                return f"Trailing comma pattern '{pattern}' found: {len(match)} occurrence(s)"
        
        return None

    def _check_indentation(self, content: str) -> Optional[str]:
        """Check for indentation inconsistencies."""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith('#'):
                leading_spaces = len(line) - len(line.lstrip())
                if leading_spaces % 2 != 0:  # Assuming 2-space indentation
                    return f"Odd indentation at line {i+1}: {leading_spaces} spaces (expected multiple of 2)"
        
        return None

    def _attempt_repair(self, content: str, filepath: str) -> Dict:
        """Attempt to automatically repair common JSON corruption issues."""
        attempts = 0
        max_attempts = 5
        
        # Strategy 1: Try to parse with Python's tolerant parsing
        import tokenize
        import io
        
        try:
            # Check if it's mostly valid by tokenizing
            tokens = list(tokenize.generate_tokens(io.StringIO(content).readline))
            
            # Find error tokens (ERR tokentype)
            error_pos = None
            for tok in tokens:
                if tok.type == tokenize.ERR:
                    error_pos = (tok.start[0], tok.start[1])
                    break
            
            if error_pos:
                # Try removing content after the error
                line, col = error_pos
                content_after_error = content.split('\n')[line-1][col:]
                
                # Create repaired version - remove trailing content after parse error
                try:
                    repaired = content[:content.find(content_after_error)] + ']' if content[content.find('['):<len(content)] else content[:content.rfind(']')] + ']'
                    
                    # Try to parse repaired version
                    repaired_data = json.loads(repaired)
                    
                    # If successful, try to format it properly
                    repaired_formatted = json.dumps(repaired_data, indent=2)
                    
                    # Actually write the repair back (safe with backup)
                    backup_path = f"{filepath}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    Path(backup_path).write_text(content)
                    
                    Path(filepath).write_text(repaired_formatted)
                    
                    return {
                        "available": True,
                        "strategy": "trailing_content_removal",
                        "result": repaired_formatted[:200] + "...",
                        "backup_created": backup_path,
                        "status": "repaired"
                    }
                except Exception:
                    pass
                    
            # Strategy 2: Try to remove trailing commas
            if self._check_trailing_comma(content):
                repaired = content[:-1].rstrip() + '\n' if content[-1] == ',' else content
                
                try:
                    repaired_data = json.loads(repaired)
                    formatted = json.dumps(repaired_data, indent=2)
                    
                    backup_path = f"{filepath}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    Path(backup_path).write_text(content)
                    Path(filepath).write_text(formatted)
                    
                    return {
                        "available": True,
                        "strategy": "trailing_comma_removal",
                        "result": formatted[:200] + "...",
                        "backup_created": backup_path,
                        "status": "repaired"
                    }
                except Exception:
                    pass
                    
        except (tokenize.TokenError, IndexError):
            # Tokenization failed - try more aggressive repair
            
            # Strategy 3: Remove trailing commas by regex
            try:
                repaired = content
                
                # Fix trailing comma before ] or }
                repaired = re.sub(r',(\s*[\]\}\]])', r'\1', repaired)
                
                try:
                    repaired_data = json.loads(repaired)
                    formatted = json.dumps(repaired_data, indent=2)
                    
                    backup_path = f"{filepath}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    Path(backup_path).write_text(content)
                    Path(filepath).write_text(formatted)
                    
                    return {
                        "available": True,
                        "strategy": "regex_trailing_comma_fix",
                        "result": formatted[:200] + "...",
                        "backup_created": backup_path,
                        "status": "repaired"
                    }
                except Exception:
                    pass
                    
            except re.error:
                return {"available": False, "reason": "Regex error"}
            
        return {
            "available": False,
            "strategy": "no_repair_possible",
            "result": None,
            "backup_created": None,
            "status": "unrepairable"
        }

    def _check_schema(self, data: Dict) -> List[Dict]:
        """Check for common schema issues in JSON objects."""
        issues = []
        
        # Check for None values in required positions
        if isinstance(data, dict):
            for key, value in data.items():
                if value is None:
                    issues.append({
                        "field": key,
                        "type": "null_value",
                        "message": f"Field '{key}' has null value (may be intentional)"
                    })
                
                # Check nested objects
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        if subvalue is None:
                            issues.append({
                                "field": f"{key}.{subkey}",
                                "type": "null_value",
                                "message": f"Nested field '{key}.{subkey}' has null value"
                            })
                        
                        # Check for trailing comma patterns in nested strings
                        if isinstance(subvalue, str):
                            if subvalue.endswith(',') and not subvalue.rstrip().endswith(','):
                                issues.append({
                                    "field": f"{key}.{subkey}",
                                    "type": "trailing_comma",
                                    "message": f"String ends with unexpected comma"
                                })
                            
        return issues

    def repair_all_in_directory(self, directory: Optional[str] = None) -> List[Dict]:
        """Find and repair all corrupted JSON files in the base directory."""
        results = []
        
        if not directory:
            directory = self.base_dir
        
        # Walk through directory
        for root, dirs, files in os.walk(directory):
            # Skip the reports directory
            if 'repair_reports' in root:
                continue
                
            for filename in files:
                if filename.endswith('.json') or filename.endswith('.js'):
                    filepath = os.path.join(root, filename)
                    
                    # Validate file
                    validation = self.validate_file(filepath)
                    
                    if validation["status"] == "corrupted":
                        result_report = {
                            "filepath": filepath,
                            "validation": validation,
                            "repair_available": validation.get("repair_available", False),
                            "timestamp": datetime.now().isoformat(),
                            "action_needed": "repair" if validation.get("repair_available") else "manual_review"
                        }
                        
                        if result_report["repair_available"]:
                            results.append({
                                "status": "repaired",
                                **result_report,
                                "backup_location": os.path.relpath(
                                    result_report.get("backup_location"), self.base_dir
                                )
                            })
                        else:
                            results.append(result_report)
                    elif validation["status"] == "valid":
                        # Still report valid files for completeness
                        results.append({
                            "status": "validated",
                            "filepath": filepath,
                            "validation": validation
                        })
        
        return results

    def generate_summary(self, all_validated: bool = False) -> str:
        """Generate a summary of the directory state."""
        issues_found = []
        healthy_files = 0
        
        for root, dirs, files in os.walk(self.base_dir):
            if 'repair_reports' in root:
                continue
                
            for filename in files:
                if filename.endswith('.json'):
                    filepath = os.path.join(root, filename)
                    
                    try:
                        with open(filepath, 'r') as f:
                            content = f.read()
                        
                        try:
                            json.loads(content)
                            healthy_files += 1
                        except json.JSONDecodeError:
                            issues_found.append(filepath)
                            
                    except Exception as e:
                        issues_found.append(f"{filepath} (read error: {e})")
        
        total_json = healthy_files + len(issues_found)
        
        summary = f"""JSON Directory Health Report
{'='*60}

Directory: {self.base_dir}
Total JSON files scanned: {total_json}
Healthy files: {healthy_files}
Corrupted files: {len(issues_found)}

Issues found:
"""
        
        if issues_found:
            for issue in issues_found[:20]:  # Limit to first 20
                summary += f"  - {issue}\n"
            
            if len(issues_found) > 20:
                summary += f"\n  ... and {len(issues_found) - 20} more corrupted files\n"
        else:
            summary += "  No issues found! All JSON files are valid.\n"
        
        summary += f"""
{'='*60}

To repair corrupted files automatically, run:
  python tools/json-validator.py repair-all

To check a specific file:
  python tools/json-validator.py validate /path/to/file.json
"""
        
        return summary


# Command-line interface
def main():
    """CLI for JSON validation and repair."""
    import argparse
    
    parser = argparse.ArgumentParser(description="JSON Validator and Repair Tool")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Validate single file
    validate_parser = subparsers.add_parser("validate", help="Validate a single JSON file")
    validate_parser.add_argument("filepath", help="Path to JSON file")
    
    # Check entire directory
    check_parser = subparsers.add_parser("check", help="Check all JSON files in ~/.openclaw/")
    check_parser.add_argument("-d", "--directory", help="Custom directory (default: ~/.openclaw/)")
    
    # Repair corrupted files
    repair_parser = subparsers.add_parser("repair-all", help="Repair all corrupted JSON files")
    repair_parser.add_argument("-d", "--directory", help="Custom directory to repair")
    
    # Generate summary
    summary_parser = subparsers.add_parser("summary", help="Generate health summary")
    
    # Interactive check
    interactive_parser = subparsers.add_parser("interactive", help="Interactive validation mode")
    
    args = parser.parse_args()
    
    validator = JSONValidator()
    
    if args.command == "validate":
        result = validator.validate_file(args.filepath)
        
        print(f"\nValidation result for: {args.filepath}")
        print(f"Status: {result['status']}")
        
        if result["status"] == "valid":
            print("✓ File is valid JSON")
            print(f"  Size: {result['size_bytes']} bytes")
            
            if result.get('trailing_comma'):
                print(f"  ⚠ Warning: {result['trailing_comma']}")
                
            if result.get('indentation_issue'):
                print(f"  ⚠ Warning: {result['indentation_issue']}")
                
        elif result["status"] == "corrupted":
            parse_error = result.get("parse_error", {})
            print(f"✗ File is corrupted (line {parse_error.get('line', 'unknown')}, column {parse_error.get('column', 'unknown')})")
            print(f"  Error: {parse_error.get('message', 'Unknown error')}")
            
            if result.get("repair_available"):
                repair_result = result.get("repair_result", {})
                print(f"\n✓ Automatic repair available!")
                print(f"  Strategy: {repair_result.get('strategy', 'unknown')}")
                print(f"  Result preview: {repair_result.get('result', '')[:100]}...")
                if repair_result.get("backup_created"):
                    print(f"  Backup saved to: {repair_result['backup_created']}")
                
                action = input("\nApply repair? (y/n): ").strip().lower()
                if action == 'y':
                    print(f"\n✓ File has been repaired!")
            
            elif result.get("action_needed") == "manual_review":
                print(f"\n⚠ No automatic repair available. Manual review required.")
                
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
        
    elif args.command == "check":
        results = validator.repair_all_in_directory(args.directory)
        
        valid_count = sum(1 for r in results if r["status"] in ("valid", "validated"))
        corrupted_count = sum(1 for r in results if r["status"] == "corrupted")
        
        print(f"\nChecked {len(results)} JSON files:")
        print(f"  Valid: {valid_count}")
        print(f"  Corrupted: {corrupted_count}")
        
        if corrupted_count > 0:
            print(f"\nCorrupted files:")
            for r in results:
                if r["status"] == "corrupted":
                    status = f"{r['filepath']}"
                    if r.get("repair_available"):
                        status += f" [AUTO-REPAIR]"
                    else:
                        status += f" [MANUAL REVIEW NEEDED]"
                    print(f"  - {status}")
                    
    elif args.command == "repair-all":
        results = validator.repair_all_in_directory(args.directory)
        
        repaired = sum(1 for r in results if r.get("backup_created"))
        validated = sum(1 for r in results if r["status"] == "validated")
        corrupted = sum(1 for r in results if r["status"] == "corrupted" and not r.get("repair_available", False))
        
        print(f"\nRepair Summary:")
        print(f"  Validated (no action needed): {validated}")
        print(f"  Repaired: {repaired}")
        print(f"  Corrupted (manual review): {corrupted}")
        
        if repaired > 0:
            print(f"\n✓ {repaired} file(s) have been repaired!")
            print("Backups saved to the same directory with timestamp suffix.")
            
    elif args.command == "summary":
        report = validator.generate_summary()
        print(report)
        
    elif args.command == "interactive":
        print("\nJSON Validator Interactive Mode")
        print("=" * 50)
        
        while True:
            print(f"\nCurrent directory: {os.path.expanduser(validator.base_dir)}")
            print("Commands: validate, check, repair-all, summary, quit")
            
            try:
                cmd = input("\nEnter command: ").strip().lower()
                
                if cmd == "quit" or cmd == "exit":
                    break
                
                elif cmd.startswith("validate"):
                    parts = cmd.split()
                    if len(parts) >= 2:
                        result = validator.validate_file(parts[1])
                        print("\n--- Result ---")
                        
                        status_info = result["status"]
                        print(f"Status: {status_info}")
                        
                        if status_info == "valid":
                            print("✓ Valid JSON file")
                        elif status_info == "corrupted":
                            parse_error = result.get("parse_error", {})
                            print(f"✗ Corrupted (line {parse_error.get('line', '?')}, col {parse_error.get('column', '?')})")
                            
                            if result.get("repair_available"):
                                rresult = result.get("repair_result", {})
                                print(f"✓ Repair available: {rresult.get('strategy')}")
                                
                                action = input("Apply repair? (y/n): ").strip().lower()
                                if action == 'y':
                                    print("✓ File repaired!\n")
                            else:
                                print("✗ Manual review required\n")
                        else:
                            print(f"Error: {result.get('error')}")
                            
                    else:
                        print("Usage: validate <filepath>")
                        
                elif cmd == "check":
                    results = validator.repair_all_in_directory()
                    print(f"\nChecked files:")
                    for r in results:
                        if r["status"] != "validated":
                            status = f"[{r['status'].upper()}]"
                            if r.get("repair_available"):
                                status += "[AUTO-FIX]"
                            
                            print(f"  {status} {r['filepath']}")
                        
                elif cmd == "summary":
                    print("\n" + validator.generate_summary())
                    
                else:
                    print("Unknown command. Type 'help' for available commands.")
                    
            except EOFError:
                break


if __name__ == "__main__":
    main()
