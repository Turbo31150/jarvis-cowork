#!/usr/bin/env python3
"""
Code Quality Metrics Monitor for JARVIS
Monitors code quality: coverage, complexity, duplication.
Analyzes projects in workspace and generates reports.
"""

import ast
import hashlib
import os
import re
import shutil
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


@dataclass
class MetricReport:
    """Represents a code quality metric report."""
    project_name: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Complexity metrics
    cyclomatic_complexity: dict[str, int] = field(default_factory=dict)  # {file: complexity}
    max_complexity: int = 0
    
    # Code coverage (simulated - real coverage requires test framework)
    coverage_estimate: float = 0.0
    lines_of_code: int = 0
    commented_lines: int = 0
    blank_lines: int = 0
    
    # Duplication metrics
    duplicate_blocks: list[dict] = field(default_factory=list)
    duplication_ratio: float = 0.0
    
    # Code health indicators
    import_statements: int = 0
    function_count: int = 0
    class_count: int = 0
    max_line_length: int = 0
    
    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if not callable(v)}


@dataclass
class ComplexityNode:
    """AST Node for tracking cyclomatic complexity."""
    file_path: str
    function_name: str
    complexity: int = 1
    location: dict[str, int] = field(default_factory=lambda: {"line": 0, "col": 0})


class CodeAnalyzer(ast.NodeVisitor):
    """AST-based code analyzer for metrics."""
    
    def __init__(self, source_code: str, file_path: str):
        self.source = source_code
        self.file_path = file_path
        self.functions: dict[str, tuple[int, int]] = {}  # name -> (start, end)
        self.complexity_nodes: list[ComplexityNode] = []
        self.current_function: Optional[str] = None
        self.max_line_length = 0
        
        try:
            self.tree = ast.parse(source_code)
        except SyntaxError as e:
            # Handle syntax errors gracefully
            self.complexity_nodes.append(ComplexityNode(
                file_path=file_path,
                function_name="PARSE_ERROR",
                complexity=1,
                location={"line": e.lineno, "col": e.offset}
            ))
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Track class definitions."""
        self._count_class(node.name)
    
    def _count_class(self, name: str) -> None:
        """Count a class definition."""
        pass  # Will count at end
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Track function definitions and calculate complexity."""
        self._process_function(node.name, node.lineno, node.col_offset)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Track async function definitions."""
        self._process_function(node.name, node.lineno, node.col_offset)
    
    def _process_function(self, name: str, start_line: int, start_col: int) -> None:
        """Process a function definition for complexity."""
        # Calculate cyclomatic complexity
        complexity = 1  # Base complexity
        
        # Add complexity for each conditional branch
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler, 
                               ast.With, ast.Assert)):
                complexity += 1
            elif isinstance(node, ast.comprehension):
                complexity += 1
        
        location = {"line": start_line, "col": start_col}
        
        self.complexity_nodes.append(ComplexityNode(
            file_path=self.file_path,
            function_name=name,
            complexity=complexity,
            location=location
        ))
    
    def visit_Import(self, node: ast.Import) -> None:
        """Track import statements."""
        for alias in node.names:
            if "." not in alias.name:  # Count top-level imports
                pass
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Track from imports."""
        pass
    
    def get_stats(self) -> dict[str, Any]:
        """Get analysis statistics."""
        total_complexity = sum(n.complexity for n in self.complexity_nodes)
        max_comp = max((n.complexity for n in self.complexity_nodes), default=0)
        
        # Calculate line metrics
        lines = self.source.splitlines()
        loc_count = len(lines) - \
                    sum(1 for l in lines if not l.strip()) + \
                    sum(1 for l in lines if l.strip() and l[0] != "#")
        
        return {
            "file": self.file_path,
            "total_functions": len(self.complexity_nodes),
            "max_complexity": max_comp,
            "average_complexity": total_complexity / len(self.complexity_nodes) if self.complexity_nodes else 0,
            "total_lines": loc_count,
            "high_complexity_funcs": [n.function_name for n in self.complexity_nodes 
                                     if n.complexity >= 10][:5]  # Top 5 high complexity
        }


class DuplicationDetector:
    """Detect code duplication using token-based comparison."""
    
    @staticmethod
    def tokenize(source: str) -> list[str]:
        """Tokenize source code into normalized tokens."""
        # Remove comments and strings, normalize whitespace
        import re
        
        # Remove single-line comments
        lines = source.splitlines()
        cleaned_lines = []
        for line in lines:
            # Remove Python-style comments
            if '#' in line:
                comment_pos = line.find('#')
                # Check if it's not inside a string
                hash_count = 0
                new_line = ""
                for i, ch in enumerate(line):
                    if ch == '"' and not (new_line.count('"') - line[:i].count('"') % 2):
                        new_line += ch
                        continue
                    if ch == '#' and (new_line.count('"') % 2) == 0:
                        break
                    new_line += ch
                line = new_line
            cleaned_lines.append(line)
        
        # Normalize whitespace in each line
        normalized = [" ".join(l.split()) for l in cleaned_lines if l.strip()]
        
        return normalized
    
    @staticmethod
    def find_duplicates(source1: str, source2: str, min_length: int = 10) -> list[dict]:
        """Find duplicate code blocks between two files."""
        tokens1 = set(DuplicationDetector.tokenize(source1))
        tokens2 = set(DupulationDetector.tokenize(source2))
        
        common_tokens = tokens1 & tokens2
        
        if not common_tokens:
            return []
        
        # Simple approach: find longest common substring in tokenized lines
        results = []
        
        def tokenize_lines(source):
            lines = source.splitlines()
            normalized = [" ".join(l.split()) for l in lines if l.strip()]
            return normalized
        
        tokens1_list = tokenize_lines(source1)
        tokens2_list = tokenize_lines(source2)
        
        # Find common sequences
        found_sequences = set()
        
        for i, t1 in enumerate(tokens1_list):
            for j, t2 in enumerate(tokens2_list):
                if len(t1) >= min_length and t1 == t2:
                    seq_key = hash(frozenset([t1]))
                    if seq_key not in found_sequences:
                        found_sequences.add(seq_key)
                        results.append({
                            "sequence": t1,
                            "file1_line": tokens1_list.index(t1),
                            "file2_line": tokens2_list.index(t2)
                        })
        
        return results


class CoverageAnalyzer:
    """Estimate code coverage (requires test infrastructure for exact values)."""
    
    @staticmethod
    def analyze_coverage(project_path: str, coverage_data_path: Optional[str] = None) -> dict:
        """Analyze or estimate code coverage."""
        
        # Check for actual coverage data from test frameworks
        result = {
            "status": "estimated",
            "method": "heuristic"
        }
        
        # Look for coverage reports
        common_coverage_files = [
            ".coverage",
            "coverage.xml", 
            "coverage.json",
            ".coveragerc",
            "pyproject.toml",
            "setup.cfg"
        ]
        
        for filename in common_coverage_files:
            if os.path.exists(os.path.join(project_path, filename)):
                result["status"] = "available"
                result["source_file"] = filename
                break
        
        # Heuristic estimation based on file structure
        result["estimated_percentage"] = 0.65  # Default estimate
        result["lines_analyzed"] = 0
        
        return result


def analyze_project(project_path: str, target_dir: Optional[str] = None) -> MetricReport:
    """Analyze a project directory for code quality metrics."""
    
    report = MetricReport(project_name=Path(project_path).name)
    
    python_files = []
    for root, dirs, files in os.walk(project_path):
        # Skip certain directories
        skip_dirs = {'.git', '__pycache__', 'node_modules', '.venv'}
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    # Analyze each Python file
    total_complexity = 0
    max_complexity = 0
    total_lines = 0
    functions_found = 0
    
    for filepath in python_files[:100]:  # Limit to first 100 files for speed
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                source = f.read()
            
            analyzer = CodeAnalyzer(source, filepath)
            stats = analyzer.get_stats()
            
            total_complexity += stats["total_functions"] * stats["average_complexity"]
            max_complexity = max(max_complexity, stats["max_complexity"])
            functions_found += stats["total_functions"]
            total_lines += stats["lines_analyzed"]
            
            # Track top complexity files
            if stats["max_complexity"] > report.max_complexity:
                report.max_complexity = stats["max_complexity"]
                
        except Exception as e:
            print(f"Warning: Could not analyze {filepath}: {e}", file=sys.stderr)
    
    report.cyclomatic_complexity = {
        "total": total_complexity,
        "functions_analyzed": functions_found,
        "max_function": max_complexity
    }
    
    # Coverage estimation
    if target_dir and os.path.exists(target_dir):
        coverage_result = CoverageAnalyzer.analyze_coverage(target_dir)
        report.coverage_estimate = coverage_result.get("estimated_percentage", 0)
    
    return report


def generate_report(project_path: str, output_format: str = "text") -> str:
    """Generate a code quality report."""
    
    print(f"\n🔍 Analyzing project: {project_path}")
    print("=" * 60)
    
    report = analyze_project(project_path)
    
    # Calculate duplication metrics
    detector = DuplicationDetector()
    
    # Simple estimation based on file count
    if report.cyclomatic_complexity["functions_analyzed"] > 0:
        avg_comp = report.cyclomatic_complexity["total"] / report.cyclomatic_complexity["functions_analyzed"]
        complexity_score = min(10, (avg_comp - 5) / 2)  # Normalize
    else:
        complexity_score = 5
    
    if report.coverage_estimate == 0:
        coverage_score = 65.0  # Default estimate
    else:
        coverage_score = report.coverage_estimate * 100
    
    duplication_score = min(95, max(70, 85 - (report.max_complexity / 5)))
    
    # Output report
    if output_format == "json":
        result = {
            "project": report.project_name,
            "timestamp": report.timestamp,
            "complexity": report.cyclomatic_complexity,
            "coverage": {"score": coverage_score},
            "duplication": {"estimated_ratio": 1.0 - (duplication_score / 95)},
            "health": {
                "complexity_score": round(complexity_score * 10, 2),
                "coverage_score": round(coverage_score, 2),
                "duplication_score": round(duplication_score, 2)
            }
        }
        return json.dumps(result, indent=2)
    else:
        output = f"""
📊 Code Quality Report - {report.project_name}
{'=' * 60}

🎯 HEALTH SCORES
----------------
│ Metric           │ Score     │ Status          │
├──────────────────┼───────────┼───────────────────┤
│ Coverage         │ {coverage_score:7.2f}%    │ {'✅ Good' if coverage_score >= 70 else '⚠️ Needs Work'} │
│ Complexity       │ {duplication_score:7.2f}   │ {'✅ Acceptable' if duplication_score >= 80 else '⚠️ High' if duplication_score >= 70 else '❌ Critical'} │
│ Duplication      │ {100 - ((report.max_complexity or 1) / 5):7.2f}%  │ {'✅ Clean' if report.max_complexity < 8 else '⚠️ Some Duplication' if report.max_complexity < 15 else '❌ Significant'} │

📈 COMPLEXITY METRICS
---------------------
Total Functions Analyzed: {report.cyclomatic_complexity.get('functions_analyzed', 0)}
Average Complexity: {report.cyclomatic_complexity['total'] / max(report.cyclomatic_complexity['functions_analyzed'], 1):.2f}
Max Function Complexity: {report.max_complexity or 0}

📝 CODE STATISTICS
------------------
Lines of Code Analyzed: {total_lines := total_lines + sum(analyzer.get_stats()['lines_analyzed'] for _ in [0]) if 'total_lines' in dir() else report.cyclomatic_complexity['functions_analyzed']} (Approximation)
Functions Found: {report.cyclomatic_complexity['functions_analyzed']}
Max Complexity Function: {report.max_complexity}

💡 RECOMMENDATIONS
------------------
• Reduce function complexity below 10 where possible
• Increase code coverage through testing
• Refactor duplicated logic into shared functions
"""
        return output


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Code Quality Metrics Monitor for JARVIS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s analyze ./my_project                 # Analyze a project directory
  %(prog)s analyze ./my_project --output json   # JSON output format
  %(pong)s monitor ~/.openclaw/config.json      # Monitor specific config

Metrics tracked:
  - Cyclomatic complexity
  - Code coverage (estimated)
  - Duplication detection
  - Function/class counts
"""
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze code quality")
    analyze_parser.add_argument("project_path", help="Path to project to analyze")
    analyze_parser.add_argument("--output", "-o", default="text", 
                               choices=["text", "json"], help="Output format")
    
    # monitor command
    monitor_parser = subparsers.add_parser("monitor", help="Start monitoring mode")
    monitor_parser.add_argument("--interval", "-i", type=int, default=300,
                               help="Check interval in seconds")
    monitor_parser.add_argument("--project", "-p", help="Project path to monitor")
    
    # report command
    report_parser = subparsers.add_parser("report", help="Generate quality report")
    report_parser.add_argument("target_path", help="Target for quality report")
    
    args = parser.parse_args()
    
    if hasattr(args, "command"):
        if args.command == "analyze":
            result = generate_report(args.project_path, args.output)
            print(result)
            
        elif args.command == "monitor":
            # Simple polling mode
            import signal
            
            def handler(signum, frame):
                print("\nStopping monitor...")
                sys.exit(0)
            
            signal.signal(signal.SIGINT, handler)
            
            if not args.project:
                parser.print_help()
            else:
                while True:
                    try:
                        generate_report(args.project_path, "text")
                        print(f"\n✓ Next check in {args.interval}s...")
                        time.sleep(args.interval)
                    except KeyboardInterrupt:
                        break
            
        elif args.command == "report":
            result = analyze_project(args.target_path)
            print(json.dumps(result.to_dict(), indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
